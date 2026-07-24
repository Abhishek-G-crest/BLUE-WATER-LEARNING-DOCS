"""
Isolated PDF builder for 24_SUPER_TRANSFER_WORKER_INTERNAL_FLOW.md
Does NOT overwrite 23_* PDFs. Uses separate diagrams_24/ output folder.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from PIL import Image
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image as RLImage,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(r"d:\BLUE-WATER\docs\knowledge")
SRC = ROOT / "24_SUPER_TRANSFER_WORKER_INTERNAL_FLOW.md"
BUILD = ROOT / "_pdf_render"
DIAG_DIR = BUILD / "diagrams_24"
OUT_PDF = ROOT / "24_SUPER_TRANSFER_WORKER_INTERNAL_FLOW.pdf"

# Wide diagrams → landscape A4
LANDSCAPE_IDS = {9, 10, 12, 13, 16, 17, 18}
# Very tall flowcharts → custom tall portrait pages
TALL_IDS = {1, 2, 3, 4, 5, 6, 7, 8, 11, 14, 15, 19, 20}

COVER_TITLE_1 = "BLUE WATER / MSRX"
COVER_TITLE_2 = "SUPER TRANSFER WORKER"
COVER_SUB = "Internal Processing Flow<br/>SQS → main.py → processLoan → DD / S3 / DynamoDB"
COVER_TAG = "Developer KT / Deep Worker Onboarding"
HEADER_LEFT = "BLUE WATER / MSRX  —  Super Transfer Worker Internal Flow"


def extract_sections(md: str):
    parts = re.split(r"\n(?=## \d+\. )", md)
    sections = []
    for part in parts:
        m = re.match(r"## (\d+)\.\s+(.+?)\n", part)
        if not m:
            continue
        num = int(m.group(1))
        title = m.group(2).strip()
        mm = re.search(r"```mermaid\n(.*?)```", part, re.S)
        if not mm:
            raise RuntimeError(f"No mermaid block in section {num}")
        mermaid = mm.group(1).strip()
        before = part[: mm.start()]
        intro_lines = before.split("\n", 1)[1].strip() if "\n" in before else ""
        take = re.search(r"\*\*KEY TAKEAWAY:\*\*\s*(.+)", part)
        takeaway = take.group(1).strip() if take else ""
        sections.append(
            {
                "num": num,
                "title": title,
                "intro": intro_lines,
                "mermaid": mermaid,
                "takeaway": takeaway,
            }
        )
    how = ""
    hm = re.search(r"# HOW TO READ THESE DIAGRAMS\n(.*?)(?:\n---|\Z)", md, re.S)
    if hm:
        how = hm.group(1).strip()
    legend = ""
    lm = re.search(r"## Legend — CONFIRMED vs UNKNOWN\n(.*?)(?=\n---)", md, re.S)
    if lm:
        legend = lm.group(1).strip()
    return sections, how, legend


def ensure_diagrams(sections):
    DIAG_DIR.mkdir(parents=True, exist_ok=True)
    config = {
        "theme": "base",
        "themeVariables": {
            "fontFamily": "Segoe UI, Arial, sans-serif",
            "fontSize": "18px",
            "primaryColor": "#E8F1F8",
            "primaryTextColor": "#102A43",
            "primaryBorderColor": "#243B53",
            "lineColor": "#334E68",
            "secondaryColor": "#FFF3CD",
            "tertiaryColor": "#F0F4F8",
            "noteBkgColor": "#FFF8E1",
            "noteTextColor": "#102A43",
        },
        "flowchart": {
            "htmlLabels": True,
            "curve": "basis",
            "padding": 20,
            "nodeSpacing": 45,
            "rankSpacing": 55,
        },
        "sequence": {"mirrorActors": False, "messageMargin": 45, "actorMargin": 55, "width": 190},
    }
    cfg_path = DIAG_DIR / "mermaid-config.json"
    cfg_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    mmdc = BUILD / "node_modules" / ".bin" / "mmdc.cmd"

    pngs = {}
    for s in sections:
        mmd = DIAG_DIR / f"diagram_{s['num']:02d}.mmd"
        png = DIAG_DIR / f"diagram_{s['num']:02d}.png"
        svg = DIAG_DIR / f"diagram_{s['num']:02d}.svg"
        mmd.write_text(s["mermaid"] + "\n", encoding="utf-8")
        # Re-render if missing
        if not png.exists() or png.stat().st_size < 1000:
            width = 2600 if s["num"] in LANDSCAPE_IDS else 1800
            print(f"Rendering diagram {s['num']} ...")
            cmd = [
                str(mmdc),
                "-i",
                str(mmd),
                "-o",
                str(png),
                "-c",
                str(cfg_path),
                "-b",
                "white",
                "-s",
                "2",
                "-w",
                str(width),
            ]
            r = subprocess.run(cmd, cwd=str(BUILD), capture_output=True, text=True)
            if r.returncode != 0:
                raise RuntimeError(f"mmdc failed diagram {s['num']}: {r.stderr}")
            subprocess.run(
                [
                    str(mmdc),
                    "-i",
                    str(mmd),
                    "-o",
                    str(svg),
                    "-c",
                    str(cfg_path),
                    "-b",
                    "white",
                    "-s",
                    "2",
                    "-w",
                    str(width),
                ],
                cwd=str(BUILD),
                capture_output=True,
                text=True,
            )
        else:
            print(f"Reusing existing PNG diagram {s['num']}")
        pngs[s["num"]] = png
    return pngs


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")


def md_inline_to_para(text: str) -> str:
    t = esc(text)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"`([^`]+)`", r"<font face='Courier' size='9'>\1</font>", t)
    return t


def page_size_for(num: int, png: Path):
    """Choose page size so diagram text stays readable."""
    margin = 14 * mm
    header = 22 * mm
    footer = 16 * mm
    text_budget = 1.35 * inch  # title + intro + takeaway approx

    with Image.open(png) as im:
        iw, ih = im.size

    if num in LANDSCAPE_IDS:
        base = landscape(A4)
        usable_w = base[0] - 2 * margin
        usable_h = base[1] - header - footer - text_budget
        scale = min(usable_w / iw, usable_h / ih)
        return base, iw * scale, ih * scale

    # Portrait / tall
    usable_w = A4[0] - 2 * margin
    # Prefer fitting to width for readability of node text
    scale_w = usable_w / iw
    needed_h = ih * scale_w + header + footer + text_budget + 10 * mm

    max_h = A4[1] * 2.6  # ~2.6x A4 tall custom page
    if num in TALL_IDS and needed_h > A4[1]:
        page_h = min(needed_h, max_h)
        if needed_h > max_h:
            # Will fit by min scale on tall page
            usable_h = page_h - header - footer - text_budget
            scale = min(usable_w / iw, usable_h / ih)
            return (A4[0], page_h), iw * scale, ih * scale
        return (A4[0], page_h), iw * scale_w, ih * scale_w

    # Standard portrait A4
    usable_h = A4[1] - header - footer - text_budget
    scale = min(usable_w / iw, usable_h / ih)
    return A4, iw * scale, ih * scale


def split_png_vertical(png: Path, max_chunk_h_px: int) -> list[Path]:
    """Split a very tall PNG into vertical chunks for multi-page readability."""
    chunks = []
    with Image.open(png) as im:
        w, h = im.size
        if h <= max_chunk_h_px:
            return [png]
        y = 0
        idx = 0
        while y < h:
            box = (0, y, w, min(y + max_chunk_h_px, h))
            chunk = im.crop(box)
            out = png.with_name(f"{png.stem}_part{idx+1}.png")
            chunk.save(out)
            chunks.append(out)
            y += max_chunk_h_px
            idx += 1
    return chunks


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="CoverTitle",
            fontName="Helvetica-Bold",
            fontSize=28,
            leading=34,
            alignment=TA_CENTER,
            textColor=HexColor("#0B2545"),
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CoverSub",
            fontName="Helvetica",
            fontSize=16,
            leading=22,
            alignment=TA_CENTER,
            textColor=HexColor("#13315C"),
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SecTitle",
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=17,
            textColor=HexColor("#0B2545"),
            spaceBefore=2,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodyText2",
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            alignment=TA_JUSTIFY,
            textColor=HexColor("#243B53"),
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Takeaway",
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=HexColor("#102A43"),
            spaceBefore=6,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Small",
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=HexColor("#486581"),
            alignment=TA_CENTER,
        )
    )
    styles.add(
        ParagraphStyle(
            name="HowItem",
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=HexColor("#102A43"),
            leftIndent=10,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="PartNote",
            fontName="Helvetica-Oblique",
            fontSize=8,
            leading=10,
            textColor=HexColor("#627D98"),
            spaceAfter=4,
        )
    )
    return styles


def add_header_footer(canvas, doc, pagesize):
    canvas.saveState()
    page_w, page_h = pagesize
    canvas.setStrokeColor(HexColor("#0B2545"))
    canvas.setLineWidth(1)
    canvas.line(15 * mm, page_h - 12 * mm, page_w - 15 * mm, page_h - 12 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(HexColor("#486581"))
    canvas.drawString(15 * mm, page_h - 10 * mm, HEADER_LEFT)
    canvas.drawRightString(page_w - 15 * mm, page_h - 10 * mm, "Developer KT / Onboarding")
    canvas.line(15 * mm, 12 * mm, page_w - 15 * mm, 12 * mm)
    canvas.drawCentredString(page_w / 2, 7 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build_cover(styles):
    story = []
    story.append(Spacer(1, 1.6 * inch))
    story.append(Paragraph(COVER_TITLE_1, styles["CoverTitle"]))
    story.append(Spacer(1, 0.25 * inch))
    story.append(Paragraph(COVER_TITLE_2, styles["CoverTitle"]))
    story.append(Spacer(1, 0.35 * inch))
    story.append(
        Paragraph(
            COVER_SUB,
            styles["CoverSub"],
        )
    )
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph(COVER_TAG, styles["CoverSub"]))
    story.append(Spacer(1, 0.35 * inch))
    story.append(
        Paragraph(
            "Source: <font face='Courier'>24_SUPER_TRANSFER_WORKER_INTERNAL_FLOW.md</font><br/>"
            "All Mermaid diagrams rendered visually — no raw Mermaid source as diagrams.<br/>"
            "UNKNOWN / KT CONFIRMATION REQUIRED boxes preserved from audit.<br/>"
            "Does NOT overwrite document 23 architecture PDF.",
            styles["Small"],
        )
    )
    story.append(Spacer(1, 0.6 * inch))
    data = [
        [Paragraph("<b>CONFIRMED FROM CODE / CONFIG</b>", styles["Small"]), "Solid boxes and normal arrows"],
        [
            Paragraph("<b>UNKNOWN — KT CONFIRMATION REQUIRED</b>", styles["Small"]),
            "??? boxes — do not invent architecture",
        ],
    ]
    t = Table(data, colWidths=[3.2 * inch, 3.5 * inch])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), HexColor("#E8F1F8")),
                ("BACKGROUND", (0, 1), (-1, 1), HexColor("#FFF3CD")),
                ("BOX", (0, 0), (-1, -1), 0.5, HexColor("#334E68")),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, HexColor("#9FB3C8")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(t)
    story.append(PageBreak())
    return story


def build_toc(styles, sections):
    story = [Paragraph("Document Contents", styles["SecTitle"]), Spacer(1, 0.1 * inch)]
    for s in sections:
        if s["num"] in LANDSCAPE_IDS:
            orient = "Landscape"
        elif s["num"] in TALL_IDS:
            orient = "Tall portrait"
        else:
            orient = "Portrait"
        story.append(
            Paragraph(
                f"<b>Diagram {s['num']}.</b> {esc(s['title'])}  <font color='#829AB1'>({orient})</font>",
                styles["HowItem"],
            )
        )
    story.append(Paragraph("HOW TO READ THESE DIAGRAMS", styles["HowItem"]))
    story.append(PageBreak())
    return story


def build_how_to_read(styles, how_md: str):
    story = [Paragraph("HOW TO READ THESE DIAGRAMS", styles["SecTitle"]), Spacer(1, 0.1 * inch)]
    for line in how_md.splitlines():
        line = line.strip()
        if not line:
            continue
        story.append(Paragraph(md_inline_to_para(line), styles["HowItem"]))
    story.append(Spacer(1, 0.2 * inch))
    story.append(
        Paragraph(
            "<b>Reminder:</b> Treat every <b>??? UNKNOWN ???</b> box as a question to ask in KT — "
            "not as a finished connector. Do not assume Lambda unless confirmed.",
            styles["BodyText2"],
        )
    )
    return story


def main():
    print("Reading", SRC)
    md = SRC.read_text(encoding="utf-8")
    sections, how, legend = extract_sections(md)
    if len(sections) != 20:
        raise RuntimeError(f"Expected 20 diagram sections, found {len(sections)}")

    # Reuse existing rendered PNGs when present (delete manually to force re-render)
    # for p in DIAG_DIR.glob("diagram_*.png"):
    #     p.unlink(missing_ok=True)
    for p in DIAG_DIR.glob("diagram_*_part*.png"):
        p.unlink(missing_ok=True)

    pngs = ensure_diagrams(sections)
    styles = build_styles()

    # Compute unique page sizes / templates
    template_specs = {}  # name -> pagesize
    template_specs["cover"] = A4
    template_specs["portrait"] = A4
    template_specs["landscape"] = landscape(A4)

    section_layouts = {}
    for s in sections:
        png = pngs[s["num"]]
        pagesize, disp_w, disp_h = page_size_for(s["num"], png)
        # If still too tall even on max custom page, split image
        with Image.open(png) as im:
            iw, ih = im.size
        margin = 14 * mm
        header = 22 * mm
        footer = 16 * mm
        text_budget = 1.35 * inch
        usable_h = pagesize[1] - header - footer - text_budget
        usable_w = pagesize[0] - 2 * margin
        # If fitted image would be < 55% of width for a tall chart, prefer split at width-fit chunks
        scale_w = usable_w / iw
        height_at_width_fit = ih * scale_w
        parts = [png]
        part_sizes = [(disp_w, disp_h)]
        if s["num"] in TALL_IDS and height_at_width_fit > usable_h * 1.05:
            # Split so each chunk fits width-scaled onto the chosen page height
            max_chunk_h_px = int(usable_h / scale_w)
            parts = split_png_vertical(png, max_chunk_h_px)
            part_sizes = []
            for part in parts:
                with Image.open(part) as im2:
                    pw, ph = im2.size
                part_sizes.append((pw * scale_w, ph * scale_w))
            # Use portrait/tall page that matches width-fit
            pagesize = (A4[0], min(A4[1] * 2.6, usable_h + header + footer + text_budget + 10 * mm))
            # recompute usable for consistency
            pagesize = (A4[0], max(A4[1], header + footer + text_budget + part_sizes[0][1] + 10 * mm))

        tname = f"sec_{s['num']}"
        template_specs[tname] = pagesize
        section_layouts[s["num"]] = {
            "template": tname,
            "pagesize": pagesize,
            "parts": parts,
            "part_sizes": part_sizes,
        }

    doc = BaseDocTemplate(
        str(OUT_PDF),
        title="Super Transfer Worker Internal Flow",
        author="BLUE WATER / MSRX KT",
    )

    margin = 14 * mm

    def make_frame(pagesize):
        w, h = pagesize
        return Frame(margin, margin, w - 2 * margin, h - 2 * margin, id="normal")

    def on_cover(canvas, doc_):
        canvas.saveState()
        canvas.setFillColor(HexColor("#0B2545"))
        canvas.rect(0, A4[1] - 18 * mm, A4[0], 18 * mm, fill=1, stroke=0)
        canvas.setFillColor(white)
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawCentredString(A4[0] / 2, A4[1] - 11 * mm, "CONFIDENTIAL — INTERNAL DEVELOPER KT")
        canvas.restoreState()

    templates = [
        PageTemplate(id="cover", frames=[make_frame(A4)], pagesize=A4, onPage=on_cover),
        PageTemplate(
            id="portrait",
            frames=[make_frame(A4)],
            pagesize=A4,
            onPage=lambda c, d: add_header_footer(c, d, A4),
        ),
        PageTemplate(
            id="landscape",
            frames=[make_frame(landscape(A4))],
            pagesize=landscape(A4),
            onPage=lambda c, d: add_header_footer(c, d, landscape(A4)),
        ),
    ]
    for s in sections:
        layout = section_layouts[s["num"]]
        ps = layout["pagesize"]
        tname = layout["template"]
        templates.append(
            PageTemplate(
                id=tname,
                frames=[make_frame(ps)],
                pagesize=ps,
                onPage=lambda c, d, ps=ps: add_header_footer(c, d, ps),
            )
        )
    doc.addPageTemplates(templates)

    story = []
    # Page 1 uses the first template ("cover") automatically.
    cover_flow = build_cover(styles)
    # build_cover ends with PageBreak — replace so template switch happens first
    if cover_flow and isinstance(cover_flow[-1], PageBreak):
        cover_flow = cover_flow[:-1]
    story.extend(cover_flow)
    story.append(NextPageTemplate("portrait"))
    story.append(PageBreak())
    toc_flow = build_toc(styles, sections)
    if toc_flow and isinstance(toc_flow[-1], PageBreak):
        toc_flow = toc_flow[:-1]
    story.extend(toc_flow)
    story.append(NextPageTemplate("portrait"))
    story.append(PageBreak())

    # Legend
    story.append(Paragraph("Legend — CONFIRMED vs UNKNOWN", styles["SecTitle"]))
    if legend:
        for line in legend.splitlines():
            line = line.strip()
            if not line or line.startswith("|---") or line.startswith("| Visual"):
                continue
            if line.startswith("|"):
                # simplify table rows
                cells = [c.strip() for c in line.strip("|").split("|")]
                if len(cells) >= 2:
                    story.append(
                        Paragraph(f"<b>{esc(cells[0])}</b> — {esc(cells[1])}", styles["BodyText2"])
                    )
            else:
                story.append(Paragraph(md_inline_to_para(line), styles["BodyText2"]))
    story.append(
        Paragraph(
            "<b>Rule:</b> If a box says UNKNOWN, the audit did <b>not</b> find that component "
            "in msrx-frontend, msrx_v2.0, or super_transfer_client.",
            styles["BodyText2"],
        )
    )

    for s in sections:
        layout = section_layouts[s["num"]]
        story.append(NextPageTemplate(layout["template"]))
        story.append(PageBreak())

        for idx, (part, (dw, dh)) in enumerate(zip(layout["parts"], layout["part_sizes"])):
            if idx > 0:
                story.append(NextPageTemplate(layout["template"]))
                story.append(PageBreak())
            title = f"Diagram {s['num']}. {esc(s['title'])}"
            if len(layout["parts"]) > 1:
                title += f" — Part {idx+1}/{len(layout['parts'])}"
            story.append(Paragraph(title, styles["SecTitle"]))
            if idx == 0 and s["intro"]:
                story.append(Paragraph(md_inline_to_para(s["intro"]), styles["BodyText2"]))
            elif idx > 0:
                story.append(
                    Paragraph(
                        "Continued from previous page (same diagram — split only for readability).",
                        styles["PartNote"],
                    )
                )
            story.append(Spacer(1, 3))
            story.append(RLImage(str(part), width=dw, height=dh))
            if idx == len(layout["parts"]) - 1 and s["takeaway"]:
                story.append(Spacer(1, 6))
                story.append(
                    Paragraph(
                        f"<b>KEY TAKEAWAY:</b> {md_inline_to_para(s['takeaway'])}",
                        styles["Takeaway"],
                    )
                )

    story.append(NextPageTemplate("portrait"))
    story.append(PageBreak())
    story.extend(build_how_to_read(styles, how))

    print("Writing PDF", OUT_PDF)
    doc.build(story)
    print("PDF size", OUT_PDF.stat().st_size)

    report = {
        "pdf": str(OUT_PDF),
        "diagrams_rendered": 20,
        "pdf_bytes": OUT_PDF.stat().st_size,
        "landscape_ids": sorted(LANDSCAPE_IDS),
        "tall_ids": sorted(TALL_IDS),
        "layouts": {
            str(k): {
                "pagesize": list(v["pagesize"]),
                "parts": len(v["parts"]),
            }
            for k, v in section_layouts.items()
        },
    }
    (BUILD / "build_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print("DONE")


if __name__ == "__main__":
    main()
