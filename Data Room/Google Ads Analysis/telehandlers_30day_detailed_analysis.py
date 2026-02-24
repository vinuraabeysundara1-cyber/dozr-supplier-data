from google.ads.googleads.client import GoogleAdsClient
from collections import defaultdict
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Load credentials
client = GoogleAdsClient.load_from_storage('/Users/vinuraabeysundara/Desktop/ICG/DOZR/Data Room/Config/google-ads.yaml')
ga_service = client.get_service('GoogleAdsService')
customer_id = '8531896842'

print("=" * 180)
print("TELEHANDLERS CAMPAIGNS - COMPLETE 30-DAY ANALYSIS WITH ALL CONVERSIONS")
print("Period: January 24 - February 23, 2026 (30 days)")
print("=" * 180)

start_date = '2026-01-24'
end_date = '2026-02-23'

# Get all Telehandler campaigns
query_campaigns = """
    SELECT
        campaign.id,
        campaign.name,
        campaign.status
    FROM campaign
    WHERE campaign.name LIKE '%Telehandler%'
        AND campaign.name LIKE '%US%'
"""

response_campaigns = ga_service.search(customer_id=customer_id, query=query_campaigns)

telehandler_campaigns = []
for row in response_campaigns:
    telehandler_campaigns.append({
        'id': row.campaign.id,
        'name': row.campaign.name,
        'status': str(row.campaign.status)
    })

print(f"\n✅ Found {len(telehandler_campaigns)} Telehandler campaign(s)")

