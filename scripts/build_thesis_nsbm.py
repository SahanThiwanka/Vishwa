"""Assemble the thesis to the NSBM Senate-approved formatting guidelines.

Run:  python scripts/build_thesis_nsbm.py

Implements the requirements in "Thesis Preparation and Formatting Guidelines for
Undergraduate and Postgraduate Degree Programmes":

  structure    Title page, Declaration, Acknowledgement, Abstract, Table of
               Contents, List of Figures, List of Tables, List of Abbreviations,
               Introduction, Objectives, Literature Review, Methodology, Results,
               Discussion and Conclusions, References, Appendices
  page         A4; margins 1" top/right/bottom, 1.25" left for binding
  type         Times New Roman 12 pt, 1.5 line spacing, single column
  pagination   lower-case Roman from the inner title page (number suppressed on
               it) through the Abbreviations; Arabic restarting at 1 from the
               Introduction; bottom centre; no other headers or footers
  headings     1 INTRODUCTION (bold capitals) / 1.1 Heading (bold) /
               1.1.1 Heading (plain, first letter capitalised only)
  captions     tables captioned ABOVE, figures captioned BELOW, numbered by
               section as Table 2.1, Figure 1.2; no cell shading
  references   IEEE numbered style, applied by to_ieee.py

Pipeline:  restructure_thesis.py  ->  to_ieee.py  ->  this script

The Table of Contents and the Lists of Figures and Tables are inserted as Word
field codes. They appear empty until the document is opened in Word and the
fields are updated (Ctrl+A, F9) - that is expected, and is the only way to get
correct page numbers without laying out the document ourselves.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "docs" / "06-thesis"
OUTPUT = CHAPTERS / "THESIS-NSBM.docx"

TITLE = ("A DUAL-OBJECTIVE DECISION SUPPORT MODEL FOR SME CREDIT APPRAISAL "
         "IN SRI LANKAN DEVELOPMENT BANKING")
AUTHOR = "A. A. V. ATHUKORALA"
DEGREE = "Master of Science in Information Technology"
DEPARTMENT = "Department of Computing and Information Systems"
FACULTY = "Faculty of Computing"
SUBMISSION = "September 2026"

BODY_SECTIONS = [
    "01-introduction.md",
    "02-objectives.md",
    "03-literature-review.md",
    "04-methodology.md",
    "05-results.md",
    "06-discussion-conclusions.md",
    "07-references.md",
    "08-appendices.md",
]

PAGEBREAK = "<<<PAGEBREAK>>>"


# ---------------------------------------------------------------------------
# Low-level Word plumbing
# ---------------------------------------------------------------------------

def add_field(paragraph, instruction: str) -> None:
    """Insert a Word field code (PAGE, TOC, SEQ ...) into a paragraph."""
    run = paragraph.add_run()

    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    run._r.append(begin)

    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = instruction
    run._r.append(instr)

    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    run._r.append(separate)

    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.append(end)


def set_page_numbering(section, fmt: str, start: int | None = None) -> None:
    """Set the numbering format (lowerRoman / decimal) for a section.

    A new section inherits a copy of the previous section's properties, so any
    pgNumType already present must be REMOVED before adding ours. Appending a
    second one leaves the inherited element first, and Word honours that one -
    which silently gave the body Roman numerals instead of Arabic.
    """
    sect_pr = section._sectPr
    for existing in sect_pr.findall(qn("w:pgNumType")):
        sect_pr.remove(existing)

    pg = OxmlElement("w:pgNumType")
    pg.set(qn("w:fmt"), fmt)
    if start is not None:
        pg.set(qn("w:start"), str(start))
    sect_pr.append(pg)


def footer_page_number(section, show: bool = True) -> None:
    """Bottom-centre page number, or an empty footer when show is False."""
    section.footer.is_linked_to_previous = False
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in list(p.runs):
        run._r.getparent().remove(run._r)
    if show:
        add_field(p, "PAGE")
        for run in p.runs:
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)


def configure(section, left: float = 1.25) -> None:
    """A4 with the required margins."""
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.right_margin = Inches(1)
    section.left_margin = Inches(left)


def centred(doc, text: str, size: int, bold: bool = False,
            space_after: int = 6):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run(text)
    run.bold = bold
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    return p


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

INLINE_BOLD = re.compile(r"\*\*(.+?)\*\*")
INLINE_CODE = re.compile(r"`(.+?)`")
LINK = re.compile(r"\[(.+?)\]\((.+?)\)")


def clean(text: str) -> str:
    text = INLINE_BOLD.sub(r"\1", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"\1", text)
    text = INLINE_CODE.sub(r"\1", text)
    text = LINK.sub(r"\1", text)
    return text.strip()


def rich_paragraph(doc, text: str, style: str | None = None, indent: float = 0):
    # A markdown-escaped asterisk (as in the symbol xi-star) must reach the page
    # as a plain asterisk, not as backslash-asterisk.
    text = text.replace("\\*", "*")
    p = doc.add_paragraph(style=style)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(6)
    if indent:
        p.paragraph_format.left_indent = Inches(indent)

    # Single-asterisk italics matter here: IEEE reference entries italicise the
    # journal or book title, and without this they render as literal asterisks.
    for part in re.split(r"(\*\*.+?\*\*|\*[^*]+?\*|`.+?`)", text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            run = p.add_run(LINK.sub(r"\1", part[2:-2]))
            run.bold = True
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            run = p.add_run(LINK.sub(r"\1", part[1:-1]))
            run.italic = True
        elif part.startswith("`") and part.endswith("`"):
            run = p.add_run(part[1:-1])
        else:
            run = p.add_run(LINK.sub(r"", part))
        run.font.name = "Times New Roman"
        run.font.size = Pt(12)
    return p


def heading(doc, text: str, level: int):
    """Headings per the guideline, applied directly rather than via styles.

    Word's built-in Heading styles carry their own fonts and colours; the
    guideline specifies Times New Roman 12 throughout, so the formatting is set
    on the run and the built-in style is used only so the field-code Table of
    Contents can find the entry.
    """
    p = doc.add_paragraph(style=f"Heading {min(level, 4)}")
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)

    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    run.font.color.rgb = None
    # Level 1 and 2 are bold; deeper levels are plain per the guideline.
    run.bold = level <= 2
    return p


def caption(doc, text: str, above: bool = True):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_before = Pt(6 if above else 2)
    p.paragraph_format.space_after = Pt(2 if above else 6)
    # The Caption style is what the List of Tables / Figures field codes collect.
    try:
        p.style = doc.styles["Caption"]
    except KeyError:
        pass
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    run.bold = False
    run.italic = False
    run.font.color.rgb = None
    return p


def parse_table(lines: list[str], start: int) -> tuple[list[list[str]], int]:
    rows, i = [], start
    while i < len(lines) and lines[i].strip().startswith("|"):
        cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
        if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            rows.append(cells)
        i += 1
    return rows, i


def add_table(doc, rows: list[list[str]]) -> None:
    if not rows:
        return
    width = max(len(r) for r in rows)
    table = doc.add_table(rows=0, cols=width)
    # A plain grid: the guideline forbids shading in table cells.
    table.style = "Table Grid"

    for r_i, row in enumerate(rows):
        cells = table.add_row().cells
        for c_i in range(width):
            cells[c_i].text = ""
            para = cells[c_i].paragraphs[0]
            para.paragraph_format.line_spacing = 1.0
            para.paragraph_format.space_after = Pt(2)
            run = para.add_run(clean(row[c_i]) if c_i < len(row) else "")
            run.font.name = "Times New Roman"
            run.font.size = Pt(11)
            run.bold = r_i == 0


def render(doc, path: Path, counters: dict) -> None:
    lines = path.read_text(encoding="utf-8").split("\n")
    i = 0
    pending_caption: str | None = None

    while i < len(lines):
        raw = lines[i]
        line = raw.strip()

        if line == PAGEBREAK:
            doc.add_page_break()
            i += 1
            continue

        if not line:
            i += 1
            continue

        # Explicit caption markers, e.g.  [Table: Benchmark results]
        m = re.match(r"^\[(Table|Figure):\s*(.+?)\]$", line)
        if m:
            pending_caption = f"{m.group(1)}|{m.group(2)}"
            i += 1
            continue

        if line.startswith("|"):
            rows, i = parse_table(lines, i)
            # Front matter (section "0") carries the abbreviations list, which
            # is not a numbered thesis table and takes no caption.
            if counters["section"] != "0":
                counters["table"] += 1
                label = f"Table {counters['section']}.{counters['table']}"
                if pending_caption and pending_caption.startswith("Table|"):
                    label += f": {pending_caption.split('|', 1)[1]}"
                    pending_caption = None
                caption(doc, label, above=True)
            add_table(doc, rows)
            doc.add_paragraph()
            continue

        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            text = clean(line.lstrip("#").strip())
            if level == 1:
                counters["table"] = 0
                counters["figure"] = 0
                m2 = re.match(r"^(\d+)\s", text)
                counters["section"] = m2.group(1) if m2 else counters["section"]
            heading(doc, text, level)
            i += 1
            continue

        if re.fullmatch(r"-{3,}", line):
            i += 1
            continue

        if line.startswith(">"):
            # Buffer the whole quote before rendering. Rendering one source line
            # at a time broke inline markup spanning a line break, so a bold run
            # written as **not\nadministered** reached the document with its
            # asterisks intact.
            quote: list[str] = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip().lstrip(">").strip())
                i += 1
            joined = " ".join(q for q in quote if q)
            if joined:
                rich_paragraph(doc, joined, indent=0.4)
            continue

        m3 = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)", raw)
        if m3:
            spaces, marker, text = m3.groups()
            style = "List Number" if marker[0].isdigit() else "List Bullet"
            rich_paragraph(doc, text, style=style,
                           indent=0.6 if len(spaces) >= 2 else 0)
            i += 1
            continue

        buffer = [line]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if (not nxt or nxt.startswith(("#", "|", ">", "-", "*", "["))
                    or nxt == PAGEBREAK or re.match(r"^\d+\.\s", nxt)):
                break
            buffer.append(nxt)
            i += 1

        rich_paragraph(doc, " ".join(buffer))


# ---------------------------------------------------------------------------

def main() -> int:
    missing = [n for n in BODY_SECTIONS if not (CHAPTERS / n).exists()]
    if missing:
        print("Missing sections: " + ", ".join(missing))
        print("Run the restructure first.")
        return 1

    doc = Document()

    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(12)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.space_after = Pt(6)

    # ---- Section 1: cover page, unnumbered ---------------------------------
    configure(doc.sections[0])
    footer_page_number(doc.sections[0], show=False)

    for _ in range(3):
        doc.add_paragraph()
    centred(doc, TITLE, 16, bold=True, space_after=12)
    for _ in range(6):
        doc.add_paragraph()
    centred(doc, AUTHOR, 14)
    doc.add_paragraph()
    centred(doc, DEGREE, 14)
    for _ in range(6):
        doc.add_paragraph()
    centred(doc, DEPARTMENT, 14)
    centred(doc, "NSBM Green University", 14)
    centred(doc, "Sri Lanka", 14)
    doc.add_paragraph()
    centred(doc, SUBMISSION, 14)

    # ---- Section 2: front matter, lower-case Roman -------------------------
    front = doc.add_section(WD_SECTION.NEW_PAGE)
    configure(front)
    set_page_numbering(front, "lowerRoman", start=1)
    footer_page_number(front, show=True)
    # The inner title page counts as i but shows no number.
    front.different_first_page_header_footer = True
    front.first_page_footer.is_linked_to_previous = False
    for p in front.first_page_footer.paragraphs:
        for run in list(p.runs):
            run._r.getparent().remove(run._r)

    for _ in range(3):
        doc.add_paragraph()
    centred(doc, TITLE, 16, bold=True, space_after=12)
    for _ in range(4):
        doc.add_paragraph()
    centred(doc, "A thesis submitted to NSBM Green University for the degree of", 14)
    centred(doc, DEGREE, 14)
    for _ in range(3):
        doc.add_paragraph()
    centred(doc, "By", 14)
    doc.add_paragraph()
    centred(doc, AUTHOR, 14)
    for _ in range(5):
        doc.add_paragraph()
    centred(doc, DEPARTMENT, 14)
    centred(doc, FACULTY, 14)
    centred(doc, "NSBM Green University", 14)
    centred(doc, "Sri Lanka", 14)
    doc.add_paragraph()
    centred(doc, SUBMISSION, 14)
    doc.add_page_break()

    counters = {"section": "0", "table": 0, "figure": 0}
    render(doc, CHAPTERS / "00-front-matter.md", counters)

    # Table of contents and lists, as field codes Word populates on update.
    for title, instruction in [
        ("TABLE OF CONTENTS", r'TOC \o "1-3" \h \z \u'),
        ("LIST OF FIGURES", r'TOC \h \z \c "Figure"'),
        ("LIST OF TABLES", r'TOC \h \z \c "Table"'),
    ]:
        doc.add_page_break()
        heading(doc, title, 1)
        p = doc.add_paragraph()
        add_field(p, instruction)
        note = doc.add_paragraph()
        run = note.add_run(
            "(Open in Word and press Ctrl+A then F9 to populate this list.)"
        )
        run.italic = True
        run.font.name = "Times New Roman"
        run.font.size = Pt(10)

    # ---- Section 3: body, Arabic restarting at 1 ---------------------------
    body = doc.add_section(WD_SECTION.NEW_PAGE)
    configure(body)
    set_page_numbering(body, "decimal", start=1)
    footer_page_number(body, show=True)
    body.different_first_page_header_footer = False

    for name in BODY_SECTIONS:
        path = CHAPTERS / name
        counters["table"] = 0
        counters["figure"] = 0
        print(f"  {name}")
        render(doc, path, counters)
        doc.add_page_break()

    doc.save(OUTPUT)

    words = sum(len((CHAPTERS / n).read_text(encoding="utf-8").split())
                for n in BODY_SECTIONS)
    words += len((CHAPTERS / "00-front-matter.md").read_text(encoding="utf-8").split())

    print(f"\nWrote {OUTPUT.relative_to(ROOT)}")
    print(f"  ~{words:,} words, {len(doc.tables)} tables")
    print("\nOpen in Word and press Ctrl+A then F9 to populate the contents lists.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
