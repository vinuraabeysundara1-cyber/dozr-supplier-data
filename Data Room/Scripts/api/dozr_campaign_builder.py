#!/usr/bin/env python3
"""
DOZR Google Ads Campaign Builder - Geo Expansion
Based on Geo-Targeting Gap Analysis Report

This script will:
1. Fetch existing campaign structure (keywords, ads, extensions)
2. Add new state geo-targets to existing campaigns (PAUSED)
3. Verify all components before going live
"""

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import json
from datetime import datetime

# Initialize
client = GoogleAdsClient.load_from_storage("/Users/vinuraabeysundara/google-ads.yaml")
customer_id = "8531896842"
ga_service = client.get_service("GoogleAdsService")
geo_service = client.get_service("GeoTargetConstantService")

print("=" * 80)
print("DOZR GOOGLE ADS CAMPAIGN BUILDER - GEO EXPANSION")
print("=" * 80)
print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Customer ID: {customer_id}")
print()

# States to add (from gap analysis)
NEW_STATES = {
    "NJ": {"name": "New Jersey", "orders": 6, "suppliers": 3, "priority": "HIGH"},
    "MD": {"name": "Maryland", "orders": 2, "suppliers": 3, "priority": "HIGH"},
    "CO": {"name": "Colorado", "orders": 3, "suppliers": 1, "priority": "HIGH"},
    "MS": {"name": "Mississippi", "orders": 4, "suppliers": 0, "priority": "MEDIUM"},
    "UT": {"name": "Utah", "orders": 2, "suppliers": 0, "priority": "MEDIUM"},
    "NV": {"name": "Nevada", "orders": 2, "suppliers": 1, "priority": "MEDIUM"},
    "NM": {"name": "New Mexico", "orders": 2, "suppliers": 0, "priority": "MEDIUM"},
    "MT": {"name": "Montana", "orders": 2, "suppliers": 1, "priority": "MEDIUM"},
    "MO": {"name": "Missouri", "orders": 2, "suppliers": 2, "priority": "MEDIUM"},
    "WI": {"name": "Wisconsin", "orders": 1, "suppliers": 1, "priority": "LOW"},
    "LA": {"name": "Louisiana", "orders": 1, "suppliers": 0, "priority": "LOW"},
    "ME": {"name": "Maine", "orders": 1, "suppliers": 2, "priority": "LOW"},
    "WA": {"name": "Washington", "orders": 1, "suppliers": 1, "priority": "LOW"},
    "IN": {"name": "Indiana", "orders": 1, "suppliers": 1, "priority": "LOW"},
    "KS": {"name": "Kansas", "orders": 1, "suppliers": 1, "priority": "LOW"},
    "MA": {"name": "Massachusetts", "orders": 0, "suppliers": 2, "priority": "TEST"},
    "DE": {"name": "Delaware", "orders": 0, "suppliers": 1, "priority": "TEST"},
}

# Target campaigns to expand (US equipment campaigns)
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

# ============================================================================
# SECTION 1: FETCH EXISTING CAMPAIGNS & STRUCTURE
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 1: CURRENT CAMPAIGN STRUCTURE")
print("=" * 80)

campaign_query = """
    SELECT
        campaign.id,
        campaign.name,
        campaign.status,
        campaign.advertising_channel_type,
        campaign.bidding_strategy_type,
        campaign_budget.amount_micros
    FROM campaign
    WHERE campaign.status != 'REMOVED'
    AND campaign.advertising_channel_type = 'SEARCH'
    ORDER BY campaign.name
"""

campaigns_data = {}
try:
    response = ga_service.search(customer_id=customer_id, query=campaign_query)
    print("\nExisting Search Campaigns:")
    print("-" * 80)
    for row in response:
        camp_name = row.campaign.name
        camp_id = row.campaign.id
        status = str(row.campaign.status).split(".")[-1]
        budget = row.campaign_budget.amount_micros / 1_000_000 if row.campaign_budget.amount_micros else 0
        bidding = str(row.campaign.bidding_strategy_type).split(".")[-1]

        campaigns_data[camp_name] = {
            "id": camp_id,
            "status": status,
            "budget": budget,
            "bidding": bidding
        }

        # Mark target campaigns
        is_target = ">>> TARGET" if camp_name in TARGET_CAMPAIGNS else ""
        print(f"  {camp_name}")
        print(f"    ID: {camp_id} | Status: {status} | Budget: ${budget:.2f}/day | {is_target}")

except GoogleAdsException as ex:
    print(f"Error fetching campaigns: {ex.failure.errors[0].message}")

# ============================================================================
# SECTION 2: FETCH KEYWORDS FROM TARGET CAMPAIGNS
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 2: KEYWORDS BY CAMPAIGN")
print("=" * 80)

keywords_data = {}

