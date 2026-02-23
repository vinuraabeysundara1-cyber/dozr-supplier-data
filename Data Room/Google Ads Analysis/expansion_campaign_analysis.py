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

print("=" * 140)
print(f"📞 EXPANSION CAMPAIGN ANALYSIS - Calls Since Launch (Feb 10-23, 2026)")
print("=" * 140)

# Query for expansion campaigns
query = f"""
    SELECT
        campaign.name,
        campaign.id,
        metrics.cost_micros,
        metrics.clicks,
        metrics.impressions,
        metrics.conversions,
        metrics.conversions_value
    FROM campaign
    WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.status = 'ENABLED'
        AND campaign.name LIKE '%Expansion%'
"""

response = ga_service.search(customer_id=customer_id, query=query)

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
            'value': 0
        }

    campaign_data[campaign_name]['spend'] += row.metrics.cost_micros / 1_000_000
    campaign_data[campaign_name]['clicks'] += row.metrics.clicks
    campaign_data[campaign_name]['impressions'] += row.metrics.impressions
    campaign_data[campaign_name]['conversions'] += row.metrics.conversions
    campaign_data[campaign_name]['value'] += row.metrics.conversions_value

# Get conversion breakdown by type
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

# Track conversions by campaign and type
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

    # Categorize conversions
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

# Get daily spend breakdown (separate query)
query_daily_spend = f"""
    SELECT
        segments.date,
        metrics.cost_micros
    FROM campaign
    WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.status = 'ENABLED'
        AND campaign.name LIKE '%Expansion%'
"""

response_daily_spend = ga_service.search(customer_id=customer_id, query=query_daily_spend)

# Organize by date
daily_data = {}

for row in response_daily_spend:
    date = row.segments.date
    spend = row.metrics.cost_micros / 1_000_000

    if date not in daily_data:
        daily_data[date] = {
            'spend': 0,
            'phone_calls': 0,
            'calls_from_ads': 0,
            'quotes': 0,
            'deals': 0,
            'total_conversions': 0
        }

    daily_data[date]['spend'] += spend

# Get daily conversions breakdown (separate query)
query_daily_conv = f"""
    SELECT
        segments.date,
        segments.conversion_action_name,
        metrics.conversions
    FROM campaign
    WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.status = 'ENABLED'
        AND campaign.name LIKE '%Expansion%'
        AND metrics.conversions > 0
"""

response_daily_conv = ga_service.search(customer_id=customer_id, query=query_daily_conv)

for row in response_daily_conv:
    date = row.segments.date
    conv_name = row.segments.conversion_action_name
    conversions = row.metrics.conversions

    if date not in daily_data:
        daily_data[date] = {
            'spend': 0,
            'phone_calls': 0,
            'calls_from_ads': 0,
            'quotes': 0,
            'deals': 0,
            'total_conversions': 0
        }

    if conv_name == 'Phone Call':
        daily_data[date]['phone_calls'] += conversions
    elif conv_name == 'Calls from ads':
        daily_data[date]['calls_from_ads'] += conversions
    elif 'quote' in conv_name.lower():
        daily_data[date]['quotes'] += conversions
    elif 'Closed Won' in conv_name or 'Deal' in conv_name:
        daily_data[date]['deals'] += conversions

    daily_data[date]['total_conversions'] += conversions

# Print Summary
print(f"\n{'━' * 140}")
print(f"📊 EXPANSION CAMPAIGNS SUMMARY")
print(f"{'━' * 140}")

if not campaign_data:
    print("\n❌ No expansion campaigns found")
else:
    print(f"\n{'Campaign':<50} {'Spend':>12} {'Clicks':>8} {'Impressions':>12} {'Conversions':>12} {'ROAS':>8}")
    print("-" * 140)

    total_spend = 0
    total_clicks = 0
    total_impressions = 0
    total_conversions = 0
    total_value = 0

    for campaign_name, data in campaign_data.items():
        roas = data['value'] / data['spend'] if data['spend'] > 0 else 0
        print(f"{campaign_name:<50} ${data['spend']:>11,.2f} {data['clicks']:>8} {data['impressions']:>12,} {int(data['conversions']):>12} {roas:>6.2f}x")

        total_spend += data['spend']
        total_clicks += data['clicks']
        total_impressions += data['impressions']
        total_conversions += data['conversions']
        total_value += data['value']

    print("-" * 140)
    total_roas = total_value / total_spend if total_spend > 0 else 0
    print(f"{'TOTAL':<50} ${total_spend:>11,.2f} {total_clicks:>8} {total_impressions:>12,} {int(total_conversions):>12} {total_roas:>6.2f}x")