# Analyze each campaign
for campaign in telehandler_campaigns:
    campaign_name = campaign['name']
    campaign_id = campaign['id']

    print(f"\n\n{'='*180}")
    print(f"📊 CAMPAIGN: {campaign_name}")
    print(f"{'='*180}")

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
    print(f"   • Total Impressions: {total_impressions:,}")
    print(f"   • Avg CPC: ${total_spend/total_clicks if total_clicks > 0 else 0:.2f}")
    print(f"   • Total Calls: {int(total_calls)}")
    print(f"   • Total Quotes: {int(total_quotes)}")
    print(f"   • Total Deals: {int(total_deals)}")
    print(f"   • Total Purchases: {int(total_purchases)}")
    print(f"   • Total Conversion Value: ${total_value:,.2f}")
    print(f"   • Overall ROAS: {total_roas:.2f}x")

    # Show all conversion types
    if all_conv_types:
        print(f"\n📊 ALL CONVERSION TYPES:")
        print("-" * 180)
        print(f"{'Conversion Type':<60} {'Count':>10} {'Value':>15} {'Avg Value':>15}")
        print("-" * 180)
        for conv_type in sorted(all_conv_types.keys()):
            count = all_conv_types[conv_type]
            value = all_conv_values[conv_type]
            avg_value = value / count if count > 0 else 0
            print(f"{conv_type:<60} {int(count):>10} ${value:>14,.2f} ${avg_value:>14,.2f}")

    # Sort ad groups by spend
    sorted_ad_groups = sorted(ad_group_data.items(), key=lambda x: x[1]['spend'], reverse=True)

    print(f"\n\n📊 AD GROUP PERFORMANCE (30 DAYS):")
    print("=" * 180)
    print(f"\n{'Ad Group':<50} {'Status':<12} {'Spend':>12} {'Clicks':>8} {'CPC':>8} {'Calls':>7} {'Quotes':>7} {'Deals':>7} {'Purch':>7} {'Value':>14} {'ROAS':>8}")
    print("-" * 180)

    recommendations = []

    for ad_group, data in sorted_ad_groups:
        if data['spend'] == 0:
            continue

        status = data['status'].replace('AdGroupStatus.', '')
        spend = data['spend']
        clicks = data['clicks']
        impressions = data['impressions']

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

        print(f"{ag_display:<50} {status_display:<12} ${spend:>11,.2f} {clicks:>8} ${cpc:>7.2f} {int(calls):>7} {int(quotes):>7} {int(deals):>7} {int(purchases):>7} ${value:>13,.2f} {roas:>7.2f}x")

        # Show detailed conversion breakdown for this ad group if it has any
        if data['conversions_by_type']:
            print(f"   └─ Conversions: ", end="")
            conv_summary = []
            for conv_type, count in sorted(data['conversions_by_type'].items(), key=lambda x: x[1], reverse=True):
                conv_summary.append(f"{conv_type}: {int(count)}")
            print(", ".join(conv_summary))

        # Determine action
        total_conversions = deals + purchases
        if total_conversions > 0 and roas >= 2.0:
            action = "✅ KEEP ON"
            reason = f"Profitable: {roas:.2f}x ROAS, {int(total_conversions)} deals/purchases"
        elif total_conversions > 0 and roas >= 1.0:
            action = "⚠️  MONITOR"
            reason = f"Breaking even: {roas:.2f}x ROAS, {int(total_conversions)} conversions"
        elif quotes > 2:
            action = "⚠️  MONITOR"
            reason = f"Getting quotes ({int(quotes)}) - may convert soon"
        elif calls > 5 and total_conversions == 0:
            action = "⚠️  MONITOR"
            reason = f"Getting calls ({int(calls)}) but no deals yet"
        elif spend > 500 and total_conversions == 0:
            action = "🔴 TURN OFF"
            reason = f"Burning ${spend:,.0f} with 0 deals"
        elif roas < 0.5 and spend > 200:
            action = "🔴 TURN OFF"
            reason = f"Poor ROAS: {roas:.2f}x after ${spend:,.0f}"
        else:
            action = "⚠️  MONITOR"
            reason = "Needs evaluation"

        recommendations.append({
            'ad_group': ad_group,
            'action': action,
            'reason': reason,
            'spend': spend,
            'roas': roas,
            'deals': deals,
            'purchases': purchases,
            'quotes': quotes,
            'calls': calls,
            'value': value
        })

    # Print recommendations
    print("\n\n" + "=" * 180)
    print("🎯 RECOMMENDATIONS BY AD GROUP")
    print("=" * 180)

    keep_on = [r for r in recommendations if '✅' in r['action']]
    monitor = [r for r in recommendations if '⚠️' in r['action']]
    turn_off = [r for r in recommendations if '🔴' in r['action']]

    if keep_on:
        print(f"\n✅ KEEP ON ({len(keep_on)} ad groups):")
        for rec in sorted(keep_on, key=lambda x: x['roas'], reverse=True):
            print(f"   • {rec['ad_group']:<60} → {rec['reason']}")
            print(f"     Performance: ${rec['spend']:,.2f} → ${rec['value']:,.2f} | {int(rec['deals'])} deals, {int(rec['purchases'])} purchases")
    else:
        print(f"\n✅ KEEP ON (0 ad groups)")
        print(f"   • No profitable ad groups found")

    if monitor:
        print(f"\n⚠️  MONITOR ({len(monitor)} ad groups):")
        for rec in sorted(monitor, key=lambda x: x['value'], reverse=True):
            print(f"   • {rec['ad_group']:<60} → {rec['reason']}")
            print(f"     Activity: {int(rec['calls'])} calls, {int(rec['quotes'])} quotes, {int(rec['deals'])} deals, {int(rec['purchases'])} purchases")

    if turn_off:
        print(f"\n🔴 TURN OFF ({len(turn_off)} ad groups):")
        for rec in sorted(turn_off, key=lambda x: x['spend'], reverse=True):
            print(f"   • {rec['ad_group']:<60} → {rec['reason']}")
            print(f"     Loss: ${rec['spend']:,.2f} spent, ${rec['value']:,.2f} return = {rec['roas']:.2f}x ROAS")

    # Overall recommendation
    print("\n\n" + "=" * 180)
    print("📋 OVERALL CAMPAIGN ASSESSMENT")
    print("=" * 180)

    if total_roas >= 2.0:
        print(f"\n✅ CAMPAIGN IS PROFITABLE")
        print(f"   • {total_roas:.2f}x ROAS is above 2.0x target")
        print(f"   • Keep running, optimize underperforming ad groups")
    elif total_roas >= 1.0:
        print(f"\n⚠️  CAMPAIGN IS BREAKING EVEN")
        print(f"   • {total_roas:.2f}x ROAS means spending $1 to make ${total_roas:.2f}")
        print(f"   • Need to improve to at least 2.0x ROAS")
        print(f"   • Turn off worst performers, keep monitoring others")
    else:
        print(f"\n🔴 CAMPAIGN IS LOSING MONEY")
        print(f"   • {total_roas:.2f}x ROAS means losing ${1-total_roas:.2f} per dollar spent")
        print(f"   • Spending ${total_spend:,.2f} to generate ${total_value:,.2f}")
        print(f"   • Consider pausing entire campaign")

    print(f"\n💰 30-Day Financial Summary:")
    print(f"   • Investment: ${total_spend:,.2f}")
    print(f"   • Return: ${total_value:,.2f}")
    print(f"   • Net: ${total_value - total_spend:,.2f} ({'profit' if total_value > total_spend else 'loss'})")
    print(f"   • Conversion Rate: {(total_deals + total_purchases) / total_calls * 100 if total_calls > 0 else 0:.1f}% (calls → deals)")

    # QUOTE TIMELINE ANALYSIS
    print("\n\n" + "=" * 180)
    print("📅 QUOTE TIMELINE ANALYSIS")
    print("=" * 180)

    # Get quotes by date
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

    # Organize by ad group
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

    # Show quote timeline for ad groups with quotes
    if ad_group_quotes:
        for ad_group in sorted(ad_group_quotes.keys()):
            quotes = ad_group_quotes[ad_group]
            total_quotes = sum(q['conversions'] for q in quotes)

            print(f"\n🔍 {ad_group}")
            print(f"   Total Quotes: {int(total_quotes)}")
            print("-" * 180)
            print(f"   {'Date':<12} {'Days Ago':<10} {'Conversion Type':<50} {'Count':>8}")
            print("-" * 180)

            for quote in sorted(quotes, key=lambda x: x['date'], reverse=True):
                date_obj = datetime.strptime(quote['date'], '%Y-%m-%d')
                today = datetime(2026, 2, 23)
                days_ago = (today - date_obj).days

                print(f"   {quote['date']:<12} {days_ago:<10} {quote['conv_name']:<50} {int(quote['conversions']):>8}")

            # Calculate freshness
            most_recent_date = max(quotes, key=lambda x: x['date'])['date']
            most_recent_date_obj = datetime.strptime(most_recent_date, '%Y-%m-%d')
            days_since_last = (datetime(2026, 2, 23) - most_recent_date_obj).days

            print(f"\n   💡 Quote Freshness:")
            if days_since_last <= 7:
                print(f"      ✅ VERY FRESH - Most recent quote was {days_since_last} days ago")
                print(f"      → High likelihood of conversion - keep monitoring closely")
            elif days_since_last <= 14:
                print(f"      ⚠️  MODERATE - Most recent quote was {days_since_last} days ago")
                print(f"      → Still possible to convert - monitor for another week")
            else:
                print(f"      ❌ OLD - Most recent quote was {days_since_last} days ago")
                print(f"      → Lower likelihood of conversion - consider turning off if no deals soon")
    else:
        print("\n   No quotes found in this campaign during the period")

# Final summary
print("\n\n" + "=" * 180)
print("📊 FINAL RECOMMENDATION")
print("=" * 180)

print(f"\n✅ Based on 30-day data analysis:")
print(f"   • Check 'KEEP ON' ad groups - these are working")
print(f"   • Monitor 'MONITOR' ad groups for another 7-14 days")
print(f"   • Turn off 'TURN OFF' ad groups immediately to stop waste")
print(f"\n💡 If any ad groups show deals/purchases, focus budget there")
print(f"   If no ad groups are profitable, pause the entire campaign")

print("\n" + "=" * 180)
