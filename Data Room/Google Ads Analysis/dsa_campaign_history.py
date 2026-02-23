from google.ads.googleads.client import GoogleAdsClient
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Load credentials
client = GoogleAdsClient.load_from_storage('/Users/vinuraabeysundara/Desktop/ICG/DOZR/Data Room/Config/google-ads.yaml')
ga_service = client.get_service('GoogleAdsService')
customer_id = '8531896842'

# Get historical data - last 6 months
end_date = '2026-02-23'
start_date = '2025-09-01'  # 6 months of history

print("=" * 160)
print(f"📜 DSA CAMPAIGN HISTORICAL PERFORMANCE")
print(f"Period: {start_date} to {end_date}")
print("=" * 160)

# Query for DSA campaign info
query_campaigns = """
    SELECT
        campaign.id,
        campaign.name,
        campaign.status
    FROM campaign
    WHERE campaign.name LIKE '%DSA%'
        AND campaign.name LIKE '%US%'
"""

print(f"\n{'━' * 160}")
print(f"🎯 DSA CAMPAIGNS OVERVIEW")
print(f"{'━' * 160}\n")

response_campaigns = ga_service.search(customer_id=customer_id, query=query_campaigns)

campaigns = []
for row in response_campaigns:
    campaigns.append({
        'id': row.campaign.id,
        'name': row.campaign.name,
        'status': row.campaign.status.name
    })
    print(f"Campaign: {row.campaign.name}")
    print(f"  • ID: {row.campaign.id}")
    print(f"  • Status: {row.campaign.status.name}")
    print()

# Query for monthly performance
query_monthly = f"""
    SELECT
        segments.month,
        metrics.cost_micros,
        metrics.clicks,
        metrics.impressions,
        metrics.conversions_value,
        metrics.ctr,
        metrics.average_cpc
    FROM campaign
    WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.status = 'ENABLED'
        AND campaign.name LIKE '%DSA%'
        AND campaign.name LIKE '%US%'
"""

response_monthly = ga_service.search(customer_id=customer_id, query=query_monthly)

monthly_data = {}
for row in response_monthly:
    month = row.segments.month
    spend = row.metrics.cost_micros / 1_000_000
    clicks = row.metrics.clicks
    impressions = row.metrics.impressions
    value = row.metrics.conversions_value
    ctr = row.metrics.ctr
    avg_cpc = row.metrics.average_cpc / 1_000_000 if row.metrics.average_cpc else 0

    if month not in monthly_data:
        monthly_data[month] = {
            'spend': 0,
            'clicks': 0,
            'impressions': 0,
            'value': 0,
            'ctr': ctr,
            'avg_cpc': avg_cpc,
            'calls': 0,
            'deals': 0
        }

    monthly_data[month]['spend'] += spend
    monthly_data[month]['clicks'] += clicks
    monthly_data[month]['impressions'] += impressions
    monthly_data[month]['value'] += value

# Query for monthly conversions
query_monthly_conv = f"""
    SELECT
        segments.month,
        segments.conversion_action_name,
        metrics.conversions
    FROM campaign
    WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.status = 'ENABLED'
        AND campaign.name LIKE '%DSA%'
        AND campaign.name LIKE '%US%'
        AND metrics.conversions > 0
"""

response_monthly_conv = ga_service.search(customer_id=customer_id, query=query_monthly_conv)

for row in response_monthly_conv:
    month = row.segments.month
    conv_name = row.segments.conversion_action_name
    conversions = row.metrics.conversions

    if month in monthly_data:
        if 'Phone Call' in conv_name or 'Calls from ads' in conv_name:
            monthly_data[month]['calls'] += conversions
        elif 'Closed Won' in conv_name:
            monthly_data[month]['deals'] += conversions

# Print monthly breakdown
print(f"\n{'=' * 160}")
print(f"📊 MONTHLY PERFORMANCE HISTORY")
print(f"{'=' * 160}\n")

print(f"{'Month':<15} {'Spend':>12} {'Impressions':>12} {'Clicks':>8} {'CTR':>8} {'Avg CPC':>10} {'Calls':>8} {'Deals':>7} {'Value':>14} {'ROAS':>8}")
print("-" * 160)

sorted_months = sorted(monthly_data.keys())
for month in sorted_months:
    data = monthly_data[month]
    roas = data['value'] / data['spend'] if data['spend'] > 0 else 0
    ctr_pct = data['ctr'] * 100 if data['ctr'] else 0

    # Format month as YYYY-MM
    month_str = month

    print(f"{month_str:<15} ${data['spend']:>11,.2f} {data['impressions']:>12,} {data['clicks']:>8} {ctr_pct:>7.2f}% ${data['avg_cpc']:>9.2f} {int(data['calls']):>8} {int(data['deals']):>7} ${data['value']:>13,.2f} {roas:>6.2f}x")

