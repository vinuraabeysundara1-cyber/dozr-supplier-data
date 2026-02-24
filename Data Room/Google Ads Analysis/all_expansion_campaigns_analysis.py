from google.ads.googleads.client import GoogleAdsClient
from collections import defaultdict
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Load credentials
client = GoogleAdsClient.load_from_storage('/Users/vinuraabeysundara/Desktop/ICG/DOZR/Data Room/Config/google-ads.yaml')
ga_service = client.get_service('GoogleAdsService')
customer_id = '8531896842'

print("=" * 200)
print("ALL EXPANSION CAMPAIGNS - COMPLETE ANALYSIS WITH QUOTE TIMELINE")
print("Period: January 24 - February 23, 2026 (30 days)")
print("=" * 200)

start_date = '2026-01-24'
end_date = '2026-02-23'

# Get all Expansion campaigns
query_campaigns = """
    SELECT
        campaign.id,
        campaign.name,
        campaign.status
    FROM campaign
    WHERE campaign.name LIKE '%Expansion%'
        AND campaign.name LIKE '%US%'
"""

response_campaigns = ga_service.search(customer_id=customer_id, query=query_campaigns)

expansion_campaigns = []
for row in response_campaigns:
    expansion_campaigns.append({
        'id': row.campaign.id,
        'name': row.campaign.name,
        'status': str(row.campaign.status)
    })

print(f"\n✅ Found {len(expansion_campaigns)} Expansion campaign(s)")
for camp in expansion_campaigns:
    status_icon = "🟢" if 'ENABLED' in camp['status'] else "🔴"
    print(f"   {status_icon} {camp['name']}")

all_recommendations = []

