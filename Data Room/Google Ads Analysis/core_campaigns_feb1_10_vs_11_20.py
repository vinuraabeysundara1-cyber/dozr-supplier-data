from google.ads.googleads.client import GoogleAdsClient
from datetime import datetime
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Load credentials
client = GoogleAdsClient.load_from_storage('/Users/vinuraabeysundara/Desktop/ICG/DOZR/Data Room/Config/google-ads.yaml')
ga_service = client.get_service('GoogleAdsService')
customer_id = '8531896842'

print("=" * 180)
print(f"📊 CORE CAMPAIGNS COMPARISON: FEB 1-10 vs FEB 11-20 (EXCLUDING EXPANSION)")
print("=" * 180)

# Define periods
period1 = {'name': 'Feb 1-10', 'start': '2026-02-01', 'end': '2026-02-10'}
period2 = {'name': 'Feb 11-20', 'start': '2026-02-11', 'end': '2026-02-20'}

def get_period_data(period):
    """Get all data for a specific period"""
    start_date = period['start']
    end_date = period['end']

    results = {
        'campaigns': defaultdict(lambda: {
            'spend': 0,
            'clicks': 0,
            'impressions': 0,
            'calls': 0,
            'deals': 0,
            'purchases': 0,
            'deal_value': 0,
            'ad_groups': defaultdict(lambda: {
                'spend': 0,
                'clicks': 0,
                'impressions': 0,
                'calls': 0,
                'deals': 0,
                'purchases': 0,
                'deal_value': 0
            })
        })
    }

    # Query for spend, clicks, impressions at ad group level
    query_metrics = f"""
        SELECT
            campaign.name,
            ad_group.name,
            metrics.cost_micros,
            metrics.clicks,
            metrics.impressions
        FROM ad_group
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
            AND campaign.status = 'ENABLED'
            AND ad_group.status = 'ENABLED'
            AND campaign.name LIKE '%US%'
            AND campaign.name NOT LIKE '%Expansion%'
    """

    response_metrics = ga_service.search(customer_id=customer_id, query=query_metrics)

    for row in response_metrics:
        campaign = row.campaign.name
        ad_group = row.ad_group.name
        spend = row.metrics.cost_micros / 1_000_000
        clicks = row.metrics.clicks
        impressions = row.metrics.impressions

        # Campaign level
        results['campaigns'][campaign]['spend'] += spend
        results['campaigns'][campaign]['clicks'] += clicks
        results['campaigns'][campaign]['impressions'] += impressions

        # Ad group level
        results['campaigns'][campaign]['ad_groups'][ad_group]['spend'] += spend
        results['campaigns'][campaign]['ad_groups'][ad_group]['clicks'] += clicks
        results['campaigns'][campaign]['ad_groups'][ad_group]['impressions'] += impressions

    # Query for conversions (calls, deals, purchases)
    query_conv = f"""
        SELECT
            campaign.name,
            ad_group.name,
            segments.conversion_action_name,
            metrics.conversions,
            metrics.conversions_value
        FROM ad_group
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
            AND campaign.status = 'ENABLED'
            AND ad_group.status = 'ENABLED'
            AND campaign.name LIKE '%US%'
            AND campaign.name NOT LIKE '%Expansion%'
            AND metrics.conversions > 0
    """

    response_conv = ga_service.search(customer_id=customer_id, query=query_conv)

    for row in response_conv:
        campaign = row.campaign.name
        ad_group = row.ad_group.name
        conv_name = row.segments.conversion_action_name
        conversions = row.metrics.conversions
        value = row.metrics.conversions_value

        # Categorize conversions
        if 'Phone Call' in conv_name or 'Calls from ads' in conv_name:
            results['campaigns'][campaign]['calls'] += conversions
            results['campaigns'][campaign]['ad_groups'][ad_group]['calls'] += conversions
        elif 'Closed Won' in conv_name:
            results['campaigns'][campaign]['deals'] += conversions
            results['campaigns'][campaign]['deal_value'] += value
            results['campaigns'][campaign]['ad_groups'][ad_group]['deals'] += conversions
            results['campaigns'][campaign]['ad_groups'][ad_group]['deal_value'] += value
        elif 'purchase' in conv_name.lower():
            results['campaigns'][campaign]['purchases'] += conversions
            results['campaigns'][campaign]['ad_groups'][ad_group]['purchases'] += conversions

    return results

