from google.ads.googleads.client import GoogleAdsClient
from datetime import datetime
from collections import defaultdict
import csv
import warnings
warnings.filterwarnings('ignore')

# Load credentials
client = GoogleAdsClient.load_from_storage('/Users/vinuraabeysundara/Desktop/ICG/DOZR/Data Room/Config/google-ads.yaml')
ga_service = client.get_service('GoogleAdsService')
customer_id = '8531896842'

print("=" * 200)
print(f"📊 DETAILED AD GROUP COMPARISON BY CAMPAIGN: FEB 1-10 vs FEB 11-20")
print("=" * 200)

# Define periods
period1 = {'name': 'Feb 1-10', 'start': '2026-02-01', 'end': '2026-02-10'}
period2 = {'name': 'Feb 11-20', 'start': '2026-02-11', 'end': '2026-02-20'}

def get_ad_group_data(period):
    """Get detailed ad group level data for a period"""
    start_date = period['start']
    end_date = period['end']

    ad_group_data = {}

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
        key = f"{campaign}|||{ad_group}"

        if key not in ad_group_data:
            ad_group_data[key] = {
                'campaign': campaign,
                'ad_group': ad_group,
                'spend': 0,
                'clicks': 0,
                'impressions': 0,
                'calls': 0,
                'deals': 0,
                'purchases': 0,
                'deal_value': 0
            }

        ad_group_data[key]['spend'] += row.metrics.cost_micros / 1_000_000
        ad_group_data[key]['clicks'] += row.metrics.clicks
        ad_group_data[key]['impressions'] += row.metrics.impressions

    # Query for conversions
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
        key = f"{campaign}|||{ad_group}"
        conv_name = row.segments.conversion_action_name
        conversions = row.metrics.conversions
        value = row.metrics.conversions_value

        if key not in ad_group_data:
            ad_group_data[key] = {
                'campaign': campaign,
                'ad_group': ad_group,
                'spend': 0,
                'clicks': 0,
                'impressions': 0,
                'calls': 0,
                'deals': 0,
                'purchases': 0,
                'deal_value': 0
            }

        if 'Phone Call' in conv_name or 'Calls from ads' in conv_name:
            ad_group_data[key]['calls'] += conversions
        elif 'Closed Won' in conv_name:
            ad_group_data[key]['deals'] += conversions
            ad_group_data[key]['deal_value'] += value
        elif 'purchase' in conv_name.lower():
            ad_group_data[key]['purchases'] += conversions

    return ad_group_data

print("\n📥 Pulling detailed ad group data for both periods...")
print("=" * 200)

period1_data = get_ad_group_data(period1)
period2_data = get_ad_group_data(period2)

print("✅ Data retrieved\n")

# Get all unique ad groups
all_keys = sorted(set(list(period1_data.keys()) + list(period2_data.keys())))

# Group by campaign
campaigns = {}
for key in all_keys:
    campaign = key.split('|||')[0]
    if campaign not in campaigns:
        campaigns[campaign] = []
    campaigns[campaign].append(key)

# Prepare data for CSV export
csv_data = []
csv_headers = [
    'Campaign', 'Ad Group',
    'P1_Spend', 'P1_Clicks', 'P1_Impressions', 'P1_CTR', 'P1_CPC', 'P1_Calls', 'P1_Deals', 'P1_Purchases', 'P1_Deal_Value', 'P1_CPA', 'P1_ROAS',
    'P2_Spend', 'P2_Clicks', 'P2_Impressions', 'P2_CTR', 'P2_CPC', 'P2_Calls', 'P2_Deals', 'P2_Purchases', 'P2_Deal_Value', 'P2_CPA', 'P2_ROAS',
    'Change_Spend', 'Change_Clicks', 'Change_Calls', 'Change_Deals', 'Change_Deal_Value', 'Change_CPA', 'Change_ROAS'
]

