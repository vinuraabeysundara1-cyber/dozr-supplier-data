#!/usr/bin/env python3
"""
DOZR Campaign Performance Analysis
Pull detailed performance data for all campaigns over the last 90 days
to validate best candidates for a weekend experiment.
"""

import warnings
warnings.filterwarnings("ignore")

import sys
from datetime import datetime, timedelta
from google.ads.googleads.client import GoogleAdsClient

# ── Config ──────────────────────────────────────────────────────────────────
CONFIG_PATH = "/Users/vinuraabeysundara/google-ads.yaml"
CUSTOMER_ID = "8531896842"

# Date range: last 90 days
end_date = datetime.today() - timedelta(days=1)
start_date = end_date - timedelta(days=89)
DATE_FROM = start_date.strftime("%Y-%m-%d")
DATE_TO = end_date.strftime("%Y-%m-%d")

print("=" * 130)
print("DOZR CAMPAIGN PERFORMANCE ANALYSIS - WEEKEND EXPERIMENT VALIDATION")
print("=" * 130)
print(f"Date range: {DATE_FROM} to {DATE_TO} (90 days)")
print(f"Customer ID: {CUSTOMER_ID}")
print()

# ── Initialize client ───────────────────────────────────────────────────────
try:
    client = GoogleAdsClient.load_from_storage(CONFIG_PATH)
    ga_service = client.get_service("GoogleAdsService")
    print("[OK] Google Ads client initialized successfully.")
except Exception as e:
    print(f"[ERROR] Failed to initialize client: {e}")
    sys.exit(1)

# ── Helper: run a GAQL query ────────────────────────────────────────────────
def run_query(query):
    rows = []
    try:
        response = ga_service.search_stream(customer_id=CUSTOMER_ID, query=query)
        for batch in response:
            for row in batch.results:
                rows.append(row)
    except Exception as e:
        print(f"[ERROR] Query failed: {e}")
        print(f"  Query: {query[:300]}...")
    return rows


# ═══════════════════════════════════════════════════════════════════════════
# QUERY 1: Campaign-level metrics (no conversion-action segment)
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "-" * 130)
print("STEP 1: Pulling campaign-level metrics...")
print("-" * 130)

campaign_query = f"""
    SELECT
        campaign.id,
        campaign.name,
        campaign.status,
        campaign.bidding_strategy_type,
        campaign_budget.amount_micros,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.all_conversions,
        metrics.all_conversions_value,
        metrics.conversions,
        metrics.conversions_value,
        metrics.search_impression_share,
        metrics.search_rank_lost_impression_share,
        metrics.search_budget_lost_impression_share
    FROM campaign
    WHERE segments.date BETWEEN '{DATE_FROM}' AND '{DATE_TO}'
        AND campaign.status != 'REMOVED'
    ORDER BY campaign.name
"""

campaign_rows = run_query(campaign_query)

# Aggregate by campaign (rows are per-date due to date filter)
campaigns = {}
for row in campaign_rows:
    cid = row.campaign.id
    if cid not in campaigns:
        campaigns[cid] = {
            "id": cid,
            "name": row.campaign.name,
            "status": row.campaign.status.name if hasattr(row.campaign.status, 'name') else str(row.campaign.status),
            "bidding_strategy_type": row.campaign.bidding_strategy_type.name if hasattr(row.campaign.bidding_strategy_type, 'name') else str(row.campaign.bidding_strategy_type),
            "daily_budget_micros": row.campaign_budget.amount_micros,
            "impressions": 0,
            "clicks": 0,
            "cost_micros": 0,
            "all_conversions": 0.0,
            "all_conversions_value": 0.0,
            "conversions": 0.0,
            "conversions_value": 0.0,
            # For impression share, we collect daily values and average
            "search_imp_share_vals": [],
            "search_rank_lost_vals": [],
            "search_budget_lost_vals": [],
            "days_with_data": 0,
        }
    c = campaigns[cid]
    c["impressions"] += row.metrics.impressions
    c["clicks"] += row.metrics.clicks
    c["cost_micros"] += row.metrics.cost_micros
    c["all_conversions"] += row.metrics.all_conversions
    c["all_conversions_value"] += row.metrics.all_conversions_value
    c["conversions"] += row.metrics.conversions
    c["conversions_value"] += row.metrics.conversions_value
    c["days_with_data"] += 1
    # Impression share is returned as a fraction (0-1) by the API
    if row.metrics.search_impression_share is not None and row.metrics.search_impression_share > 0:
        c["search_imp_share_vals"].append(row.metrics.search_impression_share)
    if row.metrics.search_rank_lost_impression_share is not None and row.metrics.search_rank_lost_impression_share > 0:
        c["search_rank_lost_vals"].append(row.metrics.search_rank_lost_impression_share)
    if row.metrics.search_budget_lost_impression_share is not None and row.metrics.search_budget_lost_impression_share > 0:
        c["search_budget_lost_vals"].append(row.metrics.search_budget_lost_impression_share)