print("\n📥 Pulling data for both periods...")
print("=" * 180)

period1_data = get_period_data(period1)
period2_data = get_period_data(period2)

print("✅ Data retrieved\n")

# ==================== CAMPAIGN LEVEL COMPARISON ====================
print("\n" + "=" * 180)
print("📊 CAMPAIGN LEVEL COMPARISON")
print("=" * 180)

# Get all campaigns
all_campaigns = sorted(set(list(period1_data['campaigns'].keys()) + list(period2_data['campaigns'].keys())))

print(f"\n{'Campaign':<60} {'Period':<12} {'Spend':>12} {'Clicks':>8} {'Calls':>8} {'Deals':>7} {'Purch':>7} {'Deal Value':>14} {'CPA':>12} {'ROAS':>8}")
print("-" * 180)

for campaign in all_campaigns:
    campaign_short = campaign.replace('Search-', '').replace('-Core-Geos-US', '').replace('-V3', '')[:57]

    # Period 1 data
    p1 = period1_data['campaigns'][campaign]
    p1_cpa = p1['spend'] / p1['deals'] if p1['deals'] > 0 else 0
    p1_roas = p1['deal_value'] / p1['spend'] if p1['spend'] > 0 else 0

    # Period 2 data
    p2 = period2_data['campaigns'][campaign]
    p2_cpa = p2['spend'] / p2['deals'] if p2['deals'] > 0 else 0
    p2_roas = p2['deal_value'] / p2['spend'] if p2['spend'] > 0 else 0

    # Print Period 1
    if p1['spend'] > 0:
        print(f"{campaign_short:<60} {'Feb 1-10':<12} ${p1['spend']:>11,.2f} {p1['clicks']:>8} {int(p1['calls']):>8} {int(p1['deals']):>7} {int(p1['purchases']):>7} ${p1['deal_value']:>13,.2f} ${p1_cpa:>11,.2f} {p1_roas:>6.2f}x")

    # Print Period 2
    if p2['spend'] > 0:
        print(f"{campaign_short:<60} {'Feb 11-20':<12} ${p2['spend']:>11,.2f} {p2['clicks']:>8} {int(p2['calls']):>8} {int(p2['deals']):>7} {int(p2['purchases']):>7} ${p2['deal_value']:>13,.2f} ${p2_cpa:>11,.2f} {p2_roas:>6.2f}x")

    # Print change
    if p1['spend'] > 0 and p2['spend'] > 0:
        spend_change = p2['spend'] - p1['spend']
        calls_change = p2['calls'] - p1['calls']
        deals_change = p2['deals'] - p1['deals']
        value_change = p2['deal_value'] - p1['deal_value']
        cpa_change = p2_cpa - p1_cpa
        roas_change = p2_roas - p1_roas

        print(f"{'':<60} {'CHANGE':<12} ${spend_change:>11,.2f} {'':<8} {int(calls_change):>8} {int(deals_change):>7} {'':<7} ${value_change:>13,.2f} ${cpa_change:>11,.2f} {roas_change:>6.2f}x")
        print("-" * 180)

# Calculate totals
total_p1 = {
    'spend': sum(c['spend'] for c in period1_data['campaigns'].values()),
    'clicks': sum(c['clicks'] for c in period1_data['campaigns'].values()),
    'calls': sum(c['calls'] for c in period1_data['campaigns'].values()),
    'deals': sum(c['deals'] for c in period1_data['campaigns'].values()),
    'purchases': sum(c['purchases'] for c in period1_data['campaigns'].values()),
    'value': sum(c['deal_value'] for c in period1_data['campaigns'].values())
}

total_p2 = {
    'spend': sum(c['spend'] for c in period2_data['campaigns'].values()),
    'clicks': sum(c['clicks'] for c in period2_data['campaigns'].values()),
    'calls': sum(c['calls'] for c in period2_data['campaigns'].values()),
    'deals': sum(c['deals'] for c in period2_data['campaigns'].values()),
    'purchases': sum(c['purchases'] for c in period2_data['campaigns'].values()),
    'value': sum(c['deal_value'] for c in period2_data['campaigns'].values())
}

