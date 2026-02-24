from google.ads.googleads.client import GoogleAdsClient
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Load credentials
client = GoogleAdsClient.load_from_storage('/Users/vinuraabeysundara/Desktop/ICG/DOZR/Data Room/Config/google-ads.yaml')
ga_service = client.get_service('GoogleAdsService')
customer_id = '8531896842'

# Define periods
period1_start = '2026-02-01'
period1_end = '2026-02-10'
period2_start = '2026-02-11'
period2_end = '2026-02-20'

print("=" * 140)
print(f"📊 US CAMPAIGNS PERFORMANCE COMPARISON (Excluding Expansion)")
print(f"Period 1: Feb 1-10, 2026  |  Period 2: Feb 11-20, 2026")
print("=" * 140)

# Query campaign performance for both periods
query = f"""
    SELECT
        campaign.name,
        campaign.id,
        segments.date,
        metrics.cost_micros,
        metrics.clicks,
        metrics.impressions,
        metrics.conversions,
        metrics.conversions_value
    FROM campaign
    WHERE segments.date BETWEEN '{period1_start}' AND '{period2_end}'
        AND campaign.status = 'ENABLED'
        AND campaign.name LIKE '%US%'
        AND campaign.name NOT LIKE '%Expansion%'
        AND campaign.name NOT LIKE '%-CA%'
    ORDER BY campaign.name
"""

response = ga_service.search(customer_id=customer_id, query=query)

# Organize data by campaign and period
campaigns = {}

for row in response:
    campaign_name = row.campaign.name
    date = row.segments.date

    # Determine which period
    if period1_start <= date <= period1_end:
        period = 'period1'
    elif period2_start <= date <= period2_end:
        period = 'period2'
    else:
        continue

    if campaign_name not in campaigns:
        campaigns[campaign_name] = {
            'period1': {'spend': 0, 'clicks': 0, 'impressions': 0, 'conversions': 0, 'value': 0},
            'period2': {'spend': 0, 'clicks': 0, 'impressions': 0, 'conversions': 0, 'value': 0}
        }

    campaigns[campaign_name][period]['spend'] += row.metrics.cost_micros / 1_000_000
    campaigns[campaign_name][period]['clicks'] += row.metrics.clicks
    campaigns[campaign_name][period]['impressions'] += row.metrics.impressions
    campaigns[campaign_name][period]['conversions'] += row.metrics.conversions
    campaigns[campaign_name][period]['value'] += row.metrics.conversions_value

# Get conversion breakdown by type
query_conversions = f"""
    SELECT
        campaign.name,
        segments.date,
        segments.conversion_action_name,
        metrics.conversions
    FROM campaign
    WHERE segments.date BETWEEN '{period1_start}' AND '{period2_end}'
        AND campaign.status = 'ENABLED'
        AND campaign.name LIKE '%US%'
        AND campaign.name NOT LIKE '%Expansion%'
        AND campaign.name NOT LIKE '%-CA%'
        AND metrics.conversions > 0
"""

response_conv = ga_service.search(customer_id=customer_id, query=query_conversions)

# Organize conversions by campaign, period, and type
campaign_conversions = {}

for row in response_conv:
    campaign_name = row.campaign.name
    date = row.segments.date
    conv_name = row.segments.conversion_action_name
    conversions = row.metrics.conversions

    # Determine which period
    if period1_start <= date <= period1_end:
        period = 'period1'
    elif period2_start <= date <= period2_end:
        period = 'period2'
    else:
        continue

    if campaign_name not in campaign_conversions:
        campaign_conversions[campaign_name] = {
            'period1': {'calls': 0, 'quotes': 0, 'deals': 0},
            'period2': {'calls': 0, 'quotes': 0, 'deals': 0}
        }

    # Categorize conversions
    if 'Phone Call' in conv_name or 'Calls from ads' in conv_name:
        campaign_conversions[campaign_name][period]['calls'] += conversions
    elif 'quote' in conv_name.lower():
        campaign_conversions[campaign_name][period]['quotes'] += conversions
    elif 'Closed Won' in conv_name or 'Deal' in conv_name:
        campaign_conversions[campaign_name][period]['deals'] += conversions

# Print campaign-by-campaign breakdown
print("\n📋 CAMPAIGN-BY-CAMPAIGN BREAKDOWN")
print("=" * 140)

