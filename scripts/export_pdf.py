"""Populate the contents fields and export the thesis to PDF.

Run:  python scripts/export_pdf.py [path/to/THESIS.docx]

Pipeline:  restructure_thesis.py -> to_ieee.py -> build_thesis_nsbm.py -> this

WHY THIS EXISTS
---------------
The Table of Contents, List of Figures and List of Tables are Word field codes.
A field code holds an instruction, not a result, so a freshly built document
shows three empty headings until something asks Word to evaluate them. Page
numbers cannot be written by the builder either: they depend on how the text
falls on the page, which only a layout engine knows.

The usual instruction is "open it in Word and press Ctrl+A then F9". That works,
but it is a manual step that is easy to forget, and forgetting it means handing
in a thesis with an empty contents page. This script drives Word to do it, saves
the result back into the .docx, and exports the PDF from the same laid-out
document, so both files carry real page numbers.

Word is automated through PowerShell rather than pywin32, which keeps the
repository free of a platform-specific Python dependency.

REQUIREMENTS
------------
Microsoft Word on Windows. If Word is not installed the script says so and exits
non-zero, leaving the .docx untouched and still usable with the manual Ctrl+A,
F9 route.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOCX = ROOT / "docs" / "06-thesis" / "THESIS-NSBM.docx"

# wdExportFormatPDF = 17, wdExportCreateHeadingBookmarks = 1.
# The bookmarks give the PDF a navigable outline built from the heading styles,
# which is how an examiner moves around a 120-page document.
POWERSHELL = r"""
$ErrorActionPreference = 'Stop'
$docx = '{docx}'
$pdf  = '{pdf}'

try {{
    $word = New-Object -ComObject Word.Application
}} catch {{
    Write-Output 'NOWORD'
    exit 3
}}

$word.Visible = $false
$word.DisplayAlerts = 0

$doc = $word.Documents.Open($docx, $false, $false)
try {{
    # Two passes. Updating the fields lays out the entries; repaginating then
    # settles the page numbers; the second pass writes the settled numbers into
    # the contents lists. With one pass the numbers can be short by a page
    # wherever the contents list itself changes length.
    foreach ($pass in 1..2) {{
        $doc.Fields.Update() | Out-Null
        foreach ($toc in $doc.TablesOfContents) {{ $toc.Update() }}
        foreach ($tof in $doc.TablesOfFigures) {{ $tof.Update() }}
        $doc.Repaginate()
    }}

    $pages = $doc.ComputeStatistics(2)
    $words = $doc.ComputeStatistics(0)

    $doc.Save()
    $doc.ExportAsFixedFormat($pdf, 17, $false, 0, 0, 0, 0, 0, $true, $true, 1)
    Write-Output "OK $pages $words"
}} finally {{
    $doc.Close(0)
    $word.Quit()
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($word)
}}
"""


def export(docx: Path) -> int:
    if not docx.exists():
        print(f"Not found: {docx}")
        print("Run scripts/build_thesis_nsbm.py first.")
        return 1

    pdf = docx.with_suffix(".pdf")
    script = POWERSHELL.format(docx=str(docx).replace("'", "''"),
                               pdf=str(pdf).replace("'", "''"))

    print(f"Updating fields and exporting {docx.name} ...")
    result = subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
        capture_output=True, text=True,
    )
    out = (result.stdout or "").strip()

    if "NOWORD" in out or result.returncode == 3:
        print("Microsoft Word is not available on this machine.")
        print("The .docx is still valid: open it and press Ctrl+A then F9 to "
              "populate the contents lists.")
        return 2

    if not out.startswith("OK"):
        print("Word reported a problem.")
        print((result.stderr or out or "no output").strip()[:2000])
        print("\nIf the thesis is open in Word, close it and run this again.")
        return 1

    _, pages, words = out.split()
    try:
        shown_docx = docx.relative_to(ROOT)
        shown_pdf = pdf.relative_to(ROOT)
    except ValueError:
        shown_docx, shown_pdf = docx, pdf

    print(f"\nContents lists populated in {shown_docx}")
    print(f"Wrote {shown_pdf}")
    print(f"  {int(pages)} pages, {int(words):,} words")
    return 0


def main() -> int:
    docx = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_DOCX
    return export(docx)


if __name__ == "__main__":
    sys.exit(main())
