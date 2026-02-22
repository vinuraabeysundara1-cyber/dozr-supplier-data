#!/usr/bin/env python3
"""Generate DOZR Google Ads Analysis PDF Report"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime

def create_report():
    doc = SimpleDocTemplate(
        "/Users/vinuraabeysundara/DOZR_Google_Ads_Report.pdf",
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.gray,
        spaceAfter=12
    )

    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=12,
        spaceBefore=12,
        spaceAfter=6,
        textColor=colors.HexColor('#1a73e8')
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=9,
        spaceAfter=4
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontSize=9,
        leftIndent=15,
        spaceAfter=3
    )

    story = []

    # Title
    story.append(Paragraph("DOZR Google Ads Optimization Report", title_style))
    story.append(Paragraph(f"Customer ID: 8531896842 | Generated: {datetime.now().strftime('%B %d, %Y')}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1a73e8')))
    story.append(Spacer(1, 10))

    # Executive Summary
    story.append(Paragraph("Executive Summary", heading_style))
    story.append(Paragraph(
        "Analysis of 15 active campaigns over 30/90-day windows reveals conversion tracking inefficiencies "
        "and unrealistic tROAS targets impacting Smart Bidding performance. Key finding: Phone Call conversions "
        "report $0 value while representing 90% of customer touchpoints, breaking value-based bidding optimization.",
        body_style
    ))

    # Key Metrics Table
    story.append(Paragraph("Account Performance Snapshot (30 Days)", heading_style))

    metrics_data = [
        ['Metric', 'tROAS Campaigns', 'Other Campaigns', 'Total'],
        ['Spend', '$21,847 (70%)', '$9,373 (30%)', '$31,220'],
        ['Closed Won Deals', '19 (76%)', '6 (24%)', '25'],
        ['Revenue', '$62,100', '$19,650', '$81,750'],
        ['True ROAS', '2.84x', '2.10x', '2.62x'],
        ['Phone Calls', '220', '45', '265'],
        ['Quote Requests', '67', '21', '88'],
    ]

    metrics_table = Table(metrics_data, colWidths=[1.8*inch, 1.5*inch, 1.5*inch, 1.2*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 8))

    # tROAS Campaign Analysis
    story.append(Paragraph("tROAS Campaign Performance", heading_style))

    troas_data = [
        ['Campaign', 'Target', 'Actual (30d)', 'Status'],
        ['Search-Demand-Forklift', '5.00x', '5.39x', 'HITTING'],
        ['Search-DSA-US', '4.80x', '5.12x', 'HITTING'],
        ['Search-Demand-Boom-Lifts', '5.70x', '4.69x', 'BELOW TARGET'],
    ]

    troas_table = Table(troas_data, colWidths=[2.2*inch, 1*inch, 1.2*inch, 1.2*inch])
    troas_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34a853')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('BACKGROUND', (3, 3), (3, 3), colors.HexColor('#fce8e6')),
        ('TEXTCOLOR', (3, 3), (3, 3), colors.HexColor('#c5221f')),
    ]))
    story.append(troas_table)
    story.append(Spacer(1, 8))

    # Critical Issues
    story.append(Paragraph("Critical Issues Identified", heading_style))

    issues = [
        "<b>1. Phone Call Conversion at $0 Value:</b> 90% of customer journey starts with phone calls, but Smart Bidding sees $0 value. This breaks tROAS optimization.",
        "<b>2. Boom Lifts tROAS Target Too High:</b> 5.70x target vs 4.69x actual = 21% gap causing impression throttling.",
        "<b>3. Duplicate Call Tracking:</b> Both 'Phone Call' (CRM upload) and 'Calls from Ads' (native) are PRIMARY, causing attribution conflicts.",
        "<b>4. Counting Type:</b> MANY_PER_CLICK may inflate conversion counts for B2B lead gen.",
    ]

    for issue in issues:
        story.append(Paragraph(issue, bullet_style))

    # Funnel Analysis
    story.append(Paragraph("Conversion Funnel Analysis (30 Days)", heading_style))

    funnel_data = [
        ['Stage', 'Count', 'Close Rate to CW', 'Proxy Value'],
        ['Phone Call', '265', '7.19%', '$235'],
        ['Qualified Call', '89', '21.35%', '$699'],
        ['Quote Requested', '88', '28.39%', '$930'],
        ['Closed Won', '25', '100%', '$3,275 (actual)'],
    ]

    funnel_table = Table(funnel_data, colWidths=[1.5*inch, 1*inch, 1.3*inch, 1.2*inch])
    funnel_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fbbc04')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    story.append(funnel_table)
    story.append(Spacer(1, 4))
    story.append(Paragraph("<i>Proxy Value Formula: Close Rate x Avg Deal Value ($3,275)</i>",
                           ParagraphStyle('Note', fontSize=7, textColor=colors.gray)))

    # Recommendations
    story.append(Paragraph("Recommendations", heading_style))

    rec_data = [
        ['Priority', 'Action', 'Impact'],
        ['P1', 'Assign $235 proxy value to Phone Call conversion', 'Enables Smart Bidding to optimize for call value'],
        ['P1', 'Lower Boom Lifts tROAS from 5.70x to 4.50x', 'Increases impression share, reduces throttling'],
        ['P2', 'Move "Calls from Ads" to SECONDARY', 'Eliminates duplicate attribution'],
        ['P2', 'Change counting type to ONE_PER_CLICK', 'Accurate B2B lead counting'],
        ['P3', 'Test weekend ads on Dozers (15.02x) & Excavator (5.43x)', 'Capture competitor gap on weekends'],
    ]

    rec_table = Table(rec_data, colWidths=[0.6*inch, 4*inch, 2*inch])
    rec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ea4335')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(rec_table)
    story.append(Spacer(1, 8))

    # Competitor Insight
    story.append(Paragraph("Competitor Weekend Analysis (90 Days)", heading_style))
    story.append(Paragraph(
        "Auction Insights data shows competitors (Big Rents, United Rentals, EquipmentShare) maintain aggressive "
        "weekend presence. DOZR's rank-lost impression share nearly doubles on weekends (competitors gain), "
        "while DOZR impressions drop 98.6%. Top-performing campaigns (Dozers, Excavator) are candidates for "
        "weekend expansion testing.",
        body_style
    ))

    # Verification
    story.append(Paragraph("Standards Verification", heading_style))

    verify_data = [
        ['Recommendation', 'Aligned with Google Docs?'],
        ['Proxy value = close rate x deal value', 'Yes - Google Conversion Value Calculator'],
        ['$0 value breaks tROAS eligibility', 'Yes - Requires non-zero values'],
        ['ONE_PER_CLICK for B2B leads', 'Yes - Industry standard'],
        ['Phone calls with proxy values', 'Yes - Google endorses lead-type values'],
    ]

    verify_table = Table(verify_data, colWidths=[3.5*inch, 2.5*inch])
    verify_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#673ab7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    story.append(verify_table)

    # Footer
    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.gray))
    story.append(Paragraph(
        "Report generated via Google Ads API v23 analysis | Data sources: Google Ads, DOZR MongoDB DW",
        ParagraphStyle('Footer', fontSize=7, textColor=colors.gray, alignment=TA_CENTER)
    ))

    doc.build(story)
    print("PDF generated: /Users/vinuraabeysundara/DOZR_Google_Ads_Report.pdf")

if __name__ == "__main__":
    create_report()
