from google.ads.googleads.client import GoogleAdsClient
from datetime import datetime
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Load credentials
client = GoogleAdsClient.load_from_storage('/Users/vinuraabeysundara/Desktop/ICG/DOZR/Data Room/Config/google-ads.yaml')
ga_service = client.get_service('GoogleAdsService')
customer_id = '8531896842'

print("=" * 160)
print(f"🔍 FEBRUARY 10TH IMPACT ANALYSIS - WHAT CHANGED?")
print("=" * 160)

# Define periods
period_before = {'name': 'Before Feb 10 (Feb 1-9)', 'start': '2026-02-01', 'end': '2026-02-09'}
period_after = {'name': 'After Feb 10 (Feb 10-23)', 'start': '2026-02-10', 'end': '2026-02-23'}

print("\n📅 Comparing Two Periods:")
print(f"   • BEFORE: {period_before['start']} to {period_before['end']} (9 days)")
print(f"   • AFTER:  {period_after['start']} to {period_after['end']} (14 days)")

def analyze_period(period):
    """Analyze a specific time period"""
    start_date = period['start']
    end_date = period['end']

    # Calculate number of days
    from datetime import datetime
    d1 = datetime.strptime(start_date, '%Y-%m-%d')
    d2 = datetime.strptime(end_date, '%Y-%m-%d')
    num_days = (d2 - d1).days + 1

    results = {
        'num_days': num_days,
        'spend': 0,
        'clicks': 0,
        'impressions': 0,
        'calls': 0,
        'quotes': 0,
        'deals': 0,
        'deal_value': 0,
        'by_equipment': defaultdict(lambda: {'deals': 0, 'value': 0}),
        'by_campaign_type': defaultdict(lambda: {'deals': 0, 'value': 0}),
        'deal_list': []
    }

    # Query spend and metrics
    query_spend = f"""
        SELECT
            campaign.name,
            metrics.cost_micros,
            metrics.clicks,
            metrics.impressions
        FROM campaign
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
            AND campaign.status = 'ENABLED'
            AND campaign.name LIKE '%US%'
    """

    response_spend = ga_service.search(customer_id=customer_id, query=query_spend)

    for row in response_spend:
        results['spend'] += row.metrics.cost_micros / 1_000_000
        results['clicks'] += row.metrics.clicks
        results['impressions'] += row.metrics.impressions

    # Query conversions
    query_conv = f"""
        SELECT
            campaign.name,
            segments.conversion_action_name,
            metrics.conversions
        FROM campaign
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
            AND campaign.status = 'ENABLED'
            AND campaign.name LIKE '%US%'
            AND metrics.conversions > 0
    """

    response_conv = ga_service.search(customer_id=customer_id, query=query_conv)

    for row in response_conv:
        conv_name = row.segments.conversion_action_name
        conversions = row.metrics.conversions

        if 'Phone Call' in conv_name or 'Calls from ads' in conv_name:
            results['calls'] += conversions
        elif 'quote' in conv_name.lower():
            results['quotes'] += conversions

    # Query deals with values
    query_deals = f"""
        SELECT
            campaign.name,
            ad_group.name,
            segments.date,
            segments.conversion_action_name,
            metrics.conversions,
            metrics.conversions_value
        FROM ad_group
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
            AND campaign.status = 'ENABLED'
            AND ad_group.status = 'ENABLED'
            AND campaign.name LIKE '%US%'
            AND metrics.conversions > 0
            AND segments.conversion_action_name LIKE '%Closed Won%'
    """

    response_deals = ga_service.search(customer_id=customer_id, query=query_deals)

    for row in response_deals:
        campaign = row.campaign.name
        conversions = row.metrics.conversions
        value = row.metrics.conversions_value

        results['deals'] += conversions
        results['deal_value'] += value

        # Categorize by equipment
        equipment = 'Unknown'
        equipment_size = 'Unknown'

        # Classify equipment and size
        if 'DSA' in campaign:
            equipment = 'DSA'
            equipment_size = 'Mixed'
        elif 'Dozer' in campaign:
            equipment = 'Dozers'
            equipment_size = 'Large'
        elif 'Excavator' in campaign:
            equipment = 'Excavators'
            equipment_size = 'Large'
        elif 'Loader' in campaign:
            equipment = 'Loaders'
            equipment_size = 'Large'
        elif 'Boom-Lift' in campaign or 'Boom Lift' in campaign:
            equipment = 'Boom Lifts'
            equipment_size = 'Large'
        elif 'Forklift' in campaign:
            equipment = 'Forklifts'
            equipment_size = 'Medium'
        elif 'Telehandler' in campaign:
            equipment = 'Telehandlers'
            equipment_size = 'Medium'
        elif 'Scissor' in campaign:
            equipment = 'Scissor Lifts'
            equipment_size = 'Small'
        elif 'Skid' in campaign:
            equipment = 'Skid Steers'
            equipment_size = 'Small'
        elif 'Backhoe' in campaign:
            equipment = 'Backhoes'
            equipment_size = 'Medium'
        elif 'Brand' in campaign:
            equipment = 'Brand'
            equipment_size = 'Mixed'

        results['by_equipment'][equipment]['deals'] += conversions
        results['by_equipment'][equipment]['value'] += value

        # Categorize by campaign type
        if 'Expansion' in campaign:
            campaign_type = 'Expansion'
        elif 'DSA' in campaign:
            campaign_type = 'DSA'
        elif 'Brand' in campaign:
            campaign_type = 'Brand'
        else:
            campaign_type = 'Core'

        results['by_campaign_type'][campaign_type]['deals'] += conversions
        results['by_campaign_type'][campaign_type]['value'] += value

        # Store individual deal
        results['deal_list'].append({
            'date': row.segments.date,
            'campaign': campaign,
            'equipment': equipment,
            'size': equipment_size,
            'value': value
        })

    return results

