from google.ads.googleads.client import GoogleAdsClient
from collections import defaultdict
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Load credentials
client = GoogleAdsClient.load_from_storage('/Users/vinuraabeysundara/Desktop/ICG/DOZR/Data Room/Config/google-ads.yaml')
ga_service = client.get_service('GoogleAdsService')
customer_id = '8531896842'

print("=" * 140)
print("📅 WEEKDAY PERFORMANCE ANALYSIS - FEBRUARY 2026")
print("Period: February 1-23, 2026")
print("=" * 140)

start_date = '2026-02-01'
end_date = '2026-02-23'

# Get metrics by day
query_metrics = f"""
    SELECT
        segments.date,
        metrics.cost_micros,
        metrics.clicks,
        metrics.impressions
    FROM campaign
    WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.status = 'ENABLED'
        AND campaign.name LIKE '%US%'
"""

response_metrics = ga_service.search(customer_id=customer_id, query=query_metrics)

weekday_data = defaultdict(lambda: {
    'days': [],
    'spend': 0,
    'clicks': 0,
    'impressions': 0,
    'calls': 0,
    'deals': 0,
    'value': 0
})

daily_data = {}

for row in response_metrics:
    date_str = row.segments.date

    # Parse date and get day of week using Python
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    day_of_week = date_obj.strftime('%A')  # Full weekday name (Monday, Tuesday, etc.)

    spend = row.metrics.cost_micros / 1_000_000
    clicks = row.metrics.clicks
    impressions = row.metrics.impressions

    if date_str not in daily_data:
        daily_data[date_str] = {
            'day_of_week': day_of_week,
            'spend': 0,
            'clicks': 0,
            'impressions': 0,
            'calls': 0,
            'deals': 0,
            'value': 0
        }

    daily_data[date_str]['spend'] += spend
    daily_data[date_str]['clicks'] += clicks
    daily_data[date_str]['impressions'] += impressions

# Get conversions
query_conv = f"""
    SELECT
        segments.date,
        segments.conversion_action_name,
        metrics.conversions,
        metrics.conversions_value
    FROM campaign
    WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.status = 'ENABLED'
        AND campaign.name LIKE '%US%'
        AND metrics.conversions > 0
"""

response_conv = ga_service.search(customer_id=customer_id, query=query_conv)

for row in response_conv:
    date = row.segments.date
    conv_name = row.segments.conversion_action_name
    conversions = row.metrics.conversions
    value = row.metrics.conversions_value

    if date in daily_data:
        if 'Phone Call' in conv_name or 'Calls from ads' in conv_name:
            daily_data[date]['calls'] += conversions
        elif 'Closed Won' in conv_name:
            daily_data[date]['deals'] += conversions
            daily_data[date]['value'] += value

# Aggregate by weekday
for date, data in daily_data.items():
    day = data['day_of_week']

    if day not in weekday_data:
        weekday_data[day] = {
            'days': [],
            'spend': 0,
            'clicks': 0,
            'impressions': 0,
            'calls': 0,
            'deals': 0,
            'value': 0
        }

    weekday_data[day]['days'].append(date)
    weekday_data[day]['spend'] += data['spend']
    weekday_data[day]['clicks'] += data['clicks']
    weekday_data[day]['impressions'] += data['impressions']
    weekday_data[day]['calls'] += data['calls']
    weekday_data[day]['deals'] += data['deals']
    weekday_data[day]['value'] += data['value']

# Print results
print("\n📊 PERFORMANCE BY DAY OF WEEK")
print("=" * 140)

# Order days properly
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

print(f"\n{'Day':<12} {'Days':>5} {'Spend':>12} {'Clicks':>8} {'Calls':>8} {'Deals':>8} {'Value':>14} {'CPC':>8} {'CPA':>10} {'ROAS':>8}")
print("-" * 120)

total_spend = 0
total_clicks = 0
total_calls = 0
total_deals = 0
total_value = 0

weekday_only_spend = 0
weekday_only_clicks = 0
weekday_only_calls = 0
weekday_only_deals = 0
weekday_only_value = 0

for day in day_order:
    if day in weekday_data:
        data = weekday_data[day]
        num_days = len(data['days'])
        cpc = data['spend'] / data['clicks'] if data['clicks'] > 0 else 0
        cpa = data['spend'] / data['deals'] if data['deals'] > 0 else 0
        roas = data['value'] / data['spend'] if data['spend'] > 0 else 0

        print(f"{day:<12} {num_days:>5} ${data['spend']:>11,.2f} {data['clicks']:>8,} {int(data['calls']):>8} {int(data['deals']):>8} ${data['value']:>13,.2f} ${cpc:>7.2f} ${cpa:>9,.2f} {roas:>7.2f}x")

        total_spend += data['spend']
        total_clicks += data['clicks']
        total_calls += data['calls']
        total_deals += data['deals']
        total_value += data['value']

        # Track weekday only (Mon-Fri)
        if day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
            weekday_only_spend += data['spend']
            weekday_only_clicks += data['clicks']
            weekday_only_calls += data['calls']
            weekday_only_deals += data['deals']
            weekday_only_value += data['value']

print("-" * 120)
total_cpc = total_spend / total_clicks if total_clicks > 0 else 0
total_cpa = total_spend / total_deals if total_deals > 0 else 0
total_roas = total_value / total_spend if total_spend > 0 else 0
print(f"{'TOTAL':<12} {'':>5} ${total_spend:>11,.2f} {total_clicks:>8,} {int(total_calls):>8} {int(total_deals):>8} ${total_value:>13,.2f} ${total_cpc:>7.2f} ${total_cpa:>9,.2f} {total_roas:>7.2f}x")

