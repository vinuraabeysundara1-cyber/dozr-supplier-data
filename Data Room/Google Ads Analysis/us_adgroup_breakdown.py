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

print("=" * 150)
print(f"📊 US CAMPAIGNS - AD GROUP LEVEL ANALYSIS (Excluding Expansion)")
print(f"Period 1: Feb 1-10, 2026  |  Period 2: Feb 11-20, 2026")
print("=" * 150)

# Query ad group performance for both periods
query = f"""
    SELECT
        campaign.name,
        campaign.id,
        ad_group.name,
        ad_group.id,
        ad_group.status,
        segments.date,
        metrics.cost_micros,
        metrics.clicks,
        metrics.impressions,
        metrics.conversions,
        metrics.conversions_value
    FROM ad_group
    WHERE segments.date BETWEEN '{period1_start}' AND '{period2_end}'
        AND campaign.status = 'ENABLED'
        AND ad_group.status = 'ENABLED'
        AND campaign.name LIKE '%US%'
        AND campaign.name NOT LIKE '%Expansion%'
        AND campaign.name NOT LIKE '%-CA%'
    ORDER BY campaign.name, ad_group.name
"""

response = ga_service.search(customer_id=customer_id, query=query)

# Organize data by campaign > ad group > period
campaigns = {}

for row in response:
    campaign_name = row.campaign.name
    ad_group_name = row.ad_group.name
    date = row.segments.date

    # Determine which period
    if period1_start <= date <= period1_end:
        period = 'period1'
    elif period2_start <= date <= period2_end:
        period = 'period2'
    else:
        continue

    if campaign_name not in campaigns:
        campaigns[campaign_name] = {}

    if ad_group_name not in campaigns[campaign_name]:
        campaigns[campaign_name][ad_group_name] = {
            'period1': {'spend': 0, 'clicks': 0, 'impressions': 0, 'conversions': 0, 'value': 0},
            'period2': {'spend': 0, 'clicks': 0, 'impressions': 0, 'conversions': 0, 'value': 0}
        }

    campaigns[campaign_name][ad_group_name][period]['spend'] += row.metrics.cost_micros / 1_000_000
    campaigns[campaign_name][ad_group_name][period]['clicks'] += row.metrics.clicks
    campaigns[campaign_name][ad_group_name][period]['impressions'] += row.metrics.impressions
    campaigns[campaign_name][ad_group_name][period]['conversions'] += row.metrics.conversions
    campaigns[campaign_name][ad_group_name][period]['value'] += row.metrics.conversions_value

