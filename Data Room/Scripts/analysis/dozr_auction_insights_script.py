#!/usr/bin/env python3
"""
DOZR Auction Insights Analysis - Weekend vs Weekday Competitive Landscape
==========================================================================

Pulls impression share and competitive metrics from the Google Ads API,
segmented by day of week, to understand competitive dynamics on weekends
vs weekdays.

NOTE: The auction_insight competitor-domain metrics (segments.auction_insight_domain)
require Standard-level API access. This script uses the available campaign-level
competitive metrics which provide impression share, lost IS (rank & budget),
top impression share, and absolute top impression share -- all segmented by
day of week.

These metrics still reveal competitive pressure patterns:
- Low impression share + high lost IS (rank) = strong competitor presence
- Weekend impression share changes = competitors scaling up/down on weekends
- Top/Abs-top IS changes = competitors changing bidding aggressiveness
"""

import warnings
warnings.filterwarnings("ignore")

import json
import sys
from datetime import datetime, timedelta
from collections import defaultdict

from google.ads.googleads.client import GoogleAdsClient

# Configuration
CONFIG_PATH = "/Users/vinuraabeysundara/google-ads.yaml"
CUSTOMER_ID = "8531896842"
OUTPUT_PATH = "/Users/vinuraabeysundara/dozr_auction_insights.json"

DAY_OF_WEEK_MAP = {
    0: "UNSPECIFIED", 1: "UNKNOWN",
    2: "MONDAY", 3: "TUESDAY", 4: "WEDNESDAY",
    5: "THURSDAY", 6: "FRIDAY", 7: "SATURDAY", 8: "SUNDAY",
}

WEEKDAY_NAMES = {"MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"}
WEEKEND_NAMES = {"SATURDAY", "SUNDAY"}
DAY_ORDER = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]


def pct(val):
    """Format a ratio as percentage string."""
    if val is None or val == 0:
        return "    N/A"
    return f"{val:>7.1%}"


def safe_avg(vals):
    """Average of non-zero values."""
    filtered = [v for v in vals if v is not None and v > 0]
    return round(sum(filtered) / len(filtered), 6) if filtered else 0.0


