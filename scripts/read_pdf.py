"""Extract text from a downloaded PDF and probe it for study characteristics.

Run:  python scripts/read_pdf.py <file.pdf> [extra keyword ...]

Built for the affected-work search in docs/07-paper/affected-work-search.md.
That search has to establish, for each candidate study, whether it used the SBA
National file, whether `Term` was among its predictors, what model class it used
and what it reported. Search-result summaries cannot settle any of those - the
protocol requires the full text - and WebFetch hands back raw PDF bytes rather
than readable text, so the pages get extracted here instead.

Prints the keyword census first, because that alone excludes most candidates: a
paper with no occurrence of "SBA" is not about this dataset, whatever a search
summary implied.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pypdf

# Probes that decide inclusion. Dataset identity first, then the feature at
# issue, then model class, then the reporting details that change what a
# headline number means.
DEFAULT_PROBES = [
    "sba", "small business administration", "899,164", "899164", "1987",
    "kaggle", "should this loan",
    "term", "disbursementgross", "grappv", "sba_appv",
    "xgboost", "random forest", "gradient boosting", "decision tree",
    "logistic regression", "neural",
    "auc", "roc", "accuracy", "smote", "oversampl", "undersampl",
    "train_test_split", "temporal", "chronolog",
]

CONTEXT = 260


def extract(path: Path) -> str:
    reader = pypdf.PdfReader(str(path))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"No such file: {path}")
        return 1

    text = extract(path)
    low = text.lower()
    probes = DEFAULT_PROBES + [a.lower() for a in sys.argv[2:]]

    print(f"{path.name}  -  {len(text):,} characters extracted")
    if len(text) < 500:
        print("WARNING: almost no text extracted. Likely a scanned image PDF; "
              "this file cannot be assessed without OCR.")

    print("\nkeyword census")
    print("-" * 46)
    for probe in probes:
        n = low.count(probe)
        if n:
            print(f"  {probe:<32} {n:>4}")
    absent = [p for p in probes if low.count(p) == 0]
    if absent:
        print(f"  (absent: {', '.join(absent)})")

    # Title block, then every sentence carrying a reported figure.
    print("\nopening")
    print("-" * 46)
    print(text[:900].strip())

    print("\nreported metrics in context")
    print("-" * 46)
    seen = set()
    for m in re.finditer(r"(?i)\b(auc|roc[- ]auc|accuracy|f1|recall|precision)\b",
                         text):
        start = max(0, m.start() - CONTEXT // 2)
        snippet = " ".join(text[start:m.start() + CONTEXT].split())
        key = snippet[:70]
        if key in seen:
            continue
        seen.add(key)
        print(f"  ...{snippet}...\n")
        if len(seen) >= 12:
            break

    out = path.with_suffix(".txt")
    out.write_text(text, encoding="utf-8")
    print(f"full text written to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
