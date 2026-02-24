from google.ads.googleads.client import GoogleAdsClient
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Load credentials
client = GoogleAdsClient.load_from_storage('/Users/vinuraabeysundara/Desktop/ICG/DOZR/Data Room/Config/google-ads.yaml')
ga_service = client.get_service('GoogleAdsService')
customer_id = '8531896842'

print("=" * 160)
print("🔍 DSA CAMPAIGN DECLINE INVESTIGATION")
print("Analyzing why ROAS dropped from 11.73x to 3.62x")
print("=" * 160)

# Define periods
period1 = {'name': 'Feb 1-10', 'start': '2026-02-01', 'end': '2026-02-10'}
period2 = {'name': 'Feb 11-20', 'start': '2026-02-11', 'end': '2026-02-20'}

def analyze_dsa_period(period):
    """Detailed analysis of DSA campaign for a period"""
    start_date = period['start']
    end_date = period['end']

    print(f"\n\n{'='*160}")
    print(f"📊 PERIOD: {period['name']} ({start_date} to {end_date})")
    print(f"{'='*160}")

    # Get metrics
    query_metrics = f"""
        SELECT
            campaign.name,
            ad_group.name,
            segments.date,
            metrics.cost_micros,
            metrics.clicks,
            metrics.impressions,
            metrics.average_cpc
        FROM ad_group
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
            AND campaign.name LIKE '%DSA%'
            AND campaign.name LIKE '%US%'
            AND campaign.name NOT LIKE '%Expansion%'
    """

    response_metrics = ga_service.search(customer_id=customer_id, query=query_metrics)

    daily_data = defaultdict(lambda: {'spend': 0, 'clicks': 0, 'impressions': 0})
    total_spend = 0
    total_clicks = 0
    total_impressions = 0

    for row in response_metrics:
        date = row.segments.date
        spend = row.metrics.cost_micros / 1_000_000
        clicks = row.metrics.clicks
        impressions = row.metrics.impressions

        daily_data[date]['spend'] += spend
        daily_data[date]['clicks'] += clicks
        daily_data[date]['impressions'] += impressions

        total_spend += spend
        total_clicks += clicks
        total_impressions += impressions

    # Get conversions
    query_conv = f"""
        SELECT
            campaign.name,
            segments.date,
            segments.conversion_action_name,
            metrics.conversions,
            metrics.conversions_value
        FROM campaign
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
            AND campaign.name LIKE '%DSA%'
            AND campaign.name LIKE '%US%'
            AND campaign.name NOT LIKE '%Expansion%'
            AND metrics.conversions > 0
    """

    response_conv = ga_service.search(customer_id=customer_id, query=query_conv)

    total_calls = 0
    total_deals = 0
    total_value = 0
    deals_by_date = defaultdict(lambda: {'deals': 0, 'value': 0})

    for row in response_conv:
        date = row.segments.date
        conv_name = row.segments.conversion_action_name
        conversions = row.metrics.conversions
        value = row.metrics.conversions_value

        if 'Phone Call' in conv_name or 'Calls from ads' in conv_name:
            total_calls += conversions
            daily_data[date]['calls'] = daily_data[date].get('calls', 0) + conversions
        elif 'Closed Won' in conv_name:
            total_deals += conversions
            total_value += value
            deals_by_date[date]['deals'] += conversions
            deals_by_date[date]['value'] += value
            daily_data[date]['deals'] = daily_data[date].get('deals', 0) + conversions
            daily_data[date]['value'] = daily_data[date].get('value', 0) + value

    # Print summary
    avg_cpc = total_spend / total_clicks if total_clicks > 0 else 0
    ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    avg_deal = total_value / total_deals if total_deals > 0 else 0
    call_to_deal = (total_deals / total_calls * 100) if total_calls > 0 else 0
    cpa = total_spend / total_deals if total_deals > 0 else 0
    roas = total_value / total_spend if total_spend > 0 else 0

    print(f"\n📈 SUMMARY METRICS:")
    print(f"   • Total Spend: ${total_spend:,.2f}")
    print(f"   • Impressions: {total_impressions:,}")
    print(f"   • Clicks: {total_clicks:,}")
    print(f"   • CTR: {ctr:.2f}%")
    print(f"   • Avg CPC: ${avg_cpc:.2f}")
    print(f"   • Calls: {int(total_calls)}")
    print(f"   • Deals: {int(total_deals)}")
    print(f"   • Deal Value: ${total_value:,.2f}")
    print(f"   • Avg Deal Value: ${avg_deal:,.2f}")
    print(f"   • Call→Deal Rate: {call_to_deal:.1f}%")
    print(f"   • CPA: ${cpa:,.2f}")
    print(f"   • ROAS: {roas:.2f}x")

    # Daily breakdown
    print(f"\n📅 DAILY BREAKDOWN:")
    print(f"{'Date':<12} {'Spend':>10} {'Impr':>8} {'Clicks':>7} {'CPC':>7} {'Calls':>7} {'Deals':>7} {'Value':>12} {'ROAS':>7}")
    print("-" * 100)

    for date in sorted(daily_data.keys()):
        data = daily_data[date]
        cpc = data['spend'] / data['clicks'] if data['clicks'] > 0 else 0
        calls = data.get('calls', 0)
        deals = data.get('deals', 0)
        value = data.get('value', 0)
        daily_roas = value / data['spend'] if data['spend'] > 0 else 0

        print(f"{date:<12} ${data['spend']:>9,.2f} {data['impressions']:>8,} {data['clicks']:>7} ${cpc:>6.2f} {int(calls):>7} {int(deals):>7} ${value:>11,.2f} {daily_roas:>6.2f}x")

    return {
        'spend': total_spend,
        'clicks': total_clicks,
        'impressions': total_impressions,
        'calls': total_calls,
        'deals': total_deals,
        'value': total_value,
        'avg_cpc': avg_cpc,
        'ctr': ctr,
        'avg_deal': avg_deal,
        'call_to_deal': call_to_deal,
        'cpa': cpa,
        'roas': roas
    }

