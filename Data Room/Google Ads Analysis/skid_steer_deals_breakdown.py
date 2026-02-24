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
print(f"🔍 SKID-STEER DEALS ANALYSIS - Which Campaign Generated the Deals?")
print("=" * 140)

# Query for deals by ad group for both periods
query = f"""
    SELECT
        campaign.name,
        campaign.id,
        ad_group.name,
        ad_group.id,
        segments.date,
        segments.conversion_action_name,
        metrics.conversions
    FROM ad_group
    WHERE segments.date BETWEEN '{period1_start}' AND '{period2_end}'
        AND campaign.status = 'ENABLED'
        AND ad_group.status = 'ENABLED'
        AND segments.conversion_action_name LIKE '%Closed Won%'
        AND metrics.conversions > 0
        AND campaign.name LIKE '%US%'
        AND campaign.name NOT LIKE '%Expansion%'
"""

response = ga_service.search(customer_id=customer_id, query=query)

# Organize deals by period
period1_deals = []
period2_deals = []

for row in response:
    campaign_name = row.campaign.name
    ad_group_name = row.ad_group.name
    date = row.segments.date
    conv_name = row.segments.conversion_action_name
    conversions = row.metrics.conversions

    deal_info = {
        'campaign': campaign_name,
        'ad_group': ad_group_name,
        'date': date,
        'conversion_type': conv_name,
        'deals': int(conversions)
    }

    if period1_start <= date <= period1_end:
        period1_deals.append(deal_info)
    elif period2_start <= date <= period2_end:
        period2_deals.append(deal_info)

# Print Period 1 results
print(f"\n{'━' * 140}")
print(f"📊 PERIOD 1 (Feb 1-10, 2026) - {len(period1_deals)} Deal Record(s)")
print(f"{'━' * 140}")

if period1_deals:
    period1_by_campaign = {}
    for deal in period1_deals:
        campaign = deal['campaign']
        if campaign not in period1_by_campaign:
            period1_by_campaign[campaign] = {'total_deals': 0, 'ad_groups': {}}

        period1_by_campaign[campaign]['total_deals'] += deal['deals']

        ad_group = deal['ad_group']
        if ad_group not in period1_by_campaign[campaign]['ad_groups']:
            period1_by_campaign[campaign]['ad_groups'][ad_group] = 0
        period1_by_campaign[campaign]['ad_groups'][ad_group] += deal['deals']

    for campaign, data in period1_by_campaign.items():
        print(f"\n🎯 Campaign: {campaign}")
        print(f"   Total Deals: {data['total_deals']}")
        print(f"   Ad Group Breakdown:")
        for ad_group, deals in data['ad_groups'].items():
            print(f"      • {ad_group}: {deals} deal(s)")
else:
    print("\nNo deals found in Period 1")

# Print Period 2 results
print(f"\n{'━' * 140}")
print(f"📊 PERIOD 2 (Feb 11-20, 2026) - {len(period2_deals)} Deal Record(s)")
print(f"{'━' * 140}")

if period2_deals:
    period2_by_campaign = {}
    for deal in period2_deals:
        campaign = deal['campaign']
        if campaign not in period2_by_campaign:
            period2_by_campaign[campaign] = {'total_deals': 0, 'ad_groups': {}}

        period2_by_campaign[campaign]['total_deals'] += deal['deals']

        ad_group = deal['ad_group']
        if ad_group not in period2_by_campaign[campaign]['ad_groups']:
            period2_by_campaign[campaign]['ad_groups'][ad_group] = 0
        period2_by_campaign[campaign]['ad_groups'][ad_group] += deal['deals']

    for campaign, data in period2_by_campaign.items():
        print(f"\n🎯 Campaign: {campaign}")
        print(f"   Total Deals: {data['total_deals']}")
        print(f"   Ad Group Breakdown:")
        for ad_group, deals in data['ad_groups'].items():
            print(f"      • {ad_group}: {deals} deal(s)")
else:
    print("\nNo deals found in Period 2")

# Check if Loader campaign has Skid-Steer ad groups
print(f"\n{'=' * 140}")
print(f"🔍 CHECKING FOR SKID-STEER AD GROUPS IN BOTH CAMPAIGNS")
print(f"{'=' * 140}")

query_adgroups = f"""
    SELECT
        campaign.name,
        ad_group.name,
        ad_group.status
    FROM ad_group
    WHERE campaign.status = 'ENABLED'
        AND campaign.name LIKE '%US%'
        AND campaign.name NOT LIKE '%Expansion%'
        AND ad_group.name LIKE '%Skid%'
"""

response_adgroups = ga_service.search(customer_id=customer_id, query=query_adgroups)

print(f"\nSkid-Steer Ad Groups Found:")
for row in response_adgroups:
    status = "ACTIVE" if row.ad_group.status.name == "ENABLED" else "PAUSED"
    print(f"   • Campaign: {row.campaign.name}")
    print(f"     Ad Group: {row.ad_group.name} ({status})")
    print()

print(f"{'=' * 140}")
print(f"✅ ANALYSIS COMPLETE")
print(f"{'=' * 140}")
