from google.ads.googleads.client import GoogleAdsClient
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Load credentials
client = GoogleAdsClient.load_from_storage('/Users/vinuraabeysundara/Desktop/ICG/DOZR/Data Room/Config/google-ads.yaml')
ga_service = client.get_service('GoogleAdsService')
customer_id = '8531896842'

# Get Saturday and Sunday dates
today = datetime.now()
days_since_sunday = (today.weekday() + 1) % 7
if days_since_sunday == 0:
    sunday_date = today
    saturday_date = today - timedelta(days=1)
else:
    sunday_date = today - timedelta(days=days_since_sunday)
    saturday_date = sunday_date - timedelta(days=1)

saturday_str = saturday_date.strftime('%Y-%m-%d')
sunday_str = sunday_date.strftime('%Y-%m-%d')

print("=" * 100)
print(f"🔍 VERIFYING CLOSED DEAL DATE")
print("=" * 100)

# Query for closed deals by date
query = f"""
    SELECT
        segments.date,
        campaign.name,
        segments.conversion_action_name,
        metrics.conversions,
        metrics.conversions_value
    FROM campaign
    WHERE segments.date BETWEEN '{saturday_str}' AND '{sunday_str}'
        AND segments.conversion_action_name LIKE '%Closed Won%'
        AND metrics.conversions > 0
"""

response = ga_service.search(customer_id=customer_id, query=query)

print(f"\nSearching for Closed Won Deals between {saturday_str} and {sunday_str}...\n")

deal_found = False
for row in response:
    deal_found = True
    date = row.segments.date
    campaign = row.campaign.name
    conv_name = row.segments.conversion_action_name
    conversions = row.metrics.conversions
    value = row.metrics.conversions_value

    day_name = "Saturday" if date == saturday_str else "Sunday"

    print(f"✅ CLOSED DEAL FOUND!")
    print(f"   Date: {date} ({day_name})")
    print(f"   Campaign: {campaign}")
    print(f"   Conversion Type: {conv_name}")
    print(f"   Number of Deals: {int(conversions)}")
    print(f"   Deal Value: ${value:,.2f}")
    print("-" * 100)

if not deal_found:
    print("❌ No closed deals found on either day")

# Also check quote requests by day
print(f"\n📋 QUOTE REQUESTS BREAKDOWN BY DAY")
print("=" * 100)

query_quotes = f"""
    SELECT
        segments.date,
        segments.conversion_action_name,
        metrics.conversions,
        metrics.conversions_value
    FROM campaign
    WHERE segments.date BETWEEN '{saturday_str}' AND '{sunday_str}'
        AND segments.conversion_action_name LIKE '%quote%'
        AND metrics.conversions > 0
"""

response_quotes = ga_service.search(customer_id=customer_id, query=query_quotes)

quotes_by_day = {saturday_str: 0, sunday_str: 0}
value_by_day = {saturday_str: 0, sunday_str: 0}

for row in response_quotes:
    date = row.segments.date
    conversions = row.metrics.conversions
    value = row.metrics.conversions_value

    quotes_by_day[date] += conversions
    value_by_day[date] += value

print(f"\nSaturday ({saturday_str}):")
print(f"   Quotes: {int(quotes_by_day[saturday_str])}")
print(f"   Value: ${value_by_day[saturday_str]:,.2f}")

print(f"\nSunday ({sunday_str}):")
print(f"   Quotes: {int(quotes_by_day[sunday_str])}")
print(f"   Value: ${value_by_day[sunday_str]:,.2f}")

print("\n" + "=" * 100)
print("💡 IMPORTANT NOTE:")
print("=" * 100)
print("\nThe conversion date in Google Ads represents when the conversion was RECORDED,")
print("not necessarily when the initial call happened. A Saturday call could convert")
print("to a deal on Sunday if the sales team closed it on Sunday.")
print("\nTo determine the actual call date, you would need to check CallRail or your CRM.")
print("=" * 100)
