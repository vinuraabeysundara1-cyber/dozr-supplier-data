from google.ads.googleads.client import GoogleAdsClient
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Load credentials
client = GoogleAdsClient.load_from_storage('/Users/vinuraabeysundara/Desktop/ICG/DOZR/Data Room/Config/google-ads.yaml')
ga_service = client.get_service('GoogleAdsService')
customer_id = '8531896842'

print("=" * 150)
print("🎯 TARGET ROAS (tROAS) READINESS ANALYSIS")
print("Analyzing conversion volume to determine tROAS eligibility")
print("Counting only: Quotes, Deals (Closed Won), Purchase - EXCLUDING Calls")
print("=" * 150)

# Analyze last 30 days (Feb 1-23 is only 23 days, so we'll use that)
start_date = '2026-02-01'
end_date = '2026-02-23'

print(f"\n📅 Analysis Period: {start_date} to {end_date} (23 days)")
print("=" * 150)

# Query for conversions by campaign
query_conv = f"""
    SELECT
        campaign.name,
        campaign.bidding_strategy_type,
        segments.conversion_action_name,
        metrics.conversions,
        metrics.conversions_value
    FROM campaign
    WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.status = 'ENABLED'
        AND campaign.name LIKE '%US%'
        AND metrics.conversions > 0
"""

response = ga_service.search(customer_id=customer_id, query=query_conv)

campaign_data = defaultdict(lambda: {
    'bidding_strategy': '',
    'calls': 0,
    'quotes': 0,
    'deals': 0,
    'purchases': 0,
    'total_value': 0,
    'eligible_conversions': 0  # quotes + deals + purchases
})

for row in response:
    campaign = row.campaign.name
    bidding_strategy = str(row.campaign.bidding_strategy_type).replace('BiddingStrategyType.', '')
    conv_name = row.segments.conversion_action_name
    conversions = row.metrics.conversions
    value = row.metrics.conversions_value

    campaign_data[campaign]['bidding_strategy'] = bidding_strategy

    # Categorize conversions
    if 'Phone Call' in conv_name or 'Calls from ads' in conv_name:
        campaign_data[campaign]['calls'] += conversions
    elif 'quote' in conv_name.lower():
        campaign_data[campaign]['quotes'] += conversions
        campaign_data[campaign]['eligible_conversions'] += conversions
        campaign_data[campaign]['total_value'] += value
    elif 'Closed Won' in conv_name or 'deal' in conv_name.lower():
        campaign_data[campaign]['deals'] += conversions
        campaign_data[campaign]['eligible_conversions'] += conversions
        campaign_data[campaign]['total_value'] += value
    elif 'purchase' in conv_name.lower():
        campaign_data[campaign]['purchases'] += conversions
        campaign_data[campaign]['eligible_conversions'] += conversions
        campaign_data[campaign]['total_value'] += value

# Get spend data
query_spend = f"""
    SELECT
        campaign.name,
        metrics.cost_micros
    FROM campaign
    WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.status = 'ENABLED'
        AND campaign.name LIKE '%US%'
"""

response_spend = ga_service.search(customer_id=customer_id, query=query_spend)

for row in response_spend:
    campaign = row.campaign.name
    spend = row.metrics.cost_micros / 1_000_000
    if campaign in campaign_data:
        campaign_data[campaign]['spend'] = campaign_data[campaign].get('spend', 0) + spend

# tROAS thresholds
# Google recommends 30+ conversions in last 30 days for optimal performance
# Minimum threshold is typically 15-20 conversions
OPTIMAL_THRESHOLD = 30  # 30 conversions
MINIMUM_THRESHOLD = 15  # 15 conversions (can work but suboptimal)

# Sort by eligible conversions
sorted_campaigns = sorted(campaign_data.items(), key=lambda x: x[1]['eligible_conversions'], reverse=True)

print("\n📊 CAMPAIGN CONVERSION VOLUME ANALYSIS")
print("=" * 150)
print(f"\n{'Campaign':<50} {'Strategy':<20} {'Quotes':>7} {'Deals':>7} {'Purch':>7} {'Total':>7} {'Spend':>12} {'Value':>14} {'ROAS':>8} {'tROAS Ready?':<15}")
print("-" * 150)

ready_for_troas = []
maybe_ready = []
not_ready = []

for campaign, data in sorted_campaigns:
    campaign_short = campaign.replace('Search-', '').replace('-Core-Geos-US', '').replace('-V3', '').replace('-US-2', '')

    quotes = int(data['quotes'])
    deals = int(data['deals'])
    purchases = int(data['purchases'])
    eligible = int(data['eligible_conversions'])
    spend = data.get('spend', 0)
    value = data['total_value']
    roas = value / spend if spend > 0 else 0
    strategy = data['bidding_strategy']

    # Determine readiness
    if eligible >= OPTIMAL_THRESHOLD:
        status = "✅ READY"
        ready_for_troas.append((campaign_short, data))
    elif eligible >= MINIMUM_THRESHOLD:
        status = "⚠️  MAYBE"
        maybe_ready.append((campaign_short, data))
    else:
        status = "❌ NOT READY"
        not_ready.append((campaign_short, data))

    print(f"{campaign_short:<50} {strategy:<20} {quotes:>7} {deals:>7} {purchases:>7} {eligible:>7} ${spend:>11,.2f} ${value:>13,.2f} {roas:>7.2f}x {status:<15}")