# Averages
print("\n\n📈 AVERAGE DAILY PERFORMANCE BY DAY OF WEEK")
print("=" * 140)

print(f"\n{'Day':<12} {'Avg Spend':>12} {'Avg Clicks':>11} {'Avg Calls':>11} {'Avg Deals':>11} {'Avg Value':>14}")
print("-" * 80)

for day in day_order:
    if day in weekday_data:
        data = weekday_data[day]
        num_days = len(data['days'])

        avg_spend = data['spend'] / num_days
        avg_clicks = data['clicks'] / num_days
        avg_calls = data['calls'] / num_days
        avg_deals = data['deals'] / num_days
        avg_value = data['value'] / num_days

        print(f"{day:<12} ${avg_spend:>11,.2f} {avg_clicks:>11,.1f} {avg_calls:>11,.1f} {avg_deals:>11,.1f} ${avg_value:>13,.2f}")

# Weekday vs Weekend comparison
print("\n\n🆚 WEEKDAY vs WEEKEND COMPARISON")
print("=" * 140)

weekend_spend = total_spend - weekday_only_spend
weekend_clicks = total_clicks - weekday_only_clicks
weekend_calls = total_calls - weekday_only_calls
weekend_deals = total_deals - weekday_only_deals
weekend_value = total_value - weekday_only_value

weekday_cpa = weekday_only_spend / weekday_only_deals if weekday_only_deals > 0 else 0
weekend_cpa = weekend_spend / weekend_deals if weekend_deals > 0 else 0
weekday_roas = weekday_only_value / weekday_only_spend if weekday_only_spend > 0 else 0
weekend_roas = weekend_value / weekend_spend if weekend_spend > 0 else 0

print(f"\n{'Period':<12} {'Spend':>12} {'Clicks':>8} {'Calls':>8} {'Deals':>8} {'Value':>14} {'CPA':>10} {'ROAS':>8} {'% of Total':>12}")
print("-" * 120)
print(f"{'Weekdays':<12} ${weekday_only_spend:>11,.2f} {weekday_only_clicks:>8,} {int(weekday_only_calls):>8} {int(weekday_only_deals):>8} ${weekday_only_value:>13,.2f} ${weekday_cpa:>9,.2f} {weekday_roas:>7.2f}x {weekday_only_value/total_value*100:>11.1f}%")
print(f"{'Weekend':<12} ${weekend_spend:>11,.2f} {weekend_clicks:>8,} {int(weekend_calls):>8} {int(weekend_deals):>8} ${weekend_value:>13,.2f} ${weekend_cpa:>9,.2f} {weekend_roas:>7.2f}x {weekend_value/total_value*100:>11.1f}%")

# Best and worst days
print("\n\n🏆 BEST & WORST PERFORMING DAYS")
print("=" * 140)

# Sort by ROAS
weekday_list = []
for day in day_order:
    if day in weekday_data:
        data = weekday_data[day]
        roas = data['value'] / data['spend'] if data['spend'] > 0 else 0
        weekday_list.append((day, data, roas))

weekday_list.sort(key=lambda x: x[2], reverse=True)

print("\n🥇 BEST DAY BY ROAS:")
if weekday_list:
    best = weekday_list[0]
    print(f"   {best[0]}: {best[2]:.2f}x ROAS | ${best[1]['value']:,.2f} value | {int(best[1]['deals'])} deals")

print("\n🥉 WORST DAY BY ROAS:")
if weekday_list:
    worst = weekday_list[-1]
    print(f"   {worst[0]}: {worst[2]:.2f}x ROAS | ${worst[1]['value']:,.2f} value | {int(worst[1]['deals'])} deals")

# Sort by deal value
weekday_list.sort(key=lambda x: x[1]['value'], reverse=True)

print("\n💰 BEST DAY BY REVENUE:")
if weekday_list:
    best = weekday_list[0]
    roas = best[1]['value'] / best[1]['spend'] if best[1]['spend'] > 0 else 0
    print(f"   {best[0]}: ${best[1]['value']:,.2f} | {int(best[1]['deals'])} deals | {roas:.2f}x ROAS")

# Sort by deals
weekday_list.sort(key=lambda x: x[1]['deals'], reverse=True)

print("\n🎯 BEST DAY BY DEAL VOLUME:")
if weekday_list:
    best = weekday_list[0]
    roas = best[1]['value'] / best[1]['spend'] if best[1]['spend'] > 0 else 0
    print(f"   {best[0]}: {int(best[1]['deals'])} deals | ${best[1]['value']:,.2f} value | {roas:.2f}x ROAS")

print("\n\n💡 KEY INSIGHTS:")
weekday_pct = (weekday_only_value / total_value * 100) if total_value > 0 else 0
print(f"   • Weekdays (Mon-Fri) generate {weekday_pct:.1f}% of total revenue")
print(f"   • Weekday ROAS: {weekday_roas:.2f}x vs Weekend ROAS: {weekend_roas:.2f}x")

if weekday_roas > weekend_roas * 1.2:
    print(f"   • ⚠️  Weekdays significantly outperform weekends - consider reducing weekend budget")
elif weekend_roas > weekday_roas * 1.2:
    print(f"   • ⚠️  Weekends outperform weekdays - consider shifting more budget to weekends")

print("\n" + "=" * 140)
