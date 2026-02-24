from google.ads.googleads.client import GoogleAdsClient
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Load credentials
client = GoogleAdsClient.load_from_storage('/Users/vinuraabeysundara/Desktop/ICG/DOZR/Data Room/Config/google-ads.yaml')
ga_service = client.get_service('GoogleAdsService')
customer_id = '8531896842'

# Define period
period_start = '2026-02-11'
period_end = '2026-02-20'

print("=" * 140)
print(f"📊 EQUIPMENT TYPE BREAKDOWN - Feb 11-20, 2026")
print("=" * 140)

# Query campaign performance
query = f"""
    SELECT
        campaign.name,
        campaign.id,
        metrics.cost_micros,
        metrics.clicks,
        metrics.impressions,
        metrics.average_cpc,
        metrics.conversions,
        metrics.conversions_value
    FROM campaign
    WHERE segments.date BETWEEN '{period_start}' AND '{period_end}'
        AND campaign.status = 'ENABLED'
        AND campaign.name LIKE '%US%'
        AND campaign.name NOT LIKE '%Expansion%'
        AND campaign.name NOT LIKE '%-CA%'
        AND campaign.name NOT LIKE '%Brand%'
        AND campaign.name NOT LIKE '%DSA%'
"""

response = ga_service.search(customer_id=customer_id, query=query)

# Organize data by campaign/equipment type
equipment_data = {}

for row in response:
    campaign_name = row.campaign.name

    if campaign_name not in equipment_data:
        equipment_data[campaign_name] = {
            'spend': 0,
            'clicks': 0,
            'impressions': 0,
            'conversions': 0,
            'value': 0
        }

    equipment_data[campaign_name]['spend'] += row.metrics.cost_micros / 1_000_000
    equipment_data[campaign_name]['clicks'] += row.metrics.clicks
    equipment_data[campaign_name]['impressions'] += row.metrics.impressions
    equipment_data[campaign_name]['conversions'] += row.metrics.conversions
    equipment_data[campaign_name]['value'] += row.metrics.conversions_value

# Get conversion breakdown by type
query_conv = f"""
    SELECT
        campaign.name,
        segments.conversion_action_name,
        metrics.conversions
    FROM campaign
    WHERE segments.date BETWEEN '{period_start}' AND '{period_end}'
        AND campaign.status = 'ENABLED'
        AND campaign.name LIKE '%US%'
        AND campaign.name NOT LIKE '%Expansion%'
        AND campaign.name NOT LIKE '%-CA%'
        AND campaign.name NOT LIKE '%Brand%'
        AND campaign.name NOT LIKE '%DSA%'
        AND metrics.conversions > 0
"""

response_conv = ga_service.search(customer_id=customer_id, query=query_conv)

# Track conversions by campaign
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
            'purchases': 0
        }

    # Categorize conversions
    if conv_name == 'Phone Call':
        campaign_conversions[campaign_name]['phone_calls'] += conversions
    elif conv_name == 'Calls from ads':
        campaign_conversions[campaign_name]['calls_from_ads'] += conversions
    elif 'quote' in conv_name.lower():
        campaign_conversions[campaign_name]['quotes'] += conversions
    elif 'Closed Won' in conv_name or 'Deal' in conv_name:
        campaign_conversions[campaign_name]['deals'] += conversions
    elif 'purchase' in conv_name.lower():
        campaign_conversions[campaign_name]['purchases'] += conversions

# Extract equipment type from campaign name
def get_equipment_type(campaign_name):
    if 'Backhoe' in campaign_name:
        return 'Backhoe'
    elif 'Dozer' in campaign_name:
        return 'Dozers/Skid-Steers'
    elif 'Excavator' in campaign_name:
        return 'Excavators'
    elif 'Forklift' in campaign_name:
        return 'Forklifts'
    elif 'Loader' in campaign_name:
        return 'Loaders'
    elif 'Scissor-Lift' in campaign_name or 'Scissor Lift' in campaign_name:
        return 'Scissor Lifts'
    elif 'Boom' in campaign_name:
        return 'Boom Lifts'
    elif 'Telehandler' in campaign_name:
        return 'Telehandlers'
    else:
        return 'Other'

# Aggregate by equipment type
equipment_summary = {}

for campaign_name in equipment_data.keys():
    equip_type = get_equipment_type(campaign_name)

    if equip_type not in equipment_summary:
        equipment_summary[equip_type] = {
            'spend': 0,
            'clicks': 0,
            'impressions': 0,
            'conversions': 0,
            'value': 0,
            'phone_calls': 0,
            'calls_from_ads': 0,
            'quotes': 0,
            'deals': 0,
            'purchases': 0,
            'campaigns': []
        }

    equipment_summary[equip_type]['spend'] += equipment_data[campaign_name]['spend']
    equipment_summary[equip_type]['clicks'] += equipment_data[campaign_name]['clicks']
    equipment_summary[equip_type]['impressions'] += equipment_data[campaign_name]['impressions']
    equipment_summary[equip_type]['conversions'] += equipment_data[campaign_name]['conversions']
    equipment_summary[equip_type]['value'] += equipment_data[campaign_name]['value']
    equipment_summary[equip_type]['campaigns'].append(campaign_name)

    conv_data = campaign_conversions.get(campaign_name, {
        'phone_calls': 0, 'calls_from_ads': 0, 'quotes': 0, 'deals': 0, 'purchases': 0
    })

    equipment_summary[equip_type]['phone_calls'] += conv_data['phone_calls']
    equipment_summary[equip_type]['calls_from_ads'] += conv_data['calls_from_ads']
    equipment_summary[equip_type]['quotes'] += conv_data['quotes']
    equipment_summary[equip_type]['deals'] += conv_data['deals']
    equipment_summary[equip_type]['purchases'] += conv_data['purchases']

