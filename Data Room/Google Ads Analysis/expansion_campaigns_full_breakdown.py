from google.ads.googleads.client import GoogleAdsClient
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Load credentials
client = GoogleAdsClient.load_from_storage('/Users/vinuraabeysundara/Desktop/ICG/DOZR/Data Room/Config/google-ads.yaml')
ga_service = client.get_service('GoogleAdsService')
customer_id = '8531896842'

# Define period - Feb 10th to today (Feb 23)
start_date = '2026-02-10'
end_date = '2026-02-23'

print("=" * 160)
print(f"📊 EXPANSION CAMPAIGNS COMPREHENSIVE PERFORMANCE BREAKDOWN")
print(f"Period: {start_date} to {end_date}")
print("=" * 160)

# Query for campaign-level data
query_campaigns = f"""
    SELECT
        campaign.name,
        campaign.id,
        metrics.cost_micros,
        metrics.clicks,
        metrics.impressions,
        metrics.average_cpc,
        metrics.conversions,
        metrics.conversions_value,
        metrics.ctr
    FROM campaign
    WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.status = 'ENABLED'
        AND campaign.name LIKE '%Expansion%'
"""

response = ga_service.search(customer_id=customer_id, query=query_campaigns)

# Aggregate campaign data
campaign_data = {}

for row in response:
    campaign_name = row.campaign.name

    if campaign_name not in campaign_data:
        campaign_data[campaign_name] = {
            'spend': 0,
            'clicks': 0,
            'impressions': 0,
            'conversions': 0,
            'value': 0,
            'cpc': 0
        }

    campaign_data[campaign_name]['spend'] += row.metrics.cost_micros / 1_000_000
    campaign_data[campaign_name]['clicks'] += row.metrics.clicks
    campaign_data[campaign_name]['impressions'] += row.metrics.impressions
    campaign_data[campaign_name]['conversions'] += row.metrics.conversions
    campaign_data[campaign_name]['value'] += row.metrics.conversions_value

# Calculate CPC for each campaign
for campaign_name in campaign_data:
    if campaign_data[campaign_name]['clicks'] > 0:
        campaign_data[campaign_name]['cpc'] = campaign_data[campaign_name]['spend'] / campaign_data[campaign_name]['clicks']

# Get conversion breakdown by campaign
query_conv = f"""
    SELECT
        campaign.name,
        segments.conversion_action_name,
        metrics.conversions
    FROM campaign
    WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.status = 'ENABLED'
        AND campaign.name LIKE '%Expansion%'
        AND metrics.conversions > 0
"""

response_conv = ga_service.search(customer_id=customer_id, query=query_conv)

campaign_conversions = {}

for row in response_conv:
    campaign_name = row.campaign.name
    conv_name = row.segments.conversion_action_name
    conversions = row.metrics.conversions

    if campaign_name not in campaign_conversions:
        campaign_conversions[campaign_name] = {
            'phone_calls': 0,
            'calls_from_ads': 0,
            'quotes': 0,
            'deals': 0,
            'other': 0
        }

    if conv_name == 'Phone Call':
        campaign_conversions[campaign_name]['phone_calls'] += conversions
    elif conv_name == 'Calls from ads':
        campaign_conversions[campaign_name]['calls_from_ads'] += conversions
    elif 'quote' in conv_name.lower():
        campaign_conversions[campaign_name]['quotes'] += conversions
    elif 'Closed Won' in conv_name or 'Deal' in conv_name:
        campaign_conversions[campaign_name]['deals'] += conversions
    else:
        campaign_conversions[campaign_name]['other'] += conversions

# Get ad group level data
query_adgroups = f"""
    SELECT
        campaign.name,
        ad_group.name,
        metrics.cost_micros,
        metrics.clicks,
        metrics.impressions,
        metrics.conversions
    FROM ad_group
    WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.status = 'ENABLED'
        AND ad_group.status = 'ENABLED'
        AND campaign.name LIKE '%Expansion%'
"""

response_adgroups = ga_service.search(customer_id=customer_id, query=query_adgroups)

adgroup_data = {}

