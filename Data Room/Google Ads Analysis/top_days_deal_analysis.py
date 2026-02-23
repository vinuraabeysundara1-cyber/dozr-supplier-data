from google.ads.googleads.client import GoogleAdsClient
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Load credentials
client = GoogleAdsClient.load_from_storage('/Users/vinuraabeysundara/Desktop/ICG/DOZR/Data Room/Config/google-ads.yaml')
ga_service = client.get_service('GoogleAdsService')
customer_id = '8531896842'

# Top 5 performing days
top_days = {
    '2026-02-04': {'name': 'Feb 4 (Wed)', 'deals': 5, 'roas': '13.87x'},
    '2026-02-13': {'name': 'Feb 13 (Fri)', 'deals': 3, 'roas': '11.24x'},
    '2026-02-05': {'name': 'Feb 5 (Thu)', 'deals': 2, 'roas': '11.22x'},
    '2026-02-19': {'name': 'Feb 19 (Thu)', 'deals': 1, 'roas': '7.11x'},
    '2026-02-18': {'name': 'Feb 18 (Wed)', 'deals': 4, 'roas': '6.46x'}
}

print("=" * 160)
print(f"🏆 TOP 5 DAYS - DEAL BREAKDOWN ANALYSIS")
print("=" * 160)

for date, info in sorted(top_days.items()):
    print(f"\n{'━' * 160}")
    print(f"📅 {info['name']} - {info['deals']} Deals ({info['roas']} ROAS)")
    print(f"{'━' * 160}")

    # Query for deals on this specific date by ad group
    query = f"""
        SELECT
            campaign.name,
            ad_group.name,
            segments.conversion_action_name,
            metrics.conversions,
            metrics.conversions_value
        FROM ad_group
        WHERE segments.date = '{date}'
            AND campaign.status = 'ENABLED'
            AND ad_group.status = 'ENABLED'
            AND campaign.name LIKE '%US%'
            AND metrics.conversions > 0
            AND segments.conversion_action_name LIKE '%Closed Won%'
    """

    response = ga_service.search(customer_id=customer_id, query=query)

    deal_data = []
    for row in response:
        campaign_name = row.campaign.name
        ad_group_name = row.ad_group.name
        conv_name = row.segments.conversion_action_name
        conversions = row.metrics.conversions
        value = row.metrics.conversions_value

        deal_data.append({
            'campaign': campaign_name,
            'ad_group': ad_group_name,
            'conversion_type': conv_name,
            'deals': int(conversions),
            'value': value
        })

    if deal_data:
        print(f"\n{'Campaign':<50} {'Ad Group':<40} {'Deals':>7} {'Value':>12}")
        print("-" * 160)

        total_deals = 0
        total_value = 0

        for deal in deal_data:
            # Extract equipment type from campaign name
            campaign_short = deal['campaign'].replace('Search-', '').replace('-Core-Geos-US', '').replace('-V3', '').replace('-Expansion', '')

            print(f"{campaign_short:<50} {deal['ad_group']:<40} {deal['deals']:>7} ${deal['value']:>11,.2f}")

            total_deals += deal['deals']
            total_value += deal['value']

        print("-" * 160)
        print(f"{'TOTAL':<91} {total_deals:>7} ${total_value:>11,.2f}")

        # Get all other conversions for context
        query_all_conv = f"""
            SELECT
                campaign.name,
                ad_group.name,
                segments.conversion_action_name,
                metrics.conversions
            FROM ad_group
            WHERE segments.date = '{date}'
                AND campaign.status = 'ENABLED'
                AND ad_group.status = 'ENABLED'
                AND campaign.name LIKE '%US%'
                AND metrics.conversions > 0
        """

        response_all = ga_service.search(customer_id=customer_id, query=query_all_conv)

        calls_data = {}
        quotes_data = {}

        for row in response_all:
            campaign_name = row.campaign.name
            ad_group_name = row.ad_group.name
            conv_name = row.segments.conversion_action_name
            conversions = row.metrics.conversions

            key = f"{campaign_name}|{ad_group_name}"

            if conv_name == 'Phone Call' or conv_name == 'Calls from ads':
                if key not in calls_data:
                    calls_data[key] = 0
                calls_data[key] += conversions
            elif 'quote' in conv_name.lower():
                if key not in quotes_data:
                    quotes_data[key] = 0
                quotes_data[key] += conversions

        # Show calls and quotes for deal-generating ad groups
        print(f"\n📊 Supporting Metrics (Calls & Quotes for these ad groups):")
        print(f"{'Campaign':<50} {'Ad Group':<40} {'Calls':>7} {'Quotes':>8}")
        print("-" * 160)

        for deal in deal_data:
            key = f"{deal['campaign']}|{deal['ad_group']}"
            calls = int(calls_data.get(key, 0))
            quotes = int(quotes_data.get(key, 0))

            campaign_short = deal['campaign'].replace('Search-', '').replace('-Core-Geos-US', '').replace('-V3', '').replace('-Expansion', '')

            print(f"{campaign_short:<50} {deal['ad_group']:<40} {calls:>7} {quotes:>8}")

    else:
        print(f"\n⚠️  No deal data found for this date")