for camp_name in TARGET_CAMPAIGNS:
    if camp_name not in campaigns_data:
        print(f"\n{camp_name}: NOT FOUND")
        continue

    camp_id = campaigns_data[camp_name]["id"]

    keyword_query = f"""
        SELECT
            ad_group.name,
            ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type,
            ad_group_criterion.status
        FROM keyword_view
        WHERE campaign.id = {camp_id}
        AND ad_group_criterion.status != 'REMOVED'
        LIMIT 50
    """

    try:
        response = ga_service.search(customer_id=customer_id, query=keyword_query)
        keywords = []
        for row in response:
            keywords.append({
                "ad_group": row.ad_group.name,
                "keyword": row.ad_group_criterion.keyword.text,
                "match_type": str(row.ad_group_criterion.keyword.match_type).split(".")[-1],
                "status": str(row.ad_group_criterion.status).split(".")[-1]
            })

        keywords_data[camp_name] = keywords
        print(f"\n{camp_name}: {len(keywords)} keywords")

        # Show sample keywords
        for kw in keywords[:5]:
            print(f"    [{kw['match_type'][:5]}] {kw['keyword']} ({kw['ad_group']})")
        if len(keywords) > 5:
            print(f"    ... and {len(keywords) - 5} more")

    except GoogleAdsException as ex:
        print(f"\n{camp_name}: Error - {ex.failure.errors[0].message}")

# ============================================================================
# SECTION 3: FETCH ADS (HEADLINES & DESCRIPTIONS)
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 3: ADS - HEADLINES & DESCRIPTIONS")
print("=" * 80)

ads_data = {}

for camp_name in TARGET_CAMPAIGNS:
    if camp_name not in campaigns_data:
        continue

    camp_id = campaigns_data[camp_name]["id"]

    ad_query = f"""
        SELECT
            ad_group.name,
            ad_group_ad.ad.id,
            ad_group_ad.ad.responsive_search_ad.headlines,
            ad_group_ad.ad.responsive_search_ad.descriptions,
            ad_group_ad.ad.final_urls,
            ad_group_ad.status
        FROM ad_group_ad
        WHERE campaign.id = {camp_id}
        AND ad_group_ad.ad.type = 'RESPONSIVE_SEARCH_AD'
        AND ad_group_ad.status != 'REMOVED'
    """

    try:
        response = ga_service.search(customer_id=customer_id, query=ad_query)
        ads = []
        for row in response:
            headlines = [h.text for h in row.ad_group_ad.ad.responsive_search_ad.headlines]
            descriptions = [d.text for d in row.ad_group_ad.ad.responsive_search_ad.descriptions]
            final_urls = list(row.ad_group_ad.ad.final_urls)

            ads.append({
                "ad_group": row.ad_group.name,
                "ad_id": row.ad_group_ad.ad.id,
                "headlines": headlines,
                "descriptions": descriptions,
                "final_urls": final_urls,
                "status": str(row.ad_group_ad.status).split(".")[-1]
            })

        ads_data[camp_name] = ads
        print(f"\n{camp_name}: {len(ads)} RSAs")

        # Show sample ad
        if ads:
            ad = ads[0]
            print(f"  Sample Ad from '{ad['ad_group']}':")
            print(f"    Headlines ({len(ad['headlines'])}):")
            for h in ad['headlines'][:3]:
                print(f"      - {h}")
            print(f"    Descriptions ({len(ad['descriptions'])}):")
            for d in ad['descriptions'][:2]:
                print(f"      - {d[:60]}...")
            print(f"    Final URL: {ad['final_urls'][0] if ad['final_urls'] else 'N/A'}")

    except GoogleAdsException as ex:
        print(f"\n{camp_name}: Error - {ex.failure.errors[0].message}")

# ============================================================================
# SECTION 4: FETCH CURRENT GEO-TARGETING
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 4: CURRENT GEO-TARGETING")
print("=" * 80)

geo_data = {}

for camp_name in TARGET_CAMPAIGNS:
    if camp_name not in campaigns_data:
        continue

    camp_id = campaigns_data[camp_name]["id"]

    geo_query = f"""
        SELECT
            campaign_criterion.location.geo_target_constant,
            campaign_criterion.bid_modifier
        FROM campaign_criterion
        WHERE campaign.id = {camp_id}
        AND campaign_criterion.type = 'LOCATION'
    """

    try:
        response = ga_service.search(customer_id=customer_id, query=geo_query)
        geos = []
        for row in response:
            geos.append({
                "geo_constant": row.campaign_criterion.location.geo_target_constant,
                "bid_modifier": row.campaign_criterion.bid_modifier
            })

        geo_data[camp_name] = geos
        print(f"\n{camp_name}: {len(geos)} geo targets")

    except GoogleAdsException as ex:
        print(f"\n{camp_name}: Error - {ex.failure.errors[0].message}")

# ============================================================================
# SECTION 5: LOOKUP GEO TARGET CONSTANTS FOR NEW STATES
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 5: GEO TARGET CONSTANTS FOR NEW STATES")
print("=" * 80)

state_geo_ids = {}

