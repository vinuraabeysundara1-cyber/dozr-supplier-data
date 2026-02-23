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
print(f"📊 GOOGLE ADS WEEKDAY PERFORMANCE BREAKDOWN (MON-FRI ONLY)")
print(f"Period: {start_date} to {end_date}")
print("=" * 160)

# Query for daily spend and metrics
query_daily_spend = f"""
    SELECT
        segments.date,
        segments.day_of_week,
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
    day_of_week = row.segments.day_of_week.name
    spend = row.metrics.cost_micros / 1_000_000
    clicks = row.metrics.clicks
    impressions = row.metrics.impressions
    value = row.metrics.conversions_value

    if date not in daily_data:
        daily_data[date] = {
            'day_of_week': day_of_week,
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

    if date in daily_data:
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

# Filter for weekdays only (exclude Saturday and Sunday)
weekday_data = {date: data for date, data in daily_data.items()
                if data['day_of_week'] not in ['SATURDAY', 'SUNDAY']}

# Sort by date
sorted_dates = sorted(weekday_data.keys())

# Print header
print(f"\n{'Date':<15} {'Day':>10} {'Spend':>12} {'Clicks':>8} {'Phone Calls':>12} {'Calls from Ads':>16} {'Total Calls':>12} {'Quotes':>8} {'Deals':>7} {'Purchases':>10} {'Conv Value':>14} {'ROAS':>8}")
print("=" * 160)

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

# Print each weekday
for date in sorted_dates:
    data = weekday_data[date]
    day_name = data['day_of_week'].title()
    total_calls = int(data['phone_calls'] + data['calls_from_ads'])
    roas = data['value'] / data['spend'] if data['spend'] > 0 else 0

    print(f"{date:<15} {day_name:>10} ${data['spend']:>11,.2f} {data['clicks']:>8} {int(data['phone_calls']):>12} {int(data['calls_from_ads']):>16} {total_calls:>12} {int(data['quotes']):>8} {int(data['deals']):>7} {int(data['purchases']):>10} ${data['value']:>13,.2f} {roas:>6.2f}x")

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

print(f"{'WEEKDAY TOTAL':<26} ${totals['spend']:>11,.2f} {totals['clicks']:>8} {int(totals['phone_calls']):>12} {int(totals['calls_from_ads']):>16} {total_calls:>12} {int(totals['quotes']):>8} {int(totals['deals']):>7} {int(totals['purchases']):>10} ${totals['value']:>13,.2f} {total_roas:>6.2f}x")

# Print summary statistics
print(f"\n{'=' * 160}")
print(f"📊 WEEKDAY SUMMARY STATISTICS")
print(f"{'=' * 160}")

num_weekdays = len(sorted_dates)
avg_spend = totals['spend'] / num_weekdays if num_weekdays > 0 else 0
avg_calls = total_calls / num_weekdays if num_weekdays > 0 else 0
cost_per_call = totals['spend'] / total_calls if total_calls > 0 else 0
call_to_quote_rate = (totals['quotes'] / total_calls * 100) if total_calls > 0 else 0
quote_to_deal_rate = (totals['deals'] / totals['quotes'] * 100) if totals['quotes'] > 0 else 0
call_to_deal_rate = (totals['deals'] / total_calls * 100) if total_calls > 0 else 0

print(f"\n📅 Total Weekdays: {num_weekdays} days")
print(f"\n💰 Financial Metrics:")
print(f"   • Total Spend: ${totals['spend']:,.2f}")
print(f"   • Average Daily Spend: ${avg_spend:,.2f}")
print(f"   • Total Conversion Value: ${totals['value']:,.2f}")
print(f"   • Overall ROAS: {total_roas:.2f}x")

print(f"\n📞 Call Metrics:")
print(f"   • Total Calls: {total_calls}")
print(f"     - Phone Calls: {int(totals['phone_calls'])} ({totals['phone_calls']/total_calls*100:.1f}%)")
print(f"     - Calls from Ads: {int(totals['calls_from_ads'])} ({totals['calls_from_ads']/total_calls*100:.1f}%)")
print(f"   • Average Calls/Day: {avg_calls:.1f}")
print(f"   • Cost Per Call: ${cost_per_call:.2f}")

print(f"\n🎯 Conversion Metrics:")
print(f"   • Total Conversions: {int(totals['total_conversions'])}")
print(f"   • Quotes: {int(totals['quotes'])} ({call_to_quote_rate:.1f}% of calls)")
print(f"   • Deals: {int(totals['deals'])} ({call_to_deal_rate:.1f}% of calls)")
print(f"   • Purchases: {int(totals['purchases'])}")

print(f"\n🔄 Conversion Rates:")
print(f"   • Call → Quote: {call_to_quote_rate:.1f}%")
print(f"   • Quote → Deal: {quote_to_deal_rate:.1f}%")
print(f"   • Call → Deal: {call_to_deal_rate:.1f}%")

# Day of week analysis
print(f"\n{'=' * 160}")
print(f"📊 PERFORMANCE BY DAY OF WEEK")
print(f"{'=' * 160}")

day_aggregates = {}
for date, data in weekday_data.items():
    day = data['day_of_week']
    if day not in day_aggregates:
        day_aggregates[day] = {
            'spend': 0,
            'calls': 0,
            'deals': 0,
            'value': 0,
            'count': 0
        }

    day_aggregates[day]['spend'] += data['spend']
    day_aggregates[day]['calls'] += data['phone_calls'] + data['calls_from_ads']
    day_aggregates[day]['deals'] += data['deals']
    day_aggregates[day]['value'] += data['value']
    day_aggregates[day]['count'] += 1

# Order by day of week
day_order = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY']
print(f"\n{'Day':<15} {'Avg Spend':>12} {'Avg Calls':>12} {'Avg Deals':>12} {'Avg Value':>14} {'Avg ROAS':>10}")
print("-" * 160)

for day in day_order:
    if day in day_aggregates:
        data = day_aggregates[day]
        avg_spend = data['spend'] / data['count']
        avg_calls = data['calls'] / data['count']
        avg_deals = data['deals'] / data['count']
        avg_value = data['value'] / data['count']
        avg_roas = avg_value / avg_spend if avg_spend > 0 else 0

        print(f"{day.title():<15} ${avg_spend:>11,.2f} {avg_calls:>12.1f} {avg_deals:>12.1f} ${avg_value:>13,.2f} {avg_roas:>8.2f}x")

# Best and worst performing weekdays
print(f"\n{'=' * 160}")
print(f"🏆 TOP 5 BEST WEEKDAYS (BY ROAS)")
print(f"{'=' * 160}")

weekday_performance = []
for date in sorted_dates:
    data = weekday_data[date]
    roas = data['value'] / data['spend'] if data['spend'] > 0 else 0
    total_calls = int(data['phone_calls'] + data['calls_from_ads'])
    weekday_performance.append((date, data['day_of_week'].title(), data['spend'], total_calls, data['deals'], data['value'], roas))

sorted_by_roas = sorted(weekday_performance, key=lambda x: x[6], reverse=True)

print(f"\n{'Date':<15} {'Day':>10} {'Spend':>12} {'Calls':>8} {'Deals':>7} {'Value':>14} {'ROAS':>8}")
print("-" * 160)
for i, (date, day, spend, calls, deals, value, roas) in enumerate(sorted_by_roas[:5], 1):
    print(f"{date:<15} {day:>10} ${spend:>11,.2f} {calls:>8} {deals:>7} ${value:>13,.2f} {roas:>6.2f}x")

print(f"\n{'=' * 160}")
print(f"⚠️  BOTTOM 5 WEEKDAYS (BY ROAS)")
print(f"{'=' * 160}")

print(f"\n{'Date':<15} {'Day':>10} {'Spend':>12} {'Calls':>8} {'Deals':>7} {'Value':>14} {'ROAS':>8}")
print("-" * 160)
for i, (date, day, spend, calls, deals, value, roas) in enumerate(sorted_by_roas[-5:], 1):
    print(f"{date:<15} {day:>10} ${spend:>11,.2f} {calls:>8} {deals:>7} ${value:>13,.2f} {roas:>6.2f}x")

print(f"\n{'=' * 160}")
print("✅ WEEKDAY BREAKDOWN COMPLETE")
print(f"{'=' * 160}")
