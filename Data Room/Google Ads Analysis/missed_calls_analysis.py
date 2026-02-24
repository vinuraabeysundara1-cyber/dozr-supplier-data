from google.ads.googleads.client import GoogleAdsClient
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Load credentials
client = GoogleAdsClient.load_from_storage('/Users/vinuraabeysundara/Desktop/ICG/DOZR/Data Room/Config/google-ads.yaml')
ga_service = client.get_service('GoogleAdsService')
customer_id = '8531896842'

# Define periods
period1_start = '2026-02-01'
period1_end = '2026-02-10'
period2_start = '2026-02-10'
period2_end = '2026-02-20'

print("=" * 140)
print(f"📞 MISSED CALLS ANALYSIS - Comparing Call Handling Before & After Expansion Launch")
print("=" * 140)

def get_call_data(start_date, end_date, period_name):
    """Get call conversion data for a specific period"""

    # Query for all call-related conversions
    query = f"""
        SELECT
            segments.conversion_action_name,
            metrics.conversions,
            metrics.all_conversions
        FROM campaign
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
            AND campaign.status = 'ENABLED'
            AND campaign.name LIKE '%US%'
            AND metrics.conversions > 0
    """

    response = ga_service.search(customer_id=customer_id, query=query)

    call_data = {
        'phone_calls': 0,
        'calls_from_ads': 0,
        'all_conversions': 0,
        'conversion_details': {}
    }

    for row in response:
        conv_name = row.segments.conversion_action_name
        conversions = row.metrics.conversions
        all_conversions = row.metrics.all_conversions

        if conv_name == 'Phone Call':
            call_data['phone_calls'] += conversions
        elif conv_name == 'Calls from ads':
            call_data['calls_from_ads'] += conversions

        call_data['all_conversions'] += conversions

        # Track all conversion types
        if conv_name not in call_data['conversion_details']:
            call_data['conversion_details'][conv_name] = 0
        call_data['conversion_details'][conv_name] += conversions

    call_data['total_calls'] = call_data['phone_calls'] + call_data['calls_from_ads']

    return call_data

# Get call data for both periods
print("\n📊 Fetching call data...")

period1_data = get_call_data(period1_start, period1_end, "Period 1 (Feb 1-10)")
period2_data = get_call_data(period2_start, period2_end, "Period 2 (Feb 10-20)")

# Print comparison
print(f"\n{'=' * 140}")
print(f"📊 CALL VOLUME COMPARISON")
print(f"{'=' * 140}")

print(f"\n{'Metric':<40} {'Period 1 (Feb 1-10)':>25} {'Period 2 (Feb 10-20)':>25} {'Change':>20}")
print("-" * 140)

# Total calls
total_calls_p1 = period1_data['total_calls']
total_calls_p2 = period2_data['total_calls']
calls_change = total_calls_p2 - total_calls_p1
calls_change_pct = (calls_change / total_calls_p1 * 100) if total_calls_p1 > 0 else 0

print(f"{'Total Calls':<40} {int(total_calls_p1):>25} {int(total_calls_p2):>25} {calls_change:>+19.0f} ({calls_change_pct:+.1f}%)")

# Phone calls
phone_p1 = period1_data['phone_calls']
phone_p2 = period2_data['phone_calls']
phone_change = phone_p2 - phone_p1
phone_change_pct = (phone_change / phone_p1 * 100) if phone_p1 > 0 else 0

print(f"{'Phone Calls':<40} {int(phone_p1):>25} {int(phone_p2):>25} {phone_change:>+19.0f} ({phone_change_pct:+.1f}%)")

# Calls from ads
ads_p1 = period1_data['calls_from_ads']
ads_p2 = period2_data['calls_from_ads']
ads_change = ads_p2 - ads_p1
ads_change_pct = (ads_change / ads_p1 * 100) if ads_p1 > 0 else 0

print(f"{'Calls from Ads':<40} {int(ads_p1):>25} {int(ads_p2):>25} {ads_change:>+19.0f} ({ads_change_pct:+.1f}%)")

# Daily average
days_p1 = 10
days_p2 = 11  # Feb 10-20 is 11 days
daily_avg_p1 = total_calls_p1 / days_p1
daily_avg_p2 = total_calls_p2 / days_p2
daily_change = daily_avg_p2 - daily_avg_p1

print(f"\n{'Daily Average Calls':<40} {daily_avg_p1:>25.1f} {daily_avg_p2:>25.1f} {daily_change:>+19.1f}")

# Print detailed conversion breakdown
print(f"\n{'=' * 140}")
print(f"📋 DETAILED CONVERSION BREAKDOWN")
print(f"{'=' * 140}")

print(f"\n{'Conversion Type':<60} {'Period 1':>20} {'Period 2':>20} {'Change':>20}")
print("-" * 140)

# Get all unique conversion types
all_conv_types = set(period1_data['conversion_details'].keys()) | set(period2_data['conversion_details'].keys())

for conv_type in sorted(all_conv_types):
    p1_count = period1_data['conversion_details'].get(conv_type, 0)
    p2_count = period2_data['conversion_details'].get(conv_type, 0)
    change = p2_count - p1_count

    print(f"{conv_type:<60} {int(p1_count):>20} {int(p2_count):>20} {change:>+19.0f}")

# Analysis
print(f"\n{'=' * 140}")
print(f"💡 CALL HANDLING CAPACITY ANALYSIS")
print(f"{'=' * 140}")

print(f"\n🔍 Key Findings:")

if calls_change > 0:
    print(f"   ✅ Call volume INCREASED by {int(calls_change)} calls ({calls_change_pct:+.1f}%)")
    print(f"      Period 1: {int(total_calls_p1)} calls over {days_p1} days ({daily_avg_p1:.1f} calls/day)")
    print(f"      Period 2: {int(total_calls_p2)} calls over {days_p2} days ({daily_avg_p2:.1f} calls/day)")
else:
    print(f"   📉 Call volume DECREASED by {abs(int(calls_change))} calls ({abs(calls_change_pct):.1f}%)")

print(f"\n⚠️  IMPORTANT NOTE:")
print(f"   Google Ads only tracks call attempts (clicks on phone numbers or call extensions).")
print(f"   To analyze MISSED CALLS, we need to check CallRail or your phone system data.")
print(f"   ")
print(f"   Google Ads data shows:")
print(f"   • Total call attempts/conversions")
print(f"   • NOT whether calls were answered or missed")
print(f"   • NOT call duration or quality")

print(f"\n📞 Next Steps to Analyze Missed Calls:")
print(f"   1. Check CallRail dashboard for missed calls ratio")
print(f"   2. Compare answered vs. missed calls for both periods")
print(f"   3. Review call duration and abandonment rates")
print(f"   4. Check if voicemail/IVR settings are optimized")

print(f"\n{'=' * 140}")
print("✅ ANALYSIS COMPLETE")
print(f"{'=' * 140}")

print(f"\n💬 If you have CallRail access credentials, I can pull detailed missed call data.")
print(f"   Otherwise, please check CallRail manually for:")
print(f"   • Missed call count for Feb 1-10 vs Feb 10-20")
print(f"   • Answer rate percentage")
print(f"   • Average time to answer")