# Get conversion breakdown by ad group
query_conversions = f"""
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

response_conv = ga_service.search(customer_id=customer_id, query=query_conversions)

# Organize conversions by campaign > ad group > period > type
adgroup_conversions = {}

for row in response_conv:
    campaign_name = row.campaign.name
    ad_group_name = row.ad_group.name
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

    if campaign_name not in adgroup_conversions:
        adgroup_conversions[campaign_name] = {}

    if ad_group_name not in adgroup_conversions[campaign_name]:
        adgroup_conversions[campaign_name][ad_group_name] = {
            'period1': {'calls': 0, 'quotes': 0, 'deals': 0},
            'period2': {'calls': 0, 'quotes': 0, 'deals': 0}
        }

    # Categorize conversions
    if 'Phone Call' in conv_name or 'Calls from ads' in conv_name:
        adgroup_conversions[campaign_name][ad_group_name][period]['calls'] += conversions
    elif 'quote' in conv_name.lower():
        adgroup_conversions[campaign_name][ad_group_name][period]['quotes'] += conversions
    elif 'Closed Won' in conv_name or 'Deal' in conv_name:
        adgroup_conversions[campaign_name][ad_group_name][period]['deals'] += conversions

# Print campaign-by-campaign, ad group-by-ad group breakdown
for campaign_name in sorted(campaigns.keys()):
    print(f"\n{'=' * 150}")
    print(f"🎯 {campaign_name}")
    print(f"{'=' * 150}")

    # Campaign totals
    campaign_p1 = {'spend': 0, 'clicks': 0, 'conversions': 0, 'value': 0, 'calls': 0, 'quotes': 0, 'deals': 0}
    campaign_p2 = {'spend': 0, 'clicks': 0, 'conversions': 0, 'value': 0, 'calls': 0, 'quotes': 0, 'deals': 0}

    for ad_group_name in campaigns[campaign_name]:
        p1 = campaigns[campaign_name][ad_group_name]['period1']
        p2 = campaigns[campaign_name][ad_group_name]['period2']

        campaign_p1['spend'] += p1['spend']
        campaign_p1['clicks'] += p1['clicks']
        campaign_p1['conversions'] += p1['conversions']
        campaign_p1['value'] += p1['value']

        campaign_p2['spend'] += p2['spend']
        campaign_p2['clicks'] += p2['clicks']
        campaign_p2['conversions'] += p2['conversions']
        campaign_p2['value'] += p2['value']

        c1 = adgroup_conversions.get(campaign_name, {}).get(ad_group_name, {}).get('period1', {'calls': 0, 'quotes': 0, 'deals': 0})
        c2 = adgroup_conversions.get(campaign_name, {}).get(ad_group_name, {}).get('period2', {'calls': 0, 'quotes': 0, 'deals': 0})

        campaign_p1['calls'] += c1['calls']
        campaign_p1['quotes'] += c1['quotes']
        campaign_p1['deals'] += c1['deals']

        campaign_p2['calls'] += c2['calls']
        campaign_p2['quotes'] += c2['quotes']
        campaign_p2['deals'] += c2['deals']

    # Print campaign summary
    p1_cpa = campaign_p1['spend'] / campaign_p1['conversions'] if campaign_p1['conversions'] > 0 else 0
    p2_cpa = campaign_p2['spend'] / campaign_p2['conversions'] if campaign_p2['conversions'] > 0 else 0
    p1_roas = campaign_p1['value'] / campaign_p1['spend'] if campaign_p1['spend'] > 0 else 0
    p2_roas = campaign_p2['value'] / campaign_p2['spend'] if campaign_p2['spend'] > 0 else 0

    print(f"\n📊 Campaign Summary:")
    print(f"   Period 1: ${campaign_p1['spend']:.2f} spend | {int(campaign_p1['calls'])} calls | {int(campaign_p1['quotes'])} quotes | {int(campaign_p1['deals'])} deals | ${p1_cpa:.2f} CPA | {p1_roas:.2f}x ROAS")
    print(f"   Period 2: ${campaign_p2['spend']:.2f} spend | {int(campaign_p2['calls'])} calls | {int(campaign_p2['quotes'])} quotes | {int(campaign_p2['deals'])} deals | ${p2_cpa:.2f} CPA | {p2_roas:.2f}x ROAS")

    # Print ad group breakdown
    print(f"\n{'─' * 150}")
    print(f"{'Ad Group':<50} {'Period 1 Spend':>15} {'P1 Calls':>10} {'P1 Quotes':>10} {'P1 Deals':>10} {'Period 2 Spend':>15} {'P2 Calls':>10} {'P2 Quotes':>10} {'P2 Deals':>10}")
    print(f"{'─' * 150}")

    for ad_group_name in sorted(campaigns[campaign_name].keys()):
        p1 = campaigns[campaign_name][ad_group_name]['period1']
        p2 = campaigns[campaign_name][ad_group_name]['period2']

        c1 = adgroup_conversions.get(campaign_name, {}).get(ad_group_name, {}).get('period1', {'calls': 0, 'quotes': 0, 'deals': 0})
        c2 = adgroup_conversions.get(campaign_name, {}).get(ad_group_name, {}).get('period2', {'calls': 0, 'quotes': 0, 'deals': 0})

        # Only show ad groups with spend in either period
        if p1['spend'] > 0 or p2['spend'] > 0:
            print(f"{ad_group_name:<50} ${p1['spend']:>14.2f} {int(c1['calls']):>10} {int(c1['quotes']):>10} {int(c1['deals']):>10} ${p2['spend']:>14.2f} {int(c2['calls']):>10} {int(c2['quotes']):>10} {int(c2['deals']):>10}")

    # Show detailed metrics for each ad group
    print(f"\n{'━' * 150}")
    print(f"📋 DETAILED AD GROUP METRICS")
    print(f"{'━' * 150}")

    for ad_group_name in sorted(campaigns[campaign_name].keys()):
        p1 = campaigns[campaign_name][ad_group_name]['period1']
        p2 = campaigns[campaign_name][ad_group_name]['period2']

        # Skip ad groups with no spend
        if p1['spend'] == 0 and p2['spend'] == 0:
            continue

        c1 = adgroup_conversions.get(campaign_name, {}).get(ad_group_name, {}).get('period1', {'calls': 0, 'quotes': 0, 'deals': 0})
        c2 = adgroup_conversions.get(campaign_name, {}).get(ad_group_name, {}).get('period2', {'calls': 0, 'quotes': 0, 'deals': 0})

        p1_cpa = p1['spend'] / p1['conversions'] if p1['conversions'] > 0 else 0
        p2_cpa = p2['spend'] / p2['conversions'] if p2['conversions'] > 0 else 0
        p1_roas = p1['value'] / p1['spend'] if p1['spend'] > 0 else 0
        p2_roas = p2['value'] / p2['spend'] if p2['spend'] > 0 else 0
        p1_ctr = (p1['clicks'] / p1['impressions'] * 100) if p1['impressions'] > 0 else 0
        p2_ctr = (p2['clicks'] / p2['impressions'] * 100) if p2['impressions'] > 0 else 0

        # Calculate changes
        spend_change = ((p2['spend'] - p1['spend']) / p1['spend'] * 100) if p1['spend'] > 0 else (100 if p2['spend'] > 0 else 0)
        calls_change = ((c2['calls'] - c1['calls']) / c1['calls'] * 100) if c1['calls'] > 0 else (100 if c2['calls'] > 0 else 0)

        print(f"\n┌─ {ad_group_name}")
        print(f"│")
        print(f"│  {'Metric':<20} {'Period 1':>20} {'Period 2':>20} {'Change':>15}")
        print(f"│  {'-' * 80}")
        print(f"│  {'💰 Spend':<20} ${p1['spend']:>19.2f} ${p2['spend']:>19.2f} {spend_change:>13.1f}%")
        print(f"│  {'👆 Clicks':<20} {p1['clicks']:>20} {p2['clicks']:>20} {((p2['clicks']-p1['clicks'])/p1['clicks']*100) if p1['clicks']>0 else 0:>13.1f}%")
        print(f"│  {'📞 Calls':<20} {int(c1['calls']):>20} {int(c2['calls']):>20} {calls_change:>13.1f}%")
        print(f"│  {'💬 Quotes':<20} {int(c1['quotes']):>20} {int(c2['quotes']):>20} {((c2['quotes']-c1['quotes'])/c1['quotes']*100) if c1['quotes']>0 else 0:>13.1f}%")
        print(f"│  {'🎉 Deals':<20} {int(c1['deals']):>20} {int(c2['deals']):>20} {((c2['deals']-c1['deals'])/c1['deals']*100) if c1['deals']>0 else 0:>13.1f}%")
        print(f"│  {'🎯 CPA':<20} ${p1_cpa:>19.2f} ${p2_cpa:>19.2f} {((p2_cpa-p1_cpa)/p1_cpa*100) if p1_cpa>0 else 0:>13.1f}%")
        print(f"│  {'💵 ROAS':<20} {p1_roas:>18.2f}x {p2_roas:>18.2f}x {((p2_roas-p1_roas)/p1_roas*100) if p1_roas>0 else 0:>13.1f}%")
        print(f"│  {'📈 CTR':<20} {p1_ctr:>18.2f}% {p2_ctr:>18.2f}% {(p2_ctr-p1_ctr):>13.2f}pp")
        print(f"└─")

print(f"\n{'=' * 150}")
print(f"✅ ANALYSIS COMPLETE")
print(f"{'=' * 150}")
