from io import BytesIO
from typing import List
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

from models.audit_log import AuditLog


def export_logs_pdf(logs: List[AuditLog], file_path: str) -> None:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=LETTER)
    width, height = LETTER

    y = height - 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Audit Logs Report")
    y -= 30

    c.setFont("Helvetica", 10)
    for log in logs:
        line = (
            f"ID: {log.id} | User: {log.user_id} | Action: {log.action} | "
            f"IP: {log.ip_address or 'N/A'} | Time: {log.timestamp or ''} | "
            f"Metadata: {log.details or ''}"
        )
        c.drawString(40, y, line)
        y -= 20
        if y < 40:
            c.showPage()
            y = height - 40
            c.setFont("Helvetica", 10)

    c.save()
    pdf_data = buffer.getvalue()
    buffer.close()

    with open(file_path, "wb") as f:
        f.write(pdf_data)
