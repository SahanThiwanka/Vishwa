"""Reorganise the drafted chapters into the NSBM-mandated section order.

Run:  python scripts/restructure_thesis.py

The guideline requires: Introduction, Objectives, Literature Review, Methodology,
Results, Discussion and Conclusions, References, Appendices. The draft was
written as six chapters that do not map one-to-one onto that list - in
particular, the design chapter contains both *how the artefact was built*
(methodology) and *what the artefact is* (a result), and those have to be
separated.

This script performs the mechanical part: splitting each source chapter at its
headings, selecting blocks by heading prefix, and renumbering them into the new
section. Editorial glue - the framing paragraphs that make the new sections read
as wholes - lives in this file so the transformation is reproducible rather than
a one-off hand edit.

Re-run it after editing any source chapter.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CH = ROOT / "docs" / "06-thesis"


def blocks(path: Path) -> list[tuple[str, str]]:
    """Split a chapter into (heading, body) pairs, preserving order."""
    text = path.read_text(encoding="utf-8")
    parts = re.split(r"^(#{1,4} .*)$", text, flags=re.M)

    out: list[tuple[str, str]] = []
    preamble = parts[0].strip()
    if preamble:
        out.append(("", preamble))
    for i in range(1, len(parts), 2):
        out.append((parts[i].strip(), parts[i + 1].rstrip()))
    return out


def number_of(head: str) -> str:
    """The section number a heading opens with, e.g. 5.6a.2.

    The trailing `(?:\\.\\d+)*` is not decoration: the draft numbers subsections
    of a suffixed section as 5.6a.1, and without it the match stopped at the
    letter. The ".1" was then left behind in the title, producing headings that
    read "5.16 .1 Method" one level too shallow.
    """
    m = re.match(r"^#+\s+(\d+(?:\.\d+)*[a-z]?(?:\.\d+)*)", head)
    return m.group(1) if m else ""


def _matches(num: str, prefix: str) -> bool:
    """Does heading number `num` fall under `prefix`?

    Must accept the draft's letter-suffixed headings: 5.5a and 5.6b are
    subsections of 5.5 and 5.6. An earlier version tested only `num == prefix`
    or `num.startswith(prefix + ".")`, which silently dropped four whole
    sections - calibration, cost analysis, weight sensitivity and objective
    separability - from the generated Results. They were still present in the
    source chapter, so nothing failed; the numbering simply jumped 5.12 to 5.15.
    """
    return re.match(rf"^{re.escape(prefix)}(\.|[a-z]|$)", num) is not None


def select(src: list[tuple[str, str]], prefixes: tuple[str, ...],
           exclude: tuple[str, ...] = ()) -> list[tuple[str, str]]:
    """Blocks whose heading number falls under one of `prefixes`."""
    chosen = []
    for head, body in src:
        num = number_of(head)
        if not num:
            continue
        if any(_matches(num, e) for e in exclude):
            continue
        if any(_matches(num, p) for p in prefixes):
            chosen.append((head, body))
    return chosen


def renumber(blocks_in: list[tuple[str, str]], old: str, new: str,
             remap: dict[str, str] | None = None) -> list[tuple[str, str]]:
    """Rewrite heading numbers from one section into another.

    `remap` handles the non-mechanical cases - the draft used suffixed headings
    such as 5.6a and 5.6b, which the guideline does not permit (Arabic only, at
    most three decimals).
    """
    out = []
    for head, body in blocks_in:
        num = number_of(head)
        if not num:
            out.append((head, body))
            continue

        target = None
        if remap and num in remap:
            target = remap[num]
        elif num == old:
            target = new
        elif num.startswith(old + "."):
            target = new + num[len(old):]

        if target is None:
            out.append((head, body))
            continue

        hashes = head.split(" ")[0]
        title = head[len(hashes):].strip()
        title = title[len(num):].strip()
        level = min(target.count(".") + 1, 4)
        out.append((f"{'#' * level} {target} {title}", body))
    return out


def write(path: Path, title: str, blocks_out: list[tuple[str, str]],
          intro: str = "") -> None:
    lines = [f"# {title}", ""]
    if intro:
        lines += [intro.strip(), ""]
    for head, body in blocks_out:
        if head:
            lines.append(head)
        if body.strip():
            lines.append("")
            lines.append(body.strip())
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    words = len(" ".join(b for _, b in blocks_out).split())
    print(f"  {path.name:<32} {len(blocks_out):>3} blocks  ~{words:,} words")


NUM = r"\d+(?:\.\d+)*[a-z]?(?:\.\d+)*"
REFERENCE = re.compile(
    rf"(?P<lead>§|\b[Ss]ection )(?P<a>{NUM})"
    rf"(?P<dash>\s*[–—-]\s*(?P<b>{NUM}))?"
)


def fix_cross_references(path: Path, mapping: dict[str, str]) -> None:
    """Update section cross-references after renumbering.

    ONE simultaneous pass, deliberately. Substituting the mapping entry by entry
    let the output of one rule become the input of another: "4.5" -> "5.3" was
    applied, and then the rule "5.3" -> "5.10" rewrote what the first rule had
    just produced, so a reference to the completeness gate came out pointing at
    the contaminated-predictor section instead. Matching every reference once and
    translating each captured number exactly once makes that impossible.

    Ranges are handled explicitly. "§5.3-5.5" previously mapped only the half
    carrying the section mark and emerged as "§5.10-5.5".
    """
    def translate(m: re.Match) -> str:
        out = m.group("lead") + mapping.get(m.group("a"), m.group("a"))
        if m.group("dash"):
            sep = m.group("dash")[:m.group("dash").index(m.group("b"))]
            out += sep + mapping.get(m.group("b"), m.group("b"))
        return out

    text = REFERENCE.sub(translate, path.read_text(encoding="utf-8"))
    path.write_text(text, encoding="utf-8")


def main() -> int:
    for name in ("ch1-introduction.md", "ch2-literature-review.md",
                 "ch3-methodology.md", "ch4-design-and-implementation.md",
                 "ch5-empirical-validation.md",
                 "ch6-results-discussion-conclusion.md"):
        if not (CH / name).exists():
            print(f"Missing source chapter: {name}")
            return 1

    ch1 = blocks(CH / "ch1-introduction.md")
    ch2 = blocks(CH / "ch2-literature-review.md")
    ch3 = blocks(CH / "ch3-methodology.md")
    ch4 = blocks(CH / "ch4-design-and-implementation.md")
    ch5 = blocks(CH / "ch5-empirical-validation.md")
    ch6 = blocks(CH / "ch6-results-discussion-conclusion.md")

    print("Restructuring into NSBM section order:")

    # ---- 1 INTRODUCTION ----------------------------------------------------
    # Objectives move out to their own mandated section.
    # 1.4 was Objectives, which the guideline requires as its own top-level
    # section. Everything after it shifts up one to avoid a gap.
    intro = select(ch1, ("1.1", "1.2", "1.3", "1.5", "1.6", "1.7", "1.8"))
    intro = renumber(intro, "1", "1",
                     remap={"1.5": "1.4", "1.6": "1.5", "1.7": "1.6",
                            "1.8": "1.7"})
    write(CH / "01-introduction.md", "1 INTRODUCTION", intro)

    # ---- 3 LITERATURE REVIEW ----------------------------------------------
    lit = select(ch2, tuple(f"2.{i}" for i in range(1, 9)))
    lit = renumber(lit, "2", "3")
    write(CH / "03-literature-review.md", "3 LITERATURE REVIEW", lit)

    # ---- 4 METHODOLOGY -----------------------------------------------------
    # Chapter 3 in full, plus the parts of chapter 4 that describe HOW the
    # artefact was produced rather than what it turned out to be.
    method = renumber(select(ch3, tuple(f"3.{i}" for i in range(1, 9))),
                      "3", "4")
    design_method = select(ch4, ("4.1", "4.2", "4.4", "4.6"),
                           exclude=("4.2.3",))
    design_method = renumber(design_method, "4", "4",
                             remap={"4.1": "4.9", "4.2": "4.10",
                                    "4.2.1": "4.10.1", "4.2.2": "4.10.2",
                                    "4.4": "4.11", "4.4.1": "4.11.1",
                                    "4.4.2": "4.11.2", "4.4.3": "4.11.3",
                                    "4.4.4": "4.11.4",
                                    "4.6": "4.12", "4.6.1": "4.12.1",
                                    "4.6a": "4.13", "4.6a.1": "4.13.1"})
    write(CH / "04-methodology.md", "4 METHODOLOGY", method + design_method)

    # ---- 5 RESULTS ---------------------------------------------------------
    # What the artefact turned out to be, then the empirical findings.
    artefact = select(ch4, ("4.2.3", "4.3", "4.5", "4.7", "4.8", "4.9", "4.10"))
    artefact = renumber(artefact, "4", "5",
                        remap={"4.2.3": "5.1", "4.3": "5.2", "4.3.1": "5.2.1",
                               "4.3.2": "5.2.2", "4.5": "5.3", "4.5.1": "5.3.1",
                               "4.5.2": "5.3.2", "4.7": "5.4", "4.8": "5.5",
                               "4.9": "5.6", "4.10": "5.7"})
    empirical = select(ch5, tuple(f"5.{i}" for i in range(1, 9)))
    empirical = renumber(
        empirical, "5", "5",
        remap={"5.1": "5.8", "5.2": "5.9", "5.2.1": "5.9.1", "5.2.2": "5.9.2",
               "5.3": "5.10", "5.3.1": "5.10.1", "5.3.2": "5.10.2",
               "5.3.3": "5.10.3", "5.3.4": "5.10.4",
               "5.4": "5.11", "5.5": "5.12", "5.5a": "5.13", "5.5b": "5.14",
               "5.6": "5.15", "5.6a": "5.16", "5.6a.1": "5.16.1",
               "5.6a.2": "5.16.2", "5.6a.3": "5.16.3",
               "5.6b": "5.17", "5.6b.1": "5.17.1", "5.6b.2": "5.17.2",
               "5.6b.3": "5.17.3",
               "5.6c": "5.18", "5.6c.1": "5.18.1", "5.6c.2": "5.18.2",
               "5.6c.3": "5.18.3",
               "5.6d": "5.19", "5.6d.1": "5.19.1", "5.6d.2": "5.19.2",
               "5.6d.3": "5.19.3", "5.6d.4": "5.19.4",
               "5.7": "5.20", "5.8": "5.21"})
    write(CH / "05-results.md", "5 RESULTS", artefact + empirical)

    # ---- 6 DISCUSSION AND CONCLUSIONS -------------------------------------
    disc = select(ch6, tuple(f"6.{i}" for i in range(1, 8)))
    disc = renumber(disc, "6", "6")
    write(CH / "06-discussion-conclusions.md",
          "6 DISCUSSION AND CONCLUSIONS", disc)

    # ---- cross-references --------------------------------------------------
    mapping = {
        "1.4": "2", "1.5": "1.4", "1.6": "1.5", "1.7": "1.6",
        "1.8": "1.7", "2.3.3": "3.5.3", "2.4.1": "3.6.1", "2.4.2": "3.6.2",
        "2.5.3": "3.5.3", "2.6.1": "3.6.1", "2.6.2": "3.6.2", "2.7": "3.8",
        "2.8": "3.8", "2.2.1": "3.4",
        "3.5": "4.5", "3.5.1": "4.5.1", "3.6.3": "4.6.3",
        "4.2.2": "4.10.2", "4.3.2": "5.2.2", "4.4.2": "4.11.2",
        "4.4.3": "4.11.3", "4.5": "5.3", "4.6": "4.12", "4.6a": "4.13",
        "4.6a.1": "4.13.1", "4.7": "5.4", "4.9": "5.6", "4.10": "5.7",
        "5.3": "5.10", "5.3.4": "5.10.4", "5.4": "5.11", "5.5": "5.12",
        "5.5a": "5.13", "5.5b": "5.14", "5.6": "5.15", "5.6a": "5.16",
        "5.6b": "5.17", "5.6b.1": "5.17.1", "5.6b.2": "5.17.2",
        "5.6b.3": "5.17.3",
        "5.6c": "5.18", "5.6d": "5.19",
        "5.7": "5.20", "5.8": "5.21", "6.1": "6.1", "6.4": "6.3",
    }
    for name in ("01-introduction.md", "03-literature-review.md",
                 "04-methodology.md", "05-results.md",
                 "06-discussion-conclusions.md", "02-objectives.md"):
        fix_cross_references(CH / name, mapping)

    print("\nCross-references updated.")
    print("Source chapters left untouched - they remain the editable originals.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
