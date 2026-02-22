#!/usr/bin/env python3
"""
Pull ad schedule (dayparting) criteria for ALL campaigns in the DOZR Google Ads account.
Groups output by campaign, sorts by day of week (Monday first), and highlights
campaigns with no ad schedule (running 24/7).
"""

from google.ads.googleads.client import GoogleAdsClient
from collections import defaultdict

# -- Configuration -----------------------------------------------------------
CONFIG_PATH = "/Users/vinuraabeysundara/google-ads.yaml"
CUSTOMER_ID = "8531896842"

# Day-of-week sort order (Monday = 1 ... Sunday = 7)
DAY_ORDER = {
    "MONDAY": 1,
    "TUESDAY": 2,
    "WEDNESDAY": 3,
    "THURSDAY": 4,
    "FRIDAY": 5,
    "SATURDAY": 6,
    "SUNDAY": 7,
    "UNSPECIFIED": 99,
    "UNKNOWN": 99,
}

# MinuteOfHour enum name -> display string
MINUTE_MAP = {
    "ZERO": "00",
    "FIFTEEN": "15",
    "THIRTY": "30",
    "FORTY_FIVE": "45",
}


def fmt_minute(val):
    """Convert a MinuteOfHour enum (or its .name string) to a two-digit display."""
    name = val.name if hasattr(val, "name") else str(val)
    return MINUTE_MAP.get(name, "00")


def fmt_time(hour, minute_enum):
    return f"{hour:02d}:{fmt_minute(minute_enum)}"


def main():
    # -- Auth & client -------------------------------------------------------
    client = GoogleAdsClient.load_from_storage(path=CONFIG_PATH, version="v23")
    ga_service = client.get_service("GoogleAdsService")

    # -- Query: ad-schedule criteria for ENABLED campaigns -------------------
    query_ad_schedule = """
        SELECT
          campaign.name,
          campaign.status,
          campaign_criterion.criterion_id,
          campaign_criterion.ad_schedule.day_of_week,
          campaign_criterion.ad_schedule.start_hour,
          campaign_criterion.ad_schedule.start_minute,
          campaign_criterion.ad_schedule.end_hour,
          campaign_criterion.ad_schedule.end_minute,
          campaign_criterion.bid_modifier
        FROM campaign_criterion
        WHERE campaign_criterion.type = 'AD_SCHEDULE'
          AND campaign.status = 'ENABLED'
        ORDER BY campaign.name
    """

    # -- Query: ALL enabled campaigns (to find those WITHOUT schedules) ------
    query_all_campaigns = """
        SELECT campaign.name
        FROM campaign
        WHERE campaign.status = 'ENABLED'
        ORDER BY campaign.name
    """

    # -- Fetch all enabled campaign names ------------------------------------
    all_campaigns = set()
    response_all = ga_service.search(customer_id=CUSTOMER_ID, query=query_all_campaigns)
    for row in response_all:
        all_campaigns.add(row.campaign.name)

    # -- Fetch ad-schedule criteria ------------------------------------------
    schedules = defaultdict(list)
    response = ga_service.search(customer_id=CUSTOMER_ID, query=query_ad_schedule)

    for row in response:
        campaign_name = row.campaign.name
        sched = row.campaign_criterion.ad_schedule
        day_enum = sched.day_of_week
        day_name = day_enum.name if hasattr(day_enum, "name") else str(day_enum)

        schedules[campaign_name].append({
            "day": day_name,
            "start_hour": sched.start_hour,
            "start_minute": sched.start_minute,
            "end_hour": sched.end_hour,
            "end_minute": sched.end_minute,
            "bid_modifier": row.campaign_criterion.bid_modifier,
        })

    # -- Campaigns with NO ad schedule ---------------------------------------
    campaigns_without_schedule = sorted(all_campaigns - set(schedules.keys()))

    # -- Sort each campaign's schedule by day order, then start time ----------
    for name in schedules:
        schedules[name].sort(
            key=lambda s: (DAY_ORDER.get(s["day"], 99), s["start_hour"])
        )

    # -- Print results -------------------------------------------------------
    divider = "=" * 90
    thin_divider = "-" * 90

    print()
    print(divider)
    print("  DOZR GOOGLE ADS -- AD SCHEDULE (DAYPARTING) REPORT")
    print(f"  Customer ID: {CUSTOMER_ID}")
    print(divider)

    # -- Campaigns WITH schedules --------------------------------------------
    for campaign_name in sorted(schedules.keys()):
        entries = schedules[campaign_name]
        print(f"\n  CAMPAIGN: {campaign_name}")
        print(thin_divider)
        print(f"  {'Day':<14} {'Start':>7}  {'End':>7}  {'Bid Modifier':>14}")
        print(f"  {'---':<14} {'-----':>7}  {'---':>7}  {'------------':>14}")
        for e in entries:
            start = fmt_time(e["start_hour"], e["start_minute"])
            end = fmt_time(e["end_hour"], e["end_minute"])
            bm = e["bid_modifier"]
            bm_str = f"{bm:.2f}" if bm and bm != 0.0 else "---"
            print(f"  {e['day']:<14} {start:>7}  {end:>7}  {bm_str:>14}")
        print()

    # -- Campaigns WITHOUT schedules -----------------------------------------
    if campaigns_without_schedule:
        print(divider)
        print("  CAMPAIGNS WITH NO AD SCHEDULE (running 24/7, all days)")
        print(divider)
        for name in campaigns_without_schedule:
            tag = ""
            if "backhoe" in name.lower():
                tag = "  <<<  NOTE: No schedule -- runs on weekends too"
            print(f"    - {name}{tag}")
        print()

    # -- Summary -------------------------------------------------------------
    print(thin_divider)
    print(f"  Total enabled campaigns:              {len(all_campaigns)}")
    print(f"  Campaigns WITH ad schedule:            {len(schedules)}")
    print(f"  Campaigns WITHOUT ad schedule (24/7):  {len(campaigns_without_schedule)}")
    print(thin_divider)
    print()


if __name__ == "__main__":
    main()