# Analyze each campaign
for campaign in expansion_campaigns:
    campaign_name = campaign['name']
    campaign_id = campaign['id']

    print(f"\n\n{'='*200}")
    print(f"📊 CAMPAIGN: {campaign_name}")
    print(f"{'='*200}")

    # Get metrics by ad group
    query_metrics = f"""
        SELECT
            ad_group.name,
            ad_group.status,
            metrics.cost_micros,
            metrics.clicks,
            metrics.impressions
        FROM ad_group
        WHERE campaign.id = {campaign_id}
            AND segments.date BETWEEN '{start_date}' AND '{end_date}'
    """

    response_metrics = ga_service.search(customer_id=customer_id, query=query_metrics)

    ad_group_data = defaultdict(lambda: {
        'status': '',
        'spend': 0,
        'clicks': 0,
        'impressions': 0,
        'conversions_by_type': defaultdict(float),
        'conversion_value_by_type': defaultdict(float)
    })

    for row in response_metrics:
        ad_group = row.ad_group.name
        status = str(row.ad_group.status)
        spend = row.metrics.cost_micros / 1_000_000
        clicks = row.metrics.clicks
        impressions = row.metrics.impressions

        ad_group_data[ad_group]['status'] = status
        ad_group_data[ad_group]['spend'] += spend
        ad_group_data[ad_group]['clicks'] += clicks
        ad_group_data[ad_group]['impressions'] += impressions

    # Get ALL conversions by type
    query_all_conv = f"""
        SELECT
            ad_group.name,
            segments.conversion_action_name,
            metrics.conversions,
            metrics.conversions_value
        FROM ad_group
        WHERE campaign.id = {campaign_id}
            AND segments.date BETWEEN '{start_date}' AND '{end_date}'
            AND metrics.conversions > 0
    """

    response_conv = ga_service.search(customer_id=customer_id, query=query_all_conv)

    for row in response_conv:
        ad_group = row.ad_group.name
        conv_name = row.segments.conversion_action_name
        conversions = row.metrics.conversions
        value = row.metrics.conversions_value

        ad_group_data[ad_group]['conversions_by_type'][conv_name] += conversions
        ad_group_data[ad_group]['conversion_value_by_type'][conv_name] += value

    # Calculate totals
    total_spend = sum(d['spend'] for d in ad_group_data.values())
    total_clicks = sum(d['clicks'] for d in ad_group_data.values())
    total_impressions = sum(d['impressions'] for d in ad_group_data.values())

    # Calculate total conversions by type
    all_conv_types = defaultdict(float)
    all_conv_values = defaultdict(float)
    for data in ad_group_data.values():
        for conv_type, count in data['conversions_by_type'].items():
            all_conv_types[conv_type] += count
            all_conv_values[conv_type] += data['conversion_value_by_type'][conv_type]

    total_value = sum(all_conv_values.values())
    total_roas = total_value / total_spend if total_spend > 0 else 0

    # Count specific conversion types
    total_calls = sum(count for conv_type, count in all_conv_types.items() if 'Phone Call' in conv_type or 'Calls from ads' in conv_type)
    total_deals = sum(count for conv_type, count in all_conv_types.items() if 'Closed Won' in conv_type)
    total_purchases = sum(count for conv_type, count in all_conv_types.items() if 'purchase' in conv_type.lower())
    total_quotes = sum(count for conv_type, count in all_conv_types.items() if 'quote' in conv_type.lower())

    # Print campaign summary
    print(f"\n📈 CAMPAIGN SUMMARY (30 DAYS):")
    print(f"   • Total Spend: ${total_spend:,.2f}")
    print(f"   • Total Clicks: {total_clicks:,}")
    print(f"   • Avg CPC: ${total_spend/total_clicks if total_clicks > 0 else 0:.2f}")
    print(f"   • Total Calls: {int(total_calls)}")
    print(f"   • Total Quotes: {int(total_quotes)}")
    print(f"   • Total Deals: {int(total_deals)}")
    print(f"   • Total Purchases: {int(total_purchases)}")
    print(f"   • Total Conversion Value: ${total_value:,.2f}")
    print(f"   • Overall ROAS: {total_roas:.2f}x")

    # Get quotes by date for this campaign
    query_quotes = f"""
        SELECT
            ad_group.name,
            segments.date,
            segments.conversion_action_name,
            metrics.conversions
        FROM ad_group
        WHERE campaign.id = {campaign_id}
            AND segments.date BETWEEN '{start_date}' AND '{end_date}'
            AND metrics.conversions > 0
            AND segments.conversion_action_name LIKE '%quote%'
        ORDER BY segments.date DESC
    """

    response_quotes = ga_service.search(customer_id=customer_id, query=query_quotes)

    # Organize quotes by ad group
    ad_group_quotes = defaultdict(list)

    for row in response_quotes:
        ad_group = row.ad_group.name
        date = row.segments.date
        conv_name = row.segments.conversion_action_name
        conversions = row.metrics.conversions

        ad_group_quotes[ad_group].append({
            'date': date,
            'conv_name': conv_name,
            'conversions': conversions
        })

    # Sort ad groups by spend
    sorted_ad_groups = sorted(ad_group_data.items(), key=lambda x: x[1]['spend'], reverse=True)

    print(f"\n📊 AD GROUP PERFORMANCE:")
    print("=" * 200)
    print(f"\n{'Ad Group':<50} {'Status':<12} {'Spend':>12} {'Clicks':>8} {'CPC':>8} {'Calls':>7} {'Quotes':>7} {'Deals':>7} {'Value':>14} {'ROAS':>8} {'Quote Fresh':>12}")
    print("-" * 200)

    for ad_group, data in sorted_ad_groups:
        if data['spend'] == 0:
            continue

        status = data['status'].replace('AdGroupStatus.', '')
        spend = data['spend']
        clicks = data['clicks']

        # Calculate conversions by type for this ad group
        calls = sum(count for conv_type, count in data['conversions_by_type'].items() if 'Phone Call' in conv_type or 'Calls from ads' in conv_type)
        quotes = sum(count for conv_type, count in data['conversions_by_type'].items() if 'quote' in conv_type.lower())
        deals = sum(count for conv_type, count in data['conversions_by_type'].items() if 'Closed Won' in conv_type)
        purchases = sum(count for conv_type, count in data['conversions_by_type'].items() if 'purchase' in conv_type.lower())

        value = sum(data['conversion_value_by_type'].values())
        cpc = spend / clicks if clicks > 0 else 0
        roas = value / spend if spend > 0 else 0

        status_icon = "🟢" if status == 'ENABLED' else "⏸️" if status == 'PAUSED' else "🔴"
        status_display = f"{status_icon} {status[:8]}"

        ag_display = ad_group[:47] + "..." if len(ad_group) > 50 else ad_group

        # Check quote freshness
        quote_freshness = ""
        if ad_group in ad_group_quotes:
            quotes_list = ad_group_quotes[ad_group]
            most_recent_date = max(quotes_list, key=lambda x: x['date'])['date']
            most_recent_date_obj = datetime.strptime(most_recent_date, '%Y-%m-%d')
            days_since_last = (datetime(2026, 2, 23) - most_recent_date_obj).days

            if days_since_last == 0:
                quote_freshness = f"TODAY 🔥"
            elif days_since_last <= 3:
                quote_freshness = f"{days_since_last}d ago ✅"
            elif days_since_last <= 7:
                quote_freshness = f"{days_since_last}d ago ⚠️"
            else:
                quote_freshness = f"{days_since_last}d ago ❌"

        print(f"{ag_display:<50} {status_display:<12} ${spend:>11,.2f} {clicks:>8} ${cpc:>7.2f} {int(calls):>7} {int(quotes):>7} {int(deals):>7} ${value:>13,.2f} {roas:>7.2f}x {quote_freshness:>12}")

        # Determine action
        total_conversions = deals + purchases

        # Decision logic for expansion campaigns
        if total_conversions > 0 and roas >= 2.0:
            action = "✅ KEEP ON"
            reason = f"Profitable: {roas:.2f}x ROAS, {int(total_conversions)} deals/purchases"
        elif quote_freshness and ("TODAY" in quote_freshness or "✅" in quote_freshness):
            action = "⚠️  MONITOR"
            reason = f"Fresh quotes ({int(quotes)} quotes, most recent {quote_freshness.replace('✅', '').strip()})"
        elif quotes > 2 and days_since_last <= 7:
            action = "⚠️  MONITOR"
            reason = f"Multiple quotes ({int(quotes)}) from last week"
        elif spend > 200 and total_conversions == 0 and quotes == 0:
            action = "🔴 TURN OFF"
            reason = f"Burning ${spend:,.0f} with no quotes or deals"
        elif spend > 100 and roas < 0.5:
            action = "🔴 TURN OFF"
            reason = f"Poor ROAS: {roas:.2f}x after ${spend:,.0f}"
        elif spend < 100 and total_conversions == 0:
            action = "🔴 TURN OFF"
            reason = f"Low spend ${spend:,.0f}, no results"
        else:
            action = "🔴 TURN OFF"
            reason = f"No meaningful activity - expansion not working"

        all_recommendations.append({
            'campaign': campaign_name,
            'ad_group': ad_group,
            'action': action,
            'reason': reason,
            'spend': spend,
            'roas': roas,
            'deals': deals,
            'purchases': purchases,
            'quotes': quotes,
            'calls': calls,
            'value': value,
            'quote_freshness': quote_freshness
        })

    # Campaign-level assessment
    print(f"\n\n{'='*200}")
    print(f"📋 CAMPAIGN-LEVEL ASSESSMENT: {campaign_name}")
    print(f"{'='*200}")

    if total_roas >= 2.0 and total_conversions > 0:
        print(f"\n✅ PROFITABLE EXPANSION - Keep Running")
        print(f"   • {total_roas:.2f}x ROAS with {int(total_conversions)} deals/purchases")
    elif total_quotes > 3 and any("✅" in rec['quote_freshness'] or "TODAY" in rec['quote_freshness'] for rec in all_recommendations if rec['campaign'] == campaign_name):
        print(f"\n⚠️  HAS FRESH QUOTES - Monitor Closely")
        print(f"   • {int(total_quotes)} quotes, some very recent")
        print(f"   • Current ROAS: {total_roas:.2f}x")
    elif total_spend > 500:
        print(f"\n🔴 TURN OFF ENTIRE CAMPAIGN")
        print(f"   • Spending ${total_spend:,.2f} with {total_roas:.2f}x ROAS")
        print(f"   • {int(total_deals)} deals, {int(total_quotes)} quotes - not enough traction")
    else:
        print(f"\n🔴 TURN OFF ENTIRE CAMPAIGN")
        print(f"   • Expansion not performing - reallocate budget to core campaigns")

