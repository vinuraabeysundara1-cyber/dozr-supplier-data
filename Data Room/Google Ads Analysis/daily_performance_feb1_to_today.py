from google.ads.googleads.client import GoogleAdsClient
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Load credentials
client = GoogleAdsClient.load_from_storage('/Users/vinuraabeysundara/Desktop/ICG/DOZR/Data Room/Config/google-ads.yaml')
ga_service = client.get_service('GoogleAdsService')
customer_id = '8531896842'

# Define period - Feb 1st to today (Feb 23)
start_date = '2026-02-01'
end_date = '2026-02-23'

print("=" * 160)
print(f"📊 GOOGLE ADS DAILY PERFORMANCE BREAKDOWN")
print(f"Period: {start_date} to {end_date}")
print("=" * 160)

# Query for daily spend and metrics
query_daily_spend = f"""
    SELECT
        segments.date,
        metrics.cost_micros,
        metrics.clicks,
        metrics.impressions,
        metrics.conversions_value
    FROM campaign
    WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.status = 'ENABLED'
        AND campaign.name LIKE '%US%'
"""

response_spend = ga_service.search(customer_id=customer_id, query=query_daily_spend)

# Organize by date
daily_data = {}

for row in response_spend:
    date = row.segments.date
    spend = row.metrics.cost_micros / 1_000_000
    clicks = row.metrics.clicks
    impressions = row.metrics.impressions
    value = row.metrics.conversions_value

    if date not in daily_data:
        daily_data[date] = {
            'spend': 0,
            'clicks': 0,
            'impressions': 0,
            'value': 0,
            'phone_calls': 0,
            'calls_from_ads': 0,
            'quotes': 0,
            'deals': 0,
            'purchases': 0,
            'total_conversions': 0
        }

    daily_data[date]['spend'] += spend
    daily_data[date]['clicks'] += clicks
    daily_data[date]['impressions'] += impressions
    daily_data[date]['value'] += value

# Query for daily conversions by type
query_daily_conv = f"""
    SELECT
        segments.date,
        segments.conversion_action_name,
        metrics.conversions
    FROM campaign
    WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.status = 'ENABLED'
        AND campaign.name LIKE '%US%'
        AND metrics.conversions > 0
"""

response_conv = ga_service.search(customer_id=customer_id, query=query_daily_conv)

for row in response_conv:
    date = row.segments.date
    conv_name = row.segments.conversion_action_name
    conversions = row.metrics.conversions

    if date not in daily_data:
        daily_data[date] = {
            'spend': 0,
            'clicks': 0,
            'impressions': 0,
            'value': 0,
            'phone_calls': 0,
            'calls_from_ads': 0,
            'quotes': 0,
            'deals': 0,
            'purchases': 0,
            'total_conversions': 0
        }

    # Categorize conversions
    if conv_name == 'Phone Call':
        daily_data[date]['phone_calls'] += conversions
    elif conv_name == 'Calls from ads':
        daily_data[date]['calls_from_ads'] += conversions
    elif 'quote' in conv_name.lower():
        daily_data[date]['quotes'] += conversions
    elif 'Closed Won' in conv_name or 'Deal' in conv_name:
        daily_data[date]['deals'] += conversions
    elif 'purchase' in conv_name.lower():
        daily_data[date]['purchases'] += conversions

    daily_data[date]['total_conversions'] += conversions

# Print daily breakdown
print(f"\n{'Date':<15} {'Spend':>12} {'Clicks':>8} {'Phone Calls':>12} {'Calls from Ads':>16} {'Total Calls':>12} {'Quotes':>8} {'Deals':>7} {'Purchases':>10} {'Conv Value':>14} {'ROAS':>8}")
print("=" * 160)

# Sort by date
sorted_dates = sorted(daily_data.keys())

# Initialize totals
totals = {
    'spend': 0,
    'clicks': 0,
    'impressions': 0,
    'phone_calls': 0,
    'calls_from_ads': 0,
    'quotes': 0,
    'deals': 0,
    'purchases': 0,
    'value': 0,
    'total_conversions': 0
}

