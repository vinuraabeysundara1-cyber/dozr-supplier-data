#!/usr/bin/env python3
"""Generate DOZR tROAS & Funnel Optimization PDF Report"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER
from datetime import datetime

def create_report():
    doc = SimpleDocTemplate(
        "/Users/vinuraabeysundara/DOZR_tROAS_Report.pdf",
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=16, alignment=TA_CENTER, spaceAfter=4)
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=9, alignment=TA_CENTER, textColor=colors.gray, spaceAfter=10)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=11, spaceBefore=14, spaceAfter=6, textColor=colors.HexColor('#1a73e8'))
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=9, spaceAfter=6)
    cell_style = ParagraphStyle('Cell', parent=styles['Normal'], fontSize=8, leading=10)
    cell_center = ParagraphStyle('CellCenter', parent=styles['Normal'], fontSize=8, leading=10, alignment=TA_CENTER)

    story = []

    # Title
    story.append(Paragraph("DOZR tROAS & Funnel Optimization", title_style))
    story.append(Paragraph(f"30-Day Analysis | {datetime.now().strftime('%B %d, %Y')}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1a73e8')))

    # Section 1: tROAS Campaign Performance
    story.append(Paragraph("1. tROAS Campaign Performance (30 Days)", heading_style))

    troas_data = [
        ['Campaign', 'Target ROAS', 'Actual ROAS', 'Spend', 'Status'],
        ['Search-Demand-Forklift', '5.00x', '5.39x', '$8,200', 'HITTING'],
        ['Search-DSA-US', '4.80x', '5.12x', '$6,100', 'HITTING'],
        ['Search-Demand-Boom-Lifts', '5.70x', '4.69x', '$7,547', 'BELOW'],
    ]

    troas_table = Table(troas_data, colWidths=[2.2*inch, 1*inch, 1*inch, 0.9*inch, 0.9*inch])
    troas_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('BACKGROUND', (4, 1), (4, 1), colors.HexColor('#e6f4ea')),
        ('BACKGROUND', (4, 2), (4, 2), colors.HexColor('#e6f4ea')),
        ('BACKGROUND', (4, 3), (4, 3), colors.HexColor('#fce8e6')),
        ('TEXTCOLOR', (4, 3), (4, 3), colors.HexColor('#c5221f')),
    ]))
    story.append(troas_table)
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Finding:</b> 2 of 3 tROAS campaigns hitting targets. Boom Lifts target (5.70x) is 21% above actual performance, causing impression throttling.", body_style))

    # Section 2: Funnel Optimization
    story.append(Paragraph("2. Conversion Funnel Analysis", heading_style))

    funnel_data = [
        ['Funnel Stage', 'Count', 'Close Rate', 'Recommended Proxy Value'],
        ['Phone Call', '265', '7.19%', '$235'],
        ['Qualified Call', '89', '21.35%', '$699'],
        ['Quote Requested', '88', '28.39%', '$930'],
        ['Closed Won', '25', '-', '$3,275 (actual avg)'],
    ]

    funnel_table = Table(funnel_data, colWidths=[1.6*inch, 0.8*inch, 1*inch, 1.8*inch])
    funnel_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fbbc04')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    story.append(funnel_table)
    story.append(Spacer(1, 4))
    story.append(Paragraph("<i>Proxy Value = Close Rate x Average Deal Value ($3,275)</i>", 
                           ParagraphStyle('Note', fontSize=8, textColor=colors.gray)))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Issue:</b> Phone Call (PRIMARY conversion) reports $0 value to Smart Bidding. With 90% of customers calling first, tROAS optimization is broken - the algorithm cannot optimize for value when most conversions show $0.", body_style))

    # Section 3: Recommendations - Using Paragraphs for text wrapping
    story.append(Paragraph("3. Verified Recommendations", heading_style))

    rec_data = [
        [
            Paragraph('<b>#</b>', cell_center),
            Paragraph('<b>Recommendation</b>', cell_style),
            Paragraph('<b>Rationale</b>', cell_style),
            Paragraph('<b>Verified</b>', cell_center)
        ],
        [
            Paragraph('1', cell_center),
            Paragraph('Assign $235 proxy value to Phone Call', cell_style),
            Paragraph('Enables Smart Bidding to optimize for call value using close rate formula', cell_style),
            Paragraph('Yes', cell_center)
        ],
        [
            Paragraph('2', cell_center),
            Paragraph('Lower Boom Lifts tROAS: 5.70x to 4.50x', cell_style),
            Paragraph('Target exceeds actual by 21%, causing Google to throttle impressions', cell_style),
            Paragraph('Yes', cell_center)
        ],
        [
            Paragraph('3', cell_center),
            Paragraph('Move "Calls from Ads" to SECONDARY', cell_style),
            Paragraph('Eliminates duplicate call tracking (CRM upload vs native Google)', cell_style),
            Paragraph('Yes', cell_center)
        ],
    ]

    rec_table = Table(rec_data, colWidths=[0.4*inch, 2.0*inch, 3.2*inch, 0.7*inch])
    rec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34a853')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(rec_table)
    story.append(Spacer(1, 10))

    # Verification note
    story.append(Paragraph("<b>Standards Verification:</b> All recommendations align with Google Ads documentation - proxy values use Google's Conversion Value Calculator formula, tROAS targets should reflect achievable performance, and duplicate tracking should be consolidated.", body_style))

    # Footer
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.gray))
    story.append(Paragraph("Data: Google Ads API v23 + DOZR MongoDB | Customer ID: 8531896842",
                           ParagraphStyle('Footer', fontSize=7, textColor=colors.gray, alignment=TA_CENTER)))

    doc.build(story)
    print("PDF generated: /Users/vinuraabeysundara/DOZR_tROAS_Report.pdf")

if __name__ == "__main__":
    create_report()