print("-" * 180)
print(f"{'TOTAL - FEB 1-10':<60} {'':<12} ${total_p1['spend']:>11,.2f} {total_p1['clicks']:>8} {int(total_p1['calls']):>8} {int(total_p1['deals']):>7} {int(total_p1['purchases']):>7} ${total_p1['value']:>13,.2f} ${total_p1['spend']/total_p1['deals'] if total_p1['deals'] > 0 else 0:>11,.2f} {total_p1['value']/total_p1['spend'] if total_p1['spend'] > 0 else 0:>6.2f}x")
print(f"{'TOTAL - FEB 11-20':<60} {'':<12} ${total_p2['spend']:>11,.2f} {total_p2['clicks']:>8} {int(total_p2['calls']):>8} {int(total_p2['deals']):>7} {int(total_p2['purchases']):>7} ${total_p2['value']:>13,.2f} ${total_p2['spend']/total_p2['deals'] if total_p2['deals'] > 0 else 0:>11,.2f} {total_p2['value']/total_p2['spend'] if total_p2['spend'] > 0 else 0:>6.2f}x")
print(f"{'CHANGE':<60} {'':<12} ${total_p2['spend']-total_p1['spend']:>11,.2f} {total_p2['clicks']-total_p1['clicks']:>8} {int(total_p2['calls']-total_p1['calls']):>8} {int(total_p2['deals']-total_p1['deals']):>7} {int(total_p2['purchases']-total_p1['purchases']):>7} ${total_p2['value']-total_p1['value']:>13,.2f} ${(total_p2['spend']/total_p2['deals'] if total_p2['deals'] > 0 else 0) - (total_p1['spend']/total_p1['deals'] if total_p1['deals'] > 0 else 0):>11,.2f} {(total_p2['value']/total_p2['spend'] if total_p2['spend'] > 0 else 0) - (total_p1['value']/total_p1['spend'] if total_p1['spend'] > 0 else 0):>6.2f}x")

# ==================== AD GROUP LEVEL BREAKDOWN ====================
print("\n\n" + "=" * 180)
print("📊 AD GROUP LEVEL BREAKDOWN")
print("=" * 180)

for campaign in sorted(all_campaigns):
    campaign_short = campaign.replace('Search-', '').replace('-Core-Geos-US', '').replace('-V3', '')

    # Get all ad groups for this campaign
    ad_groups_p1 = set(period1_data['campaigns'][campaign]['ad_groups'].keys())
    ad_groups_p2 = set(period2_data['campaigns'][campaign]['ad_groups'].keys())
    all_ad_groups = sorted(ad_groups_p1 | ad_groups_p2)

    if not all_ad_groups:
        continue

    print(f"\n{'─' * 180}")
    print(f"Campaign: {campaign_short}")
    print(f"{'─' * 180}")

    print(f"{'Ad Group':<60} {'Period':<12} {'Spend':>12} {'Clicks':>8} {'Calls':>8} {'Deals':>7} {'Purch':>7} {'Deal Value':>14} {'CPA':>12} {'ROAS':>8}")
    print("-" * 180)

    for ad_group in all_ad_groups:
        ad_group_short = ad_group[:57] + '...' if len(ad_group) > 60 else ad_group

        # Period 1 data
        p1_ag = period1_data['campaigns'][campaign]['ad_groups'][ad_group]
        p1_cpa = p1_ag['spend'] / p1_ag['deals'] if p1_ag['deals'] > 0 else 0
        p1_roas = p1_ag['deal_value'] / p1_ag['spend'] if p1_ag['spend'] > 0 else 0

        # Period 2 data
        p2_ag = period2_data['campaigns'][campaign]['ad_groups'][ad_group]
        p2_cpa = p2_ag['spend'] / p2_ag['deals'] if p2_ag['deals'] > 0 else 0
        p2_roas = p2_ag['deal_value'] / p2_ag['spend'] if p2_ag['spend'] > 0 else 0

        # Print Period 1
        if p1_ag['spend'] > 0:
            print(f"{ad_group_short:<60} {'Feb 1-10':<12} ${p1_ag['spend']:>11,.2f} {p1_ag['clicks']:>8} {int(p1_ag['calls']):>8} {int(p1_ag['deals']):>7} {int(p1_ag['purchases']):>7} ${p1_ag['deal_value']:>13,.2f} ${p1_cpa:>11,.2f} {p1_roas:>6.2f}x")

        # Print Period 2
        if p2_ag['spend'] > 0:
            print(f"{ad_group_short:<60} {'Feb 11-20':<12} ${p2_ag['spend']:>11,.2f} {p2_ag['clicks']:>8} {int(p2_ag['calls']):>8} {int(p2_ag['deals']):>7} {int(p2_ag['purchases']):>7} ${p2_ag['deal_value']:>13,.2f} ${p2_cpa:>11,.2f} {p2_roas:>6.2f}x")

        # Print change if both periods have data
        if p1_ag['spend'] > 0 and p2_ag['spend'] > 0:
            spend_change = p2_ag['spend'] - p1_ag['spend']
            calls_change = p2_ag['calls'] - p1_ag['calls']
            deals_change = p2_ag['deals'] - p1_ag['deals']
            value_change = p2_ag['deal_value'] - p1_ag['deal_value']

            print(f"{'':<60} {'CHANGE':<12} ${spend_change:>11,.2f} {'':<8} {int(calls_change):>8} {int(deals_change):>7} {'':<7} ${value_change:>13,.2f}")

        print()