# Summary
print("\n\n" + "=" * 150)
print("📈 tROAS READINESS SUMMARY")
print("=" * 150)

print(f"\n✅ READY FOR tROAS ({len(ready_for_troas)} campaigns):")
print(f"   These campaigns have {OPTIMAL_THRESHOLD}+ eligible conversions and are optimal for tROAS")
if ready_for_troas:
    for campaign, data in ready_for_troas:
        print(f"   • {campaign}: {int(data['eligible_conversions'])} conversions, {data['total_value']/data.get('spend', 1):.2f}x ROAS")
else:
    print("   • None")

print(f"\n⚠️  MARGINAL FOR tROAS ({len(maybe_ready)} campaigns):")
print(f"   These campaigns have {MINIMUM_THRESHOLD}-{OPTIMAL_THRESHOLD-1} conversions. Can use tROAS but may have unstable performance")
if maybe_ready:
    for campaign, data in maybe_ready:
        print(f"   • {campaign}: {int(data['eligible_conversions'])} conversions, {data['total_value']/data.get('spend', 1):.2f}x ROAS")
else:
    print("   • None")

print(f"\n❌ NOT READY FOR tROAS ({len(not_ready)} campaigns):")
print(f"   These campaigns have <{MINIMUM_THRESHOLD} conversions. Need more conversion volume before switching to tROAS")
if not_ready:
    for campaign, data in not_ready:
        conversions = int(data['eligible_conversions'])
        needed = MINIMUM_THRESHOLD - conversions
        print(f"   • {campaign}: {conversions} conversions (need {needed} more)")
else:
    print("   • None")

# Weekly conversion rate analysis
days_in_period = 23
weekly_rate = {}

print("\n\n📊 CONVERSION RATE ANALYSIS")
print("=" * 150)
print(f"\nProjected conversions per 30 days (for tROAS stability):")
print("-" * 80)

for campaign, data in sorted_campaigns:
    campaign_short = campaign.replace('Search-', '').replace('-Core-Geos-US', '').replace('-V3', '').replace('-US-2', '')
    eligible = data['eligible_conversions']

    # Project to 30 days
    projected_30day = (eligible / days_in_period) * 30
    weekly_rate[campaign_short] = projected_30day

    status = "✅" if projected_30day >= OPTIMAL_THRESHOLD else "⚠️" if projected_30day >= MINIMUM_THRESHOLD else "❌"

    print(f"{status} {campaign_short:<50} Current: {int(eligible):>3} → Projected 30-day: {projected_30day:>5.1f}")

# Recommendations
print("\n\n💡 RECOMMENDATIONS")
print("=" * 150)

print("\n🎯 IMMEDIATE ACTION - Switch to tROAS:")
if ready_for_troas:
    print("   The following campaigns are ready for Target ROAS bidding:")
    for campaign, data in ready_for_troas:
        current_roas = data['total_value'] / data.get('spend', 1) if data.get('spend', 0) > 0 else 0
        target_roas = current_roas * 0.8  # Start conservative at 80% of current ROAS
        print(f"   • {campaign}")
        print(f"     - Current ROAS: {current_roas:.2f}x")
        print(f"     - Recommended Starting Target ROAS: {target_roas:.0f}% ({target_roas:.2f}x)")
        print(f"     - {int(data['eligible_conversions'])} conversions in 23 days")
else:
    print("   ⚠️  NO campaigns currently have sufficient conversion volume for tROAS")
    print("   Consider:")
    print("   1. Waiting to accumulate more conversions")
    print("   2. Using Maximize Conversion Value instead")
    print("   3. Combining similar campaigns to increase conversion volume")

print("\n⏳ WATCH & WAIT:")
if maybe_ready:
    print("   These campaigns are borderline. Monitor for another week:")
    for campaign, data in maybe_ready:
        print(f"   • {campaign}: {int(data['eligible_conversions'])} conversions")
else:
    print("   • None")

print("\n🔄 OPTIMIZE FIRST:")
if not_ready:
    print("   These campaigns need more optimization before considering tROAS:")
    for campaign, data in not_ready:
        if data['eligible_conversions'] == 0:
            print(f"   • {campaign}: ZERO conversions - consider pausing or major restructuring")
        else:
            print(f"   • {campaign}: {int(data['eligible_conversions'])} conversions - keep using current strategy")

# Important notes
print("\n\n⚠️  IMPORTANT NOTES:")
print("   1. tROAS requires consistent conversion tracking - ensure all conversions are being recorded")
print("   2. When switching to tROAS, expect a 1-2 week learning period with potential performance volatility")
print("   3. Start with a conservative target ROAS (80% of current ROAS) and optimize up")
print("   4. Monitor daily for the first week after switching")
print("   5. Campaigns with <30 conversions may see unstable bidding")
print("   6. Consider using Maximize Conversion Value as an alternative if conversion volume is low")

print("\n" + "=" * 150)
