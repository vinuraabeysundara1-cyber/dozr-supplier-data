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
print(f"📊 DOZR CAMPAIGN - AD GROUP LEVEL BREAKDOWN")
print(f"Period 1: Feb 1-10, 2026  |  Period 2: Feb 11-20, 2026")
print("=" * 140)

# Query for campaigns with "Dozer" or "Dozr" in the name
query_campaigns = f"""
    SELECT
        campaign.name,
        campaign.id
    FROM campaign
    WHERE campaign.status = 'ENABLED'
        AND campaign.name LIKE '%Dozer%'
        AND campaign.name NOT LIKE '%Expansion%'
"""

response_campaigns = ga_service.search(customer_id=customer_id, query=query_campaigns)

campaign_ids = []
campaign_names = {}

for row in response_campaigns:
    campaign_ids.append(str(row.campaign.id))
    campaign_names[str(row.campaign.id)] = row.campaign.name

print(f"\n🔍 Found {len(campaign_ids)} DOZR campaign(s):")
for cid, cname in campaign_names.items():
    print(f"   • {cname}")

# Query ad group performance for both periods
query = f"""
    SELECT
        campaign.name,
        campaign.id,
        ad_group.name,
        ad_group.id,
        segments.date,
        metrics.cost_micros,
        metrics.clicks,
        metrics.impressions,
        metrics.average_cpc,
        metrics.conversions,
        metrics.conversions_value
    FROM ad_group
    WHERE segments.date BETWEEN '{period1_start}' AND '{period2_end}'
        AND campaign.status = 'ENABLED'
        AND ad_group.status = 'ENABLED'
        AND campaign.name LIKE '%Dozer%'
        AND campaign.name NOT LIKE '%Expansion%'
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

# Get conversion breakdown by type
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
        AND campaign.name LIKE '%Dozer%'
        AND campaign.name NOT LIKE '%Expansion%'
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
            'period1': {'phone_calls': 0, 'calls_from_ads': 0, 'quotes': 0, 'deals': 0, 'purchases': 0},
            'period2': {'phone_calls': 0, 'calls_from_ads': 0, 'quotes': 0, 'deals': 0, 'purchases': 0}
        }

    # Categorize conversions
    if conv_name == 'Phone Call':
        adgroup_conversions[campaign_name][ad_group_name][period]['phone_calls'] += conversions
    elif conv_name == 'Calls from ads':
        adgroup_conversions[campaign_name][ad_group_name][period]['calls_from_ads'] += conversions
    elif 'quote' in conv_name.lower():
        adgroup_conversions[campaign_name][ad_group_name][period]['quotes'] += conversions
    elif 'Closed Won' in conv_name or 'Deal' in conv_name:
        adgroup_conversions[campaign_name][ad_group_name][period]['deals'] += conversions
    elif 'purchase' in conv_name.lower():
        adgroup_conversions[campaign_name][ad_group_name][period]['purchases'] += conversions

# Print detailed breakdown for each campaign
for campaign_name in sorted(campaigns.keys()):
    print(f"\n{'=' * 140}")
    print(f"🎯 {campaign_name}")
    print(f"{'=' * 140}")

    # Campaign summary
    campaign_p1 = {'spend': 0, 'clicks': 0, 'impressions': 0, 'conversions': 0, 'value': 0,
                   'phone_calls': 0, 'calls_from_ads': 0, 'quotes': 0, 'deals': 0, 'purchases': 0}
    campaign_p2 = {'spend': 0, 'clicks': 0, 'impressions': 0, 'conversions': 0, 'value': 0,
                   'phone_calls': 0, 'calls_from_ads': 0, 'quotes': 0, 'deals': 0, 'purchases': 0}

    for ad_group_name in campaigns[campaign_name]:
        p1 = campaigns[campaign_name][ad_group_name]['period1']
        p2 = campaigns[campaign_name][ad_group_name]['period2']

        campaign_p1['spend'] += p1['spend']
        campaign_p1['clicks'] += p1['clicks']
        campaign_p1['impressions'] += p1['impressions']
        campaign_p1['conversions'] += p1['conversions']
        campaign_p1['value'] += p1['value']

        campaign_p2['spend'] += p2['spend']
        campaign_p2['clicks'] += p2['clicks']
        campaign_p2['impressions'] += p2['impressions']
        campaign_p2['conversions'] += p2['conversions']
        campaign_p2['value'] += p2['value']

        c1 = adgroup_conversions.get(campaign_name, {}).get(ad_group_name, {}).get('period1',
            {'phone_calls': 0, 'calls_from_ads': 0, 'quotes': 0, 'deals': 0, 'purchases': 0})
        c2 = adgroup_conversions.get(campaign_name, {}).get(ad_group_name, {}).get('period2',
            {'phone_calls': 0, 'calls_from_ads': 0, 'quotes': 0, 'deals': 0, 'purchases': 0})

        campaign_p1['phone_calls'] += c1['phone_calls']
        campaign_p1['calls_from_ads'] += c1['calls_from_ads']
        campaign_p1['quotes'] += c1['quotes']
        campaign_p1['deals'] += c1['deals']
        campaign_p1['purchases'] += c1['purchases']

        campaign_p2['phone_calls'] += c2['phone_calls']
        campaign_p2['calls_from_ads'] += c2['calls_from_ads']
        campaign_p2['quotes'] += c2['quotes']
        campaign_p2['deals'] += c2['deals']
        campaign_p2['purchases'] += c2['purchases']

    # Calculate campaign level metrics
    p1_cpc = campaign_p1['spend'] / campaign_p1['clicks'] if campaign_p1['clicks'] > 0 else 0
    p2_cpc = campaign_p2['spend'] / campaign_p2['clicks'] if campaign_p2['clicks'] > 0 else 0

    p1_cpa = campaign_p1['spend'] / campaign_p1['conversions'] if campaign_p1['conversions'] > 0 else 0
    p2_cpa = campaign_p2['spend'] / campaign_p2['conversions'] if campaign_p2['conversions'] > 0 else 0

    p1_roas = campaign_p1['value'] / campaign_p1['spend'] if campaign_p1['spend'] > 0 else 0
    p2_roas = campaign_p2['value'] / campaign_p2['spend'] if campaign_p2['spend'] > 0 else 0

    p1_total_calls = campaign_p1['phone_calls'] + campaign_p1['calls_from_ads']
    p2_total_calls = campaign_p2['phone_calls'] + campaign_p2['calls_from_ads']

    print(f"\n📊 CAMPAIGN SUMMARY")
    print(f"{'─' * 140}")
    print(f"\n{'Metric':<30} {'Period 1 (Feb 1-10)':>30} {'Period 2 (Feb 11-20)':>30} {'Change':>25}")
    print(f"{'─' * 140}")
    print(f"{'💰 Total Spend':<30} ${campaign_p1['spend']:>29.2f} ${campaign_p2['spend']:>29.2f} {((campaign_p2['spend']-campaign_p1['spend'])/campaign_p1['spend']*100) if campaign_p1['spend']>0 else 0:>23.1f}%")
    print(f"{'👆 Total Clicks':<30} {campaign_p1['clicks']:>30} {campaign_p2['clicks']:>30} {((campaign_p2['clicks']-campaign_p1['clicks'])/campaign_p1['clicks']*100) if campaign_p1['clicks']>0 else 0:>23.1f}%")
    print(f"{'📊 Average CPC':<30} ${p1_cpc:>29.2f} ${p2_cpc:>29.2f} {((p2_cpc-p1_cpc)/p1_cpc*100) if p1_cpc>0 else 0:>23.1f}%")
    print(f"{'📞 Phone Calls':<30} {int(campaign_p1['phone_calls']):>30} {int(campaign_p2['phone_calls']):>30} {((campaign_p2['phone_calls']-campaign_p1['phone_calls'])/campaign_p1['phone_calls']*100) if campaign_p1['phone_calls']>0 else 0:>23.1f}%")
    print(f"{'📞 Calls from Ads':<30} {int(campaign_p1['calls_from_ads']):>30} {int(campaign_p2['calls_from_ads']):>30} {((campaign_p2['calls_from_ads']-campaign_p1['calls_from_ads'])/campaign_p1['calls_from_ads']*100) if campaign_p1['calls_from_ads']>0 else 0:>23.1f}%")
    print(f"{'📞 Total Calls':<30} {int(p1_total_calls):>30} {int(p2_total_calls):>30} {((p2_total_calls-p1_total_calls)/p1_total_calls*100) if p1_total_calls>0 else 0:>23.1f}%")
    print(f"{'💬 Quotes':<30} {int(campaign_p1['quotes']):>30} {int(campaign_p2['quotes']):>30} {((campaign_p2['quotes']-campaign_p1['quotes'])/campaign_p1['quotes']*100) if campaign_p1['quotes']>0 else 0:>23.1f}%")
    print(f"{'🎉 Deals':<30} {int(campaign_p1['deals']):>30} {int(campaign_p2['deals']):>30} {((campaign_p2['deals']-campaign_p1['deals'])/campaign_p1['deals']*100) if campaign_p1['deals']>0 else 0:>23.1f}%")
    print(f"{'🛒 Purchases':<30} {int(campaign_p1['purchases']):>30} {int(campaign_p2['purchases']):>30}")
    print(f"{'🎯 Average CPA':<30} ${p1_cpa:>29.2f} ${p2_cpa:>29.2f} {((p2_cpa-p1_cpa)/p1_cpa*100) if p1_cpa>0 else 0:>23.1f}%")
    print(f"{'💵 ROAS':<30} {p1_roas:>28.2f}x {p2_roas:>28.2f}x {((p2_roas-p1_roas)/p1_roas*100) if p1_roas>0 else 0:>23.1f}%")
    print(f"{'💰 Conversion Value':<30} ${campaign_p1['value']:>29.2f} ${campaign_p2['value']:>29.2f} {((campaign_p2['value']-campaign_p1['value'])/campaign_p1['value']*100) if campaign_p1['value']>0 else 0:>23.1f}%")

    # Ad group level breakdown
    print(f"\n{'=' * 140}")
    print(f"📋 AD GROUP LEVEL BREAKDOWN")
    print(f"{'=' * 140}")

    for ad_group_name in sorted(campaigns[campaign_name].keys()):
        p1 = campaigns[campaign_name][ad_group_name]['period1']
        p2 = campaigns[campaign_name][ad_group_name]['period2']

        # Skip if no spend
        if p1['spend'] == 0 and p2['spend'] == 0:
            continue

        c1 = adgroup_conversions.get(campaign_name, {}).get(ad_group_name, {}).get('period1',
            {'phone_calls': 0, 'calls_from_ads': 0, 'quotes': 0, 'deals': 0, 'purchases': 0})
        c2 = adgroup_conversions.get(campaign_name, {}).get(ad_group_name, {}).get('period2',
            {'phone_calls': 0, 'calls_from_ads': 0, 'quotes': 0, 'deals': 0, 'purchases': 0})

        # Calculate metrics
        p1_cpc = p1['spend'] / p1['clicks'] if p1['clicks'] > 0 else 0
        p2_cpc = p2['spend'] / p2['clicks'] if p2['clicks'] > 0 else 0

        p1_cpa = p1['spend'] / p1['conversions'] if p1['conversions'] > 0 else 0
        p2_cpa = p2['spend'] / p2['conversions'] if p2['conversions'] > 0 else 0

        p1_roas = p1['value'] / p1['spend'] if p1['spend'] > 0 else 0
        p2_roas = p2['value'] / p2['spend'] if p2['spend'] > 0 else 0

        p1_total_calls = c1['phone_calls'] + c1['calls_from_ads']
        p2_total_calls = c2['phone_calls'] + c2['calls_from_ads']

        print(f"\n┌─ {ad_group_name}")
        print(f"│")
        print(f"│  {'Metric':<25} {'Period 1':>20} {'Period 2':>20} {'Change':>15}")
        print(f"│  {'-' * 85}")
        print(f"│  {'💰 Spend':<25} ${p1['spend']:>19.2f} ${p2['spend']:>19.2f} {((p2['spend']-p1['spend'])/p1['spend']*100) if p1['spend']>0 else 0:>13.1f}%")
        print(f"│  {'👆 Clicks':<25} {p1['clicks']:>20} {p2['clicks']:>20} {((p2['clicks']-p1['clicks'])/p1['clicks']*100) if p1['clicks']>0 else 0:>13.1f}%")
        print(f"│  {'📊 CPC':<25} ${p1_cpc:>19.2f} ${p2_cpc:>19.2f} {((p2_cpc-p1_cpc)/p1_cpc*100) if p1_cpc>0 else 0:>13.1f}%")
        print(f"│  {'📞 Phone Calls':<25} {int(c1['phone_calls']):>20} {int(c2['phone_calls']):>20} {((c2['phone_calls']-c1['phone_calls'])/c1['phone_calls']*100) if c1['phone_calls']>0 else 0:>13.1f}%")
        print(f"│  {'📞 Calls from Ads':<25} {int(c1['calls_from_ads']):>20} {int(c2['calls_from_ads']):>20} {((c2['calls_from_ads']-c1['calls_from_ads'])/c1['calls_from_ads']*100) if c1['calls_from_ads']>0 else 0:>13.1f}%")
        print(f"│  {'📞 Total Calls':<25} {int(p1_total_calls):>20} {int(p2_total_calls):>20} {((p2_total_calls-p1_total_calls)/p1_total_calls*100) if p1_total_calls>0 else 0:>13.1f}%")
        print(f"│  {'💬 Quotes':<25} {int(c1['quotes']):>20} {int(c2['quotes']):>20} {((c2['quotes']-c1['quotes'])/c1['quotes']*100) if c1['quotes']>0 else 0:>13.1f}%")
        print(f"│  {'🎉 Deals':<25} {int(c1['deals']):>20} {int(c2['deals']):>20} {((c2['deals']-c1['deals'])/c1['deals']*100) if c1['deals']>0 else 0:>13.1f}%")
        print(f"│  {'🛒 Purchases':<25} {int(c1['purchases']):>20} {int(c2['purchases']):>20}")
        print(f"│  {'🎯 CPA':<25} ${p1_cpa:>19.2f} ${p2_cpa:>19.2f} {((p2_cpa-p1_cpa)/p1_cpa*100) if p1_cpa>0 else 0:>13.1f}%")
        print(f"│  {'💵 ROAS':<25} {p1_roas:>18.2f}x {p2_roas:>18.2f}x {((p2_roas-p1_roas)/p1_roas*100) if p1_roas>0 else 0:>13.1f}%")
        print(f"│  {'💰 Conv Value':<25} ${p1['value']:>19.2f} ${p2['value']:>19.2f} {((p2['value']-p1['value'])/p1['value']*100) if p1['value']>0 else 0:>13.1f}%")
        print(f"└─")

print(f"\n{'=' * 140}")
print(f"✅ ANALYSIS COMPLETE")
print(f"{'=' * 140}")
