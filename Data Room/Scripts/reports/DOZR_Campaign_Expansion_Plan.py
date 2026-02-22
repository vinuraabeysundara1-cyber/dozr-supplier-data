#!/usr/bin/env python3
"""
DOZR Campaign Expansion Plan - New Geo Markets
Creates a detailed PDF plan for duplicating campaigns to new geos
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime

# New Geos to Target
NEW_GEOS = [
    {"state": "Colorado", "abbrev": "CO", "key_market": "Denver", "geo_id_state": 21123},
    {"state": "Indiana", "abbrev": "IN", "key_market": "Indianapolis", "geo_id_state": 21140},
    {"state": "Kansas", "abbrev": "KS", "key_market": "Kansas City", "geo_id_state": 21147},
    {"state": "Kentucky", "abbrev": "KY", "key_market": "Louisville", "geo_id_state": 21148},
    {"state": "Louisiana", "abbrev": "LA", "key_market": "New Orleans", "geo_id_state": 21151},
    {"state": "Minnesota", "abbrev": "MN", "key_market": "Minneapolis", "geo_id_state": 21158},
    {"state": "Missouri", "abbrev": "MO", "key_market": "Kansas City", "geo_id_state": 21161},
    {"state": "Nebraska", "abbrev": "NE", "key_market": "Omaha", "geo_id_state": 21164},
    {"state": "New Mexico", "abbrev": "NM", "key_market": "Albuquerque", "geo_id_state": 21168},
    {"state": "Nevada", "abbrev": "NV", "key_market": "Las Vegas", "geo_id_state": 21166},
    {"state": "Oklahoma", "abbrev": "OK", "key_market": "Oklahoma City", "geo_id_state": 21172},
    {"state": "Utah", "abbrev": "UT", "key_market": "Salt Lake City", "geo_id_state": 21183},
    {"state": "Washington", "abbrev": "WA", "key_market": "Seattle", "geo_id_state": 21186},
    {"state": "Iowa", "abbrev": "IA", "key_market": "Omaha Metro", "geo_id_state": 21145},
]

# Current campaigns to duplicate
CURRENT_CAMPAIGNS = [
    {"name": "Search-Scissor-Lift-Core-Geos-US", "type": "Search", "equipment": "Scissor Lift", "bid_strategy": "tROAS"},
    {"name": "Search-Forklift-Core-Geos-US", "type": "Search", "equipment": "Forklift", "bid_strategy": "tROAS"},
    {"name": "Search-Telehandler-Core-Geos-US", "type": "Search", "equipment": "Telehandler", "bid_strategy": "tROAS"},
    {"name": "Search-Excavator-Core-Geos-US", "type": "Search", "equipment": "Excavator", "bid_strategy": "tROAS"},
    {"name": "Search-Dozers-Core-Geos-US-V3", "type": "Search", "equipment": "Dozer", "bid_strategy": "tROAS"},
    {"name": "Search-Backhoe-Core-Geos-US", "type": "Search", "equipment": "Backhoe", "bid_strategy": "tROAS"},
    {"name": "Search-Loader-Core-Geos-US", "type": "Search", "equipment": "Loader", "bid_strategy": "tROAS"},
    {"name": "Search-Demand-Boom-Lifts", "type": "Search", "equipment": "Boom Lift", "bid_strategy": "Max Conv"},
    {"name": "DSA-AllPages-Tier1-New-US-2", "type": "DSA", "equipment": "All", "bid_strategy": "tROAS"},
]

# Create PDF
pdf_path = "/Users/vinuraabeysundara/DOZR_Campaign_Expansion_Plan.pdf"
doc = SimpleDocTemplate(pdf_path, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch,
                        leftMargin=0.5*inch, rightMargin=0.5*inch)

# Styles
styles = getSampleStyleSheet()
title_style = ParagraphStyle('Title1', parent=styles['Title'], fontSize=20, spaceAfter=6,
                             textColor=colors.HexColor('#1a5276'), alignment=TA_CENTER)
subtitle_style = ParagraphStyle('Subtitle1', parent=styles['Normal'], fontSize=11, spaceAfter=12,
                                textColor=colors.HexColor('#5d6d7e'), alignment=TA_CENTER)
section_style = ParagraphStyle('Section1', parent=styles['Heading1'], fontSize=13, spaceBefore=12,
                               spaceAfter=8, textColor=colors.HexColor('#1a5276'))
subsection_style = ParagraphStyle('Subsection1', parent=styles['Heading2'], fontSize=11, spaceBefore=10,
                                  spaceAfter=6, textColor=colors.HexColor('#2874a6'))
body_style = ParagraphStyle('Body1', parent=styles['Normal'], fontSize=9, spaceAfter=6,
                            alignment=TA_JUSTIFY, leading=12)
highlight_style = ParagraphStyle('Highlight1', parent=styles['Normal'], fontSize=9, spaceAfter=4,
                                 textColor=colors.HexColor('#1a5276'), fontName='Helvetica-Bold')
small_style = ParagraphStyle('Small1', parent=styles['Normal'], fontSize=8, spaceAfter=4,
                             textColor=colors.HexColor('#5d6d7e'))
warning_style = ParagraphStyle('Warning1', parent=styles['Normal'], fontSize=9, spaceAfter=6,
                               textColor=colors.HexColor('#c0392b'), fontName='Helvetica-Bold')

content = []

# Title Page
content.append(Spacer(1, 0.5*inch))
content.append(Paragraph("DOZR Campaign Expansion Plan", title_style))
content.append(Paragraph("New Geo Markets - Duplicate Campaign Strategy", subtitle_style))
content.append(Spacer(1, 0.2*inch))

meta_data = [
    ["Document Type:", "Campaign Duplication & Geo Expansion Plan"],
    ["Date:", datetime.now().strftime("%B %d, %Y")],
    ["New Markets:", f"{len(NEW_GEOS)} States/Markets"],
    ["Campaigns to Duplicate:", f"{len(CURRENT_CAMPAIGNS)} campaigns"],
    ["New Campaigns to Create:", f"{len(CURRENT_CAMPAIGNS)} expansion campaigns"],
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

# Section 1: New Geo Markets
content.append(Paragraph("SECTION 1: NEW GEO MARKETS TO TARGET", section_style))

geo_data = [["#", "State", "Abbrev", "Key Market", "Geo Target ID"]]
for i, geo in enumerate(NEW_GEOS, 1):
    geo_data.append([str(i), geo["state"], geo["abbrev"], geo["key_market"], str(geo["geo_id_state"])])

geo_table = Table(geo_data, colWidths=[0.4*inch, 1.3*inch, 0.7*inch, 1.4*inch, 1*inch])
geo_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5276')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('ALIGN', (0, 0), (0, -1), 'CENTER'),
    ('ALIGN', (2, 0), (2, -1), 'CENTER'),
    ('ALIGN', (4, 0), (4, -1), 'CENTER'),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
]))
content.append(geo_table)

content.append(Spacer(1, 0.15*inch))
content.append(Paragraph("<b>Note:</b> Kansas City spans both Kansas and Missouri. Iowa's Omaha Metro will share the Omaha, NE DMA.", small_style))

content.append(PageBreak())

# Section 2: Campaign Duplication Strategy
content.append(Paragraph("SECTION 2: CAMPAIGN DUPLICATION STRATEGY", section_style))

content.append(Paragraph("2.1 Overview", subsection_style))
strategy_text = """
To protect your existing campaign data and Smart Bidding learning, we will create <b>separate expansion campaigns</b>
for the new geos rather than adding them to existing campaigns. This approach:
<br/><br/>
- Preserves historical data and bidding optimization in current campaigns<br/>
- Allows new geos to build their own conversion history<br/>
- Enables independent budget control for expansion markets<br/>
- Provides clear performance comparison between established vs. new markets
"""
content.append(Paragraph(strategy_text, body_style))

content.append(Paragraph("2.2 Naming Convention", subsection_style))
naming_text = """
New campaigns will follow this naming pattern to maintain organization:
"""
content.append(Paragraph(naming_text, body_style))

naming_data = [
    ["Current Campaign", "New Expansion Campaign"],
    ["Search-Scissor-Lift-Core-Geos-US", "Search-Scissor-Lift-Expansion-Geos-US"],
    ["Search-Forklift-Core-Geos-US", "Search-Forklift-Expansion-Geos-US"],
    ["Search-Telehandler-Core-Geos-US", "Search-Telehandler-Expansion-Geos-US"],
    ["Search-Excavator-Core-Geos-US", "Search-Excavator-Expansion-Geos-US"],
    ["Search-Dozers-Core-Geos-US-V3", "Search-Dozers-Expansion-Geos-US"],
    ["Search-Backhoe-Core-Geos-US", "Search-Backhoe-Expansion-Geos-US"],
    ["Search-Loader-Core-Geos-US", "Search-Loader-Expansion-Geos-US"],
    ["Search-Demand-Boom-Lifts", "Search-Boom-Lifts-Expansion-Geos-US"],
    ["DSA-AllPages-Tier1-New-US-2", "DSA-AllPages-Expansion-Geos-US"],
]

naming_table = Table(naming_data, colWidths=[3.2*inch, 3.2*inch])
naming_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
    ('BACKGROUND', (1, 1), (1, -1), colors.HexColor('#eafaf1')),
]))
content.append(naming_table)

content.append(PageBreak())

# Section 3: Geo Exclusion Strategy
content.append(Paragraph("SECTION 3: GEO EXCLUSION STRATEGY (CRITICAL)", section_style))

content.append(Paragraph("""
To prevent campaigns from competing with each other, each campaign group must EXCLUDE the other's geos.
This ensures clean data and no auction overlap.
""", warning_style))

content.append(Paragraph("3.1 Exclusions for CURRENT Campaigns (Core Geos)", subsection_style))
content.append(Paragraph("Add these 14 states as <b>NEGATIVE location targets</b> to all existing Core-Geos-US campaigns:", body_style))

exclude_from_current = [["State to Exclude", "Geo Target ID", "Exclude From"]]
for geo in NEW_GEOS:
    exclude_from_current.append([f"{geo['state']} ({geo['abbrev']})", str(geo["geo_id_state"]), "All Core-Geos-US campaigns"])

exclude_table1 = Table(exclude_from_current, colWidths=[1.8*inch, 1.2*inch, 2.5*inch])
exclude_table1.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c0392b')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 7),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ('TOPPADDING', (0, 0), (-1, -1), 3),
]))
content.append(exclude_table1)

content.append(Spacer(1, 0.15*inch))

content.append(Paragraph("3.2 Exclusions for NEW Expansion Campaigns", subsection_style))
content.append(Paragraph("Add these 8 states + 30 DMAs as <b>NEGATIVE location targets</b> to all new Expansion campaigns:", body_style))

current_geos_exclude = [
    ["Location Type", "Locations to Exclude"],
    ["States (8)", "Arizona, California, Florida, Georgia, New York, North Carolina, Tennessee, Texas"],
    ["DMAs (30)", "Atlanta, Austin, Buffalo, Charleston SC, Charlotte, Charlottesville, Dallas-Ft Worth, Greensboro, Greenville-Spartanburg, Houston, Knoxville, Los Angeles, Memphis, Miami, Nashville, New York NY, Norfolk, Orlando, Raleigh-Durham, Richmond, Rochester, San Antonio, San Diego, Savannah, Syracuse, Tampa, Tri-Cities TN-VA, Waco-Temple-Bryan, West Palm Beach, Albany-Schenectady-Troy"],
    ["Counties (2)", "Maricopa County (AZ), Pinal County (AZ)"],
    ["Cities (5)", "Phoenix, Hesperia, Loma Linda, Elberton, Stonecrest"],
    ["Regions (1)", "San Francisco Bay Area"],
]

exclude_table2 = Table(current_geos_exclude, colWidths=[1.2*inch, 5.3*inch])
exclude_table2.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c0392b')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 7),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
]))
content.append(exclude_table2)

content.append(PageBreak())

# Section 4: Campaign Settings
content.append(Paragraph("SECTION 4: EXPANSION CAMPAIGN SETTINGS", section_style))

content.append(Paragraph("4.1 Bid Strategy Recommendations", subsection_style))
bid_text = """
For new expansion campaigns with no historical data, we recommend starting with <b>Maximize Conversions</b>
(not tROAS) for the first 4-6 weeks until you accumulate 30+ conversions, then switch to tROAS.
"""
content.append(Paragraph(bid_text, body_style))

bid_data = [
    ["Campaign Type", "Current Bid Strategy", "Expansion Campaign Strategy", "Switch to tROAS After"],
    ["Equipment Search", "tROAS", "Maximize Conversions", "30+ conversions"],
    ["Boom Lifts", "Max Conversions", "Maximize Conversions", "Keep as-is"],
    ["DSA", "tROAS", "Maximize Conversions", "30+ conversions"],
]

bid_table = Table(bid_data, colWidths=[1.5*inch, 1.3*inch, 1.8*inch, 1.5*inch])
bid_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5276')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
    ('ALIGN', (3, 0), (3, -1), 'CENTER'),
]))
content.append(bid_table)

content.append(Paragraph("4.2 Budget Recommendations", subsection_style))
budget_text = """
Start with conservative daily budgets for expansion campaigns. You can increase once performance data is available.
"""
content.append(Paragraph(budget_text, body_style))

budget_data = [
    ["Campaign", "Recommended Starting Budget", "Notes"],
    ["Search-Scissor-Lift-Expansion", "$50-75/day", "High volume equipment"],
    ["Search-Forklift-Expansion", "$50-75/day", "High volume equipment"],
    ["Search-Boom-Lifts-Expansion", "$40-60/day", "Medium volume"],
    ["Search-Excavator-Expansion", "$40-60/day", "Medium volume"],
    ["Search-Telehandler-Expansion", "$30-50/day", "Lower volume"],
    ["Search-Backhoe-Expansion", "$30-50/day", "Lower volume"],
    ["Search-Dozers-Expansion", "$25-40/day", "Lower volume"],
    ["Search-Loader-Expansion", "$30-50/day", "Medium volume"],
    ["DSA-Expansion", "$40-60/day", "Catch-all campaign"],
]

budget_table = Table(budget_data, colWidths=[2.3*inch, 1.8*inch, 2*inch])
budget_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
]))
content.append(budget_table)

content.append(Paragraph("<b>Total Estimated Daily Budget for Expansion:</b> $335-520/day ($10,000-15,600/month)", highlight_style))

content.append(PageBreak())

# Section 5: Keyword Strategy
content.append(Paragraph("SECTION 5: KEYWORD & NEGATIVE KEYWORD ALIGNMENT", section_style))

content.append(Paragraph("5.1 Keyword Duplication", subsection_style))
kw_text = """
All keywords from existing campaigns will be duplicated to expansion campaigns. The same match types
and keyword structure will be maintained. Keywords do NOT need location modifiers since geo-targeting
handles location relevance.
"""
content.append(Paragraph(kw_text, body_style))

content.append(Paragraph("5.2 Cross-Campaign Negative Keywords", subsection_style))
neg_text = """
To prevent keyword cannibalization between campaigns, ensure these negative keyword rules are in place:
"""
content.append(Paragraph(neg_text, body_style))

neg_data = [
    ["Campaign Type", "Negative Keywords to Add"],
    ["Scissor Lift campaigns", "boom lift, cherry picker, forklift, telehandler, excavator, backhoe, dozer, loader, skid steer"],
    ["Boom Lift campaigns", "scissor lift, forklift, telehandler, excavator, backhoe, dozer, loader, skid steer"],
    ["Forklift campaigns", "scissor lift, boom lift, telehandler, excavator, backhoe, dozer, loader, skid steer"],
    ["Telehandler campaigns", "scissor lift, boom lift, forklift, excavator, backhoe, dozer, loader, skid steer"],
    ["Excavator campaigns", "scissor lift, boom lift, forklift, telehandler, backhoe, dozer, loader, skid steer"],
    ["Backhoe campaigns", "scissor lift, boom lift, forklift, telehandler, excavator, dozer, loader, skid steer"],
    ["Dozer campaigns", "scissor lift, boom lift, forklift, telehandler, excavator, backhoe, loader, skid steer"],
    ["Loader campaigns", "scissor lift, boom lift, forklift, telehandler, excavator, backhoe, dozer"],
]

neg_table = Table(neg_data, colWidths=[1.5*inch, 5*inch])
neg_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8e44ad')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 7),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
]))
content.append(neg_table)

content.append(Paragraph("5.3 Non-DOZR Equipment Negatives (Apply to ALL campaigns)", subsection_style))
non_dozr = """
<b>Negative Keywords for equipment DOZR does not rent:</b><br/>
generator, crane, dump truck, concrete mixer, cement mixer, compressor, trailer, semi truck,
box truck, moving truck, power tools, hand tools, welding, pressure washer, lawn mower, tractor
"""
content.append(Paragraph(non_dozr, body_style))

content.append(PageBreak())

# Section 6: Implementation Checklist
content.append(Paragraph("SECTION 6: IMPLEMENTATION CHECKLIST", section_style))

checklist = [
    ["Step", "Action", "Status"],
    ["1", "Export current campaign settings from Google Ads Editor", "[ ]"],
    ["2", "Duplicate campaigns with new naming convention", "[ ]"],
    ["3", "Update geo-targeting: Add 14 new states to expansion campaigns", "[ ]"],
    ["4", "Update geo-targeting: Add geo EXCLUSIONS to expansion campaigns (current 8 states + DMAs)", "[ ]"],
    ["5", "Update geo-targeting: Add geo EXCLUSIONS to current campaigns (14 new states)", "[ ]"],
    ["6", "Set bid strategy to Maximize Conversions for expansion campaigns", "[ ]"],
    ["7", "Set daily budgets for expansion campaigns", "[ ]"],
    ["8", "Verify negative keywords are in place (equipment cross-negatives)", "[ ]"],
    ["9", "Verify ads and extensions are duplicated correctly", "[ ]"],
    ["10", "Set expansion campaigns to PAUSED initially", "[ ]"],
    ["11", "Review all settings, then ENABLE expansion campaigns", "[ ]"],
    ["12", "Monitor for 48 hours for any issues", "[ ]"],
    ["13", "After 4-6 weeks: Evaluate switching to tROAS", "[ ]"],
]

check_table = Table(checklist, colWidths=[0.5*inch, 5*inch, 0.8*inch])
check_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5276')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
    ('ALIGN', (0, 0), (0, -1), 'CENTER'),
    ('ALIGN', (2, 0), (2, -1), 'CENTER'),
]))
content.append(check_table)

content.append(PageBreak())

# Section 7: Geo Target IDs Reference
content.append(Paragraph("SECTION 7: GEO TARGET CONSTANT IDs FOR IMPLEMENTATION", section_style))

content.append(Paragraph("7.1 New States to ADD to Expansion Campaigns", subsection_style))

new_geo_ids = [["State", "Geo Target ID", "Resource Name"]]
for geo in NEW_GEOS:
    new_geo_ids.append([f"{geo['state']} ({geo['abbrev']})", str(geo["geo_id_state"]), f"geoTargetConstants/{geo['geo_id_state']}"])

new_geo_table = Table(new_geo_ids, colWidths=[2*inch, 1.2*inch, 2.5*inch])
new_geo_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
]))
content.append(new_geo_table)

content.append(Spacer(1, 0.15*inch))

content.append(Paragraph("7.2 Current States to EXCLUDE from Expansion Campaigns", subsection_style))

current_states = [
    {"state": "Arizona", "geo_id": 21136},
    {"state": "California", "geo_id": 21137},
    {"state": "Florida", "geo_id": 21142},
    {"state": "Georgia", "geo_id": 21143},
    {"state": "New York", "geo_id": 21167},
    {"state": "North Carolina", "geo_id": 21160},
    {"state": "Tennessee", "geo_id": 21175},
    {"state": "Texas", "geo_id": 21176},
]

current_geo_ids = [["State", "Geo Target ID", "Resource Name"]]
for geo in current_states:
    current_geo_ids.append([geo['state'], str(geo["geo_id"]), f"geoTargetConstants/{geo['geo_id']}"])

current_geo_table = Table(current_geo_ids, colWidths=[2*inch, 1.2*inch, 2.5*inch])
current_geo_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c0392b')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
]))
content.append(current_geo_table)

content.append(PageBreak())

# Section 8: Summary
content.append(Paragraph("SECTION 8: SUMMARY", section_style))

summary_data = [
    ["Metric", "Count"],
    ["New States/Markets", "14"],
    ["Campaigns to Duplicate", "9"],
    ["New Campaigns to Create", "9"],
    ["Total Geo Exclusions (Current -> Expansion)", "14 states"],
    ["Total Geo Exclusions (Expansion -> Current)", "8 states + 30 DMAs + cities/counties"],
    ["Estimated Daily Budget (Expansion)", "$335-520/day"],
    ["Estimated Monthly Budget (Expansion)", "$10,000-15,600/month"],
    ["Recommended Initial Bid Strategy", "Maximize Conversions"],
    ["Switch to tROAS After", "30+ conversions (4-6 weeks)"],
]

summary_table = Table(summary_data, colWidths=[3.5*inch, 2.5*inch])
summary_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5276')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#d5f5e3')),
]))
content.append(summary_table)

content.append(Spacer(1, 0.2*inch))

key_points = """
<b>Key Takeaways:</b><br/><br/>
1. <b>Separate campaigns</b> for expansion geos protects existing campaign data<br/><br/>
2. <b>Mutual geo exclusions</b> prevent campaigns from competing in auctions<br/><br/>
3. <b>Start with Maximize Conversions</b> until you have enough data for tROAS<br/><br/>
4. <b>Conservative budgets</b> initially, scale up based on performance<br/><br/>
5. <b>Same keywords</b> work for new geos - geo-targeting handles location relevance
"""
content.append(Paragraph(key_points, body_style))

# Build PDF
doc.build(content)
print(f"PDF created: {pdf_path}")
