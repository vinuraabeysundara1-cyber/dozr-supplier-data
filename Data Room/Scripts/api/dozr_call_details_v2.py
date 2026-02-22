#!/usr/bin/env python3
"""
Fetch phone call details from Google Ads API - Fixed queries
"""

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from datetime import datetime, timedelta
import json

# Initialize the Google Ads client
client = GoogleAdsClient.load_from_storage("/Users/vinuraabeysundara/google-ads.yaml")
customer_id = "8531896842"

ga_service = client.get_service("GoogleAdsService")

# Date range
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

print("=" * 70)
print("GOOGLE ADS CALL & GCLID DATA EXTRACTION")
print("=" * 70)

# Query 1: Call details from call_view (without date segment)
print("\n1. CALL VIEW DATA (Call Extensions & Call-Only Ads)")
print("-" * 70)

call_view_query = """
    SELECT
        call_view.call_duration_seconds,
        call_view.call_status,
        call_view.call_tracking_display_location,
        call_view.caller_area_code,
        call_view.caller_country_code,
        call_view.start_call_date_time,
        call_view.end_call_date_time,
        call_view.type,
        campaign.name,
        ad_group.name
    FROM call_view
    ORDER BY call_view.start_call_date_time DESC
    LIMIT 5000
"""

try:
    response = ga_service.search(customer_id=customer_id, query=call_view_query)

    call_data = []
    for row in response:
        # Filter by date in Python
        start_time = row.call_view.start_call_date_time
        if start_time:
            call_date = datetime.strptime(start_time[:10], "%Y-%m-%d")
            if call_date >= start_date:
                call_info = {
                    "caller_area_code": row.call_view.caller_area_code,
                    "caller_country_code": row.call_view.caller_country_code,
                    "call_duration_seconds": row.call_view.call_duration_seconds,
                    "call_status": str(row.call_view.call_status).split(".")[-1],
                    "start_time": row.call_view.start_call_date_time,
                    "end_time": row.call_view.end_call_date_time,
                    "call_type": str(row.call_view.type).split(".")[-1],
                    "tracking_location": str(row.call_view.call_tracking_display_location).split(".")[-1],
                    "campaign": row.campaign.name,
                    "ad_group": row.ad_group.name
                }
                call_data.append(call_info)

    print(f"Total calls in last 30 days: {len(call_data)}")

    if call_data:
        # Save to JSON
        with open("/Users/vinuraabeysundara/dozr_call_details.json", "w") as f:
            json.dump({"total_calls": len(call_data), "date_range": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}", "calls": call_data}, f, indent=2)
        print(f"Call details saved to dozr_call_details.json")

        # Print summary by area code
        area_codes = {}
        for call in call_data:
            area = f"+{call['caller_country_code']}-{call['caller_area_code']}"
            area_codes[area] = area_codes.get(area, 0) + 1

        print("\nTop 25 Area Codes:")
        for area, count in sorted(area_codes.items(), key=lambda x: -x[1])[:25]:
            print(f"  {area}: {count} calls")

        # Summary by campaign
        print("\nCalls by Campaign:")
        campaigns = {}
        for call in call_data:
            campaigns[call['campaign']] = campaigns.get(call['campaign'], 0) + 1
        for camp, count in sorted(campaigns.items(), key=lambda x: -x[1])[:10]:
            print(f"  {camp}: {count} calls")

except GoogleAdsException as ex:
    print(f"Call view query failed: {ex.failure.errors[0].message}")
except Exception as e:
    print(f"Error: {e}")

# Query 2: Click view with GCLID - one day at a time for last 7 days
print("\n\n2. CLICK VIEW DATA WITH GCLIDs (Last 7 Days)")
print("-" * 70)

all_clicks = []
for i in range(7):
    query_date = (end_date - timedelta(days=i)).strftime("%Y-%m-%d")

    click_query = f"""
        SELECT
            click_view.gclid,
            click_view.area_of_interest.city,
            click_view.area_of_interest.region,
            click_view.area_of_interest.country,
            campaign.name,
            segments.date
        FROM click_view
        WHERE segments.date = '{query_date}'
        LIMIT 500
    """

    try:
        response = ga_service.search(customer_id=customer_id, query=click_query)
        day_clicks = 0
        for row in response:
            click_info = {
                "gclid": row.click_view.gclid,
                "city": row.click_view.area_of_interest.city if row.click_view.area_of_interest.city else "N/A",
                "region": row.click_view.area_of_interest.region if row.click_view.area_of_interest.region else "N/A",
                "country": row.click_view.area_of_interest.country if row.click_view.area_of_interest.country else "N/A",
                "campaign": row.campaign.name,
                "date": row.segments.date
            }
            all_clicks.append(click_info)
            day_clicks += 1
        print(f"  {query_date}: {day_clicks} clicks with GCLIDs")
    except GoogleAdsException as ex:
        print(f"  {query_date}: Query failed - {ex.failure.errors[0].message}")
    except Exception as e:
        print(f"  {query_date}: Error - {e}")

print(f"\nTotal clicks with GCLIDs (7 days): {len(all_clicks)}")

if all_clicks:
    with open("/Users/vinuraabeysundara/dozr_gclid_clicks.json", "w") as f:
        json.dump({"total_clicks": len(all_clicks), "clicks": all_clicks}, f, indent=2)
    print("GCLID data saved to dozr_gclid_clicks.json")

# Query 3: List all conversion actions
print("\n\n3. CONVERSION ACTIONS (For Reference)")
print("-" * 70)

conversion_query = """
    SELECT
        conversion_action.id,
        conversion_action.name,
        conversion_action.type,
        conversion_action.status
    FROM conversion_action
    WHERE conversion_action.status = 'ENABLED'
"""

try:
    response = ga_service.search(customer_id=customer_id, query=conversion_query)

    print("Active Conversion Actions:")
    for row in response:
        action_type = str(row.conversion_action.type).split(".")[-1]
        print(f"  - {row.conversion_action.name}")
        print(f"    ID: {row.conversion_action.id}, Type: {action_type}")

except GoogleAdsException as ex:
    print(f"Conversion query failed: {ex.failure.errors[0].message}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 70)
print("IMPORTANT: PHONE NUMBER AVAILABILITY")
print("=" * 70)
print("""
Google Ads API Privacy Limitations:
-----------------------------------
1. CALLER AREA CODES: Available (e.g., +1-512, +1-416)
   - Full phone numbers are NOT exposed by Google for privacy

2. GCLIDs: Available - These are click identifiers
   - GCLIDs link ad clicks to conversions
   - Phone numbers associated with GCLIDs are in YOUR systems

WHERE TO FIND FULL PHONE NUMBERS:
---------------------------------
The phone numbers with GCLIDs are stored in:
1. HubSpot CRM - Contacts with GCLID field populated
2. DOZR Backend - Orders/leads with GCLID tracking
3. Call Tracking Software (CallRail, CallTrackingMetrics, etc.)

To get the full list, you would need to:
- Export HubSpot contacts where GCLID is not empty
- Query your backend database for records with GCLIDs
- Export from your call tracking platform
""")