# Compute averages for impression share
for cid, c in campaigns.items():
    c["search_imp_share"] = (sum(c["search_imp_share_vals"]) / len(c["search_imp_share_vals"]) * 100) if c["search_imp_share_vals"] else 0.0
    c["search_rank_lost"] = (sum(c["search_rank_lost_vals"]) / len(c["search_rank_lost_vals"]) * 100) if c["search_rank_lost_vals"] else 0.0
    c["search_budget_lost"] = (sum(c["search_budget_lost_vals"]) / len(c["search_budget_lost_vals"]) * 100) if c["search_budget_lost_vals"] else 0.0
    c["cost"] = c["cost_micros"] / 1_000_000
    c["daily_budget"] = c["daily_budget_micros"] / 1_000_000
    c["cpc"] = c["cost"] / c["clicks"] if c["clicks"] > 0 else 0
    c["ctr"] = (c["clicks"] / c["impressions"] * 100) if c["impressions"] > 0 else 0

print(f"  Found {len(campaigns)} campaigns with data in the period.")

# ═══════════════════════════════════════════════════════════════════════════
# QUERY 2: Conversion breakdown by conversion action name
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "-" * 130)
print("STEP 2: Pulling conversion breakdown by conversion action...")
print("-" * 130)

conv_query = f"""
    SELECT
        campaign.id,
        campaign.name,
        segments.conversion_action_name,
        metrics.conversions,
        metrics.conversions_value,
        metrics.all_conversions,
        metrics.all_conversions_value
    FROM campaign
    WHERE segments.date BETWEEN '{DATE_FROM}' AND '{DATE_TO}'
        AND campaign.status != 'REMOVED'
        AND metrics.conversions > 0
    ORDER BY campaign.name
"""

conv_rows = run_query(conv_query)

# Aggregate conversion data by campaign + conversion action
conv_breakdown = {}  # campaign_id -> {action_name -> {conversions, value}}
all_conv_actions = set()
for row in conv_rows:
    cid = row.campaign.id
    action_name = row.segments.conversion_action_name
    all_conv_actions.add(action_name)
    if cid not in conv_breakdown:
        conv_breakdown[cid] = {}
    if action_name not in conv_breakdown[cid]:
        conv_breakdown[cid][action_name] = {
            "conversions": 0.0,
            "value": 0.0,
            "all_conversions": 0.0,
            "all_value": 0.0,
        }
    conv_breakdown[cid][action_name]["conversions"] += row.metrics.conversions
    conv_breakdown[cid][action_name]["value"] += row.metrics.conversions_value
    conv_breakdown[cid][action_name]["all_conversions"] += row.metrics.all_conversions
    conv_breakdown[cid][action_name]["all_value"] += row.metrics.all_conversions_value

print(f"  Found conversion data for {len(conv_breakdown)} campaigns.")
print(f"  Unique conversion action names across all campaigns:")
for a in sorted(all_conv_actions):
    print(f"    - {a}")

