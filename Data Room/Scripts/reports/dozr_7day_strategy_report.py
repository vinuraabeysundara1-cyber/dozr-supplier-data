#!/usr/bin/env python3
"""Generate DOZR 7-Day Geo Strategy Report with Equipment Analysis"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import json

def create_report():
    doc = SimpleDocTemplate(
        "/Users/vinuraabeysundara/DOZR_7Day_Geo_Strategy_Report.pdf",
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=16, alignment=TA_CENTER, spaceAfter=6)
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=9, alignment=TA_CENTER, textColor=colors.gray, spaceAfter=12)
    h1_style = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=13, spaceBefore=14, spaceAfter=8, textColor=colors.HexColor('#1a73e8'))
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=10, spaceBefore=10, spaceAfter=6, textColor=colors.HexColor('#333333'))
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=9, spaceAfter=6, leading=12)
    cell_style = ParagraphStyle('Cell', parent=styles['Normal'], fontSize=8, leading=10)
    small_style = ParagraphStyle('Small', parent=styles['Normal'], fontSize=7, textColor=colors.gray)
    
    story = []

    # Title
    story.append(Paragraph("DOZR Geo & Equipment Strategy Report", title_style))
    story.append(Paragraph(f"7-Day Ads Performance | 14-Day Order Fulfillment | {datetime.now().strftime('%B %d, %Y')}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a73e8')))
    story.append(Spacer(1, 15))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", h1_style))
    
    summary_data = [
        [Paragraph('<b>Metric</b>', cell_style), Paragraph('<b>7-Day Ads</b>', cell_style), Paragraph('<b>14-Day Orders</b>', cell_style)],
        ['Total Spend', '$19,310', '-'],
        ['Conversions', '273', '118 Closed Won'],
        ['ROAS', '3.52x avg', '74.7% win rate'],
        ['Top Equipment', 'Boom Lifts ($7,188)', 'Forklifts (41 orders)'],
        ['Top States', 'N/A (by campaign)', 'TX (24), CA (17), ON (11)'],
    ]
    
    sum_table = Table(summary_data, colWidths=[1.8*inch, 2*inch, 2.5*inch])
    sum_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    story.append(sum_table)
    story.append(Spacer(1, 15))

    # Section 1: Ads Performance by Equipment
    story.append(Paragraph("1. Google Ads Performance by Equipment Type (7 Days)", h1_style))
    
    ads_data = [
        [Paragraph('<b>Equipment</b>', cell_style), Paragraph('<b>Spend</b>', cell_style), 
         Paragraph('<b>Conv</b>', cell_style), Paragraph('<b>Value</b>', cell_style),
         Paragraph('<b>ROAS</b>', cell_style), Paragraph('<b>Status</b>', cell_style)],
        ['Boom Lifts', '$7,188', '75', '$13,339', '1.86x', 'Top spend'],
        ['Excavators', '$2,564', '16', '$1,524', '0.59x', 'Underperforming'],
        ['Scissor Lifts', '$2,259', '44', '$5,076', '2.25x', 'Healthy'],
        ['Forklifts', '$1,908', '39', '$3,722', '1.95x', 'Healthy'],
        ['DSA (All)', '$1,751', '25', '$20,525', '11.72x', 'Best ROAS'],
        ['Telehandlers', '$1,078', '7', '$1,083', '1.00x', 'Break-even'],
        ['Dozers', '$1,021', '21', '$11,894', '11.65x', 'High ROAS'],
        ['Loaders', '$1,018', '31', '$4,839', '4.76x', 'Strong'],
    ]
    
    ads_table = Table(ads_data, colWidths=[1.3*inch, 0.8*inch, 0.6*inch, 0.9*inch, 0.7*inch, 1.2*inch])
    ads_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34a853')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (1, 0), (-2, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('BACKGROUND', (5, 2), (5, 2), colors.HexColor('#fce8e6')),  # Excavators underperforming
    ]))
    story.append(ads_table)
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>Key Insight:</b> Dozers (11.65x) and DSA (11.72x) have highest ROAS but Excavators (0.59x) are underperforming - review targeting.", body_style))

    # Section 2: Order Fulfillment by Equipment
    story.append(Paragraph("2. Order Fulfillment by Equipment Type (14 Days)", h1_style))
    
    orders_data = [
        [Paragraph('<b>Equipment</b>', cell_style), Paragraph('<b>Orders</b>', cell_style),
         Paragraph('<b>% Total</b>', cell_style), Paragraph('<b>Top States</b>', cell_style)],
        ['Forklifts', '41', '34.7%', 'TX(9), CO(6), CA(5), ON(4)'],
        ['Scissor Lifts', '23', '19.5%', 'AZ(3), MT(2), SC(2), CO(2)'],
        ['Boom Lifts', '20', '16.9%', 'CA(6), FL(4), ON(3), TX(2)'],
        ['Excavators', '10', '8.5%', 'CA(3), FL(2), GA(1), TX(1)'],
        ['Loaders', '9', '7.6%', 'TX(3), NJ(1), NY(1), VA(1)'],
        ['Dozers', '2', '1.7%', 'TX(2)'],
        ['Unknown', '13', '11.0%', 'Various'],
    ]
    
    orders_table = Table(orders_data, colWidths=[1.2*inch, 0.8*inch, 0.8*inch, 3.5*inch])
    orders_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fbbc04')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (1, 0), (2, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    story.append(orders_table)
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>Key Insight:</b> Forklifts dominate orders (34.7%) but Boom Lifts get 37% of ad spend. Consider rebalancing.", body_style))

    story.append(PageBreak())
    
    # Section 3: Supply Gaps
    story.append(Paragraph("3. Equipment-Specific Supply Gaps", h1_style))
    story.append(Paragraph("States with orders but LIMITED or NO supplier coverage for specific equipment types:", body_style))
    
    gaps_data = [
        [Paragraph('<b>State</b>', cell_style), Paragraph('<b>Equipment</b>', cell_style),
         Paragraph('<b>Orders</b>', cell_style), Paragraph('<b>Suppliers</b>', cell_style), Paragraph('<b>Risk</b>', cell_style)],
        ['MS', 'Boom Lifts', '1', '0', 'HIGH'],
        ['MS', 'Forklifts', '1', '0', 'HIGH'],
        ['BC', 'Forklifts', '1', '0', 'HIGH'],
        ['BC', 'Boom Lifts', '1', '0', 'HIGH'],
        ['IA', 'Scissor Lifts', '1', '0', 'HIGH'],
        ['MT', 'Scissor Lifts', '2', '1', 'MEDIUM'],
    ]
    
    gaps_table = Table(gaps_data, colWidths=[0.8*inch, 1.3*inch, 0.8*inch, 0.9*inch, 0.8*inch])
    gaps_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ea4335')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('BACKGROUND', (4, 1), (4, 5), colors.HexColor('#fce8e6')),
    ]))
    story.append(gaps_table)
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>Action:</b> Monitor MS, BC, IA orders - may need to expand supplier network or adjust targeting.", body_style))

    # Section 4: Untapped Opportunities
    story.append(Paragraph("4. Untapped Supplier Coverage (Expansion Opportunities)", h1_style))
    story.append(Paragraph("States with strong supplier coverage but few/no orders - high potential for ad expansion:", body_style))
    
    untapped_data = [
        [Paragraph('<b>State</b>', cell_style), Paragraph('<b>Equipment</b>', cell_style),
         Paragraph('<b>Suppliers</b>', cell_style), Paragraph('<b>Orders</b>', cell_style), Paragraph('<b>Potential</b>', cell_style)],
        ['TX', 'Scissor Lifts', '42', '1', 'HIGH'],
        ['TX', 'Excavators', '41', '1', 'HIGH'],
        ['CA', 'Loaders', '28', '0', 'HIGH'],
        ['FL', 'Scissor Lifts', '26', '0', 'HIGH'],
        ['FL', 'Loaders', '23', '0', 'HIGH'],
        ['AZ', 'Boom Lifts', '13', '1', 'HIGH'],
        ['AZ', 'Forklifts', '13', '0', 'HIGH'],
        ['CO', 'Boom Lifts', '13', '0', 'HIGH'],
        ['GA', 'Boom Lifts', '12', '0', 'HIGH'],
        ['OH', 'All types', '10+', '0', 'HIGH'],
    ]
    
    untapped_table = Table(untapped_data, colWidths=[0.8*inch, 1.3*inch, 0.9*inch, 0.8*inch, 0.8*inch])
    untapped_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d652d')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#e6f4ea'), colors.white]),
    ]))
    story.append(untapped_table)
    
    story.append(PageBreak())
    
    # Section 5: Ads vs Orders Alignment
    story.append(Paragraph("5. Ads vs Orders Alignment Analysis", h1_style))
    
    alignment_data = [
        [Paragraph('<b>Equipment</b>', cell_style), Paragraph('<b>Ad Spend</b>', cell_style),
         Paragraph('<b>ROAS</b>', cell_style), Paragraph('<b>Orders</b>', cell_style), Paragraph('<b>Alignment</b>', cell_style)],
        ['Forklifts', '$1,908', '1.95x', '41 (35%)', 'ALIGNED - High demand, good spend'],
        ['Scissor Lifts', '$2,259', '2.25x', '23 (20%)', 'ALIGNED - Balanced'],
        ['Boom Lifts', '$7,188', '1.86x', '20 (17%)', 'REVIEW - 37% spend, 17% orders'],
        ['Excavators', '$2,564', '0.59x', '10 (8%)', 'OVERSPEND - Low ROAS, reduce'],
        ['Loaders', '$1,018', '4.76x', '9 (8%)', 'UNDERSPEND - Good ROAS, increase'],
        ['Dozers', '$1,021', '11.65x', '2 (2%)', 'WATCH - Amazing ROAS, low volume'],
        ['Telehandlers', '$1,078', '1.00x', '0 (0%)', 'OVERSPEND - No orders, review'],
    ]
    
    align_table = Table(alignment_data, colWidths=[1.1*inch, 0.8*inch, 0.7*inch, 0.9*inch, 2.8*inch])
    align_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#673ab7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (1, 0), (3, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('BACKGROUND', (4, 3), (4, 3), colors.HexColor('#e8f0fe')),  # Boom - review
        ('BACKGROUND', (4, 4), (4, 4), colors.HexColor('#fce8e6')),  # Excavators - overspend
        ('BACKGROUND', (4, 7), (4, 7), colors.HexColor('#fce8e6')),  # Telehandlers - overspend
    ]))
    story.append(align_table)
    story.append(Spacer(1, 15))

    # Section 6: Recommendations
    story.append(Paragraph("6. Recommendations", h1_style))
    
    rec_data = [
        [Paragraph('<b>#</b>', cell_style), Paragraph('<b>Action</b>', cell_style), 
         Paragraph('<b>Equipment</b>', cell_style), Paragraph('<b>Geos to Add</b>', cell_style), Paragraph('<b>Priority</b>', cell_style)],
        ['1', Paragraph('Reduce spend or improve targeting', cell_style), 'Excavators', 'Review current geos', 'HIGH'],
        ['2', Paragraph('Expand geo targeting', cell_style), 'Scissor Lifts', 'FL (Jacksonville, Orlando, Bradenton)', 'HIGH'],
        ['3', Paragraph('Expand geo targeting', cell_style), 'Forklifts', 'AZ, GA, OH cities', 'HIGH'],
        ['4', Paragraph('Launch test campaign', cell_style), 'All types', 'Ohio (Perry, Bedford Heights)', 'MEDIUM'],
        ['5', Paragraph('Review/pause if no improvement', cell_style), 'Telehandlers', 'Current targeting', 'MEDIUM'],
        ['6', Paragraph('Increase budget (high ROAS)', cell_style), 'Loaders', 'CA, FL expansion', 'MEDIUM'],
        ['7', Paragraph('Expand to match supplier coverage', cell_style), 'Boom Lifts', 'CO (Denver, Colorado Springs)', 'LOW'],
    ]
    
    rec_table = Table(rec_data, colWidths=[0.3*inch, 2*inch, 1*inch, 2*inch, 0.7*inch])
    rec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (4, 0), (4, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(rec_table)
    
    story.append(PageBreak())
    
    # Section 7: Industry Best Practices
    story.append(Paragraph("7. Industry Best Practices Validation", h1_style))
    
    bp_data = [
        [Paragraph('<b>Recommendation</b>', cell_style), Paragraph('<b>Best Practice</b>', cell_style), Paragraph('<b>Verified</b>', cell_style)],
        [Paragraph('Match ad geos to supplier coverage', cell_style), 
         Paragraph('Only advertise where you can fulfill orders to reduce wasted spend and improve customer experience', cell_style), 
         '✓'],
        [Paragraph('Equipment-specific campaigns', cell_style),
         Paragraph('Separate campaigns by equipment type allows budget control and bid optimization per category', cell_style),
         '✓'],
        [Paragraph('Reduce spend on underperforming segments', cell_style),
         Paragraph('Equipment types with <1.0x ROAS should be reviewed - fix targeting or reduce budget', cell_style),
         '✓'],
        [Paragraph('Test campaigns for new markets', cell_style),
         Paragraph('Isolate new geo tests to measure incrementality without affecting proven campaigns', cell_style),
         '✓'],
        [Paragraph('Align spend with demand patterns', cell_style),
         Paragraph('Ad budget allocation should roughly match order volume by equipment type', cell_style),
         '✓'],
        [Paragraph('DMA/City targeting for B2B', cell_style),
         Paragraph('Equipment rental is location-sensitive; city-level targeting preferred over state-level', cell_style),
         '✓'],
    ]
    
    bp_table = Table(bp_data, colWidths=[2*inch, 3.5*inch, 0.6*inch])
    bp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d652d')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#e6f4ea'), colors.white]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(bp_table)
    
    # Footer
    story.append(Spacer(1, 30))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.gray))
    story.append(Paragraph(
        "Data Sources: Google Ads API (7-day), DOZR MongoDB (14-day orders), Supplier Excel (243 locations, 155 suppliers, 8 equipment types)",
        ParagraphStyle('Footer', fontSize=7, textColor=colors.gray, alignment=TA_CENTER)
    ))

    doc.build(story)
    print("PDF generated: /Users/vinuraabeysundara/DOZR_7Day_Geo_Strategy_Report.pdf")

if __name__ == "__main__":
    create_report()
