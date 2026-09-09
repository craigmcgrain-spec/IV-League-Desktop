import math
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph

NAVY = colors.HexColor("#12283F")
TEAL = colors.HexColor("#008A8C")
CREAM = colors.HexColor("#F7F4ED")
PALE_TEAL = colors.HexColor("#E6F5F3")
BORDER = colors.HexColor("#D6DEE2")
TEXT = colors.HexColor("#1B2B38")
MUTED = colors.HexColor("#647480")
LIGHT_PURPLE = colors.HexColor("#C8C0D4")
INFO_BAR_BG = colors.HexColor("#E8ECF4")

WIDTH, HEIGHT = letter


def _draw_lightning_watermark(c, cx, cy, size):
    c.saveState()
    c.setFillColor(LIGHT_PURPLE)
    c.setStrokeColor(LIGHT_PURPLE)
    c.setLineWidth(1.5)

    r = size * 0.55
    c.circle(cx, cy, r, stroke=1, fill=0)

    s = size * 0.4
    path = c.beginPath()
    path.moveTo(cx - s * 0.15, cy + s * 0.70)
    path.lineTo(cx - s * 0.45, cy + s * 0.10)
    path.lineTo(cx - s * 0.10, cy + s * 0.10)
    path.lineTo(cx - s * 0.20, cy - s * 0.70)
    path.lineTo(cx + s * 0.45, cy - s * 0.10)
    path.lineTo(cx + s * 0.10, cy - s * 0.10)
    path.lineTo(cx + s * 0.20, cy + s * 0.70)
    path.close()
    c.drawPath(path, stroke=1, fill=1)

    c.restoreState()


def _draw_text(c, x, y, text, font="Helvetica", size=11, color=TEXT):
    c.setFont(font, size)
    c.setFillColor(color)
    c.drawString(x, y, text)


def _draw_right_text(c, x, y, text, font="Helvetica", size=11, color=TEXT):
    c.setFont(font, size)
    c.setFillColor(color)
    c.drawRightString(x, y, text)