# Identify Closed Won Deal data per campaign
# We search for action names that look like "closed won" or "deal"
print(f"\n  Identifying 'Closed Won' conversion actions...")
closed_won_actions = []
for a in all_conv_actions:
    lower_a = a.lower()
    if "closed" in lower_a or "won" in lower_a or "deal" in lower_a or "revenue" in lower_a:
        closed_won_actions.append(a)
        print(f"    Matched: {a}")

if not closed_won_actions:
    print("    [NOTE] No exact 'Closed Won' actions found. Will check for revenue-bearing actions.")
    # Fallback: find actions with the highest conversion values
    action_totals = {}
    for cid, actions in conv_breakdown.items():
        for action_name, data in actions.items():
            if action_name not in action_totals:
                action_totals[action_name] = {"conversions": 0, "value": 0}
            action_totals[action_name]["conversions"] += data["conversions"]
            action_totals[action_name]["value"] += data["value"]
    print("\n    Conversion actions ranked by total value:")
    for a in sorted(action_totals.keys(), key=lambda x: action_totals[x]["value"], reverse=True):
        print(f"      {a:<55} Conv: {action_totals[a]['conversions']:>8.1f}  Value: ${action_totals[a]['value']:>14,.2f}")

for cid, c in campaigns.items():
    c["closed_won_count"] = 0.0
    c["closed_won_value"] = 0.0
    if cid in conv_breakdown:
        for action_name, data in conv_breakdown[cid].items():
            lower_name = action_name.lower()
            if any(cw.lower() == lower_name for cw in closed_won_actions):
                c["closed_won_count"] += data["conversions"]
                c["closed_won_value"] += data["value"]
            elif not closed_won_actions:
                # If no specific closed won actions, use all actions with value
                # (We'll refine below)
                pass
    c["true_roas"] = c["closed_won_value"] / c["cost"] if c["cost"] > 0 else 0
    c["is_winner"] = c["closed_won_count"] > 0 and c["true_roas"] > 0

# If no closed_won_actions were found, use conversion value as proxy
if not closed_won_actions:
    print("\n  [FALLBACK] Using total conversions_value as Closed Won proxy (highest-value actions)")
    for cid, c in campaigns.items():
        c["closed_won_count"] = c["conversions"]
        c["closed_won_value"] = c["conversions_value"]
        c["true_roas"] = c["closed_won_value"] / c["cost"] if c["cost"] > 0 else 0
        c["is_winner"] = c["closed_won_count"] > 0 and c["true_roas"] > 0


# ═══════════════════════════════════════════════════════════════════════════
# DISPLAY: Campaign-Level Summary Table
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 155)
print("CAMPAIGN-LEVEL PERFORMANCE SUMMARY (Last 90 Days)")
print("=" * 155)

sorted_campaigns = sorted(campaigns.values(), key=lambda x: x["cost"], reverse=True)

header = f"{'Campaign Name':<45} {'Status':<9} {'Bidding':<18} {'Impr':>10} {'Clicks':>8} {'Cost':>12} {'CPC':>8} {'CTR':>7} {'Conv':>7} {'Conv Val':>12} {'AllConv':>8} {'AllConvVal':>12}"
print(header)
print("-" * 155)

for c in sorted_campaigns:
    print(
        f"{c['name'][:44]:<45} "
        f"{c['status'][:8]:<9} "
        f"{c['bidding_strategy_type'][:17]:<18} "
        f"{c['impressions']:>10,} "
        f"{c['clicks']:>8,} "
        f"${c['cost']:>10,.2f} "
        f"${c['cpc']:>6,.2f} "
        f"{c['ctr']:>6.2f}% "
        f"{c['conversions']:>7.1f} "
        f"${c['conversions_value']:>10,.2f} "
        f"{c['all_conversions']:>8.1f} "
        f"${c['all_conversions_value']:>10,.2f}"
    )