for campaign_name in sorted(campaigns.keys()):
    p1 = campaigns[campaign_name]['period1']
    p2 = campaigns[campaign_name]['period2']

    # Get conversion data
    c1 = campaign_conversions.get(campaign_name, {}).get('period1', {'calls': 0, 'quotes': 0, 'deals': 0})
    c2 = campaign_conversions.get(campaign_name, {}).get('period2', {'calls': 0, 'quotes': 0, 'deals': 0})

    # Calculate metrics
    p1_cpa = p1['spend'] / p1['conversions'] if p1['conversions'] > 0 else 0
    p2_cpa = p2['spend'] / p2['conversions'] if p2['conversions'] > 0 else 0

    p1_roas = p1['value'] / p1['spend'] if p1['spend'] > 0 else 0
    p2_roas = p2['value'] / p2['spend'] if p2['spend'] > 0 else 0

    # Calculate changes
    spend_change = ((p2['spend'] - p1['spend']) / p1['spend'] * 100) if p1['spend'] > 0 else 0
    conv_change = ((p2['conversions'] - p1['conversions']) / p1['conversions'] * 100) if p1['conversions'] > 0 else 0

    print(f"\n{'━' * 140}")
    print(f"📌 {campaign_name}")
    print(f"{'━' * 140}")

    print(f"\n{'Metric':<25} {'Period 1 (Feb 1-10)':>30} {'Period 2 (Feb 11-20)':>30} {'Change':>25}")
    print(f"{'-' * 140}")
    print(f"{'💰 Spend':<25} ${p1['spend']:>29.2f} ${p2['spend']:>29.2f} {spend_change:>23.1f}%")
    print(f"{'👆 Clicks':<25} {p1['clicks']:>30} {p2['clicks']:>30} {((p2['clicks']-p1['clicks'])/p1['clicks']*100) if p1['clicks']>0 else 0:>23.1f}%")
    print(f"{'📞 Phone Calls':<25} {int(c1['calls']):>30} {int(c2['calls']):>30} {((c2['calls']-c1['calls'])/c1['calls']*100) if c1['calls']>0 else 0:>23.1f}%")
    print(f"{'💬 Quotes':<25} {int(c1['quotes']):>30} {int(c2['quotes']):>30} {((c2['quotes']-c1['quotes'])/c1['quotes']*100) if c1['quotes']>0 else 0:>23.1f}%")
    print(f"{'🎉 Deals':<25} {int(c1['deals']):>30} {int(c2['deals']):>30} {((c2['deals']-c1['deals'])/c1['deals']*100) if c1['deals']>0 else 0:>23.1f}%")
    print(f"{'📊 Total Conversions':<25} {int(p1['conversions']):>30} {int(p2['conversions']):>30} {conv_change:>23.1f}%")
    print(f"{'🎯 CPA':<25} ${p1_cpa:>29.2f} ${p2_cpa:>29.2f} {((p2_cpa-p1_cpa)/p1_cpa*100) if p1_cpa>0 else 0:>23.1f}%")
    print(f"{'💵 ROAS':<25} {p1_roas:>28.2f}x {p2_roas:>28.2f}x {((p2_roas-p1_roas)/p1_roas*100) if p1_roas>0 else 0:>23.1f}%")

    # Funnel metrics
    p1_call_to_quote = (c1['quotes'] / c1['calls'] * 100) if c1['calls'] > 0 else 0
    p2_call_to_quote = (c2['quotes'] / c2['calls'] * 100) if c2['calls'] > 0 else 0

    p1_quote_to_deal = (c1['deals'] / c1['quotes'] * 100) if c1['quotes'] > 0 else 0
    p2_quote_to_deal = (c2['deals'] / c2['quotes'] * 100) if c2['quotes'] > 0 else 0

    print(f"\n{'Funnel Metrics':<25} {'Period 1':>30} {'Period 2':>30}")
    print(f"{'-' * 140}")
    print(f"{'📊 Call→Quote Rate':<25} {p1_call_to_quote:>28.1f}% {p2_call_to_quote:>28.1f}%")
    print(f"{'🎯 Quote→Deal Rate':<25} {p1_quote_to_deal:>28.1f}% {p2_quote_to_deal:>28.1f}%")

# Print overall summary
print(f"\n{'=' * 140}")
print(f"📊 OVERALL SUMMARY - ALL US CAMPAIGNS (Excluding Expansion)")
print(f"{'=' * 140}")

total_p1 = {'spend': 0, 'clicks': 0, 'conversions': 0, 'value': 0, 'calls': 0, 'quotes': 0, 'deals': 0}
total_p2 = {'spend': 0, 'clicks': 0, 'conversions': 0, 'value': 0, 'calls': 0, 'quotes': 0, 'deals': 0}

for campaign_name in campaigns.keys():
    p1 = campaigns[campaign_name]['period1']
    p2 = campaigns[campaign_name]['period2']

    total_p1['spend'] += p1['spend']
    total_p1['clicks'] += p1['clicks']
    total_p1['conversions'] += p1['conversions']
    total_p1['value'] += p1['value']

    total_p2['spend'] += p2['spend']
    total_p2['clicks'] += p2['clicks']
    total_p2['conversions'] += p2['conversions']
    total_p2['value'] += p2['value']

    c1 = campaign_conversions.get(campaign_name, {}).get('period1', {'calls': 0, 'quotes': 0, 'deals': 0})
    c2 = campaign_conversions.get(campaign_name, {}).get('period2', {'calls': 0, 'quotes': 0, 'deals': 0})

    total_p1['calls'] += c1['calls']
    total_p1['quotes'] += c1['quotes']
    total_p1['deals'] += c1['deals']

    total_p2['calls'] += c2['calls']
    total_p2['quotes'] += c2['quotes']
    total_p2['deals'] += c2['deals']

