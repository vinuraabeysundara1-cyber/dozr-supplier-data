from google.ads.googleads.client import GoogleAdsClient
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Load credentials
client = GoogleAdsClient.load_from_storage('/Users/vinuraabeysundara/Desktop/ICG/DOZR/Data Room/Config/google-ads.yaml')
ga_service = client.get_service('GoogleAdsService')
customer_id = '8531896842'

# Define period - February 2026
start_date = '2026-02-01'
end_date = '2026-02-23'

print("=" * 160)
print(f"🚜 SKID STEER ANALYSIS - FEBRUARY 2026")
print(f"Period: {start_date} to {end_date}")
print("=" * 160)

# ==================== PART 1: DEALS AND SPEND ====================
print("\n\n📊 PART 1: SKID STEER DEALS AND AD SPEND")
print("=" * 160)

# Query for skid steer campaigns with spend
query_spend_campaign = f"""
    SELECT
        campaign.name,
        ad_group.name,
        metrics.cost_micros,
        metrics.clicks,
        metrics.impressions
    FROM ad_group
    WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.status = 'ENABLED'
        AND ad_group.status = 'ENABLED'
        AND campaign.name LIKE '%US%'
        AND campaign.name LIKE '%Skid%'
"""

# Query for ad groups with "Skid" in name (might be in other campaigns)
query_spend_adgroup = f"""
    SELECT
        campaign.name,
        ad_group.name,
        metrics.cost_micros,
        metrics.clicks,
        metrics.impressions
    FROM ad_group
    WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.status = 'ENABLED'
        AND ad_group.status = 'ENABLED'
        AND campaign.name LIKE '%US%'
        AND ad_group.name LIKE '%Skid%'
"""

# Collect all responses
all_spend_data = []

response_spend_campaign = ga_service.search(customer_id=customer_id, query=query_spend_campaign)
for row in response_spend_campaign:
    all_spend_data.append(row)

response_spend_adgroup = ga_service.search(customer_id=customer_id, query=query_spend_adgroup)
for row in response_spend_adgroup:
    # Check for duplicates
    is_duplicate = False
    for existing_row in all_spend_data:
        if (existing_row.campaign.name == row.campaign.name and
            existing_row.ad_group.name == row.ad_group.name):
            is_duplicate = True
            break
    if not is_duplicate:
        all_spend_data.append(row)

skid_steer_campaigns = {}
total_spend = 0
total_clicks = 0
total_impressions = 0

print("\n💰 Ad Spend Breakdown:")
print(f"\n{'Campaign':<60} {'Ad Group':<40} {'Spend':>12} {'Clicks':>8} {'Impr':>10}")
print("-" * 160)

for row in all_spend_data:
    campaign = row.campaign.name
    ad_group = row.ad_group.name
    spend = row.metrics.cost_micros / 1_000_000
    clicks = row.metrics.clicks
    impressions = row.metrics.impressions

    campaign_short = campaign[:57] + '...' if len(campaign) > 60 else campaign
    ad_group_short = ad_group[:37] + '...' if len(ad_group) > 40 else ad_group

    print(f"{campaign_short:<60} {ad_group_short:<40} ${spend:>11,.2f} {clicks:>8} {impressions:>10,}")

    # Aggregate by campaign
    if campaign not in skid_steer_campaigns:
        skid_steer_campaigns[campaign] = {
            'spend': 0,
            'clicks': 0,
            'impressions': 0,
            'ad_groups': []
        }

    skid_steer_campaigns[campaign]['spend'] += spend
    skid_steer_campaigns[campaign]['clicks'] += clicks
    skid_steer_campaigns[campaign]['impressions'] += impressions
    skid_steer_campaigns[campaign]['ad_groups'].append(ad_group)

    total_spend += spend
    total_clicks += clicks
    total_impressions += impressions

print("-" * 160)
print(f"{'TOTAL SKID STEER AD SPEND':<101} ${total_spend:>11,.2f} {total_clicks:>8} {total_impressions:>10,}")

# ==================== PART 2: SKID STEER DEALS ====================
print("\n\n📊 PART 2: SKID STEER DEALS (CLOSED WON)")
print("=" * 160)

