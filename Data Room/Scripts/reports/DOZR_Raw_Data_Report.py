#!/usr/bin/env python3
"""
DOZR Google Ads — Complete Raw Data Report PDF
Pure data — no recommendations, no opinions. Just the facts.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from datetime import datetime
import json, os

OUTPUT_PATH = os.path.expanduser("~/DOZR_Complete_Account_Data_Feb2026.pdf")
DATA_PATH = os.path.expanduser("~/dozr_full_raw_data.json")

with open(DATA_PATH) as f:
    data = json.load(f)

campaigns_raw = data['campaigns']
camp_conv = data['camp_conv']
adgroups_raw = data['adgroups']
ag_conv = data['ag_conv']
ads_raw = data['ads']
ad_conv = data['ad_conv']

# ─── Conversion helpers ──────────────────────────────────────────────────────

def extract_conv(actions):
    """Extract phone calls, calls from ads, qualified calls, quotes, deals, GA4 from actions dict."""
    phone = 0; calls_ads = 0; qual = 0; quotes = 0; deals = 0; deal_val = 0; ga4 = 0; ga4_val = 0
    if not actions:
        return phone, calls_ads, qual, quotes, deals, deal_val, ga4, ga4_val
    for k, v in actions.items():
        if 'Phone' in k:
            phone += v['conv']
        elif 'Calls from' in k:
            calls_ads += v['conv']
        elif 'Qualified' in k:
            qual += v['conv']
        elif 'Quote' in k:
            quotes += v['conv']
        elif 'Closed' in k:
            deals += v['conv']; deal_val += v['value']
        elif 'GA4' in k or 'Purchase' in k:
            ga4 += v['conv']; ga4_val += v['value']
    return phone, calls_ads, qual, quotes, deals, deal_val, ga4, ga4_val

# ─── Styles ───────────────────────────────────────────────────────────────────

styles = getSampleStyleSheet()
ACCENT = colors.HexColor('#1a1a2e')
ACCENT_LIGHT = colors.HexColor('#e8e8f0')
GRAY_LIGHT = colors.HexColor('#f5f5f8')
GRAY_MED = colors.HexColor('#dddddd')
WHITE = colors.white
GREEN_BG = colors.HexColor('#f0faf0')
YELLOW_BG = colors.HexColor('#fefce8')

custom_styles = {
    'Cover': ('Helvetica-Bold', 28, 34, '#1a1a2e', TA_LEFT),
    'CoverSub': ('Helvetica', 12, 17, '#4a4a6a', TA_LEFT),
    'SectH': ('Helvetica-Bold', 16, 21, '#1a1a2e', TA_LEFT),
    'CampH': ('Helvetica-Bold', 13, 18, '#1a1a2e', TA_LEFT),
    'AgH': ('Helvetica-Bold', 10.5, 14, '#2d2d5e', TA_LEFT),
    'AdH': ('Helvetica-Bold', 9, 12, '#3d3d7e', TA_LEFT),
    'Body': ('Helvetica', 8.5, 12, '#2a2a2a', TA_LEFT),
    'Note': ('Helvetica-Oblique', 7, 10, '#888888', TA_LEFT),
    'HeadlineP': ('Helvetica', 7, 9.5, '#333333', TA_LEFT),
}
for name, (font, size, lead, clr, align) in custom_styles.items():
    try:
        styles.add(ParagraphStyle(name=name, fontName=font, fontSize=size, leading=lead,
            textColor=colors.HexColor(clr), alignment=align, spaceAfter=3))
    except KeyError:
        pass

def section_line():
    return HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceBefore=1, spaceAfter=5)

def thin_line():
    return HRFlowable(width="100%", thickness=0.5, color=GRAY_MED, spaceBefore=2, spaceAfter=2)

def make_table(headers, rows, col_widths=None, highlight_last=False, alt_colors=True):
    hps = ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=6.5, leading=8.5, textColor=WHITE, alignment=TA_LEFT)
    tl = ParagraphStyle('tl', fontName='Helvetica', fontSize=6.5, leading=8.5, textColor=colors.HexColor('#2a2a2a'), alignment=TA_LEFT)
    tr = ParagraphStyle('tr', fontName='Helvetica', fontSize=6.5, leading=8.5, textColor=colors.HexColor('#2a2a2a'), alignment=TA_RIGHT)
    tb = ParagraphStyle('tb', fontName='Helvetica-Bold', fontSize=6.5, leading=8.5, textColor=colors.HexColor('#2a2a2a'), alignment=TA_LEFT)

    left_headers = {'Campaign', 'Ad Group', 'Ad ID', 'Status', 'Strength', 'Type', 'Bidding',
                    'Channel', 'Headlines', 'URL', 'Name', 'Active Since'}
    data_out = [[Paragraph(f'<b>{h}</b>', hps) for h in headers]]
    for row in rows:
        styled = []
        for i, cell in enumerate(row):
            if isinstance(cell, Paragraph):
                styled.append(cell)
            elif headers[i] in left_headers or i == 0:
                styled.append(Paragraph(str(cell), tl))
            else:
                styled.append(Paragraph(str(cell), tr))
        data_out.append(styled)

    t = Table(data_out, colWidths=col_widths, repeatRows=1)
    cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), ACCENT),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
        ('TOPPADDING', (0, 0), (-1, 0), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 2.5),
        ('TOPPADDING', (0, 1), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('GRID', (0, 0), (-1, -1), 0.3, GRAY_MED),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]
    if alt_colors:
        for i in range(1, len(data_out)):
            if i % 2 == 0:
                cmds.append(('BACKGROUND', (0, i), (-1, i), GRAY_LIGHT))
    if highlight_last and len(data_out) > 1:
        cmds.append(('BACKGROUND', (0, -1), (-1, -1), ACCENT_LIGHT))
        cmds.append(('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'))
    t.setStyle(TableStyle(cmds))
    return t

def on_page(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(ACCENT); canvas.setLineWidth(0.4)
    canvas.line(45, letter[1]-42, letter[0]-45, letter[1]-42)
    canvas.setFont('Helvetica', 6); canvas.setFillColor(colors.HexColor('#999'))
    canvas.drawString(45, letter[1]-38, "DOZR Google Ads — Complete Account Data — February 2026")
    canvas.drawRightString(letter[0]-45, letter[1]-38, "Confidential — Raw Data Report")
    canvas.drawCentredString(letter[0]/2, 32, f"Page {doc.page}")
    canvas.line(45, 42, letter[0]-45, 42)
    canvas.restoreState()

def on_first(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(ACCENT)
    canvas.rect(0, letter[1]-6, letter[0], 6, fill=1, stroke=0)
    canvas.rect(0, 0, letter[0], 3, fill=1, stroke=0)
    canvas.restoreState()

# ─── Organize data by campaign hierarchy ──────────────────────────────────────

# Sort campaigns: enabled first sorted by spend desc, then paused sorted by spend desc
camp_list = sorted(campaigns_raw.values(), key=lambda x: (0 if x['status']=='ENABLED' else 1, -x['spend']))

# Group ad groups by campaign
ag_by_camp = {}
for key, ag in adgroups_raw.items():
    cid = str(ag['campaign_id'])
    if cid not in ag_by_camp: ag_by_camp[cid] = []
    ag_by_camp[cid].append((key, ag))

# Group ads by ad group
ads_by_ag = {}
for key, ad in ads_raw.items():
    ag_key = f"{ad['campaign_id']}_{ad['adgroup_id']}"
    if ag_key not in ads_by_ag: ads_by_ag[ag_key] = []
    ads_by_ag[ag_key].append((key, ad))

# ─── BUILD PDF ────────────────────────────────────────────────────────────────

doc = SimpleDocTemplate(OUTPUT_PATH, pagesize=letter,
    topMargin=0.6*inch, bottomMargin=0.6*inch, leftMargin=0.55*inch, rightMargin=0.55*inch)

story = []

# ═══ COVER ═══
story.append(Spacer(1, 1.3*inch))
story.append(Paragraph("DOZR Google Ads", styles['Cover']))
story.append(Paragraph("Complete Account Data", styles['Cover']))
story.append(Spacer(1, 0.15*inch))
story.append(HRFlowable(width="30%", thickness=3, color=ACCENT, spaceBefore=0, spaceAfter=10))
story.append(Paragraph("Raw Performance Data — Campaign, Ad Group & Ad Level", styles['CoverSub']))
story.append(Paragraph(f"Report Date: {datetime.now().strftime('%B %d, %Y')}", styles['CoverSub']))
story.append(Paragraph("Period: Last 30 Days (January 4 — February 3, 2026)", styles['CoverSub']))
story.append(Paragraph("Google Ads Customer ID: 853-189-6842", styles['CoverSub']))
story.append(Spacer(1, 0.5*inch))
story.append(Paragraph(
    "This report contains the complete raw performance data for every campaign, ad group, and individual "
    "ad in the DOZR Google Ads account. Conversion data is broken down by type: Phone Calls, Calls from Ads, "
    "Qualified Calls, Quote Requests, Closed Won Deals (with revenue), and GA4 Purchases (with revenue). "
    "No recommendations or opinions are included — this is purely data for decision-making.",
    styles['Body']))

story.append(Spacer(1, 0.3*inch))
story.append(Paragraph(
    f"<b>Account snapshot:</b> {sum(1 for c in camp_list if c['status']=='ENABLED')} enabled campaigns, "
    f"{sum(1 for c in camp_list if c['status']=='PAUSED')} paused | "
    f"{len(adgroups_raw)} ad groups | {len(ads_raw)} ads | "
    f"${sum(c['spend'] for c in camp_list):,.0f} total 30-day spend",
    styles['Body']))

story.append(Spacer(1, 0.6*inch))
# Mini TOC
story.append(Paragraph("<b>Report Structure</b>", ParagraphStyle('toch', fontName='Helvetica-Bold', fontSize=11, leading=14, textColor=ACCENT, spaceAfter=4)))
story.append(Paragraph("For each campaign (sorted by status then spend):", styles['Body']))
story.append(Paragraph("&nbsp;&nbsp;&nbsp;&bull;&nbsp; Campaign summary card: budget, spend, all conversion types, revenue", styles['Body']))
story.append(Paragraph("&nbsp;&nbsp;&nbsp;&bull;&nbsp; All ad groups within that campaign with full metrics", styles['Body']))
story.append(Paragraph("&nbsp;&nbsp;&nbsp;&bull;&nbsp; All individual ads within each ad group: headlines, strength, CTR, conversions, revenue", styles['Body']))

story.append(PageBreak())

# ═══ ACCOUNT OVERVIEW TABLE ═══
story.append(Paragraph("Account Overview — All Campaigns", styles['SectH']))
story.append(section_line())

oh = ['Campaign', 'Status', 'Channel', 'Bidding', 'Budget/Day', 'Spend', 'Clicks', 'Impr',
      'CTR', 'Avg CPC', 'Conv', 'Value', 'Active Since']
orows = []
t_spend = 0; t_clicks = 0; t_impr = 0; t_conv = 0; t_val = 0; t_budget = 0
for c in camp_list:
    status = 'ON' if c['status']=='ENABLED' else 'PAUSED'
    ctr = f"{c['ctr']*100:.1f}%" if c['ctr'] else '—'
    cpc = f"${c['avg_cpc']:.2f}" if c['avg_cpc'] else '—'
    first = c.get('first_activity', '—')
    orows.append([
        c['name'], status, c['channel'][:6], c['bidding'][:12],
        f"${c['daily_budget']:,.0f}", f"${c['spend']:,.0f}", f"{c['clicks']:,}",
        f"{c['impressions']:,}", ctr, cpc,
        f"{c['conversions']:.1f}", f"${c['conv_value']:,.0f}", str(first)
    ])
    t_spend += c['spend']; t_clicks += c['clicks']; t_impr += c['impressions']
    t_conv += c['conversions']; t_val += c['conv_value']; t_budget += c['daily_budget']

orows.append(['TOTAL', '', '', '', f"${t_budget:,.0f}", f"${t_spend:,.0f}", f"{t_clicks:,}",
              f"{t_impr:,}", '', '', f"{t_conv:.1f}", f"${t_val:,.0f}", ''])

story.append(make_table(oh, orows,
    col_widths=[1.7*inch, 0.4*inch, 0.4*inch, 0.55*inch, 0.45*inch, 0.5*inch, 0.4*inch,
                0.45*inch, 0.35*inch, 0.4*inch, 0.35*inch, 0.5*inch, 0.6*inch],
    highlight_last=True))
story.append(Paragraph("Conv = all conversion types combined. Value = all conversion values combined. Active Since = earliest date with impressions in last 365 days.", styles['Note']))

story.append(PageBreak())

# ═══ CAMPAIGN-BY-CAMPAIGN DETAIL ═══

for c_idx, camp in enumerate(camp_list):
    cid = str(camp['id'])
    camp_status = 'ENABLED' if camp['status']=='ENABLED' else 'PAUSED'

    # ── Campaign Header ──
    story.append(Paragraph(f"{camp['name']}", styles['CampH']))
    story.append(thin_line())

    # Campaign summary card
    conv_actions = camp_conv.get(int(cid), camp_conv.get(cid, {}))
    phone, calls_ads, qual, quotes, deals, deal_val, ga4, ga4_val = extract_conv(conv_actions)

    first_date = camp.get('first_activity', '—')
    imp_share = f"{camp['imp_share']*100:.1f}%" if camp.get('imp_share') else '—'

    card_data = [
        ['Status', camp_status, 'Channel', camp['channel'], 'Bidding Strategy', camp['bidding']],
        ['Daily Budget', f"${camp['daily_budget']:,.2f}", '30d Spend', f"${camp['spend']:,.2f}",
         'Active Since', str(first_date)],
        ['Clicks', f"{camp['clicks']:,}", 'Impressions', f"{camp['impressions']:,}",
         'Imp. Share', imp_share],
        ['Avg CTR', f"{camp['ctr']*100:.2f}%", 'Avg CPC', f"${camp['avg_cpc']:.2f}",
         'Total Conv', f"{camp['conversions']:.1f}"],
    ]
    card_ps_label = ParagraphStyle('cl', fontName='Helvetica-Bold', fontSize=7, leading=9,
        textColor=colors.HexColor('#666'))
    card_ps_val = ParagraphStyle('cv', fontName='Helvetica-Bold', fontSize=8, leading=10,
        textColor=colors.HexColor('#1a1a2e'))

    card_rows = []
    for row in card_data:
        card_rows.append([
            Paragraph(row[0], card_ps_label), Paragraph(row[1], card_ps_val),
            Paragraph(row[2], card_ps_label), Paragraph(row[3], card_ps_val),
            Paragraph(row[4], card_ps_label), Paragraph(row[5], card_ps_val),
        ])

    ct = Table(card_rows, colWidths=[0.8*inch, 0.95*inch, 0.8*inch, 0.95*inch, 0.85*inch, 0.95*inch])
    ct.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f8fc')),
        ('BOX', (0, 0), (-1, -1), 0.5, GRAY_MED),
        ('INNERGRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#eee')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(ct)
    story.append(Spacer(1, 0.05*inch))

    # Conversion breakdown
    conv_h = ['Phone Calls', 'Calls from Ads', 'Qualified Calls', 'Quotes', 'Closed Deals', 'Deal Revenue', 'GA4 Purchases', 'GA4 Revenue']
    conv_r = [[f"{phone:.0f}", f"{calls_ads:.0f}", f"{qual:.0f}", f"{quotes:.0f}",
               f"{deals:.1f}", f"${deal_val:,.0f}", f"{ga4:.0f}", f"${ga4_val:,.0f}"]]
    story.append(make_table(conv_h, conv_r,
        col_widths=[0.7*inch, 0.7*inch, 0.7*inch, 0.6*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch],
        alt_colors=False))
    story.append(Spacer(1, 0.08*inch))

    # ── Ad Groups in this campaign ──
    camp_ags = ag_by_camp.get(cid, [])
    camp_ags.sort(key=lambda x: x[1]['spend'], reverse=True)

    if camp_ags:
        story.append(Paragraph(f"Ad Groups ({len(camp_ags)})", styles['AgH']))

        ag_h = ['Ad Group', 'Status', 'Spend', 'Clicks', 'Impr', 'CTR', 'CPC',
                'Phone', 'Calls', 'Qual', 'Quotes', 'Deals', 'Deal$', 'GA4', 'GA4$', 'ImpShare']
        ag_rows = []
        for ag_key, ag in camp_ags:
            ag_actions = ag_conv.get(ag_key, {})
            ph, ca, ql, qt, dl, dv, g4, g4v = extract_conv(ag_actions)
            st = 'ON' if ag['status']=='ENABLED' else 'OFF'
            ctr = f"{ag['ctr']*100:.1f}%" if ag['ctr'] else '—'
            cpc = f"${ag['avg_cpc']:.2f}" if ag['avg_cpc'] else '—'
            iss = f"{ag['imp_share']*100:.0f}%" if ag.get('imp_share') else '—'
            ag_rows.append([
                ag['name'], st, f"${ag['spend']:,.0f}", f"{ag['clicks']:,}",
                f"{ag['impressions']:,}", ctr, cpc,
                f"{ph:.0f}", f"{ca:.0f}", f"{ql:.0f}", f"{qt:.0f}",
                f"{dl:.1f}", f"${dv:,.0f}", f"{g4:.0f}", f"${g4v:,.0f}", iss
            ])

        story.append(make_table(ag_h, ag_rows,
            col_widths=[1.15*inch, 0.28*inch, 0.45*inch, 0.38*inch, 0.42*inch, 0.33*inch, 0.35*inch,
                        0.32*inch, 0.3*inch, 0.28*inch, 0.35*inch, 0.32*inch, 0.45*inch, 0.28*inch, 0.42*inch, 0.42*inch]))
        story.append(Paragraph("Phone=Phone Calls, Calls=Calls from Ads, Qual=Qualified Calls, Quotes=Quote Requested, Deals=Closed Won, GA4=GA4 Purchase", styles['Note']))
    else:
        story.append(Paragraph("No ad groups with data in this period.", styles['Body']))

    story.append(Spacer(1, 0.08*inch))

    # ── Ads within each ad group ──
    for ag_key, ag in camp_ags:
        ag_ads = ads_by_ag.get(ag_key, [])
        if not ag_ads:
            continue

        ag_ads.sort(key=lambda x: x[1]['spend'], reverse=True)

        story.append(Paragraph(f"Ads in: {ag['name']} ({len(ag_ads)} ad{'s' if len(ag_ads)!=1 else ''})", styles['AdH']))

        for ad_key, ad in ag_ads:
            ad_actions = ad_conv.get(ad_key, {})
            ph, ca, ql, qt, dl, dv, g4, g4v = extract_conv(ad_actions)

            # Ad info row
            headlines_str = ' | '.join(ad.get('headlines', [])[:5]) if ad.get('headlines') else '(DSA auto-generated)'
            if len(headlines_str) > 120:
                headlines_str = headlines_str[:117] + '...'
            url = ad['final_urls'][0] if ad.get('final_urls') else '—'
            if len(url) > 60:
                url = url[:57] + '...'

            strength = ad.get('strength', '—').replace('AdStrength.', '')
            ctr = f"{ad['ctr']*100:.1f}%" if ad['ctr'] else '—'
            cpc = f"${ad['avg_cpc']:.2f}" if ad['avg_cpc'] else '—'

            ad_h = ['Ad ID', 'Status', 'Strength', 'Spend', 'Clicks', 'Impr', 'CTR', 'CPC',
                    'Phone', 'Quotes', 'Deals', 'Deal$', 'GA4$']
            ad_r = [[
                str(ad['ad_id']), ad['status'][:3], strength,
                f"${ad['spend']:,.0f}", f"{ad['clicks']:,}", f"{ad['impressions']:,}",
                ctr, cpc, f"{ph:.0f}", f"{qt:.0f}", f"{dl:.1f}", f"${dv:,.0f}", f"${g4v:,.0f}"
            ]]

            story.append(make_table(ad_h, ad_r,
                col_widths=[0.75*inch, 0.3*inch, 0.55*inch, 0.45*inch, 0.38*inch, 0.42*inch,
                            0.35*inch, 0.38*inch, 0.35*inch, 0.38*inch, 0.35*inch, 0.45*inch, 0.42*inch],
                alt_colors=False))

            # Headlines
            story.append(Paragraph(f"<b>Headlines:</b> {headlines_str}", styles['HeadlineP']))
            if url != '—':
                story.append(Paragraph(f"<b>URL:</b> {url}", styles['HeadlineP']))
            story.append(Spacer(1, 0.03*inch))

    # Page break between campaigns (except last)
    if c_idx < len(camp_list) - 1:
        story.append(PageBreak())

# ═══ FINAL SUMMARY PAGE ═══
story.append(PageBreak())
story.append(Paragraph("Account Summary", styles['SectH']))
story.append(section_line())

# Overall totals
total_spend = sum(c['spend'] for c in camp_list)
total_clicks = sum(c['clicks'] for c in camp_list)
total_impr = sum(c['impressions'] for c in camp_list)
total_budget = sum(c['daily_budget'] for c in camp_list if c['status']=='ENABLED')

# Sum all conversion types across all campaigns
all_phone = 0; all_calls = 0; all_qual = 0; all_quotes = 0
all_deals = 0; all_deal_val = 0; all_ga4 = 0; all_ga4_val = 0
for cid_key in camp_conv:
    ph, ca, ql, qt, dl, dv, g4, g4v = extract_conv(camp_conv[cid_key])
    all_phone += ph; all_calls += ca; all_qual += ql; all_quotes += qt
    all_deals += dl; all_deal_val += dv; all_ga4 += g4; all_ga4_val += g4v

summary_h = ['Metric', 'Value']
summary_r = [
    ['Total Campaigns', f"{len(camp_list)} ({sum(1 for c in camp_list if c['status']=='ENABLED')} enabled, {sum(1 for c in camp_list if c['status']=='PAUSED')} paused)"],
    ['Total Ad Groups', f"{len(adgroups_raw)} ({sum(1 for ag in adgroups_raw.values() if ag['status']=='ENABLED')} enabled)"],
    ['Total Ads', f"{len(ads_raw)} ({sum(1 for ad in ads_raw.values() if ad['status']=='ENABLED')} enabled)"],
    ['Daily Budget (Enabled)', f"${total_budget:,.2f}/day (${total_budget*30:,.0f}/month)"],
    ['30-Day Spend', f"${total_spend:,.2f}"],
    ['30-Day Clicks', f"{total_clicks:,}"],
    ['30-Day Impressions', f"{total_impr:,}"],
    ['', ''],
    ['Phone Calls (all campaigns)', f"{all_phone:.0f}"],
    ['Calls from Ads (all campaigns)', f"{all_calls:.0f}"],
    ['Qualified Calls (all campaigns)', f"{all_qual:.0f}"],
    ['Quote Requests (all campaigns)', f"{all_quotes:.0f}"],
    ['Closed Won Deals (all campaigns)', f"{all_deals:.1f}"],
    ['Closed Won Deal Revenue', f"${all_deal_val:,.2f}"],
    ['GA4 Purchases (all campaigns)', f"{all_ga4:.0f}"],
    ['GA4 Purchase Revenue', f"${all_ga4_val:,.2f}"],
    ['', ''],
    ['Total Conversion Value', f"${all_deal_val + all_ga4_val:,.2f}"],
    ['Overall ROAS (all conv value / spend)', f"{(all_deal_val + all_ga4_val)/total_spend:.2f}x" if total_spend > 0 else '—'],
    ['Deal-Only ROAS (deal rev / spend)', f"{all_deal_val/total_spend:.2f}x" if total_spend > 0 else '—'],
]
story.append(make_table(summary_h, summary_r, col_widths=[2.5*inch, 4.0*inch], alt_colors=True))

story.append(Spacer(1, 0.2*inch))

# Conversion action definitions
story.append(Paragraph("Conversion Action Definitions", styles['AgH']))
story.append(Spacer(1, 0.05*inch))
defs_h = ['Conversion Action', 'Source', 'Default Value', 'Description']
defs_r = [
    ['Phone Call', 'Website call tracking', '$0', 'Visitor clicks phone number on DOZR website'],
    ['Calls from Ads', 'Call extension', '$1', 'Visitor calls directly from the Google ad'],
    ['Qualified Calls', 'Offline upload (GCLID)', '$50', 'Calls meeting qualification criteria, uploaded via CRM'],
    ['Quote Requested', 'Offline upload (GCLID)', '$540', 'Customer requests a quote, uploaded via CRM'],
    ['Closed Won Deals', 'Offline upload (GCLID)', '$1,700', 'Deal closed and revenue recorded, uploaded via CRM'],
    ['GA4 Purchase', 'GA4 import', 'Actual value', 'Purchase completed on website, tracked via GA4'],
]
story.append(make_table(defs_h, defs_r,
    col_widths=[1.1*inch, 1.1*inch, 0.7*inch, 3.6*inch]))

story.append(Spacer(1, 0.3*inch))
story.append(HRFlowable(width="100%", thickness=0.5, color=GRAY_MED, spaceBefore=3, spaceAfter=3))
story.append(Paragraph(
    f"Generated {datetime.now().strftime('%B %d, %Y at %I:%M %p')}. "
    "Data period: January 4 — February 3, 2026. CID: 853-189-6842. All figures USD.",
    styles['Note']))

# ─── Build ────────────────────────────────────────────────────────────────────

doc.build(story, onFirstPage=on_first, onLaterPages=on_page)
fsize = os.path.getsize(OUTPUT_PATH) / 1024
print(f"Report saved to: {OUTPUT_PATH}")
print(f"File size: {fsize:.1f} KB")
