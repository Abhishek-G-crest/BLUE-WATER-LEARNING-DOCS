"""Validate worker internal flow PDF (doc 24). Does not touch doc 23."""
from __future__ import annotations

import json
from pathlib import Path

import fitz
from PIL import Image

ROOT = Path(r"d:\BLUE-WATER\docs\knowledge")
PDF = ROOT / "24_SUPER_TRANSFER_WORKER_INTERNAL_FLOW.pdf"
DIAG = ROOT / "_pdf_render" / "diagrams_24"
ARCH_A = ROOT / "23_MSRX_SUPER_TRANSFER_VISUAL_DIAGRAMS.pdf"
ARCH_B = ROOT / "23_MSRX_SUPER_TRANSFER_END_TO_END_ARCHITECTURE.pdf"
OUT_DIR = ROOT / "_pdf_render" / "validation_pages_24"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CHECKS = {}
doc = fitz.open(PDF)
CHECKS["opens"] = True
CHECKS["page_count"] = doc.page_count
CHECKS["pdf_bytes"] = PDF.stat().st_size

full_text = ""
for i, page in enumerate(doc):
    full_text += page.get_text("text") + "\n"
    if i < 4 or i >= doc.page_count - 2:
        pix = page.get_pixmap(matrix=fitz.Matrix(1.0, 1.0))
        pix.save(str(OUT_DIR / f"page_{i+1:02d}.png"))

CHECKS["raw_mermaid_fence"] = "```mermaid" in full_text
CHECKS["has_how_to_read"] = "HOW TO READ THESE DIAGRAMS" in full_text
CHECKS["has_unknown"] = "KT CONFIRMATION REQUIRED" in full_text or "UNKNOWN" in full_text
CHECKS["has_pkl"] = "naive_bayes_classifier.pkl" in full_text or "tf_idf.pkl" in full_text
CHECKS["has_seller_loan_example"] = "117-42_2208066387" in full_text
CHECKS["no_training_claim"] = "NO MODEL TRAINING PER LOAN" in full_text

missing = [n for n in range(1, 21) if f"Diagram {n}." not in full_text]
CHECKS["missing_diagram_titles"] = missing
CHECKS["pages_with_images"] = sum(1 for p in doc if p.get_images())

png_info = []
for n in range(1, 21):
    p = DIAG / f"diagram_{n:02d}.png"
    with Image.open(p) as im:
        png_info.append({"n": n, "w": im.size[0], "h": im.size[1], "bytes": p.stat().st_size})
CHECKS["png_info"] = png_info

CHECKS["arch_visual_exists"] = ARCH_A.exists()
CHECKS["arch_alias_exists"] = ARCH_B.exists()
CHECKS["worker_pdf_exists"] = PDF.exists()
CHECKS["arch_not_overwritten_same_as_worker"] = (
    ARCH_A.exists() and PDF.exists() and ARCH_A.stat().st_size != PDF.stat().st_size
)

failures = []
if CHECKS["raw_mermaid_fence"]:
    failures.append("Raw mermaid fence in PDF")
if missing:
    failures.append(f"Missing titles {missing}")
if not CHECKS["has_how_to_read"]:
    failures.append("Missing HOW TO READ")
if CHECKS["pages_with_images"] < 20:
    failures.append(f"Too few image pages: {CHECKS['pages_with_images']}")
if not CHECKS["arch_visual_exists"]:
    failures.append("Architecture visual PDF missing")
if not CHECKS["worker_pdf_exists"]:
    failures.append("Worker PDF missing")

CHECKS["failures"] = failures
CHECKS["passed"] = len(failures) == 0
(OUT_DIR / "validation_report.json").write_text(json.dumps(CHECKS, indent=2), encoding="utf-8")
print(json.dumps(CHECKS, indent=2))
print("PASSED" if CHECKS["passed"] else "FAILED")
doc.close()