print()
totals_impr = sum(c["impressions"] for c in campaigns.values())
totals_clicks = sum(c["clicks"] for c in campaigns.values())
totals_cost = sum(c["cost"] for c in campaigns.values())
totals_conv = sum(c["conversions"] for c in campaigns.values())
totals_conv_val = sum(c["conversions_value"] for c in campaigns.values())
totals_all_conv = sum(c["all_conversions"] for c in campaigns.values())
totals_all_val = sum(c["all_conversions_value"] for c in campaigns.values())
totals_cpc = totals_cost / totals_clicks if totals_clicks > 0 else 0
totals_ctr = totals_clicks / totals_impr * 100 if totals_impr > 0 else 0
print(
    f"{'TOTALS':<45} {'':9} {'':18} "
    f"{totals_impr:>10,} "
    f"{totals_clicks:>8,} "
    f"${totals_cost:>10,.2f} "
    f"${totals_cpc:>6,.2f} "
    f"{totals_ctr:>6.2f}% "
    f"{totals_conv:>7.1f} "
    f"${totals_conv_val:>10,.2f} "
    f"{totals_all_conv:>8.1f} "
    f"${totals_all_val:>10,.2f}"
)


# ═══════════════════════════════════════════════════════════════════════════
# DISPLAY: Search Impression Share Table
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 130)
print("SEARCH IMPRESSION SHARE ANALYSIS")
print("=" * 130)

header2 = f"{'Campaign Name':<45} {'Daily Budget':>13} {'Search IS':>10} {'Rank Lost':>10} {'Budget Lost':>12} {'Budget Constrained?':>20}"
print(header2)
print("-" * 130)

for c in sorted_campaigns:
    budget_constrained = "YES" if c["search_budget_lost"] > 10 else ("MAYBE" if c["search_budget_lost"] > 5 else "No")
    print(
        f"{c['name'][:44]:<45} "
        f"${c['daily_budget']:>11,.2f} "
        f"{c['search_imp_share']:>9.1f}% "
        f"{c['search_rank_lost']:>9.1f}% "
        f"{c['search_budget_lost']:>11.1f}% "
        f"{budget_constrained:>20}"
    )


# ═══════════════════════════════════════════════════════════════════════════
# DISPLAY: Closed Won Deal Analysis & Winner Identification
# ═══════════════════════════════════════════════════════════════════════════
cw_label = "Closed Won" if closed_won_actions else "Total Conversion Value (proxy)"
print("\n" + "=" * 130)
print(f"{cw_label.upper()} DEAL ANALYSIS & WINNER IDENTIFICATION")
print("=" * 130)

header3 = f"{'Campaign Name':<45} {'Cost':>12} {'CW Deals':>9} {'CW Value':>14} {'True ROAS':>10} {'Winner?':>12}"
print(header3)
print("-" * 130)

for c in sorted(campaigns.values(), key=lambda x: x["closed_won_value"], reverse=True):
    winner_label = "*** YES ***" if c["is_winner"] else "No"
    print(
        f"{c['name'][:44]:<45} "
        f"${c['cost']:>10,.2f} "
        f"{c['closed_won_count']:>9.1f} "
        f"${c['closed_won_value']:>12,.2f} "
        f"{c['true_roas']:>9.2f}x "
        f"{winner_label:>12}"
    )


# ═══════════════════════════════════════════════════════════════════════════
# RANKING 1: By Total Closed Won Revenue
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 130)
print("RANKING 1: By Total Closed Won Deal Revenue (Descending)")
print("=" * 130)

rank = 1
for c in sorted(campaigns.values(), key=lambda x: x["closed_won_value"], reverse=True):
    name_lower = c["name"].lower()
    marker = ""
    if "boom" in name_lower and "us" in name_lower:
        marker = " <-- BOOM LIFTS US"
    elif "excavator" in name_lower and "us" in name_lower:
        marker = " <-- EXCAVATOR US"
    print(f"  #{rank:<3} {c['name']:<48} CW Revenue: ${c['closed_won_value']:>12,.2f}   ROAS: {c['true_roas']:>7.2f}x   Cost: ${c['cost']:>10,.2f}{marker}")
    rank += 1