for row in response_adgroups:
    campaign_name = row.campaign.name
    adgroup_name = row.ad_group.name

    if campaign_name not in adgroup_data:
        adgroup_data[campaign_name] = {}

    if adgroup_name not in adgroup_data[campaign_name]:
        adgroup_data[campaign_name][adgroup_name] = {
            'spend': 0,
            'clicks': 0,
            'impressions': 0,
            'conversions': 0
        }

    adgroup_data[campaign_name][adgroup_name]['spend'] += row.metrics.cost_micros / 1_000_000
    adgroup_data[campaign_name][adgroup_name]['clicks'] += row.metrics.clicks
    adgroup_data[campaign_name][adgroup_name]['impressions'] += row.metrics.impressions
    adgroup_data[campaign_name][adgroup_name]['conversions'] += row.metrics.conversions

# Print overall summary
print(f"\n{'━' * 160}")
print(f"📊 OVERALL EXPANSION PERFORMANCE")
print(f"{'━' * 160}")

total_spend = sum(d['spend'] for d in campaign_data.values())
total_clicks = sum(d['clicks'] for d in campaign_data.values())
total_impressions = sum(d['impressions'] for d in campaign_data.values())
total_conversions = sum(d['conversions'] for d in campaign_data.values())
total_value = sum(d['value'] for d in campaign_data.values())

total_phone_calls = sum(campaign_conversions.get(c, {}).get('phone_calls', 0) for c in campaign_data.keys())
total_calls_from_ads = sum(campaign_conversions.get(c, {}).get('calls_from_ads', 0) for c in campaign_data.keys())
total_quotes = sum(campaign_conversions.get(c, {}).get('quotes', 0) for c in campaign_data.keys())
total_deals = sum(campaign_conversions.get(c, {}).get('deals', 0) for c in campaign_data.keys())
total_calls = total_phone_calls + total_calls_from_ads

avg_cpc = total_spend / total_clicks if total_clicks > 0 else 0
avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
total_roas = total_value / total_spend if total_spend > 0 else 0
cpa = total_spend / total_conversions if total_conversions > 0 else 0
cost_per_call = total_spend / total_calls if total_calls > 0 else 0

print(f"\n💰 Spend: ${total_spend:,.2f}")
print(f"👆 Clicks: {total_clicks:,}")
print(f"👁️  Impressions: {total_impressions:,}")
print(f"💵 Avg CPC: ${avg_cpc:.2f}")
print(f"📊 CTR: {avg_ctr:.2f}%")
print(f"\n📞 Total Calls: {int(total_calls)} (${cost_per_call:.2f} per call)")
print(f"   • Phone Calls: {int(total_phone_calls)}")
print(f"   • Calls from Ads: {int(total_calls_from_ads)}")
print(f"\n🎯 Total Conversions: {int(total_conversions)} (${cpa:.2f} CPA)")
print(f"📋 Quotes: {int(total_quotes)} ({(total_quotes/total_calls*100) if total_calls > 0 else 0:.1f}% of calls)")
print(f"🎉 Deals: {int(total_deals)} ({(total_deals/total_calls*100) if total_calls > 0 else 0:.1f}% of calls)")
print(f"💎 Conversion Value: ${total_value:,.2f}")
print(f"📈 ROAS: {total_roas:.2f}x")

# Print detailed campaign breakdown
print(f"\n{'=' * 160}")
print(f"📋 DETAILED CAMPAIGN PERFORMANCE")
print(f"{'=' * 160}")

# Sort campaigns by spend
sorted_campaigns = sorted(campaign_data.items(), key=lambda x: x[1]['spend'], reverse=True)