# Query for deals from campaigns with "Skid" in the name
query_deals_campaign = f"""
    SELECT
        campaign.name,
        ad_group.name,
        segments.date,
        segments.conversion_action_name,
        metrics.conversions,
        metrics.conversions_value
    FROM ad_group
    WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.status = 'ENABLED'
        AND ad_group.status = 'ENABLED'
        AND campaign.name LIKE '%US%'
        AND campaign.name LIKE '%Skid%'
        AND metrics.conversions > 0
        AND segments.conversion_action_name LIKE '%Closed Won%'
"""

response_deals_campaign = ga_service.search(customer_id=customer_id, query=query_deals_campaign)

deals_from_campaign = []
for row in response_deals_campaign:
    deals_from_campaign.append({
        'date': row.segments.date,
        'campaign': row.campaign.name,
        'ad_group': row.ad_group.name,
        'deals': int(row.metrics.conversions),
        'value': row.metrics.conversions_value
    })

# Query for deals from ad groups with "Skid" in the name (might be in other campaigns)
query_deals_adgroup = f"""
    SELECT
        campaign.name,
        ad_group.name,
        segments.date,
        segments.conversion_action_name,
        metrics.conversions,
        metrics.conversions_value
    FROM ad_group
    WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.status = 'ENABLED'
        AND ad_group.status = 'ENABLED'
        AND campaign.name LIKE '%US%'
        AND ad_group.name LIKE '%Skid%'
        AND metrics.conversions > 0
        AND segments.conversion_action_name LIKE '%Closed Won%'
"""

response_deals_adgroup = ga_service.search(customer_id=customer_id, query=query_deals_adgroup)

deals_from_adgroup = []
for row in response_deals_adgroup:
    # Check if this deal is already in deals_from_campaign to avoid duplicates
    is_duplicate = False
    for deal in deals_from_campaign:
        if (deal['date'] == row.segments.date and
            deal['campaign'] == row.campaign.name and
            deal['ad_group'] == row.ad_group.name):
            is_duplicate = True
            break

    if not is_duplicate:
        deals_from_adgroup.append({
            'date': row.segments.date,
            'campaign': row.campaign.name,
            'ad_group': row.ad_group.name,
            'deals': int(row.metrics.conversions),
            'value': row.metrics.conversions_value
        })

# Combine all deals
all_deals = deals_from_campaign + deals_from_adgroup

if all_deals:
    print(f"\n🎯 Skid Steer Deals Found: {len(all_deals)}")
    print(f"\n{'Date':<15} {'Campaign':<50} {'Ad Group':<40} {'Deals':>7} {'Value':>14}")
    print("-" * 160)

    total_deals = 0
    total_value = 0

    for deal in sorted(all_deals, key=lambda x: x['date']):
        campaign_short = deal['campaign'].replace('Search-', '').replace('-Core-Geos-US', '').replace('-V3', '')[:47]
        ad_group_short = deal['ad_group'][:37] + '...' if len(deal['ad_group']) > 40 else deal['ad_group']

        print(f"{deal['date']:<15} {campaign_short:<50} {ad_group_short:<40} {deal['deals']:>7} ${deal['value']:>13,.2f}")

        total_deals += deal['deals']
        total_value += deal['value']

    print("-" * 160)
    print(f"{'TOTAL':<106} {int(total_deals):>7} ${total_value:>13,.2f}")

    # Calculate average
    avg_deal_value = total_value / total_deals if total_deals > 0 else 0

    print(f"\n\n📊 SKID STEER METRICS SUMMARY")
    print("=" * 160)
    print(f"\n💰 Financial Performance:")
    print(f"   • Total Ad Spend: ${total_spend:,.2f}")
    print(f"   • Total Deals: {int(total_deals)}")
    print(f"   • Total Deal Value: ${total_value:,.2f}")
    print(f"   • Average Deal Value (GMV): ${avg_deal_value:,.2f}")
    print(f"   • ROAS: {total_value / total_spend if total_spend > 0 else 0:.2f}x")
    print(f"   • Cost Per Deal: ${total_spend / total_deals if total_deals > 0 else 0:,.2f}")

    print(f"\n📈 Efficiency Metrics:")
    print(f"   • Clicks: {total_clicks:,}")
    print(f"   • Impressions: {total_impressions:,}")
    print(f"   • CTR: {total_clicks / total_impressions * 100 if total_impressions > 0 else 0:.2f}%")
    print(f"   • CPC: ${total_spend / total_clicks if total_clicks > 0 else 0:.2f}")

