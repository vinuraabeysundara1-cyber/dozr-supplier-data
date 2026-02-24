from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from google.ads.googleads.client import GoogleAdsClient
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Load credentials and data
client = GoogleAdsClient.load_from_storage('/Users/vinuraabeysundara/Desktop/ICG/DOZR/Data Room/Config/google-ads.yaml')
ga_service = client.get_service('GoogleAdsService')
customer_id = '8531896842'

# Define periods
period1_start = '2026-02-01'
period1_end = '2026-02-10'
period2_start = '2026-02-11'
period2_end = '2026-02-20'

print("Fetching data from Google Ads API...")

# Query ad group performance
query = f"""
    SELECT
        campaign.name,
        ad_group.name,
        segments.date,
        metrics.cost_micros,
        metrics.clicks,
        metrics.conversions,
        metrics.conversions_value
    FROM ad_group
    WHERE segments.date BETWEEN '{period1_start}' AND '{period2_end}'
        AND campaign.status = 'ENABLED'
        AND ad_group.status = 'ENABLED'
        AND campaign.name LIKE '%US%'
        AND campaign.name NOT LIKE '%Expansion%'
        AND campaign.name NOT LIKE '%-CA%'
"""

response = ga_service.search(customer_id=customer_id, query=query)

# Organize data
campaigns = {}
for row in response:
    campaign_name = row.campaign.name
    ad_group_name = row.ad_group.name
    date = row.segments.date

    period = 'period1' if period1_start <= date <= period1_end else 'period2'

    if campaign_name not in campaigns:
        campaigns[campaign_name] = {}
    if ad_group_name not in campaigns[campaign_name]:
        campaigns[campaign_name][ad_group_name] = {
            'period1': {'spend': 0, 'clicks': 0, 'conversions': 0, 'value': 0},
            'period2': {'spend': 0, 'clicks': 0, 'conversions': 0, 'value': 0}
        }

    campaigns[campaign_name][ad_group_name][period]['spend'] += row.metrics.cost_micros / 1_000_000
    campaigns[campaign_name][ad_group_name][period]['clicks'] += row.metrics.clicks
    campaigns[campaign_name][ad_group_name][period]['conversions'] += row.metrics.conversions
    campaigns[campaign_name][ad_group_name][period]['value'] += row.metrics.conversions_value

# Get conversions breakdown
query_conv = f"""
    SELECT
        campaign.name,
        ad_group.name,
        segments.date,
        segments.conversion_action_name,
        metrics.conversions
    FROM ad_group
    WHERE segments.date BETWEEN '{period1_start}' AND '{period2_end}'
        AND campaign.status = 'ENABLED'
        AND ad_group.status = 'ENABLED'
        AND campaign.name LIKE '%US%'
        AND campaign.name NOT LIKE '%Expansion%'
        AND campaign.name NOT LIKE '%-CA%'
        AND metrics.conversions > 0
"""

response_conv = ga_service.search(customer_id=customer_id, query=query_conv)

adgroup_conversions = {}
for row in response_conv:
    campaign_name = row.campaign.name
    ad_group_name = row.ad_group.name
    date = row.segments.date
    conv_name = row.segments.conversion_action_name
    conversions = row.metrics.conversions

    period = 'period1' if period1_start <= date <= period1_end else 'period2'

    if campaign_name not in adgroup_conversions:
        adgroup_conversions[campaign_name] = {}
    if ad_group_name not in adgroup_conversions[campaign_name]:
        adgroup_conversions[campaign_name][ad_group_name] = {
            'period1': {'calls': 0, 'quotes': 0, 'deals': 0},
            'period2': {'calls': 0, 'quotes': 0, 'deals': 0}
        }

    if 'Phone Call' in conv_name or 'Calls from ads' in conv_name:
        adgroup_conversions[campaign_name][ad_group_name][period]['calls'] += conversions
    elif 'quote' in conv_name.lower():
        adgroup_conversions[campaign_name][ad_group_name][period]['quotes'] += conversions
    elif 'Closed Won' in conv_name or 'Deal' in conv_name:
        adgroup_conversions[campaign_name][ad_group_name][period]['deals'] += conversions

print("Creating PDF report...")

# Create PDF
pdf_filename = '/Users/vinuraabeysundara/Desktop/ICG/DOZR/US_AdGroup_Analysis_Feb1-20.pdf'
doc = SimpleDocTemplate(pdf_filename, pagesize=landscape(letter),
                       rightMargin=0.5*inch, leftMargin=0.5*inch,
                       topMargin=0.75*inch, bottomMargin=0.5*inch)

# Styles
styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=16,
    textColor=colors.HexColor('#1a1a1a'),
    spaceAfter=12,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)
heading_style = ParagraphStyle(
    'CustomHeading',
    parent=styles['Heading2'],
    fontSize=12,
    textColor=colors.HexColor('#2c5aa0'),
    spaceAfter=6,
    fontName='Helvetica-Bold'
)

story = []

# Title page
story.append(Paragraph("US CAMPAIGNS - AD GROUP LEVEL ANALYSIS", title_style))
story.append(Paragraph("Excluding Expansion Campaigns", styles['Normal']))
story.append(Spacer(1, 0.2*inch))
story.append(Paragraph(f"Period 1: Feb 1-10, 2026  |  Period 2: Feb 11-20, 2026", styles['Normal']))
story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
story.append(Spacer(1, 0.3*inch))

# Process each campaign
for campaign_name in sorted(campaigns.keys()):
    story.append(Paragraph(f"{campaign_name}", heading_style))
    story.append(Spacer(1, 0.1*inch))

    # Create table data
    table_data = [
        ['Ad Group', 'P1 Spend', 'P1 Calls', 'P1 Quotes', 'P1 Deals', 'P2 Spend', 'P2 Calls', 'P2 Quotes', 'P2 Deals', 'Change']
    ]

    for ad_group_name in sorted(campaigns[campaign_name].keys()):
        p1 = campaigns[campaign_name][ad_group_name]['period1']
        p2 = campaigns[campaign_name][ad_group_name]['period2']

        # Skip if no spend
        if p1['spend'] == 0 and p2['spend'] == 0:
            continue

        c1 = adgroup_conversions.get(campaign_name, {}).get(ad_group_name, {}).get('period1', {'calls': 0, 'quotes': 0, 'deals': 0})
        c2 = adgroup_conversions.get(campaign_name, {}).get(ad_group_name, {}).get('period2', {'calls': 0, 'quotes': 0, 'deals': 0})

        spend_change = ((p2['spend'] - p1['spend']) / p1['spend'] * 100) if p1['spend'] > 0 else 0

        table_data.append([
            ad_group_name[:30],
            f"${p1['spend']:.0f}",
            str(int(c1['calls'])),
            str(int(c1['quotes'])),
            str(int(c1['deals'])),
            f"${p2['spend']:.0f}",
            str(int(c2['calls'])),
            str(int(c2['quotes'])),
            str(int(c2['deals'])),
            f"{spend_change:+.0f}%"
        ])

    # Create table
    if len(table_data) > 1:
        t = Table(table_data, colWidths=[2.2*inch, 0.6*inch, 0.5*inch, 0.5*inch, 0.5*inch,
                                         0.6*inch, 0.5*inch, 0.5*inch, 0.5*inch, 0.6*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
        ]))
        story.append(t)

    story.append(Spacer(1, 0.2*inch))

# Build PDF
doc.build(story)

print(f"\n✅ PDF report created: {pdf_filename}")
print(f"📄 File size: {__import__('os').path.getsize(pdf_filename) / 1024:.1f} KB")