# ═══════════════════════════════════════════════════════════════════════════
# RANKING 2: By True ROAS
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 130)
print("RANKING 2: By True ROAS (Descending)")
print("=" * 130)

rank = 1
for c in sorted(campaigns.values(), key=lambda x: x["true_roas"], reverse=True):
    name_lower = c["name"].lower()
    marker = ""
    if "boom" in name_lower and "us" in name_lower:
        marker = " <-- BOOM LIFTS US"
    elif "excavator" in name_lower and "us" in name_lower:
        marker = " <-- EXCAVATOR US"
    print(f"  #{rank:<3} {c['name']:<48} ROAS: {c['true_roas']:>7.2f}x   CW Revenue: ${c['closed_won_value']:>12,.2f}   Cost: ${c['cost']:>10,.2f}{marker}")
    rank += 1


# ═══════════════════════════════════════════════════════════════════════════
# RANKING 3: By Total Impression Volume
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 130)
print("RANKING 3: By Total Impression Volume (Descending)")
print("=" * 130)

rank = 1
for c in sorted(campaigns.values(), key=lambda x: x["impressions"], reverse=True):
    name_lower = c["name"].lower()
    marker = ""
    if "boom" in name_lower and "us" in name_lower:
        marker = " <-- BOOM LIFTS US"
    elif "excavator" in name_lower and "us" in name_lower:
        marker = " <-- EXCAVATOR US"
    print(f"  #{rank:<3} {c['name']:<48} Impressions: {c['impressions']:>10,}   Clicks: {c['clicks']:>7,}   CTR: {c['ctr']:>6.2f}%{marker}")
    rank += 1


# ═══════════════════════════════════════════════════════════════════════════
# DEEP DIVE: Boom Lifts US and Excavator US Campaigns
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 130)
print("DEEP DIVE: TOP CANDIDATE CAMPAIGNS (Boom Lifts US & Excavator US)")
print("=" * 130)

target_campaigns = []
for c in campaigns.values():
    name_lower = c["name"].lower()
    if ("boom" in name_lower and "lift" in name_lower and "us" in name_lower):
        target_campaigns.append(c)
    elif ("excavator" in name_lower and "us" in name_lower):
        target_campaigns.append(c)

if not target_campaigns:
    # Broader search
    print("\n  [NOTE] No exact match. Searching broader for 'boom' or 'excavator'...")
    for c in campaigns.values():
        name_lower = c["name"].lower()
        if "boom" in name_lower or "excavator" in name_lower:
            target_campaigns.append(c)

if not target_campaigns:
    print("  [WARNING] Could not find Boom Lifts or Excavator campaigns.")
    print("  Available campaigns:")
    for c in sorted(campaigns.values(), key=lambda x: x["name"]):
        print(f"    - {c['name']}")