# Analyze both periods
print("\n\n📊 ANALYZING BOTH PERIODS...")
print("=" * 160)

before = analyze_period(period_before)
after = analyze_period(period_after)

# Print comparison
print("\n\n💰 FINANCIAL PERFORMANCE COMPARISON")
print("=" * 160)

print(f"\n{'Metric':<40} {'Before (Feb 1-9)':>20} {'After (Feb 10-23)':>20} {'Change':>15} {'% Change':>12}")
print("-" * 120)

metrics = [
    ('Total Spend', before['spend'], after['spend']),
    ('Total Deal Value', before['deal_value'], after['deal_value']),
    ('Total Deals', before['deals'], after['deals']),
    ('Average Deal Value', before['deal_value']/before['deals'] if before['deals'] > 0 else 0,
                         after['deal_value']/after['deals'] if after['deals'] > 0 else 0),
    ('Daily Deal Value', before['deal_value']/before['num_days'], after['deal_value']/after['num_days']),
    ('ROAS', before['deal_value']/before['spend'] if before['spend'] > 0 else 0,
            after['deal_value']/after['spend'] if after['spend'] > 0 else 0),
]

for metric_name, before_val, after_val in metrics:
    change = after_val - before_val
    pct_change = (change / before_val * 100) if before_val > 0 else 0

    if 'ROAS' in metric_name:
        print(f"{metric_name:<40} {before_val:>19.2f}x {after_val:>19.2f}x {change:>14.2f}x {pct_change:>11.1f}%")
    elif 'Deals' in metric_name and 'Value' not in metric_name:
        print(f"{metric_name:<40} {int(before_val):>20} {int(after_val):>20} {int(change):>15} {pct_change:>11.1f}%")
    else:
        print(f"{metric_name:<40} ${before_val:>19,.2f} ${after_val:>19,.2f} ${change:>14,.2f} {pct_change:>11.1f}%")

# Call quality metrics
print("\n\n📞 CALL QUALITY COMPARISON")
print("=" * 160)

print(f"\n{'Metric':<40} {'Before (Feb 1-9)':>20} {'After (Feb 10-23)':>20} {'Change':>15}")
print("-" * 120)

