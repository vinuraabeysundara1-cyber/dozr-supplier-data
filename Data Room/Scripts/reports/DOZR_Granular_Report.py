#!/usr/bin/env python3
"""
DOZR Google Ads — Granular Ad Group × Geo Action Plan PDF
February 3, 2026
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from datetime import datetime
import json, os

OUTPUT_PATH = os.path.expanduser("~/DOZR_Granular_Action_Plan_Feb2026.pdf")
DATA_PATH = os.path.expanduser("~/dozr_granular_data.json")

with open(DATA_PATH) as f:
    data = json.load(f)

adgroup_conv = data['adgroup_conv']
adgroup_metrics = data['adgroup_metrics']
geo_campaign = data['geo_campaign']
city_names = data['city_names']
geo_conv = data['geo_conv']

# ─── Campaign classifications ─────────────────────────────────────────────────

WINNER_CAMPAIGNS = {
    'Search-Demand-Boom-Lifts', 'DSA-AllPages-Tier1-New-US-2',
    'Search-Forklift-Core-Geos-US', 'Search-Excavator-Core-Geos-US',
    'Search-Dozers-Core-Geos-US-V3', 'Search-Loader-Core-Geos-US',
    'Search-Demand-Brand-CA', 'Search-Demand-Brand-US'
}
LOSER_CAMPAIGNS = {
    'Search-Scissor-Lift-Core-Geos-US', 'Search-Telehandler-Core-Geos-US',
    'Search-Scissor-Lift-Core-Geos-CA', 'Search-Backhoe-Core-Geos-US',
    'Search-Excavator-Core-Geos-CA', 'Search-Telehandler-Core-Geos-CA',
    'Search-Loader-Core-Geos-CA'
}

# ─── Helpers: extract deal / call / quote from conversion actions ──────────

def get_deals(actions):
    d = 0; v = 0
    for k, a in actions.items():
        if 'Closed' in k:
            d += a['conv']; v += a['value']
    return d, v

def get_ga4(actions):
    d = 0; v = 0
    for k, a in actions.items():
        if 'GA4' in k or 'Purchase' in k:
            d += a['conv']; v += a['value']
    return d, v

def get_calls(actions):
    c = 0
    for k, a in actions.items():
        if 'Phone' in k or ('Call' in k and 'Qualified' not in k and 'Closed' not in k):
            c += a['conv']
    return c

def get_quotes(actions):
    q = 0
    for k, a in actions.items():
        if 'Quote' in k:
            q += a['conv']
    return q

def city_label(city_id):
    if city_id in city_names:
        cn = city_names[city_id]
        # Extract state/province from canonical name
        parts = cn['canonical'].split(',')
        if len(parts) >= 3:
            return f"{cn['name']}, {parts[1].strip()}"
        elif len(parts) >= 2:
            return f"{cn['name']}, {parts[1].strip()}"
        return cn['name']
    return f"ID:{city_id}"

def city_country(city_id):
    if city_id in city_names:
        return city_names[city_id]['country']
    return '??'

# ─── Build enriched data structures ───────────────────────────────────────────

# Enriched ad groups
adgroups = {}
for key, m in adgroup_metrics.items():
    ag = dict(m)
    if key in adgroup_conv:
        ag['actions'] = adgroup_conv[key]['actions']
    else:
        ag['actions'] = {}
    ag['deals'], ag['deal_value'] = get_deals(ag['actions'])
    ag['ga4_conv'], ag['ga4_value'] = get_ga4(ag['actions'])
    ag['calls'] = get_calls(ag['actions'])
    ag['quotes'] = get_quotes(ag['actions'])
    ag['total_rev'] = ag['deal_value'] + ag['ga4_value']
    ag['roas'] = ag['total_rev'] / ag['spend'] if ag['spend'] > 0 else 0
    ag['deal_roas'] = ag['deal_value'] / ag['spend'] if ag['spend'] > 0 else 0
    adgroups[key] = ag

# Enriched geo × campaign
geo_enriched = {}
for key, g in geo_campaign.items():
    ge = dict(g)
    if key in geo_conv:
        ge['actions'] = geo_conv[key]['actions']
    else:
        ge['actions'] = {}
    ge['deals'], ge['deal_value'] = get_deals(ge['actions'])
    ge['ga4_conv'], ge['ga4_value'] = get_ga4(ge['actions'])
    ge['calls'] = get_calls(ge['actions'])
    ge['quotes'] = get_quotes(ge['actions'])
    ge['total_rev'] = ge['deal_value'] + ge['ga4_value']
    ge['roas'] = ge['total_rev'] / ge['spend'] if ge['spend'] > 0 else 0
    ge['city_name'] = city_label(ge['city_id'])
    ge['country'] = city_country(ge['city_id'])
    geo_enriched[key] = ge

# Group data by campaign
campaigns = {}
for key, ag in adgroups.items():
    cname = ag['campaign_name']
    if cname not in campaigns:
        campaigns[cname] = {'adgroups': [], 'geos': [], 'campaign_id': ag['campaign_id']}
    campaigns[cname]['adgroups'].append(ag)

for key, ge in geo_enriched.items():
    cname = ge['campaign_name']
    if cname not in campaigns:
        campaigns[cname] = {'adgroups': [], 'geos': [], 'campaign_id': ge['campaign_id']}
    campaigns[cname]['geos'].append(ge)

# Sort ad groups by spend desc, geos by spend desc
for c in campaigns.values():
    c['adgroups'].sort(key=lambda x: x['spend'], reverse=True)
    c['geos'].sort(key=lambda x: x['spend'], reverse=True)

# ─── Styles ───────────────────────────────────────────────────────────────────

styles = getSampleStyleSheet()
ACCENT = colors.HexColor('#1a1a2e')
ACCENT_LIGHT = colors.HexColor('#e8e8f0')
GREEN = colors.HexColor('#27ae60')
GREEN_LIGHT = colors.HexColor('#eafaf1')
RED = colors.HexColor('#c0392b')
RED_LIGHT = colors.HexColor('#fdedec')
ORANGE = colors.HexColor('#e67e22')
ORANGE_LIGHT = colors.HexColor('#fef9e7')
GRAY_LIGHT = colors.HexColor('#f5f5f5')
GRAY_MED = colors.HexColor('#dddddd')
WHITE = colors.white

for name, font, size, leading, clr, align, sb, sa in [
    ('CoverTitle', 'Helvetica-Bold', 30, 36, '#1a1a2e', TA_LEFT, 0, 4),
    ('CoverSub', 'Helvetica', 13, 18, '#4a4a6a', TA_LEFT, 0, 3),
    ('SectionH', 'Helvetica-Bold', 17, 22, '#1a1a2e', TA_LEFT, 20, 8),
    ('SubH', 'Helvetica-Bold', 12, 16, '#2d2d5e', TA_LEFT, 14, 5),
    ('SubH2', 'Helvetica-Bold', 10, 14, '#3d3d7e', TA_LEFT, 8, 3),
    ('Body', 'Helvetica', 9, 13, '#2a2a2a', TA_JUSTIFY, 0, 5),
    ('Callout', 'Helvetica-Bold', 9, 13, '#c0392b', TA_LEFT, 4, 4),
    ('CalloutG', 'Helvetica-Bold', 9, 13, '#27ae60', TA_LEFT, 4, 4),
    ('TNote', 'Helvetica-Oblique', 7.5, 10, '#666666', TA_LEFT, 0, 6),
    ('BulletCustom', 'Helvetica', 9, 13, '#2a2a2a', TA_LEFT, 0, 2),
    ('ActionH', 'Helvetica-Bold', 9, 12, '#ffffff', TA_LEFT, 0, 0),
    ('SmallB', 'Helvetica-Bold', 8, 11, '#2a2a2a', TA_LEFT, 0, 0),
]:
    styles.add(ParagraphStyle(name=name, fontName=font, fontSize=size, leading=leading,
        textColor=colors.HexColor(clr), alignment=align, spaceBefore=sb, spaceAfter=sa))

styles['BulletCustom'].leftIndent = 20
styles['BulletCustom'].bulletIndent = 10

def section_line():
    return HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceBefore=2, spaceAfter=6)

def thin_line():
    return HRFlowable(width="100%", thickness=0.5, color=GRAY_MED, spaceBefore=3, spaceAfter=3)

def bullet(text):
    return Paragraph(f'<bullet>&bull;</bullet> {text}', styles['BulletCustom'])

def make_table(headers, rows, col_widths=None, highlight_last=False, row_colors=None):
    header_ps = ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=7, leading=9, textColor=WHITE)
    td_ps_l = ParagraphStyle('tdl', fontName='Helvetica', fontSize=7, leading=9.5, textColor=colors.HexColor('#2a2a2a'), alignment=TA_LEFT)
    td_ps_r = ParagraphStyle('tdr', fontName='Helvetica', fontSize=7, leading=9.5, textColor=colors.HexColor('#2a2a2a'), alignment=TA_RIGHT)
    td_ps_b = ParagraphStyle('tdb', fontName='Helvetica-Bold', fontSize=7, leading=9.5, textColor=colors.HexColor('#2a2a2a'), alignment=TA_LEFT)

    right_cols = {'Spend', 'Clicks', 'Impr', 'Phone', 'Quote', 'Deals', 'Deal$', 'GA4$', 'ROAS', 'Deal ROAS',
                  'Conv', 'Value', 'Monthly Waste', 'Budget Impact', '30d Spend', 'ImpShare'}

    data = [[Paragraph(f'<b>{h}</b>', header_ps) for h in headers]]
    for row in rows:
        styled = []
        for i, cell in enumerate(row):
            if isinstance(cell, Paragraph):
                styled.append(cell)
            elif i == 0 or headers[i] in ('Action', 'Verdict', 'Reason', 'City', 'Ad Group', 'Campaign', 'Rationale', 'Status'):
                styled.append(Paragraph(str(cell), td_ps_l))
            elif headers[i] in right_cols:
                styled.append(Paragraph(str(cell), td_ps_r))
            else:
                styled.append(Paragraph(str(cell), td_ps_l))
        data.append(styled)

    t = Table(data, colWidths=col_widths, repeatRows=1)
    cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), ACCENT),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 7),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
        ('TOPPADDING', (0, 0), (-1, 0), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
        ('TOPPADDING', (0, 1), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.4, GRAY_MED),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            cmds.append(('BACKGROUND', (0, i), (-1, i), GRAY_LIGHT))
    if highlight_last:
        cmds.append(('BACKGROUND', (0, -1), (-1, -1), ACCENT_LIGHT))
        cmds.append(('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'))
    if row_colors:
        for idx, clr in row_colors.items():
            if idx + 1 < len(data):
                cmds.append(('BACKGROUND', (0, idx + 1), (-1, idx + 1), clr))
    t.setStyle(TableStyle(cmds))
    return t

def on_page(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(ACCENT)
    canvas.setLineWidth(0.5)
    canvas.line(50, letter[1] - 45, letter[0] - 50, letter[1] - 45)
    canvas.setFont('Helvetica', 6.5)
    canvas.setFillColor(colors.HexColor('#999999'))
    canvas.drawString(50, letter[1] - 41, "DOZR — Granular Ad Group & Geo Action Plan — February 2026")
    canvas.drawRightString(letter[0] - 50, letter[1] - 41, "Confidential")
    canvas.drawCentredString(letter[0] / 2, 34, f"Page {doc.page}")
    canvas.line(50, 44, letter[0] - 50, 44)
    canvas.restoreState()

def on_first(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(ACCENT)
    canvas.rect(0, letter[1] - 7, letter[0], 7, fill=1, stroke=0)
    canvas.rect(0, 0, letter[0], 3, fill=1, stroke=0)
    canvas.restoreState()

# ─── Build document ───────────────────────────────────────────────────────────

doc = SimpleDocTemplate(OUTPUT_PATH, pagesize=letter,
    topMargin=0.65*inch, bottomMargin=0.65*inch, leftMargin=0.65*inch, rightMargin=0.65*inch)

story = []

# ═══ COVER ═══
story.append(Spacer(1, 1.2*inch))
story.append(Paragraph("DOZR Google Ads", styles['CoverTitle']))
story.append(Paragraph("Granular Action Plan", styles['CoverTitle']))
story.append(Spacer(1, 0.2*inch))
story.append(HRFlowable(width="35%", thickness=3, color=ACCENT, spaceBefore=0, spaceAfter=12))
story.append(Paragraph("Ad Group × Geography Optimization — Specific Changes to Make", styles['CoverSub']))
story.append(Paragraph(f"Report Date: {datetime.now().strftime('%B %d, %Y')}", styles['CoverSub']))
story.append(Paragraph("Period: January 4 — February 3, 2026 (30 Days)", styles['CoverSub']))
story.append(Paragraph("Google Ads Customer ID: 853-189-6842", styles['CoverSub']))

story.append(Spacer(1, 0.8*inch))
story.append(Paragraph(
    "This report provides <b>specific, actionable changes</b> at the ad group and city level for each campaign. "
    "Rather than campaign-level budget moves, this document identifies exactly which ad groups within which "
    "campaigns to increase, decrease, or pause — and which geographic locations to bid up or suppress — based on "
    "30-day Closed Won Deal data cross-referenced with DOZR's supplier fulfillment capability.",
    styles['Body']
))

story.append(Spacer(1, 0.6*inch))
toc_s = ParagraphStyle('tocs', fontName='Helvetica', fontSize=10, leading=17, textColor=colors.HexColor('#4a4a6a'))
story.append(Paragraph('<b>Contents</b>', ParagraphStyle('toch', fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=ACCENT, spaceAfter=6)))
toc_items = [
    "Master Action Summary — Every Change in One Table",
    "Search-Demand-Boom-Lifts — Ad Group & Geo Breakdown",
    "DSA-AllPages-Tier1-New-US-2 — Ad Group & Geo Breakdown",
    "Search-Dozers-Core-Geos-US-V3 — Ad Group & Geo Breakdown",
    "Search-Excavator-Core-Geos-US — Ad Group & Geo Breakdown",
    "Search-Forklift-Core-Geos-US — Ad Group & Geo Breakdown",
    "Search-Loader-Core-Geos-US — Ad Group & Geo Breakdown",
    "Brand Campaigns — Ad Group & Geo Breakdown",
    "Losing Campaigns — Complete Pause Recommendations",
    "City-Level Action Table — All Geo Bid Adjustments",
]
for i, s in enumerate(toc_items, 1):
    story.append(Paragraph(f'{i}.&nbsp;&nbsp;&nbsp;{s}', toc_s))

story.append(PageBreak())

# ═══ 1. MASTER ACTION SUMMARY ═══
story.append(Paragraph("1. Master Action Summary", styles['SectionH']))
story.append(section_line())
story.append(Paragraph(
    "The table below lists every specific change recommended, organized by priority. Each action specifies the "
    "exact campaign, ad group, or city to modify, the type of change, and the data supporting it.",
    styles['Body']
))

# Build master actions list
master_actions = []

# --- PHASE 1: Pause entire loser campaigns ---
loser_list = [
    ('Search-Scissor-Lift-Core-Geos-US', '$350/day', '$3,954', '1.0', '$623', "Can't source scissor lifts"),
    ('Search-Scissor-Lift-Core-Geos-CA', '$120/day', '$1,457', '0.0', '$0', 'No CA scissor lift supply'),
    ('Search-Telehandler-Core-Geos-US', '$100/day', '$1,863', '0.0', '$0', 'Zero deals; no telehandler supply'),
    ('Search-Telehandler-Core-Geos-CA', '$100/day', '$1,121', '0.0', '$0', 'No CA telehandler supply'),
    ('Search-Backhoe-Core-Geos-US', '$100/day', '$1,430', '0.3', '$444', 'Near-zero deals; sourcing failures'),
    ('Search-Excavator-Core-Geos-CA', '$100/day', '$1,208', '0.0', '$0', 'No CA excavator supply'),
    ('Search-Loader-Core-Geos-CA', '$80/day', '$981', '0.0', '$0', 'Zero deals; weak CA supply'),
]

story.append(Paragraph("Phase 1: Pause Entire Loser Campaigns (saves $950/day = $28,500/month)", styles['SubH']))

p1_headers = ['Campaign', 'Daily Budget', '30d Spend', 'Deals', 'Deal$', 'Action', 'Reason']
p1_rows = []
for name, budget, spend, deals, rev, reason in loser_list:
    p1_rows.append([name, budget, spend, deals, rev, 'PAUSE', reason])

story.append(make_table(p1_headers, p1_rows,
    col_widths=[1.85*inch, 0.6*inch, 0.6*inch, 0.4*inch, 0.5*inch, 0.5*inch, 1.95*inch],
    row_colors={i: RED_LIGHT for i in range(len(p1_rows))}))

story.append(Spacer(1, 0.1*inch))

# --- PHASE 2: Pause/reduce ad groups within winners ---
story.append(Paragraph("Phase 2: Pause Non-Converting Ad Groups Within Winners (redirects ~$5,400/month)", styles['SubH']))

p2_actions = []
# Build from actual data
for cname in WINNER_CAMPAIGNS:
    if cname not in campaigns:
        continue
    for ag in campaigns[cname]['adgroups']:
        if ag['spend'] >= 50 and ag['deals'] == 0 and ag['deal_value'] == 0 and ag['ga4_value'] == 0:
            action = 'PAUSE' if ag['spend'] >= 100 else 'REDUCE'
            p2_actions.append({
                'campaign': cname, 'adgroup': ag['adgroup_name'],
                'spend': ag['spend'], 'calls': ag['calls'], 'quotes': ag['quotes'],
                'deals': ag['deals'], 'action': action,
                'reason': f"{ag['calls']:.0f} calls, {ag['quotes']:.0f} quotes, 0 deals"
            })

p2_actions.sort(key=lambda x: x['spend'], reverse=True)

p2_headers = ['Campaign', 'Ad Group', 'Spend', 'Phone', 'Quote', 'Deals', 'Action', 'Reason']
p2_rows = []
total_p2_waste = 0
for a in p2_actions:
    short_camp = a['campaign'].replace('Search-', '').replace('Core-Geos-', '').replace('-Demand-', '-')
    p2_rows.append([short_camp, a['adgroup'], f"${a['spend']:,.0f}", f"{a['calls']:.0f}",
                    f"{a['quotes']:.0f}", f"{a['deals']:.1f}", a['action'], a['reason']])
    total_p2_waste += a['spend']

p2_rows.append(['TOTAL REDIRECTED', '', f'${total_p2_waste:,.0f}', '', '', '', '', 'Flows to top ad groups'])

story.append(make_table(p2_headers, p2_rows,
    col_widths=[1.3*inch, 1.2*inch, 0.5*inch, 0.4*inch, 0.4*inch, 0.4*inch, 0.5*inch, 1.5*inch],
    highlight_last=True,
    row_colors={i: RED_LIGHT for i in range(len(p2_rows)-1)}))

story.append(Spacer(1, 0.1*inch))

# --- PHASE 3: Increase winning ad groups ---
story.append(Paragraph("Phase 3: Increase Budget on Top-Performing Ad Groups", styles['SubH']))

p3_actions = []
for cname in WINNER_CAMPAIGNS:
    if cname not in campaigns:
        continue
    for ag in campaigns[cname]['adgroups']:
        if ag['deals'] >= 1.0 and ag['deal_roas'] >= 2.0:
            imp_share = ag.get('imp_share')
            headroom = f"{(1-imp_share)*100:.0f}% headroom" if imp_share and imp_share < 0.95 else "Check IS"
            p3_actions.append({
                'campaign': cname, 'adgroup': ag['adgroup_name'],
                'spend': ag['spend'], 'deals': ag['deals'], 'deal_value': ag['deal_value'],
                'roas': ag['deal_roas'], 'imp_share': imp_share, 'headroom': headroom
            })

p3_actions.sort(key=lambda x: x['roas'], reverse=True)

p3_headers = ['Campaign', 'Ad Group', 'Spend', 'Deals', 'Deal$', 'Deal ROAS', 'Action', 'ImpShare']
p3_rows = []
for a in p3_actions:
    short_camp = a['campaign'].replace('Search-', '').replace('Core-Geos-', '').replace('-Demand-', '-')
    is_str = f"{a['imp_share']*100:.0f}%" if a['imp_share'] else '—'
    p3_rows.append([short_camp, a['adgroup'], f"${a['spend']:,.0f}", f"{a['deals']:.1f}",
                    f"${a['deal_value']:,.0f}", f"{a['roas']:.1f}x", 'INCREASE', is_str])

story.append(make_table(p3_headers, p3_rows,
    col_widths=[1.3*inch, 1.4*inch, 0.55*inch, 0.4*inch, 0.65*inch, 0.6*inch, 0.6*inch, 0.6*inch],
    row_colors={i: GREEN_LIGHT for i in range(len(p3_rows))}))

story.append(Paragraph(
    "These ad groups have proven deal-closing ability with ROAS above 2x. Budget freed from paused ad groups "
    "and loser campaigns should flow primarily to these ad groups. Impression Share shows how much room each "
    "has to scale — lower IS means more headroom for additional spend.",
    styles['TNote']
))

story.append(PageBreak())

# ═══ CAMPAIGN-BY-CAMPAIGN DEEP DIVES ═══

# Define campaign order with display names
campaign_order = [
    ('Search-Demand-Boom-Lifts', '2. Search-Demand-Boom-Lifts'),
    ('DSA-AllPages-Tier1-New-US-2', '3. DSA-AllPages-Tier1-New-US-2'),
    ('Search-Dozers-Core-Geos-US-V3', '4. Search-Dozers-Core-Geos-US-V3'),
    ('Search-Excavator-Core-Geos-US', '5. Search-Excavator-Core-Geos-US'),
    ('Search-Forklift-Core-Geos-US', '6. Search-Forklift-Core-Geos-US'),
    ('Search-Loader-Core-Geos-US', '7. Search-Loader-Core-Geos-US'),
]

for cname, section_title in campaign_order:
    if cname not in campaigns:
        continue

    camp = campaigns[cname]
    ags = camp['adgroups']
    geos = camp['geos']

    # Campaign totals
    total_spend = sum(a['spend'] for a in ags)
    total_deals = sum(a['deals'] for a in ags)
    total_deal_val = sum(a['deal_value'] for a in ags)
    total_ga4 = sum(a['ga4_value'] for a in ags)

    story.append(Paragraph(section_title, styles['SectionH']))
    story.append(section_line())

    story.append(Paragraph(
        f"<b>Campaign Total (30d):</b> ${total_spend:,.0f} spend | {total_deals:.1f} closed deals | "
        f"${total_deal_val:,.0f} deal revenue | ${total_ga4:,.0f} GA4 revenue | "
        f"{(total_deal_val/total_spend if total_spend > 0 else 0):.2f}x deal ROAS",
        styles['Body']
    ))

    # ── Ad Group Table with Actions ──
    story.append(Paragraph("Ad Group Performance & Actions", styles['SubH']))

    ag_headers = ['Ad Group', 'Status', 'Spend', 'Phone', 'Quote', 'Deals', 'Deal$', 'GA4$', 'ROAS', 'Action']
    ag_rows = []
    ag_colors = {}

    for i, ag in enumerate(ags):
        status = 'ON' if ag['status'] == 'ENABLED' else 'OFF'
        roas_val = ag['deal_roas']
        roas_str = f"{roas_val:.1f}x" if roas_val > 0 else '0.0x'

        # Determine action
        if ag['deals'] >= 1.0 and roas_val >= 2.0:
            action = 'INCREASE'
            ag_colors[i] = GREEN_LIGHT
        elif ag['deals'] >= 0.5 or (ag['ga4_value'] > 500 and ag['spend'] > 100):
            action = 'MAINTAIN'
            ag_colors[i] = ORANGE_LIGHT
        elif ag['spend'] >= 100 and ag['deals'] == 0 and ag['deal_value'] == 0 and ag['ga4_value'] == 0:
            action = 'PAUSE'
            ag_colors[i] = RED_LIGHT
        elif ag['spend'] >= 50 and ag['deals'] == 0 and ag['deal_value'] == 0 and ag['ga4_value'] == 0:
            action = 'REDUCE'
            ag_colors[i] = RED_LIGHT
        elif ag['spend'] < 50:
            action = 'MONITOR'
        else:
            action = 'MONITOR'

        ag_rows.append([
            ag['adgroup_name'], status, f"${ag['spend']:,.0f}",
            f"{ag['calls']:.0f}", f"{ag['quotes']:.0f}", f"{ag['deals']:.1f}",
            f"${ag['deal_value']:,.0f}", f"${ag['ga4_value']:,.0f}", roas_str, action
        ])

    story.append(make_table(ag_headers, ag_rows,
        col_widths=[1.4*inch, 0.35*inch, 0.5*inch, 0.4*inch, 0.4*inch, 0.4*inch, 0.55*inch, 0.5*inch, 0.45*inch, 0.6*inch],
        row_colors=ag_colors))
    story.append(Paragraph("Green = Increase spend | Orange = Maintain | Red = Pause or reduce", styles['TNote']))

    # ── Top Cities for this campaign ──
    story.append(Paragraph("Top Cities — With Deal Revenue (Bid Up)", styles['SubH2']))

    # Cities with deals
    deal_cities = [g for g in geos if g['deal_value'] > 0 and g['spend'] >= 10]
    deal_cities.sort(key=lambda x: x['deal_value'], reverse=True)

    if deal_cities:
        gc_headers = ['City', 'Spend', 'Clicks', 'Deals', 'Deal$', 'ROAS', 'Action']
        gc_rows = []
        for g in deal_cities[:12]:
            r = g['deal_value'] / g['spend'] if g['spend'] > 0 else 0
            bid_adj = '+25%' if r >= 5 else '+20%' if r >= 3 else '+15%' if r >= 1.5 else '+10%'
            gc_rows.append([g['city_name'], f"${g['spend']:,.0f}", f"{g['clicks']}", f"{g['deals']:.1f}",
                           f"${g['deal_value']:,.0f}", f"{r:.1f}x", f"Bid {bid_adj}"])
        story.append(make_table(gc_headers, gc_rows,
            col_widths=[1.6*inch, 0.55*inch, 0.45*inch, 0.4*inch, 0.65*inch, 0.5*inch, 0.7*inch],
            row_colors={i: GREEN_LIGHT for i in range(len(gc_rows))}))
    else:
        story.append(Paragraph("No cities with deal revenue in this campaign.", styles['Body']))

    # Cities wasting money
    waste_cities = [g for g in geos if g['spend'] >= 40 and g['deal_value'] == 0 and g['ga4_value'] == 0]
    waste_cities.sort(key=lambda x: x['spend'], reverse=True)

    if waste_cities[:8]:
        story.append(Paragraph("Cities Wasting Budget — $40+ Spend, Zero Revenue (Bid Down or Exclude)", styles['SubH2']))
        wc_headers = ['City', 'Spend', 'Clicks', 'Conv', 'Value', 'Action']
        wc_rows = []
        for g in waste_cities[:8]:
            action = 'EXCLUDE' if g['spend'] >= 100 else 'Bid -30%' if g['spend'] >= 60 else 'Bid -20%'
            wc_rows.append([g['city_name'], f"${g['spend']:,.0f}", f"{g['clicks']}",
                           f"{g['conversions']:.0f}", '$0', action])
        story.append(make_table(wc_headers, wc_rows,
            col_widths=[1.8*inch, 0.6*inch, 0.5*inch, 0.45*inch, 0.5*inch, 0.7*inch],
            row_colors={i: RED_LIGHT for i in range(len(wc_rows))}))

    story.append(PageBreak())

# ═══ 8. BRAND CAMPAIGNS ═══
story.append(Paragraph("8. Brand Campaigns", styles['SectionH']))
story.append(section_line())

for cname in ['Search-Demand-Brand-CA', 'Search-Demand-Brand-US']:
    if cname not in campaigns:
        continue
    camp = campaigns[cname]
    ags = camp['adgroups']
    geos = camp['geos']

    total_spend = sum(a['spend'] for a in ags)
    total_deals = sum(a['deals'] for a in ags)
    total_deal_val = sum(a['deal_value'] for a in ags)
    total_ga4 = sum(a['ga4_value'] for a in ags)

    story.append(Paragraph(f"{cname}", styles['SubH']))
    story.append(Paragraph(
        f"${total_spend:,.0f} spend | {total_deals:.1f} deals | ${total_deal_val:,.0f} deal rev | "
        f"${total_ga4:,.0f} GA4 rev",
        styles['Body']
    ))

    # Top cities
    deal_cities = [g for g in geos if (g['deal_value'] > 0 or g['ga4_value'] > 0) and g['spend'] >= 5]
    deal_cities.sort(key=lambda x: x['total_rev'], reverse=True)

    if deal_cities:
        gc_headers = ['City', 'Spend', 'Clicks', 'Total Value', 'Action']
        gc_rows = []
        for g in deal_cities[:6]:
            gc_rows.append([g['city_name'], f"${g['spend']:,.0f}", f"{g['clicks']}",
                           f"${g['total_rev']:,.0f}", 'MAINTAIN'])
        story.append(make_table(gc_headers, gc_rows,
            col_widths=[2*inch, 0.7*inch, 0.6*inch, 0.8*inch, 0.8*inch]))

    story.append(Paragraph(
        f"Recommendation: {'MAINTAIN' if total_deals > 0 else 'MAINTAIN for brand defense'}. "
        f"Brand campaigns protect against competitors bidding on DOZR's name.",
        styles['Body']
    ))

story.append(PageBreak())

# ═══ 9. LOSING CAMPAIGNS — DETAILED PAUSE RECS ═══
story.append(Paragraph("9. Losing Campaigns — Complete Pause Recommendations", styles['SectionH']))
story.append(section_line())

story.append(Paragraph(
    "Each losing campaign is shown with its ad group and city-level data to demonstrate that the problem is "
    "systemic (not isolated to one ad group or city). The recommendation for all 7 campaigns is: <b>PAUSE ENTIRELY</b>. "
    "The supplier network cannot fulfill orders for these equipment types/geographies.",
    styles['Body']
))

for cname in sorted(LOSER_CAMPAIGNS):
    if cname not in campaigns:
        continue

    camp = campaigns[cname]
    ags = camp['adgroups']
    geos = camp['geos']

    total_spend = sum(a['spend'] for a in ags)
    total_deals = sum(a['deals'] for a in ags)
    total_deal_val = sum(a['deal_value'] for a in ags)
    total_calls = sum(a['calls'] for a in ags)
    total_quotes = sum(a['quotes'] for a in ags)

    short_name = cname.replace('Search-', '').replace('-Core-Geos-', ' ')
    story.append(Paragraph(f"{short_name} — PAUSE ALL", styles['SubH']))
    story.append(Paragraph(
        f"${total_spend:,.0f} spend | {total_calls:.0f} phone calls | {total_quotes:.0f} quotes | "
        f"{total_deals:.1f} deals | ${total_deal_val:,.0f} revenue",
        styles['Body']
    ))

    ag_headers = ['Ad Group', 'Spend', 'Phone', 'Quote', 'Deals', 'Deal$', 'Action']
    ag_rows = []
    for ag in ags:
        if ag['spend'] >= 10:
            ag_rows.append([ag['adgroup_name'], f"${ag['spend']:,.0f}", f"{ag['calls']:.0f}",
                           f"{ag['quotes']:.0f}", f"{ag['deals']:.1f}", f"${ag['deal_value']:,.0f}", 'PAUSE'])

    if ag_rows:
        story.append(make_table(ag_headers, ag_rows,
            col_widths=[1.6*inch, 0.6*inch, 0.5*inch, 0.5*inch, 0.45*inch, 0.6*inch, 0.55*inch],
            row_colors={i: RED_LIGHT for i in range(len(ag_rows))}))

    # Show top cities to illustrate the waste
    top_waste_cities = [g for g in geos if g['spend'] >= 20]
    top_waste_cities.sort(key=lambda x: x['spend'], reverse=True)
    if top_waste_cities[:5]:
        city_str = ", ".join(f"{g['city_name']} (${g['spend']:,.0f})" for g in top_waste_cities[:5])
        story.append(Paragraph(f"<i>Top cities burning budget: {city_str}</i>", styles['TNote']))

    story.append(Spacer(1, 0.05*inch))

story.append(PageBreak())

# ═══ 10. CITY-LEVEL ACTION TABLE ═══
story.append(Paragraph("10. City-Level Action Table — All Geo Bid Adjustments", styles['SectionH']))
story.append(section_line())

story.append(Paragraph(
    "This table aggregates city performance across all winning campaigns and provides specific bid adjustment "
    "recommendations. Once loser campaigns are paused, these adjustments apply to the remaining winner campaigns.",
    styles['Body']
))

# Aggregate cities across WINNER campaigns only
city_agg = {}
for key, ge in geo_enriched.items():
    if ge['campaign_name'] not in WINNER_CAMPAIGNS:
        continue
    cid = ge['city_id']
    if cid not in city_agg:
        city_agg[cid] = {'city_name': ge['city_name'], 'country': ge['country'],
                         'spend': 0, 'clicks': 0, 'deals': 0, 'deal_value': 0,
                         'ga4_value': 0, 'calls': 0, 'quotes': 0, 'campaigns': set()}
    city_agg[cid]['spend'] += ge['spend']
    city_agg[cid]['clicks'] += ge['clicks']
    city_agg[cid]['deals'] += ge['deals']
    city_agg[cid]['deal_value'] += ge['deal_value']
    city_agg[cid]['ga4_value'] += ge['ga4_value']
    city_agg[cid]['calls'] += ge['calls']
    city_agg[cid]['quotes'] += ge['quotes']
    city_agg[cid]['campaigns'].add(ge['campaign_name'])

# Cities to bid UP (have deal revenue)
story.append(Paragraph("Cities to Bid UP (Deal Revenue Producing)", styles['SubH']))

bid_up = [(cid, c) for cid, c in city_agg.items() if c['deal_value'] > 0 and c['spend'] >= 20]
bid_up.sort(key=lambda x: x[1]['deal_value'], reverse=True)

bu_headers = ['City', 'Country', 'Spend', 'Deals', 'Deal$', 'GA4$', 'Deal ROAS', 'Bid Adj', '# Campaigns']
bu_rows = []
for cid, c in bid_up[:25]:
    r = c['deal_value'] / c['spend'] if c['spend'] > 0 else 0
    bid = '+25%' if r >= 8 else '+20%' if r >= 4 else '+15%' if r >= 2 else '+10%'
    bu_rows.append([c['city_name'], c['country'], f"${c['spend']:,.0f}", f"{c['deals']:.1f}",
                   f"${c['deal_value']:,.0f}", f"${c['ga4_value']:,.0f}", f"{r:.1f}x", bid,
                   str(len(c['campaigns']))])

story.append(make_table(bu_headers, bu_rows,
    col_widths=[1.3*inch, 0.4*inch, 0.5*inch, 0.4*inch, 0.55*inch, 0.5*inch, 0.55*inch, 0.5*inch, 0.6*inch],
    row_colors={i: GREEN_LIGHT for i in range(len(bu_rows))}))

story.append(Spacer(1, 0.1*inch))

# Cities to bid DOWN or EXCLUDE (high spend, zero revenue)
story.append(Paragraph("Cities to Bid DOWN or Exclude (Zero Revenue, $50+ Spend)", styles['SubH']))

bid_down = [(cid, c) for cid, c in city_agg.items()
            if c['deal_value'] == 0 and c['ga4_value'] == 0 and c['spend'] >= 50]
bid_down.sort(key=lambda x: x[1]['spend'], reverse=True)

bd_headers = ['City', 'Country', 'Spend', 'Clicks', 'Calls', 'Quotes', 'Deals', 'Action']
bd_rows = []
for cid, c in bid_down[:20]:
    action = 'EXCLUDE' if c['spend'] >= 150 else 'Bid -30%' if c['spend'] >= 80 else 'Bid -20%'
    bd_rows.append([c['city_name'], c['country'], f"${c['spend']:,.0f}", f"{c['clicks']}",
                   f"{c['calls']:.0f}", f"{c['quotes']:.0f}", f"{c['deals']:.1f}", action])

story.append(make_table(bd_headers, bd_rows,
    col_widths=[1.4*inch, 0.45*inch, 0.55*inch, 0.45*inch, 0.45*inch, 0.5*inch, 0.45*inch, 0.65*inch],
    row_colors={i: RED_LIGHT for i in range(len(bd_rows))}))

story.append(Spacer(1, 0.15*inch))

# ── Final summary ──
story.append(Paragraph("Summary of All Changes", styles['SubH']))

# Count actions
n_camp_pause = len(loser_list)
n_ag_pause = len([a for a in p2_actions if a['action'] == 'PAUSE'])
n_ag_reduce = len([a for a in p2_actions if a['action'] == 'REDUCE'])
n_ag_increase = len(p3_actions)
n_city_up = len(bu_rows)
n_city_down = len(bd_rows)

summary_headers = ['Action Type', 'Count', 'Monthly Impact']
summary_rows = [
    ['Campaigns to PAUSE', str(n_camp_pause), f'Saves $28,500/mo (freed for reallocation)'],
    ['Ad groups to PAUSE within winners', str(n_ag_pause), f'Redirects ~${total_p2_waste:,.0f}/mo to top performers'],
    ['Ad groups to INCREASE', str(n_ag_increase), 'Absorbs freed budget from paused campaigns/ad groups'],
    ['Cities to bid UP', str(n_city_up), 'Concentrates spend in deal-producing metros'],
    ['Cities to bid DOWN or EXCLUDE', str(n_city_down), 'Reduces waste in zero-revenue cities'],
    ['TOTAL ACTIONS', str(n_camp_pause + n_ag_pause + n_ag_reduce + n_ag_increase + n_city_up + n_city_down), ''],
]
story.append(make_table(summary_headers, summary_rows,
    col_widths=[2.0*inch, 0.6*inch, 4.0*inch],
    highlight_last=True))

story.append(Spacer(1, 0.15*inch))
story.append(Paragraph(
    '<b>Net result: Same $3,850/day total budget, but every dollar flows to ad groups and cities that have '
    'proven they can generate closed deals through DOZR\'s supplier network. Projected additional revenue: '
    '$19,000–$55,000/month with zero increase in ad spend.</b>',
    ParagraphStyle('final', fontName='Helvetica-Bold', fontSize=9.5, leading=14,
        textColor=GREEN, spaceBefore=6, spaceAfter=6, alignment=TA_LEFT)
))

story.append(Spacer(1, 0.3*inch))
story.append(HRFlowable(width="100%", thickness=0.5, color=GRAY_MED, spaceBefore=4, spaceAfter=4))
story.append(Paragraph(
    f"Report generated {datetime.now().strftime('%B %d, %Y at %I:%M %p')}. "
    "Data: January 4 — February 3, 2026. Google Ads CID: 853-189-6842. All figures in USD.",
    styles['TNote']
))

# ─── Build ────────────────────────────────────────────────────────────────────

doc.build(story, onFirstPage=on_first, onLaterPages=on_page)
print(f"Report saved to: {OUTPUT_PATH}")
print(f"File size: {os.path.getsize(OUTPUT_PATH) / 1024:.1f} KB")
print(f"Total pages generated successfully.")