# Print results
print(f"\n{'Equipment Type':<25} {'Spend':>12} {'Clicks':>8} {'Calls':>8} {'Quotes':>8} {'Deals':>7} {'CPA':>10} {'ROAS':>8} {'CTR':>7}")
print("=" * 140)

totals = {
    'spend': 0, 'clicks': 0, 'impressions': 0, 'phone_calls': 0, 'calls_from_ads': 0,
    'quotes': 0, 'deals': 0, 'purchases': 0, 'conversions': 0, 'value': 0
}

for equip_type in sorted(equipment_summary.keys()):
    data = equipment_summary[equip_type]

    total_calls = data['phone_calls'] + data['calls_from_ads']
    cpa = data['spend'] / data['conversions'] if data['conversions'] > 0 else 0
    roas = data['value'] / data['spend'] if data['spend'] > 0 else 0
    ctr = (data['clicks'] / data['impressions'] * 100) if data['impressions'] > 0 else 0

    print(f"{equip_type:<25} ${data['spend']:>11.2f} {data['clicks']:>8} {int(total_calls):>8} {int(data['quotes']):>8} {int(data['deals']):>7} ${cpa:>9.2f} {roas:>6.2f}x {ctr:>6.2f}%")

    # Add to totals
    totals['spend'] += data['spend']
    totals['clicks'] += data['clicks']
    totals['impressions'] += data['impressions']
    totals['phone_calls'] += data['phone_calls']
    totals['calls_from_ads'] += data['calls_from_ads']
    totals['quotes'] += data['quotes']
    totals['deals'] += data['deals']
    totals['purchases'] += data['purchases']
    totals['conversions'] += data['conversions']
    totals['value'] += data['value']

print("=" * 140)
total_calls = totals['phone_calls'] + totals['calls_from_ads']
total_cpa = totals['spend'] / totals['conversions'] if totals['conversions'] > 0 else 0
total_roas = totals['value'] / totals['spend'] if totals['spend'] > 0 else 0
total_ctr = (totals['clicks'] / totals['impressions'] * 100) if totals['impressions'] > 0 else 0

print(f"{'TOTAL':<25} ${totals['spend']:>11.2f} {totals['clicks']:>8} {int(total_calls):>8} {int(totals['quotes']):>8} {int(totals['deals']):>7} ${total_cpa:>9.2f} {total_roas:>6.2f}x {total_ctr:>6.2f}%")

# Detailed breakdown by equipment type
print("\n" + "=" * 140)
print("📋 DETAILED BREAKDOWN BY EQUIPMENT TYPE")
print("=" * 140)

for equip_type in sorted(equipment_summary.keys()):
    data = equipment_summary[equip_type]

    total_calls = data['phone_calls'] + data['calls_from_ads']
    cpa = data['spend'] / data['conversions'] if data['conversions'] > 0 else 0
    roas = data['value'] / data['spend'] if data['spend'] > 0 else 0
    ctr = (data['clicks'] / data['impressions'] * 100) if data['impressions'] > 0 else 0
    cpc = data['spend'] / data['clicks'] if data['clicks'] > 0 else 0

    # Calculate funnel metrics
    total_quotes = data['quotes'] + data['deals']  # Deals are also quotes
    call_to_quote = (total_quotes / total_calls * 100) if total_calls > 0 else 0
    quote_to_deal = (data['deals'] / total_quotes * 100) if total_quotes > 0 else 0
    call_to_deal = (data['deals'] / total_calls * 100) if total_calls > 0 else 0

    print(f"\n{'━' * 140}")
    print(f"🔧 {equip_type.upper()}")
    print(f"{'━' * 140}")

    print(f"\n📊 Performance Metrics:")
    print(f"   • Spend: ${data['spend']:,.2f}")
    print(f"   • Clicks: {data['clicks']:,}")
    print(f"   • Impressions: {data['impressions']:,}")
    print(f"   • CPC: ${cpc:.2f}")
    print(f"   • CTR: {ctr:.2f}%")
    print(f"   • Total Conversions: {int(data['conversions'])}")
    print(f"   • CPA: ${cpa:.2f}")
    print(f"   • ROAS: {roas:.2f}x")
    print(f"   • Conversion Value: ${data['value']:,.2f}")

    print(f"\n📞 Conversion Funnel:")
    print(f"   • Phone Calls: {int(data['phone_calls'])}")
    print(f"   • Calls from Ads: {int(data['calls_from_ads'])}")
    print(f"   • Total Calls: {int(total_calls)}")
    print(f"   • Quotes: {int(data['quotes'])}")
    print(f"   • Deals: {int(data['deals'])}")
    print(f"   • Purchases: {int(data['purchases'])}")

    print(f"\n🎯 Funnel Conversion Rates:")
    print(f"   • Call → Quote: {call_to_quote:.1f}%")
    print(f"   • Quote → Deal: {quote_to_deal:.1f}%")
    print(f"   • Call → Deal: {call_to_deal:.1f}%")

    print(f"\n📋 Campaigns: {', '.join([c.replace('Search-', '').replace('-Core-Geos-US', '').replace('-V3', '') for c in data['campaigns']])}")

print("\n" + "=" * 140)
print("✅ ANALYSIS COMPLETE")
print("=" * 140)