else:
    for c in sorted(target_campaigns, key=lambda x: x["closed_won_value"], reverse=True):
        print(f"\n{'─' * 110}")
        print(f"  CAMPAIGN: {c['name']}")
        print(f"{'─' * 110}")
        print(f"  Status:                {c['status']}")
        print(f"  Bidding Strategy:      {c['bidding_strategy_type']}")
        print(f"  Daily Budget:          ${c['daily_budget']:,.2f}")
        print(f"  Days with Data:        {c['days_with_data']}")
        print()
        print(f"  --- Traffic Metrics ---")
        print(f"  Impressions:           {c['impressions']:,}")
        print(f"  Clicks:                {c['clicks']:,}")
        print(f"  Cost:                  ${c['cost']:,.2f}")
        print(f"  CPC:                   ${c['cpc']:,.2f}")
        print(f"  CTR:                   {c['ctr']:.2f}%")
        print()
        print(f"  --- Impression Share ---")
        print(f"  Search Impression Share:          {c['search_imp_share']:.1f}%")
        print(f"  Search Rank Lost IS:              {c['search_rank_lost']:.1f}%")
        print(f"  Search Budget Lost IS:            {c['search_budget_lost']:.1f}%")
        budget_status = "BUDGET CONSTRAINED - high potential for weekend budget increase" if c["search_budget_lost"] > 10 else ("Slightly constrained - some room for growth" if c["search_budget_lost"] > 5 else "Not significantly budget constrained - may need bid/targeting changes")
        print(f"  Budget Constraint:                {budget_status}")
        print()
        print(f"  --- Conversion Summary ---")
        print(f"  Total Conversions:     {c['conversions']:.1f}")
        print(f"  Total Conv Value:      ${c['conversions_value']:,.2f}")
        print(f"  All Conversions:       {c['all_conversions']:.1f}")
        print(f"  All Conv Value:        ${c['all_conversions_value']:,.2f}")
        print()
        print(f"  --- Closed Won Deals ---")
        print(f"  Closed Won Count:      {c['closed_won_count']:.1f}")
        print(f"  Closed Won Value:      ${c['closed_won_value']:,.2f}")
        print(f"  True ROAS:             {c['true_roas']:.2f}x")
        print(f"  Winner Status:         {'YES - Positive ROAS with Closed Won Deals' if c['is_winner'] else 'NO - Does not meet winner criteria'}")
        print()
        print(f"  --- Conversion Action Breakdown ---")
        cid = c["id"]
        if cid in conv_breakdown:
            conv_header = f"    {'Conversion Action':<55} {'Conversions':>12} {'Value':>14}"
            print(conv_header)
            print(f"    {'-' * 81}")
            for action_name in sorted(conv_breakdown[cid].keys(), key=lambda x: conv_breakdown[cid][x]["value"], reverse=True):
                d = conv_breakdown[cid][action_name]
                is_cw = " <<< CLOSED WON" if any(cw.lower() == action_name.lower() for cw in closed_won_actions) else ""
                print(f"    {action_name[:54]:<55} {d['conversions']:>12.1f} ${d['value']:>12,.2f}{is_cw}")
        else:
            print("    (No conversion data found for this campaign)")


# ═══════════════════════════════════════════════════════════════════════════
# DISPLAY: Full conversion action breakdown for ALL campaigns
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 130)
print("FULL CONVERSION BREAKDOWN BY CAMPAIGN")
print("=" * 130)

for c in sorted(campaigns.values(), key=lambda x: x["closed_won_value"], reverse=True):
    cid = c["id"]
    print(f"\n  {c['name']} (Cost: ${c['cost']:,.2f} | CW Value: ${c['closed_won_value']:,.2f} | ROAS: {c['true_roas']:.2f}x)")
    if cid in conv_breakdown:
        for action_name in sorted(conv_breakdown[cid].keys(), key=lambda x: conv_breakdown[cid][x]["value"], reverse=True):
            d = conv_breakdown[cid][action_name]
            marker = " *** CLOSED WON ***" if any(cw.lower() == action_name.lower() for cw in closed_won_actions) else ""
            print(f"    {action_name:<55} Conv: {d['conversions']:>7.1f}  Value: ${d['value']:>12,.2f}{marker}")
    else:
        print(f"    (No conversions)")


# ═══════════════════════════════════════════════════════════════════════════
# WEEKEND EXPERIMENT RECOMMENDATION
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 130)
print("WEEKEND EXPERIMENT VALIDATION SUMMARY")
print("=" * 130)

winners = sorted([c for c in campaigns.values() if c["is_winner"]], key=lambda x: x["true_roas"], reverse=True)
non_winners = [c for c in campaigns.values() if not c["is_winner"]]

print(f"\n  Total campaigns analyzed: {len(campaigns)}")
print(f"  Winners (Closed Won + positive ROAS): {len(winners)}")
print(f"  Non-winners: {len(non_winners)}")