# Summary analysis
print(f"\n{'=' * 160}")
print(f"📊 OVERALL ANALYSIS - 15 DEALS ACROSS TOP 5 DAYS")
print(f"{'=' * 160}")

# Aggregate by campaign
print(f"\n🎯 Deals by Campaign (Top 5 Days):")

# Query all deals for top 5 days
all_dates = "', '".join(top_days.keys())
query_summary = f"""
    SELECT
        campaign.name,
        ad_group.name,
        segments.conversion_action_name,
        metrics.conversions,
        metrics.conversions_value
    FROM ad_group
    WHERE segments.date IN ('{all_dates}')
        AND campaign.status = 'ENABLED'
        AND ad_group.status = 'ENABLED'
        AND campaign.name LIKE '%US%'
        AND metrics.conversions > 0
        AND segments.conversion_action_name LIKE '%Closed Won%'
"""

response_summary = ga_service.search(customer_id=customer_id, query=query_summary)

campaign_deals = {}
adgroup_deals = {}

for row in response_summary:
    campaign_name = row.campaign.name
    ad_group_name = row.ad_group.name
    conversions = row.metrics.conversions
    value = row.metrics.conversions_value

    # Aggregate by campaign
    if campaign_name not in campaign_deals:
        campaign_deals[campaign_name] = {'deals': 0, 'value': 0}
    campaign_deals[campaign_name]['deals'] += conversions
    campaign_deals[campaign_name]['value'] += value

    # Aggregate by ad group
    key = f"{campaign_name}|{ad_group_name}"
    if key not in adgroup_deals:
        adgroup_deals[key] = {'deals': 0, 'value': 0, 'campaign': campaign_name, 'ad_group': ad_group_name}
    adgroup_deals[key]['deals'] += conversions
    adgroup_deals[key]['value'] += value

# Sort and display campaigns
sorted_campaigns = sorted(campaign_deals.items(), key=lambda x: x[1]['deals'], reverse=True)

print(f"\n{'Campaign':<70} {'Deals':>7} {'Value':>14}")
print("-" * 160)

for campaign, data in sorted_campaigns:
    campaign_short = campaign.replace('Search-', '').replace('-Core-Geos-US', '').replace('-V3', '').replace('-Expansion', '')
    print(f"{campaign_short:<70} {int(data['deals']):>7} ${data['value']:>13,.2f}")

# Display ad groups
print(f"\n🎯 Deals by Ad Group (Top 5 Days):")

sorted_adgroups = sorted(adgroup_deals.items(), key=lambda x: x[1]['deals'], reverse=True)

print(f"\n{'Campaign':<50} {'Ad Group':<40} {'Deals':>7} {'Value':>14}")
print("-" * 160)

for key, data in sorted_adgroups:
    campaign_short = data['campaign'].replace('Search-', '').replace('-Core-Geos-US', '').replace('-V3', '').replace('-Expansion', '')
    print(f"{campaign_short:<50} {data['ad_group']:<40} {int(data['deals']):>7} ${data['value']:>13,.2f}")

print(f"\n{'=' * 160}")
print("✅ ANALYSIS COMPLETE")
print(f"{'=' * 160}")