for state_code, info in NEW_STATES.items():
    state_name = info["name"]

    # Search for the state geo target
    suggest_query = f"{state_name}, United States"

    try:
        request = client.get_type("SuggestGeoTargetConstantsRequest")
        request.locale = "en"
        request.country_code = "US"
        request.location_names.names.append(suggest_query)

        response = geo_service.suggest_geo_target_constants(request=request)

        for suggestion in response.geo_target_constant_suggestions:
            geo = suggestion.geo_target_constant
            target_type = str(geo.target_type).split(".")[-1]

            # We want STATE type
            if target_type == "STATE":
                state_geo_ids[state_code] = {
                    "id": geo.id,
                    "name": geo.name,
                    "canonical_name": geo.canonical_name,
                    "resource_name": geo.resource_name,
                    "target_type": target_type
                }
                print(f"  {state_code}: {geo.name} (ID: {geo.id})")
                break

    except GoogleAdsException as ex:
        print(f"  {state_code}: Error - {ex.failure.errors[0].message}")

# ============================================================================
# SECTION 6: CONVERSION TRACKING VERIFICATION
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 6: CONVERSION TRACKING")
print("=" * 80)

conversion_query = """
    SELECT
        conversion_action.id,
        conversion_action.name,
        conversion_action.type,
        conversion_action.status,
        conversion_action.primary_for_goal
    FROM conversion_action
    WHERE conversion_action.status = 'ENABLED'
"""

conversions = []
try:
    response = ga_service.search(customer_id=customer_id, query=conversion_query)
    print("\nActive Conversion Actions:")
    for row in response:
        conv_type = str(row.conversion_action.type).split(".")[-1]
        is_primary = "PRIMARY" if row.conversion_action.primary_for_goal else ""
        conversions.append({
            "id": row.conversion_action.id,
            "name": row.conversion_action.name,
            "type": conv_type,
            "primary": row.conversion_action.primary_for_goal
        })
        print(f"  - {row.conversion_action.name} ({conv_type}) {is_primary}")

except GoogleAdsException as ex:
    print(f"Error: {ex.failure.errors[0].message}")

# ============================================================================
# SECTION 7: CALL EXTENSIONS VERIFICATION
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 7: CALL EXTENSIONS")
print("=" * 80)

call_query = """
    SELECT
        asset.id,
        asset.name,
        asset.call_asset.phone_number,
        asset.call_asset.country_code
    FROM asset
    WHERE asset.type = 'CALL'
"""

try:
    response = ga_service.search(customer_id=customer_id, query=call_query)
    print("\nCall Assets:")
    for row in response:
        phone = row.asset.call_asset.phone_number
        country = row.asset.call_asset.country_code
        print(f"  - {country} {phone}")

except GoogleAdsException as ex:
    print(f"Error: {ex.failure.errors[0].message}")

# ============================================================================
# SECTION 8: SITELINK EXTENSIONS
# ============================================================================
print("\n" + "=" * 80)
print("SECTION 8: SITELINK EXTENSIONS")
print("=" * 80)

sitelink_query = """
    SELECT
        asset.id,
        asset.sitelink_asset.link_text,
        asset.sitelink_asset.description1,
        asset.sitelink_asset.description2,
        asset.final_urls
    FROM asset
    WHERE asset.type = 'SITELINK'
    LIMIT 10
"""

try:
    response = ga_service.search(customer_id=customer_id, query=sitelink_query)
    print("\nSitelink Assets (Sample):")
    for row in response:
        link_text = row.asset.sitelink_asset.link_text
        desc1 = row.asset.sitelink_asset.description1
        final_url = list(row.asset.final_urls)[0] if row.asset.final_urls else "N/A"
        print(f"  - {link_text}")
        print(f"    Desc: {desc1}")
        print(f"    URL: {final_url}")

except GoogleAdsException as ex:
    print(f"Error: {ex.failure.errors[0].message}")

# ============================================================================
# SAVE ALL DATA FOR REVIEW
# ============================================================================
print("\n" + "=" * 80)
print("SAVING DATA FOR REVIEW")
print("=" * 80)

output_data = {
    "generated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    "customer_id": customer_id,
    "new_states_to_add": NEW_STATES,
    "state_geo_ids": state_geo_ids,
    "target_campaigns": TARGET_CAMPAIGNS,
    "campaigns": campaigns_data,
    "keywords_sample": {k: v[:10] for k, v in keywords_data.items()},
    "ads_sample": {k: v[:2] for k, v in ads_data.items()},
    "current_geo_targets": geo_data,
    "conversions": conversions
}

with open("/Users/vinuraabeysundara/dozr_campaign_expansion_data.json", "w") as f:
    json.dump(output_data, f, indent=2, default=str)
print("Saved to: dozr_campaign_expansion_data.json")

print("\n" + "=" * 80)
print("NEXT STEP: Run dozr_add_geo_targets.py to add new states (PAUSED)")
print("=" * 80)
