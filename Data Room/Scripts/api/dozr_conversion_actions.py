#!/usr/bin/env python3
"""
DOZR Google Ads - Full Conversion Action Technical Details
Pulls every available field for all conversion actions.
"""

import warnings
warnings.filterwarnings("ignore")

from google.ads.googleads.client import GoogleAdsClient
from collections import defaultdict
import sys

CONFIG_PATH = "/Users/vinuraabeysundara/google-ads.yaml"
CUSTOMER_ID = "8531896842"
OUTPUT_FILE = "/Users/vinuraabeysundara/dozr_conversion_actions_report.txt"

def enum_name(client, enum_path, value):
    """Convert a protobuf enum int to its human-readable name (short form)."""
    try:
        enum_type = client.enums.__getattr__(enum_path)
        full = enum_type(value).name
        return full
    except Exception:
        # If the value itself is already an enum object with .name, extract short name
        s = str(value)
        if "." in s:
            return s.rsplit(".", 1)[-1]
        return s

class Tee:
    """Write to both stdout and a file."""
    def __init__(self, filename):
        self.file = open(filename, "w")
        self.stdout = sys.stdout
    def write(self, data):
        self.stdout.write(data)
        self.file.write(data)
    def flush(self):
        self.stdout.flush()
        self.file.flush()
    def close(self):
        self.file.close()