# Print detailed breakdown for each campaign
for campaign in sorted(campaigns.keys()):
    campaign_short = campaign.replace('Search-', '').replace('-Core-Geos-US', '').replace('-V3', '')

    print("\n" + "=" * 200)
    print(f"📊 CAMPAIGN: {campaign_short}")
    print("=" * 200)

    print(f"\n{'Ad Group':<60} {'Period':<12} {'Spend':>12} {'Clicks':>8} {'Impr':>10} {'CTR':>8} {'CPC':>10} {'Calls':>8} {'Deals':>7} {'Purch':>7} {'Deal Value':>14} {'CPA':>12} {'ROAS':>8}")
    print("-" * 200)

    campaign_total_p1 = {'spend': 0, 'clicks': 0, 'impressions': 0, 'calls': 0, 'deals': 0, 'purchases': 0, 'deal_value': 0}
    campaign_total_p2 = {'spend': 0, 'clicks': 0, 'impressions': 0, 'calls': 0, 'deals': 0, 'purchases': 0, 'deal_value': 0}

    for key in sorted(campaigns[campaign], key=lambda x: x.split('|||')[1]):
        ad_group_name = key.split('|||')[1]
        ad_group_short = ad_group_name[:57] + '...' if len(ad_group_name) > 60 else ad_group_name

        # Period 1 data
        p1 = period1_data.get(key, {'spend': 0, 'clicks': 0, 'impressions': 0, 'calls': 0, 'deals': 0, 'purchases': 0, 'deal_value': 0})
        p1_ctr = (p1['clicks'] / p1['impressions'] * 100) if p1['impressions'] > 0 else 0
        p1_cpc = p1['spend'] / p1['clicks'] if p1['clicks'] > 0 else 0
        p1_cpa = p1['spend'] / p1['deals'] if p1['deals'] > 0 else 0
        p1_roas = p1['deal_value'] / p1['spend'] if p1['spend'] > 0 else 0

        # Period 2 data
        p2 = period2_data.get(key, {'spend': 0, 'clicks': 0, 'impressions': 0, 'calls': 0, 'deals': 0, 'purchases': 0, 'deal_value': 0})
        p2_ctr = (p2['clicks'] / p2['impressions'] * 100) if p2['impressions'] > 0 else 0
        p2_cpc = p2['spend'] / p2['clicks'] if p2['clicks'] > 0 else 0
        p2_cpa = p2['spend'] / p2['deals'] if p2['deals'] > 0 else 0
        p2_roas = p2['deal_value'] / p2['spend'] if p2['spend'] > 0 else 0

        # Update campaign totals
        for metric in ['spend', 'clicks', 'impressions', 'calls', 'deals', 'purchases', 'deal_value']:
            campaign_total_p1[metric] += p1[metric]
            campaign_total_p2[metric] += p2[metric]

        # Print Period 1
        if p1['spend'] > 0:
            print(f"{ad_group_short:<60} {'Feb 1-10':<12} ${p1['spend']:>11,.2f} {p1['clicks']:>8} {p1['impressions']:>10,} {p1_ctr:>7.2f}% ${p1_cpc:>9.2f} {int(p1['calls']):>8} {int(p1['deals']):>7} {int(p1['purchases']):>7} ${p1['deal_value']:>13,.2f} ${p1_cpa:>11,.2f} {p1_roas:>6.2f}x")

        # Print Period 2
        if p2['spend'] > 0:
            print(f"{ad_group_short:<60} {'Feb 11-20':<12} ${p2['spend']:>11,.2f} {p2['clicks']:>8} {p2['impressions']:>10,} {p2_ctr:>7.2f}% ${p2_cpc:>9.2f} {int(p2['calls']):>8} {int(p2['deals']):>7} {int(p2['purchases']):>7} ${p2['deal_value']:>13,.2f} ${p2_cpa:>11,.2f} {p2_roas:>6.2f}x")

        # Print change
        if p1['spend'] > 0 and p2['spend'] > 0:
            change_spend = p2['spend'] - p1['spend']
            change_clicks = p2['clicks'] - p1['clicks']
            change_calls = p2['calls'] - p1['calls']
            change_deals = p2['deals'] - p1['deals']
            change_value = p2['deal_value'] - p1['deal_value']
            change_cpa = p2_cpa - p1_cpa
            change_roas = p2_roas - p1_roas

            print(f"{'':<60} {'CHANGE':<12} ${change_spend:>11,.2f} {change_clicks:>8} {'':<10} {'':<8} {'':<10} {int(change_calls):>8} {int(change_deals):>7} {'':<7} ${change_value:>13,.2f} ${change_cpa:>11,.2f} {change_roas:>6.2f}x")

        print()

        # Add to CSV data
        csv_data.append([
            campaign_short, ad_group_name,
            f"{p1['spend']:.2f}", p1['clicks'], p1['impressions'], f"{p1_ctr:.2f}", f"{p1_cpc:.2f}", int(p1['calls']), int(p1['deals']), int(p1['purchases']), f"{p1['deal_value']:.2f}", f"{p1_cpa:.2f}", f"{p1_roas:.2f}",
            f"{p2['spend']:.2f}", p2['clicks'], p2['impressions'], f"{p2_ctr:.2f}", f"{p2_cpc:.2f}", int(p2['calls']), int(p2['deals']), int(p2['purchases']), f"{p2['deal_value']:.2f}", f"{p2_cpa:.2f}", f"{p2_roas:.2f}",
            f"{p2['spend']-p1['spend']:.2f}", p2['clicks']-p1['clicks'], int(p2['calls']-p1['calls']), int(p2['deals']-p1['deals']), f"{p2['deal_value']-p1['deal_value']:.2f}", f"{p2_cpa-p1_cpa:.2f}", f"{p2_roas-p1_roas:.2f}"
        ])

    # Print campaign totals
    print("-" * 200)
    ct1_ctr = (campaign_total_p1['clicks'] / campaign_total_p1['impressions'] * 100) if campaign_total_p1['impressions'] > 0 else 0
    ct1_cpc = campaign_total_p1['spend'] / campaign_total_p1['clicks'] if campaign_total_p1['clicks'] > 0 else 0
    ct1_cpa = campaign_total_p1['spend'] / campaign_total_p1['deals'] if campaign_total_p1['deals'] > 0 else 0
    ct1_roas = campaign_total_p1['deal_value'] / campaign_total_p1['spend'] if campaign_total_p1['spend'] > 0 else 0

    ct2_ctr = (campaign_total_p2['clicks'] / campaign_total_p2['impressions'] * 100) if campaign_total_p2['impressions'] > 0 else 0
    ct2_cpc = campaign_total_p2['spend'] / campaign_total_p2['clicks'] if campaign_total_p2['clicks'] > 0 else 0
    ct2_cpa = campaign_total_p2['spend'] / campaign_total_p2['deals'] if campaign_total_p2['deals'] > 0 else 0
    ct2_roas = campaign_total_p2['deal_value'] / campaign_total_p2['spend'] if campaign_total_p2['spend'] > 0 else 0

    print(f"{'CAMPAIGN TOTAL':<60} {'Feb 1-10':<12} ${campaign_total_p1['spend']:>11,.2f} {campaign_total_p1['clicks']:>8} {campaign_total_p1['impressions']:>10,} {ct1_ctr:>7.2f}% ${ct1_cpc:>9.2f} {int(campaign_total_p1['calls']):>8} {int(campaign_total_p1['deals']):>7} {int(campaign_total_p1['purchases']):>7} ${campaign_total_p1['deal_value']:>13,.2f} ${ct1_cpa:>11,.2f} {ct1_roas:>6.2f}x")
    print(f"{'CAMPAIGN TOTAL':<60} {'Feb 11-20':<12} ${campaign_total_p2['spend']:>11,.2f} {campaign_total_p2['clicks']:>8} {campaign_total_p2['impressions']:>10,} {ct2_ctr:>7.2f}% ${ct2_cpc:>9.2f} {int(campaign_total_p2['calls']):>8} {int(campaign_total_p2['deals']):>7} {int(campaign_total_p2['purchases']):>7} ${campaign_total_p2['deal_value']:>13,.2f} ${ct2_cpa:>11,.2f} {ct2_roas:>6.2f}x")
    print(f"{'CHANGE':<60} {'':<12} ${campaign_total_p2['spend']-campaign_total_p1['spend']:>11,.2f} {campaign_total_p2['clicks']-campaign_total_p1['clicks']:>8} {'':<10} {'':<8} {'':<10} {int(campaign_total_p2['calls']-campaign_total_p1['calls']):>8} {int(campaign_total_p2['deals']-campaign_total_p1['deals']):>7} {'':<7} ${campaign_total_p2['deal_value']-campaign_total_p1['deal_value']:>13,.2f} ${ct2_cpa-ct1_cpa:>11,.2f} {ct2_roas-ct1_roas:>6.2f}x")

# Save to CSV
csv_filename = 'ad_group_comparison_feb1_10_vs_11_20.csv'
with open(csv_filename, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(csv_headers)
    writer.writerows(csv_data)

print("\n\n" + "=" * 200)
print("✅ ANALYSIS COMPLETE")
print("=" * 200)
print(f"\n📄 CSV Export saved to: {csv_filename}")
print("   • Import into Excel or Google Sheets for further analysis")
print("   • Includes all ad groups with detailed metrics for both periods")
