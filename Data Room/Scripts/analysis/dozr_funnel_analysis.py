#!/usr/bin/env python3
"""
DOZR 30-Day Funnel Analysis
Separates data by: ALL campaigns, tROAS campaigns only, and OTHER campaigns
"""

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from collections import defaultdict
import sys

# Configuration
CONFIG_FILE = "/Users/vinuraabeysundara/google-ads.yaml"
CUSTOMER_ID = "8531896842"

# The 3 tROAS campaigns to analyze separately
TROAS_CAMPAIGNS = [
    "Search-Demand-Boom-Lifts",
    "Search-Forklift-Core-Geos-US",
    "DSA-AllPages-Tier1-New-US-2"
]

def format_currency(amount):
    """Format as currency"""
    return f"${amount:,.2f}"

def format_number(num):
    """Format number with commas"""
    if isinstance(num, float):
        return f"{num:,.2f}"
    return f"{num:,}"

def format_percentage(num):
    """Format as percentage"""
    return f"{num:.2f}%"

def print_separator(char="=", length=90):
    print(char * length)

def print_header(title):
    print_separator()
    print(f"  {title}")
    print_separator()

def main():
    # Initialize the Google Ads client
    print("Initializing Google Ads client...")
    client = GoogleAdsClient.load_from_storage(CONFIG_FILE)
    ga_service = client.get_service("GoogleAdsService")
    
    # Query 1: Account-level conversion data
    print("Fetching account-level conversion data...")
    account_query = """
        SELECT
          segments.conversion_action_name,
          metrics.conversions,
          metrics.conversions_value
        FROM customer
        WHERE segments.date DURING LAST_30_DAYS
    """
    
    account_conversions = defaultdict(lambda: {"conversions": 0, "value": 0})
    
    try:
        response = ga_service.search(customer_id=CUSTOMER_ID, query=account_query)
        for row in response:
            action_name = row.segments.conversion_action_name
            account_conversions[action_name]["conversions"] += row.metrics.conversions
            account_conversions[action_name]["value"] += row.metrics.conversions_value
    except GoogleAdsException as ex:
        print(f"Account query failed: {ex}")
        sys.exit(1)
    
    # Query 2: Campaign-level conversion data (separate from metrics)
    print("Fetching campaign-level conversion data...")
    campaign_conversion_query = """
        SELECT
          campaign.id,
          campaign.name,
          campaign.status,
          campaign.bidding_strategy_type,
          segments.conversion_action_name,
          metrics.conversions,
          metrics.conversions_value
        FROM campaign
        WHERE segments.date DURING LAST_30_DAYS
          AND campaign.status = 'ENABLED'
    """
    
    # Data structures
    campaign_data = {}  # campaign_id -> {name, status, bidding_strategy}
    campaign_conversions = defaultdict(lambda: defaultdict(lambda: {"conversions": 0, "value": 0}))
    
    try:
        response = ga_service.search(customer_id=CUSTOMER_ID, query=campaign_conversion_query)
        for row in response:
            campaign_id = row.campaign.id
            campaign_name = row.campaign.name
            action_name = row.segments.conversion_action_name
            
            # Store campaign info
            if campaign_id not in campaign_data:
                campaign_data[campaign_id] = {
                    "name": campaign_name,
                    "status": row.campaign.status.name,
                    "bidding_strategy": row.campaign.bidding_strategy_type.name
                }
            
            # Aggregate conversions by campaign and action
            campaign_conversions[campaign_id][action_name]["conversions"] += row.metrics.conversions
            campaign_conversions[campaign_id][action_name]["value"] += row.metrics.conversions_value
    except GoogleAdsException as ex:
        print(f"Campaign conversion query failed: {ex}")
        sys.exit(1)
    
    # Query 3: Campaign-level metrics (cost, clicks, impressions) - separate query
    print("Fetching campaign-level metrics...")
    campaign_metrics_query = """
        SELECT
          campaign.id,
          campaign.name,
          metrics.cost_micros,
          metrics.clicks,
          metrics.impressions
        FROM campaign
        WHERE segments.date DURING LAST_30_DAYS
          AND campaign.status = 'ENABLED'
    """
    
    campaign_metrics = defaultdict(lambda: {"cost": 0, "clicks": 0, "impressions": 0})
    
    try:
        response = ga_service.search(customer_id=CUSTOMER_ID, query=campaign_metrics_query)
        for row in response:
            campaign_id = row.campaign.id
            campaign_metrics[campaign_id]["cost"] += row.metrics.cost_micros / 1_000_000
            campaign_metrics[campaign_id]["clicks"] += row.metrics.clicks
            campaign_metrics[campaign_id]["impressions"] += row.metrics.impressions
    except GoogleAdsException as ex:
        print(f"Campaign metrics query failed: {ex}")
        sys.exit(1)
    
    # Separate campaigns into tROAS and OTHER
    troas_campaign_ids = []
    other_campaign_ids = []
    
    for campaign_id, data in campaign_data.items():
        if data["name"] in TROAS_CAMPAIGNS:
            troas_campaign_ids.append(campaign_id)
        else:
            other_campaign_ids.append(campaign_id)
    
    # DOZR-specific conversion action categorization
    def categorize_action(action_name):
        """Categorize DOZR conversion actions into funnel stages"""
        action_lower = action_name.lower()
        
        # Phone Calls: "Phone Call", "Calls from ads"
        if action_name == "Phone Call" or action_name == "Calls from ads":
            return "phone_calls"
        
        # Qualified Calls: "AdWords Qualified Calls May 2025"
        if "qualified" in action_lower:
            return "qualified_calls"
        
        # Quote Requests: "AdWords Caller requested a quote May 2025"
        if "quote" in action_lower or "requested a quote" in action_lower:
            return "quote_requests"
        
        # Closed Won: "Closed Won Deals From AdWords Caller May 2025", "Purchase"
        if "closed won" in action_lower or action_name == "Purchase (Google Analytics event purchase)":
            return "closed_won"
        
        return "other"
    
    def categorize_conversions(conversions_dict):
        """Categorize conversions into funnel stages"""
        result = {
            "phone_calls": {"conversions": 0, "value": 0},
            "qualified_calls": {"conversions": 0, "value": 0},
            "quote_requests": {"conversions": 0, "value": 0},
            "closed_won": {"conversions": 0, "value": 0},
            "other": {"conversions": 0, "value": 0},
            "all_actions": {}
        }
        
        for action_name, data in conversions_dict.items():
            result["all_actions"][action_name] = data.copy()
            category = categorize_action(action_name)
            result[category]["conversions"] += data["conversions"]
            result[category]["value"] += data["value"]
        
        return result
    
    def aggregate_campaign_group(campaign_ids):
        """Aggregate metrics for a group of campaigns"""
        total_conversions = defaultdict(lambda: {"conversions": 0, "value": 0})
        total_cost = 0
        total_clicks = 0
        total_impressions = 0
        
        for cid in campaign_ids:
            for action_name, data in campaign_conversions[cid].items():
                total_conversions[action_name]["conversions"] += data["conversions"]
                total_conversions[action_name]["value"] += data["value"]
            
            total_cost += campaign_metrics[cid]["cost"]
            total_clicks += campaign_metrics[cid]["clicks"]
            total_impressions += campaign_metrics[cid]["impressions"]
        
        return {
            "conversions": dict(total_conversions),
            "cost": total_cost,
            "clicks": total_clicks,
            "impressions": total_impressions
        }
    
    # Aggregate data for each group
    all_campaigns_data = aggregate_campaign_group(list(campaign_data.keys()))
    troas_data = aggregate_campaign_group(troas_campaign_ids)
    other_data = aggregate_campaign_group(other_campaign_ids)
    
    # Print Results
    print("\n")
    print_separator("=", 90)
    print("  DOZR 30-DAY FUNNEL ANALYSIS")
    print_separator("=", 90)
    print(f"Customer ID: {CUSTOMER_ID}")
    print(f"Analysis Period: Last 30 Days")
    print(f"Total Enabled Campaigns: {len(campaign_data)}")
    print(f"tROAS Campaigns Found: {len(troas_campaign_ids)}")
    print(f"Other Campaigns: {len(other_campaign_ids)}")
    
    # List all campaigns found
    print("\n")
    print_separator("=", 90)
    print("  CAMPAIGN INVENTORY")
    print_separator("=", 90)
    print("\ntROAS Campaigns (MAXIMIZE_CONVERSION_VALUE with Target ROAS):")
    for cid in troas_campaign_ids:
        cost = campaign_metrics[cid]["cost"]
        print(f"  - {campaign_data[cid]['name']}")
        print(f"    ID: {cid} | Strategy: {campaign_data[cid]['bidding_strategy']} | Cost: {format_currency(cost)}")
    
    print("\nOther Enabled Campaigns:")
    for cid in other_campaign_ids:
        cost = campaign_metrics[cid]["cost"]
        print(f"  - {campaign_data[cid]['name']}")
        print(f"    Strategy: {campaign_data[cid]['bidding_strategy']} | Cost: {format_currency(cost)}")
    
    # Show all conversion actions found with categorization
    print("\n")
    print_separator("=", 90)
    print("  ALL CONVERSION ACTIONS FOUND (Account Level)")
    print_separator("=", 90)
    print(f"{'Conversion Action':<55} {'Category':<15} {'Conversions':>12} {'Value':>15}")
    print("-" * 90)
    for action_name, data in sorted(account_conversions.items(), key=lambda x: x[1]["conversions"], reverse=True):
        category = categorize_action(action_name)
        print(f"{action_name:<55} {category:<15} {format_number(data['conversions']):>12} {format_currency(data['value']):>15}")
    
    # ==================== Analysis 1: ALL Enabled Campaigns ====================
    print("\n")
    print_separator("=", 90)
    print("  ANALYSIS 1: ALL ENABLED CAMPAIGNS (30 Days)")
    print_separator("=", 90)
    
    all_categorized = categorize_conversions(all_campaigns_data["conversions"])
    total_value = sum(d["value"] for d in all_categorized["all_actions"].values())
    all_cost = all_campaigns_data["cost"]
    
    print(f"\n{'Conversion Action':<55} {'Conversions':>15} {'Value':>15}")
    print("-" * 90)
    for action_name, data in sorted(all_categorized["all_actions"].items(), key=lambda x: x[1]["conversions"], reverse=True):
        print(f"{action_name:<55} {format_number(data['conversions']):>15} {format_currency(data['value']):>15}")
    
    pc = all_categorized['phone_calls']['conversions']
    qc = all_categorized['qualified_calls']['conversions']
    qr = all_categorized['quote_requests']['conversions']
    cw = all_categorized['closed_won']['conversions']
    
    print("\n--- FUNNEL SUMMARY (ALL CAMPAIGNS) ---")
    print(f"{'Stage':<30} {'Count':>15} {'Value':>20}")
    print("-" * 65)
    print(f"{'Phone Calls':<30} {format_number(pc):>15} {format_currency(all_categorized['phone_calls']['value']):>20}")
    print(f"{'Qualified Calls':<30} {format_number(qc):>15} {format_currency(all_categorized['qualified_calls']['value']):>20}")
    print(f"{'Quote Requests':<30} {format_number(qr):>15} {format_currency(all_categorized['quote_requests']['value']):>20}")
    print(f"{'Closed Won Deals':<30} {format_number(cw):>15} {format_currency(all_categorized['closed_won']['value']):>20}")
    
    print(f"\n--- PERFORMANCE METRICS (ALL CAMPAIGNS) ---")
    print(f"Total Cost:              {format_currency(all_cost)}")
    print(f"Total Conversion Value:  {format_currency(total_value)}")
    if all_cost > 0:
        print(f"ROAS:                    {format_number(total_value / all_cost)}x")
    
    print(f"\n--- CONVERSION RATES (ALL CAMPAIGNS) ---")
    if pc > 0:
        print(f"Phone Call -> Qualified Call: {format_percentage(qc/pc*100)} ({format_number(qc)} / {format_number(pc)})")
        print(f"Phone Call -> Quote Request:  {format_percentage(qr/pc*100)} ({format_number(qr)} / {format_number(pc)})")
        print(f"Phone Call -> Closed Won:     {format_percentage(cw/pc*100)} ({format_number(cw)} / {format_number(pc)})")
    if qc > 0:
        print(f"Qualified Call -> Closed Won: {format_percentage(cw/qc*100)} ({format_number(cw)} / {format_number(qc)})")
    if qr > 0:
        print(f"Quote Request -> Closed Won:  {format_percentage(cw/qr*100)} ({format_number(cw)} / {format_number(qr)})")
    
    # ==================== Analysis 2: tROAS Campaigns Only ====================
    print("\n")
    print_separator("=", 90)
    print("  ANALYSIS 2: tROAS CAMPAIGNS ONLY (30 Days)")
    print_separator("=", 90)
    print("Campaigns included:")
    print("  1. Search-Demand-Boom-Lifts")
    print("  2. Search-Forklift-Core-Geos-US")
    print("  3. DSA-AllPages-Tier1-New-US-2")
    
    troas_categorized = categorize_conversions(troas_data["conversions"])
    troas_total_value = sum(d["value"] for d in troas_categorized["all_actions"].values())
    troas_cost = troas_data["cost"]
    
    print(f"\n{'Conversion Action':<55} {'Conversions':>15} {'Value':>15}")
    print("-" * 90)
    for action_name, data in sorted(troas_categorized["all_actions"].items(), key=lambda x: x[1]["conversions"], reverse=True):
        print(f"{action_name:<55} {format_number(data['conversions']):>15} {format_currency(data['value']):>15}")
    
    t_pc = troas_categorized['phone_calls']['conversions']
    t_qc = troas_categorized['qualified_calls']['conversions']
    t_qr = troas_categorized['quote_requests']['conversions']
    t_cw = troas_categorized['closed_won']['conversions']
    
    print("\n--- FUNNEL SUMMARY (tROAS CAMPAIGNS) ---")
    print(f"{'Stage':<30} {'Count':>15} {'Value':>20}")
    print("-" * 65)
    print(f"{'Phone Calls':<30} {format_number(t_pc):>15} {format_currency(troas_categorized['phone_calls']['value']):>20}")
    print(f"{'Qualified Calls':<30} {format_number(t_qc):>15} {format_currency(troas_categorized['qualified_calls']['value']):>20}")
    print(f"{'Quote Requests':<30} {format_number(t_qr):>15} {format_currency(troas_categorized['quote_requests']['value']):>20}")
    print(f"{'Closed Won Deals':<30} {format_number(t_cw):>15} {format_currency(troas_categorized['closed_won']['value']):>20}")
    
    print(f"\n--- PERFORMANCE METRICS (tROAS CAMPAIGNS) ---")
    print(f"Total Cost:              {format_currency(troas_cost)}")
    print(f"Total Conversion Value:  {format_currency(troas_total_value)}")
    if troas_cost > 0:
        print(f"ROAS:                    {format_number(troas_total_value / troas_cost)}x")
    
    print(f"\n--- CONVERSION RATES (tROAS CAMPAIGNS) ---")
    if t_pc > 0:
        print(f"Phone Call -> Qualified Call: {format_percentage(t_qc/t_pc*100)} ({format_number(t_qc)} / {format_number(t_pc)})")
        print(f"Phone Call -> Quote Request:  {format_percentage(t_qr/t_pc*100)} ({format_number(t_qr)} / {format_number(t_pc)})")
        print(f"Phone Call -> Closed Won:     {format_percentage(t_cw/t_pc*100)} ({format_number(t_cw)} / {format_number(t_pc)})")
    if t_qc > 0:
        print(f"Qualified Call -> Closed Won: {format_percentage(t_cw/t_qc*100)} ({format_number(t_cw)} / {format_number(t_qc)})")
    if t_qr > 0:
        print(f"Quote Request -> Closed Won:  {format_percentage(t_cw/t_qr*100)} ({format_number(t_cw)} / {format_number(t_qr)})")
    
    # Per-campaign breakdown for tROAS
    print("\n--- PER-CAMPAIGN BREAKDOWN (tROAS) ---")
    for cid in troas_campaign_ids:
        camp_name = campaign_data[cid]["name"]
        camp_cat = categorize_conversions(campaign_conversions[cid])
        camp_value = sum(d["value"] for d in camp_cat["all_actions"].values())
        camp_cost = campaign_metrics[cid]["cost"]
        
        c_pc = camp_cat['phone_calls']['conversions']
        c_qc = camp_cat['qualified_calls']['conversions']
        c_qr = camp_cat['quote_requests']['conversions']
        c_cw = camp_cat['closed_won']['conversions']
        
        print(f"\n  {camp_name}")
        print(f"  {'='*70}")
        print(f"    Phone Calls:     {format_number(c_pc):>10}")
        print(f"    Qualified Calls: {format_number(c_qc):>10}")
        print(f"    Quote Requests:  {format_number(c_qr):>10}")
        print(f"    Closed Won:      {format_number(c_cw):>10}")
        print(f"    Cost:            {format_currency(camp_cost):>10}")
        print(f"    Value:           {format_currency(camp_value):>10}")
        if camp_cost > 0:
            print(f"    ROAS:            {format_number(camp_value / camp_cost)}x")
        if c_pc > 0:
            print(f"    Phone->Closed:   {format_percentage(c_cw/c_pc*100)}")
        if c_qr > 0:
            print(f"    Quote->Closed:   {format_percentage(c_cw/c_qr*100)}")
    
    # ==================== Analysis 3: OTHER Campaigns ====================
    print("\n")
    print_separator("=", 90)
    print("  ANALYSIS 3: OTHER CAMPAIGNS (Excluding tROAS) (30 Days)")
    print_separator("=", 90)
    
    other_categorized = categorize_conversions(other_data["conversions"])
    other_total_value = sum(d["value"] for d in other_categorized["all_actions"].values())
    other_cost = other_data["cost"]
    
    print(f"\n{'Conversion Action':<55} {'Conversions':>15} {'Value':>15}")
    print("-" * 90)
    for action_name, data in sorted(other_categorized["all_actions"].items(), key=lambda x: x[1]["conversions"], reverse=True):
        print(f"{action_name:<55} {format_number(data['conversions']):>15} {format_currency(data['value']):>15}")
    
    o_pc = other_categorized['phone_calls']['conversions']
    o_qc = other_categorized['qualified_calls']['conversions']
    o_qr = other_categorized['quote_requests']['conversions']
    o_cw = other_categorized['closed_won']['conversions']
    
    print("\n--- FUNNEL SUMMARY (OTHER CAMPAIGNS) ---")
    print(f"{'Stage':<30} {'Count':>15} {'Value':>20}")
    print("-" * 65)
    print(f"{'Phone Calls':<30} {format_number(o_pc):>15} {format_currency(other_categorized['phone_calls']['value']):>20}")
    print(f"{'Qualified Calls':<30} {format_number(o_qc):>15} {format_currency(other_categorized['qualified_calls']['value']):>20}")
    print(f"{'Quote Requests':<30} {format_number(o_qr):>15} {format_currency(other_categorized['quote_requests']['value']):>20}")
    print(f"{'Closed Won Deals':<30} {format_number(o_cw):>15} {format_currency(other_categorized['closed_won']['value']):>20}")
    
    print(f"\n--- PERFORMANCE METRICS (OTHER CAMPAIGNS) ---")
    print(f"Total Cost:              {format_currency(other_cost)}")
    print(f"Total Conversion Value:  {format_currency(other_total_value)}")
    if other_cost > 0:
        print(f"ROAS:                    {format_number(other_total_value / other_cost)}x")
    
    print(f"\n--- CONVERSION RATES (OTHER CAMPAIGNS) ---")
    if o_pc > 0:
        print(f"Phone Call -> Qualified Call: {format_percentage(o_qc/o_pc*100)} ({format_number(o_qc)} / {format_number(o_pc)})")
        print(f"Phone Call -> Quote Request:  {format_percentage(o_qr/o_pc*100)} ({format_number(o_qr)} / {format_number(o_pc)})")
        print(f"Phone Call -> Closed Won:     {format_percentage(o_cw/o_pc*100)} ({format_number(o_cw)} / {format_number(o_pc)})")
    if o_qc > 0:
        print(f"Qualified Call -> Closed Won: {format_percentage(o_cw/o_qc*100)} ({format_number(o_cw)} / {format_number(o_qc)})")
    if o_qr > 0:
        print(f"Quote Request -> Closed Won:  {format_percentage(o_cw/o_qr*100)} ({format_number(o_cw)} / {format_number(o_qr)})")
    
    # Per-campaign breakdown for OTHER
    print("\n--- PER-CAMPAIGN BREAKDOWN (Other Campaigns) ---")
    for cid in sorted(other_campaign_ids, key=lambda x: campaign_metrics[x]["cost"], reverse=True):
        camp_name = campaign_data[cid]["name"]
        camp_cat = categorize_conversions(campaign_conversions[cid])
        camp_value = sum(d["value"] for d in camp_cat["all_actions"].values())
        camp_cost = campaign_metrics[cid]["cost"]
        
        c_pc = camp_cat['phone_calls']['conversions']
        c_qc = camp_cat['qualified_calls']['conversions']
        c_qr = camp_cat['quote_requests']['conversions']
        c_cw = camp_cat['closed_won']['conversions']
        
        print(f"\n  {camp_name}")
        print(f"  {'='*70}")
        print(f"    Phone Calls:     {format_number(c_pc):>10}")
        print(f"    Qualified Calls: {format_number(c_qc):>10}")
        print(f"    Quote Requests:  {format_number(c_qr):>10}")
        print(f"    Closed Won:      {format_number(c_cw):>10}")
        print(f"    Cost:            {format_currency(camp_cost):>10}")
        print(f"    Value:           {format_currency(camp_value):>10}")
        if camp_cost > 0:
            print(f"    ROAS:            {format_number(camp_value / camp_cost)}x")
        if c_pc > 0:
            print(f"    Phone->Closed:   {format_percentage(c_cw/c_pc*100)}")
        if c_qr > 0:
            print(f"    Quote->Closed:   {format_percentage(c_cw/c_qr*100)}")
    
    # ==================== Comparison: tROAS vs Others ====================
    print("\n")
    print_separator("=", 90)
    print("  COMPARISON: tROAS vs OTHER CAMPAIGNS")
    print_separator("=", 90)
    
    total_all_conversions = sum(d["conversions"] for d in all_categorized["all_actions"].values())
    total_troas_conversions = sum(d["conversions"] for d in troas_categorized["all_actions"].values())
    total_other_conversions = sum(d["conversions"] for d in other_categorized["all_actions"].values())
    
    print("\n--- SHARE OF METRICS ---")
    print(f"{'Metric':<30} {'tROAS':>25} {'Other':>25}")
    print("-" * 80)
    
    if total_all_conversions > 0:
        print(f"{'Total Conversions':<30} {format_percentage(total_troas_conversions/total_all_conversions*100) + ' (' + format_number(total_troas_conversions) + ')':>25} {format_percentage(total_other_conversions/total_all_conversions*100) + ' (' + format_number(total_other_conversions) + ')':>25}")
    
    if pc > 0:
        print(f"{'Phone Calls':<30} {format_percentage(t_pc/pc*100) + ' (' + format_number(t_pc) + ')':>25} {format_percentage(o_pc/pc*100) + ' (' + format_number(o_pc) + ')':>25}")
    
    if qc > 0:
        print(f"{'Qualified Calls':<30} {format_percentage(t_qc/qc*100) + ' (' + format_number(t_qc) + ')':>25} {format_percentage(o_qc/qc*100) + ' (' + format_number(o_qc) + ')':>25}")
    
    if qr > 0:
        print(f"{'Quote Requests':<30} {format_percentage(t_qr/qr*100) + ' (' + format_number(t_qr) + ')':>25} {format_percentage(o_qr/qr*100) + ' (' + format_number(o_qr) + ')':>25}")
    
    if cw > 0:
        print(f"{'Closed Won Deals':<30} {format_percentage(t_cw/cw*100) + ' (' + format_number(t_cw) + ')':>25} {format_percentage(o_cw/cw*100) + ' (' + format_number(o_cw) + ')':>25}")
    
    if all_cost > 0:
        print(f"{'Spend':<30} {format_percentage(troas_cost/all_cost*100) + ' (' + format_currency(troas_cost) + ')':>25} {format_percentage(other_cost/all_cost*100) + ' (' + format_currency(other_cost) + ')':>25}")
    
    if total_value > 0:
        print(f"{'Value':<30} {format_percentage(troas_total_value/total_value*100) + ' (' + format_currency(troas_total_value) + ')':>25} {format_percentage(other_total_value/total_value*100) + ' (' + format_currency(other_total_value) + ')':>25}")
    
    # Side-by-side comparison table
    print("\n--- SIDE-BY-SIDE PERFORMANCE COMPARISON ---")
    print(f"{'Metric':<25} {'tROAS':>20} {'Other':>20} {'ALL':>20}")
    print("-" * 85)
    print(f"{'Phone Calls':<25} {format_number(t_pc):>20} {format_number(o_pc):>20} {format_number(pc):>20}")
    print(f"{'Qualified Calls':<25} {format_number(t_qc):>20} {format_number(o_qc):>20} {format_number(qc):>20}")
    print(f"{'Quote Requests':<25} {format_number(t_qr):>20} {format_number(o_qr):>20} {format_number(qr):>20}")
    print(f"{'Closed Won':<25} {format_number(t_cw):>20} {format_number(o_cw):>20} {format_number(cw):>20}")
    print(f"{'Cost':<25} {format_currency(troas_cost):>20} {format_currency(other_cost):>20} {format_currency(all_cost):>20}")
    print(f"{'Value':<25} {format_currency(troas_total_value):>20} {format_currency(other_total_value):>20} {format_currency(total_value):>20}")
    
    troas_roas = troas_total_value / troas_cost if troas_cost > 0 else 0
    other_roas = other_total_value / other_cost if other_cost > 0 else 0
    all_roas = total_value / all_cost if all_cost > 0 else 0
    
    print(f"{'ROAS':<25} {format_number(troas_roas) + 'x':>20} {format_number(other_roas) + 'x':>20} {format_number(all_roas) + 'x':>20}")
    
    # Conversion rate comparison
    print("\n--- CONVERSION RATE COMPARISON ---")
    print(f"{'Rate':<30} {'tROAS':>20} {'Other':>20} {'ALL':>20}")
    print("-" * 90)
    
    t_phone_to_close = (t_cw/t_pc*100) if t_pc > 0 else 0
    o_phone_to_close = (o_cw/o_pc*100) if o_pc > 0 else 0
    a_phone_to_close = (cw/pc*100) if pc > 0 else 0
    print(f"{'Phone -> Closed Won':<30} {format_percentage(t_phone_to_close):>20} {format_percentage(o_phone_to_close):>20} {format_percentage(a_phone_to_close):>20}")
    
    t_quote_to_close = (t_cw/t_qr*100) if t_qr > 0 else 0
    o_quote_to_close = (o_cw/o_qr*100) if o_qr > 0 else 0
    a_quote_to_close = (cw/qr*100) if qr > 0 else 0
    print(f"{'Quote -> Closed Won':<30} {format_percentage(t_quote_to_close):>20} {format_percentage(o_quote_to_close):>20} {format_percentage(a_quote_to_close):>20}")
    
    t_qual_to_close = (t_cw/t_qc*100) if t_qc > 0 else 0
    o_qual_to_close = (o_cw/o_qc*100) if o_qc > 0 else 0
    a_qual_to_close = (cw/qc*100) if qc > 0 else 0
    print(f"{'Qualified -> Closed Won':<30} {format_percentage(t_qual_to_close):>20} {format_percentage(o_qual_to_close):>20} {format_percentage(a_qual_to_close):>20}")
    
    # ==================== Recommended Proxy Values ====================
    print("\n")
    print_separator("=", 90)
    print("  RECOMMENDED PROXY VALUES (Based on 30-Day Data)")
    print_separator("=", 90)
    
    # Calculate value per conversion type
    print("\n--- VALUE PER CONVERSION TYPE (from Google Ads) ---")
    print(f"{'Conversion Action':<55} {'Value/Conv':>15}")
    print("-" * 70)
    for action_name, data in sorted(account_conversions.items(), key=lambda x: x[1]["conversions"], reverse=True):
        if data["conversions"] > 0:
            value_per = data["value"] / data["conversions"]
            print(f"{action_name:<55} {format_currency(value_per):>15}")
    
    # Calculate implied values based on funnel math
    print("\n--- IMPLIED PROXY VALUES (Based on Funnel Progression) ---")
    
    # Average Closed Won value
    if cw > 0:
        avg_closed_won_value = all_categorized['closed_won']['value'] / cw
        print(f"\nAverage Closed Won Deal Value: {format_currency(avg_closed_won_value)}")
        
        print("\nImplied values based on close rates:")
        
        if pc > 0:
            phone_to_close_rate = cw / pc
            implied_phone_value = avg_closed_won_value * phone_to_close_rate
            print(f"  Phone Call Value:     {format_currency(implied_phone_value)}")
            print(f"    (Based on {format_percentage(phone_to_close_rate*100)} close rate)")
        
        if qc > 0:
            qual_to_close_rate = cw / qc
            implied_qual_value = avg_closed_won_value * qual_to_close_rate
            print(f"  Qualified Call Value: {format_currency(implied_qual_value)}")
            print(f"    (Based on {format_percentage(qual_to_close_rate*100)} close rate)")
        
        if qr > 0:
            quote_to_close_rate = cw / qr
            implied_quote_value = avg_closed_won_value * quote_to_close_rate
            print(f"  Quote Request Value:  {format_currency(implied_quote_value)}")
            print(f"    (Based on {format_percentage(quote_to_close_rate*100)} close rate)")
    
    # ==================== Funnel Math Verification ====================
    print("\n")
    print_separator("=", 90)
    print("  FUNNEL MATH VERIFICATION")
    print_separator("=", 90)
    
    print("\n--- VERIFICATION: ALL CAMPAIGNS ---")
    print(f"Phone Calls:             {format_number(pc)}")
    print(f"Qualified Calls:         {format_number(qc)}")
    print(f"Quote Requests:          {format_number(qr)}")
    print(f"Closed Won Deals:        {format_number(cw)}")
    print(f"\nProgression Rates:")
    if pc > 0:
        print(f"  Phone -> Qualified:    {format_percentage(qc/pc*100)}")
        print(f"  Phone -> Quote:        {format_percentage(qr/pc*100)}")
        print(f"  Phone -> Closed Won:   {format_percentage(cw/pc*100)}")
    if qc > 0:
        print(f"  Qualified -> Closed:   {format_percentage(cw/qc*100)}")
    if qr > 0:
        print(f"  Quote -> Closed:       {format_percentage(cw/qr*100)}")
    
    print("\n--- VERIFICATION: tROAS CAMPAIGNS ---")
    print(f"Phone Calls:             {format_number(t_pc)}")
    print(f"Qualified Calls:         {format_number(t_qc)}")
    print(f"Quote Requests:          {format_number(t_qr)}")
    print(f"Closed Won Deals:        {format_number(t_cw)}")
    print(f"\nProgression Rates:")
    if t_pc > 0:
        print(f"  Phone -> Qualified:    {format_percentage(t_qc/t_pc*100)}")
        print(f"  Phone -> Quote:        {format_percentage(t_qr/t_pc*100)}")
        print(f"  Phone -> Closed Won:   {format_percentage(t_cw/t_pc*100)}")
    if t_qc > 0:
        print(f"  Qualified -> Closed:   {format_percentage(t_cw/t_qc*100)}")
    if t_qr > 0:
        print(f"  Quote -> Closed:       {format_percentage(t_cw/t_qr*100)}")
    
    print("\n--- VERIFICATION: OTHER CAMPAIGNS ---")
    print(f"Phone Calls:             {format_number(o_pc)}")
    print(f"Qualified Calls:         {format_number(o_qc)}")
    print(f"Quote Requests:          {format_number(o_qr)}")
    print(f"Closed Won Deals:        {format_number(o_cw)}")
    print(f"\nProgression Rates:")
    if o_pc > 0:
        print(f"  Phone -> Qualified:    {format_percentage(o_qc/o_pc*100)}")
        print(f"  Phone -> Quote:        {format_percentage(o_qr/o_pc*100)}")
        print(f"  Phone -> Closed Won:   {format_percentage(o_cw/o_pc*100)}")
    if o_qc > 0:
        print(f"  Qualified -> Closed:   {format_percentage(o_cw/o_qc*100)}")
    if o_qr > 0:
        print(f"  Quote -> Closed:       {format_percentage(o_cw/o_qr*100)}")
    
    print("\n")
    print_separator("=", 90)
    print("  END OF ANALYSIS")
    print_separator("=", 90)
    print("\n")

if __name__ == "__main__":
    main()