for date in sorted_dates:
    data = daily_data[date]
    total_calls = int(data['phone_calls'] + data['calls_from_ads'])
    roas = data['value'] / data['spend'] if data['spend'] > 0 else 0

    print(f"{date:<15} ${data['spend']:>11,.2f} {data['clicks']:>8} {int(data['phone_calls']):>12} {int(data['calls_from_ads']):>16} {total_calls:>12} {int(data['quotes']):>8} {int(data['deals']):>7} {int(data['purchases']):>10} ${data['value']:>13,.2f} {roas:>6.2f}x")

    # Add to totals
    totals['spend'] += data['spend']
    totals['clicks'] += data['clicks']
    totals['impressions'] += data['impressions']
    totals['phone_calls'] += data['phone_calls']
    totals['calls_from_ads'] += data['calls_from_ads']
    totals['quotes'] += data['quotes']
    totals['deals'] += data['deals']
    totals['purchases'] += data['purchases']
    totals['value'] += data['value']
    totals['total_conversions'] += data['total_conversions']

# Print totals
print("=" * 160)
total_calls = int(totals['phone_calls'] + totals['calls_from_ads'])
total_roas = totals['value'] / totals['spend'] if totals['spend'] > 0 else 0

print(f"{'TOTAL':<15} ${totals['spend']:>11,.2f} {totals['clicks']:>8} {int(totals['phone_calls']):>12} {int(totals['calls_from_ads']):>16} {total_calls:>12} {int(totals['quotes']):>8} {int(totals['deals']):>7} {int(totals['purchases']):>10} ${totals['value']:>13,.2f} {total_roas:>6.2f}x")

# Print summary statistics
print(f"\n{'=' * 160}")
print(f"📊 SUMMARY STATISTICS")
print(f"{'=' * 160}")

num_days = len(sorted_dates)
avg_spend = totals['spend'] / num_days if num_days > 0 else 0
avg_calls = total_calls / num_days if num_days > 0 else 0
cost_per_call = totals['spend'] / total_calls if total_calls > 0 else 0
call_to_quote_rate = (totals['quotes'] / total_calls * 100) if total_calls > 0 else 0
quote_to_deal_rate = (totals['deals'] / totals['quotes'] * 100) if totals['quotes'] > 0 else 0
call_to_deal_rate = (totals['deals'] / total_calls * 100) if total_calls > 0 else 0

print(f"\n📅 Period: {num_days} days")
print(f"\n💰 Financial:")
print(f"   • Total Spend: ${totals['spend']:,.2f}")
print(f"   • Average Daily Spend: ${avg_spend:,.2f}")
print(f"   • Total Conversion Value: ${totals['value']:,.2f}")
print(f"   • Overall ROAS: {total_roas:.2f}x")

print(f"\n📞 Calls:")
print(f"   • Total Calls: {total_calls}")
print(f"   • Phone Calls: {int(totals['phone_calls'])}")
print(f"   • Calls from Ads: {int(totals['calls_from_ads'])}")
print(f"   • Average Calls/Day: {avg_calls:.1f}")
print(f"   • Cost Per Call: ${cost_per_call:.2f}")

print(f"\n🎯 Conversion Funnel:")
print(f"   • Total Conversions: {int(totals['total_conversions'])}")
print(f"   • Quotes: {int(totals['quotes'])} ({call_to_quote_rate:.1f}% of calls)")
print(f"   • Deals: {int(totals['deals'])} ({call_to_deal_rate:.1f}% of calls)")
print(f"   • Purchases: {int(totals['purchases'])}")
print(f"\n🔄 Conversion Rates:")
print(f"   • Call → Quote: {call_to_quote_rate:.1f}%")
print(f"   • Quote → Deal: {quote_to_deal_rate:.1f}%")
print(f"   • Call → Deal: {call_to_deal_rate:.1f}%")

