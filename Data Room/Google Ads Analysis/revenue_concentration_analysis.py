from google.ads.googleads.client import GoogleAdsClient
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Load credentials
client = GoogleAdsClient.load_from_storage('/Users/vinuraabeysundara/Desktop/ICG/DOZR/Data Room/Config/google-ads.yaml')
ga_service = client.get_service('GoogleAdsService')
customer_id = '8531896842'

print("=" * 140)
print("💰 REVENUE CONCENTRATION ANALYSIS - FEBRUARY 2026")
print("Period: February 1-23, 2026")
print("=" * 140)

start_date = '2026-02-01'
end_date = '2026-02-23'

# Query for conversions by campaign (without cost_micros)
query_conv = f"""
    SELECT
        campaign.name,
        segments.conversion_action_name,
        metrics.conversions,
        metrics.conversions_value
    FROM campaign
    WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.status = 'ENABLED'
        AND campaign.name LIKE '%US%'
        AND metrics.conversions > 0
        AND segments.conversion_action_name LIKE '%Closed Won%'
"""

response_conv = ga_service.search(customer_id=customer_id, query=query_conv)

campaign_data = defaultdict(lambda: {'deals': 0, 'value': 0, 'spend': 0})

for row in response_conv:
    campaign = row.campaign.name
    conversions = row.metrics.conversions
    value = row.metrics.conversions_value

    campaign_data[campaign]['deals'] += conversions
    campaign_data[campaign]['value'] += value

# Get spend data separately
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

spend_by_campaign = defaultdict(float)
for row in response_spend:
    campaign = row.campaign.name
    spend = row.metrics.cost_micros / 1_000_000
    spend_by_campaign[campaign] += spend

# Add spend to campaign_data
for campaign in campaign_data:
    campaign_data[campaign]['spend'] = spend_by_campaign.get(campaign, 0)

# Calculate totals
total_value = sum(d['value'] for d in campaign_data.values())
total_deals = sum(d['deals'] for d in campaign_data.values())
total_spend = sum(d['spend'] for d in campaign_data.values())

# Sort by value
sorted_campaigns = sorted(campaign_data.items(), key=lambda x: x[1]['value'], reverse=True)

print("\n📊 CAMPAIGN REVENUE BREAKDOWN")
print("=" * 140)
print(f"\n{'Campaign':<60} {'Deals':>8} {'Revenue':>14} {'Spend':>12} {'ROAS':>8} {'% of Total':>12}")
print("-" * 140)

# Categorize campaigns
dsa_value = 0
dozer_value = 0
other_value = 0

for campaign, data in sorted_campaigns:
    deals = int(data['deals'])
    value = data['value']
    spend = data['spend']
    roas = value / spend if spend > 0 else 0
    pct = (value / total_value * 100) if total_value > 0 else 0

    campaign_short = campaign.replace('Search-', '').replace('-Core-Geos-US', '').replace('-V3', '').replace('-US-2', '')

    print(f"{campaign_short:<60} {deals:>8} ${value:>13,.2f} ${spend:>11,.2f} {roas:>7.2f}x {pct:>11.1f}%")

    # Categorize
    if 'DSA' in campaign:
        dsa_value += value
    elif 'Dozer' in campaign:
        dozer_value += value
    else:
        other_value += value

print("-" * 140)
print(f"{'TOTAL':<60} {int(total_deals):>8} ${total_value:>13,.2f} ${total_spend:>11,.2f} {total_value/total_spend if total_spend > 0 else 0:>7.2f}x {'100.0%':>12}")

# Campaign category breakdown
print("\n\n🎯 CAMPAIGN CATEGORY BREAKDOWN")
print("=" * 140)

dsa_pct = (dsa_value / total_value * 100) if total_value > 0 else 0
dozer_pct = (dozer_value / total_value * 100) if total_value > 0 else 0
other_pct = (other_value / total_value * 100) if total_value > 0 else 0
combined_pct = dsa_pct + dozer_pct

print(f"\n{'Category':<30} {'Revenue':>14} {'% of Total':>12}")
print("-" * 60)
print(f"{'DSA Campaigns':<30} ${dsa_value:>13,.2f} {dsa_pct:>11.1f}%")
print(f"{'Dozer Campaigns':<30} ${dozer_value:>13,.2f} {dozer_pct:>11.1f}%")
print(f"{'DSA + Dozer COMBINED':<30} ${dsa_value + dozer_value:>13,.2f} {combined_pct:>11.1f}%")
print(f"{'All Other Campaigns':<30} ${other_value:>13,.2f} {other_pct:>11.1f}%")
print("-" * 60)
print(f"{'TOTAL':<30} ${total_value:>13,.2f} {'100.0%':>12}")

# Key insight
print("\n\n💡 KEY INSIGHT")
print("=" * 140)
print(f"🎯 DSA and Dozer campaigns generate {combined_pct:.1f}% of total revenue")
print(f"   • DSA: ${dsa_value:,.2f} ({dsa_pct:.1f}%)")
print(f"   • Dozers: ${dozer_value:,.2f} ({dozer_pct:.1f}%)")
print(f"   • Combined: ${dsa_value + dozer_value:,.2f} ({combined_pct:.1f}%)")
print(f"\n⚠️  Revenue is highly concentrated in just 2 campaign types")
print(f"   This creates risk if performance declines (as seen in recent analysis)")

# Top 3 campaigns
print("\n\n🏆 TOP 3 REVENUE GENERATORS")
print("=" * 140)
for i, (campaign, data) in enumerate(sorted_campaigns[:3], 1):
    campaign_short = campaign.replace('Search-', '').replace('-Core-Geos-US', '').replace('-V3', '').replace('-US-2', '')
    pct = (data['value'] / total_value * 100) if total_value > 0 else 0
    roas = data['value'] / data['spend'] if data['spend'] > 0 else 0
    print(f"#{i}. {campaign_short}")
    print(f"    Revenue: ${data['value']:,.2f} ({pct:.1f}% of total) | {int(data['deals'])} deals | {roas:.2f}x ROAS")

print("\n" + "=" * 140)
