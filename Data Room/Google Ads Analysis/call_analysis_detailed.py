import urllib.request
import json
from datetime import datetime
from collections import defaultdict
from google.ads.googleads.client import GoogleAdsClient
import warnings
warnings.filterwarnings('ignore')

# ==================== CONFIGURATION ====================
METABASE_URL = "https://starry-bolt.metabaseapp.com"
METABASE_KEY = "mb_XRBKMlQkz3Waw1jpgaNUVIYM+nEkF2bCexU1sUI0Uks="

def metabase_request(endpoint, method="GET", data=None):
    """Make request to Metabase API"""
    url = f"{METABASE_URL}{endpoint}"
    headers = {"x-api-key": METABASE_KEY, "Content-Type": "application/json"}
    req = urllib.request.Request(url, headers=headers, method=method)
    if data:
        req.data = json.dumps(data).encode()
    try:
        response = urllib.request.urlopen(req)
        return json.loads(response.read())
    except Exception as e:
        print(f"Error with request to {endpoint}: {e}")
        return None

def run_metabase_query(query_json):
    """Run a native MongoDB query via Metabase"""
    return metabase_request("/api/dataset", method="POST", data=query_json)

print("=" * 160)
print("🔍 COMPREHENSIVE CALL DISCREPANCY ANALYSIS")
print("=" * 160)

# ==================== PART 1: METABASE CALL DATA ====================
print("\n\n📞 PART 1: PULLING CALL DATA FROM METABASE")
print("=" * 160)

# Define date ranges for analysis
weeks = {
    'Week 1': {'start': '2026-02-01', 'end': '2026-02-07'},
    'Week 2': {'start': '2026-02-08', 'end': '2026-02-14'},
    'Week 3': {'start': '2026-02-15', 'end': '2026-02-21'}
}

print("\n📅 Analysis Periods:")
for week, dates in weeks.items():
    print(f"   • {week}: {dates['start']} to {dates['end']}")

# Query: Get all calls from the calls collection
print("\n\n🔍 Querying 'calls' collection for Feb 1-21...")

# Try querying the existing saved question for call volume
print("   Attempting to use existing saved question: 'KPI: Daily Call Volume by Category'")

# Get the existing card/question data
card_id = 311  # KPI: Daily Call Volume by Category
card_query_result = metabase_request(f"/api/card/{card_id}/query")

calls_result = card_query_result

if calls_result and calls_result.get('status') == 'completed':
    print("✅ Call data retrieved successfully")

    # Parse results
    rows = calls_result.get('data', {}).get('rows', [])
    cols = calls_result.get('data', {}).get('cols', [])

    print(f"\n📊 Total calls found: {len(rows)}")

    if len(rows) > 0:
        print(f"\n🔍 Sample call record (first row):")
        for i, col in enumerate(cols):
            if i < len(rows[0]):
                print(f"   • {col.get('display_name')}: {rows[0][i]}")

        # Analyze calls by week
        print("\n\n📊 CALL BREAKDOWN BY WEEK")
        print("=" * 160)

        weekly_stats = defaultdict(lambda: {
            'total_calls': 0,
            'by_medium': defaultdict(int),
            'by_duration': {'<30s': 0, '30s-2min': 0, '2-5min': 0, '5min+': 0},
            'by_source': defaultdict(int),
            'by_campaign': defaultdict(int)
        })

        # Process each call
        for row in rows:
            call_data = {}
            for i, col in enumerate(cols):
                if i < len(row):
                    call_data[col.get('name')] = row[i]

            # Determine week
            call_time = call_data.get('callTime')
            if call_time:
                call_date = call_time[:10] if isinstance(call_time, str) else str(call_time)[:10]

                week_label = None
                for week, dates in weeks.items():
                    if dates['start'] <= call_date <= dates['end']:
                        week_label = week
                        break

                if week_label:
                    weekly_stats[week_label]['total_calls'] += 1

                    # By medium
                    medium = call_data.get('callMedium', 'Unknown')
                    weekly_stats[week_label]['by_medium'][medium] += 1

                    # By duration
                    duration = call_data.get('callDuration', 0)
                    if isinstance(duration, (int, float)):
                        if duration < 30:
                            weekly_stats[week_label]['by_duration']['<30s'] += 1
                        elif duration < 120:
                            weekly_stats[week_label]['by_duration']['30s-2min'] += 1
                        elif duration < 300:
                            weekly_stats[week_label]['by_duration']['2-5min'] += 1
                        else:
                            weekly_stats[week_label]['by_duration']['5min+'] += 1

                    # By source
                    source = call_data.get('callSource', 'Unknown')
                    weekly_stats[week_label]['by_source'][source] += 1

                    # By campaign
                    campaign = call_data.get('campaignName', 'Unknown')
                    weekly_stats[week_label]['by_campaign'][campaign] += 1

        # Display weekly stats
        print(f"\n{'Week':<15} {'Total Calls':>12} {'<30s':>8} {'30s-2min':>10} {'2-5min':>8} {'5min+':>8}")
        print("-" * 80)
        for week in ['Week 1', 'Week 2', 'Week 3']:
            stats = weekly_stats[week]
            print(f"{week:<15} {stats['total_calls']:>12} "
                  f"{stats['by_duration']['<30s']:>8} "
                  f"{stats['by_duration']['30s-2min']:>10} "
                  f"{stats['by_duration']['2-5min']:>8} "
                  f"{stats['by_duration']['5min+']:>8}")

        print(f"\n\n📊 CALL SOURCE BREAKDOWN")
        print("=" * 160)
        print(f"\n{'Week':<15} {'Source':<30} {'Calls':>10}")
        print("-" * 80)
        for week in ['Week 1', 'Week 2', 'Week 3']:
            stats = weekly_stats[week]
            for source, count in sorted(stats['by_source'].items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"{week:<15} {source:<30} {count:>10}")

        print(f"\n\n📊 TOP CAMPAIGNS BY WEEK")
        print("=" * 160)
        print(f"\n{'Week':<15} {'Campaign':<50} {'Calls':>10}")
        print("-" * 80)
        for week in ['Week 1', 'Week 2', 'Week 3']:
            stats = weekly_stats[week]
            for campaign, count in sorted(stats['by_campaign'].items(), key=lambda x: x[1], reverse=True)[:5]:
                campaign_short = campaign[:47] + '...' if len(campaign) > 50 else campaign
                print(f"{week:<15} {campaign_short:<50} {count:>10}")

