"""Check that numbers quoted in the thesis match the generated result files.

Run:  python scripts/verify_claims.py

WHY THIS EXISTS
---------------
Every figure in the thesis is supposed to come from code in `research/`. Nothing
enforces that. Chapters are edited by hand, analyses are re-run with different
settings, and a number that was right in March quietly becomes wrong in
September while still reading perfectly well.

This script re-derives the load-bearing figures from
`research/outputs/tables/` and checks each against what the chapters actually
say. It has already earned its place: two values in Chapter 5 were wrong on
first drafting and were corrected against the generated tables.

Exit code 1 on any mismatch, so it can gate a build.
"""

from __future__ import annotations

import collections
import csv
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "research" / "outputs" / "tables"
CHAPTERS = ROOT / "docs" / "06-thesis"
PAPER = ROOT / "docs" / "07-paper" / "paper-term-contamination.md"


def load_csv(name: str) -> list[dict]:
    path = TABLES / name
    if not path.exists():
        return []
    with io.open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_json(name: str) -> dict:
    path = TABLES / name
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def documents() -> dict[str, str]:
    """The source chapters, the restructured sections, and the paper.

    Both copies of the thesis content are checked. The ch*.md chapters are the
    editable originals; the numbered 0N-*.md sections are generated from them by
    restructure_thesis.py and are what the submitted document is built from. If
    a chapter is edited without re-running the restructure, the two diverge and
    the submitted document silently carries stale numbers - so both are verified.
    """
    docs = {}
    for pattern in ("ch*.md", "0[0-9]-*.md"):
        for path in sorted(CHAPTERS.glob(pattern)):
            docs[path.name] = path.read_text(encoding="utf-8")
    if PAPER.exists():
        docs[PAPER.name] = PAPER.read_text(encoding="utf-8")
    return docs


def check_restructure_current() -> tuple[bool, str]:
    """Are the generated sections newer than the chapters they derive from?"""
    sources = list(CHAPTERS.glob("ch*.md"))
    generated = list(CHAPTERS.glob("0[1-9]-*.md"))
    if not sources or not generated:
        return True, "OK    restructure check skipped (files absent)"

    newest_source = max(p.stat().st_mtime for p in sources)
    oldest_generated = min(p.stat().st_mtime for p in generated)

    if newest_source > oldest_generated + 1:
        return False, ("FAIL  a source chapter is newer than the generated "
                       "sections - re-run restructure_thesis.py")
    return True, "OK    generated sections are current with source chapters"


HEADING = re.compile(r"^#{1,4}\s+(\d+(?:\.\d+)*[a-z]?(?:\.\d+)*)\s+(.*)$", re.M)


BODY_ORDER = ["01-introduction.md", "02-objectives.md", "03-literature-review.md",
              "04-methodology.md", "05-results.md", "06-discussion-conclusions.md",
              "08-appendices.md"]

# Everything that reaches the page. BODY_ORDER leaves out the front matter and
# the reference list because they carry no numbered sections, and the path check
# was reading BODY_ORDER - so "docs/02-literature/bibliography.md", printed in
# the preamble to the References, passed every build.
ALL_RENDERED = ["00-front-matter.md"] + BODY_ORDER[:-1] + ["07-references.md",
                                                           "08-appendices.md"]


def _body_text() -> str:
    return "\n".join((CHAPTERS / n).read_text(encoding="utf-8")
                     for n in BODY_ORDER if (CHAPTERS / n).exists())


def check_no_self_references() -> list[tuple[bool, str]]:
    """No section may point the reader at itself.

    "Full specification in Section 4.4" was printed inside Section 4.4. The
    reference was correct in the draft, where that material sat in a different
    chapter, and the restructure's mapping had no entry for 4.4, so it was left
    pointing where it already was. Every cross-reference resolved to a real
    section, so the existing check passed.
    """
    offenders = []
    for path in sorted(CHAPTERS.glob("0[0-9]-*.md")):
        current = None
        for line in path.read_text(encoding="utf-8").splitlines():
            head = HEADING.match(line)
            if head:
                current = head.group(1)
                continue
            if not current:
                continue
            for m in CROSSREF.finditer(line):
                if m.group(1) == current:
                    offenders.append(f"{path.name}: {current} -> itself")
    if offenders:
        out = [(False, f"FAIL  {len(offenders)} section(s) reference "
                       f"themselves")]
        return out + [(False, f"        {o}") for o in offenders[:8]]
    return [(True, "OK    no section references itself")]


