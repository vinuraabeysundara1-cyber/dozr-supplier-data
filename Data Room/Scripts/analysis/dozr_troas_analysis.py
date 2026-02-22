#!/usr/bin/env python3
"""
DOZR Google Ads tROAS Eligibility Analysis
============================================
Analyzes all campaigns for Target ROAS eligibility, current bidding strategies,
and performance metrics over 30-day and 90-day windows.
"""

import warnings
warnings.filterwarnings("ignore")

import sys
from datetime import datetime, timedelta
from google.ads.googleads.client import GoogleAdsClient

# --- Configuration ---
CONFIG_PATH = "/Users/vinuraabeysundara/google-ads.yaml"
CUSTOMER_ID = "8531896842"
TROAS_MIN_CONVERSIONS_30D = 15  # Google's minimum for tROAS eligibility

# Date ranges
today = datetime.today()
date_30d_ago = (today - timedelta(days=30)).strftime("%Y-%m-%d")
date_90d_ago = (today - timedelta(days=90)).strftime("%Y-%m-%d")
date_today = today.strftime("%Y-%m-%d")


def fmt_currency(val):
    """Format micros to dollars."""
    if val is None:
        return "$0.00"
    return f"${val / 1_000_000:,.2f}"


def fmt_number(val):
    if val is None:
        return "0"
    return f"{val:,.0f}"


def fmt_roas(val):
    if val is None or val == 0:
        return "N/A"
    return f"{val:.2f}x"


def print_separator(char="=", width=150):
    print(char * width)


def print_header(title):
    print()
    print_separator()
    print(f"  {title}")
    print_separator()