# Calculate summary metrics
p1_cpa = total_p1['spend'] / total_p1['conversions'] if total_p1['conversions'] > 0 else 0
p2_cpa = total_p2['spend'] / total_p2['conversions'] if total_p2['conversions'] > 0 else 0

p1_roas = total_p1['value'] / total_p1['spend'] if total_p1['spend'] > 0 else 0
p2_roas = total_p2['value'] / total_p2['spend'] if total_p2['spend'] > 0 else 0

p1_call_to_quote = (total_p1['quotes'] / total_p1['calls'] * 100) if total_p1['calls'] > 0 else 0
p2_call_to_quote = (total_p2['quotes'] / total_p2['calls'] * 100) if total_p2['calls'] > 0 else 0

p1_quote_to_deal = (total_p1['deals'] / total_p1['quotes'] * 100) if total_p1['quotes'] > 0 else 0
p2_quote_to_deal = (total_p2['deals'] / total_p2['quotes'] * 100) if total_p2['quotes'] > 0 else 0

print(f"\n{'Metric':<30} {'Period 1 (Feb 1-10)':>30} {'Period 2 (Feb 11-20)':>30} {'Change':>25}")
print(f"{'-' * 140}")
print(f"{'💰 Total Spend':<30} ${total_p1['spend']:>29.2f} ${total_p2['spend']:>29.2f} {((total_p2['spend']-total_p1['spend'])/total_p1['spend']*100) if total_p1['spend']>0 else 0:>23.1f}%")
print(f"{'👆 Total Clicks':<30} {total_p1['clicks']:>30} {total_p2['clicks']:>30} {((total_p2['clicks']-total_p1['clicks'])/total_p1['clicks']*100) if total_p1['clicks']>0 else 0:>23.1f}%")
print(f"{'📞 Total Phone Calls':<30} {int(total_p1['calls']):>30} {int(total_p2['calls']):>30} {((total_p2['calls']-total_p1['calls'])/total_p1['calls']*100) if total_p1['calls']>0 else 0:>23.1f}%")
print(f"{'💬 Total Quotes':<30} {int(total_p1['quotes']):>30} {int(total_p2['quotes']):>30} {((total_p2['quotes']-total_p1['quotes'])/total_p1['quotes']*100) if total_p1['quotes']>0 else 0:>23.1f}%")
print(f"{'🎉 Total Deals':<30} {int(total_p1['deals']):>30} {int(total_p2['deals']):>30} {((total_p2['deals']-total_p1['deals'])/total_p1['deals']*100) if total_p1['deals']>0 else 0:>23.1f}%")
print(f"{'📊 Total Conversions':<30} {int(total_p1['conversions']):>30} {int(total_p2['conversions']):>30} {((total_p2['conversions']-total_p1['conversions'])/total_p1['conversions']*100) if total_p1['conversions']>0 else 0:>23.1f}%")
print(f"{'🎯 Average CPA':<30} ${p1_cpa:>29.2f} ${p2_cpa:>29.2f} {((p2_cpa-p1_cpa)/p1_cpa*100) if p1_cpa>0 else 0:>23.1f}%")
print(f"{'💵 ROAS':<30} {p1_roas:>28.2f}x {p2_roas:>28.2f}x {((p2_roas-p1_roas)/p1_roas*100) if p1_roas>0 else 0:>23.1f}%")
print(f"{'💰 Conversion Value':<30} ${total_p1['value']:>29.2f} ${total_p2['value']:>29.2f} {((total_p2['value']-total_p1['value'])/total_p1['value']*100) if total_p1['value']>0 else 0:>23.1f}%")

print(f"\n{'Funnel Performance':<30} {'Period 1':>30} {'Period 2':>30}")
print(f"{'-' * 140}")
print(f"{'📊 Call→Quote Rate':<30} {p1_call_to_quote:>28.1f}% {p2_call_to_quote:>28.1f}%")
print(f"{'🎯 Quote→Deal Rate':<30} {p1_quote_to_deal:>28.1f}% {p2_quote_to_deal:>28.1f}%")
print(f"{'💰 Call→Deal Rate':<30} {(total_p1['deals']/total_p1['calls']*100) if total_p1['calls']>0 else 0:>28.1f}% {(total_p2['deals']/total_p2['calls']*100) if total_p2['calls']>0 else 0:>28.1f}%")

print(f"\n{'=' * 140}")