for campaign_name, data in sorted_campaigns:
    conv_data = campaign_conversions.get(campaign_name, {
        'phone_calls': 0, 'calls_from_ads': 0, 'quotes': 0, 'deals': 0
    })

    phone_calls = int(conv_data['phone_calls'])
    calls_from_ads = int(conv_data['calls_from_ads'])
    total_camp_calls = phone_calls + calls_from_ads
    quotes = int(conv_data['quotes'])
    deals = int(conv_data['deals'])

    ctr = (data['clicks'] / data['impressions'] * 100) if data['impressions'] > 0 else 0
    roas = data['value'] / data['spend'] if data['spend'] > 0 else 0
    cpa = data['spend'] / data['conversions'] if data['conversions'] > 0 else 0
    cost_per_call = data['spend'] / total_camp_calls if total_camp_calls > 0 else 0

    print(f"\n{'━' * 160}")
    print(f"🎯 {campaign_name}")
    print(f"{'━' * 160}")

    print(f"\n📊 Performance Metrics:")
    print(f"   • Spend: ${data['spend']:,.2f}")
    print(f"   • Clicks: {data['clicks']:,}")
    print(f"   • Impressions: {data['impressions']:,}")
    print(f"   • CPC: ${data['cpc']:.2f}")
    print(f"   • CTR: {ctr:.2f}%")

    print(f"\n📞 Calls & Conversions:")
    print(f"   • Total Calls: {total_camp_calls} (${cost_per_call:.2f} per call)")
    print(f"     - Phone Calls: {phone_calls}")
    print(f"     - Calls from Ads: {calls_from_ads}")
    print(f"   • Quotes: {quotes} ({(quotes/total_camp_calls*100) if total_camp_calls > 0 else 0:.1f}% of calls)")
    print(f"   • Deals: {deals} ({(deals/total_camp_calls*100) if total_camp_calls > 0 else 0:.1f}% of calls)")

    print(f"\n💰 ROI Metrics:")
    print(f"   • Total Conversions: {int(data['conversions'])}")
    print(f"   • CPA: ${cpa:.2f}")
    print(f"   • Conversion Value: ${data['value']:,.2f}")
    print(f"   • ROAS: {roas:.2f}x")

    # Ad group breakdown
    if campaign_name in adgroup_data:
        print(f"\n📋 Ad Group Breakdown:")
        sorted_adgroups = sorted(adgroup_data[campaign_name].items(),
                                 key=lambda x: x[1]['spend'], reverse=True)

        print(f"   {'Ad Group':<50} {'Spend':>12} {'Clicks':>8} {'Conv':>6} {'CPC':>8}")
        print(f"   {'-' * 90}")

        for adgroup_name, adgroup_metrics in sorted_adgroups[:5]:  # Top 5 ad groups
            ag_cpc = adgroup_metrics['spend'] / adgroup_metrics['clicks'] if adgroup_metrics['clicks'] > 0 else 0
            print(f"   {adgroup_name[:50]:<50} ${adgroup_metrics['spend']:>11,.2f} {adgroup_metrics['clicks']:>8} {int(adgroup_metrics['conversions']):>6} ${ag_cpc:>7.2f}")

# Performance ranking
print(f"\n{'=' * 160}")
print(f"🏆 CAMPAIGN RANKINGS")
print(f"{'=' * 160}")

# By ROAS
print(f"\n💎 Best ROAS:")
sorted_by_roas = sorted(campaign_data.items(),
                        key=lambda x: x[1]['value']/x[1]['spend'] if x[1]['spend'] > 0 else 0,
                        reverse=True)
for i, (name, data) in enumerate(sorted_by_roas[:3], 1):
    roas = data['value'] / data['spend'] if data['spend'] > 0 else 0
    print(f"   {i}. {name}: {roas:.2f}x ROAS (${data['spend']:,.2f} spend)")

# By Call Volume
print(f"\n📞 Most Calls:")
campaign_call_counts = {}
for campaign_name in campaign_data.keys():
    conv_data = campaign_conversions.get(campaign_name, {'phone_calls': 0, 'calls_from_ads': 0})
    total_camp_calls = conv_data['phone_calls'] + conv_data['calls_from_ads']
    campaign_call_counts[campaign_name] = total_camp_calls

sorted_by_calls = sorted(campaign_call_counts.items(), key=lambda x: x[1], reverse=True)
for i, (name, calls) in enumerate(sorted_by_calls[:3], 1):
    spend = campaign_data[name]['spend']
    cost_per = spend / calls if calls > 0 else 0
    print(f"   {i}. {name}: {int(calls)} calls (${cost_per:.2f} per call)")

# By Deals
print(f"\n🎉 Most Deals:")
campaign_deal_counts = {}
for campaign_name in campaign_data.keys():
    conv_data = campaign_conversions.get(campaign_name, {'deals': 0})
    campaign_deal_counts[campaign_name] = conv_data['deals']

sorted_by_deals = sorted(campaign_deal_counts.items(), key=lambda x: x[1], reverse=True)
for i, (name, deals) in enumerate(sorted_by_deals[:3], 1):
    if deals > 0:
        print(f"   {i}. {name}: {int(deals)} deals")

# Underperformers
print(f"\n⚠️  Needs Attention (Low/No Calls):")
for name, calls in sorted_by_calls[-3:]:
    spend = campaign_data[name]['spend']
    print(f"   • {name}: {int(calls)} calls from ${spend:.2f} spend")

print(f"\n{'=' * 160}")
print("✅ BREAKDOWN COMPLETE")
print(f"{'=' * 160}")