def generate_invoice_pdf(filepath, facility_name, start_date, end_date, items,
                         facility_details=None, company_info=None, items_dated=None):
    c = canvas.Canvas(filepath, pagesize=letter)

    margin = 50
    top = HEIGHT - 50

    _draw_text(c, margin, top, "I N V O I C E", "Helvetica-Bold", 20, NAVY)
    c.setStrokeColor(BORDER)
    c.setLineWidth(1)
    c.line(margin + 180, top + 5, WIDTH - margin, top + 5)

    _draw_lightning_watermark(c, WIDTH * 0.50, HEIGHT * 0.55, size=100)

    y_left = top - 40
    company_name = company_info.get("name", "The IV League II") if company_info else "The IV League II"
    _draw_text(c, margin, y_left, company_name, "Helvetica-Bold", 22, NAVY)

    y_addr = y_left - 22
    if company_info:
        if company_info.get("street"):
            _draw_text(c, margin, y_addr, company_info["street"], "Helvetica", 10, MUTED)
            y_addr -= 15
        city_parts = []
        if company_info.get("city"):
            city_parts.append(company_info["city"])
        if company_info.get("zip"):
            city_parts.append(company_info["zip"])
        if city_parts:
            _draw_text(c, margin, y_addr, ", ".join(city_parts), "Helvetica", 10, MUTED)
            y_addr -= 15
        if company_info.get("phone"):
            _draw_text(c, margin, y_addr, company_info["phone"], "Helvetica", 10, MUTED)
            y_addr -= 15
        if company_info.get("contact_name"):
            contact = company_info["contact_name"]
            if company_info.get("contact_email"):
                contact += f" — {company_info['contact_email']}"
            _draw_text(c, margin, y_addr, contact, "Helvetica", 10, MUTED)
        elif company_info.get("contact_email"):
            _draw_text(c, margin, y_addr, company_info["contact_email"], "Helvetica", 10, MUTED)

    y_right = top - 40
    _draw_right_text(c, WIDTH - margin, y_right + 18, "BILL TO:", "Helvetica-Bold", 9, MUTED)
    _draw_right_text(c, WIDTH - margin, y_right, facility_name, "Helvetica-Bold", 14, NAVY)

    y_bill = y_right - 20

    if facility_details:
        y_fac_addr = y_bill
        if facility_details.get("street"):
            _draw_right_text(c, WIDTH - margin, y_fac_addr, facility_details["street"], "Helvetica", 10, MUTED)
            y_fac_addr -= 15
        fac_city_parts = []
        if facility_details.get("city"):
            fac_city_parts.append(facility_details["city"])
        if facility_details.get("zip"):
            fac_city_parts.append(facility_details["zip"])
        if fac_city_parts:
            _draw_right_text(c, WIDTH - margin, y_fac_addr, ", ".join(fac_city_parts), "Helvetica", 10, MUTED)
            y_fac_addr -= 15
        if facility_details.get("phone"):
            _draw_right_text(c, WIDTH - margin, y_fac_addr, facility_details["phone"], "Helvetica", 10, MUTED)
            y_fac_addr -= 15
        if facility_details.get("contact_name"):
            contact = facility_details["contact_name"]
            if facility_details.get("contact_email"):
                contact += f" — {facility_details['contact_email']}"
            _draw_right_text(c, WIDTH - margin, y_fac_addr, contact, "Helvetica", 10, MUTED)
        elif facility_details.get("contact_email"):
            _draw_right_text(c, WIDTH - margin, y_fac_addr, facility_details["contact_email"], "Helvetica", 10, MUTED)

    info_y = top - 130
    info_h = 50
    c.setFillColor(INFO_BAR_BG)
    c.rect(margin, info_y - info_h, WIDTH - 2 * margin, info_h, stroke=0, fill=1)

    col1 = margin + 15
    col2 = margin + 250
    col3 = WIDTH - margin - 15

    info_text_y = info_y - 18
    info_val_y = info_y - 38

    _draw_text(c, col1, info_text_y, "INVOICE NO #", "Helvetica-Bold", 8, MUTED)
    _draw_text(c, col1, info_val_y, "0001", "Helvetica-Bold", 14, NAVY)

    _draw_text(c, col2, info_text_y, "DATE", "Helvetica-Bold", 8, MUTED)
    _draw_text(c, col2, info_val_y, start_date, "Helvetica-Bold", 12, NAVY)

    grand_total = sum(item["qty"] * item["price"] for item in items)
    total_qty = sum(item["qty"] for item in items)
    _draw_right_text(c, col3, info_text_y, "AMOUNT DUE", "Helvetica-Bold", 8, MUTED)
    _draw_right_text(c, col3, info_val_y, f"${grand_total:.2f}", "Helvetica-Bold", 14, NAVY)

    table_y = info_y - info_h - 30
    _draw_text(c, margin, table_y, "DESCRIPTION", "Helvetica-Bold", 9, MUTED)
    _draw_right_text(c, WIDTH - margin - 220, table_y, "QTY", "Helvetica-Bold", 9, MUTED)
    _draw_right_text(c, WIDTH - margin - 150, table_y, "PRICE", "Helvetica-Bold", 9, MUTED)
    _draw_right_text(c, WIDTH - margin - 60, table_y, "AMOUNT", "Helvetica-Bold", 9, MUTED)

    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    table_y -= 12
    c.line(margin, table_y, WIDTH - margin, table_y)

    row_y = table_y - 20
    for i, item in enumerate(items):
        subtotal = item["qty"] * item["price"]
        _draw_text(c, margin, row_y, item["task_name"], "Helvetica", 10, TEXT)
        _draw_right_text(c, WIDTH - margin - 220, row_y, str(item["qty"]), "Helvetica", 10, TEXT)
        _draw_right_text(c, WIDTH - margin - 150, row_y, f"${item['price']:.2f}", "Helvetica", 10, TEXT)
        _draw_right_text(c, WIDTH - margin - 60, row_y, f"${subtotal:.2f}", "Helvetica", 10, TEXT)
        row_y -= 20

    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    c.line(margin, row_y + 5, WIDTH - margin, row_y + 5)

    notes_y = row_y - 15
    _draw_text(c, margin, notes_y, "NOTES:", "Helvetica-Bold", 9, TEXT)
    _draw_text(c, margin, notes_y - 15, "IV therapy services rendered.", "Helvetica", 9, MUTED)

    summary_right = WIDTH - margin
    sy = row_y

    _draw_right_text(c, summary_right, sy, "SUB-TOTAL", "Helvetica-Bold", 9, TEXT)
    _draw_right_text(c, summary_right, sy - 15, f"${grand_total:.2f}", "Helvetica", 10, TEXT)

    sy -= 40
    _draw_right_text(c, summary_right, sy, "TOTAL", "Helvetica-Bold", 11, NAVY)
    _draw_right_text(c, summary_right, sy - 18, f"${grand_total:.2f}", "Helvetica-Bold", 14, NAVY)

    c.setStrokeColor(NAVY)
    c.setLineWidth(1)
    c.line(summary_right - 120, sy - 22, summary_right, sy - 22)

    footer_y = 40
    _draw_text(c, margin, footer_y, "This invoice was generated by IV League Desktop.", "Helvetica", 7, MUTED)
    _draw_right_text(c, WIDTH - margin, footer_y, "Powered by IV League", "Helvetica", 7, MUTED)

    c.showPage()

    if items_dated:
        _draw_itemized_page(c, facility_name, start_date, end_date, items_dated,
                            company_info, facility_details)

    c.save()


