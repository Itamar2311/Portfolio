from datetime import datetime
from io import BytesIO
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def clean(text):
    if not text:
        return ""
    return str(text).encode('ascii', 'ignore').decode('ascii')


def set_cell_bg(cell, hex_color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)


def add_cell_text(cell, text, bold=False, font_size=10, color=None):
    para = cell.paragraphs[0]
    run = para.add_run(clean(str(text or "")))
    run.bold = bold
    run.font.size = Pt(font_size)
    run.font.name = "Arial"
    if color:
        run.font.color.rgb = RGBColor.from_string(color)


def add_section_heading(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '4')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), 'CCCCCC')
    pBdr.append(bottom)
    pPr.append(pBdr)
    run = p.add_run(clean(text).upper())
    run.bold = True
    run.font.size = Pt(11)
    run.font.name = "Arial"
    run.font.color.rgb = RGBColor.from_string("1F3864")


def add_body(doc, text, italic=False, color=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(clean(str(text or "")))
    run.font.size = Pt(10)
    run.font.name = "Arial"
    run.italic = italic
    if color:
        run.font.color.rgb = RGBColor.from_string(color)


def add_bullet(doc, text, color=None):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(2)
    run = p.runs[0] if p.runs else p.add_run()
    run.text = clean(str(text or ""))
    run.font.size = Pt(10)
    run.font.name = "Arial"
    if color:
        run.font.color.rgb = RGBColor.from_string(color)


def rec_color(rec):
    if rec == "Monitor": return "1F5C2E"
    if rec == "Follow Up": return "854F0B"
    return "A32D2D"


def rec_bg(rec):
    if rec == "Monitor": return "EAF3DE"
    if rec == "Follow Up": return "FAEEDA"
    return "FCEBEB"


def generate_report(portfolio_results: list[dict]) -> bytes:
    today = datetime.now().strftime("%B %d, %Y")
    doc = Document()

    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # ── Header ───────────────────────────────────────────────
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '12')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), '1F3864')
    pBdr.append(bottom)
    pPr.append(pBdr)
    r1 = p.add_run("GFAM MARKET WATCHLIST REPORT")
    r1.bold = True
    r1.font.size = Pt(16)
    r1.font.name = "Arial"
    r1.font.color.rgb = RGBColor.from_string("1F3864")
    r2 = p.add_run(f"    {today}")
    r2.font.size = Pt(10)
    r2.font.name = "Arial"
    r2.font.color.rgb = RGBColor.from_string("888888")

    doc.add_paragraph()

    # ── Portfolio summary table ───────────────────────────────
    add_section_heading(doc, "Portfolio Summary")
    doc.add_paragraph()

    table = doc.add_table(rows=0, cols=5)
    table.style = 'Table Grid'
    table.autofit = False
    table.columns[0].width = Inches(1.8)
    table.columns[1].width = Inches(1.4)
    table.columns[2].width = Inches(1.0)
    table.columns[3].width = Inches(1.2)
    table.columns[4].width = Inches(2.1)

    hrow = table.add_row()
    for cell, label in zip(hrow.cells, ["Company", "Sector", "Sentiment", "Action", "Key Development"]):
        set_cell_bg(cell, "1F3864")
        add_cell_text(cell, label, bold=True, font_size=9, color="FFFFFF")

    for pr in portfolio_results:
        row = table.add_row()
        analysis = pr["analysis"]
        rec = clean(analysis.get("recommendation", "Monitor"))
        sentiment = clean(analysis.get("sentiment", "Neutral"))
        score = analysis.get("sentiment_score", 5)
        score_icon = "+" if score >= 7 else "~" if score >= 4 else "-"
        summary = clean(analysis.get("news_summary", ""))[:120]

        add_cell_text(row.cells[0], pr["company"]["name"], bold=True, font_size=9)
        add_cell_text(row.cells[1], pr["company"]["sector"], font_size=9)
        add_cell_text(row.cells[2], f"{score_icon} {sentiment}", font_size=9)
        set_cell_bg(row.cells[3], rec_bg(rec))
        add_cell_text(row.cells[3], rec, bold=True, font_size=9, color=rec_color(rec))
        add_cell_text(row.cells[4], summary, font_size=9)

    doc.add_paragraph()

    # ── Per company detail ────────────────────────────────────
    add_section_heading(doc, "Company Updates")

    for pr in portfolio_results:
        company = pr["company"]
        analysis = pr["analysis"]
        rec = clean(analysis.get("recommendation", "Monitor"))

        doc.add_paragraph()
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(f"{clean(company['name'])}  |  {clean(company['sector'])}  |  Since {clean(company.get('entry_date',''))}")
        r.bold = True
        r.font.size = Pt(11)
        r.font.name = "Arial"
        r.font.color.rgb = RGBColor.from_string("1F3864")

        # Recommendation badge
        p2 = doc.add_paragraph()
        p2.paragraph_format.space_after = Pt(6)
        pPr2 = p2._p.get_or_add_pPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), rec_bg(rec))
        pPr2.append(shd)
        rb = p2.add_run(f"  {rec.upper()}  —  {clean(analysis.get('recommendation_reason', ''))}")
        rb.bold = True
        rb.font.size = Pt(9)
        rb.font.name = "Arial"
        rb.font.color.rgb = RGBColor.from_string(rec_color(rec))

        add_body(doc, analysis.get("news_summary", ""))

        sector_summary = clean(analysis.get("sector_summary", ""))
        if sector_summary:
            p3 = doc.add_paragraph()
            p3.paragraph_format.space_after = Pt(4)
            r3a = p3.add_run("Sector context: ")
            r3a.bold = True
            r3a.font.size = Pt(10)
            r3a.font.name = "Arial"
            r3b = p3.add_run(sector_summary)
            r3b.italic = True
            r3b.font.size = Pt(10)
            r3b.font.name = "Arial"
            r3b.font.color.rgb = RGBColor.from_string("444444")

        material_events = analysis.get("material_events", [])
        if material_events:
            p4 = doc.add_paragraph()
            r4 = p4.add_run("Material events: ")
            r4.bold = True
            r4.font.size = Pt(10)
            r4.font.name = "Arial"
            for event in material_events:
                add_bullet(doc, event)

        risks = analysis.get("risks_flagged", [])
        if risks:
            p5 = doc.add_paragraph()
            r5 = p5.add_run("Risks flagged: ")
            r5.bold = True
            r5.font.size = Pt(10)
            r5.font.name = "Arial"
            for risk in risks:
                add_bullet(doc, risk, color="A32D2D")

        opportunities = analysis.get("opportunities_flagged", [])
        if opportunities:
            p6 = doc.add_paragraph()
            r6 = p6.add_run("Opportunities: ")
            r6.bold = True
            r6.font.size = Pt(10)
            r6.font.name = "Arial"
            for opp in opportunities:
                add_bullet(doc, opp, color="1F5C2E")

    # ── Footer ────────────────────────────────────────────────
    footer = doc.sections[0].footer
    fp = footer.paragraphs[0]
    fr = fp.add_run(f"GFAM Market Watchlist  |  Confidential  |  {today}")
    fr.font.size = Pt(8)
    fr.font.name = "Arial"
    fr.font.color.rgb = RGBColor.from_string("999999")

    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.read()
