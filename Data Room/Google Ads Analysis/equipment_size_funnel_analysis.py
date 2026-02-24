from google.ads.googleads.client import GoogleAdsClient
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Load credentials
client = GoogleAdsClient.load_from_storage('/Users/vinuraabeysundara/Desktop/ICG/DOZR/Data Room/Config/google-ads.yaml')
ga_service = client.get_service('GoogleAdsService')
customer_id = '8531896842'

print("=" * 120)
print(f"📊 EQUIPMENT SIZE FUNNEL ANALYSIS - Small vs Large Equipment")
print(f"Analyzing last 30 days of data")
print("=" * 120)

# Define equipment categories
small_equipment = {
    'keywords': ['Skid-Steer', 'Mini-Excavator', 'Telehandler', 'Backhoe'],
    'campaigns': []
}

large_equipment = {
    'keywords': ['Excavator', 'Dozer', 'Loader', 'Forklift', 'Boom-Lift', 'Scissor-Lift'],
    'campaigns': [],
    'exclude': ['Mini-Excavator']  # Exclude mini from large
}

# Get last 30 days
end_date = datetime.now()
start_date = end_date - timedelta(days=30)
start_str = start_date.strftime('%Y-%m-%d')
end_str = end_date.strftime('%Y-%m-%d')

# Query campaign performance
query = f"""
    SELECT
        campaign.name,
        campaign.id,
        ad_group.name,
        segments.date,
        metrics.cost_micros,
        metrics.clicks,
        metrics.conversions
    FROM ad_group
    WHERE segments.date BETWEEN '{start_str}' AND '{end_str}'
        AND campaign.status = 'ENABLED'
        AND ad_group.status = 'ENABLED'
        AND campaign.name LIKE '%US%'
        AND campaign.name NOT LIKE '%Expansion%'
        AND campaign.name NOT LIKE '%-CA%'
"""

response = ga_service.search(customer_id=customer_id, query=query)

# Categorize campaigns and aggregate data
campaigns_data = {}

for row in response:
    campaign_name = row.campaign.name
    ad_group_name = row.ad_group.name

    if campaign_name not in campaigns_data:
        campaigns_data[campaign_name] = {
            'spend': 0,
            'clicks': 0,
            'conversions': 0,
            'ad_groups': set()
        }

    campaigns_data[campaign_name]['spend'] += row.metrics.cost_micros / 1_000_000
    campaigns_data[campaign_name]['clicks'] += row.metrics.clicks
    campaigns_data[campaign_name]['conversions'] += row.metrics.conversions
    campaigns_data[campaign_name]['ad_groups'].add(ad_group_name)