def main():
    print("=" * 80)
    print("  DOZR Competitive Landscape - Weekend vs Weekday Analysis")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # 1. Initialize
    # -------------------------------------------------------------------------
    print("\n[1/5] Initializing Google Ads API client...")
    client = GoogleAdsClient.load_from_storage(CONFIG_PATH)
    ga_service = client.get_service("GoogleAdsService")

    end_date = datetime.now() - timedelta(days=1)
    start_date = end_date - timedelta(days=90)
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    print(f"   Date range: {start_str} to {end_str} (90 days)")

    # -------------------------------------------------------------------------
    # 2. Pull campaign-level competitive metrics by day of week
    # -------------------------------------------------------------------------
    print("\n[2/5] Pulling campaign-level competitive metrics by day of week...")

    campaign_query = f"""
        SELECT
            campaign.id,
            campaign.name,
            segments.day_of_week,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.search_impression_share,
            metrics.search_rank_lost_impression_share,
            metrics.search_budget_lost_impression_share,
            metrics.search_top_impression_share,
            metrics.search_rank_lost_top_impression_share,
            metrics.search_budget_lost_top_impression_share,
            metrics.search_absolute_top_impression_share,
            metrics.search_rank_lost_absolute_top_impression_share,
            metrics.search_budget_lost_absolute_top_impression_share
        FROM campaign
        WHERE segments.date BETWEEN '{start_str}' AND '{end_str}'
            AND campaign.status = 'ENABLED'
            AND campaign.advertising_channel_type = 'SEARCH'
    """

    campaign_data = []
    row_count = 0
    response = ga_service.search_stream(customer_id=CUSTOMER_ID, query=campaign_query)
    for batch in response:
        for row in batch.results:
            row_count += 1
            day_name = DAY_OF_WEEK_MAP.get(row.segments.day_of_week, "UNKNOWN")
            campaign_data.append({
                "campaign_id": row.campaign.id,
                "campaign_name": row.campaign.name,
                "day_of_week": day_name,
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "cost": row.metrics.cost_micros / 1_000_000,
                "search_impression_share": row.metrics.search_impression_share,
                "search_rank_lost_is": row.metrics.search_rank_lost_impression_share,
                "search_budget_lost_is": row.metrics.search_budget_lost_impression_share,
                "search_top_is": row.metrics.search_top_impression_share,
                "search_rank_lost_top_is": row.metrics.search_rank_lost_top_impression_share,
                "search_budget_lost_top_is": row.metrics.search_budget_lost_top_impression_share,
                "search_abs_top_is": row.metrics.search_absolute_top_impression_share,
                "search_rank_lost_abs_top_is": row.metrics.search_rank_lost_absolute_top_impression_share,
                "search_budget_lost_abs_top_is": row.metrics.search_budget_lost_absolute_top_impression_share,
            })
    print(f"   Retrieved {row_count} campaign x day-of-week rows")
    unique_campaigns = set(r["campaign_name"] for r in campaign_data)
    print(f"   Active search campaigns: {len(unique_campaigns)}")

    # -------------------------------------------------------------------------
    # 3. Aggregate by day of week (account level)
    # -------------------------------------------------------------------------
    print("\n[3/5] Aggregating account-level metrics by day of week...")

    day_agg = defaultdict(lambda: {
        "impressions": 0, "clicks": 0, "cost": 0.0,
        "search_is_vals": [], "rank_lost_is_vals": [], "budget_lost_is_vals": [],
        "top_is_vals": [], "rank_lost_top_is_vals": [], "budget_lost_top_is_vals": [],
        "abs_top_is_vals": [], "rank_lost_abs_top_is_vals": [], "budget_lost_abs_top_is_vals": [],
    })

    for r in campaign_data:
        d = day_agg[r["day_of_week"]]
        d["impressions"] += r["impressions"]
        d["clicks"] += r["clicks"]
        d["cost"] += r["cost"]
        if r["search_impression_share"] and r["search_impression_share"] > 0:
            d["search_is_vals"].append(r["search_impression_share"])
        if r["search_rank_lost_is"] and r["search_rank_lost_is"] > 0:
            d["rank_lost_is_vals"].append(r["search_rank_lost_is"])
        if r["search_budget_lost_is"] and r["search_budget_lost_is"] > 0:
            d["budget_lost_is_vals"].append(r["search_budget_lost_is"])
        if r["search_top_is"] and r["search_top_is"] > 0:
            d["top_is_vals"].append(r["search_top_is"])
        if r["search_rank_lost_top_is"] and r["search_rank_lost_top_is"] > 0:
            d["rank_lost_top_is_vals"].append(r["search_rank_lost_top_is"])
        if r["search_budget_lost_top_is"] and r["search_budget_lost_top_is"] > 0:
            d["budget_lost_top_is_vals"].append(r["search_budget_lost_top_is"])
        if r["search_abs_top_is"] and r["search_abs_top_is"] > 0:
            d["abs_top_is_vals"].append(r["search_abs_top_is"])
        if r["search_rank_lost_abs_top_is"] and r["search_rank_lost_abs_top_is"] > 0:
            d["rank_lost_abs_top_is_vals"].append(r["search_rank_lost_abs_top_is"])
        if r["search_budget_lost_abs_top_is"] and r["search_budget_lost_abs_top_is"] > 0:
            d["budget_lost_abs_top_is_vals"].append(r["search_budget_lost_abs_top_is"])

    day_summary = {}
    for day in DAY_ORDER:
        d = day_agg[day]
        day_summary[day] = {
            "impressions": d["impressions"],
            "clicks": d["clicks"],
            "cost": round(d["cost"], 2),
            "avg_search_is": safe_avg(d["search_is_vals"]),
            "avg_rank_lost_is": safe_avg(d["rank_lost_is_vals"]),
            "avg_budget_lost_is": safe_avg(d["budget_lost_is_vals"]),
            "avg_top_is": safe_avg(d["top_is_vals"]),
            "avg_rank_lost_top_is": safe_avg(d["rank_lost_top_is_vals"]),
            "avg_budget_lost_top_is": safe_avg(d["budget_lost_top_is_vals"]),
            "avg_abs_top_is": safe_avg(d["abs_top_is_vals"]),
            "avg_rank_lost_abs_top_is": safe_avg(d["rank_lost_abs_top_is_vals"]),
            "avg_budget_lost_abs_top_is": safe_avg(d["budget_lost_abs_top_is_vals"]),
        }

    # -------------------------------------------------------------------------
    # 4. Campaign-level breakdown by day of week
    # -------------------------------------------------------------------------
    print("\n[4/5] Building per-campaign day-of-week breakdown...")

    camp_day_agg = defaultdict(lambda: defaultdict(lambda: {
        "impressions": 0, "clicks": 0, "cost": 0.0,
        "search_is_vals": [], "rank_lost_is_vals": [], "top_is_vals": [], "abs_top_is_vals": [],
    }))

    for r in campaign_data:
        cd = camp_day_agg[r["campaign_name"]][r["day_of_week"]]
        cd["impressions"] += r["impressions"]
        cd["clicks"] += r["clicks"]
        cd["cost"] += r["cost"]
        if r["search_impression_share"] and r["search_impression_share"] > 0:
            cd["search_is_vals"].append(r["search_impression_share"])
        if r["search_rank_lost_is"] and r["search_rank_lost_is"] > 0:
            cd["rank_lost_is_vals"].append(r["search_rank_lost_is"])
        if r["search_top_is"] and r["search_top_is"] > 0:
            cd["top_is_vals"].append(r["search_top_is"])
        if r["search_abs_top_is"] and r["search_abs_top_is"] > 0:
            cd["abs_top_is_vals"].append(r["search_abs_top_is"])

    camp_day_summary = {}
    for camp in camp_day_agg:
        camp_day_summary[camp] = {}
        for day in DAY_ORDER:
            cd = camp_day_agg[camp][day]
            camp_day_summary[camp][day] = {
                "impressions": cd["impressions"],
                "clicks": cd["clicks"],
                "cost": round(cd["cost"], 2),
                "avg_search_is": safe_avg(cd["search_is_vals"]),
                "avg_rank_lost_is": safe_avg(cd["rank_lost_is_vals"]),
                "avg_top_is": safe_avg(cd["top_is_vals"]),
                "avg_abs_top_is": safe_avg(cd["abs_top_is_vals"]),
            }

    # -------------------------------------------------------------------------
    # 5. Print Results
    # -------------------------------------------------------------------------
    print("\n[5/5] Generating report...\n")

    # --- Account-Level Day-of-Week Summary ---
    print("=" * 80)
    print("  ACCOUNT-LEVEL COMPETITIVE METRICS BY DAY OF WEEK")
    print("=" * 80)
    print()
    print("  Interpretation Guide:")
    print("  - Search IS: % of available impressions DOZR captured")
    print("  - Rank Lost IS: % lost due to Ad Rank (competitor outbidding/quality)")
    print("  - Budget Lost IS: % lost due to budget constraints")
    print("  - Top IS: % of impressions shown in top positions")
    print("  - Abs Top IS: % of impressions shown in position #1")
    print()

    header = f"  {'Day':<12} {'Impressions':>12} {'Cost':>10} {'Search IS':>10} {'Rank Lost':>10} {'Budget Lost':>11} {'Top IS':>10} {'AbsTop IS':>10}"
    print(header)
    print("  " + "-" * (len(header) - 2))

    for day in DAY_ORDER:
        ds = day_summary[day]
        marker = " <<" if day in WEEKEND_NAMES else ""
        print(
            f"  {day:<12}"
            f" {ds['impressions']:>12,}"
            f" ${ds['cost']:>9,.0f}"
            f" {pct(ds['avg_search_is'])}"
            f" {pct(ds['avg_rank_lost_is'])}"
            f" {pct(ds['avg_budget_lost_is']):>11}"
            f" {pct(ds['avg_top_is'])}"
            f" {pct(ds['avg_abs_top_is'])}"
            f"{marker}"
        )

    # Weekday vs Weekend comparison
    weekday_metrics = {k: [] for k in ["avg_search_is", "avg_rank_lost_is", "avg_budget_lost_is",
                                        "avg_top_is", "avg_abs_top_is", "impressions", "cost"]}
    weekend_metrics = {k: [] for k in weekday_metrics}

    for day in DAY_ORDER:
        target = weekend_metrics if day in WEEKEND_NAMES else weekday_metrics
        for k in target:
            target[k].append(day_summary[day][k])

    print()
    print("  " + "-" * 78)
    wk_is = safe_avg(weekday_metrics["avg_search_is"])
    we_is = safe_avg(weekend_metrics["avg_search_is"])
    wk_rank = safe_avg(weekday_metrics["avg_rank_lost_is"])
    we_rank = safe_avg(weekend_metrics["avg_rank_lost_is"])
    wk_budget = safe_avg(weekday_metrics["avg_budget_lost_is"])
    we_budget = safe_avg(weekend_metrics["avg_budget_lost_is"])
    wk_top = safe_avg(weekday_metrics["avg_top_is"])
    we_top = safe_avg(weekend_metrics["avg_top_is"])
    wk_abs = safe_avg(weekday_metrics["avg_abs_top_is"])
    we_abs = safe_avg(weekend_metrics["avg_abs_top_is"])
    wk_imp = sum(weekday_metrics["impressions"])
    we_imp = sum(weekend_metrics["impressions"])
    wk_cost = sum(weekday_metrics["cost"])
    we_cost = sum(weekend_metrics["cost"])

    print(f"  {'WEEKDAY AVG':<12} {int(wk_imp/5):>12,} ${wk_cost/5:>9,.0f} {pct(wk_is)} {pct(wk_rank)} {pct(wk_budget):>11} {pct(wk_top)} {pct(wk_abs)}")
    print(f"  {'WEEKEND AVG':<12} {int(we_imp/2):>12,} ${we_cost/2:>9,.0f} {pct(we_is)} {pct(we_rank)} {pct(we_budget):>11} {pct(we_top)} {pct(we_abs)}")

    print()
    print("  WEEKEND vs WEEKDAY DIFFERENCES:")
    is_diff = we_is - wk_is
    rank_diff = we_rank - wk_rank
    budget_diff = we_budget - wk_budget
    top_diff = we_top - wk_top
    abs_diff = we_abs - wk_abs

    def interpret(metric_name, diff, invert=False):
        if abs(diff) < 0.005:
            return f"    {metric_name}: {diff:+.1%}  (roughly flat)"
        direction_good = diff > 0 if not invert else diff < 0
        if direction_good:
            return f"    {metric_name}: {diff:+.1%}  (BETTER on weekends)"
        else:
            return f"    {metric_name}: {diff:+.1%}  (WORSE on weekends)"

    print(interpret("Search Impression Share", is_diff))
    print(interpret("Rank Lost IS (competitor)", rank_diff, invert=True))
    print(interpret("Budget Lost IS", budget_diff, invert=True))
    print(interpret("Top Impression Share", top_diff))
    print(interpret("Abs Top Impression Share", abs_diff))

    # Competitive Pressure Analysis
    print()
    print("=" * 80)
    print("  COMPETITIVE PRESSURE ANALYSIS")
    print("=" * 80)
    print()

    if we_rank < wk_rank and abs(we_rank - wk_rank) > 0.005:
        print("  FINDING: Rank-lost IS is LOWER on weekends.")
        print("  >> This means competitors are LESS aggressive on Sat/Sun.")
        print("  >> Competitors like BigRentz, United Rentals, EquipmentShare")
        print("     may be reducing bids or pausing campaigns on weekends.")
        print(f"     Weekday rank-lost IS: {wk_rank:.1%} vs Weekend: {we_rank:.1%}")
    elif we_rank > wk_rank and abs(we_rank - wk_rank) > 0.005:
        print("  FINDING: Rank-lost IS is HIGHER on weekends.")
        print("  >> This means competitors are MORE aggressive on Sat/Sun.")
        print("  >> Competitors may be increasing bids on weekends to capture")
        print("     last-minute/urgent rental demand.")
        print(f"     Weekday rank-lost IS: {wk_rank:.1%} vs Weekend: {we_rank:.1%}")
    else:
        print("  FINDING: Rank-lost IS is roughly flat across weekdays/weekends.")
        print("  >> Competitor bidding pressure is consistent throughout the week.")

    print()
    if we_is > wk_is and abs(we_is - wk_is) > 0.005:
        print("  OPPORTUNITY: DOZR's impression share is HIGHER on weekends.")
        print("  >> This suggests reduced competition or better relative positioning")
        print("     on Sat/Sun. Consider increasing weekend bids to capitalize.")
    elif we_is < wk_is and abs(we_is - wk_is) > 0.005:
        print("  CHALLENGE: DOZR's impression share is LOWER on weekends.")
        print("  >> This may indicate stronger weekend competition or budget")
        print("     constraints hitting before the weekend.")

    # --- Per-Campaign Breakdown ---
    print()
    print("=" * 80)
    print("  PER-CAMPAIGN WEEKEND vs WEEKDAY ANALYSIS")
    print("=" * 80)

    # Sort campaigns by total impressions
    camp_totals = {}
    for camp in camp_day_summary:
        total_imp = sum(camp_day_summary[camp][d]["impressions"] for d in DAY_ORDER)
        camp_totals[camp] = total_imp
    sorted_camps = sorted(camp_totals.keys(), key=lambda c: camp_totals[c], reverse=True)

    print(f"\n  {'Campaign':<45} {'WkDay IS':>9} {'WkEnd IS':>9} {'Diff':>8} {'WkDay RankLost':>15} {'WkEnd RankLost':>15}")
    print("  " + "-" * 102)

    camp_weekend_analysis = {}
    for camp in sorted_camps[:20]:
        wk_vals = [camp_day_summary[camp][d]["avg_search_is"] for d in DAY_ORDER if d in WEEKDAY_NAMES]
        we_vals = [camp_day_summary[camp][d]["avg_search_is"] for d in DAY_ORDER if d in WEEKEND_NAMES]
        wk_rank_vals = [camp_day_summary[camp][d]["avg_rank_lost_is"] for d in DAY_ORDER if d in WEEKDAY_NAMES]
        we_rank_vals = [camp_day_summary[camp][d]["avg_rank_lost_is"] for d in DAY_ORDER if d in WEEKEND_NAMES]

        wk_avg = safe_avg(wk_vals)
        we_avg = safe_avg(we_vals)
        wk_r = safe_avg(wk_rank_vals)
        we_r = safe_avg(we_rank_vals)
        diff = we_avg - wk_avg if (wk_avg and we_avg) else 0

        camp_name_short = camp[:44]
        print(
            f"  {camp_name_short:<45}"
            f" {pct(wk_avg)}"
            f" {pct(we_avg)}"
            f" {diff:>+7.1%}" if diff else f" {'N/A':>8}"
            f" {pct(wk_r):>15}"
            f" {pct(we_r):>15}"
        )

        camp_weekend_analysis[camp] = {
            "weekday_search_is": wk_avg,
            "weekend_search_is": we_avg,
            "diff": diff,
            "weekday_rank_lost": wk_r,
            "weekend_rank_lost": we_r,
            "total_impressions": camp_totals[camp],
        }

    # --- Detailed Day Breakdown for Top Campaigns ---
    print()
    print("=" * 80)
    print("  DETAILED DAY-BY-DAY FOR TOP 5 CAMPAIGNS")
    print("=" * 80)

    for camp in sorted_camps[:5]:
        print(f"\n  >> {camp}")
        print(f"     {'Day':<12} {'Impr':>10} {'Cost':>10} {'Search IS':>10} {'RankLost':>10} {'Top IS':>10} {'AbsTop IS':>10}")
        print(f"     {'-'*12} {'-'*10} {'-'*10} {'-'*10} {'-'*10} {'-'*10} {'-'*10}")
        for day in DAY_ORDER:
            cd = camp_day_summary[camp][day]
            marker = " <<" if day in WEEKEND_NAMES else ""
            print(
                f"     {day:<12}"
                f" {cd['impressions']:>10,}"
                f" ${cd['cost']:>9,.0f}"
                f" {pct(cd['avg_search_is'])}"
                f" {pct(cd['avg_rank_lost_is'])}"
                f" {pct(cd['avg_top_is'])}"
                f" {pct(cd['avg_abs_top_is'])}"
                f"{marker}"
            )

    # -------------------------------------------------------------------------
    # NOTE about auction insight competitor domains
    # -------------------------------------------------------------------------
    print()
    print("=" * 80)
    print("  NOTE ON COMPETITOR DOMAIN-LEVEL DATA")
    print("=" * 80)
    print()
    print("  The per-competitor domain breakdown (BigRentz, United Rentals,")
    print("  EquipmentShare, etc.) requires Standard-level API access for the")
    print("  auction_insight metrics:")
    print("    - segments.auction_insight_domain")
    print("    - metrics.auction_insight_search_impression_share")
    print("    - metrics.auction_insight_search_overlap_rate")
    print("    - metrics.auction_insight_search_outranking_share")
    print()
    print("  The current developer token has Basic access. To unlock this data:")
    print("  1. Apply for Standard access at: https://ads.google.com/nav/selectaccount")
    print("     (Google Ads API Center > API Access > Apply for Standard Access)")
    print("  2. Or export Auction Insights from the Google Ads UI with day-of-week")
    print("     segmentation as a workaround.")
    print()
    print("  However, the Rank Lost Impression Share data above is a strong proxy:")
    print("  HIGH rank-lost IS = competitors are outranking DOZR (strong presence)")
    print("  LOW rank-lost IS = competitors are weaker (DOZR has the advantage)")

    # -------------------------------------------------------------------------
    # Save JSON
    # -------------------------------------------------------------------------
    output = {
        "metadata": {
            "customer_id": CUSTOMER_ID,
            "date_range": {"start": start_str, "end": end_str},
            "total_rows": row_count,
            "active_search_campaigns": len(unique_campaigns),
            "generated_at": datetime.now().isoformat(),
            "note": (
                "Per-competitor domain data requires Standard API access. "
                "Rank Lost IS is used as a proxy for competitive pressure."
            ),
        },
        "account_level_by_day": day_summary,
        "account_weekday_vs_weekend": {
            "weekday": {
                "avg_impressions_per_day": int(wk_imp / 5),
                "avg_cost_per_day": round(wk_cost / 5, 2),
                "avg_search_impression_share": wk_is,
                "avg_rank_lost_impression_share": wk_rank,
                "avg_budget_lost_impression_share": wk_budget,
                "avg_top_impression_share": wk_top,
                "avg_abs_top_impression_share": wk_abs,
            },
            "weekend": {
                "avg_impressions_per_day": int(we_imp / 2),
                "avg_cost_per_day": round(we_cost / 2, 2),
                "avg_search_impression_share": we_is,
                "avg_rank_lost_impression_share": we_rank,
                "avg_budget_lost_impression_share": we_budget,
                "avg_top_impression_share": we_top,
                "avg_abs_top_impression_share": we_abs,
            },
            "differences": {
                "search_is_diff": round(is_diff, 6),
                "rank_lost_is_diff": round(rank_diff, 6),
                "budget_lost_is_diff": round(budget_diff, 6),
                "top_is_diff": round(top_diff, 6),
                "abs_top_is_diff": round(abs_diff, 6),
            },
        },
        "per_campaign_weekend_analysis": camp_weekend_analysis,
        "per_campaign_by_day": {
            camp: camp_day_summary[camp] for camp in sorted_camps[:20]
        },
    }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n  Results saved to: {OUTPUT_PATH}")
    print("=" * 80)


if __name__ == "__main__":
    main()