def check_abstract_length() -> list[tuple[bool, str]]:
    """The guideline sets the abstract at 200-300 words."""
    path = CHAPTERS / "00-front-matter.md"
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    if "# ABSTRACT" not in text:
        return [(False, "FAIL  no abstract found")]
    body = text.split("# ABSTRACT", 1)[1].split("**Keywords:**")[0]
    n = len(body.split())
    if 200 <= n <= 300:
        return [(True, f"OK    abstract length                          {n} words")]
    return [(False, f"FAIL  abstract is {n} words, outside the 200-300 the "
                    f"guideline specifies")]


def check_exhibits_are_referenced() -> list[tuple[bool, str]]:
    """Every table and figure must be named by number somewhere in the text.

    The guideline requires each to appear as close as possible to its first
    mention, which presupposes a mention. In the draft of 17 September not one
    of the 32 tables or 7 figures was referred to anywhere, so a reader met each
    one with no idea why it was there.
    """
    text = _body_text()
    if not text:
        return []
    defined = ([("tbl", m) for m in
                re.findall(r"^\[Table:\s*([a-z0-9-]+)\s*\|", text, re.M)]
               + [("fig", m) for m in
                  re.findall(r"^\[Image:\s*\S+\s*\|\s*([a-z0-9-]+)\s*\|",
                             text, re.M)])
    referenced = set(re.findall(r"@(?:tbl|fig):([a-z0-9-]+)", text))

    orphans = [f"{kind}:{key}" for kind, key in defined if key not in referenced]
    unkeyed = (len(re.findall(r"^\[Table:\s*[^|\]]+\]$", text, re.M))
               + len(re.findall(r"^\[Image:\s*[^|]+\|\s*[^|\]]+\]$", text, re.M)))

    out = []
    if unkeyed:
        out.append((False, f"FAIL  {unkeyed} exhibit(s) carry no reference key"))
    if orphans:
        out.append((False, f"FAIL  {len(orphans)} exhibit(s) never referred to "
                           f"in the text"))
        out += [(False, f"        {o}") for o in orphans[:8]]
    if not out:
        out.append((True, f"OK    all {len(defined)} tables and figures are "
                          f"referred to by number"))
    out.extend(_check_exhibits_are_read())
    return out


def _check_exhibits_are_read() -> list[tuple[bool, str]]:
    """Is there prose after each exhibit saying what it shows?

    Naming a table in the sentence before it is half the job. The guideline's
    own worked example names the exhibit and then states what the reader should
    take from it. All six figures in Chapter 5 were followed immediately by the
    next heading, so each was shown and then abandoned.
    """
    silent = []
    for name in BODY_ORDER:
        path = CHAPTERS / name
        if not path.exists():
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        i = 0
        while i < len(lines):
            marker = re.match(
                r"^\[(?:Table:\s*|Image:\s*\S+\s*\|\s*)([a-z0-9-]+)\s*\|",
                lines[i])
            if not marker:
                i += 1
                continue
            j = i + 1
            while j < len(lines) and (not lines[j].strip()
                                      or lines[j].strip().startswith("|")):
                j += 1
            after = []
            while j < len(lines):
                s = lines[j].strip()
                if not s:
                    if after:
                        break
                    j += 1
                    continue
                if s.startswith(("#", "[")) or re.match(r"^\s*([-*]\s|\d+\.\s)",
                                                        lines[j]):
                    break
                after.append(s)
                j += 1
            if len(" ".join(after)) < 60:
                silent.append(f"{name[:2]}: {marker.group(1)}")
            i += 1
    if silent:
        out = [(False, f"FAIL  {len(silent)} exhibit(s) have no sentence "
                       f"reading them")]
        return out + [(False, f"        {s}") for s in silent[:8]]
    return [(True, "OK    every table and figure is read in the text that "
                   "follows it")]


def check_abbreviations_expanded() -> list[tuple[bool, str]]:
    """Each abbreviation must be explained in the text where it first appears.

    Checked against the List of Abbreviations, so adding an entry to the list
    without introducing it in the text fails, and so does the reverse.
    """
    front = CHAPTERS / "00-front-matter.md"
    text = _body_text()
    if not front.exists() or not text:
        return []
    table = front.read_text(encoding="utf-8")
    if "# LIST OF ABBREVIATIONS" not in table:
        return []
    table = table.split("# LIST OF ABBREVIATIONS", 1)[1]
    entries = re.findall(r"^\|\s*([A-Z][A-Za-z0-9]{1,9})\s*\|\s*([^|]+?)\s*\|$",
                         table, re.M)

    unexplained = []
    for abbr, meaning in entries:
        # A trailing plural "s" is still a use of the abbreviation: "SMEs" is
        # where a reader first meets SME, and the expansion has to be there.
        m = re.search(rf"(?<![A-Za-z]){re.escape(abbr)}s?(?![A-Za-z])", text)
        if not m:
            unexplained.append(f"{abbr} (listed but never used)")
            continue
        # The expansion has to be near the first use, not anywhere at all.
        window = text[max(0, m.start() - 260):m.start() + 260].lower()
        head = meaning.split("(")[0].strip().lower()
        if head[:22] not in window:
            unexplained.append(f"{abbr} first used without its expansion")

    if unexplained:
        out = [(False, f"FAIL  {len(unexplained)} abbreviation(s) not "
                       f"explained at first use")]
        return out + [(False, f"        {u}") for u in unexplained[:8]]
    return [(True, f"OK    all {len(entries)} abbreviations expanded at first "
                   f"use")]