# Final Summary
print("\n\n" + "=" * 200)
print("📊 FINAL EXPANSION CAMPAIGNS SUMMARY")
print("=" * 200)

# Group recommendations by action
keep_on = [r for r in all_recommendations if '✅' in r['action']]
monitor = [r for r in all_recommendations if '⚠️' in r['action']]
turn_off = [r for r in all_recommendations if '🔴' in r['action']]

print(f"\n\n{'='*200}")
print("✅ AD GROUPS TO KEEP ON (Profitable)")
print(f"{'='*200}")

if keep_on:
    current_campaign = None
    for rec in sorted(keep_on, key=lambda x: (x['campaign'], -x['roas'])):
        if rec['campaign'] != current_campaign:
            current_campaign = rec['campaign']
            print(f"\n📂 {current_campaign}")
        print(f"   ✅ {rec['ad_group']:<60} | ${rec['spend']:>8,.0f} → ${rec['value']:>8,.0f} | {rec['roas']:.2f}x ROAS")
        print(f"      → {rec['reason']}")
else:
    print("\n   ❌ No profitable ad groups found in expansion campaigns")

print(f"\n\n{'='*200}")
print("⚠️  AD GROUPS TO MONITOR (Fresh Quotes)")
print(f"{'='*200}")

if monitor:
    current_campaign = None
    for rec in sorted(monitor, key=lambda x: (x['campaign'], x['quote_freshness'])):
        if rec['campaign'] != current_campaign:
            current_campaign = rec['campaign']
            print(f"\n📂 {current_campaign}")
        print(f"   ⚠️  {rec['ad_group']:<60} | {int(rec['quotes'])} quotes | Last: {rec['quote_freshness']}")
        print(f"      ${rec['spend']:,.0f} spent | {int(rec['calls'])} calls | {rec['roas']:.2f}x ROAS")
        print(f"      → {rec['reason']}")