else:
    print("⚠️  No call data retrieved from Metabase")
    print("   This could mean:")
    print("   • The query format needs adjustment")
    print("   • The collection structure is different")
    print("   • Data is stored in a different format")

# ==================== PART 2: GOOGLE ADS CALL DATA ====================
print("\n\n📞 PART 2: PULLING GOOGLE ADS CALL DATA")
print("=" * 160)

try:
    client = GoogleAdsClient.load_from_storage('/Users/vinuraabeysundara/Desktop/ICG/DOZR/Data Room/Config/google-ads.yaml')
    ga_service = client.get_service('GoogleAdsService')
    customer_id = '8531896842'

    print("\n✅ Connected to Google Ads API")

    # Query call conversions by week
    for week, dates in weeks.items():
        print(f"\n📊 {week} ({dates['start']} to {dates['end']}):")

        # Query for Phone Calls
        query_phone = f"""
            SELECT
                campaign.name,
                segments.conversion_action_name,
                metrics.conversions
            FROM campaign
            WHERE segments.date BETWEEN '{dates['start']}' AND '{dates['end']}'
                AND campaign.status = 'ENABLED'
                AND campaign.name LIKE '%US%'
                AND metrics.conversions > 0
                AND segments.conversion_action_name LIKE '%Phone Call%'
        """

        # Query for Calls from ads
        query_calls_ads = f"""
            SELECT
                campaign.name,
                segments.conversion_action_name,
                metrics.conversions
            FROM campaign
            WHERE segments.date BETWEEN '{dates['start']}' AND '{dates['end']}'
                AND campaign.status = 'ENABLED'
                AND campaign.name LIKE '%US%'
                AND metrics.conversions > 0
                AND segments.conversion_action_name LIKE '%Calls from ads%'
        """

        week_calls = defaultdict(lambda: {'Phone Call': 0, 'Calls from ads': 0})

        # Get Phone Calls
        response_phone = ga_service.search(customer_id=customer_id, query=query_phone)
        for row in response_phone:
            campaign = row.campaign.name
            conversions = row.metrics.conversions
            week_calls[campaign]['Phone Call'] += conversions

        # Get Calls from ads
        response_ads = ga_service.search(customer_id=customer_id, query=query_calls_ads)
        for row in response_ads:
            campaign = row.campaign.name
            conversions = row.metrics.conversions
            week_calls[campaign]['Calls from ads'] += conversions

        print(f"\n   {'Campaign':<60} {'Phone Calls':>12} {'Calls from Ads':>15} {'Total':>10}")
        print("   " + "-" * 100)

        total_phone = 0
        total_calls_from_ads = 0

        for campaign, calls in sorted(week_calls.items(), key=lambda x: x[1]['Phone Call'] + x[1]['Calls from ads'], reverse=True)[:10]:
            phone = int(calls['Phone Call'])
            ads = int(calls['Calls from ads'])
            total = phone + ads

            total_phone += phone
            total_calls_from_ads += ads

            campaign_short = campaign[:57] + '...' if len(campaign) > 60 else campaign
            print(f"   {campaign_short:<60} {phone:>12} {ads:>15} {total:>10}")

        print("   " + "-" * 100)
        print(f"   {'TOTAL':<60} {total_phone:>12} {total_calls_from_ads:>15} {total_phone + total_calls_from_ads:>10}")

except Exception as e:
    print(f"❌ Error connecting to Google Ads: {e}")

# ==================== PART 3: EXISTING METABASE DASHBOARDS ====================
print("\n\n📊 PART 3: CHECKING EXISTING METABASE DASHBOARDS")
print("=" * 160)

# Get the call volume dashboard data
dashboard_id = 311  # KPI: Daily Call Volume by Category
print(f"\n🔍 Fetching Dashboard: KPI: Daily Call Volume by Category (ID: {dashboard_id})")

card_result = metabase_request(f"/api/card/{dashboard_id}")
if card_result:
    print(f"   ✅ Dashboard found: {card_result.get('name')}")
    print(f"   • Description: {card_result.get('description', 'N/A')}")

# Get Twilio Call Quality Report
dashboard_id = 47
print(f"\n🔍 Fetching Dashboard: Twilio Call Quality Report (ID: {dashboard_id})")

dashboard_result = metabase_request(f"/api/dashboard/{dashboard_id}")
if dashboard_result:
    print(f"   ✅ Dashboard found: {dashboard_result.get('name')}")
    cards = dashboard_result.get('dashcards', [])
    print(f"   • Contains {len(cards)} cards/metrics")

print("\n\n" + "=" * 160)
print("✅ DATA COLLECTION COMPLETE")
print("=" * 160)

print("\n\n📋 SUMMARY OF FINDINGS:")
print("   1. Metabase 'calls' collection contains call logs with attribution")
print("   2. Google Ads shows call conversions by campaign")
print("   3. Existing dashboards provide additional context")
print("\n   Next: Analyze discrepancies and identify root causes")
