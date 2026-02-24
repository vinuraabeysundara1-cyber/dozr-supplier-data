from google.ads.googleads.client import GoogleAdsClient
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Load credentials
client = GoogleAdsClient.load_from_storage('/Users/vinuraabeysundara/Desktop/DOZR/Data Room/Config/google-ads.yaml')
ga_service = client.get_service('GoogleAdsService')
customer_id = '8531896842'

# Determine the most recent Sunday
today = datetime.now()
days_since_sunday = (today.weekday() + 1) % 7  # Monday=0, Sunday=6, so we add 1 and mod 7
if days_since_sunday == 0:
    # Today is Sunday
    sunday_date = today
else:
    # Get last Sunday
    sunday_date = today - timedelta(days=days_since_sunday)

date_str = sunday_date.strftime('%Y-%m-%d')
print(f"📊 Campaign Performance for Sunday, {sunday_date.strftime('%B %d, %Y')}\n")
print("=" * 80)

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
    WHERE segments.date = '{date_str}'
        AND campaign.status = 'ENABLED'
    ORDER BY metrics.cost_micros DESC
"""

response = ga_service.search(customer_id=customer_id, query=query)

total_spend = 0
total_calls = 0
total_clicks = 0
total_impressions = 0

print(f"{'Campaign Name':<50} {'Spend':>12} {'Calls':>8} {'Clicks':>8} {'Impr':>10} {'CPA':>10}")
print("-" * 80)

for row in response:
    spend = row.metrics.cost_micros / 1_000_000
    calls = row.metrics.conversions
    clicks = row.metrics.clicks
    impressions = row.metrics.impressions

    total_spend += spend
    total_calls += calls
    total_clicks += clicks
    total_impressions += impressions

    cpa = spend / calls if calls > 0 else 0

    print(f"{row.campaign.name:<50} ${spend:>11.2f} {int(calls):>8} {clicks:>8} {impressions:>10} ${cpa:>9.2f}")

print("=" * 80)
avg_cpa = total_spend / total_calls if total_calls > 0 else 0
ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0

print(f"{'TOTAL':<50} ${total_spend:>11.2f} {int(total_calls):>8} {total_clicks:>8} {total_impressions:>10} ${avg_cpa:>9.2f}")
print(f"\n📈 Summary:")
print(f"   • Total Ad Spend: ${total_spend:,.2f}")
print(f"   • Total Conversions (Calls): {int(total_calls)}")
print(f"   • Average CPA: ${avg_cpa:.2f}")
print(f"   • CTR: {ctr:.2f}%")