else:
    print("\n   • No ad groups with fresh quotes requiring monitoring")

print(f"\n\n{'='*200}")
print("🔴 AD GROUPS TO TURN OFF (Not Performing)")
print(f"{'='*200}")

if turn_off:
    current_campaign = None
    total_waste = 0
    for rec in sorted(turn_off, key=lambda x: (x['campaign'], -x['spend'])):
        if rec['campaign'] != current_campaign:
            current_campaign = rec['campaign']
            print(f"\n📂 {current_campaign}")
        print(f"   🔴 {rec['ad_group']:<60} | ${rec['spend']:>8,.0f} spent | {rec['roas']:.2f}x ROAS")
        print(f"      {int(rec['calls'])} calls, {int(rec['quotes'])} quotes, {int(rec['deals'])} deals")
        print(f"      → {rec['reason']}")
        total_waste += rec['spend']

    print(f"\n💰 TOTAL POTENTIAL SAVINGS: ${total_waste:,.2f}/month by turning off these ad groups")
else:
    print("\n   • All ad groups are performing")

# Campaign-level summary
print(f"\n\n{'='*200}")
print("🎯 CAMPAIGN-LEVEL RECOMMENDATIONS")
print(f"{'='*200}")

campaign_summary = defaultdict(lambda: {'spend': 0, 'value': 0, 'keep': 0, 'monitor': 0, 'turn_off': 0})

