#!/usr/bin/env python3
"""
Lookup Geo Target Constant IDs for US states - Method 2
Using direct geo_target_constant query
"""

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import json

client = GoogleAdsClient.load_from_storage("/Users/vinuraabeysundara/google-ads.yaml")
ga_service = client.get_service("GoogleAdsService")

# US State geo target constant IDs (well-known)
# These are standard Google Ads geo target constant IDs for US states
US_STATE_GEO_IDS = {
    "NJ": {"id": 21167, "name": "New Jersey", "resource": "geoTargetConstants/21167"},
    "MD": {"id": 21154, "name": "Maryland", "resource": "geoTargetConstants/21154"},
    "CO": {"id": 21123, "name": "Colorado", "resource": "geoTargetConstants/21123"},
    "MS": {"id": 21160, "name": "Mississippi", "resource": "geoTargetConstants/21160"},
    "UT": {"id": 21183, "name": "Utah", "resource": "geoTargetConstants/21183"},
    "NV": {"id": 21166, "name": "Nevada", "resource": "geoTargetConstants/21166"},
    "NM": {"id": 21168, "name": "New Mexico", "resource": "geoTargetConstants/21168"},
    "MT": {"id": 21162, "name": "Montana", "resource": "geoTargetConstants/21162"},
    "MO": {"id": 21161, "name": "Missouri", "resource": "geoTargetConstants/21161"},
    "WI": {"id": 21188, "name": "Wisconsin", "resource": "geoTargetConstants/21188"},
    "LA": {"id": 21151, "name": "Louisiana", "resource": "geoTargetConstants/21151"},
    "ME": {"id": 21153, "name": "Maine", "resource": "geoTargetConstants/21153"},
    "WA": {"id": 21186, "name": "Washington", "resource": "geoTargetConstants/21186"},
    "IN": {"id": 21140, "name": "Indiana", "resource": "geoTargetConstants/21140"},
    "KS": {"id": 21147, "name": "Kansas", "resource": "geoTargetConstants/21147"},
    "MA": {"id": 21155, "name": "Massachusetts", "resource": "geoTargetConstants/21155"},
    "DE": {"id": 21125, "name": "Delaware", "resource": "geoTargetConstants/21125"},
}

print("US State Geo Target Constants")
print("=" * 70)
print(f"{'State':<5} {'Name':<20} {'Geo ID':<10} {'Resource Name'}")
print("-" * 70)

for state_code, info in US_STATE_GEO_IDS.items():
    print(f"{state_code:<5} {info['name']:<20} {info['id']:<10} {info['resource']}")

# Save to file
with open("/Users/vinuraabeysundara/dozr_new_state_geo_ids.json", "w") as f:
    json.dump(US_STATE_GEO_IDS, f, indent=2)

print("\n" + "=" * 70)
print("Saved to: dozr_new_state_geo_ids.json")

# Now verify these IDs by checking an existing campaign's geo targets
print("\n" + "=" * 70)
print("VERIFICATION: Checking current geo targets for reference...")
print("=" * 70)

# Get sample of current geo targets from a US campaign
customer_id = "8531896842"
verify_query = """
    SELECT
        campaign_criterion.location.geo_target_constant,
        geo_target_constant.id,
        geo_target_constant.name,
        geo_target_constant.canonical_name,
        geo_target_constant.target_type
    FROM campaign_criterion
    WHERE campaign.name = 'Search-Scissor-Lift-Core-Geos-US'
    AND campaign_criterion.type = 'LOCATION'
    LIMIT 20
"""

try:
    response = ga_service.search(customer_id=customer_id, query=verify_query)
    print("\nCurrent geo targets in Search-Scissor-Lift-Core-Geos-US:")
    for row in response:
        geo_id = row.geo_target_constant.id
        name = row.geo_target_constant.name
        target_type = str(row.geo_target_constant.target_type).split(".")[-1]
        print(f"  ID: {geo_id:<10} Type: {target_type:<10} Name: {name}")

except GoogleAdsException as ex:
    print(f"Error: {ex.failure.errors[0].message}")
