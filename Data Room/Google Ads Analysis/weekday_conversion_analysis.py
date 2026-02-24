from google.ads.googleads.client import GoogleAdsClient
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Load credentials
client = GoogleAdsClient.load_from_storage('/Users/vinuraabeysundara/Desktop/ICG/DOZR/Data Room/Config/google-ads.yaml')
ga_service = client.get_service('GoogleAdsService')
customer_id = '8531896842'

# Get last 30 days of weekday data (Monday-Friday)
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

print("=" * 100)
print(f"📊 CONVERSION FUNNEL ANALYSIS - Last 30 Days (Weekdays Only)")
print("=" * 100)

# Query conversion data by date
query = f"""
    SELECT
        segments.date,
        segments.day_of_week,
        segments.conversion_action_name,
        metrics.conversions
    FROM campaign
    WHERE segments.date BETWEEN '{start_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}'
        AND metrics.conversions > 0
"""

response = ga_service.search(customer_id=customer_id, query=query)

# Organize by date and day of week
data_by_date = {}

for row in response:
    date = row.segments.date
    day_of_week = row.segments.day_of_week.name
    conv_name = row.segments.conversion_action_name
    conversions = row.metrics.conversions

    if date not in data_by_date:
        data_by_date[date] = {
            'day_of_week': day_of_week,
            'phone_calls': 0,
            'quotes': 0,
            'deals': 0
        }

    # Categorize conversions
    if 'Phone Call' in conv_name or 'Calls from ads' in conv_name:
        data_by_date[date]['phone_calls'] += conversions
    elif 'quote' in conv_name.lower():
        data_by_date[date]['quotes'] += conversions
    elif 'Closed Won' in conv_name or 'Deal' in conv_name:
        data_by_date[date]['deals'] += conversions

# Separate weekdays and weekends
weekday_stats = {'phone_calls': 0, 'quotes': 0, 'deals': 0, 'days': 0}
weekend_stats = {'phone_calls': 0, 'quotes': 0, 'deals': 0, 'days': 0}

weekdays = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY']

for date, data in data_by_date.items():
    if data['day_of_week'] in weekdays:
        weekday_stats['phone_calls'] += data['phone_calls']
        weekday_stats['quotes'] += data['quotes']
        weekday_stats['deals'] += data['deals']
        weekday_stats['days'] += 1
    else:
        weekend_stats['phone_calls'] += data['phone_calls']
        weekend_stats['quotes'] += data['quotes']
        weekend_stats['deals'] += data['deals']
        weekend_stats['days'] += 1

# Calculate conversion rates
def calc_rates(stats, label):
    calls = stats['phone_calls']
    quotes = stats['quotes']
    deals = stats['deals']
    days = stats['days']

    # Note: The deal probably started as a quote, so total quotes = quotes + deals
    total_quotes = quotes + deals

    call_to_quote_rate = (total_quotes / calls * 100) if calls > 0 else 0
    quote_to_deal_rate = (deals / total_quotes * 100) if total_quotes > 0 else 0

    print(f"\n{label}")
    print("-" * 100)
    print(f"   Days analyzed: {days}")
    print(f"   Total phone calls: {int(calls)}")
    print(f"   Total quotes (including deals): {int(total_quotes)}")
    print(f"   Total closed deals: {int(deals)}")
    print(f"   📊 Call → Quote rate: {call_to_quote_rate:.1f}%")
    print(f"   🎯 Quote → Deal rate: {quote_to_deal_rate:.1f}%")
    print(f"   📈 Call → Deal rate: {(deals/calls*100) if calls > 0 else 0:.1f}%")

    if calls > 0 and days > 0:
        print(f"\n   Daily averages:")
        print(f"      • {calls/days:.1f} calls per day")
        print(f"      • {total_quotes/days:.1f} quotes per day")
        print(f"      • {deals/days:.1f} deals per day")

    return call_to_quote_rate, quote_to_deal_rate

weekday_c2q, weekday_q2d = calc_rates(weekday_stats, "📅 WEEKDAYS (Mon-Fri)")
weekend_c2q, weekend_q2d = calc_rates(weekend_stats, "🎉 WEEKENDS (Sat-Sun)")

# Today's stats
print(f"\n🔥 TODAY (Sunday)")
print("-" * 100)
print(f"   Total phone calls: 11")
print(f"   Total quotes (including deals): 3")
print(f"   Total closed deals: 1")
print(f"   📊 Call → Quote rate: 27.3%")
print(f"   🎯 Quote → Deal rate: 33.3%")
print(f"   📈 Call → Deal rate: 9.1%")

# Comparison
print("\n" + "=" * 100)
print("📊 COMPARISON - Today vs Historical Averages")
print("=" * 100)
print(f"\nCall → Quote Conversion:")
print(f"   Today: 27.3%")
print(f"   Weekday avg: {weekday_c2q:.1f}%")
print(f"   Weekend avg: {weekend_c2q:.1f}%")

print(f"\nQuote → Deal Conversion:")
print(f"   Today: 33.3%")
print(f"   Weekday avg: {weekday_q2d:.1f}%")
print(f"   Weekend avg: {weekend_q2d:.1f}%")

print("\n" + "=" * 100)