def check_no_repository_paths() -> list[tuple[bool, str]]:
    """No file paths, script names or shell commands in the thesis body.

    An examiner reads the thesis without the repository, so "run
    research/src/bwm.py" is a dead reference and reads as a note the author
    forgot to take out. 45 of them were in the submitted draft.

    Checked over everything that reaches the page, not just the numbered
    chapters: the one that survived the first sweep was in the front matter of
    the reference list.
    """
    text = "\n".join((CHAPTERS / n).read_text(encoding="utf-8")
                     for n in ALL_RENDERED if (CHAPTERS / n).exists())
    if not text:
        return []
    patterns = {
        "a code span": r"`[^`]+`",
        "a script name": r"\b\w+\.py\b",
        "a repository path": r"\b(?:research|scripts|web|docs|shared)/[\w./-]+",
        "a shell command": r"\b(?:npm|python|cd|pip) +[\w./:-]+",
    }
    hits = []
    for label, pattern in patterns.items():
        found = re.findall(pattern, text)
        if found:
            hits.append((label, sorted(set(found))[:4], len(found)))
    if hits:
        out = [(False, "FAIL  the thesis body still refers to the repository")]
        for label, sample, n in hits:
            out.append((False, f"        {n} x {label}: {', '.join(sample)}"))
        return out
    return [(True, "OK    no file paths or commands in the thesis body")]


