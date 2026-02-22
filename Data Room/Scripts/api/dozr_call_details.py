#!/usr/bin/env python3
"""
Fetch phone call details from Google Ads API for the last 30 days.
"""

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from datetime import datetime, timedelta
import json

# Initialize the Google Ads client
client = GoogleAdsClient.load_from_storage("/Users/vinuraabeysundara/google-ads.yaml")
customer_id = "8531896842"

ga_service = client.get_service("GoogleAdsService")

# Date range for last 30 days
end_date = datetime.now()
start_date = end_date - timedelta(days=30)
start_date_str = start_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")

print(f"Fetching call details from {start_date_str} to {end_date_str}")
print("=" * 60)

# Query 1: Call details from call_view (call extensions and call-only ads)
call_view_query = f"""
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
    WHERE segments.date BETWEEN '{start_date_str}' AND '{end_date_str}'
    ORDER BY call_view.start_call_date_time DESC
"""

print("\n1. CALL VIEW DATA (Call Extensions & Call-Only Ads)")
print("-" * 60)

try:
    response = ga_service.search(customer_id=customer_id, query=call_view_query)

    call_data = []
    for row in response:
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

    print(f"Total calls found: {len(call_data)}")

    if call_data:
        # Save to JSON
        with open("/Users/vinuraabeysundara/dozr_call_details.json", "w") as f:
            json.dump({"total_calls": len(call_data), "calls": call_data}, f, indent=2)
        print(f"Call details saved to dozr_call_details.json")

        # Print summary by area code
        area_codes = {}
        for call in call_data:
            area = f"+{call['caller_country_code']}-{call['caller_area_code']}"
            area_codes[area] = area_codes.get(area, 0) + 1

        print("\nCalls by Area Code:")
        for area, count in sorted(area_codes.items(), key=lambda x: -x[1])[:20]:
            print(f"  {area}: {count} calls")

except GoogleAdsException as ex:
    print(f"Call view query failed: {ex.failure.errors[0].message}")
except Exception as e:
    print(f"Error: {e}")

# Query 2: Check for click_view with GCLID data
print("\n\n2. CLICK VIEW DATA (GCLID Information)")
print("-" * 60)

click_query = f"""
    SELECT
        click_view.gclid,
        click_view.area_of_interest.city,
        click_view.area_of_interest.region,
        click_view.area_of_interest.country,
        campaign.name,
        segments.date
    FROM click_view
    WHERE segments.date BETWEEN '{start_date_str}' AND '{end_date_str}'
    LIMIT 1000
"""

try:
    response = ga_service.search(customer_id=customer_id, query=click_query)

    click_data = []
    for row in response:
        click_info = {
            "gclid": row.click_view.gclid,
            "city": row.click_view.area_of_interest.city if row.click_view.area_of_interest.city else "N/A",
            "region": row.click_view.area_of_interest.region if row.click_view.area_of_interest.region else "N/A",
            "country": row.click_view.area_of_interest.country if row.click_view.area_of_interest.country else "N/A",
            "campaign": row.campaign.name,
            "date": row.segments.date
        }
        click_data.append(click_info)

    print(f"Click records with GCLIDs found: {len(click_data)}")

    if click_data:
        with open("/Users/vinuraabeysundara/dozr_gclid_clicks.json", "w") as f:
            json.dump({"total_clicks": len(click_data), "clicks": click_data[:100]}, f, indent=2)
        print("Sample GCLID data saved to dozr_gclid_clicks.json")

except GoogleAdsException as ex:
    print(f"Click view query failed: {ex.failure.errors[0].message}")
except Exception as e:
    print(f"Error: {e}")

# Query 3: Offline conversion uploads (these contain GCLIDs)
print("\n\n3. OFFLINE CONVERSIONS (Uploaded via GCLID)")
print("-" * 60)

conversion_query = f"""
    SELECT
        conversion_action.name,
        conversion_action.type,
        metrics.all_conversions,
        metrics.all_conversions_value,
        segments.conversion_action_name,
        segments.date
    FROM conversion_action
    WHERE conversion_action.type = 'UPLOAD_CLICKS'
"""

try:
    response = ga_service.search(customer_id=customer_id, query=conversion_query)

    print("Offline Conversion Actions (GCLID-based):")
    for row in response:
        print(f"  - {row.conversion_action.name}")
        print(f"    Type: {str(row.conversion_action.type).split('.')[-1]}")

except GoogleAdsException as ex:
    print(f"Conversion query failed: {ex.failure.errors[0].message}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("IMPORTANT NOTE:")
print("=" * 60)
print("""
Google Ads API provides:
1. CALL VIEW: Area codes and call duration for calls through call extensions
   - Full phone numbers are NOT exposed for privacy reasons
   - Only area codes are available

2. CLICK VIEW: GCLIDs for ad clicks
   - GCLIDs identify the click, not the caller's phone number
   - Phone numbers associated with GCLIDs are stored in YOUR CRM/backend

3. OFFLINE CONVERSIONS: Conversions uploaded via GCLID
   - The phone numbers are in your system (HubSpot, etc.)
   - Google only stores the GCLID and conversion value

To get actual phone numbers with GCLIDs, you need to query your:
- HubSpot CRM
- DOZR backend database
- Call tracking software (CallRail, CallTrackingMetrics, etc.)
""")