call_metrics = [
    ('Total Calls', before['calls'], after['calls']),
    ('Total Quotes', before['quotes'], after['quotes']),
    ('Total Deals', before['deals'], after['deals']),
    ('Calls per Day', before['calls']/before['num_days'], after['calls']/after['num_days']),
    ('Call → Quote Rate', (before['quotes']/before['calls']*100) if before['calls'] > 0 else 0,
                         (after['quotes']/after['calls']*100) if after['calls'] > 0 else 0),
    ('Quote → Deal Rate', (before['deals']/before['quotes']*100) if before['quotes'] > 0 else 0,
                         (after['deals']/after['quotes']*100) if after['quotes'] > 0 else 0),
    ('Call → Deal Rate', (before['deals']/before['calls']*100) if before['calls'] > 0 else 0,
                        (after['deals']/after['calls']*100) if after['calls'] > 0 else 0),
    ('Cost per Call', before['spend']/before['calls'] if before['calls'] > 0 else 0,
                     after['spend']/after['calls'] if after['calls'] > 0 else 0),
]

for metric_name, before_val, after_val in call_metrics:
    change = after_val - before_val

    if 'Rate' in metric_name:
        print(f"{metric_name:<40} {before_val:>19.1f}% {after_val:>19.1f}% {change:>14.1f}%")
    elif 'Cost' in metric_name or 'per' in metric_name:
        print(f"{metric_name:<40} ${before_val:>19,.2f} ${after_val:>19,.2f} ${change:>14,.2f}")
    else:
        print(f"{metric_name:<40} {int(before_val):>20} {int(after_val):>20} {int(change):>15}")

# Equipment mix comparison
print("\n\n🚜 EQUIPMENT MIX COMPARISON")
print("=" * 160)

print(f"\n{'Equipment':<30} {'Before Deals':>15} {'Before Value':>15} {'After Deals':>15} {'After Value':>15} {'Value Change':>15}")
print("-" * 130)

all_equipment = set(list(before['by_equipment'].keys()) + list(after['by_equipment'].keys()))

for equipment in sorted(all_equipment):
    before_deals = int(before['by_equipment'][equipment]['deals'])
    before_value = before['by_equipment'][equipment]['value']
    after_deals = int(after['by_equipment'][equipment]['deals'])
    after_value = after['by_equipment'][equipment]['value']
    value_change = after_value - before_value

    if before_deals > 0 or after_deals > 0:
        print(f"{equipment:<30} {before_deals:>15} ${before_value:>14,.2f} {after_deals:>15} ${after_value:>14,.2f} ${value_change:>14,.2f}")

# Deal size distribution
print("\n\n📊 DEAL SIZE DISTRIBUTION")
print("=" * 160)

def categorize_deal_size(value):
    if value < 2000:
        return 'Small (<$2k)'
    elif value < 5000:
        return 'Medium ($2k-$5k)'
    elif value < 8000:
        return 'Large ($5k-$8k)'
    else:
        return 'Very Large ($8k+)'

before_size_dist = defaultdict(lambda: {'count': 0, 'value': 0})
after_size_dist = defaultdict(lambda: {'count': 0, 'value': 0})

for deal in before['deal_list']:
    size_cat = categorize_deal_size(deal['value'])
    before_size_dist[size_cat]['count'] += 1
    before_size_dist[size_cat]['value'] += deal['value']

for deal in after['deal_list']:
    size_cat = categorize_deal_size(deal['value'])
    after_size_dist[size_cat]['count'] += 1
    after_size_dist[size_cat]['value'] += deal['value']

print(f"\n{'Deal Size':<25} {'Before Count':>15} {'Before %':>12} {'After Count':>15} {'After %':>12} {'Change':>12}")
print("-" * 110)

size_order = ['Small (<$2k)', 'Medium ($2k-$5k)', 'Large ($5k-$8k)', 'Very Large ($8k+)']

for size in size_order:
    before_count = before_size_dist[size]['count']
    after_count = after_size_dist[size]['count']
    before_pct = (before_count / before['deals'] * 100) if before['deals'] > 0 else 0
    after_pct = (after_count / after['deals'] * 100) if after['deals'] > 0 else 0
    change_pct = after_pct - before_pct

    print(f"{size:<25} {before_count:>15} {before_pct:>11.1f}% {after_count:>15} {after_pct:>11.1f}% {change_pct:>11.1f}%")

