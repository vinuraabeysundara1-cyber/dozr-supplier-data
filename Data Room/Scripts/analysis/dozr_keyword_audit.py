#!/usr/bin/env python3
"""
DOZR Keyword Audit - Check for location-based keywords
"""

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import json
import re

client = GoogleAdsClient.load_from_storage("/Users/vinuraabeysundara/google-ads.yaml")
customer_id = "8531896842"
ga_service = client.get_service("GoogleAdsService")

# Target campaigns
TARGET_CAMPAIGNS = [
    "Search-Scissor-Lift-Core-Geos-US",
    "Search-Forklift-Core-Geos-US",
    "Search-Telehandler-Core-Geos-US",
    "Search-Excavator-Core-Geos-US",
    "Search-Dozers-Core-Geos-US-V3",
    "Search-Backhoe-Core-Geos-US",
    "Search-Loader-Core-Geos-US",
    "Search-Demand-Boom-Lifts",
    "DSA-AllPages-Tier1-New-US-2",
]

# US States and cities to check for
US_STATES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
    "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
    "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan",
    "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
    "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
    "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia",
    "Wisconsin", "Wyoming"
]

STATE_ABBREVS = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN",
    "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV",
    "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN",
    "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
]

MAJOR_CITIES = [
    "Houston", "Dallas", "Austin", "San Antonio", "Phoenix", "Los Angeles", "San Diego",
    "San Francisco", "Miami", "Orlando", "Tampa", "Jacksonville", "Atlanta", "Chicago",
    "New York", "Brooklyn", "Denver", "Seattle", "Portland", "Las Vegas", "Boston",
    "Philadelphia", "Detroit", "Minneapolis", "Charlotte", "Nashville", "Memphis",
    "Baltimore", "Indianapolis", "Columbus", "Cleveland", "Pittsburgh", "St. Louis",
    "Kansas City", "Milwaukee", "Raleigh", "Richmond", "Virginia Beach", "Newark",
    "Jersey City", "Albuquerque", "Tucson", "Mesa", "Sacramento", "Oakland", "Fresno"
]

# Location keywords patterns
LOCATION_PATTERNS = [
    r'\bnear me\b',
    r'\bnearby\b',
    r'\blocal\b',
    r'\bin my area\b',
]

print("=" * 80)
print("DOZR KEYWORD AUDIT - LOCATION-BASED KEYWORDS CHECK")
print("=" * 80)

all_keywords = {}
location_keywords = {}
near_me_keywords = {}