# Get conversion breakdown by type
query_conv = f"""
    SELECT
        campaign.name,
        ad_group.name,
        segments.conversion_action_name,
        metrics.conversions
    FROM ad_group
    WHERE segments.date BETWEEN '{start_str}' AND '{end_str}'
        AND campaign.status = 'ENABLED'
        AND ad_group.status = 'ENABLED'
        AND campaign.name LIKE '%US%'
        AND campaign.name NOT LIKE '%Expansion%'
        AND campaign.name NOT LIKE '%-CA%'
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
            'calls': 0,
            'quotes': 0,
            'deals': 0
        }

    # Categorize conversions
    if 'Phone Call' in conv_name or 'Calls from ads' in conv_name:
        campaign_conversions[campaign_name]['calls'] += conversions
    elif 'quote' in conv_name.lower():
        campaign_conversions[campaign_name]['quotes'] += conversions
    elif 'Closed Won' in conv_name or 'Deal' in conv_name:
        campaign_conversions[campaign_name]['deals'] += conversions

# Categorize campaigns by equipment size
small_equip_data = {'spend': 0, 'clicks': 0, 'calls': 0, 'quotes': 0, 'deals': 0, 'campaigns': []}
large_equip_data = {'spend': 0, 'clicks': 0, 'calls': 0, 'quotes': 0, 'deals': 0, 'campaigns': []}

for campaign_name in campaigns_data.keys():
    # Determine if small equipment
    is_small = any(keyword in campaign_name for keyword in small_equipment['keywords'])

    # Determine if large equipment (excluding mini-excavator)
    is_large = any(keyword in campaign_name for keyword in large_equipment['keywords'])
    is_large = is_large and not any(exclude in campaign_name for exclude in large_equipment.get('exclude', []))

    # Get conversion data
    conv_data = campaign_conversions.get(campaign_name, {'calls': 0, 'quotes': 0, 'deals': 0})

    if is_small:
        small_equip_data['spend'] += campaigns_data[campaign_name]['spend']
        small_equip_data['clicks'] += campaigns_data[campaign_name]['clicks']
        small_equip_data['calls'] += conv_data['calls']
        small_equip_data['quotes'] += conv_data['quotes']
        small_equip_data['deals'] += conv_data['deals']
        small_equip_data['campaigns'].append(campaign_name)

    if is_large and not is_small:  # Don't double count
        large_equip_data['spend'] += campaigns_data[campaign_name]['spend']
        large_equip_data['clicks'] += campaigns_data[campaign_name]['clicks']
        large_equip_data['calls'] += conv_data['calls']
        large_equip_data['quotes'] += conv_data['quotes']
        large_equip_data['deals'] += conv_data['deals']
        large_equip_data['campaigns'].append(campaign_name)

# Calculate conversion rates
def calc_funnel_rates(data, label):
    calls = data['calls']
    quotes = data['quotes']
    deals = data['deals']

    # Adjust quotes to include deals (since deals start as quotes)
    total_quotes = quotes + deals

    call_to_quote = (total_quotes / calls * 100) if calls > 0 else 0
    quote_to_deal = (deals / total_quotes * 100) if total_quotes > 0 else 0
    call_to_deal = (deals / calls * 100) if calls > 0 else 0

    print(f"\n{'━' * 120}")
    print(f"{'Equipment Type':<30} {label}")
    print(f"{'━' * 120}")
    print(f"\n📊 Overall Metrics:")
    print(f"   • Total Spend: ${data['spend']:,.2f}")
    print(f"   • Total Clicks: {data['clicks']:,}")
    print(f"   • Total Calls: {int(calls)}")
    print(f"   • Total Quotes: {int(total_quotes)} (including {int(deals)} deals)")
    print(f"   • Total Deals: {int(deals)}")

    print(f"\n🎯 Funnel Conversion Rates:")
    print(f"   • Call → Quote Rate: {call_to_quote:.1f}%")
    print(f"   • Quote → Deal Rate: {quote_to_deal:.1f}%")
    print(f"   • Call → Deal Rate: {call_to_deal:.1f}%")

    print(f"\n📋 Campaigns Included ({len(data['campaigns'])}):")
    for campaign in sorted(data['campaigns']):
        campaign_short = campaign.replace('Search-', '').replace('-Core-Geos-US', '')
        print(f"   • {campaign_short}")

    return {
        'call_to_quote': call_to_quote,
        'quote_to_deal': quote_to_deal,
        'call_to_deal': call_to_deal,
        'calls': calls,
        'quotes': total_quotes,
        'deals': deals
    }

# Display results
print(f"\n🔍 Analysis Period: {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}")

small_rates = calc_funnel_rates(small_equip_data, "🔧 SMALL EQUIPMENT (Skid-Steers, Mini-Excavators, Telehandlers, Backhoes)")
large_rates = calc_funnel_rates(large_equip_data, "🏗️  LARGE EQUIPMENT (Excavators, Dozers, Loaders, Forklifts, Boom/Scissor Lifts)")

# Comparison
print(f"\n{'=' * 120}")
print(f"📊 COMPARISON: Small vs Large Equipment")
print(f"{'=' * 120}")

print(f"\n{'Metric':<40} {'Small Equipment':>25} {'Large Equipment':>25} {'Difference':>20}")
print(f"{'-' * 120}")

# Call to Quote
diff_c2q = small_rates['call_to_quote'] - large_rates['call_to_quote']
winner_c2q = "🏆 Small" if diff_c2q > 0 else "🏆 Large" if diff_c2q < 0 else "Tie"
print(f"{'📊 Call → Quote Rate':<40} {small_rates['call_to_quote']:>23.1f}% {large_rates['call_to_quote']:>23.1f}% {diff_c2q:>18.1f}pp {winner_c2q}")

# Quote to Deal
diff_q2d = small_rates['quote_to_deal'] - large_rates['quote_to_deal']
winner_q2d = "🏆 Small" if diff_q2d > 0 else "🏆 Large" if diff_q2d < 0 else "Tie"
print(f"{'🎯 Quote → Deal Rate':<40} {small_rates['quote_to_deal']:>23.1f}% {large_rates['quote_to_deal']:>23.1f}% {diff_q2d:>18.1f}pp {winner_q2d}")

# Call to Deal
diff_c2d = small_rates['call_to_deal'] - large_rates['call_to_deal']
winner_c2d = "🏆 Small" if diff_c2d > 0 else "🏆 Large" if diff_c2d < 0 else "Tie"
print(f"{'💰 Call → Deal Rate':<40} {small_rates['call_to_deal']:>23.1f}% {large_rates['call_to_deal']:>23.1f}% {diff_c2d:>18.1f}pp {winner_c2d}")

print(f"\n{'Volume Metrics':<40} {'Small Equipment':>25} {'Large Equipment':>25}")
print(f"{'-' * 120}")
print(f"{'📞 Total Calls':<40} {int(small_rates['calls']):>25} {int(large_rates['calls']):>25}")
print(f"{'💬 Total Quotes':<40} {int(small_rates['quotes']):>25} {int(large_rates['quotes']):>25}")
print(f"{'🎉 Total Deals':<40} {int(small_rates['deals']):>25} {int(large_rates['deals']):>25}")

# Key insights
print(f"\n{'=' * 120}")
print(f"💡 KEY INSIGHTS")
print(f"{'=' * 120}")

if diff_c2q > 5:
    print(f"\n✅ Small equipment has significantly better call-to-quote conversion (+{diff_c2q:.1f}pp)")
elif diff_c2q < -5:
    print(f"\n✅ Large equipment has significantly better call-to-quote conversion (+{abs(diff_c2q):.1f}pp)")
else:
    print(f"\n📊 Call-to-quote rates are similar between small and large equipment (within {abs(diff_c2q):.1f}pp)")

if diff_q2d > 5:
    print(f"✅ Small equipment has significantly better quote-to-deal conversion (+{diff_q2d:.1f}pp)")
elif diff_q2d < -5:
    print(f"✅ Large equipment has significantly better quote-to-deal conversion (+{abs(diff_q2d):.1f}pp)")
else:
    print(f"📊 Quote-to-deal rates are similar between small and large equipment (within {abs(diff_q2d):.1f}pp)")

if small_rates['deals'] > large_rates['deals']:
    print(f"\n🏆 Small equipment generated more deals: {int(small_rates['deals'])} vs {int(large_rates['deals'])}")
elif large_rates['deals'] > small_rates['deals']:
    print(f"\n🏆 Large equipment generated more deals: {int(large_rates['deals'])} vs {int(small_rates['deals'])}")

print(f"\n{'=' * 120}")
