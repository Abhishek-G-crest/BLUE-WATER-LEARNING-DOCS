# PDF render workspace (documentation tooling only)

Isolated from `msrx_v2.0`, `msrx-frontend`, and `super_transfer_client`.

## Regenerate PDF

```bat
cd docs\knowledge\_pdf_render
.venv\Scripts\python.exe build_pdf.py
.venv\Scripts\python.exe validate_pdf.py
```

Output: `../23_MSRX_SUPER_TRANSFER_VISUAL_DIAGRAMS.pdf`

## Tools used

- `@mermaid-js/mermaid-cli` (mmdc) → PNG/SVG diagrams
- ReportLab → professional multi-orientation PDF
- Playwright Chromium (pulled by mermaid-cli / optional)
- PyMuPDF → validation only

Do not install these into application repositories.