# Week-over-week analysis
print(f"\n{'=' * 160}")
print(f"📈 WEEK BREAKDOWN")
print(f"{'=' * 160}")

# Week 1: Feb 1-7
week1_dates = [d for d in sorted_dates if '2026-02-01' <= d <= '2026-02-07']
week1_data = {
    'spend': sum(daily_data[d]['spend'] for d in week1_dates),
    'calls': sum(daily_data[d]['phone_calls'] + daily_data[d]['calls_from_ads'] for d in week1_dates),
    'deals': sum(daily_data[d]['deals'] for d in week1_dates),
    'value': sum(daily_data[d]['value'] for d in week1_dates)
}
week1_roas = week1_data['value'] / week1_data['spend'] if week1_data['spend'] > 0 else 0

# Week 2: Feb 8-14
week2_dates = [d for d in sorted_dates if '2026-02-08' <= d <= '2026-02-14']
week2_data = {
    'spend': sum(daily_data[d]['spend'] for d in week2_dates),
    'calls': sum(daily_data[d]['phone_calls'] + daily_data[d]['calls_from_ads'] for d in week2_dates),
    'deals': sum(daily_data[d]['deals'] for d in week2_dates),
    'value': sum(daily_data[d]['value'] for d in week2_dates)
}
week2_roas = week2_data['value'] / week2_data['spend'] if week2_data['spend'] > 0 else 0

# Week 3: Feb 15-21
week3_dates = [d for d in sorted_dates if '2026-02-15' <= d <= '2026-02-21']
week3_data = {
    'spend': sum(daily_data[d]['spend'] for d in week3_dates),
    'calls': sum(daily_data[d]['phone_calls'] + daily_data[d]['calls_from_ads'] for d in week3_dates),
    'deals': sum(daily_data[d]['deals'] for d in week3_dates),
    'value': sum(daily_data[d]['value'] for d in week3_dates)
}
week3_roas = week3_data['value'] / week3_data['spend'] if week3_data['spend'] > 0 else 0

# Week 4: Feb 22-23 (partial)
week4_dates = [d for d in sorted_dates if d >= '2026-02-22']
week4_data = {
    'spend': sum(daily_data[d]['spend'] for d in week4_dates),
    'calls': sum(daily_data[d]['phone_calls'] + daily_data[d]['calls_from_ads'] for d in week4_dates),
    'deals': sum(daily_data[d]['deals'] for d in week4_dates),
    'value': sum(daily_data[d]['value'] for d in week4_dates)
}
week4_roas = week4_data['value'] / week4_data['spend'] if week4_data['spend'] > 0 else 0

print(f"\n{'Week':<20} {'Spend':>12} {'Calls':>8} {'Deals':>7} {'Value':>14} {'ROAS':>8}")
print("-" * 160)
print(f"{'Week 1 (Feb 1-7)':<20} ${week1_data['spend']:>11,.2f} {int(week1_data['calls']):>8} {int(week1_data['deals']):>7} ${week1_data['value']:>13,.2f} {week1_roas:>6.2f}x")
print(f"{'Week 2 (Feb 8-14)':<20} ${week2_data['spend']:>11,.2f} {int(week2_data['calls']):>8} {int(week2_data['deals']):>7} ${week2_data['value']:>13,.2f} {week2_roas:>6.2f}x")
print(f"{'Week 3 (Feb 15-21)':<20} ${week3_data['spend']:>11,.2f} {int(week3_data['calls']):>8} {int(week3_data['deals']):>7} ${week3_data['value']:>13,.2f} {week3_roas:>6.2f}x")
print(f"{'Week 4 (Feb 22-23)':<20} ${week4_data['spend']:>11,.2f} {int(week4_data['calls']):>8} {int(week4_data['deals']):>7} ${week4_data['value']:>13,.2f} {week4_roas:>6.2f}x")

print(f"\n{'=' * 160}")
print("✅ DAILY BREAKDOWN COMPLETE")
print(f"{'=' * 160}")