# Analyze both periods
p1_data = analyze_dsa_period(period1)
p2_data = analyze_dsa_period(period2)

# Comparison
print("\n\n" + "=" * 160)
print("📊 PERIOD-OVER-PERIOD COMPARISON")
print("=" * 160)

metrics = [
    ('Spend', 'spend', '$'),
    ('Clicks', 'clicks', ''),
    ('Impressions', 'impressions', ''),
    ('Avg CPC', 'avg_cpc', '$'),
    ('CTR', 'ctr', '%'),
    ('Calls', 'calls', ''),
    ('Deals', 'deals', ''),
    ('Deal Value', 'value', '$'),
    ('Avg Deal Value', 'avg_deal', '$'),
    ('Call→Deal Rate', 'call_to_deal', '%'),
    ('CPA', 'cpa', '$'),
    ('ROAS', 'roas', 'x')
]

print(f"\n{'Metric':<20} {'Feb 1-10':>15} {'Feb 11-20':>15} {'Change':>15} {'% Change':>12}")
print("-" * 80)

for name, key, unit in metrics:
    p1_val = p1_data[key]
    p2_val = p2_data[key]
    change = p2_val - p1_val
    pct_change = (change / p1_val * 100) if p1_val != 0 else 0

    if unit == '$':
        print(f"{name:<20} ${p1_val:>14,.2f} ${p2_val:>14,.2f} ${change:>14,.2f} {pct_change:>11.1f}%")
    elif unit == '%':
        print(f"{name:<20} {p1_val:>14.2f}% {p2_val:>14.2f}% {change:>14.2f}% {pct_change:>11.1f}%")
    elif unit == 'x':
        print(f"{name:<20} {p1_val:>14.2f}x {p2_val:>14.2f}x {change:>14.2f}x {pct_change:>11.1f}%")
    else:
        print(f"{name:<20} {p1_val:>15,.0f} {p2_val:>15,.0f} {change:>15,.0f} {pct_change:>11.1f}%")

# Root cause analysis
print("\n\n" + "=" * 160)
print("🔍 ROOT CAUSE ANALYSIS")
print("=" * 160)

print("\n❌ PRIMARY ISSUES:")

# Issue 1: Conversion rate collapse
if p2_data['call_to_deal'] < p1_data['call_to_deal']:
    drop = p1_data['call_to_deal'] - p2_data['call_to_deal']
    print(f"\n1. CALL-TO-DEAL CONVERSION COLLAPSED")
    print(f"   • Dropped from {p1_data['call_to_deal']:.1f}% to {p2_data['call_to_deal']:.1f}% (-{drop:.1f} points)")
    print(f"   • Despite getting MORE calls ({int(p1_data['calls'])} → {int(p2_data['calls'])}), closing FEWER deals")
    print(f"   • This suggests LEAD QUALITY declined significantly")

# Issue 2: Deal value decline
if p2_data['avg_deal'] < p1_data['avg_deal']:
    drop = p1_data['avg_deal'] - p2_data['avg_deal']
    pct = (drop / p1_data['avg_deal'] * 100)
    print(f"\n2. AVERAGE DEAL VALUE DROPPED")
    print(f"   • From ${p1_data['avg_deal']:,.2f} to ${p2_data['avg_deal']:,.2f} (-${drop:,.2f}, -{pct:.1f}%)")
    print(f"   • Deals in P2 were smaller/lower value equipment")

# Issue 3: Spend efficiency
if p2_data['avg_cpc'] > p1_data['avg_cpc']:
    increase = p2_data['avg_cpc'] - p1_data['avg_cpc']
    pct = (increase / p1_data['avg_cpc'] * 100)
    print(f"\n3. COST PER CLICK INCREASED")
    print(f"   • From ${p1_data['avg_cpc']:.2f} to ${p2_data['avg_cpc']:.2f} (+${increase:.2f}, +{pct:.1f}%)")
    print(f"   • Paying more for each click")

print("\n\n💡 LIKELY CAUSES:")
print("   1. Expansion campaigns launched Feb 10th may have caused:")
print("      • Budget/impression share dilution across campaigns")
print("      • Algorithmic learning period affecting DSA targeting")
print("      • Competition for same audiences")
print("   2. DSA algorithm may have expanded to lower-intent queries")
print("   3. Seasonality or market conditions changed mid-month")
print("   4. Lead quality degradation (more tire-kickers, fewer serious buyers)")

print("\n\n🎯 RECOMMENDATIONS:")
print("   1. Review DSA search term report to identify low-performing queries")
print("   2. Add negative keywords for low-intent searches")
print("   3. Consider pausing expansion campaigns temporarily to test impact")
print("   4. Review page feed and ensure high-quality landing pages only")
print("   5. Increase target CPA or adjust bid strategy if budget was constrained")
print("   6. Analyze deal size distribution - if skewing toward small equipment, adjust targeting")

print("\n" + "=" * 160)
