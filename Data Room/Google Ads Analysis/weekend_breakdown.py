from google.ads.googleads.client import GoogleAdsClient
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Load credentials
client = GoogleAdsClient.load_from_storage('/Users/vinuraabeysundara/Desktop/DOZR/Data Room/Config/google-ads.yaml')
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
print(f"📊 WEEKEND PERFORMANCE BREAKDOWN")
print(f"Saturday {saturday_date.strftime('%B %d, %Y')} vs Sunday {sunday_date.strftime('%B %d, %Y')}")
print("=" * 100)

# Query 1: Get campaign metrics by date
query_metrics = f"""
    SELECT
        segments.date,
        metrics.cost_micros,
        metrics.clicks,
        metrics.impressions,
        metrics.average_cpc,
        metrics.conversions,
        metrics.all_conversions
    FROM campaign
    WHERE segments.date BETWEEN '{saturday_str}' AND '{sunday_str}'
        AND campaign.status = 'ENABLED'
"""

response_metrics = ga_service.search(customer_id=customer_id, query=query_metrics)

totals = {
    saturday_str: {'spend': 0, 'clicks': 0, 'impressions': 0, 'conversions': 0, 'all_conversions': 0},
    sunday_str: {'spend': 0, 'clicks': 0, 'impressions': 0, 'conversions': 0, 'all_conversions': 0}
}

for row in response_metrics:
    date = row.segments.date
    totals[date]['spend'] += row.metrics.cost_micros / 1_000_000
    totals[date]['clicks'] += row.metrics.clicks
    totals[date]['impressions'] += row.metrics.impressions
    totals[date]['conversions'] += row.metrics.conversions
    totals[date]['all_conversions'] += row.metrics.all_conversions

# Query 2: Get conversion action breakdown by date
query_conversions = f"""
    SELECT
        segments.date,
        segments.conversion_action_name,
        metrics.conversions
    FROM campaign
    WHERE segments.date BETWEEN '{saturday_str}' AND '{sunday_str}'
        AND campaign.status = 'ENABLED'
"""

response_conversions = ga_service.search(customer_id=customer_id, query=query_conversions)

conversions_by_type = {
    saturday_str: {},
    sunday_str: {}
}

for row in response_conversions:
    date = row.segments.date
    conv_name = row.segments.conversion_action_name
    conversions = row.metrics.conversions

    if conv_name and conversions > 0:
        if conv_name not in conversions_by_type[date]:
            conversions_by_type[date][conv_name] = 0
        conversions_by_type[date][conv_name] += conversions

# Print results
print(f"\n{'Metric':<30} {'Saturday':>20} {'Sunday':>20} {'Change':>20}")
print("-" * 100)

sat = totals[saturday_str]
sun = totals[sunday_str]

# Spend
spend_change = ((sun['spend'] - sat['spend']) / sat['spend'] * 100) if sat['spend'] > 0 else 0
print(f"{'💰 Total Spend':<30} ${sat['spend']:>19.2f} ${sun['spend']:>19.2f} {spend_change:>18.1f}%")

# Clicks
clicks_change = ((sun['clicks'] - sat['clicks']) / sat['clicks'] * 100) if sat['clicks'] > 0 else 0
print(f"{'👆 Clicks':<30} {sat['clicks']:>20} {sun['clicks']:>20} {clicks_change:>18.1f}%")

# Impressions
impr_change = ((sun['impressions'] - sat['impressions']) / sat['impressions'] * 100) if sat['impressions'] > 0 else 0
print(f"{'👁️  Impressions':<30} {sat['impressions']:>20} {sun['impressions']:>20} {impr_change:>18.1f}%")

# CPC
sat_cpc = sat['spend'] / sat['clicks'] if sat['clicks'] > 0 else 0
sun_cpc = sun['spend'] / sun['clicks'] if sun['clicks'] > 0 else 0
cpc_change = ((sun_cpc - sat_cpc) / sat_cpc * 100) if sat_cpc > 0 else 0
print(f"{'📊 Average CPC':<30} ${sat_cpc:>19.2f} ${sun_cpc:>19.2f} {cpc_change:>18.1f}%")

# CTR
sat_ctr = (sat['clicks'] / sat['impressions'] * 100) if sat['impressions'] > 0 else 0
sun_ctr = (sun['clicks'] / sun['impressions'] * 100) if sun['impressions'] > 0 else 0
ctr_change = sun_ctr - sat_ctr
print(f"{'📈 CTR':<30} {sat_ctr:>19.2f}% {sun_ctr:>19.2f}% {ctr_change:>18.2f}pp")

# Total Conversions
conv_change = ((sun['conversions'] - sat['conversions']) / sat['conversions'] * 100) if sat['conversions'] > 0 else 0
print(f"{'📞 Total Conversions':<30} {int(sat['conversions']):>20} {int(sun['conversions']):>20} {conv_change:>18.1f}%")

# CPA
sat_cpa = sat['spend'] / sat['conversions'] if sat['conversions'] > 0 else 0
sun_cpa = sun['spend'] / sun['conversions'] if sun['conversions'] > 0 else 0
cpa_change = ((sun_cpa - sat_cpa) / sat_cpa * 100) if sat_cpa > 0 else 0
print(f"{'🎯 Average CPA':<30} ${sat_cpa:>19.2f} ${sun_cpa:>19.2f} {cpa_change:>18.1f}%")

# Conversion breakdown
print("\n" + "=" * 100)
print("📋 CONVERSION BREAKDOWN BY TYPE")
print("=" * 100)

all_conversion_types = set()
for date in [saturday_str, sunday_str]:
    all_conversion_types.update(conversions_by_type[date].keys())

if all_conversion_types:
    print(f"\n{'Conversion Type':<50} {'Saturday':>20} {'Sunday':>20}")
    print("-" * 100)
    for conv_type in sorted(all_conversion_types):
        sat_conv = conversions_by_type[saturday_str].get(conv_type, 0)
        sun_conv = conversions_by_type[sunday_str].get(conv_type, 0)
        print(f"{conv_type:<50} {int(sat_conv):>20} {int(sun_conv):>20}")
else:
    print("\nNo conversion action data available for this date range.")

print("\n" + "=" * 100)
print("\n💡 NOTE: Conversion types shown above represent the conversion actions configured in your")
print("   Google Ads account (e.g., Phone Calls, Form Submissions, Quotes, etc.)")
print("=" * 100)