else:
    print("\n⚠️  No skid steer deals found in February 2026")

# ==================== PART 3: CONVERSION FUNNEL ====================
print("\n\n📊 PART 3: SKID STEER CONVERSION FUNNEL")
print("=" * 160)

# Get all conversions for skid steer campaigns/ad groups
query_all_conv_campaign = f"""
    SELECT
        campaign.name,
        ad_group.name,
        segments.conversion_action_name,
        metrics.conversions
    FROM ad_group
    WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.status = 'ENABLED'
        AND ad_group.status = 'ENABLED'
        AND campaign.name LIKE '%US%'
        AND campaign.name LIKE '%Skid%'
        AND metrics.conversions > 0
"""

query_all_conv_adgroup = f"""
    SELECT
        campaign.name,
        ad_group.name,
        segments.conversion_action_name,
        metrics.conversions
    FROM ad_group
    WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.status = 'ENABLED'
        AND ad_group.status = 'ENABLED'
        AND campaign.name LIKE '%US%'
        AND ad_group.name LIKE '%Skid%'
        AND metrics.conversions > 0
"""

all_conv_data = []

response_all_conv_campaign = ga_service.search(customer_id=customer_id, query=query_all_conv_campaign)
for row in response_all_conv_campaign:
    all_conv_data.append(row)

response_all_conv_adgroup = ga_service.search(customer_id=customer_id, query=query_all_conv_adgroup)
for row in response_all_conv_adgroup:
    # Check for duplicates
    is_duplicate = False
    for existing_row in all_conv_data:
        if (existing_row.campaign.name == row.campaign.name and
            existing_row.ad_group.name == row.ad_group.name and
            existing_row.segments.conversion_action_name == row.segments.conversion_action_name):
            is_duplicate = True
            break
    if not is_duplicate:
        all_conv_data.append(row)

calls = 0
quotes = 0
deals = 0

for row in all_conv_data:
    conv_name = row.segments.conversion_action_name
    conversions = row.metrics.conversions

    if 'Phone Call' in conv_name or 'Calls from ads' in conv_name:
        calls += conversions
    elif 'quote' in conv_name.lower():
        quotes += conversions
    elif 'Closed Won' in conv_name:
        deals += conversions

print(f"\n📞 Conversion Funnel:")
print(f"   • Calls: {int(calls)}")
print(f"   • Quotes: {int(quotes)}")
print(f"   • Deals: {int(deals)}")

if calls > 0 and deals > 0:
    print(f"\n🔄 Conversion Rates:")
    print(f"   • Call → Quote: {quotes / calls * 100 if calls > 0 else 0:.1f}%")
    print(f"   • Quote → Deal: {deals / quotes * 100 if quotes > 0 else 0:.1f}%")
    print(f"   • Call → Deal: {deals / calls * 100:.1f}%")

# ==================== PART 4: CAMPAIGN BREAKDOWN ====================
print("\n\n📊 PART 4: CAMPAIGN BREAKDOWN")
print("=" * 160)

print(f"\n{'Campaign':<70} {'Spend':>12} {'Clicks':>8} {'Ad Groups':>12}")
print("-" * 160)

for campaign, data in sorted(skid_steer_campaigns.items(), key=lambda x: x[1]['spend'], reverse=True):
    campaign_short = campaign.replace('Search-', '').replace('-Core-Geos-US', '').replace('-V3', '')[:67]
    num_ad_groups = len(set(data['ad_groups']))

    print(f"{campaign_short:<70} ${data['spend']:>11,.2f} {data['clicks']:>8} {num_ad_groups:>12}")

print("\n\n" + "=" * 160)
print("✅ SKID STEER ANALYSIS COMPLETE")
print("=" * 160)

print(f"\n\n📋 QUICK ANSWERS:")
print(f"   1. How many skid steer deals this month? {int(total_deals) if all_deals else 0}")
print(f"   2. How much spent on skid steer ad groups? ${total_spend:,.2f}")
print(f"   3. Average GMV on skid steer deals? ${avg_deal_value if all_deals else 0:,.2f}")
