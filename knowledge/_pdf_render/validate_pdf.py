"""Validate rendered PDF for Mermaid leftovers and diagram presence."""
from __future__ import annotations

import json
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image

ROOT = Path(r"d:\BLUE-WATER\docs\knowledge")
PDF = ROOT / "23_MSRX_SUPER_TRANSFER_VISUAL_DIAGRAMS.pdf"
DIAG = ROOT / "_pdf_render" / "diagrams"
OUT_DIR = ROOT / "_pdf_render" / "validation_pages"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CHECKS = {}

doc = fitz.open(PDF)
CHECKS["opens"] = True
CHECKS["page_count"] = doc.page_count
CHECKS["pdf_bytes"] = PDF.stat().st_size

full_text = ""
for i, page in enumerate(doc):
    full_text += page.get_text("text") + "\n"
    # render preview for first few + key pages
    if i < 5 or i in {6, 8, 10, 12, 16, doc.page_count - 1}:
        pix = page.get_pixmap(matrix=fitz.Matrix(1.2, 1.2))
        out = OUT_DIR / f"page_{i+1:02d}.png"
        pix.save(str(out))

# Raw mermaid code should NOT appear as the diagram body
bad_markers = [
    "```mermaid",
    "flowchart TD\n",
    "sequenceDiagram\n",
]
# Some labels may contain words like flowchart in explanations — check code fence mainly
CHECKS["raw_mermaid_fence"] = "```mermaid" in full_text
CHECKS["has_how_to_read"] = "HOW TO READ THESE DIAGRAMS" in full_text
CHECKS["has_unknown"] = ("UNKNOWN ENRICHMENT" in full_text) or ("KT CONFIRMATION REQUIRED" in full_text)
CHECKS["has_seller_loan_example"] = "117-42_2208066387" in full_text
CHECKS["has_cover"] = "MSRX" in full_text and "SUPER TRANSFER" in full_text

# Diagram section titles
missing_titles = []
for n in range(1, 16):
    if f"Diagram {n}." not in full_text:
        missing_titles.append(n)
CHECKS["missing_diagram_titles"] = missing_titles

# Image presence on diagram pages (pages after cover/toc/legend)
image_pages = 0
for page in doc:
    if page.get_images():
        image_pages += 1
CHECKS["pages_with_images"] = image_pages

# PNG diagram sanity
png_info = []
for n in range(1, 16):
    p = DIAG / f"diagram_{n:02d}.png"
    with Image.open(p) as im:
        png_info.append({"n": n, "w": im.size[0], "h": im.size[1], "bytes": p.stat().st_size})
CHECKS["png_info"] = png_info

# Search page text for processLoan / post_loan_to_sqs (may be in images only — OK)
CHECKS["text_has_processLoan"] = "processLoan" in full_text
CHECKS["text_has_post_loan"] = "post_loan_to_sqs" in full_text or "seller-loan_id" in full_text

# Fail conditions
failures = []
if CHECKS["raw_mermaid_fence"]:
    failures.append("Raw ```mermaid fence found in PDF text")
if CHECKS["missing_diagram_titles"]:
    failures.append(f"Missing diagram titles: {CHECKS['missing_diagram_titles']}")
if not CHECKS["has_how_to_read"]:
    failures.append("Missing HOW TO READ section")
if not CHECKS["has_unknown"]:
    failures.append("UNKNOWN / KT text not found in PDF text layer (may be image-only — check visually)")
if CHECKS["pages_with_images"] < 15:
    failures.append(f"Expected >=15 pages with images, got {CHECKS['pages_with_images']}")
if CHECKS["page_count"] < 18:
    failures.append(f"Page count unexpectedly low: {CHECKS['page_count']}")

CHECKS["failures"] = failures
CHECKS["passed"] = len(failures) == 0

(OUT_DIR / "validation_report.json").write_text(json.dumps(CHECKS, indent=2), encoding="utf-8")
print(json.dumps(CHECKS, indent=2))
print("PASSED" if CHECKS["passed"] else "FAILED")
doc.close()