# Print Conversion Breakdown
print(f"\n{'━' * 140}")
print(f"📞 CALL BREAKDOWN BY CAMPAIGN")
print(f"{'━' * 140}")

total_phone_calls = 0
total_calls_from_ads = 0
total_quotes = 0
total_deals = 0

if campaign_conversions:
    print(f"\n{'Campaign':<50} {'Phone Calls':>12} {'Calls from Ads':>16} {'Total Calls':>12} {'Quotes':>8} {'Deals':>7}")
    print("-" * 140)

    for campaign_name in campaign_data.keys():
        conv_data = campaign_conversions.get(campaign_name, {
            'phone_calls': 0, 'calls_from_ads': 0, 'quotes': 0, 'deals': 0
        })

        phone_calls = int(conv_data['phone_calls'])
        calls_from_ads = int(conv_data['calls_from_ads'])
        total_calls = phone_calls + calls_from_ads
        quotes = int(conv_data['quotes'])
        deals = int(conv_data['deals'])

        print(f"{campaign_name:<50} {phone_calls:>12} {calls_from_ads:>16} {total_calls:>12} {quotes:>8} {deals:>7}")

        total_phone_calls += phone_calls
        total_calls_from_ads += calls_from_ads
        total_quotes += quotes
        total_deals += deals

    print("-" * 140)
    grand_total_calls = total_phone_calls + total_calls_from_ads
    print(f"{'TOTAL':<50} {total_phone_calls:>12} {total_calls_from_ads:>16} {grand_total_calls:>12} {total_quotes:>8} {total_deals:>7}")

# Print Daily Breakdown
print(f"\n{'━' * 140}")
print(f"📅 DAILY PERFORMANCE BREAKDOWN")
print(f"{'━' * 140}")

print(f"\n{'Date':<15} {'Spend':>12} {'Phone Calls':>12} {'Calls from Ads':>16} {'Total Calls':>12} {'Quotes':>8} {'Deals':>7}")
print("-" * 140)

for date in sorted(daily_data.keys()):
    data = daily_data[date]
    total_calls = int(data['phone_calls'] + data['calls_from_ads'])

    print(f"{date:<15} ${data['spend']:>11,.2f} {int(data['phone_calls']):>12} {int(data['calls_from_ads']):>16} {total_calls:>12} {int(data['quotes']):>8} {int(data['deals']):>7}")

# Calculate metrics
print(f"\n{'=' * 140}")
print(f"📊 KEY METRICS")
print(f"{'=' * 140}")

if total_spend > 0 and grand_total_calls > 0:
    cost_per_call = total_spend / grand_total_calls
    print(f"\n✅ Total Calls Since Launch (Feb 10): {grand_total_calls}")
    print(f"   • Phone Calls: {total_phone_calls}")
    print(f"   • Calls from Ads: {total_calls_from_ads}")
    print(f"\n💰 Total Spend: ${total_spend:,.2f}")
    print(f"💵 Cost Per Call: ${cost_per_call:.2f}")
    print(f"📈 Total Conversions: {int(total_conversions)}")

    if total_quotes > 0:
        call_to_quote_rate = (total_quotes / grand_total_calls * 100) if grand_total_calls > 0 else 0
        print(f"📋 Quotes: {total_quotes} ({call_to_quote_rate:.1f}% of calls)")

    if total_deals > 0:
        call_to_deal_rate = (total_deals / grand_total_calls * 100) if grand_total_calls > 0 else 0
        print(f"🎉 Deals: {total_deals} ({call_to_deal_rate:.1f}% of calls)")

print(f"\n{'=' * 140}")
print("✅ ANALYSIS COMPLETE")
print(f"{'=' * 140}")
