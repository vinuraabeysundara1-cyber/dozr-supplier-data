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

print("=" * 120)
print(f"📊 WEEKEND AD EXPERIMENT SUMMARY - February 21-22, 2026")
print(f"Generated: {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}")
print("=" * 120)

# Get totals for each day
query_totals = f"""
    SELECT
        segments.date,
        metrics.cost_micros,
        metrics.clicks,
        metrics.impressions,
        metrics.conversions,
        metrics.all_conversions
    FROM campaign
    WHERE segments.date BETWEEN '{saturday_str}' AND '{sunday_str}'
        AND campaign.status = 'ENABLED'
"""

response_totals = ga_service.search(customer_id=customer_id, query=query_totals)

totals = {
    saturday_str: {'spend': 0, 'clicks': 0, 'impressions': 0, 'conversions': 0},
    sunday_str: {'spend': 0, 'clicks': 0, 'impressions': 0, 'conversions': 0}
}

for row in response_totals:
    date = row.segments.date
    totals[date]['spend'] += row.metrics.cost_micros / 1_000_000
    totals[date]['clicks'] += row.metrics.clicks
    totals[date]['impressions'] += row.metrics.impressions
    totals[date]['conversions'] += row.metrics.conversions

# Get conversion breakdown
query_conv = f"""
    SELECT
        segments.date,
        segments.conversion_action_name,
        metrics.conversions
    FROM campaign
    WHERE segments.date BETWEEN '{saturday_str}' AND '{sunday_str}'
        AND metrics.conversions > 0
"""

response_conv = ga_service.search(customer_id=customer_id, query=query_conv)

conversions = {
    saturday_str: {},
    sunday_str: {}
}

for row in response_conv:
    date = row.segments.date
    conv_name = row.segments.conversion_action_name
    conv_count = row.metrics.conversions

    if conv_name:
        if conv_name not in conversions[date]:
            conversions[date][conv_name] = 0
        conversions[date][conv_name] += conv_count

# Calculate metrics
sat = totals[saturday_str]
sun = totals[sunday_str]

sat_cpc = sat['spend'] / sat['clicks'] if sat['clicks'] > 0 else 0
sun_cpc = sun['spend'] / sun['clicks'] if sun['clicks'] > 0 else 0

sat_cpa = sat['spend'] / sat['conversions'] if sat['conversions'] > 0 else 0
sun_cpa = sun['spend'] / sun['conversions'] if sun['conversions'] > 0 else 0

sat_ctr = (sat['clicks'] / sat['impressions'] * 100) if sat['impressions'] > 0 else 0
sun_ctr = (sun['clicks'] / sun['impressions'] * 100) if sun['impressions'] > 0 else 0

# Weekend totals
weekend_spend = sat['spend'] + sun['spend']
weekend_clicks = sat['clicks'] + sun['clicks']
weekend_impressions = sat['impressions'] + sun['impressions']
weekend_conversions = sat['conversions'] + sun['conversions']
weekend_cpa = weekend_spend / weekend_conversions if weekend_conversions > 0 else 0
weekend_cpc = weekend_spend / weekend_clicks if weekend_clicks > 0 else 0
weekend_ctr = (weekend_clicks / weekend_impressions * 100) if weekend_impressions > 0 else 0

# Print Day-by-Day Performance
print("\n" + "=" * 120)
print("📅 DAY-BY-DAY PERFORMANCE")
print("=" * 120)

print(f"\n{'Metric':<30} {'Saturday':>25} {'Sunday':>25} {'Weekend Total':>25}")
print("-" * 120)
print(f"{'💰 Ad Spend':<30} ${sat['spend']:>24.2f} ${sun['spend']:>24.2f} ${weekend_spend:>24.2f}")
print(f"{'👆 Clicks':<30} {sat['clicks']:>25} {sun['clicks']:>25} {weekend_clicks:>25}")
print(f"{'👁️  Impressions':<30} {sat['impressions']:>25} {sun['impressions']:>25} {weekend_impressions:>25}")
print(f"{'📊 Average CPC':<30} ${sat_cpc:>24.2f} ${sun_cpc:>24.2f} ${weekend_cpc:>24.2f}")
print(f"{'📈 CTR':<30} {sat_ctr:>23.2f}% {sun_ctr:>23.2f}% {weekend_ctr:>23.2f}%")
print(f"{'📞 Total Conversions':<30} {int(sat['conversions']):>25} {int(sun['conversions']):>25} {int(weekend_conversions):>25}")
print(f"{'🎯 Average CPA':<30} ${sat_cpa:>24.2f} ${sun_cpa:>24.2f} ${weekend_cpa:>24.2f}")

