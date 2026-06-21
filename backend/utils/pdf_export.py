from datetime import datetime
from io import BytesIO

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def export_report_pdf(title: str, report: str, references: list[str] | list[dict]) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER, title=title)
    styles = getSampleStyleSheet()
    story = [
        Paragraph(title, styles["Title"]),
        Spacer(1, 12),
        Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", styles["Normal"]),
        Spacer(1, 18),
    ]

    for block in report.split("\n"):
        text = block.strip()
        if not text:
            story.append(Spacer(1, 8))
        elif text.startswith("#"):
            story.append(Paragraph(text.lstrip("# ").strip(), styles["Heading2"]))
        else:
            story.append(Paragraph(text, styles["BodyText"]))

    story.append(Spacer(1, 18))
    story.append(Paragraph("References", styles["Heading2"]))
    if references:
        for ref in references:
            if isinstance(ref, dict):
                ref_text = ref.get("citation") or ref.get("url") or str(ref)
            else:
                ref_text = str(ref)
            story.append(Paragraph(ref_text, styles["BodyText"]))
            story.append(Spacer(1, 6))
    else:
        story.append(Paragraph("No references collected.", styles["BodyText"]))

    doc.build(story)
    return buffer.getvalue()