def main():
    tee = Tee(OUTPUT_FILE)
    sys.stdout = tee

    client = GoogleAdsClient.load_from_storage(CONFIG_PATH, version="v23")
    ga_service = client.get_service("GoogleAdsService")

    query_all = """
        SELECT
          conversion_action.id,
          conversion_action.name,
          conversion_action.type,
          conversion_action.category,
          conversion_action.status,
          conversion_action.tag_snippets,
          conversion_action.origin,
          conversion_action.primary_for_goal,
          conversion_action.counting_type,
          conversion_action.attribution_model_settings.attribution_model,
          conversion_action.attribution_model_settings.data_driven_model_status,
          conversion_action.value_settings.default_value,
          conversion_action.value_settings.always_use_default_value,
          conversion_action.click_through_lookback_window_days,
          conversion_action.view_through_lookback_window_days,
          conversion_action.include_in_conversions_metric,
          conversion_action.phone_call_duration_seconds,
          conversion_action.app_id
        FROM conversion_action
        ORDER BY conversion_action.status
    """

    print("=" * 100)
    print("  DOZR GOOGLE ADS — FULL CONVERSION ACTION TECHNICAL AUDIT")
    print("  Customer ID: {}".format(CUSTOMER_ID))
    print("=" * 100)

    response = ga_service.search(customer_id=CUSTOMER_ID, query=query_all)

    actions = []
    for row in response:
        ca = row.conversion_action
        actions.append(ca)

    if not actions:
        print("\nNo conversion actions found.")
        return

    # Group by type
    grouped = defaultdict(list)
    for ca in actions:
        type_name = enum_name(client, "ConversionActionTypeEnum.ConversionActionType", ca.type_)
        grouped[type_name].append(ca)

    # Summary counts
    print("\n{:<50} {:>5}".format("CONVERSION ACTION TYPE", "COUNT"))
    print("-" * 57)
    for t in sorted(grouped.keys()):
        print("{:<50} {:>5}".format(t, len(grouped[t])))
    print("-" * 57)
    print("{:<50} {:>5}".format("TOTAL", len(actions)))

    # Detailed listing grouped by type
    for type_name in sorted(grouped.keys()):
        cas = grouped[type_name]
        print("\n\n")
        print("#" * 100)
        print("##  TYPE: {}  ({} conversion action{})".format(
            type_name, len(cas), "s" if len(cas) != 1 else ""))
        print("#" * 100)

        # Type explanation at the group level
        type_explanations = {
            "UPLOAD_CLICKS": "Offline conversion upload via GCLID matching — conversions happen offline and are uploaded back to Google Ads",
            "WEBPAGE": "Google Ads tag or GTM tag firing on a webpage — tracks when a user visits a specific page or triggers an event",
            "PHONE_CALL": "Google forwarding number call tracking — uses a Google forwarding number on your website",
            "GOOGLE_ANALYTICS_4_CUSTOM": "Imported from GA4 (custom event) — a GA4 event imported into Google Ads as a conversion",
            "GOOGLE_ANALYTICS_4_PURCHASE": "Imported from GA4 (purchase event) — GA4 purchase/ecommerce event imported into Google Ads",
            "AD_CALL": "Calls from ads — tracks calls made directly from call extensions or call-only ads",
            "CLICK_TO_CALL": "Click-to-call — tracks when someone clicks a phone number on mobile",
            "WEBSITE_CALL": "Website call — tracks calls from a Google forwarding number displayed on your website",
            "STORE_VISIT": "Store visit conversion (Google-modeled)",
            "FIREBASE": "Firebase app conversion",
            "FLOODLIGHT_ACTION": "Floodlight action tag (CM360)",
            "FLOODLIGHT_TRANSACTION": "Floodlight transaction tag (CM360)",
            "UPLOAD_CALLS": "Offline call conversion upload",
        }
        explanation = type_explanations.get(type_name, "")
        if explanation:
            print("\n  HOW IT WORKS: {}".format(explanation))

        for idx, ca in enumerate(cas, 1):
            status_name = enum_name(client, "ConversionActionStatusEnum.ConversionActionStatus", ca.status)
            category_name = enum_name(client, "ConversionActionCategoryEnum.ConversionActionCategory", ca.category)
            origin_name = enum_name(client, "ConversionOriginEnum.ConversionOrigin", ca.origin)
            counting_name = enum_name(client, "ConversionActionCountingTypeEnum.ConversionActionCountingType", ca.counting_type)
            attribution_model_name = enum_name(client, "AttributionModelEnum.AttributionModel", ca.attribution_model_settings.attribution_model)
            dd_status_name = enum_name(client, "DataDrivenModelStatusEnum.DataDrivenModelStatus", ca.attribution_model_settings.data_driven_model_status)

            print("\n" + "-" * 100)
            print("  [{}/{}]  {}".format(idx, len(cas), ca.name))
            print("-" * 100)

            print("  {:<44} {}".format("ID:", ca.id))
            print("  {:<44} {}".format("Name:", ca.name))
            print("  {:<44} {}".format("Type:", type_name))
            print("  {:<44} {}".format("Origin:", origin_name))

            origin_explanations = {
                "GOOGLE_ADS": "Created natively in Google Ads",
                "GOOGLE_ANALYTICS_4_LINKED": "Imported/linked from GA4 property",
                "FLOODLIGHT": "Imported from Campaign Manager 360",
                "SEARCH_ADS_360": "Imported from Search Ads 360",
                "FIREBASE_LINKED": "Imported from Firebase",
                "SALESFORCE": "Imported from Salesforce",
                "CALL_FROM_ADS": "Auto-created by Google Ads for call extensions",
                "WEBSITE": "Created for website-based tracking",
            }
            origin_exp = origin_explanations.get(origin_name, "")
            if origin_exp:
                print("  {:<44} {}".format("  -> Meaning:", origin_exp))

            print("  {:<44} {}".format("Category:", category_name))
            print("  {:<44} {}".format("Status:", status_name))
            print("  {:<44} {}".format("Primary for Goal:", ca.primary_for_goal))
            print("  {:<44} {}".format("Include in 'Conversions' Metric:", ca.include_in_conversions_metric))
            print("  {:<44} {}".format("Counting Type:", counting_name))
            print("  {:<44} {}".format("Attribution Model:", attribution_model_name))
            print("  {:<44} {}".format("Data-Driven Model Status:", dd_status_name))
            print("  {:<44} {} days".format("Click-Through Lookback Window:", ca.click_through_lookback_window_days))
            print("  {:<44} {} days".format("View-Through Lookback Window:", ca.view_through_lookback_window_days))

            # Value settings
            vs = ca.value_settings
            print("  {:<44} {}".format("Default Conversion Value:", vs.default_value))
            print("  {:<44} {}".format("Always Use Default Value:", vs.always_use_default_value))

            # Phone call duration
            if ca.phone_call_duration_seconds:
                print("  {:<44} {} seconds".format("Phone Call Duration Threshold:", ca.phone_call_duration_seconds))
            else:
                print("  {:<44} N/A".format("Phone Call Duration Threshold:"))

            # App ID
            if ca.app_id:
                print("  {:<44} {}".format("App ID:", ca.app_id))

            # Tag snippets
            if ca.tag_snippets:
                print("\n  TAG SNIPPETS:")
                for si, snippet in enumerate(ca.tag_snippets):
                    tag_type = enum_name(client, "TrackingCodeTypeEnum.TrackingCodeType", snippet.type_)
                    page_fmt = enum_name(client, "TrackingCodePageFormatEnum.TrackingCodePageFormat", snippet.page_format)
                    print("    --- Snippet {} ---".format(si + 1))
                    print("    Tag Type:    {}".format(tag_type))
                    print("    Page Format: {}".format(page_fmt))
                    if snippet.global_site_tag:
                        gst = snippet.global_site_tag.strip()
                        if len(gst) > 400:
                            print("    Global Site Tag (truncated):")
                            for line in gst[:400].split("\n"):
                                print("      {}".format(line))
                            print("      ...")
                        else:
                            print("    Global Site Tag:")
                            for line in gst.split("\n"):
                                print("      {}".format(line))
                    if snippet.event_snippet:
                        es = snippet.event_snippet.strip()
                        if len(es) > 600:
                            print("    Event Snippet (truncated):")
                            for line in es[:600].split("\n"):
                                print("      {}".format(line))
                            print("      ...")
                        else:
                            print("    Event Snippet:")
                            for line in es.split("\n"):
                                print("      {}".format(line))
                    print()
            else:
                print("  {:<44} (none)".format("Tag Snippets:"))

    # ----------------------------------------------------------------
    # Query 2 – Specifically GA4-linked conversion actions
    # ----------------------------------------------------------------
    query_ga4 = """
        SELECT
          conversion_action.id,
          conversion_action.name,
          conversion_action.type,
          conversion_action.origin
        FROM conversion_action
        WHERE conversion_action.type IN ('GOOGLE_ANALYTICS_4_CUSTOM', 'GOOGLE_ANALYTICS_4_PURCHASE')
    """

    print("\n\n")
    print("=" * 100)
    print("  GA4-LINKED CONVERSION ACTIONS (Filtered Query)")
    print("=" * 100)

    response_ga4 = ga_service.search(customer_id=CUSTOMER_ID, query=query_ga4)

    ga4_actions = []
    for row in response_ga4:
        ga4_actions.append(row.conversion_action)

    if not ga4_actions:
        print("\n  No GA4-linked conversion actions found in this account.")
    else:
        print("\n  Found {} GA4-linked conversion action(s):\n".format(len(ga4_actions)))
        for idx, ca in enumerate(ga4_actions, 1):
            type_name = enum_name(client, "ConversionActionTypeEnum.ConversionActionType", ca.type_)
            origin_name = enum_name(client, "ConversionOriginEnum.ConversionOrigin", ca.origin)
            print("  {}. {} (ID: {})".format(idx, ca.name, ca.id))
            print("     Type:   {}".format(type_name))
            print("     Origin: {}".format(origin_name))
            print()

    # ----------------------------------------------------------------
    # Summary: Conversions included in the "Conversions" column
    # ----------------------------------------------------------------
    print("\n")
    print("=" * 100)
    print("  SUMMARY: ACTIONS INCLUDED IN 'CONVERSIONS' BIDDING COLUMN")
    print("=" * 100)

    enabled_actions = [ca for ca in actions
                       if enum_name(client, "ConversionActionStatusEnum.ConversionActionStatus", ca.status) == "ENABLED"]

    included = [ca for ca in enabled_actions if ca.include_in_conversions_metric]
    not_included = [ca for ca in enabled_actions if not ca.include_in_conversions_metric]

    print("\n  INCLUDED in Conversions column (these drive bidding) - {} actions:\n".format(len(included)))
    for ca in included:
        type_name = enum_name(client, "ConversionActionTypeEnum.ConversionActionType", ca.type_)
        primary = "PRIMARY" if ca.primary_for_goal else "secondary"
        print("    [{:<9}] [{:<35}] {} (ID: {})".format(
            primary, type_name, ca.name, ca.id))

    print("\n  NOT INCLUDED (observe only, do not drive bidding) - {} actions:\n".format(len(not_included)))
    for ca in not_included:
        type_name = enum_name(client, "ConversionActionTypeEnum.ConversionActionType", ca.type_)
        primary = "PRIMARY" if ca.primary_for_goal else "secondary"
        print("    [{:<9}] [{:<35}] {} (ID: {})".format(
            primary, type_name, ca.name, ca.id))

    # Show removed/hidden
    removed_actions = [ca for ca in actions
                       if enum_name(client, "ConversionActionStatusEnum.ConversionActionStatus", ca.status) in ("REMOVED", "HIDDEN")]
    if removed_actions:
        print("\n  REMOVED/HIDDEN - {} actions:\n".format(len(removed_actions)))
        for ca in removed_actions:
            status_name = enum_name(client, "ConversionActionStatusEnum.ConversionActionStatus", ca.status)
            type_name = enum_name(client, "ConversionActionTypeEnum.ConversionActionType", ca.type_)
            print("    [{}] [{}] {} (ID: {})".format(
                status_name, type_name, ca.name, ca.id))

    # ----------------------------------------------------------------
    # Summary: Primary vs Secondary goals
    # ----------------------------------------------------------------
    print("\n")
    print("=" * 100)
    print("  SUMMARY: PRIMARY vs SECONDARY GOAL ACTIONS (ENABLED ONLY)")
    print("=" * 100)

    primary_actions = [ca for ca in enabled_actions if ca.primary_for_goal]
    secondary_actions = [ca for ca in enabled_actions if not ca.primary_for_goal]

    print("\n  PRIMARY GOAL ACTIONS ({}) — these drive Smart Bidding:\n".format(len(primary_actions)))
    for ca in primary_actions:
        type_name = enum_name(client, "ConversionActionTypeEnum.ConversionActionType", ca.type_)
        incl = "IN conversions" if ca.include_in_conversions_metric else "NOT in conversions"
        print("    [{}] [{}] {} (ID: {})".format(type_name, incl, ca.name, ca.id))

    print("\n  SECONDARY GOAL ACTIONS ({}) — observation only:\n".format(len(secondary_actions)))
    for ca in secondary_actions:
        type_name = enum_name(client, "ConversionActionTypeEnum.ConversionActionType", ca.type_)
        incl = "IN conversions" if ca.include_in_conversions_metric else "NOT in conversions"
        print("    [{}] [{}] {} (ID: {})".format(type_name, incl, ca.name, ca.id))

    print("\n" + "=" * 100)
    print("  REPORT SAVED TO: {}".format(OUTPUT_FILE))
    print("  END OF REPORT")
    print("=" * 100)

    sys.stdout = tee.stdout
    tee.close()

if __name__ == "__main__":
    main()
