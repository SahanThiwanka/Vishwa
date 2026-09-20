"""Derive criterion weights from Best-Worst Method elicitation responses.

Run:              python research/src/derive_weights.py
Write the tree:   python research/src/derive_weights.py --apply

Reads responses collected through the web instrument (web/dev.db), solves the
BWM programme per respondent per level, reports each respondent's consistency
ratio, aggregates by geometric mean, and optionally writes the resulting weights
into shared/model/criteria-tree.json - flipping weightStatus from PLACEHOLDER to
ELICITED.

    ~~~ THE GATE ON REPORTING RESULTS ~~~

--apply refuses to run unless there is at least one usable respondent, and it
records exactly how many responses were collected, how many were discarded for
inconsistency, and when. Every number the thesis reports from the weighted model
must be traceable to that record. If --apply has never been run, the tree still
says PLACEHOLDER and no scored output may be reported as a result.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import statistics
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bwm import CONSISTENCY_THRESHOLD, aggregate, solve_bwm  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "web" / "dev.db"
TREE = ROOT / "shared" / "model" / "criteria-tree.json"
OUT_TABLES = ROOT / "research" / "outputs" / "tables"

# Responses whose code starts with any of these are excluded from analysis.
#
# Prefix, not exact match. The exact-match version excluded only the single
# literal code "TESTDATA-DELETE-ME", so a second pilot run coded "TESTDATA-2"
# would have been aggregated into the real weights without a word. The whole
# purpose of the guard is that a pilot cannot contaminate a result, and a guard
# that only catches one spelling of "this is not real data" does not do that.
EXCLUDED_PREFIXES = ("TESTDATA", "TEST-", "PILOT", "DEMO")


QUERY = (
    "SELECT respondentCode, yearsExperience, institution, role, level, "
    "best, worst, bestToOthers, othersToWorst FROM ElicitationResponse"
)

# Postgres folds unquoted identifiers to lower case, and Prisma creates the
# table with camelCase column names, so the same SQL needs quoting there.
PG_QUERY = (
    'SELECT "respondentCode", "yearsExperience", institution, role, level, '
    'best, worst, "bestToOthers", "othersToWorst" FROM "ElicitationResponse"'
)

FIELDS = ["respondentCode", "yearsExperience", "institution", "role", "level",
          "best", "worst", "bestToOthers", "othersToWorst"]


def _database_url() -> str:
    """DATABASE_URL from the environment, falling back to web/.env.

    Deliberately parsed here rather than requiring python-dotenv. The connection
    string already lives in web/.env for the application's benefit, and asking
    whoever runs the analysis to retype it into their shell invites two failure
    modes: pointing at the wrong database, and pasting a live credential into
    shell history. A shell variable still wins if one is set.
    """
    from_env = os.environ.get("DATABASE_URL")
    if from_env:
        return from_env

    dotenv = ROOT / "web" / ".env"
    if not dotenv.exists():
        return ""

    for line in dotenv.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        if key.strip() == "DATABASE_URL":
            return value.strip().strip('"').strip("'")
    return ""


def _fetch_rows() -> list[dict] | None:
    """Read the responses, from PostgreSQL if configured and SQLite otherwise.

    The deployed instrument writes to PostgreSQL, and it is the deployed one
    practitioners actually use. Requiring the analysis to be pointed at the
    production database by hand-editing this function - which is what the
    deployment guide used to say - is how a study ends up analysing the wrong
    responses, or none.
    """
    url = _database_url()
    if url.startswith(("postgres://", "postgresql://")):
        try:
            import psycopg
        except ImportError:
            print("DATABASE_URL points at PostgreSQL but psycopg is not "
                  "installed.\n  pip install 'psycopg[binary]'")
            return None
        try:
            with psycopg.connect(url, connect_timeout=15) as con:
                with con.cursor() as cur:
                    cur.execute(PG_QUERY)
                    fetched = cur.fetchall()
        except psycopg.OperationalError as exc:
            # Almost always a wrong or expired connection string. A stack trace
            # here tells the reader nothing they can act on.
            print(f"Could not connect to PostgreSQL.\n  {exc}\n"
                  "  Check DATABASE_URL - copy it again from the Neon "
                  "dashboard, and keep the ?sslmode=require suffix.")
            return None
        except psycopg.errors.UndefinedTable:
            print('No "ElicitationResponse" table in that database.\n'
                  "  The migrations have not been applied. From web/:\n"
                  "    npm run db:setup:postgres")
            return None
        print(f"Read {len(fetched)} response rows from PostgreSQL.")
        return [dict(zip(FIELDS, row)) for row in fetched]

    if not DB.exists():
        print(f"No database at {DB}, and no PostgreSQL DATABASE_URL found in "
              f"the environment or web/.env.\n"
              f"  Local:     run the web app and collect responses first\n"
              f"  Deployed:  put the Neon connection string in web/.env, or\n"
              f"             set DATABASE_URL before running this script")
        return None

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = con.execute(QUERY).fetchall()
    con.close()
    return [dict(r) for r in rows]


def load_responses() -> list[dict]:
    rows = _fetch_rows()
    if rows is None:
        return []

    out = []
    excluded: set[str] = set()
    for r in rows:
        code = (r["respondentCode"] or "").strip()
        if code.upper().startswith(EXCLUDED_PREFIXES):
            excluded.add(code)
            continue
        out.append({
            "respondent": r["respondentCode"],
            "years": r["yearsExperience"],
            "institution": r["institution"],
            "role": r["role"],
            "level": r["level"],
            "best": r["best"],
            "worst": r["worst"],
            "bestToOthers": json.loads(r["bestToOthers"]),
            "othersToWorst": json.loads(r["othersToWorst"]),
        })

    # Say so out loud. A response silently dropped is indistinguishable from one
    # never collected, and a participant coded by mistake in a way that matches
    # a reserved prefix should be visible rather than vanish.
    if excluded:
        print(f"Excluded {len(excluded)} test/pilot respondent(s): "
              f"{', '.join(sorted(excluded))}")
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true",
                        help="write derived weights into the criteria tree")
    args = parser.parse_args()

    responses = load_responses()
    if not responses:
        print("No usable elicitation responses found.")
        print("The criteria tree keeps weightStatus = PLACEHOLDER, and no scored")
        print("output may be reported as a research result.")
        return 1

    by_level: dict[str, list[dict]] = defaultdict(list)
    for r in responses:
        by_level[r["level"]].append(r)

    respondents = sorted({r["respondent"] for r in responses})
    print(f"{len(respondents)} respondent(s): {', '.join(respondents)}")
    print(f"{len(responses)} level-responses across {len(by_level)} levels\n")

    level_weights: dict[str, dict[str, float]] = {}
    consistency_rows = []
    dropped = 0

    for level, entries in sorted(by_level.items()):
        print("=" * 68)
        print(level)
        print("=" * 68)

        results = []
        for entry in entries:
            items = sorted(set(entry["bestToOthers"]) | set(entry["othersToWorst"]))
            try:
                res = solve_bwm(
                    items, entry["best"], entry["worst"],
                    entry["bestToOthers"], entry["othersToWorst"],
                )
            except Exception as exc:  # noqa: BLE001
                print(f"  {entry['respondent']}: FAILED ({exc})")
                continue

            flag = "" if res.reliable else "   <-- EXCLUDED (inconsistent)"
            print(f"  {entry['respondent']:<22} CR = {res.consistency_ratio:.3f}{flag}")
            consistency_rows.append({
                "level": level,
                "respondent": entry["respondent"],
                "consistency_ratio": round(res.consistency_ratio, 4),
                "usable": res.reliable,
            })
            if not res.reliable:
                dropped += 1
            results.append(res)

        usable = [r for r in results if r.reliable]
        if not usable:
            print("  no usable responses at this level - weights left unset")
            continue

        weights = aggregate(results)
        level_weights[level] = weights

        print()
        for item, w in sorted(weights.items(), key=lambda kv: -kv[1]):
            bar = "#" * int(round(w * 60))
            print(f"    {item:<26} {w:.4f}  {bar}")
        print()

    # The exclusion threshold is a design choice, so report what it costs rather
    # than only what it is. An examiner asking "why 0.25 and not 0.10?" is owed
    # the number of responses each answer would have discarded, and the gap in
    # the observed distribution that the chosen value sits in.
    observed = sorted((row["consistency_ratio"] for row in consistency_rows),
                      reverse=True)
    sensitivity = [
        {"threshold": t,
         "excluded": sum(1 for cr in observed if cr > t),
         "retained": sum(1 for cr in observed if cr <= t)}
        for t in (0.10, 0.15, 0.20, 0.25, 0.30)
    ]

    # --- persist the audit tables ------------------------------------------
    OUT_TABLES.mkdir(parents=True, exist_ok=True)
    with open(OUT_TABLES / "elicited_weights.json", "w", encoding="utf-8") as fh:
        json.dump({
            "respondents": respondents,
            "n_respondents": len(respondents),
            "n_level_responses": len(consistency_rows),
            "n_dropped_inconsistent": dropped,
            "consistency_threshold": CONSISTENCY_THRESHOLD,
            # statistics.median, not the middle element: with an even count the
            # middle element is one of two equally central values, and which one
            # it is depends on the sort direction.
            "consistency_median": round(
                statistics.median(observed) if observed else 0.0, 4),
            "consistency_highest": observed[:8],
            "threshold_sensitivity": sensitivity,
            "weights": level_weights,
        }, fh, indent=2)

    import csv
    with open(OUT_TABLES / "elicitation_consistency.csv", "w",
              newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["level", "respondent", "consistency_ratio", "usable"])
        writer.writeheader()
        writer.writerows(consistency_rows)

    print("=" * 68)
    print(f"{len(respondents)} respondents, {dropped} level-responses dropped "
          f"for CR > {CONSISTENCY_THRESHOLD}")
    print(f"Saved research/outputs/tables/elicited_weights.json")

    if not args.apply:
        print("\nDry run. Re-run with --apply to write these into the criteria tree.")
        return 0

    # --- write into the tree ------------------------------------------------
    tree = json.loads(TREE.read_text(encoding="utf-8"))

    for objective in tree["objectives"]:
        dim_weights = level_weights.get(f"objective:{objective['id']}")
        for dimension in objective["dimensions"]:
            if dim_weights and dimension["id"] in dim_weights:
                dimension["weight"] = round(dim_weights[dimension["id"]], 6)
            elif len(objective["dimensions"]) == 1:
                dimension["weight"] = 1.0

            crit_weights = level_weights.get(f"dimension:{dimension['id']}")
            if not crit_weights:
                continue
            for criterion in dimension["criteria"]:
                if criterion["id"] in crit_weights:
                    criterion["weight"] = round(crit_weights[criterion["id"]], 6)

    tree["weightStatus"] = {
        "state": "ELICITED",
        "detail": (
            f"Weights derived by Best-Worst Method from {len(respondents)} "
            f"respondent(s). {dropped} level-response(s) were excluded for "
            f"consistency ratio above {CONSISTENCY_THRESHOLD}. Aggregation is by "
            f"geometric mean over usable responses."
        ),
        "plannedMethod": tree["weightStatus"].get("plannedMethod"),
        "elicitation": {
            "method": "Best-Worst Method (Rezaei 2015), linear programme",
            "respondents": len(respondents),
            "date": date.today().isoformat(),
            "droppedInconsistent": dropped,
            "consistencyThreshold": CONSISTENCY_THRESHOLD,
        },
    }

    TREE.write_text(json.dumps(tree, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote elicited weights to {TREE.relative_to(ROOT)}")
    print("weightStatus is now ELICITED. Run `npm run sync-model` in web/.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
