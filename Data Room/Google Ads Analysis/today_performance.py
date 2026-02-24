from google.ads.googleads.client import GoogleAdsClient
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Load credentials
client = GoogleAdsClient.load_from_storage('/Users/vinuraabeysundara/Desktop/ICG/DOZR/Data Room/Config/google-ads.yaml')
ga_service = client.get_service('GoogleAdsService')
customer_id = '8531896842'

today = datetime.now()
today_str = today.strftime('%Y-%m-%d')

print("=" * 100)
print(f"📊 TODAY'S PERFORMANCE - {today.strftime('%A, %B %d, %Y')}")
print(f"⏰ Report Generated: {today.strftime('%I:%M %p')}")
print("=" * 100)

# Query for today's performance
query = f"""
    SELECT
        campaign.name,
        campaign.status,
        metrics.cost_micros,
        metrics.conversions,
        metrics.clicks,
        metrics.impressions,
        metrics.average_cpc
    FROM campaign
    WHERE segments.date = '{today_str}'
        AND campaign.status = 'ENABLED'
    ORDER BY metrics.cost_micros DESC
"""

response = ga_service.search(customer_id=customer_id, query=query)

total_spend = 0
total_calls = 0
total_clicks = 0
total_impressions = 0
active_campaigns = 0

print(f"\n{'Campaign Name':<50} {'Spend':>12} {'Conv':>6} {'Clicks':>8} {'Impr':>10} {'CPA':>10}")
print("-" * 100)

for row in response:
    spend = row.metrics.cost_micros / 1_000_000
    calls = row.metrics.conversions
    clicks = row.metrics.clicks
    impressions = row.metrics.impressions

    # Only show campaigns with spend > 0
    if spend > 0:
        active_campaigns += 1
        total_spend += spend
        total_calls += calls
        total_clicks += clicks
        total_impressions += impressions

        cpa = spend / calls if calls > 0 else 0

        print(f"{row.campaign.name:<50} ${spend:>11.2f} {int(calls):>6} {clicks:>8} {impressions:>10} ${cpa:>9.2f}")

print("=" * 100)
avg_cpa = total_spend / total_calls if total_calls > 0 else 0
ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
avg_cpc = total_spend / total_clicks if total_clicks > 0 else 0

print(f"{'TOTAL':<50} ${total_spend:>11.2f} {int(total_calls):>6} {total_clicks:>8} {total_impressions:>10} ${avg_cpa:>9.2f}")

print(f"\n📈 Summary:")
print(f"   • Active Campaigns: {active_campaigns}")
print(f"   • Total Ad Spend: ${total_spend:,.2f}")
print(f"   • Total Conversions: {int(total_calls)}")
print(f"   • Total Clicks: {total_clicks}")
print(f"   • Total Impressions: {total_impressions:,}")
print(f"   • Average CPA: ${avg_cpa:.2f}")
print(f"   • Average CPC: ${avg_cpc:.2f}")
print(f"   • CTR: {ctr:.2f}%")

# Get conversion breakdown
print("\n" + "=" * 100)
print("📋 CONVERSION BREAKDOWN")
print("=" * 100)

query_conv = f"""
    SELECT
        segments.conversion_action_name,
        metrics.conversions
    FROM campaign
    WHERE segments.date = '{today_str}'
        AND metrics.conversions > 0
"""

response_conv = ga_service.search(customer_id=customer_id, query=query_conv)

conversions_by_type = {}
for row in response_conv:
    conv_name = row.segments.conversion_action_name
    conversions = row.metrics.conversions

    if conv_name:
        if conv_name not in conversions_by_type:
            conversions_by_type[conv_name] = 0
        conversions_by_type[conv_name] += conversions

if conversions_by_type:
    print(f"\n{'Conversion Type':<60} {'Count':>10}")
    print("-" * 100)
    for conv_type, count in sorted(conversions_by_type.items(), key=lambda x: x[1], reverse=True):
        print(f"{conv_type:<60} {int(count):>10}")
else:
    print("\nNo conversions yet today.")

print("\n" + "=" * 100)