for camp_name in TARGET_CAMPAIGNS:
    print(f"\n{'='*80}")
    print(f"CAMPAIGN: {camp_name}")
    print("=" * 80)

    # Get all keywords for this campaign
    keyword_query = f"""
        SELECT
            campaign.id,
            campaign.name,
            ad_group.name,
            ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type,
            ad_group_criterion.status
        FROM keyword_view
        WHERE campaign.name = '{camp_name}'
        AND ad_group_criterion.status != 'REMOVED'
    """

    try:
        response = ga_service.search(customer_id=customer_id, query=keyword_query)

        keywords = []
        location_based = []
        near_me_based = []

        for row in response:
            kw_text = row.ad_group_criterion.keyword.text.lower()
            kw_info = {
                "keyword": row.ad_group_criterion.keyword.text,
                "match_type": str(row.ad_group_criterion.keyword.match_type).split(".")[-1],
                "ad_group": row.ad_group.name,
                "status": str(row.ad_group_criterion.status).split(".")[-1]
            }
            keywords.append(kw_info)

            # Check for state names
            has_state = False
            for state in US_STATES:
                if state.lower() in kw_text:
                    location_based.append({**kw_info, "location_type": "STATE", "location": state})
                    has_state = True
                    break

            # Check for state abbreviations (with word boundaries)
            if not has_state:
                for abbrev in STATE_ABBREVS:
                    if re.search(rf'\b{abbrev.lower()}\b', kw_text):
                        location_based.append({**kw_info, "location_type": "STATE_ABBREV", "location": abbrev})
                        has_state = True
                        break

            # Check for city names
            if not has_state:
                for city in MAJOR_CITIES:
                    if city.lower() in kw_text:
                        location_based.append({**kw_info, "location_type": "CITY", "location": city})
                        break

            # Check for "near me" type keywords
            for pattern in LOCATION_PATTERNS:
                if re.search(pattern, kw_text):
                    near_me_based.append({**kw_info, "pattern": pattern})
                    break

        all_keywords[camp_name] = keywords
        location_keywords[camp_name] = location_based
        near_me_keywords[camp_name] = near_me_based

        print(f"\nTotal Keywords: {len(keywords)}")
        print(f"Location-Based Keywords (State/City): {len(location_based)}")
        print(f"'Near Me' Type Keywords: {len(near_me_based)}")

        if location_based:
            print(f"\n  LOCATION-BASED KEYWORDS FOUND:")
            for kw in location_based:
                print(f"    [{kw['match_type'][:5]}] \"{kw['keyword']}\" ({kw['location_type']}: {kw['location']})")

        if near_me_based:
            print(f"\n  'NEAR ME' TYPE KEYWORDS:")
            for kw in near_me_based:
                print(f"    [{kw['match_type'][:5]}] \"{kw['keyword']}\"")

        if not location_based and not near_me_based:
            print(f"\n  >> NO LOCATION-BASED KEYWORDS - Uses generic equipment terms only")
            print(f"  Sample keywords:")
            for kw in keywords[:5]:
                print(f"    [{kw['match_type'][:5]}] \"{kw['keyword']}\"")

    except GoogleAdsException as ex:
        print(f"Error: {ex.failure.errors[0].message}")

# Summary
print("\n" + "=" * 80)
print("SUMMARY: LOCATION-BASED KEYWORDS BY CAMPAIGN")
print("=" * 80)

print(f"\n{'Campaign':<45} {'Total KWs':<12} {'Location':<12} {'Near Me':<12}")
print("-" * 80)

total_location = 0
total_near_me = 0

for camp_name in TARGET_CAMPAIGNS:
    total = len(all_keywords.get(camp_name, []))
    loc = len(location_keywords.get(camp_name, []))
    near = len(near_me_keywords.get(camp_name, []))
    total_location += loc
    total_near_me += near

    flag = "⚠️ NEEDS REVIEW" if loc > 0 else "✓ OK"
    print(f"{camp_name:<45} {total:<12} {loc:<12} {near:<12} {flag}")

print("-" * 80)
print(f"{'TOTAL':<45} {'':<12} {total_location:<12} {total_near_me:<12}")

# Save detailed data
output = {
    "all_keywords": {k: v for k, v in all_keywords.items()},
    "location_keywords": location_keywords,
    "near_me_keywords": near_me_keywords,
    "summary": {
        camp: {
            "total": len(all_keywords.get(camp, [])),
            "location_based": len(location_keywords.get(camp, [])),
            "near_me": len(near_me_keywords.get(camp, []))
        }
        for camp in TARGET_CAMPAIGNS
    }
}

with open("/Users/vinuraabeysundara/dozr_keyword_audit.json", "w") as f:
    json.dump(output, f, indent=2)

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)

if total_location > 0:
    print(f"""
⚠️  FOUND {total_location} LOCATION-BASED KEYWORDS

This means you ARE using state/city-specific keywords like:
- "scissor lift rental Texas"
- "forklift Houston"

ACTION REQUIRED: You will need to create similar keywords for the new states:
- NJ, MD, CO, MS, UT, NV, NM, MT, MO, WI, LA, ME, WA, IN, KS
""")
else:
    print(f"""
✓  NO LOCATION-BASED KEYWORDS FOUND

Your campaigns use generic equipment keywords like:
- "scissor lift rental"
- "forklift for rent"
- "boom lift near me"

These keywords work with any geo-target. The "near me" keywords ({total_near_me} found)
are handled by Google based on user location, not keyword text.

ACTION: Simply add the new states as geo-targets. No new keywords needed.
""")

print("\nDetailed data saved to: dozr_keyword_audit.json")