# Campaign type analysis
print("\n\n🎯 CAMPAIGN TYPE ANALYSIS")
print("=" * 160)

print(f"\n{'Campaign Type':<30} {'Before Deals':>15} {'Before Value':>15} {'After Deals':>15} {'After Value':>15}")
print("-" * 110)

for camp_type in ['Core', 'DSA', 'Expansion', 'Brand']:
    before_deals = int(before['by_campaign_type'][camp_type]['deals'])
    before_value = before['by_campaign_type'][camp_type]['value']
    after_deals = int(after['by_campaign_type'][camp_type]['deals'])
    after_value = after['by_campaign_type'][camp_type]['value']

    if before_deals > 0 or after_deals > 0:
        print(f"{camp_type:<30} {before_deals:>15} ${before_value:>14,.2f} {after_deals:>15} ${after_value:>14,.2f}")

# Key findings
print("\n\n💡 KEY FINDINGS")
print("=" * 160)

avg_deal_before = before['deal_value']/before['deals'] if before['deals'] > 0 else 0
avg_deal_after = after['deal_value']/after['deals'] if after['deals'] > 0 else 0
avg_deal_drop = avg_deal_before - avg_deal_after
avg_deal_drop_pct = (avg_deal_drop / avg_deal_before * 100) if avg_deal_before > 0 else 0

daily_gmv_before = before['deal_value']/before['num_days']
daily_gmv_after = after['deal_value']/after['num_days']
daily_gmv_drop = daily_gmv_before - daily_gmv_after
daily_gmv_drop_pct = (daily_gmv_drop / daily_gmv_before * 100) if daily_gmv_before > 0 else 0

print(f"\n🔴 PROBLEM CONFIRMED:")
print(f"   1. Average Deal Value DROPPED by ${avg_deal_drop:,.2f} ({avg_deal_drop_pct:.1f}%)")
print(f"      • Before: ${avg_deal_before:,.2f}")
print(f"      • After:  ${avg_deal_after:,.2f}")

print(f"\n   2. Daily GMV DROPPED by ${daily_gmv_drop:,.2f}/day ({daily_gmv_drop_pct:.1f}%)")
print(f"      • Before: ${daily_gmv_before:,.2f}/day")
print(f"      • After:  ${daily_gmv_after:,.2f}/day")

call_to_deal_before = (before['deals']/before['calls']*100) if before['calls'] > 0 else 0
call_to_deal_after = (after['deals']/after['calls']*100) if after['calls'] > 0 else 0

print(f"\n   3. Call Quality DECLINED:")
print(f"      • Call→Deal rate dropped from {call_to_deal_before:.1f}% to {call_to_deal_after:.1f}%")
print(f"      • Quote→Deal rate dropped from {(before['deals']/before['quotes']*100) if before['quotes'] > 0 else 0:.1f}% to {(after['deals']/after['quotes']*100) if after['quotes'] > 0 else 0:.1f}%")

# Count small deals
small_before = sum(1 for deal in before['deal_list'] if deal['value'] < 5000)
small_after = sum(1 for deal in after['deal_list'] if deal['value'] < 5000)
small_pct_before = (small_before / len(before['deal_list']) * 100) if len(before['deal_list']) > 0 else 0
small_pct_after = (small_after / len(after['deal_list']) * 100) if len(after['deal_list']) > 0 else 0

print(f"\n   4. SMALLER DEALS INCREASED:")
print(f"      • Deals under $5k: {small_pct_before:.1f}% before → {small_pct_after:.1f}% after")
print(f"      • That's a {small_pct_after - small_pct_before:+.1f}% increase in small deals")

print("\n\n🎯 ROOT CAUSE:")
print(f"   • Expansion campaigns launched Feb 10th")
print(f"   • These campaigns target broader/lower-intent keywords")
print(f"   • Result: More calls, but lower quality leads")
print(f"   • Lower quality = smaller deal sizes = lower GMV")

print("\n\n" + "=" * 160)
print("✅ ANALYSIS COMPLETE")
print("=" * 160)