for rec in all_recommendations:
    campaign = rec['campaign']
    campaign_summary[campaign]['spend'] += rec['spend']
    campaign_summary[campaign]['value'] += rec['value']
    if '✅' in rec['action']:
        campaign_summary[campaign]['keep'] += 1
    elif '⚠️' in rec['action']:
        campaign_summary[campaign]['monitor'] += 1
    else:
        campaign_summary[campaign]['turn_off'] += 1

for campaign in sorted(campaign_summary.keys()):
    stats = campaign_summary[campaign]
    roas = stats['value'] / stats['spend'] if stats['spend'] > 0 else 0

    print(f"\n📂 {campaign}")
    print(f"   Spend: ${stats['spend']:,.2f} | Return: ${stats['value']:,.2f} | ROAS: {roas:.2f}x")
    print(f"   Ad Groups: {stats['keep']} keep | {stats['monitor']} monitor | {stats['turn_off']} turn off")

    if stats['keep'] > 0 or (stats['monitor'] > 0 and roas > 1.0):
        print(f"   ✅ RECOMMENDATION: Keep campaign, turn off {stats['turn_off']} underperforming ad groups")
    elif stats['monitor'] > 0 and stats['turn_off'] == 0:
        print(f"   ⚠️  RECOMMENDATION: Monitor for 7 days, evaluate quote conversions")
    else:
        print(f"   🔴 RECOMMENDATION: TURN OFF ENTIRE CAMPAIGN - not gaining traction")

print(f"\n\n{'='*200}")
print("💡 EXECUTIVE SUMMARY")
print(f"{'='*200}")

total_expansion_spend = sum(rec['spend'] for rec in all_recommendations)
total_expansion_value = sum(rec['value'] for rec in all_recommendations)
total_expansion_roas = total_expansion_value / total_expansion_spend if total_expansion_spend > 0 else 0

total_keep_spend = sum(rec['spend'] for rec in keep_on)
total_turn_off_spend = sum(rec['spend'] for rec in turn_off)

print(f"\n📊 Overall Expansion Performance:")
print(f"   • Total Spend: ${total_expansion_spend:,.2f}")
print(f"   • Total Return: ${total_expansion_value:,.2f}")
print(f"   • Overall ROAS: {total_expansion_roas:.2f}x")
print(f"   • Profit/Loss: ${total_expansion_value - total_expansion_spend:,.2f}")

print(f"\n💰 Budget Optimization:")
print(f"   • Currently Profitable: ${total_keep_spend:,.2f} ({total_keep_spend/total_expansion_spend*100 if total_expansion_spend > 0 else 0:.1f}%)")
print(f"   • Wasted Spend: ${total_turn_off_spend:,.2f} ({total_turn_off_spend/total_expansion_spend*100 if total_expansion_spend > 0 else 0:.1f}%)")
print(f"   • Potential Monthly Savings: ${total_turn_off_spend:,.2f}")

print(f"\n🎯 Action Items:")
print(f"   1. Turn off {len(turn_off)} underperforming ad groups immediately")
print(f"   2. Monitor {len(monitor)} ad groups with fresh quotes for 7 days")
print(f"   3. Keep {len(keep_on)} profitable ad groups running")
if total_keep_spend > 0:
    print(f"   4. Consider reallocating ${total_turn_off_spend:,.2f} to profitable expansion ad groups")
else:
    print(f"   4. Reallocate ${total_turn_off_spend:,.2f} to core campaigns (Dozers, Forklift, Loaders)")

print("\n" + "=" * 200)
