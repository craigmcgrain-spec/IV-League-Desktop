from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def generate_invoice_pdf(filepath, facility_name, start_date, end_date, items):
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("IV League", styles["Title"]))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(f"<b>Facility:</b> {facility_name}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Period:</b> {start_date} to {end_date}", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    data = [["Task", "Quantity"]]
    total = 0
    for item in items:
        data.append([item["task_name"], str(item["qty"])])
        total += item["qty"]

    data.append(["", ""])
    data.append(["TOTAL", str(total)])

    table = Table(data, colWidths=[4 * inch, 1.5 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#ecf0f1")),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
        ("FONTSIZE", (0, 1), (-1, -1), 11),
        ("TOPPADDING", (0, 1), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#bdc3c7")),
    ]))

    elements.append(table)
    doc.build(elements)
