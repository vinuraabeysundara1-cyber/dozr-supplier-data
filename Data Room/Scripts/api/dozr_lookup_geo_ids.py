#!/usr/bin/env python3
"""
Lookup Geo Target Constant IDs for new states
"""

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import json

client = GoogleAdsClient.load_from_storage("/Users/vinuraabeysundara/google-ads.yaml")
geo_service = client.get_service("GeoTargetConstantService")

# States to add
NEW_STATES = [
    ("NJ", "New Jersey"),
    ("MD", "Maryland"),
    ("CO", "Colorado"),
    ("MS", "Mississippi"),
    ("UT", "Utah"),
    ("NV", "Nevada"),
    ("NM", "New Mexico"),
    ("MT", "Montana"),
    ("MO", "Missouri"),
    ("WI", "Wisconsin"),
    ("LA", "Louisiana"),
    ("ME", "Maine"),
    ("WA", "Washington"),
    ("IN", "Indiana"),
    ("KS", "Kansas"),
    ("MA", "Massachusetts"),
    ("DE", "Delaware"),
]

print("Looking up Geo Target Constants for new states...")
print("=" * 60)

state_geo_ids = {}

for state_code, state_name in NEW_STATES:
    try:
        request = client.get_type("SuggestGeoTargetConstantsRequest")
        request.locale = "en"
        request.country_code = "US"
        request.location_names.names.append(f"{state_name}")

        response = geo_service.suggest_geo_target_constants(request=request)

        for suggestion in response.geo_target_constant_suggestions:
            geo = suggestion.geo_target_constant
            target_type = str(geo.target_type).split(".")[-1]

            # We want STATE type matching the name
            if target_type == "STATE" and state_name.lower() in geo.name.lower():
                state_geo_ids[state_code] = {
                    "id": geo.id,
                    "name": geo.name,
                    "canonical_name": geo.canonical_name,
                    "resource_name": geo.resource_name,
                }
                print(f"{state_code}: {geo.name} - ID: {geo.id}")
                print(f"    Resource: {geo.resource_name}")
                break

    except GoogleAdsException as ex:
        print(f"{state_code}: Error - {ex.failure.errors[0].message}")
    except Exception as e:
        print(f"{state_code}: Error - {e}")

# Save results
with open("/Users/vinuraabeysundara/dozr_new_state_geo_ids.json", "w") as f:
    json.dump(state_geo_ids, f, indent=2)

print("\n" + "=" * 60)
print(f"Found {len(state_geo_ids)} of {len(NEW_STATES)} states")
print("Saved to: dozr_new_state_geo_ids.json")