def main():
    # --- Initialize Client ---
    print("Connecting to Google Ads API...")
    client = GoogleAdsClient.load_from_storage(CONFIG_PATH)
    ga_service = client.get_service("GoogleAdsService")

    # =====================================================================
    # QUERY 1: All Campaigns - Configuration & Bidding Strategy
    # =====================================================================
    print("Fetching campaign configurations...")

    query_campaigns = """
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.bidding_strategy,
            campaign.bidding_strategy_type,
            campaign.maximize_conversions.target_cpa_micros,
            campaign.maximize_conversion_value.target_roas,
            campaign.target_roas.target_roas,
            campaign.target_cpa.target_cpa_micros,
            campaign_budget.amount_micros
        FROM campaign
        WHERE campaign.status IN ('ENABLED', 'PAUSED')
        ORDER BY campaign.status ASC, campaign.name ASC
    """

    campaigns = {}
    response = ga_service.search(customer_id=CUSTOMER_ID, query=query_campaigns)
    for row in response:
        c = row.campaign
        cid = str(c.id)
        bid_type = c.bidding_strategy_type.name if c.bidding_strategy_type else "UNKNOWN"

        # Check for optional tROAS on Maximize Conversion Value
        max_cv_troas = None
        try:
            val = c.maximize_conversion_value.target_roas
            if val and val > 0:
                max_cv_troas = val
        except Exception:
            pass

        # Check for optional tCPA on Maximize Conversions
        max_conv_tcpa = None
        try:
            val = c.maximize_conversions.target_cpa_micros
            if val and val > 0:
                max_conv_tcpa = val
        except Exception:
            pass

        # Check explicit target_roas
        explicit_troas = None
        try:
            val = c.target_roas.target_roas
            if val and val > 0:
                explicit_troas = val
        except Exception:
            pass

        # Check explicit target_cpa
        explicit_tcpa = None
        try:
            val = c.target_cpa.target_cpa_micros
            if val and val > 0:
                explicit_tcpa = val
        except Exception:
            pass

        # Portfolio bidding strategy resource name
        portfolio_strategy = None
        try:
            if c.bidding_strategy:
                portfolio_strategy = c.bidding_strategy
        except Exception:
            pass

        # Budget
        budget_micros = 0
        try:
            budget_micros = row.campaign_budget.amount_micros
        except Exception:
            pass

        campaigns[cid] = {
            "id": cid,
            "name": c.name,
            "status": c.status.name,
            "bid_type": bid_type,
            "max_cv_troas": max_cv_troas,
            "max_conv_tcpa": max_conv_tcpa,
            "explicit_troas": explicit_troas,
            "explicit_tcpa": explicit_tcpa,
            "portfolio_strategy": portfolio_strategy,
            "budget_micros": budget_micros,
            # Metrics placeholders
            "30d": {"impressions": 0, "clicks": 0, "cost_micros": 0, "conversions": 0.0, "conv_value": 0.0},
            "90d": {"impressions": 0, "clicks": 0, "cost_micros": 0, "conversions": 0.0, "conv_value": 0.0},
            "conv_actions_90d": {},
        }

    print(f"  Found {len(campaigns)} campaigns (enabled + paused).")

    # =====================================================================
    # QUERY 2: Enabled Campaign Metrics - Last 30 Days
    # =====================================================================
    print(f"Fetching 30-day metrics ({date_30d_ago} to {date_today})...")

    query_30d = f"""
        SELECT
            campaign.id,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value
        FROM campaign
        WHERE campaign.status = 'ENABLED'
            AND segments.date BETWEEN '{date_30d_ago}' AND '{date_today}'
    """

    response = ga_service.search(customer_id=CUSTOMER_ID, query=query_30d)
    for row in response:
        cid = str(row.campaign.id)
        if cid in campaigns:
            campaigns[cid]["30d"]["impressions"] += row.metrics.impressions
            campaigns[cid]["30d"]["clicks"] += row.metrics.clicks
            campaigns[cid]["30d"]["cost_micros"] += row.metrics.cost_micros
            campaigns[cid]["30d"]["conversions"] += row.metrics.conversions
            campaigns[cid]["30d"]["conv_value"] += row.metrics.conversions_value

    # =====================================================================
    # QUERY 3: Enabled Campaign Metrics - Last 90 Days
    # =====================================================================
    print(f"Fetching 90-day metrics ({date_90d_ago} to {date_today})...")

    query_90d = f"""
        SELECT
            campaign.id,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value
        FROM campaign
        WHERE campaign.status = 'ENABLED'
            AND segments.date BETWEEN '{date_90d_ago}' AND '{date_today}'
    """

    response = ga_service.search(customer_id=CUSTOMER_ID, query=query_90d)
    for row in response:
        cid = str(row.campaign.id)
        if cid in campaigns:
            campaigns[cid]["90d"]["impressions"] += row.metrics.impressions
            campaigns[cid]["90d"]["clicks"] += row.metrics.clicks
            campaigns[cid]["90d"]["cost_micros"] += row.metrics.cost_micros
            campaigns[cid]["90d"]["conversions"] += row.metrics.conversions
            campaigns[cid]["90d"]["conv_value"] += row.metrics.conversions_value

    # =====================================================================
    # QUERY 4: Conversion Breakdown by Action Name - 90 Days
    # =====================================================================
    print("Fetching conversion action breakdown (90 days)...")

    query_conv_actions = f"""
        SELECT
            campaign.id,
            segments.conversion_action_name,
            metrics.conversions,
            metrics.conversions_value
        FROM campaign
        WHERE campaign.status = 'ENABLED'
            AND segments.date BETWEEN '{date_90d_ago}' AND '{date_today}'
    """

    response = ga_service.search(customer_id=CUSTOMER_ID, query=query_conv_actions)
    for row in response:
        cid = str(row.campaign.id)
        action_name = row.segments.conversion_action_name
        if cid in campaigns:
            if action_name not in campaigns[cid]["conv_actions_90d"]:
                campaigns[cid]["conv_actions_90d"][action_name] = {"conversions": 0.0, "value": 0.0}
            campaigns[cid]["conv_actions_90d"][action_name]["conversions"] += row.metrics.conversions
            campaigns[cid]["conv_actions_90d"][action_name]["value"] += row.metrics.conversions_value

    # =====================================================================
    # QUERY 5: Portfolio Bidding Strategies
    # =====================================================================
    print("Fetching portfolio bidding strategies...")

    query_portfolio = """
        SELECT
            bidding_strategy.id,
            bidding_strategy.name,
            bidding_strategy.type,
            bidding_strategy.target_roas.target_roas
        FROM bidding_strategy
    """

    portfolio_strategies = []
    try:
        response = ga_service.search(customer_id=CUSTOMER_ID, query=query_portfolio)
        for row in response:
            bs = row.bidding_strategy
            troas_val = None
            try:
                troas_val = bs.target_roas.target_roas
            except Exception:
                pass
            portfolio_strategies.append({
                "id": str(bs.id),
                "name": bs.name,
                "type": bs.type_.name if bs.type_ else "UNKNOWN",
                "target_roas": troas_val,
            })
    except Exception as e:
        print(f"  Note: Could not fetch portfolio strategies: {e}")

    # =====================================================================
    #  REPORTING
    # =====================================================================

    # --- Section 1: Campaign Bidding Configuration ---
    print_header("1. CAMPAIGN BIDDING CONFIGURATION (All Campaigns)")

    header = f"{'Campaign Name':<55} {'Status':<10} {'Bidding Strategy':<30} {'tROAS Set?':<12} {'Target':<14} {'Daily Budget':<14}"
    print(header)
    print("-" * 150)

    for cid, c in sorted(campaigns.items(), key=lambda x: (0 if x[1]["status"] == "ENABLED" else 1, x[1]["name"])):
        bid_type = c["bid_type"]

        # Determine if tROAS is in play
        troas_status = "NO"
        target_val = "-"

        if bid_type == "TARGET_ROAS":
            troas_status = "YES"
            if c["explicit_troas"]:
                target_val = f"{c['explicit_troas']:.2f}x"
        elif bid_type == "MAXIMIZE_CONVERSION_VALUE":
            if c["max_cv_troas"] and c["max_cv_troas"] > 0:
                troas_status = "YES (opt)"
                target_val = f"{c['max_cv_troas']:.2f}x"
        elif bid_type == "MAXIMIZE_CONVERSIONS":
            if c["max_conv_tcpa"] and c["max_conv_tcpa"] > 0:
                target_val = f"tCPA: {fmt_currency(c['max_conv_tcpa'])}"
        elif bid_type == "TARGET_CPA":
            if c["explicit_tcpa"]:
                target_val = f"tCPA: {fmt_currency(c['explicit_tcpa'])}"

        # Portfolio indicator
        portfolio_tag = ""
        if c["portfolio_strategy"]:
            portfolio_tag = " [PORT]"

        budget_str = fmt_currency(c["budget_micros"])
        name_display = c["name"][:53]

        print(f"{name_display:<55} {c['status']:<10} {bid_type + portfolio_tag:<30} {troas_status:<12} {target_val:<14} {budget_str:<14}")

    # --- Section 2: 30-Day Performance (Enabled Only) ---
    print_header("2. 30-DAY PERFORMANCE METRICS (Enabled Campaigns)")

    enabled = {cid: c for cid, c in campaigns.items() if c["status"] == "ENABLED"}

    header = f"{'Campaign Name':<50} {'Impr':>10} {'Clicks':>8} {'Cost':>14} {'Conv':>8} {'Conv Value':>16} {'ROAS':>8}"
    print(header)
    print("-" * 150)

    totals_30d = {"impressions": 0, "clicks": 0, "cost_micros": 0, "conversions": 0.0, "conv_value": 0.0}

    for cid, c in sorted(enabled.items(), key=lambda x: x[1]["name"]):
        m = c["30d"]
        roas = (m["conv_value"] / (m["cost_micros"] / 1_000_000)) if m["cost_micros"] > 0 else 0
        print(f"{c['name'][:48]:<50} {m['impressions']:>10,} {m['clicks']:>8,} {fmt_currency(m['cost_micros']):>14} {m['conversions']:>8.1f} {'${:,.2f}'.format(m['conv_value']):>16} {fmt_roas(roas):>8}")
        for k in totals_30d:
            totals_30d[k] += m[k]

    print("-" * 150)
    total_roas_30d = (totals_30d["conv_value"] / (totals_30d["cost_micros"] / 1_000_000)) if totals_30d["cost_micros"] > 0 else 0
    print(f"{'TOTAL':<50} {totals_30d['impressions']:>10,} {totals_30d['clicks']:>8,} {fmt_currency(totals_30d['cost_micros']):>14} {totals_30d['conversions']:>8.1f} {'${:,.2f}'.format(totals_30d['conv_value']):>16} {fmt_roas(total_roas_30d):>8}")

    # --- Section 3: 90-Day Performance (Enabled Only) ---
    print_header("3. 90-DAY PERFORMANCE METRICS (Enabled Campaigns)")

    header = f"{'Campaign Name':<50} {'Impr':>10} {'Clicks':>8} {'Cost':>14} {'Conv':>8} {'Conv Value':>16} {'ROAS':>8}"
    print(header)
    print("-" * 150)

    totals_90d = {"impressions": 0, "clicks": 0, "cost_micros": 0, "conversions": 0.0, "conv_value": 0.0}

    for cid, c in sorted(enabled.items(), key=lambda x: x[1]["name"]):
        m = c["90d"]
        roas = (m["conv_value"] / (m["cost_micros"] / 1_000_000)) if m["cost_micros"] > 0 else 0
        print(f"{c['name'][:48]:<50} {m['impressions']:>10,} {m['clicks']:>8,} {fmt_currency(m['cost_micros']):>14} {m['conversions']:>8.1f} {'${:,.2f}'.format(m['conv_value']):>16} {fmt_roas(roas):>8}")
        for k in totals_90d:
            totals_90d[k] += m[k]

    print("-" * 150)
    total_roas_90d = (totals_90d["conv_value"] / (totals_90d["cost_micros"] / 1_000_000)) if totals_90d["cost_micros"] > 0 else 0
    print(f"{'TOTAL':<50} {totals_90d['impressions']:>10,} {totals_90d['clicks']:>8,} {fmt_currency(totals_90d['cost_micros']):>14} {totals_90d['conversions']:>8.1f} {'${:,.2f}'.format(totals_90d['conv_value']):>16} {fmt_roas(total_roas_90d):>8}")

    # --- Section 4: Conversion Action Breakdown (90 Days) ---
    print_header("4. CONVERSION ACTION BREAKDOWN - 90 DAYS (Enabled Campaigns)")
    print("  [Closed Won Deals marked with <<<]")

    for cid, c in sorted(enabled.items(), key=lambda x: x[1]["name"]):
        if not c["conv_actions_90d"]:
            continue
        print(f"\n  Campaign: {c['name']}")
        print(f"  {'Conversion Action':<60} {'Conversions':>12} {'Value':>16}")
        print(f"  {'-'*92}")

        for action_name, data in sorted(c["conv_actions_90d"].items(), key=lambda x: x[1]["value"], reverse=True):
            is_cw = " <<<" if "closed" in action_name.lower() and "won" in action_name.lower() else ""
            print(f"  {action_name[:58]:<60} {data['conversions']:>12.2f} {'${:,.2f}'.format(data['value']):>16}{is_cw}")

    # --- Section 5: tROAS Eligibility Analysis ---
    print_header("5. tROAS ELIGIBILITY ANALYSIS (Enabled Campaigns)")

    header = (
        f"{'Campaign Name':<42} "
        f"{'Bid Type':<24} "
        f"{'tROAS Now?':<12} "
        f"{'30d Conv':>9} "
        f"{'30d ROAS':>9} "
        f"{'90d ROAS':>9} "
        f"{'CW 90d ROAS':>12} "
        f"{'Eligible?':>10} "
        f"{'Notes'}"
    )
    print(header)
    print("-" * 160)

    for cid, c in sorted(enabled.items(), key=lambda x: x[1]["name"]):
        m30 = c["30d"]
        m90 = c["90d"]

        roas_30d = (m30["conv_value"] / (m30["cost_micros"] / 1_000_000)) if m30["cost_micros"] > 0 else 0
        roas_90d = (m90["conv_value"] / (m90["cost_micros"] / 1_000_000)) if m90["cost_micros"] > 0 else 0

        # True ROAS: Closed Won Deals only (90d)
        cw_value_90d = 0.0
        cw_conversions_90d = 0.0
        for action_name, data in c["conv_actions_90d"].items():
            if "closed" in action_name.lower() and "won" in action_name.lower():
                cw_value_90d += data["value"]
                cw_conversions_90d += data["conversions"]

        cw_roas_90d = (cw_value_90d / (m90["cost_micros"] / 1_000_000)) if m90["cost_micros"] > 0 else 0

        # Current tROAS status
        using_troas = "NO"
        if c["bid_type"] == "TARGET_ROAS":
            using_troas = "YES"
        elif c["bid_type"] == "MAXIMIZE_CONVERSION_VALUE" and c["max_cv_troas"] and c["max_cv_troas"] > 0:
            using_troas = "YES (opt)"

        # Eligibility check
        conv_30d = m30["conversions"]
        meets_conv_threshold = conv_30d >= TROAS_MIN_CONVERSIONS_30D
        has_conv_value = m30["conv_value"] > 0

        if using_troas in ("YES", "YES (opt)"):
            eligible = "ACTIVE"
            notes = "Already using tROAS"
        elif meets_conv_threshold and has_conv_value:
            eligible = "YES"
            notes = f"{conv_30d:.0f} conv >= {TROAS_MIN_CONVERSIONS_30D}"
        elif has_conv_value and not meets_conv_threshold:
            eligible = "NO"
            notes = f"Only {conv_30d:.0f}/{TROAS_MIN_CONVERSIONS_30D} conv in 30d"
        else:
            eligible = "NO"
            notes = "No conv value data"

        name_display = c["name"][:40]
        print(
            f"{name_display:<42} "
            f"{c['bid_type']:<24} "
            f"{using_troas:<12} "
            f"{conv_30d:>9.1f} "
            f"{fmt_roas(roas_30d):>9} "
            f"{fmt_roas(roas_90d):>9} "
            f"{fmt_roas(cw_roas_90d):>12} "
            f"{eligible:>10} "
            f"{notes}"
        )

    # --- Section 6: Portfolio Bidding Strategies ---
    print_header("6. PORTFOLIO BIDDING STRATEGIES")

    if portfolio_strategies:
        header = f"{'Strategy Name':<50} {'Type':<30} {'Target ROAS':<14} {'ID':<20}"
        print(header)
        print("-" * 120)
        for ps in portfolio_strategies:
            troas_display = f"{ps['target_roas']:.2f}x" if ps["target_roas"] and ps["target_roas"] > 0 else "-"
            print(f"{ps['name'][:48]:<50} {ps['type']:<30} {troas_display:<14} {ps['id']:<20}")
    else:
        print("  No portfolio bidding strategies found in this account.")

    # --- Section 7: Summary & Recommendations ---
    print_header("7. SUMMARY & RECOMMENDATIONS")

    already_troas = []
    eligible_troas = []
    not_eligible = []

    for cid, c in enabled.items():
        m30 = c["30d"]
        conv_30d = m30["conversions"]
        has_value = m30["conv_value"] > 0

        if c["bid_type"] == "TARGET_ROAS" or (c["bid_type"] == "MAXIMIZE_CONVERSION_VALUE" and c["max_cv_troas"] and c["max_cv_troas"] > 0):
            already_troas.append(c)
        elif conv_30d >= TROAS_MIN_CONVERSIONS_30D and has_value:
            eligible_troas.append(c)
        else:
            not_eligible.append(c)

    print(f"\n  Campaigns ALREADY using tROAS:                {len(already_troas)}")
    for c in sorted(already_troas, key=lambda x: x["name"]):
        target = ""
        if c["explicit_troas"]:
            target = f" (target: {c['explicit_troas']:.2f}x)"
        elif c["max_cv_troas"]:
            target = f" (optional target: {c['max_cv_troas']:.2f}x)"
        print(f"    - {c['name']}{target}")

    print(f"\n  Campaigns ELIGIBLE for tROAS (>=15 conv/30d): {len(eligible_troas)}")
    for c in sorted(eligible_troas, key=lambda x: x["name"]):
        m30 = c["30d"]
        roas = (m30["conv_value"] / (m30["cost_micros"] / 1_000_000)) if m30["cost_micros"] > 0 else 0
        print(f"    - {c['name']} ({m30['conversions']:.0f} conv, {fmt_roas(roas)} ROAS, currently: {c['bid_type']})")

    print(f"\n  Campaigns NOT YET eligible for tROAS:         {len(not_eligible)}")
    for c in sorted(not_eligible, key=lambda x: x["name"]):
        m30 = c["30d"]
        shortfall = max(0, TROAS_MIN_CONVERSIONS_30D - m30["conversions"])
        print(f"    - {c['name']} ({m30['conversions']:.0f} conv in 30d, need {shortfall:.0f} more, currently: {c['bid_type']})")

    # Closed Won analysis
    print(f"\n  --- Closed Won Deal ROAS Analysis (90 days) ---")
    for cid, c in sorted(enabled.items(), key=lambda x: x[1]["name"]):
        m90 = c["90d"]
        cw_value = 0.0
        cw_conv = 0.0
        for action_name, data in c["conv_actions_90d"].items():
            if "closed" in action_name.lower() and "won" in action_name.lower():
                cw_value += data["value"]
                cw_conv += data["conversions"]
        if cw_conv > 0 or cw_value > 0:
            cw_roas = (cw_value / (m90["cost_micros"] / 1_000_000)) if m90["cost_micros"] > 0 else 0
            total_roas = (m90["conv_value"] / (m90["cost_micros"] / 1_000_000)) if m90["cost_micros"] > 0 else 0
            print(f"    - {c['name']}")
            print(f"        CW Conversions: {cw_conv:.2f} | CW Value: ${cw_value:,.2f} | CW ROAS: {fmt_roas(cw_roas)} | Google ROAS: {fmt_roas(total_roas)}")

    print()
    print_separator()
    print("  ANALYSIS COMPLETE")
    print(f"  Date range: 30-day ({date_30d_ago} to {date_today}) | 90-day ({date_90d_ago} to {date_today})")
    print(f"  Customer ID: {CUSTOMER_ID}")
    print(f"  tROAS eligibility threshold: {TROAS_MIN_CONVERSIONS_30D} conversions in 30 days (Google minimum)")
    print_separator()
    print()


if __name__ == "__main__":
    main()
