
from fpdf import FPDF
from datetime import datetime

def to_pdf_bytes(title: str, rows):
    pdf = FPDF(orientation="L")
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, title, ln=1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 8, f"Generated: {datetime.utcnow().isoformat()}Z", ln=1)

    if rows:
        headers = list(rows[0].keys())
        col_width = (pdf.w - 20) / len(headers)
        pdf.set_font("Arial", "B", 9)
        for h in headers:
            pdf.cell(col_width, 8, str(h)[:20], border=1)
        pdf.ln(8)
        pdf.set_font("Arial", "", 9)
        for r in rows:
            for h in headers:
                txt = str(r.get(h, ""))[:40]
                pdf.cell(col_width, 8, txt, border=1)
            pdf.ln(8)
    else:
        pdf.cell(0, 10, "No data", ln=1)

    return bytes(pdf.output(dest="S").encode("latin1"))