# Calculate totals
total_spend = sum(d['spend'] for d in monthly_data.values())
total_clicks = sum(d['clicks'] for d in monthly_data.values())
total_impressions = sum(d['impressions'] for d in monthly_data.values())
total_calls = sum(d['calls'] for d in monthly_data.values())
total_deals = sum(d['deals'] for d in monthly_data.values())
total_value = sum(d['value'] for d in monthly_data.values())
total_roas = total_value / total_spend if total_spend > 0 else 0
avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
avg_cpc = total_spend / total_clicks if total_clicks > 0 else 0

print("-" * 160)
print(f"{'TOTAL':<15} ${total_spend:>11,.2f} {total_impressions:>12,} {total_clicks:>8} {avg_ctr:>7.2f}% ${avg_cpc:>9.2f} {int(total_calls):>8} {int(total_deals):>7} ${total_value:>13,.2f} {total_roas:>6.2f}x")

# Weekly breakdown for Feb 2026
print(f"\n{'=' * 160}")
print(f"📅 FEBRUARY 2026 - WEEKLY BREAKDOWN")
print(f"{'=' * 160}\n")

query_weekly = f"""
    SELECT
        segments.week,
        metrics.cost_micros,
        metrics.clicks,
        metrics.impressions,
        metrics.conversions_value
    FROM campaign
    WHERE segments.date BETWEEN '2026-02-01' AND '2026-02-23'
        AND campaign.status = 'ENABLED'
        AND campaign.name LIKE '%DSA%'
        AND campaign.name LIKE '%US%'
"""

response_weekly = ga_service.search(customer_id=customer_id, query=query_weekly)

weekly_data = {}
for row in response_weekly:
    week = row.segments.week
    spend = row.metrics.cost_micros / 1_000_000
    clicks = row.metrics.clicks
    impressions = row.metrics.impressions
    value = row.metrics.conversions_value

    if week not in weekly_data:
        weekly_data[week] = {
            'spend': 0,
            'clicks': 0,
            'impressions': 0,
            'value': 0,
            'calls': 0,
            'deals': 0
        }

    weekly_data[week]['spend'] += spend
    weekly_data[week]['clicks'] += clicks
    weekly_data[week]['impressions'] += impressions
    weekly_data[week]['value'] += value

# Query for weekly conversions
query_weekly_conv = f"""
    SELECT
        segments.week,
        segments.conversion_action_name,
        metrics.conversions
    FROM campaign
    WHERE segments.date BETWEEN '2026-02-01' AND '2026-02-23'
        AND campaign.status = 'ENABLED'
        AND campaign.name LIKE '%DSA%'
        AND campaign.name LIKE '%US%'
        AND metrics.conversions > 0
"""

response_weekly_conv = ga_service.search(customer_id=customer_id, query=query_weekly_conv)

for row in response_weekly_conv:
    week = row.segments.week
    conv_name = row.segments.conversion_action_name
    conversions = row.metrics.conversions

    if week in weekly_data:
        if 'Phone Call' in conv_name or 'Calls from ads' in conv_name:
            weekly_data[week]['calls'] += conversions
        elif 'Closed Won' in conv_name:
            weekly_data[week]['deals'] += conversions

print(f"{'Week':<20} {'Spend':>12} {'Impressions':>12} {'Clicks':>8} {'Calls':>8} {'Deals':>7} {'Value':>14} {'ROAS':>8}")
print("-" * 160)

sorted_weeks = sorted(weekly_data.keys())
for week in sorted_weeks:
    data = weekly_data[week]
    roas = data['value'] / data['spend'] if data['spend'] > 0 else 0

    print(f"{week:<20} ${data['spend']:>11,.2f} {data['impressions']:>12,} {data['clicks']:>8} {int(data['calls']):>8} {int(data['deals']):>7} ${data['value']:>13,.2f} {roas:>6.2f}x")

# Growth analysis
print(f"\n{'=' * 160}")
print(f"📈 GROWTH & TREND ANALYSIS")
print(f"{'=' * 160}\n")

