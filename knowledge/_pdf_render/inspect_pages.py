import fitz
from pathlib import Path

PDF = Path(r"d:\BLUE-WATER\docs\knowledge\23_MSRX_SUPER_TRANSFER_VISUAL_DIAGRAMS.pdf")
OUT = Path(r"d:\BLUE-WATER\docs\knowledge\_pdf_render\validation_pages")
OUT.mkdir(parents=True, exist_ok=True)

doc = fitz.open(PDF)
for i, p in enumerate(doc):
    text = (p.get_text("text") or "").replace("\u2192", "->")
    title = text.strip().splitlines()[0] if text.strip() else ""
    print(f"p{i+1:02d}: {p.rect.width:.0f}x{p.rect.height:.0f} imgs={len(p.get_images())} | {title[:100]}")
    pix = p.get_pixmap(matrix=fitz.Matrix(1.05, 1.05))
    pix.save(str(OUT / f"full_page_{i+1:02d}.png"))
print("pages", doc.page_count)
doc.close()