def _draw_itemized_page(c, facility_name, start_date, end_date, items_dated,
                        company_info, facility_details):
    margin = 50
    top = HEIGHT - 50

    company_name = company_info.get("name", "The IV League II") if company_info else "The IV League II"
    _draw_text(c, margin, top, company_name, "Helvetica-Bold", 14, NAVY)

    _draw_text(c, margin, top - 20, f"Itemized Procedures — {facility_name}", "Helvetica-Bold", 12, NAVY)
    _draw_text(c, margin, top - 35, f"{start_date} to {end_date}", "Helvetica", 10, MUTED)

    table_y = top - 60
    _draw_text(c, margin, table_y, "DATE", "Helvetica-Bold", 8, MUTED)
    _draw_text(c, margin + 80, table_y, "TIME", "Helvetica-Bold", 8, MUTED)
    _draw_text(c, margin + 140, table_y, "CLIENT", "Helvetica-Bold", 8, MUTED)
    _draw_text(c, margin + 300, table_y, "PROCEDURE", "Helvetica-Bold", 8, MUTED)
    _draw_right_text(c, WIDTH - margin, table_y, "PRICE", "Helvetica-Bold", 8, MUTED)

    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    table_y -= 12
    c.line(margin, table_y, WIDTH - margin, table_y)

    row_y = table_y - 15
    for item in items_dated:
        if row_y < 80:
            c.showPage()
            top = HEIGHT - 50
            row_y = top - 30

        _draw_text(c, margin, row_y, item["date"], "Helvetica", 9, TEXT)
        _draw_text(c, margin + 80, row_y, item["time"], "Helvetica", 9, TEXT)
        _draw_text(c, margin + 140, row_y, item["client_name"], "Helvetica", 9, TEXT)
        _draw_text(c, margin + 300, row_y, item["task_name"], "Helvetica", 9, TEXT)
        _draw_right_text(c, WIDTH - margin, row_y, f"${item['price']:.2f}", "Helvetica", 9, TEXT)
        row_y -= 15

    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    c.line(margin, row_y + 5, WIDTH - margin, row_y + 5)

    grand_total = sum(item["price"] for item in items_dated)
    _draw_right_text(c, WIDTH - margin, row_y - 10, "TOTAL", "Helvetica-Bold", 10, NAVY)
    _draw_right_text(c, WIDTH - margin, row_y - 25, f"${grand_total:.2f}", "Helvetica-Bold", 12, NAVY)