if len(sorted_months) >= 2:
    # Compare first month vs last month
    first_month = sorted_months[0]
    last_month = sorted_months[-1]

    first_data = monthly_data[first_month]
    last_data = monthly_data[last_month]

    spend_growth = ((last_data['spend'] - first_data['spend']) / first_data['spend'] * 100) if first_data['spend'] > 0 else 0
    calls_growth = ((last_data['calls'] - first_data['calls']) / first_data['calls'] * 100) if first_data['calls'] > 0 else 0
    deals_growth = ((last_data['deals'] - first_data['deals']) / first_data['deals'] * 100) if first_data['deals'] > 0 else 0
    value_growth = ((last_data['value'] - first_data['value']) / first_data['value'] * 100) if first_data['value'] > 0 else 0

    first_roas = first_data['value'] / first_data['spend'] if first_data['spend'] > 0 else 0
    last_roas = last_data['value'] / last_data['spend'] if last_data['spend'] > 0 else 0
    roas_change = last_roas - first_roas

    print(f"📊 Comparing {first_month} vs {last_month}:\n")
    print(f"   • Spend: ${first_data['spend']:,.2f} → ${last_data['spend']:,.2f} ({spend_growth:+.1f}%)")
    print(f"   • Calls: {int(first_data['calls'])} → {int(last_data['calls'])} ({calls_growth:+.1f}%)")
    print(f"   • Deals: {int(first_data['deals'])} → {int(last_data['deals'])} ({deals_growth:+.1f}%)")
    print(f"   • Value: ${first_data['value']:,.2f} → ${last_data['value']:,.2f} ({value_growth:+.1f}%)")
    print(f"   • ROAS: {first_roas:.2f}x → {last_roas:.2f}x ({roas_change:+.2f}x)")

# Best and worst months
print(f"\n{'=' * 160}")
print(f"🏆 BEST & WORST PERFORMING MONTHS")
print(f"{'=' * 160}\n")

months_by_roas = [(month, data['value'] / data['spend'] if data['spend'] > 0 else 0, data)
                  for month, data in monthly_data.items()]
months_by_roas.sort(key=lambda x: x[1], reverse=True)

print(f"🥇 Best Month by ROAS:")
if months_by_roas:
    best_month, best_roas, best_data = months_by_roas[0]
    print(f"   • {best_month}: {best_roas:.2f}x ROAS")
    print(f"   • Spend: ${best_data['spend']:,.2f}")
    print(f"   • Deals: {int(best_data['deals'])}")
    print(f"   • Value: ${best_data['value']:,.2f}")

print(f"\n⚠️  Worst Month by ROAS:")
if months_by_roas:
    worst_month, worst_roas, worst_data = months_by_roas[-1]
    print(f"   • {worst_month}: {worst_roas:.2f}x ROAS")
    print(f"   • Spend: ${worst_data['spend']:,.2f}")
    print(f"   • Deals: {int(worst_data['deals'])}")
    print(f"   • Value: ${worst_data['value']:,.2f}")

# Summary statistics
print(f"\n{'=' * 160}")
print(f"📊 HISTORICAL SUMMARY STATISTICS")
print(f"{'=' * 160}\n")

num_months = len(monthly_data)
avg_monthly_spend = total_spend / num_months if num_months > 0 else 0
avg_monthly_calls = total_calls / num_months if num_months > 0 else 0
avg_monthly_deals = total_deals / num_months if num_months > 0 else 0
avg_monthly_value = total_value / num_months if num_months > 0 else 0
cost_per_call = total_spend / total_calls if total_calls > 0 else 0
cost_per_deal = total_spend / total_deals if total_deals > 0 else 0
call_to_deal_rate = (total_deals / total_calls * 100) if total_calls > 0 else 0

print(f"⏱️  Period: {num_months} months ({start_date} to {end_date})")
print(f"\n💰 Financial Metrics:")
print(f"   • Total Spend: ${total_spend:,.2f}")
print(f"   • Average Monthly Spend: ${avg_monthly_spend:,.2f}")
print(f"   • Total Conversion Value: ${total_value:,.2f}")
print(f"   • Overall ROAS: {total_roas:.2f}x")

print(f"\n📞 Call Metrics:")
print(f"   • Total Calls: {int(total_calls)}")
print(f"   • Average Calls/Month: {avg_monthly_calls:.1f}")
print(f"   • Cost Per Call: ${cost_per_call:.2f}")

print(f"\n🎯 Deal Metrics:")
print(f"   • Total Deals: {int(total_deals)}")
print(f"   • Average Deals/Month: {avg_monthly_deals:.1f}")
print(f"   • Cost Per Deal: ${cost_per_deal:.2f}")
print(f"   • Average Deal Value: ${total_value / total_deals if total_deals > 0 else 0:,.2f}")
print(f"   • Call → Deal Rate: {call_to_deal_rate:.1f}%")

print(f"\n📈 Click Metrics:")
print(f"   • Total Impressions: {total_impressions:,}")
print(f"   • Total Clicks: {total_clicks:,}")
print(f"   • Average CTR: {avg_ctr:.2f}%")
print(f"   • Average CPC: ${avg_cpc:.2f}")

print(f"\n{'=' * 160}")
print("✅ HISTORICAL ANALYSIS COMPLETE")
print(f"{'=' * 160}")
