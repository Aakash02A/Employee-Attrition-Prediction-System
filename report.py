"""Tiny in-memory PDF builder (ReportLab). Nothing is written to disk."""
from datetime import datetime
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

DISCLAIMER = ("This application is an educational machine learning prototype. Its analyses and attrition "
              "predictions are based on the available dataset and may be inaccurate or affected by bias. "
              "They must not be used as the sole basis for employment decisions.")


def make_pdf(title: str, blocks: list) -> bytes:
    """blocks: ("h", text) | ("p", text) | ("table", [header_row, *rows]). Returns PDF bytes."""
    styles = getSampleStyleSheet()
    small = styles["BodyText"].clone("small", fontSize=8, leading=10)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    story = [Paragraph(escape(title), styles["Title"]),
             Paragraph(f"Employee Attrition Prediction System &nbsp;|&nbsp; Generated {stamp}", styles["Normal"]),
             Spacer(1, 12)]
    for kind, content in blocks:
        if kind == "h":
            story += [Spacer(1, 8), Paragraph(escape(content), styles["Heading2"])]
        elif kind == "p":
            story += [Paragraph(escape(content), styles["BodyText"]), Spacer(1, 4)]
        elif kind == "table" and content:
            data = [[Paragraph(escape(str(c)), small) for c in row] for row in content]
            t = Table(data, repeatRows=1)
            t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef7")),
                                   ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                                   ("VALIGN", (0, 0), (-1, -1), "TOP")]))
            story += [t, Spacer(1, 8)]
    story += [Spacer(1, 12), Paragraph("<b>Notice:</b> " + escape(DISCLAIMER), small)]

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.drawString(2 * cm, 1.2 * cm, "Employee Attrition Prediction System")
        canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Page {doc.page}")
        canvas.restoreState()

    buf = BytesIO()
    SimpleDocTemplate(buf, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                      topMargin=2 * cm, bottomMargin=2 * cm, title=title).build(
        story, onFirstPage=footer, onLaterPages=footer)
    return buf.getvalue()


def fmt_table(rows, header):
    return [header, *[[(f"{v:.3f}" if isinstance(v, float) else v) for v in r] for r in rows]]
