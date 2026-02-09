from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
from typing import Dict, List
import os


class PDFService:
    """Service for generating PDF invoices"""
    
    def __init__(self, output_dir: str = "./uploads/invoices"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_invoice_pdf(self, invoice_data: Dict, work_order_data: Dict, 
                           shop_data: Dict, customer_data: Dict, 
                           line_items: List[Dict]) -> str:
        """
        Generate PDF invoice
        Returns the file path of generated PDF
        """
        filename = f"invoice_{invoice_data['invoice_number']}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
        )
        title = Paragraph(f"ФАКТУРА / INVOICE", title_style)
        story.append(title)
        story.append(Spacer(1, 0.5 * cm))
        
        # Shop info
        shop_info = [
            [Paragraph(f"<b>{shop_data['name']}</b>", styles['Normal'])],
            [shop_data.get('address', '')],
            [f"Тел: {shop_data.get('phone', '')}"],
            [f"Email: {shop_data.get('email', '')}"],
        ]
        shop_table = Table(shop_info, colWidths=[8 * cm])
        shop_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(shop_table)
        story.append(Spacer(1, 0.5 * cm))
        
        # Invoice details
        invoice_details = [
            ["Номер на фактура / Invoice Number:", invoice_data['invoice_number']],
            ["Дата / Date:", datetime.fromisoformat(str(invoice_data['created_at'])).strftime("%d.%m.%Y")],
            ["Клиент / Customer:", f"{customer_data['first_name']} {customer_data['last_name']}"],
            ["Телефон / Phone:", customer_data.get('phone', '')],
        ]
        
        details_table = Table(invoice_details, colWidths=[7 * cm, 7 * cm])
        details_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(details_table)
        story.append(Spacer(1, 1 * cm))
        
        # Line items table
        data = [["Описание / Description", "Кол-во / Qty", "Цена / Price", "Сума / Total"]]
        
        for item in line_items:
            data.append([
                item['description'],
                str(item['quantity']),
                f"{item['unit_price']:.2f} лв.",
                f"{item['total_price']:.2f} лв."
            ])
        
        # Totals
        data.append(["", "", "Междинна сума / Subtotal:", f"{invoice_data['subtotal']:.2f} лв."])
        if invoice_data.get('tax_amount', 0) > 0:
            data.append(["", "", f"ДДС / VAT ({invoice_data.get('tax_rate', 0)*100}%):", 
                        f"{invoice_data['tax_amount']:.2f} лв."])
        data.append(["", "", "ОБЩА СУМА / TOTAL:", f"{invoice_data['total']:.2f} лв."])
        
        items_table = Table(data, colWidths=[8 * cm, 2 * cm, 3 * cm, 3 * cm])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -4), colors.beige),
            ('GRID', (0, 0), (-1, -4), 1, colors.black),
            ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 14),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 1 * cm))
        
        # Notes
        if invoice_data.get('notes'):
            notes = Paragraph(f"<b>Бележки / Notes:</b><br/>{invoice_data['notes']}", styles['Normal'])
            story.append(notes)
            story.append(Spacer(1, 0.5 * cm))
        
        # Payment status
        if invoice_data['status'] == 'paid':
            paid_date = datetime.fromisoformat(str(invoice_data.get('paid_at', datetime.now()))).strftime("%d.%m.%Y")
            payment_info = Paragraph(
                f"<b>ПЛАТЕНО / PAID</b><br/>Дата: {paid_date}<br/>Метод: {invoice_data.get('payment_method', 'N/A')}",
                styles['Normal']
            )
            story.append(payment_info)
        
        # Footer
        story.append(Spacer(1, 1 * cm))
        footer = Paragraph(
            f"<i>Благодарим Ви! / Thank you!</i><br/>{shop_data.get('website', '')}",
            styles['Normal']
        )
        story.append(footer)
        
        # Build PDF
        doc.build(story)
        
        return filepath


def get_pdf_service() -> PDFService:
    """Dependency to get PDF service instance"""
    return PDFService()
