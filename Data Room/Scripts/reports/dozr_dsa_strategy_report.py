#!/usr/bin/env python3
"""
DOZR DSA Campaign Strategy Report - Equipment-Specific Keywords
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime

# Create PDF
pdf_path = "/Users/vinuraabeysundara/DOZR_DSA_Campaign_Strategy.pdf"
doc = SimpleDocTemplate(pdf_path, pagesize=letter, topMargin=0.6*inch, bottomMargin=0.6*inch, leftMargin=0.6*inch, rightMargin=0.6*inch)

# Styles
styles = getSampleStyleSheet()

title_style = ParagraphStyle('ReportTitle', parent=styles['Title'], fontSize=22, spaceAfter=6, textColor=colors.HexColor('#1a5276'), alignment=TA_CENTER)
subtitle_style = ParagraphStyle('ReportSubtitle', parent=styles['Normal'], fontSize=12, spaceAfter=15, textColor=colors.HexColor('#5d6d7e'), alignment=TA_CENTER)
section_style = ParagraphStyle('SectionHeader', parent=styles['Heading1'], fontSize=14, spaceBefore=15, spaceAfter=10, textColor=colors.HexColor('#1a5276'))
subsection_style = ParagraphStyle('SubsectionHeader', parent=styles['Heading2'], fontSize=11, spaceBefore=12, spaceAfter=6, textColor=colors.HexColor('#2874a6'))
body_style = ParagraphStyle('BodyText', parent=styles['Normal'], fontSize=9, spaceAfter=6, alignment=TA_JUSTIFY, leading=12)
highlight_style = ParagraphStyle('HighlightText', parent=styles['Normal'], fontSize=9, spaceAfter=6, textColor=colors.HexColor('#1a5276'), fontName='Helvetica-Bold')
small_style = ParagraphStyle('SmallText', parent=styles['Normal'], fontSize=8, spaceAfter=4, textColor=colors.HexColor('#5d6d7e'))

content = []

# Title Page
content.append(Spacer(1, 0.8*inch))
content.append(Paragraph("DOZR DSA Campaign", title_style))
content.append(Paragraph("Geo-Expansion Keyword Strategy", title_style))
content.append(Spacer(1, 0.2*inch))
content.append(Paragraph("Equipment-Specific Keywords for 15 New US States", subtitle_style))
content.append(Spacer(1, 0.3*inch))

meta_data = [
    ["Document Type:", "DSA Campaign Strategy & Keyword List"],
    ["Date:", datetime.now().strftime("%B %d, %Y")],
    ["Target Campaign:", "DSA-AllPages-Tier1-New-US-2"],
    ["Total New Keywords:", "240 keywords across 15 states"],
]
meta_table = Table(meta_data, colWidths=[1.8*inch, 4.5*inch])
meta_table.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
    ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
]))
content.append(meta_table)

content.append(PageBreak())

# Section 1: DOZR Equipment Categories
content.append(Paragraph("SECTION 1: DOZR EQUIPMENT CATEGORIES", section_style))

equip_intro = """
DOZR exclusively rents the following 8 categories of heavy equipment. All keywords in this strategy
are aligned with these categories to ensure we only drive traffic for equipment DOZR can fulfill.
"""
content.append(Paragraph(equip_intro, body_style))

equip_data = [
    ["#", "Equipment Category", "Common Search Terms", "Landing Page"],
    ["1", "Scissor Lifts", "scissor lift, aerial lift, slab scissor, electric scissor lift", "dozr.com/rent/scissor-lift"],
    ["2", "Boom Lifts", "boom lift, articulating boom, cherry picker, manlift", "dozr.com/rent/articulating-boom-lift"],
    ["3", "Forklifts", "forklift, lift truck, warehouse forklift, industrial forklift", "dozr.com/rent/forklift"],
    ["4", "Telehandlers", "telehandler, telescopic handler, reach forklift, lull", "dozr.com/rent/telehandler"],
    ["5", "Excavators", "excavator, mini excavator, digger, trackhoe", "dozr.com/rent/excavator"],
    ["6", "Backhoes", "backhoe, backhoe loader, tractor backhoe", "dozr.com/rent/backhoe"],
    ["7", "Dozers", "dozer, bulldozer, crawler dozer, track dozer", "dozr.com/rent/dozer"],
    ["8", "Skid Steers/Loaders", "skid steer, bobcat, compact loader, track loader", "dozr.com/rent/skid-steer"],
]

equip_table = Table(equip_data, colWidths=[0.3*inch, 1.3*inch, 2.8*inch, 2.3*inch])
equip_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5276')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('ALIGN', (0, 0), (0, -1), 'CENTER'),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
]))
content.append(equip_table)

content.append(Spacer(1, 0.15*inch))
content.append(Paragraph("<b>Note:</b> Keywords like 'generator rental', 'tool rental', or 'dump truck rental' should NOT be used as DOZR does not rent these items.", small_style))

content.append(PageBreak())

# Section 2: Keyword Strategy Overview
content.append(Paragraph("SECTION 2: KEYWORD STRATEGY OVERVIEW", section_style))

content.append(Paragraph("2.1 Keyword Formula", subsection_style))
formula_text = """
Each state will receive keywords following this formula to maximize coverage while staying relevant to DOZR's offerings:
"""
content.append(Paragraph(formula_text, body_style))

formula_data = [
    ["Pattern", "Example", "Match Type"],
    ["[equipment] rental [state]", "scissor lift rental new jersey", "Phrase"],
    ["[equipment] rental [city]", "forklift rental newark", "Phrase"],
    ["[equipment] rental [city] [state abbrev]", "boom lift rental denver co", "Phrase"],
    ["[equipment] for rent [state]", "excavator for rent colorado", "Phrase"],
    ["rent [equipment] [city]", "rent backhoe baltimore", "Phrase"],
    ["[equipment] hire [state]", "telehandler hire mississippi", "Phrase"],
]

formula_table = Table(formula_data, colWidths=[2.5*inch, 2.5*inch, 1*inch])
formula_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
    ('ALIGN', (2, 0), (2, -1), 'CENTER'),
]))
content.append(formula_table)

content.append(Paragraph("2.2 Keywords Per State", subsection_style))
per_state_text = """
Each state receives 16 keywords (2 per equipment category) to ensure comprehensive coverage:
"""
content.append(Paragraph(per_state_text, body_style))

per_state_data = [
    ["Equipment", "State-Level Keyword", "City-Level Keyword"],
    ["Scissor Lift", "[equipment] rental [state]", "[equipment] rental [major city]"],
    ["Boom Lift", "[equipment] rental [state]", "[equipment] rental [major city]"],
    ["Forklift", "[equipment] rental [state]", "[equipment] rental [major city]"],
    ["Telehandler", "[equipment] rental [state]", "[equipment] rental [major city]"],
    ["Excavator", "[equipment] rental [state]", "[equipment] rental [major city]"],
    ["Backhoe", "[equipment] rental [state]", "[equipment] rental [major city]"],
    ["Dozer", "[equipment] rental [state]", "[equipment] rental [major city]"],
    ["Skid Steer", "[equipment] rental [state]", "[equipment] rental [major city]"],
    ["TOTAL", "8 keywords", "8 keywords = 16/state"],
]

per_state_table = Table(per_state_data, colWidths=[1.3*inch, 2.4*inch, 2.4*inch])
per_state_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5276')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BACKGROUND', (0, 9), (-1, 9), colors.HexColor('#d5d8dc')),
    ('FONTNAME', (0, 9), (-1, 9), 'Helvetica-Bold'),
]))
content.append(per_state_table)

content.append(PageBreak())

# Section 3: Complete Keyword List - HIGH PRIORITY
content.append(Paragraph("SECTION 3: COMPLETE KEYWORD LIST", section_style))
content.append(Paragraph("3.1 HIGH PRIORITY STATES", subsection_style))

# NEW JERSEY
content.append(Paragraph("<b>NEW JERSEY (NJ)</b> - 6 Orders | 3 Suppliers | Top Equipment: Skid Steer", highlight_style))

nj_keywords = [
    ["Keyword", "Match", "Equipment", "Landing Page"],
    ["scissor lift rental new jersey", "Phrase", "Scissor Lift", "dozr.com/rent/scissor-lift"],
    ["scissor lift rental newark", "Phrase", "Scissor Lift", "dozr.com/rent/scissor-lift"],
    ["boom lift rental new jersey", "Phrase", "Boom Lift", "dozr.com/rent/articulating-boom-lift"],
    ["cherry picker rental jersey city", "Phrase", "Boom Lift", "dozr.com/rent/articulating-boom-lift"],
    ["forklift rental new jersey", "Phrase", "Forklift", "dozr.com/rent/forklift"],
    ["forklift rental newark nj", "Phrase", "Forklift", "dozr.com/rent/forklift"],
    ["telehandler rental new jersey", "Phrase", "Telehandler", "dozr.com/rent/telehandler"],
    ["telehandler rental edison nj", "Phrase", "Telehandler", "dozr.com/rent/telehandler"],
    ["excavator rental new jersey", "Phrase", "Excavator", "dozr.com/rent/excavator"],
    ["mini excavator rental newark", "Phrase", "Excavator", "dozr.com/rent/excavator"],
    ["backhoe rental new jersey", "Phrase", "Backhoe", "dozr.com/rent/backhoe"],
    ["backhoe rental jersey city", "Phrase", "Backhoe", "dozr.com/rent/backhoe"],
    ["dozer rental new jersey", "Phrase", "Dozer", "dozr.com/rent/dozer"],
    ["bulldozer rental newark nj", "Phrase", "Dozer", "dozr.com/rent/dozer"],
    ["skid steer rental new jersey", "Phrase", "Skid Steer", "dozr.com/rent/skid-steer"],
    ["bobcat rental newark", "Phrase", "Skid Steer", "dozr.com/rent/skid-steer"],
]

nj_table = Table(nj_keywords, colWidths=[2.4*inch, 0.6*inch, 1*inch, 2.5*inch])
nj_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c0392b')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 7),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ('TOPPADDING', (0, 0), (-1, -1), 3),
    ('ALIGN', (1, 0), (1, -1), 'CENTER'),
]))
content.append(nj_table)
content.append(Spacer(1, 0.1*inch))

# MISSISSIPPI
content.append(Paragraph("<b>MISSISSIPPI (MS)</b> - 4 Orders | 0 Suppliers | Top Equipment: Telehandler", highlight_style))

ms_keywords = [
    ["Keyword", "Match", "Equipment", "Landing Page"],
    ["scissor lift rental mississippi", "Phrase", "Scissor Lift", "dozr.com/rent/scissor-lift"],
    ["scissor lift rental jackson ms", "Phrase", "Scissor Lift", "dozr.com/rent/scissor-lift"],
    ["boom lift rental mississippi", "Phrase", "Boom Lift", "dozr.com/rent/articulating-boom-lift"],
    ["boom lift rental gulfport", "Phrase", "Boom Lift", "dozr.com/rent/articulating-boom-lift"],
    ["forklift rental mississippi", "Phrase", "Forklift", "dozr.com/rent/forklift"],
    ["forklift rental jackson ms", "Phrase", "Forklift", "dozr.com/rent/forklift"],
    ["telehandler rental mississippi", "Phrase", "Telehandler", "dozr.com/rent/telehandler"],
    ["telehandler rental biloxi", "Phrase", "Telehandler", "dozr.com/rent/telehandler"],
    ["excavator rental mississippi", "Phrase", "Excavator", "dozr.com/rent/excavator"],
    ["excavator rental jackson ms", "Phrase", "Excavator", "dozr.com/rent/excavator"],
    ["backhoe rental mississippi", "Phrase", "Backhoe", "dozr.com/rent/backhoe"],
    ["backhoe rental gulfport ms", "Phrase", "Backhoe", "dozr.com/rent/backhoe"],
    ["dozer rental mississippi", "Phrase", "Dozer", "dozr.com/rent/dozer"],
    ["bulldozer rental jackson", "Phrase", "Dozer", "dozr.com/rent/dozer"],
    ["skid steer rental mississippi", "Phrase", "Skid Steer", "dozr.com/rent/skid-steer"],
    ["bobcat rental jackson ms", "Phrase", "Skid Steer", "dozr.com/rent/skid-steer"],
]

ms_table = Table(ms_keywords, colWidths=[2.4*inch, 0.6*inch, 1*inch, 2.5*inch])
ms_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c0392b')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 7),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ('TOPPADDING', (0, 0), (-1, -1), 3),
    ('ALIGN', (1, 0), (1, -1), 'CENTER'),
]))
content.append(ms_table)
content.append(Spacer(1, 0.1*inch))

# COLORADO
content.append(Paragraph("<b>COLORADO (CO)</b> - 3 Orders | 1 Supplier | Top Equipment: Scissor Lift", highlight_style))

co_keywords = [
    ["Keyword", "Match", "Equipment", "Landing Page"],
    ["scissor lift rental colorado", "Phrase", "Scissor Lift", "dozr.com/rent/scissor-lift"],
    ["scissor lift rental denver", "Phrase", "Scissor Lift", "dozr.com/rent/scissor-lift"],
    ["boom lift rental colorado", "Phrase", "Boom Lift", "dozr.com/rent/articulating-boom-lift"],
    ["boom lift rental denver co", "Phrase", "Boom Lift", "dozr.com/rent/articulating-boom-lift"],
    ["forklift rental colorado", "Phrase", "Forklift", "dozr.com/rent/forklift"],
    ["forklift rental denver", "Phrase", "Forklift", "dozr.com/rent/forklift"],
    ["telehandler rental colorado", "Phrase", "Telehandler", "dozr.com/rent/telehandler"],
    ["telehandler rental colorado springs", "Phrase", "Telehandler", "dozr.com/rent/telehandler"],
    ["excavator rental colorado", "Phrase", "Excavator", "dozr.com/rent/excavator"],
    ["excavator rental denver co", "Phrase", "Excavator", "dozr.com/rent/excavator"],
    ["backhoe rental colorado", "Phrase", "Backhoe", "dozr.com/rent/backhoe"],
    ["backhoe rental denver", "Phrase", "Backhoe", "dozr.com/rent/backhoe"],
    ["dozer rental colorado", "Phrase", "Dozer", "dozr.com/rent/dozer"],
    ["bulldozer rental denver co", "Phrase", "Dozer", "dozr.com/rent/dozer"],
    ["skid steer rental colorado", "Phrase", "Skid Steer", "dozr.com/rent/skid-steer"],
    ["bobcat rental denver", "Phrase", "Skid Steer", "dozr.com/rent/skid-steer"],
]

co_table = Table(co_keywords, colWidths=[2.4*inch, 0.6*inch, 1*inch, 2.5*inch])
co_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c0392b')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 7),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ('TOPPADDING', (0, 0), (-1, -1), 3),
    ('ALIGN', (1, 0), (1, -1), 'CENTER'),
]))
content.append(co_table)

content.append(PageBreak())

# MEDIUM PRIORITY STATES
content.append(Paragraph("3.2 MEDIUM PRIORITY STATES", subsection_style))

# Maryland
content.append(Paragraph("<b>MARYLAND (MD)</b> - 2 Orders | 3 Suppliers | Major Cities: Baltimore, Frederick", highlight_style))
md_keywords = [
    ["Keyword", "Match", "Equipment", "Landing Page"],
    ["scissor lift rental maryland", "Phrase", "Scissor Lift", "dozr.com/rent/scissor-lift"],
    ["scissor lift rental baltimore", "Phrase", "Scissor Lift", "dozr.com/rent/scissor-lift"],
    ["boom lift rental maryland", "Phrase", "Boom Lift", "dozr.com/rent/articulating-boom-lift"],
    ["boom lift rental baltimore md", "Phrase", "Boom Lift", "dozr.com/rent/articulating-boom-lift"],
    ["forklift rental maryland", "Phrase", "Forklift", "dozr.com/rent/forklift"],
    ["forklift rental baltimore", "Phrase", "Forklift", "dozr.com/rent/forklift"],
    ["telehandler rental maryland", "Phrase", "Telehandler", "dozr.com/rent/telehandler"],
    ["telehandler rental frederick md", "Phrase", "Telehandler", "dozr.com/rent/telehandler"],
    ["excavator rental maryland", "Phrase", "Excavator", "dozr.com/rent/excavator"],
    ["excavator rental baltimore", "Phrase", "Excavator", "dozr.com/rent/excavator"],
    ["backhoe rental maryland", "Phrase", "Backhoe", "dozr.com/rent/backhoe"],
    ["backhoe rental baltimore md", "Phrase", "Backhoe", "dozr.com/rent/backhoe"],
    ["dozer rental maryland", "Phrase", "Dozer", "dozr.com/rent/dozer"],
    ["bulldozer rental baltimore", "Phrase", "Dozer", "dozr.com/rent/dozer"],
    ["skid steer rental maryland", "Phrase", "Skid Steer", "dozr.com/rent/skid-steer"],
    ["bobcat rental baltimore", "Phrase", "Skid Steer", "dozr.com/rent/skid-steer"],
]
md_table = Table(md_keywords, colWidths=[2.4*inch, 0.6*inch, 1*inch, 2.5*inch])
md_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f39c12')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 7),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ('TOPPADDING', (0, 0), (-1, -1), 3),
    ('ALIGN', (1, 0), (1, -1), 'CENTER'),
]))
content.append(md_table)
content.append(Spacer(1, 0.1*inch))

# Missouri
content.append(Paragraph("<b>MISSOURI (MO)</b> - 2 Orders | 2 Suppliers | Major Cities: St. Louis, Kansas City", highlight_style))
mo_keywords = [
    ["Keyword", "Match", "Equipment", "Landing Page"],
    ["scissor lift rental missouri", "Phrase", "Scissor Lift", "dozr.com/rent/scissor-lift"],
    ["scissor lift rental st louis", "Phrase", "Scissor Lift", "dozr.com/rent/scissor-lift"],
    ["boom lift rental missouri", "Phrase", "Boom Lift", "dozr.com/rent/articulating-boom-lift"],
    ["boom lift rental kansas city mo", "Phrase", "Boom Lift", "dozr.com/rent/articulating-boom-lift"],
    ["forklift rental missouri", "Phrase", "Forklift", "dozr.com/rent/forklift"],
    ["forklift rental st louis", "Phrase", "Forklift", "dozr.com/rent/forklift"],
    ["telehandler rental missouri", "Phrase", "Telehandler", "dozr.com/rent/telehandler"],
    ["telehandler rental st louis mo", "Phrase", "Telehandler", "dozr.com/rent/telehandler"],
    ["excavator rental missouri", "Phrase", "Excavator", "dozr.com/rent/excavator"],
    ["excavator rental kansas city", "Phrase", "Excavator", "dozr.com/rent/excavator"],
    ["backhoe rental missouri", "Phrase", "Backhoe", "dozr.com/rent/backhoe"],
    ["backhoe rental st louis", "Phrase", "Backhoe", "dozr.com/rent/backhoe"],
    ["dozer rental missouri", "Phrase", "Dozer", "dozr.com/rent/dozer"],
    ["bulldozer rental kansas city mo", "Phrase", "Dozer", "dozr.com/rent/dozer"],
    ["skid steer rental missouri", "Phrase", "Skid Steer", "dozr.com/rent/skid-steer"],
    ["bobcat rental st louis", "Phrase", "Skid Steer", "dozr.com/rent/skid-steer"],
]
mo_table = Table(mo_keywords, colWidths=[2.4*inch, 0.6*inch, 1*inch, 2.5*inch])
mo_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f39c12')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 7),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ('TOPPADDING', (0, 0), (-1, -1), 3),
    ('ALIGN', (1, 0), (1, -1), 'CENTER'),
]))
content.append(mo_table)

content.append(PageBreak())

# Continue Medium Priority - Utah, Nevada, Montana, New Mexico
content.append(Paragraph("3.2 MEDIUM PRIORITY STATES (Continued)", subsection_style))

# Remaining medium priority states - condensed format
medium_states = [
    ("UTAH (UT)", "2 Orders | 0 Suppliers", "Salt Lake City, Provo", [
        "scissor lift rental utah", "scissor lift rental salt lake city",
        "boom lift rental utah", "forklift rental salt lake city",
        "telehandler rental utah", "excavator rental salt lake city",
        "backhoe rental utah", "dozer rental salt lake city",
        "skid steer rental utah", "bobcat rental provo"
    ]),
    ("NEVADA (NV)", "2 Orders | 1 Supplier", "Las Vegas, Reno", [
        "scissor lift rental nevada", "scissor lift rental las vegas",
        "boom lift rental nevada", "forklift rental las vegas",
        "telehandler rental nevada", "excavator rental reno",
        "backhoe rental las vegas", "dozer rental nevada",
        "skid steer rental las vegas", "bobcat rental reno"
    ]),
    ("MONTANA (MT)", "2 Orders | 1 Supplier", "Billings, Great Falls", [
        "scissor lift rental montana", "scissor lift rental billings",
        "boom lift rental montana", "forklift rental billings",
        "telehandler rental montana", "excavator rental great falls",
        "backhoe rental billings", "dozer rental montana",
        "skid steer rental billings", "bobcat rental great falls"
    ]),
    ("NEW MEXICO (NM)", "2 Orders | 0 Suppliers", "Albuquerque, Santa Fe", [
        "scissor lift rental new mexico", "scissor lift rental albuquerque",
        "boom lift rental new mexico", "forklift rental albuquerque",
        "telehandler rental new mexico", "excavator rental santa fe",
        "backhoe rental albuquerque", "dozer rental new mexico",
        "skid steer rental albuquerque", "bobcat rental santa fe"
    ]),
]

for state_name, stats, cities, keywords in medium_states:
    content.append(Paragraph(f"<b>{state_name}</b> - {stats} | Cities: {cities}", highlight_style))
    kw_text = " | ".join(keywords)
    content.append(Paragraph(f"Keywords: {kw_text}", small_style))
    content.append(Spacer(1, 0.08*inch))

content.append(PageBreak())

# LOW PRIORITY STATES
content.append(Paragraph("3.3 LOW PRIORITY STATES", subsection_style))

low_states = [
    ("WISCONSIN (WI)", "1 Order | 1 Supplier", "Milwaukee, Madison", [
        "scissor lift rental wisconsin", "scissor lift rental milwaukee",
        "boom lift rental wisconsin", "forklift rental milwaukee",
        "telehandler rental wisconsin", "excavator rental madison",
        "backhoe rental milwaukee", "dozer rental wisconsin",
        "skid steer rental milwaukee", "bobcat rental madison"
    ]),
    ("INDIANA (IN)", "1 Order | 1 Supplier", "Indianapolis, Fort Wayne", [
        "scissor lift rental indiana", "scissor lift rental indianapolis",
        "boom lift rental indiana", "forklift rental indianapolis",
        "telehandler rental indiana", "excavator rental fort wayne",
        "backhoe rental indianapolis", "dozer rental indiana",
        "skid steer rental indianapolis", "bobcat rental fort wayne"
    ]),
    ("KANSAS (KS)", "1 Order | 1 Supplier", "Wichita, Kansas City", [
        "scissor lift rental kansas", "scissor lift rental wichita",
        "boom lift rental kansas", "forklift rental wichita",
        "telehandler rental kansas", "excavator rental kansas city ks",
        "backhoe rental wichita", "dozer rental kansas",
        "skid steer rental wichita", "bobcat rental kansas city ks"
    ]),
    ("LOUISIANA (LA)", "1 Order | 0 Suppliers", "New Orleans, Baton Rouge", [
        "scissor lift rental louisiana", "scissor lift rental new orleans",
        "boom lift rental louisiana", "forklift rental new orleans",
        "telehandler rental louisiana", "excavator rental baton rouge",
        "backhoe rental new orleans", "dozer rental louisiana",
        "skid steer rental new orleans", "bobcat rental baton rouge"
    ]),
    ("MAINE (ME)", "1 Order | 2 Suppliers", "Portland, Augusta", [
        "scissor lift rental maine", "scissor lift rental portland me",
        "boom lift rental maine", "forklift rental portland maine",
        "telehandler rental maine", "excavator rental augusta me",
        "backhoe rental portland me", "dozer rental maine",
        "skid steer rental portland me", "bobcat rental augusta"
    ]),
    ("WASHINGTON (WA)", "1 Order | 1 Supplier", "Seattle, Spokane", [
        "scissor lift rental washington state", "scissor lift rental seattle",
        "boom lift rental washington", "forklift rental seattle",
        "telehandler rental washington state", "excavator rental spokane",
        "backhoe rental seattle", "dozer rental washington",
        "skid steer rental seattle", "bobcat rental spokane"
    ]),
]

for state_name, stats, cities, keywords in low_states:
    content.append(Paragraph(f"<b>{state_name}</b> - {stats} | Cities: {cities}", highlight_style))
    kw_text = " | ".join(keywords)
    content.append(Paragraph(f"Keywords: {kw_text}", small_style))
    content.append(Spacer(1, 0.08*inch))

content.append(PageBreak())

# Section 4: DSA Campaign Implementation
content.append(Paragraph("SECTION 4: DSA CAMPAIGN IMPLEMENTATION STRATEGY", section_style))

content.append(Paragraph("4.1 Campaign Structure", subsection_style))
structure_text = """
The DSA-AllPages-Tier1-New-US-2 campaign will be modified to include the new state keywords.
The recommended structure maintains alignment with existing campaign architecture:
"""
content.append(Paragraph(structure_text, body_style))

structure_data = [
    ["Component", "Configuration", "Notes"],
    ["Campaign", "DSA-AllPages-Tier1-New-US-2", "Existing campaign - add geo-targets"],
    ["Ad Group", "DSA-Tier1-New-USA", "Add keywords to existing ad group"],
    ["Geo-Targeting", "Add 15 new states", "NJ, MS, CO, MD, MO, MT, UT, NV, NM, WI, LA, ME, WA, IN, KS"],
    ["Match Types", "Phrase Match", "Balanced reach and control for new markets"],
    ["Bid Strategy", "Inherit from campaign (tROAS)", "No manual bid adjustments initially"],
    ["Daily Budget", "Shared with existing", "No budget increase required"],
]

structure_table = Table(structure_data, colWidths=[1.3*inch, 2.2*inch, 3*inch])
structure_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5276')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
]))
content.append(structure_table)

content.append(Paragraph("4.2 Keyword-to-Landing Page Mapping", subsection_style))
mapping_text = """
Each keyword must direct to the correct equipment landing page to maximize Quality Score and conversion rate:
"""
content.append(Paragraph(mapping_text, body_style))

mapping_data = [
    ["Equipment Keyword Contains", "Final URL"],
    ["scissor lift, aerial lift, slab lift", "https://dozr.com/rent/scissor-lift"],
    ["boom lift, cherry picker, manlift, articulating", "https://dozr.com/rent/articulating-boom-lift"],
    ["forklift, lift truck", "https://dozr.com/rent/forklift"],
    ["telehandler, reach forklift, lull", "https://dozr.com/rent/telehandler"],
    ["excavator, mini excavator, digger", "https://dozr.com/rent/excavator"],
    ["backhoe", "https://dozr.com/rent/backhoe"],
    ["dozer, bulldozer", "https://dozr.com/rent/dozer"],
    ["skid steer, bobcat, loader", "https://dozr.com/rent/skid-steer"],
]

mapping_table = Table(mapping_data, colWidths=[2.8*inch, 3.7*inch])
mapping_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
]))
content.append(mapping_table)

content.append(Paragraph("4.3 Negative Keywords", subsection_style))
neg_text = """
To prevent wasted spend on equipment DOZR doesn't rent, add these negative keywords:
"""
content.append(Paragraph(neg_text, body_style))

neg_keywords = [
    ["Category", "Negative Keywords (Exact Match)"],
    ["Generators", "generator rental, portable generator, power generator"],
    ["Tools", "tool rental, power tools, hand tools, tool hire"],
    ["Trucks", "dump truck rental, semi truck, box truck, moving truck"],
    ["Cranes", "crane rental, mobile crane, tower crane"],
    ["Trailers", "trailer rental, flatbed trailer, equipment trailer"],
    ["Compressors", "air compressor rental, compressor hire"],
    ["Concrete", "concrete mixer, cement mixer, concrete pump"],
    ["Jobs/Careers", "forklift jobs, operator jobs, equipment operator"],
]

neg_table = Table(neg_keywords, colWidths=[1.3*inch, 5.2*inch])
neg_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c0392b')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
]))
content.append(neg_table)

content.append(PageBreak())

# Section 5: Summary
content.append(Paragraph("SECTION 5: KEYWORD SUMMARY & TOTALS", section_style))

summary_data = [
    ["Priority", "States", "Keywords/State", "Total Keywords"],
    ["HIGH", "NJ, MS, CO (3 states)", "16", "48"],
    ["MEDIUM", "MD, MO, MT, UT, NV, NM (6 states)", "16", "96"],
    ["LOW", "WI, IN, KS, LA, ME, WA (6 states)", "16", "96"],
    ["TOTAL", "15 states", "-", "240 keywords"],
]

summary_table = Table(summary_data, colWidths=[1.2*inch, 2.5*inch, 1.2*inch, 1.2*inch])
summary_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5276')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ('TOPPADDING', (0, 0), (-1, -1), 8),
    ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
    ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#d5d8dc')),
    ('FONTNAME', (0, 4), (-1, 4), 'Helvetica-Bold'),
]))
content.append(summary_table)

content.append(Spacer(1, 0.2*inch))

content.append(Paragraph("Equipment Coverage Per State:", subsection_style))
equip_summary = [
    ["Equipment", "State KWs", "City KWs", "Total"],
    ["Scissor Lift", "15", "15", "30"],
    ["Boom Lift", "15", "15", "30"],
    ["Forklift", "15", "15", "30"],
    ["Telehandler", "15", "15", "30"],
    ["Excavator", "15", "15", "30"],
    ["Backhoe", "15", "15", "30"],
    ["Dozer", "15", "15", "30"],
    ["Skid Steer", "15", "15", "30"],
    ["TOTAL", "120", "120", "240"],
]

equip_sum_table = Table(equip_summary, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch])
equip_sum_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ('BACKGROUND', (0, 9), (-1, 9), colors.HexColor('#d5d8dc')),
    ('FONTNAME', (0, 9), (-1, 9), 'Helvetica-Bold'),
]))
content.append(equip_sum_table)

content.append(Spacer(1, 0.2*inch))

key_points = """
<b>Key Implementation Points:</b><br/>
• All 240 keywords are aligned with DOZR's 8 equipment categories<br/>
• Each keyword maps to the correct equipment landing page<br/>
• Negative keywords prevent spend on non-DOZR equipment<br/>
• Phrase Match provides balanced reach and control for new markets<br/>
• Landing pages match search intent for maximum Quality Score
"""
content.append(Paragraph(key_points, body_style))

# Build PDF
doc.build(content)
print(f"PDF created: {pdf_path}")