if winners:
    print(f"\n  All Winner campaigns (ranked by True ROAS):")
    for c in winners:
        budget_note = "BUDGET-CONSTRAINED" if c["search_budget_lost"] > 10 else ("slightly constrained" if c["search_budget_lost"] > 5 else "not constrained")
        print(
            f"    - {c['name']:<48} ROAS: {c['true_roas']:>7.2f}x  "
            f"CW Rev: ${c['closed_won_value']:>12,.2f}  "
            f"Budget: ${c['daily_budget']:,.2f}/day  "
            f"IS: {c['search_imp_share']:.0f}%  "
            f"Budget Lost IS: {c['search_budget_lost']:.1f}% ({budget_note})"
        )

# Specific validation for Boom Lifts and Excavator US
print(f"\n  {'=' * 80}")
print(f"  VALIDATION: Boom Lifts US & Excavator US as Weekend Test Candidates")
print(f"  {'=' * 80}")
for c in target_campaigns:
    name_lower = c["name"].lower()
    label = "BOOM LIFTS US" if "boom" in name_lower else "EXCAVATOR US"
    print(f"\n  [{label}] {c['name']}:")
    if c["is_winner"]:
        print(f"    STATUS: VALIDATED as winner")
        print(f"    True ROAS:            {c['true_roas']:.2f}x")
        print(f"    Closed Won Revenue:   ${c['closed_won_value']:,.2f} over 90 days")
        print(f"    Daily Budget:         ${c['daily_budget']:,.2f}")
        print(f"    Search IS:            {c['search_imp_share']:.1f}%")
        print(f"    Budget Lost IS:       {c['search_budget_lost']:.1f}%")
        if c["search_budget_lost"] > 10:
            print(f"    VERDICT: STRONG candidate. Campaign IS budget-constrained ({c['search_budget_lost']:.0f}% lost to budget).")
            print(f"             Increasing weekend budget should directly capture additional impressions and conversions.")
        elif c["search_budget_lost"] > 5:
            print(f"    VERDICT: MODERATE candidate. Slightly budget-constrained ({c['search_budget_lost']:.0f}% lost to budget).")
            print(f"             Some room for growth with increased weekend budget.")
        else:
            print(f"    VERDICT: CAUTION. Not significantly budget-constrained ({c['search_budget_lost']:.0f}% lost to budget).")
            print(f"             Weekend budget increase alone may not drive significant incremental volume.")
            print(f"             Consider also adjusting bids or broadening targeting.")
    else:
        print(f"    STATUS: NOT VALIDATED as winner")
        if c["conversions"] > 0:
            print(f"    Has {c['conversions']:.1f} conversions but no Closed Won Deals or zero ROAS.")
        else:
            print(f"    No conversions in the period.")
        print(f"    VERDICT: WEAK candidate for weekend test. Consider alternatives.")

# Overall recommendation
print(f"\n  {'─' * 80}")
print(f"  OVERALL RECOMMENDATION:")
print(f"  {'─' * 80}")
if target_campaigns:
    valid_targets = [c for c in target_campaigns if c["is_winner"]]
    if len(valid_targets) == 2:
        print(f"  Both Boom Lifts US and Excavator US are validated winners.")
        best = max(valid_targets, key=lambda x: x["true_roas"])
        print(f"  Strongest pick by ROAS: {best['name']} ({best['true_roas']:.2f}x)")
        most_constrained = max(valid_targets, key=lambda x: x["search_budget_lost"])
        print(f"  Most budget-constrained (biggest weekend upside): {most_constrained['name']} ({most_constrained['search_budget_lost']:.1f}% budget lost IS)")
    elif len(valid_targets) == 1:
        v = valid_targets[0]
        nv = [c for c in target_campaigns if not c["is_winner"]][0] if len(target_campaigns) > 1 else None
        print(f"  Only {v['name']} is validated. Consider it as the primary weekend test candidate.")
        if nv:
            print(f"  {nv['name']} is NOT validated - look for a better second candidate from the winner list above.")
    else:
        print(f"  NEITHER Boom Lifts US nor Excavator US are validated winners.")
        print(f"  Review the full winner list above for better weekend test candidates.")

print("\n" + "=" * 130)
print("END OF ANALYSIS")
print("=" * 130)
