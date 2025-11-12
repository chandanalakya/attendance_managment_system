from io import BytesIO
from typing import List
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

# ✅ Correct import path (fixed)
from src.models.audit_log import AuditLog


def export_logs_pdf(logs: List[AuditLog], file_path: str) -> None:
    """
    Exports a list of AuditLog entries (or similar dict objects) into a
    simple paginated PDF report using ReportLab.

    Each log entry includes: ID, User ID, Action, IP, Timestamp, and Metadata.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=LETTER)
    width, height = LETTER

    # Header
    y = height - 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Audit Logs Report")
    y -= 30

    # Content
    c.setFont("Helvetica", 10)
    for log in logs:
        # Support both ORM objects and dicts
        if isinstance(log, dict):
            log_id = log.get("id", "")
            user_id = log.get("user_id", "")
            action = log.get("action", "")
            ip = log.get("ip_address", "N/A")
            timestamp = log.get("timestamp", "")
            metadata = log.get("metadata", "")
        else:
            log_id = getattr(log, "id", "")
            user_id = getattr(log, "user_id", "")
            action = getattr(log, "action", "")
            ip = getattr(log, "ip_address", "N/A")
            timestamp = getattr(log, "timestamp", "")
            metadata = getattr(log, "details", getattr(log, "metadata", ""))

        line = (
            f"ID: {log_id} | User: {user_id} | Action: {action} | "
            f"IP: {ip} | Time: {timestamp} | Metadata: {metadata}"
        )
        c.drawString(40, y, line)
        y -= 20

        # Add page break if needed
        if y < 40:
            c.showPage()
            y = height - 40
            c.setFont("Helvetica", 10)

    # Save PDF
    c.save()
    pdf_data = buffer.getvalue()
    buffer.close()

    with open(file_path, "wb") as f:
        f.write(pdf_data)