# ==================== SUMMARY STATS ====================
print("\n" + "=" * 180)
print("📊 SUMMARY STATISTICS")
print("=" * 180)

print(f"\n{'Metric':<40} {'Feb 1-10':>20} {'Feb 11-20':>20} {'Change':>15} {'% Change':>12}")
print("-" * 120)

summary_metrics = [
    ('Total Spend', total_p1['spend'], total_p2['spend']),
    ('Total Clicks', total_p1['clicks'], total_p2['clicks']),
    ('Total Calls', total_p1['calls'], total_p2['calls']),
    ('Total Deals', total_p1['deals'], total_p2['deals']),
    ('Total Purchases', total_p1['purchases'], total_p2['purchases']),
    ('Total Deal Value', total_p1['value'], total_p2['value']),
    ('Average CPA', total_p1['spend']/total_p1['deals'] if total_p1['deals'] > 0 else 0,
                   total_p2['spend']/total_p2['deals'] if total_p2['deals'] > 0 else 0),
    ('ROAS', total_p1['value']/total_p1['spend'] if total_p1['spend'] > 0 else 0,
            total_p2['value']/total_p2['spend'] if total_p2['spend'] > 0 else 0),
    ('Cost per Call', total_p1['spend']/total_p1['calls'] if total_p1['calls'] > 0 else 0,
                     total_p2['spend']/total_p2['calls'] if total_p2['calls'] > 0 else 0),
    ('Call to Deal %', (total_p1['deals']/total_p1['calls']*100) if total_p1['calls'] > 0 else 0,
                      (total_p2['deals']/total_p2['calls']*100) if total_p2['calls'] > 0 else 0),
]

for metric_name, p1_val, p2_val in summary_metrics:
    change = p2_val - p1_val
    pct_change = (change / p1_val * 100) if p1_val > 0 else 0

    if 'ROAS' in metric_name:
        print(f"{metric_name:<40} {p1_val:>19.2f}x {p2_val:>19.2f}x {change:>14.2f}x {pct_change:>11.1f}%")
    elif '%' in metric_name:
        print(f"{metric_name:<40} {p1_val:>19.1f}% {p2_val:>19.1f}% {change:>14.1f}% {pct_change:>11.1f}%")
    elif 'Deals' in metric_name or 'Calls' in metric_name or 'Clicks' in metric_name or 'Purchases' in metric_name:
        print(f"{metric_name:<40} {int(p1_val):>20} {int(p2_val):>20} {int(change):>15} {pct_change:>11.1f}%")
    else:
        print(f"{metric_name:<40} ${p1_val:>19,.2f} ${p2_val:>19,.2f} ${change:>14,.2f} {pct_change:>11.1f}%")

print("\n\n" + "=" * 180)
print("✅ ANALYSIS COMPLETE")
print("=" * 180)