def check_headings_are_numbered() -> list[tuple[bool, str]]:
    """Every subheading in a source chapter must carry a section number.

    THIS EXISTS BECAUSE SECTION 6.2 - THE ANSWERS TO THE RESEARCH QUESTIONS -
    WAS SILENTLY EMPTY IN A SUBMITTED DRAFT. Its four subheadings were written
    as "RQ1 - Can the instrument be formalised?" with no number. The restructure
    selects blocks by heading number, so an unnumbered heading matches nothing
    and is dropped with its entire body. Coverage checking did not catch it
    either: that check compares heading TITLES, and it collects titles with the
    same numbered pattern, so an unnumbered heading is invisible to both.

    The chapter title itself is exempt, as is a trailing per-chapter reference
    list, which is drafting scaffolding and is not meant to be carried across.
    """
    exempt = re.compile(r"^(references|references cited in this chapter)$", re.I)
    unnumbered: list[str] = []
    for path in sorted(CHAPTERS.glob("ch*.md")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.startswith("##"):
                continue          # "# Chapter 5 - ..." is the title, exempt
            title = line.lstrip("#").strip()
            if HEADING.match(line) or exempt.match(title):
                continue
            unnumbered.append(f"{path.name}: {title[:58]}")

    if unnumbered:
        out = [(False, f"FAIL  {len(unnumbered)} source heading(s) carry no "
                       f"section number and will be dropped")]
        out += [(False, f"        {u}") for u in unnumbered[:8]]
        return out
    return [(True, "OK    every source subheading carries a section number")]


def check_section_coverage() -> list[tuple[bool, str]]:
    """Did every drafted section survive into the generated document?

    THIS EXISTS BECAUSE THE VERIFIER ONCE PASSED 26/26 WHILE FOUR WHOLE SECTIONS
    WERE MISSING. restructure_thesis.py selected blocks by heading prefix and
    silently skipped the letter-suffixed ones (5.5a, 5.5b, 5.6a, 5.6b), so
    calibration, cost analysis, weight sensitivity and objective separability
    never reached the submitted document. Every numeric check still passed: the
    values were quoted in the ch*.md originals, which this script also reads.

    Matching is by heading title, not number, because the whole point of the
    restructure is that the numbers change.
    """
    def titles(pattern: str) -> collections.Counter:
        found: collections.Counter = collections.Counter()
        for path in sorted(CHAPTERS.glob(pattern)):
            for _, title in HEADING.findall(path.read_text(encoding="utf-8")):
                found[title.strip().lower()] += 1
        return found

    source = titles("ch*.md")
    generated = titles("0[0-9]-*.md")
    if not source or not generated:
        return [(True, "OK    section coverage skipped (files absent)")]

    missing = sorted(t for t in source if generated[t] < source[t])
    out = []
    if missing:
        out.append((False, f"FAIL  {len(missing)} drafted section(s) missing "
                           f"from the generated document"))
        for title in missing[:8]:
            out.append((False, f"        dropped: {title[:64]}"))
    else:
        out.append((True, f"OK    all {len(source)} drafted sections present "
                          f"in the generated document"))

    # Contiguity: a gap in the generated numbering means a block was lost or
    # a remap entry is wrong, even when every title happens to be accounted for.
    #
    # Checked at EVERY depth, not just the top. Checking only two-part numbers
    # let a subsection through with the wrong parent: a new 5.3.5 was added to
    # the source chapter, no remap entry was written for it, and it appeared in
    # the generated Results between 5.10.4 and 5.11 still numbered 5.3.5. Every
    # other check passed - the title was present, the top-level numbering was
    # contiguous, and nothing referenced it.
    gaps = []
    for path in sorted(CHAPTERS.glob("0[0-9]-*.md")):
        by_parent: dict[str, list[int]] = {}
        for num, _ in HEADING.findall(path.read_text(encoding="utf-8")):
            parts = num.split(".")
            if not parts[-1].isdigit():
                continue
            parent = ".".join(parts[:-1])
            by_parent.setdefault(parent, []).append(int(parts[-1]))
        for parent, seq in by_parent.items():
            for prev, nxt in zip(seq, seq[1:]):
                if nxt not in (prev, prev + 1):
                    label = f"{parent}." if parent else ""
                    gaps.append(f"{path.name}: {label}{prev} -> {label}{nxt}")
    if gaps:
        out.append((False, f"FAIL  numbering gap in generated sections: "
                           f"{'; '.join(gaps[:4])}"))
    else:
        out.append((True, "OK    generated section numbering is contiguous"))
    return out


CROSSREF = re.compile(r"(?:§|\b[Ss]ection )(\d+(?:\.\d+)+[a-z]?(?:\.\d+)*)")


def check_cross_references() -> tuple[bool, str]:
    """Does every section a generated chapter points at actually exist?

    The restructure renumbers sections and rewrites references to match. It got
    this wrong twice in ways nothing detected: substitutions were applied one
    mapping entry at a time, so a reference rewritten by one rule was rewritten
    again by the next, and a reference to the completeness gate ended up pointing
    at the contaminated-predictor section. Both targets existed, so the document
    read perfectly and was wrong.

    This cannot catch a reference that points at a real but incorrect section. It
    does catch every reference pointing at a section that is not there at all,
    which is what a renumbering slip usually produces.
    """
    numbers: set[str] = set()
    refs: dict[str, set[str]] = {}
    for path in sorted(CHAPTERS.glob("0[0-9]-*.md")):
        text = path.read_text(encoding="utf-8")
        numbers.update(n for n, _ in HEADING.findall(text))
        refs[path.name] = set(CROSSREF.findall(text))

    if not numbers:
        return True, "OK    cross-reference check skipped (files absent)"

    dangling = sorted(
        f"{name}:{ref}"
        for name, found in refs.items()
        for ref in found
        # A reference may name a parent of a numbered heading (5.16 exists as
        # 5.16.1) - only flag what matches nothing at any depth.
        if ref not in numbers
        and not any(n.startswith(ref + ".") for n in numbers)
    )
    if dangling:
        return False, (f"FAIL  {len(dangling)} cross-reference(s) point at "
                       f"sections that do not exist: {', '.join(dangling[:6])}")
    total = sum(len(v) for v in refs.values())
    return True, f"OK    all {total} cross-references resolve to real sections"


def check(label: str, expected: str, docs: dict[str, str],
          required_in: list[str] | None = None) -> tuple[bool, str]:
    """Is `expected` present verbatim in the documents that should carry it?

    With no `required_in`, the value must appear somewhere - it is quoted in
    whichever chapters happen to discuss it. With `required_in`, it must appear
    in *every* named document. That distinction matters: naming both the source
    chapter and the generated section is how a value that is dropped during the
    restructure gets caught, and an any-of test would not catch it.
    """
    targets = required_in or list(docs)
    found = [name for name in targets if expected in docs.get(name, "")]

    if required_in:
        absent = [name for name in targets if name not in found]
        if absent:
            return False, (f"FAIL  {label:<46} {expected:>10}  "
                           f"missing from {', '.join(absent)}")
        return True, f"OK    {label:<46} {expected:>10}  ({', '.join(found)})"

    if found:
        return True, f"OK    {label:<46} {expected:>10}  ({', '.join(found)})"
    return False, f"FAIL  {label:<46} {expected:>10}  not found in {targets}"


def main() -> int:
    docs = documents()
    if not docs:
        print("No chapters found.")
        return 1

    checks: list[tuple[bool, str]] = []

    # ---- leakage findings --------------------------------------------------
    leak = load_json("leakage_findings.json")
    if leak:
        checks.append(check("roundness AUC", f"{leak['roundness_auc']:.4f}", docs))
        checks.append(check("round share, repaid",
                            f"{leak['round_share_repaid'] * 100:.1f}%", docs))
        checks.append(check("round share, charged off",
                            f"{leak['round_share_default'] * 100:.1f}%", docs))
        checks.append(check("survival correlation",
                            f"{leak['survival_correlation']:.3f}", docs))
        checks.append(check("cohort size", f"{leak['n']:,}", docs))

    # ---- benchmark AUCs ----------------------------------------------------
    bench = load_csv("benchmark_results.csv")
    key_models = [
        ("clean", "temporal", "Gradient boosting"),
        ("clean", "random", "Gradient boosting"),
        ("contaminated", "temporal", "Gradient boosting"),
        ("contaminated", "random", "Gradient boosting"),
        ("clean", "temporal", "Logistic regression"),
        ("clean", "random", "Expert scorecard (unfitted)"),
        ("clean", "temporal", "Expert scorecard (unfitted)"),
    ]
    for spec, protocol, model in key_models:
        row = next((r for r in bench if r["spec"] == spec
                    and r["protocol"] == protocol and r["model"] == model), None)
        if row:
            checks.append(check(f"{model[:22]} {spec}/{protocol}",
                                f"{float(row['auc']):.4f}", docs))

    # ---- derived quantities ------------------------------------------------
    def auc(spec, protocol, model):
        r = next((x for x in bench if x["spec"] == spec
                  and x["protocol"] == protocol and x["model"] == model), None)
        return float(r["auc"]) if r else None

    if bench:
        gbm_c = auc("contaminated", "temporal", "Gradient boosting")
        gbm_k = auc("clean", "temporal", "Gradient boosting")
        if gbm_c and gbm_k:
            checks.append(check("leakage inflation (temporal)",
                                f"{gbm_c - gbm_k:.3f}", docs))

        rand_k = auc("clean", "random", "Gradient boosting")
        if rand_k and gbm_k:
            checks.append(check("random-split optimism",
                                f"{rand_k - gbm_k:.3f}", docs))

    # ---- weight sensitivity ------------------------------------------------
    sens = load_csv("weight_sensitivity.csv")
    for row in sens:
        if row["objective"] == "credit_risk" and float(row["perturbation"]) == 0.25:
            checks.append(check("weight sensitivity rho at +/-25%",
                                f"{float(row['spearman_mean']):.4f}", docs,
                                ["ch5-empirical-validation.md", "05-results.md"]))
            checks.append(check("band stability at +/-25%",
                                f"{float(row['band_agreement_mean']) * 100:.1f}%", docs,
                                ["ch5-empirical-validation.md", "05-results.md"]))

    # ---- objective separability (RQ4) --------------------------------------
    indep = load_json("objective_independence.json")
    if indep:
        checks.append(check("objectives Pearson r",
                            f"+{indep['pearson_r']:.4f}", docs,
                            ["ch5-empirical-validation.md", "05-results.md"]))
        checks.append(check("disjoint-input r",
                            f"+{indep['disjoint_pearson_r']:.4f}", docs,
                            ["ch5-empirical-validation.md", "05-results.md"]))
        checks.append(check("bands disagree",
                            f"{(1 - indep['band_same']) * 100:.1f}%", docs))
        checks.append(check("two or more bands apart",
                            f"{indep['band_two_plus_apart'] * 100:.1f}%", docs))

    # ---- the artefact in SBA's own FOIA records -----------------------------
    foia = load_json("foia_replication.json")
    if foia:
        BOTH_F = ["ch5-empirical-validation.md", "05-results.md"]
        by_name = {d["dataset"].split(" programme")[0]: d
                   for d in foia["datasets"]}
        seven = by_name.get("7(a)")
        if seven:
            checks.append(check("FOIA 7(a) resolved facilities",
                                f"{seven['n_resolved']:,}", docs, BOTH_F))
            checks.append(check("FOIA 7(a) round share, repaid",
                                f"{seven['round_share_repaid'] * 100:.2f}%",
                                docs, BOTH_F))
            checks.append(check("FOIA 7(a) round share, charged off",
                                f"{seven['round_share_default'] * 100:.2f}%",
                                docs, BOTH_F))
            checks.append(check("FOIA 7(a) roundness AUC",
                                f"{seven['roundness_auc']:.4f}", docs, BOTH_F))
        five = by_name.get("504")
        if five:
            checks.append(check("FOIA 504 roundness AUC",
                                f"{five['roundness_auc']:.4f}", docs, BOTH_F))
            checks.append(check("FOIA 504 round share, charged off",
                                f"{five['round_share_default'] * 100:.2f}%",
                                docs, BOTH_F))
        later = next((d for d in foia["datasets"]
                      if "FY2010-2019" in d["dataset"]), None)
        if later:
            checks.append(check("FOIA 7(a) 2010s resolved",
                                f"{later['n_resolved']:,}", docs, BOTH_F))
            checks.append(check("FOIA 7(a) 2010s roundness AUC",
                                f"{later['roundness_auc']:.4f}", docs, BOTH_F))
            checks.append(check("FOIA 7(a) 2010s round share, repaid",
                                f"{later['round_share_repaid'] * 100:.2f}%",
                                docs, BOTH_F))
            checks.append(check("FOIA 7(a) 2010s round share, charged off",
                                f"{later['round_share_default'] * 100:.2f}%",
                                docs, BOTH_F))
        if foia.get("combined_resolved_7a"):
            checks.append(check("FOIA combined resolved facilities",
                                f"{foia['combined_resolved_7a']:,}", docs,
                                BOTH_F))
            checks.append(check("FOIA span, lowest AUC",
                                f"{foia['span_low_auc']:.4f}", docs, BOTH_F))
            checks.append(check("FOIA span, highest AUC",
                                f"{foia['span_high_auc']:.4f}", docs, BOTH_F))

        if foia.get("five04_share_240_months") is not None:
            checks.append(check("FOIA 504 share at 240 months",
                                f"{foia['five04_share_240_months'] * 100:.1f}%",
                                docs, BOTH_F))

    foia_years = load_csv("foia_7a_by_year.csv")
    if foia_years:
        aucs = [float(r["auc"]) for r in foia_years]
        checks.append(check("FOIA 7(a) yearly AUC, lowest",
                            f"{min(aucs):.4f}", docs,
                            ["ch5-empirical-validation.md", "05-results.md"]))
        checks.append(check("FOIA 7(a) yearly AUC, highest",
                            f"{max(aucs):.4f}", docs,
                            ["ch5-empirical-validation.md", "05-results.md"]))

    # ---- is twelve doing the work? -----------------------------------------
    mod = load_csv("modulus_probe.csv")
    if mod:
        BOTH_M = ["ch5-empirical-validation.md", "05-results.md"]
        by_m = {int(r["modulus"]): r for r in mod}
        for m in (12, 6, 4, 3, 2, 11, 13):
            row = by_m.get(m)
            if row and row["raw_auc"]:
                checks.append(check(f"modulus {m} raw AUC",
                                    f"{float(row['raw_auc']):.4f}", docs,
                                    BOTH_M))
        # The residual signal that refines the finding rather than breaking it.
        for m in (3, 6):
            row = by_m.get(m)
            if row and row["auc_within_non_multiples_of_12"]:
                checks.append(check(
                    f"modulus {m} residual AUC",
                    f"{float(row['auc_within_non_multiples_of_12']):.4f}",
                    docs, BOTH_M))

    # ---- the RealEstate feature in the dataset's own documentation ---------
    re_probe = load_json("realestate_probe.json")
    if re_probe:
        BOTH_RE = ["ch5-empirical-validation.md", "05-results.md"]
        checks.append(check("RealEstate default rate",
                            f"{re_probe['default_real_estate'] * 100:.2f}%",
                            docs, BOTH_RE))
        checks.append(check("non-RealEstate default rate",
                            f"{re_probe['default_other'] * 100:.2f}%",
                            docs, BOTH_RE))
        checks.append(check("RealEstate censored share",
                            f"{re_probe['censored_share_real_estate'] * 100:.1f}%",
                            docs, BOTH_RE))
        checks.append(check("RealEstate matured default",
                            f"{re_probe['default_real_estate_matured'] * 100:.2f}%",
                            docs, BOTH_RE))
        checks.append(check("RealEstate round-term share",
                            f"{re_probe['round_share_real_estate'] * 100:.2f}%",
                            docs, BOTH_RE))
        irregular = re_probe["stratified"]["irregular term"]
        checks.append(check("irregular-term default, non-RealEstate",
                            f"{irregular['default_other'] * 100:.2f}%",
                            docs, BOTH_RE))

    # ---- elicitation --------------------------------------------------------
    elicited = load_json("elicited_weights.json")
    if elicited:
        BOTH_E = ["ch6-results-discussion-conclusion.md",
                  "06-discussion-conclusions.md"]
        checks.append(check("elicitation respondents",
                            str(elicited["n_respondents"]), docs, BOTH_E))
        w = elicited["weights"].get("objective:credit_risk", {})
        for item, label in (("project_viability", "project viability weight"),
                            ("risk_security", "risk & security weight")):
            if item in w:
                checks.append(check(label, f"{w[item]:.4f}", docs, BOTH_E))

    vs = load_json("elicited_vs_placeholder.json")
    if vs:
        BOTH_E = ["ch6-results-discussion-conclusion.md",
                  "06-discussion-conclusions.md"]
        checks.append(check("largest within-level weight ratio",
                            f"{vs['largest_within_level_ratio']:.2f}", docs,
                            BOTH_E))
        for oid, label in (("credit_risk", "credit"),
                           ("development_impact", "development")):
            o = vs["objectives"].get(oid)
            if o:
                checks.append(check(f"elicited-vs-placeholder rho, {label}",
                                    f"{o['spearman']:.4f}", docs, BOTH_E))
                checks.append(check(f"same band after elicitation, {label}",
                                    f"{o['same_band'] * 100:.1f}%", docs,
                                    BOTH_E))

    # ---- fairness / disparate impact ---------------------------------------
    BOTH = ["ch5-empirical-validation.md", "05-results.md"]
    fair = load_csv("fairness_groups.csv")
    if fair:
        GBM = "Gradient boosting (clean, temporal)"
        CARD = "Expert scorecard (unfitted)"

        def cell(model: str, attribute: str, group: str, field: str) -> str:
            row = next(r for r in fair if r["model"] == model
                       and r["attribute"] == attribute and r["group"] == group)
            return row[field]

        # The error-rate disparities - creditworthy applicants declined.
        for label, model, attr, grp in (
            ("micro-enterprise good declined", GBM,
             "Firm size (employees)", "Micro (1-4)"),
            ("large-firm good declined", GBM,
             "Firm size (employees)", "Large (100+)"),
            ("smallest-facility good declined", GBM,
             "Facility size", "Smallest 25%"),
            ("largest-facility good declined", GBM,
             "Facility size", "Largest 25%"),
        ):
            checks.append(check(
                label,
                f"{float(cell(model, attr, grp, 'fpr_good_declined')) * 100:.2f}%",
                docs, BOTH))

        # The scorecard penalises the best-performing sector hardest.
        checks.append(check(
            "agriculture good declined (scorecard)",
            f"{float(cell(CARD, 'Sector', 'Agriculture/Forestry/Fishing', 'fpr_good_declined')) * 100:.2f}%",
            docs, BOTH))
        checks.append(check(
            "agriculture default rate",
            f"{float(cell(CARD, 'Sector', 'Agriculture/Forestry/Fishing', 'default_rate')) * 100:.2f}%",
            docs, BOTH))

    fair_sum = load_json("fairness_summary.json")
    if fair_sum:
        by_key = {(d["model"], d["attribute"]): d
                  for d in fair_sum["disparities"]}
        for model, attr in (("Gradient boosting (clean, temporal)", "Rurality"),
                            ("Expert scorecard (unfitted)", "Rurality")):
            d = by_key.get((model, attr))
            if d:
                checks.append(check(
                    f"disparate impact, {model.split()[0].lower()} {attr.lower()}",
                    f"{d['disparate_impact_ratio']:.3f}", docs, BOTH))
        d = by_key.get(("Gradient boosting (clean, temporal)",
                        "Firm size (employees)"))
        if d:
            checks.append(check("micro/large equal-opportunity ratio",
                                f"{d['equal_opportunity_ratio']:.2f}", docs,
                                BOTH))

        # Bootstrap intervals and the permutation floor. Without these the
        # disparity ratios are min/max statistics quoted without uncertainty.
        for model, attr, label in (
            ("Gradient boosting (clean, temporal)", "Rurality",
             "GBM rurality DI interval"),
            ("Expert scorecard (unfitted)", "Rurality",
             "scorecard rurality DI interval"),
            ("Expert scorecard (unfitted)", "Firm size (employees)",
             "scorecard firm-size DI interval"),
        ):
            d = by_key.get((model, attr))
            if d and d.get("di_lo") is not None:
                checks.append(check(
                    label, f"[{d['di_lo']:.3f}, {d['di_hi']:.3f}]", docs, BOTH))

        nulls = [d["null_ratio_median"] for d in fair_sum["disparities"]
                 if d.get("null_ratio_median") is not None]
        if nulls:
            checks.append(check("permutation floor, lowest",
                                f"{min(nulls):.3f}", docs, BOTH))
            checks.append(check("permutation floor, highest",
                                f"{max(nulls):.3f}", docs, BOTH))

    # ---- what the models do with withheld information ----------------------
    miss = load_json("missingness_summary.json")
    if miss:
        gbm = miss["models"]["Gradient boosting (native NaN)"]
        checks.append(check("no-information decline threshold",
                            f"{gbm['decline_threshold']:.4f}", docs, BOTH))
        checks.append(check("baseline mean P(default)",
                            f"{gbm['baseline_mean_p'] * 100:.2f}%", docs, BOTH))
        checks.append(check(
            "share scored less risky when withholding",
            f"{gbm['share_scored_less_risky_when_withheld'] * 100:.1f}%",
            docs, BOTH))
        checks.append(check("complete records analysed",
                            f"{miss['n_complete_records']:,}", docs, BOTH))

        # Threshold independence: the finding must not rest on one policy.
        info = miss.get("no_information_applicant", {})
        for model_key, label in (
            ("Gradient boosting (native NaN)", "GBM"),
            ("Logistic regression (median imputation)", "logistic"),
        ):
            entry = info.get(model_key)
            if entry:
                checks.append(check(
                    f"{label} no-information percentile",
                    f"{entry['percentile_among_real_applicants'] * 100:.1f}th",
                    docs, BOTH))
                checks.append(check(
                    f"{label} withholding crossover",
                    f"{entry['crossover_decline_share'] * 100:.1f}%",
                    docs, BOTH))

    # ---- calibration --------------------------------------------------------
    calib = load_csv("calibration.csv")
    for row in calib:
        if row["protocol"] == "temporal" and row["model"].startswith("Gradient"):
            checks.append(check("GBM temporal reliability",
                                f"{float(row['reliability']):.5f}", docs))
        if row["protocol"] == "random" and row["model"].startswith("Gradient"):
            checks.append(check("GBM random reliability",
                                f"{float(row['reliability']):.5f}", docs))

    # ---- model structure ---------------------------------------------------
    tree = json.loads(
        (ROOT / "shared" / "model" / "criteria-tree.json").read_text(encoding="utf-8")
    )
    n_criteria = sum(len(d["criteria"]) for o in tree["objectives"]
                     for d in o["dimensions"])
    n_dims = sum(len(o["dimensions"]) for o in tree["objectives"])
    checks.append(check("criteria count", str(n_criteria), docs))
    checks.append(check("dimension count", str(n_dims), docs))

    checks.append(check_restructure_current())
    checks.extend(check_headings_are_numbered())
    checks.extend(check_no_self_references())
    checks.extend(check_abstract_length())
    checks.extend(check_exhibits_are_referenced())
    checks.extend(check_abbreviations_expanded())
    checks.extend(check_no_repository_paths())
    checks.extend(check_section_coverage())
    checks.append(check_cross_references())

    # ---- placeholder-weight guard -----------------------------------------
    state = tree["weightStatus"]["state"]
    placeholder_claimed = any(
        "PLACEHOLDER" in text for text in docs.values()
    )
    if state == "PLACEHOLDER" and not placeholder_claimed:
        checks.append((False,
                       "FAIL  weights are PLACEHOLDER but no chapter says so"))
    elif state == "ELICITED" and placeholder_claimed:
        checks.append((False,
                       "FAIL  weights are ELICITED but a chapter still says PLACEHOLDER"))
    else:
        checks.append((True, f"OK    weight status consistent ({state})"))

    # ---- report ------------------------------------------------------------
    print("Verifying thesis claims against generated results")
    print("=" * 78)
    for ok, line in checks:
        print(line)

    failed = sum(1 for ok, _ in checks if not ok)
    print("=" * 78)

    if failed:
        print(f"{failed} of {len(checks)} checks FAILED.")
        print()
        print("A failure means a number in the thesis no longer matches the")
        print("result files. Either the analysis was re-run and the chapter is")
        print("stale, or the chapter was edited by hand. Fix the chapter — never")
        print("adjust this script to make it pass.")
        return 1

    print(f"All {len(checks)} checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
