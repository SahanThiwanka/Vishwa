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
           ->  export_pdf.py  (updates the contents fields and writes the PDF)

The Table of Contents and the Lists of Figures and Tables are inserted as Word
field codes, which stay empty until a field update runs. export_pdf.py drives
Word to do that, so the delivered .docx and .pdf both carry real page numbers.

Typesetting decisions this file makes, beyond the guideline:

  * Tables are laid out at FIXED width, with columns sized from their content
    and the total pinned to the 6.02" text column. Word's automatic layout sizes
    to content with no upper bound, which pushed the wider tables past the right
    margin and off the page.
  * Body paragraphs are justified, with automatic hyphenation. Ragged-right at
    12 pt over a 6" measure leaves visibly uneven lines.
  * Headings, table captions and figures are marked keep-with-next, so a heading
    cannot be stranded at the foot of a page and a caption cannot be separated
    from what it captions.
  * Fenced code blocks render as monospaced, single-spaced paragraphs. Before
    this they were flattened into the surrounding prose, backticks and all.
"""

from __future__ import annotations

import os
import re
import sys
from datetime import date
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "docs" / "06-thesis"

# Each build day writes its own file. Overwriting one name in place meant the
# only copy of the document was whatever the last run produced, and there was
# no way to put a chapter beside the version of it that went to the supervisor
# a week earlier. The dated file is the deliverable; the earlier ones stay.
OUTPUT = CHAPTERS / f"THESIS-NSBM-{date.today():%Y-%m-%d}.docx"

# Word holds an exclusive lock on an open document, so a rebuild while the
# thesis is open fails with PermissionError - and does so after the previous
# build has already been superseded in the author's mind, which is the worst
# moment to lose a file. THESIS_OUT redirects the build somewhere else when the
# usual target cannot be written, so a rebuild on submission day is never
# blocked by having the document open to read it.
if os.environ.get("THESIS_OUT"):
    # Resolved, because the closing status line reports the path relative to the
    # repository root and a bare relative path is not under it.
    OUTPUT = Path(os.environ["THESIS_OUT"]).resolve()

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
SPACER = "&SPACE;"

BODY_FONT = "Times New Roman"
MONO_FONT = "Consolas"
BODY_PT = 12

# A4 (8.27") less the 1.25" binding margin and the 1" right margin.
TEXT_WIDTH_IN = 8.27 - 1.25 - 1.0


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
            run.font.name = BODY_FONT
            run.font.size = Pt(BODY_PT)


def configure(section, left: float = 1.25) -> None:
    """A4 with the required margins."""
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.right_margin = Inches(1)
    section.left_margin = Inches(left)


def enable_hyphenation(doc) -> None:
    """Turn on automatic hyphenation.

    Justified 12 pt text over a 6" measure without hyphenation opens rivers of
    white space between words, which is the usual reason a justified thesis
    looks worse than a ragged-right one. Capitals are left unhyphenated so the
    bold capitalised chapter headings are not broken.
    """
    settings = doc.settings.element
    for name, value in (("w:autoHyphenation", "true"),
                        ("w:hyphenationZone", "288"),
                        # Never more than two hyphenated lines in a row: a
                        # ladder of hyphens down the right edge is as
                        # distracting as the white space it prevents.
                        ("w:consecutiveHyphenLimit", "2"),
                        ("w:doNotHyphenateCaps", "true")):
        el = OxmlElement(name)
        el.set(qn("w:val"), value)
        settings.append(el)


def style_run(run, size: int = BODY_PT, font: str = BODY_FONT):
    run.font.name = font
    run.font.size = Pt(size)
    # ascii/hAnsi alone leave complex-script and East Asian runs on the theme
    # font, which shows up as a different typeface on the Greek letters.
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(attr), font)
    return run


def centred(doc, text: str, size: int, bold: bool = False,
            space_after: int = 6):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run(text)
    run.bold = bold
    style_run(run, size)
    return p


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

INLINE_BOLD = re.compile(r"\*\*(.+?)\*\*")
INLINE_CODE = re.compile(r"`(.+?)`")
LINK = re.compile(r"\[(.+?)\]\((.+?)\)")

# Only these bracketed forms open a block. Breaking a paragraph at any line
# beginning with "[" split it at IEEE citation numbers, leaving fragments like
# "[8], who benchmarked forty-one classifiers ..." standing as paragraphs.
BLOCK_MARKER = re.compile(r"^\[(Image|Table|Figure):")

# An in-text reference to an exhibit: @tbl:leakage-taxonomy, @fig:term-leakage.
#
# The guideline requires every table and figure to appear as close as possible
# to its FIRST MENTION IN THE TEXT, which presupposes a mention. The numbers
# cannot be written into the chapters by hand: the restructure renumbers whole
# sections, so a table that is 5.9 today is 5.11 after one section is inserted
# above it. The key is stable, the number is resolved at build time, and an
# unresolved key fails the build instead of printing "Table ??" into a
# submitted document.
EXHIBIT_REF = re.compile(r"@(tbl|fig):([a-z0-9][a-z0-9-]*)")
UNRESOLVED = "Table ??"


def substitute_refs(text: str, labels: dict, missing: list) -> str:
    def one(m: re.Match) -> str:
        key = f"{m.group(1)}:{m.group(2)}"
        if key in labels:
            return labels[key]
        missing.append(key)
        return UNRESOLVED
    return EXHIBIT_REF.sub(one, text)


def clean(text: str) -> str:
    text = INLINE_BOLD.sub(r"\1", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"\1", text)
    text = INLINE_CODE.sub(r"\1", text)
    text = LINK.sub(r"\1", text)
    return text.replace("\\*", "*").strip()


def add_inline_runs(p, text: str, size: int = BODY_PT) -> None:
    """Split markdown inline markup into Word runs.

    Single-asterisk italics matter here: IEEE reference entries italicise the
    journal or book title, and a figure caption naming a dataset field writes it
    as *Term*. Captions used to be added as one plain run, so that caption
    reached the page as "\\*Term\\*", asterisks and all.
    """
    # A markdown-escaped asterisk (as in the symbol xi-star) must reach the page
    # as a plain asterisk, not as backslash-asterisk.
    text = text.replace("\\*", "*")
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
            style_run(p.add_run(part[1:-1]), size - 1, MONO_FONT)
            continue
        else:
            run = p.add_run(LINK.sub(r"\1", part))
        style_run(run, size)


def rich_paragraph(doc, text: str, style: str | None = None, indent: float = 0,
                   justify: bool = True, size: int = BODY_PT):
    p = doc.add_paragraph(style=style)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.widow_control = True
    if justify:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if indent:
        p.paragraph_format.left_indent = Inches(indent)
    add_inline_runs(p, text, size)
    return p


LIST_ITEM = re.compile(r"^\s*([-*]\s|\d+\.\s)")


def more_list_items(lines: list[str], i: int) -> bool:
    """Is another item of the same list still to come, from position i?"""
    while i < len(lines) and not lines[i].strip():
        i += 1
    return i < len(lines) and bool(LIST_ITEM.match(lines[i]))


def list_run_length(lines: list[str], i: int) -> int:
    """How many items remain in this list, counting from position i."""
    count = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if LIST_ITEM.match(line):
            count += 1
            i += 1
            while (i < len(lines) and lines[i].strip()
                   and not LIST_ITEM.match(lines[i])
                   and not lines[i].strip().startswith(("#", "|", ">", "```"))):
                i += 1
            continue
        break
    return count


def set_tab_stop(paragraph, inches: float) -> None:
    """A left tab stop, so a hanging number and its text align."""
    p_pr = paragraph._p.get_or_add_pPr()
    tabs = p_pr.find(qn("w:tabs"))
    if tabs is None:
        tabs = OxmlElement("w:tabs")
        p_pr.append(tabs)
    tab = OxmlElement("w:tab")
    tab.set(qn("w:val"), "left")
    tab.set(qn("w:pos"), str(int(inches * 1440)))
    tabs.append(tab)


def reference_paragraph(doc, text: str):
    """An IEEE reference entry, with its number hanging in the left margin."""
    p = rich_paragraph(doc, text, justify=False)
    p.paragraph_format.left_indent = Inches(0.4)
    p.paragraph_format.first_line_indent = Inches(-0.4)
    p.paragraph_format.space_after = Pt(8)
    return p


def heading(doc, text: str, level: int, page_break_before: bool = False):
    """Headings per the guideline, applied directly rather than via styles.

    Word's built-in Heading styles carry their own fonts AND COLOURS - the
    default theme renders them in blue, which is how a thesis ends up with a
    blue heading on almost every page. The guideline specifies Times New Roman
    12 in black throughout, so both are set explicitly on the run: assigning
    None to the colour does not override the style, it only stops overriding
    it. The built-in style is kept so the field-code Table of Contents finds
    the entry.
    """
    p = doc.add_paragraph(style=f"Heading {min(level, 4)}")
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_before = Pt(14 if level == 1 else 12)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.keep_together = True
    # Opening each chapter with a break-before, rather than closing the previous
    # one with an explicit page break, avoids the stray blank page that appears
    # whenever a chapter happens to end near the foot of a page.
    p.paragraph_format.page_break_before = page_break_before

    run = p.add_run(text)
    style_run(run)
    run.font.color.rgb = RGBColor(0, 0, 0)
    # Level 1 and 2 are bold; deeper levels are plain per the guideline.
    run.bold = level <= 2
    return p


TABLE_CAPTION_STYLE = "Table Caption"
FIGURE_CAPTION_STYLE = "Figure Caption"


def blacken_contents_styles(doc) -> None:
    """Black, unlinked contents entries.

    A TOC field built with \\h makes every entry a hyperlink, and Word paints
    hyperlinks in theme blue. The Table of Contents, the List of Figures and the
    List of Tables therefore came out blue on a thesis that is black
    everywhere else, and would print that way. The links themselves are worth
    keeping for the PDF, so the colour is changed and the underline removed
    instead of dropping \\h.
    """
    for name in ("Hyperlink", "FollowedHyperlink",
                 "TOC 1", "TOC 2", "TOC 3", "TOC 4"):
        try:
            style = doc.styles[name]
        except KeyError:
            if not name.startswith("TOC"):
                style = doc.styles.add_style(name, WD_STYLE_TYPE.CHARACTER)
            else:
                continue
        style.font.color.rgb = RGBColor(0, 0, 0)
        style.font.underline = False
        style.font.name = BODY_FONT


def ensure_caption_styles(doc) -> None:
    """Separate paragraph styles for table and figure captions.

    THE LISTS OF FIGURES AND TABLES CAME OUT EMPTY BEFORE THIS. They were built
    with the TOC \\c switch, which collects SEQ fields, and these captions carry
    no SEQ field: their numbers are section-relative (Table 5.13) and are
    written by this script, not counted by Word. Word therefore reported "No
    table of figures entries found" on both pages.

    Collecting by paragraph STYLE instead works with numbers we write
    ourselves, and needs one style per list so the two do not merge.
    """
    base = doc.styles["Caption"]
    for name in (TABLE_CAPTION_STYLE, FIGURE_CAPTION_STYLE):
        try:
            style = doc.styles[name]
        except KeyError:
            style = doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
            style.base_style = base
        style.font.name = BODY_FONT
        style.font.size = Pt(11)
        style.font.italic = False
        style.font.bold = False
        style.font.color.rgb = RGBColor(0, 0, 0)
        style.quick_style = False


def caption(doc, text: str, above: bool = True):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(8 if above else 4)
    p.paragraph_format.space_after = Pt(4 if above else 10)
    # A caption above its table must not be orphaned at the foot of a page.
    p.paragraph_format.keep_with_next = above
    p.paragraph_format.keep_together = True
    # Tables are captioned above, figures below, so `above` identifies which
    # list this caption belongs in.
    try:
        p.style = doc.styles[TABLE_CAPTION_STYLE if above
                             else FIGURE_CAPTION_STYLE]
    except KeyError:
        pass
    add_inline_runs(p, text, 11)
    for run in p.runs:
        run.font.color.rgb = RGBColor(0, 0, 0)
    return p


def code_block(doc, lines: list[str]) -> None:
    """A fenced code block: monospaced, single-spaced, indented, not justified."""
    for idx, raw in enumerate(lines):
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_before = Pt(8 if idx == 0 else 0)
        p.paragraph_format.space_after = Pt(8 if idx == len(lines) - 1 else 0)
        p.paragraph_format.left_indent = Inches(0.3)
        p.paragraph_format.keep_together = True
        p.paragraph_format.keep_with_next = idx < len(lines) - 1
        style_run(p.add_run(raw), 10, MONO_FONT)


# ---------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------

def parse_table(lines: list[str], start: int):
    """Read a pipe table. Returns (rows, alignments, next index).

    The delimiter row is not content, but it does carry the column alignment,
    which is how the numeric columns come out right-aligned instead of ragged.
    """
    rows: list[list[str]] = []
    aligns: list[str] = []
    i = start
    while i < len(lines) and lines[i].strip().startswith("|"):
        cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
        if cells and all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            aligns = ["center" if c.startswith(":") and c.endswith(":")
                      else "right" if c.endswith(":")
                      else "left" for c in cells]
        else:
            rows.append(cells)
        i += 1
    return rows, aligns, i


def set_repeat_header(row) -> None:
    """Repeat this row at the top of every page the table continues onto."""
    tr_pr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true")
    tr_pr.append(el)


def set_cannot_split(row) -> None:
    """Never break a single row across a page."""
    tr_pr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:cantSplit")
    el.set(qn("w:val"), "true")
    tr_pr.append(el)


# Above this many rows a table is allowed to break across a page, because
# holding a long one together would push a large gap ahead of it. Below it the
# table stays whole: the chapter-structure table was breaking after its header,
# leaving one row and a repeated header alone at the top of a page.
KEEP_WHOLE_ROWS = 9


def set_fixed_layout(table) -> None:
    tbl_pr = table._tbl.tblPr
    for existing in tbl_pr.findall(qn("w:tblLayout")):
        tbl_pr.remove(existing)
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tbl_pr.append(layout)


def column_widths(rows: list[list[str]], ncol: int) -> list[float]:
    """Inches per column, summing to the text width.

    Word's automatic layout has no upper bound, so a table holding one
    129-character cell simply grew until it ran off the right-hand edge of the
    page. Sizing happens here instead: each column asks for the width of its
    longest cell, capped so long prose wraps rather than dictating the layout,
    and never narrower than its longest single word so words are not broken.
    """
    longest = [1] * ncol
    longest_word = [1] * ncol
    for row in rows:
        for j in range(min(len(row), ncol)):
            cell = clean(row[j])
            longest[j] = max(longest[j], len(cell))
            for word in cell.split():
                longest_word[j] = max(longest_word[j], len(word))

    # 45 characters is roughly a third of the text column at 10 pt; past that a
    # cell is prose and should wrap.
    demand = [max(min(longest[j], 45), min(longest_word[j], 22))
              for j in range(ncol)]
    total = sum(demand) or 1

    min_in = min(0.6, TEXT_WIDTH_IN / ncol)
    widths = [max(min_in, TEXT_WIDTH_IN * d / total) for d in demand]

    # Re-normalise: the minimum-width floor can push the total over the measure.
    scale = TEXT_WIDTH_IN / sum(widths)
    return [w * scale for w in widths]


def table_font_size(rows: list[list[str]], ncol: int) -> int:
    """Shrink the type for tables carrying a lot of text, rather than overflow."""
    bulk = max(sum(len(clean(c)) for c in row) for row in rows)
    if bulk > 130 or ncol >= 6:
        return 9
    if bulk > 85 or ncol == 5:
        return 10
    return 11


def add_table(doc, rows: list[list[str]], aligns: list[str]) -> None:
    if not rows:
        return
    # A table written with an empty header row - "| | |" - is a two-column
    # layout of labels and values, not a headed table. Rendering the blank row
    # put an empty bold band across the top of it.
    if all(not c.strip() for c in rows[0]):
        rows = rows[1:]
        has_header = False
    else:
        has_header = True
    if not rows:
        return

    ncol = max(len(r) for r in rows)
    widths = column_widths(rows, ncol)
    size = table_font_size(rows, ncol)

    table = doc.add_table(rows=0, cols=ncol)
    # A plain grid: the guideline forbids shading in table cells.
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_fixed_layout(table)

    align_map = {"right": WD_ALIGN_PARAGRAPH.RIGHT,
                 "center": WD_ALIGN_PARAGRAPH.CENTER,
                 "left": WD_ALIGN_PARAGRAPH.LEFT}

    for r_i, row in enumerate(rows):
        cells = table.add_row().cells
        for c_i in range(ncol):
            cell = cells[c_i]
            cell.width = Inches(widths[c_i])
            cell.text = ""
            para = cell.paragraphs[0]
            para.paragraph_format.line_spacing = 1.0
            para.paragraph_format.space_before = Pt(2)
            para.paragraph_format.space_after = Pt(2)
            if c_i < len(aligns):
                para.alignment = align_map.get(aligns[c_i],
                                               WD_ALIGN_PARAGRAPH.LEFT)
            text = clean(row[c_i]) if c_i < len(row) else ""
            run = para.add_run(text)
            style_run(run, size)
            run.bold = has_header and r_i == 0

    # Widths have to be set on every cell AND on the grid, or Word recomputes
    # them from content when the document is opened.
    for c_i, width in enumerate(widths):
        table.columns[c_i].width = Inches(width)
    if has_header and table.rows:
        set_repeat_header(table.rows[0])

    keep_whole = len(table.rows) <= KEEP_WHOLE_ROWS
    for r_i, row in enumerate(table.rows):
        set_cannot_split(row)
        if keep_whole and r_i < len(table.rows) - 1:
            for cell in row.cells:
                for para in cell.paragraphs:
                    para.paragraph_format.keep_with_next = True


# ---------------------------------------------------------------------------

def render(doc, path: Path, counters: dict,
           chapter_breaks: bool = False) -> None:
    text = path.read_text(encoding="utf-8")
    if "@" in text:
        # Whole-file, so a reference inside a table cell or on a continuation
        # line is resolved as well as one in a plain paragraph.
        text = substitute_refs(text, counters["labels"], counters["unresolved"])
    lines = text.split("\n")
    is_references = path.name.startswith("07-")
    i = 0
    pending_caption: tuple[str, str | None, str] | None = None

    while i < len(lines):
        raw = lines[i]
        line = raw.strip()

        if line == PAGEBREAK:
            doc.add_page_break()
            i += 1
            continue

        if line == SPACER:
            doc.add_paragraph()
            i += 1
            continue

        if not line:
            i += 1
            continue

        # Fenced code block. Previously unhandled, which flattened the whole
        # block into one run-on paragraph with the fence marks still in it.
        if line.startswith("```"):
            i += 1
            block: list[str] = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                block.append(lines[i].rstrip())
                i += 1
            i += 1
            if block:
                code_block(doc, block)
            continue

        # Embedded figure:  [Image: file.png | key | Caption text]
        # The key is optional and is what prose refers to as @fig:key.
        m_img = re.match(
            r"^\[Image:\s*([^|\]]+?)\s*\|\s*(?:([a-z0-9-]+)\s*\|\s*)?(.+?)\]$",
            line)
        if m_img:
            src = ROOT / "docs" / "05-results" / "figures" / m_img.group(1).strip()
            if src.exists():
                counters["figure"] += 1
                number = f"{counters['section']}.{counters['figure']}"
                if m_img.group(2):
                    counters["labels"][f"fig:{m_img.group(2)}"] = \
                        f"Figure {number}"
                para = doc.add_paragraph()
                para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                para.paragraph_format.space_before = Pt(10)
                para.paragraph_format.space_after = Pt(2)
                para.paragraph_format.keep_with_next = True
                # Sized to the 6.02in text column, then capped on height so a
                # tall figure cannot push its own caption onto the next page.
                run = para.add_run()
                picture = run.add_picture(str(src), width=Inches(5.9))
                if picture.height > Inches(7.4):
                    picture.width = int(picture.width * Inches(7.4)
                                        / picture.height)
                    picture.height = Inches(7.4)
                # The guideline puts figure captions BELOW the figure.
                caption(doc, f"Figure {number}: {m_img.group(3).strip()}",
                        above=False)
            else:
                if not counters.get("quiet"):
                    print(f"    ! missing figure: {src.name}")
            i += 1
            continue

        # Explicit caption markers:  [Table: key | Benchmark results]
        # The key is optional and is what prose refers to as @tbl:key.
        m = re.match(r"^\[(Table|Figure):\s*(?:([a-z0-9-]+)\s*\|\s*)?(.+?)\]$",
                     line)
        if m:
            pending_caption = (m.group(1), m.group(2), m.group(3))
            i += 1
            continue

        if line.startswith("|"):
            rows, aligns, i = parse_table(lines, i)
            # Front matter (section "0") carries the abbreviations list, which
            # is not a numbered thesis table and takes no caption.
            if counters["section"] != "0":
                counters["table"] += 1
                number = f"{counters['section']}.{counters['table']}"
                label = f"Table {number}"
                if pending_caption and pending_caption[0] == "Table":
                    _, key, text = pending_caption
                    label += f": {text}"
                    if key:
                        counters["labels"][f"tbl:{key}"] = f"Table {number}"
                    pending_caption = None
                caption(doc, label, above=True)
            add_table(doc, rows, aligns)
            spacer = doc.add_paragraph()
            spacer.paragraph_format.space_after = Pt(0)
            continue

        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            text = clean(line.lstrip("#").strip())
            brk = False
            if level == 1:
                counters["table"] = 0
                counters["figure"] = 0
                m2 = re.match(r"^(\d+)\s", text)
                if m2:
                    counters["section"] = m2.group(1)
                elif text.upper().startswith("APPENDIC"):
                    # The appendices carry no chapter number, so the counter
                    # kept the previous chapter's and produced a second
                    # "Table 6.1" - two different tables with one number, both
                    # listed in the List of Tables.
                    counters["section"] = "A"
                # Not on the very first chapter: the body already opens on a
                # fresh page, and a break there would leave one blank.
                brk = chapter_breaks and counters["chapters_seen"] > 0
                counters["chapters_seen"] += 1
            heading(doc, text, level, page_break_before=brk)
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
                p = rich_paragraph(doc, joined, indent=0.4)
                p.paragraph_format.right_indent = Inches(0.4)
                p.paragraph_format.space_before = Pt(6)
            continue

        m3 = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)", raw)
        if m3:
            spaces, marker, text = m3.groups()
            # Word's List Number style numbers EVERY list in the document from
            # one running sequence, so the six numbered lists here came out as
            # 1-7, 8-13, 14-17, 18-20, 21-23 and 24-34. Chapter 5's summary of
            # findings opened at item 24. The number is therefore written as
            # text, taken from the source, with a hanging indent: it is then
            # always the number the author wrote and no list can inherit a
            # count from the one before it.
            ordered = marker[0].isdigit()
            style = None if ordered else "List Bullet"
            # A list item wrapped over several source lines is ONE item. Taking
            # only the first line left every continuation to fall through to the
            # paragraph branch below, so a two-line bullet reached the page as a
            # bullet followed by an unbulleted paragraph set flush to the
            # margin, and the list fell apart wherever an item ran long.
            item = [text]
            i += 1
            while i < len(lines):
                nxt = lines[i]
                stripped = nxt.strip()
                if (not stripped or stripped.startswith(("#", "|", ">", "```"))
                        or BLOCK_MARKER.match(stripped)
                        or stripped in (PAGEBREAK, SPACER)
                        or re.match(r"^\s*([-*]\s|\d+\.\s)", nxt)
                        or re.fullmatch(r"-{3,}", stripped)):
                    break
                item.append(stripped)
                i += 1

            body_text = " ".join(item)
            base = 0.6 if len(spaces) >= 2 else 0.0
            if ordered:
                p = rich_paragraph(doc, f"{marker}\t{body_text}",
                                   indent=base + 0.35, justify=False)
                p.paragraph_format.first_line_indent = Inches(-0.35)
                set_tab_stop(p, base + 0.35)
            else:
                p = rich_paragraph(doc, body_text, style=style, indent=base)

            # A short list is kept whole. The four contributions at the end of
            # the Literature Review were splitting three-and-one, leaving item 4
            # alone on a page of its own, and hand-tuning the text above it only
            # moves the break to the next edit. Long lists are still allowed to
            # split, because holding an eleven-item list together would push
            # half a page of white space ahead of it.
            if more_list_items(lines, i) and list_run_length(lines, i) <= 5:
                p.paragraph_format.keep_with_next = True
            continue

        buffer = [line]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if (not nxt or nxt.startswith(("#", "|", ">", "```"))
                    or BLOCK_MARKER.match(nxt)
                    or nxt in (PAGEBREAK, SPACER)
                    or re.match(r"^\s*([-*]\s|\d+\.\s)", nxt)
                    or re.fullmatch(r"-{3,}", nxt)):
                break
            buffer.append(nxt)
            i += 1

        joined = " ".join(buffer)
        if is_references and re.match(r"^\[\d+\]", joined):
            reference_paragraph(doc, joined)
        else:
            rich_paragraph(doc, joined)


# ---------------------------------------------------------------------------

def new_counters(labels: dict | None = None) -> dict:
    return {"section": "0", "table": 0, "figure": 0, "chapters_seen": 0,
            "labels": labels if labels is not None else {},
            "unresolved": [], "quiet": False}


def collect_labels() -> dict:
    """Number every exhibit, by rendering into a document that is discarded.

    A reference almost always precedes the exhibit it names, so the numbers
    cannot be resolved in a single pass. Rather than reimplement the counting
    rules in a separate scanner, which would drift from the renderer the first
    time either changed, the whole body is rendered once into a throwaway
    document purely to fill the key-to-number map.
    """
    scratch = Document()
    ensure_caption_styles(scratch)
    counters = new_counters()
    counters["quiet"] = True
    render(scratch, CHAPTERS / "00-front-matter.md", counters)
    for name in BODY_SECTIONS:
        counters["table"] = 0
        counters["figure"] = 0
        render(scratch, CHAPTERS / name, counters, chapter_breaks=True)
    return counters["labels"]


def main() -> int:
    missing = [n for n in BODY_SECTIONS if not (CHAPTERS / n).exists()]
    if missing:
        print("Missing sections: " + ", ".join(missing))
        print("Run the restructure first.")
        return 1

    labels = collect_labels()
    print(f"  numbered {len(labels)} referenced exhibits")

    doc = Document()
    enable_hyphenation(doc)
    ensure_caption_styles(doc)
    blacken_contents_styles(doc)

    normal = doc.styles["Normal"]
    normal.font.name = BODY_FONT
    normal.font.size = Pt(BODY_PT)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.widow_control = True

    # The list and caption styles otherwise inherit a font from the template.
    for name in ("Heading 1", "Heading 2", "Heading 3", "Heading 4",
                 "List Bullet", "List Number", "Caption"):
        try:
            style = doc.styles[name]
        except KeyError:
            continue
        style.font.name = BODY_FONT
        style.font.size = Pt(11 if name == "Caption" else BODY_PT)
        style.font.color.rgb = RGBColor(0, 0, 0)
        if name == "Caption":
            style.font.italic = False
            style.font.bold = False
            style.font.color.rgb = None

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

    # Spacing on both title pages is counted, not eyeballed. At 1.5 line
    # spacing Word sets a 14 pt line at about 30 pt, and one blank paragraph
    # too many pushed the closing lines onto a page of their own.
    for _ in range(2):
        doc.add_paragraph()
    centred(doc, TITLE, 16, bold=True, space_after=12)
    for _ in range(3):
        doc.add_paragraph()
    centred(doc, "A thesis submitted to NSBM Green University for the degree of", 14)
    centred(doc, DEGREE, 14)
    for _ in range(2):
        doc.add_paragraph()
    centred(doc, "By", 14)
    centred(doc, AUTHOR, 14)
    for _ in range(3):
        doc.add_paragraph()
    centred(doc, DEPARTMENT, 14)
    centred(doc, FACULTY, 14)
    centred(doc, "NSBM Green University", 14)
    centred(doc, "Sri Lanka", 14)
    centred(doc, SUBMISSION, 14)
    doc.add_page_break()

    counters = new_counters(labels)
    render(doc, CHAPTERS / "00-front-matter.md", counters)

    # Table of contents and lists, as field codes Word populates on update.
    for title, instruction in [
        ("TABLE OF CONTENTS", r'TOC \o "1-3" \h \z \u'),
        # Collected by paragraph STYLE, not by SEQ field: see
        # ensure_caption_styles for why the \c switch cannot work here.
        ("LIST OF FIGURES", rf'TOC \h \z \t "{FIGURE_CAPTION_STYLE},1"'),
        ("LIST OF TABLES", rf'TOC \h \z \t "{TABLE_CAPTION_STYLE},1"'),
    ]:
        doc.add_page_break()
        heading(doc, title, 1)
        p = doc.add_paragraph()
        add_field(p, instruction)

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
        render(doc, path, counters, chapter_breaks=True)

    if counters["unresolved"]:
        unique = sorted(set(counters["unresolved"]))
        print("\nUnresolved exhibit references, so the document is NOT "
              "written:")
        for key in unique:
            print(f"    @{key}")
        print("Each must match the key in a [Table: key | ...] or "
              "[Image: file | key | ...] marker.")
        return 1

    doc.save(OUTPUT)

    words = sum(len((CHAPTERS / n).read_text(encoding="utf-8").split())
                for n in BODY_SECTIONS)
    words += len((CHAPTERS / "00-front-matter.md").read_text(encoding="utf-8").split())

    try:
        shown = OUTPUT.relative_to(ROOT)
    except ValueError:
        shown = OUTPUT
    print(f"\nWrote {shown}")
    print(f"  ~{words:,} words, {len(doc.tables)} tables")
    print("\nRun scripts/export_pdf.py to populate the contents lists and "
          "write the PDF.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
