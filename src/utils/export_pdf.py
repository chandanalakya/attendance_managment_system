from io import BytesIO
from typing import List, Dict, Any
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas


def to_pdf_bytes(title: str, logs: List[Dict[str, Any]]) -> bytes:
    """Convert logs to PDF bytes for download."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=LETTER)
    width, height = LETTER

    # Header
    y = height - 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, title)
    y -= 30

    # Content
    c.setFont("Helvetica", 10)
    for log in logs:
        log_id = log.get("id", "")
        user_id = log.get("user_id", "")
        action = log.get("action_type", "")
        ip = log.get("ip_address", "N/A")
        timestamp = log.get("created_at", "")
        details = log.get("details", "")

        line = f"ID: {log_id} | User: {user_id} | Action: {action} | IP: {ip} | Time: {timestamp}"
        c.drawString(40, y, line)
        y -= 20

        if y < 40:
            c.showPage()
            y = height - 40
            c.setFont("Helvetica", 10)

    c.save()
    return buffer.getvalue()


def export_logs_pdf(logs: List[Dict[str, Any]], file_path: str) -> None:
    """Export logs to PDF file."""
    pdf_bytes = to_pdf_bytes("Audit Logs Report", logs)
    with open(file_path, "wb") as f:
        f.write(pdf_bytes)