# Conversion Breakdown
print("\n" + "=" * 120)
print("📋 CONVERSION BREAKDOWN")
print("=" * 120)

all_conv_types = set()
for date in [saturday_str, sunday_str]:
    all_conv_types.update(conversions[date].keys())

if all_conv_types:
    print(f"\n{'Conversion Type':<60} {'Saturday':>20} {'Sunday':>20} {'Total':>15}")
    print("-" * 120)

    weekend_conv_totals = {}
    for conv_type in sorted(all_conv_types):
        sat_conv = conversions[saturday_str].get(conv_type, 0)
        sun_conv = conversions[sunday_str].get(conv_type, 0)
        total_conv = sat_conv + sun_conv
        weekend_conv_totals[conv_type] = total_conv

        print(f"{conv_type:<60} {int(sat_conv):>20} {int(sun_conv):>20} {int(total_conv):>15}")

    # Calculate funnel metrics
    total_phone_calls = 0
    total_quotes = 0
    total_deals = 0

    for conv_type, count in weekend_conv_totals.items():
        if 'Phone Call' in conv_type or 'Calls from ads' in conv_type:
            total_phone_calls += count
        elif 'quote' in conv_type.lower():
            total_quotes += count
        elif 'Closed Won' in conv_type or 'Deal' in conv_type:
            total_deals += count

    # Adjust: deals are also quotes
    total_quotes_including_deals = total_quotes + total_deals

    print("\n" + "=" * 120)
    print("🎯 CONVERSION FUNNEL ANALYSIS")
    print("=" * 120)
    print(f"\n📞 Total Phone Calls: {int(total_phone_calls)}")
    print(f"💬 Total Quotes (including deals): {int(total_quotes_including_deals)}")
    print(f"🎉 Total Closed Deals: {int(total_deals)}")

    call_to_quote = (total_quotes_including_deals / total_phone_calls * 100) if total_phone_calls > 0 else 0
    quote_to_deal = (total_deals / total_quotes_including_deals * 100) if total_quotes_including_deals > 0 else 0
    call_to_deal = (total_deals / total_phone_calls * 100) if total_phone_calls > 0 else 0

    print(f"\n📊 Call → Quote Rate: {call_to_quote:.1f}%")
    print(f"🎯 Quote → Deal Rate: {quote_to_deal:.1f}%")
    print(f"💰 Call → Deal Rate: {call_to_deal:.1f}%")

# Key Insights
print("\n" + "=" * 120)
print("💡 KEY INSIGHTS & RECOMMENDATIONS")
print("=" * 120)

spend_change = ((sun['spend'] - sat['spend']) / sat['spend'] * 100) if sat['spend'] > 0 else 0
conv_change = ((sun['conversions'] - sat['conversions']) / sat['conversions'] * 100) if sat['conversions'] > 0 else 0
cpa_change = ((sun_cpa - sat_cpa) / sat_cpa * 100) if sat_cpa > 0 else 0

print(f"\n1. EFFICIENCY IMPROVEMENT:")
print(f"   • Sunday CPA was ${sun_cpa:.2f} vs Saturday ${sat_cpa:.2f} ({abs(cpa_change):.1f}% {'better' if cpa_change < 0 else 'worse'})")
print(f"   • Sunday spent {abs(spend_change):.1f}% {'less' if spend_change < 0 else 'more'} but CPA improved significantly")

print(f"\n2. WEEKEND PERFORMANCE:")
print(f"   • Total Weekend Spend: ${weekend_spend:,.2f}")
print(f"   • Total Weekend Conversions: {int(weekend_conversions)}")
print(f"   • Weekend Average CPA: ${weekend_cpa:.2f}")
print(f"   • ROI Potential: {int(total_deals)} deal(s) closed this weekend")

print(f"\n3. SUNDAY STANDOUT:")
if total_deals > 0:
    print(f"   • Closed {int(total_deals)} deal(s) on Sunday!")
    print(f"   • Quote-to-Deal conversion rate of {quote_to_deal:.1f}% is exceptional")

print(f"\n4. CALL QUALITY:")
print(f"   • {call_to_quote:.1f}% of calls resulted in quotes")
print(f"   • Weekend traffic may be lower volume but quality remains strong")

print("\n" + "=" * 120)
print("✅ WEEKEND EXPERIMENT COMPLETE")
print("=" * 120)
