import uuid
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Paragraph
from reportlab.platypus import Spacer
from reportlab.lib.styles import getSampleStyleSheet


def generate_pdf(text: str) -> str:
    """Generate PDF report and return file path."""

    file_path = f"{uuid.uuid4()}.pdf"

    document = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()

    content = []

    for line in text.split("\n"):
        content.append(Paragraph(line, styles["Normal"]))
        content.append(Spacer(1, 6))

    document.build(content)

    return file_path