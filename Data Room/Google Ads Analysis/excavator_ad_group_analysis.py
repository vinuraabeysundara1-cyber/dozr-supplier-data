from google.ads.googleads.client import GoogleAdsClient
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Load credentials
client = GoogleAdsClient.load_from_storage('/Users/vinuraabeysundara/Desktop/ICG/DOZR/Data Room/Config/google-ads.yaml')
ga_service = client.get_service('GoogleAdsService')
customer_id = '8531896842'

print("=" * 160)
print("EXCAVATOR CAMPAIGN - AD GROUP PERFORMANCE ANALYSIS")
print("Period: February 1-23, 2026")
print("=" * 160)

start_date = '2026-02-01'
end_date = '2026-02-23'

# Get all Excavator campaigns
query_campaigns = """
    SELECT
        campaign.id,
        campaign.name,
        campaign.status
    FROM campaign
    WHERE campaign.name LIKE '%Excavator%'
        AND campaign.name LIKE '%US%'
"""

response_campaigns = ga_service.search(customer_id=customer_id, query=query_campaigns)

excavator_campaigns = []
for row in response_campaigns:
    excavator_campaigns.append({
        'id': row.campaign.id,
        'name': row.campaign.name,
        'status': str(row.campaign.status)
    })

print(f"\n✅ Found {len(excavator_campaigns)} Excavator campaign(s):")
for camp in excavator_campaigns:
    status_icon = "🟢" if camp['status'] == 'CampaignStatus.ENABLED' else "🔴"
    print(f"   {status_icon} {camp['name']} (Status: {camp['status']})")

# Analyze each campaign
for campaign in excavator_campaigns:
    campaign_name = campaign['name']
    campaign_id = campaign['id']

    print(f"\n\n{'='*160}")
    print(f"📊 CAMPAIGN: {campaign_name}")
    print(f"{'='*160}")

    # Get metrics by ad group
    query_metrics = f"""
        SELECT
            ad_group.name,
            ad_group.status,
            metrics.cost_micros,
            metrics.clicks,
            metrics.impressions,
            metrics.conversions
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
        'calls': 0,
        'deals': 0,
        'purchases': 0,
        'value': 0
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

    # Get conversions by ad group
    query_conv = f"""
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

    response_conv = ga_service.search(customer_id=customer_id, query=query_conv)

    for row in response_conv:
        ad_group = row.ad_group.name
        conv_name = row.segments.conversion_action_name
        conversions = row.metrics.conversions
        value = row.metrics.conversions_value

        if 'Phone Call' in conv_name or 'Calls from ads' in conv_name:
            ad_group_data[ad_group]['calls'] += conversions
        elif 'Closed Won' in conv_name:
            ad_group_data[ad_group]['deals'] += conversions
            ad_group_data[ad_group]['value'] += value
        elif 'purchase' in conv_name.lower():
            ad_group_data[ad_group]['purchases'] += conversions
            ad_group_data[ad_group]['value'] += value

    # Calculate totals
    total_spend = sum(d['spend'] for d in ad_group_data.values())
    total_clicks = sum(d['clicks'] for d in ad_group_data.values())
    total_impressions = sum(d['impressions'] for d in ad_group_data.values())
    total_calls = sum(d['calls'] for d in ad_group_data.values())
    total_deals = sum(d['deals'] for d in ad_group_data.values())
    total_value = sum(d['value'] for d in ad_group_data.values())
    total_roas = total_value / total_spend if total_spend > 0 else 0

    # Print summary
    print(f"\n📈 CAMPAIGN SUMMARY:")
    print(f"   • Total Spend: ${total_spend:,.2f}")
    print(f"   • Total Clicks: {total_clicks:,}")
    print(f"   • Total Impressions: {total_impressions:,}")
    print(f"   • Total Calls: {int(total_calls)}")
    print(f"   • Total Deals: {int(total_deals)}")
    print(f"   • Total Value: ${total_value:,.2f}")
    print(f"   • ROAS: {total_roas:.2f}x")

    # Sort by spend
    sorted_ad_groups = sorted(ad_group_data.items(), key=lambda x: x[1]['spend'], reverse=True)

    print(f"\n📊 AD GROUP PERFORMANCE:")
    print("-" * 160)
    print(f"\n{'Ad Group':<60} {'Status':<15} {'Spend':>12} {'Clicks':>8} {'CTR':>8} {'CPC':>10} {'Calls':>8} {'Deals':>7} {'Value':>14} {'ROAS':>8}")
    print("-" * 160)

    recommendations = []

    for ad_group, data in sorted_ad_groups:
        status = data['status'].replace('AdGroupStatus.', '')
        spend = data['spend']
        clicks = data['clicks']
        impressions = data['impressions']
        calls = int(data['calls'])
        deals = int(data['deals'])
        value = data['value']

        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        cpc = spend / clicks if clicks > 0 else 0
        roas = value / spend if spend > 0 else 0

        # Determine status icon
        if status == 'ENABLED':
            status_icon = "🟢"
        elif status == 'PAUSED':
            status_icon = "⏸️"
        else:
            status_icon = "🔴"

        status_display = f"{status_icon} {status}"

        # Truncate ad group name
        ag_display = ad_group[:57] + "..." if len(ad_group) > 60 else ad_group

        print(f"{ag_display:<60} {status_display:<15} ${spend:>11,.2f} {clicks:>8} {ctr:>7.2f}% ${cpc:>9.2f} {calls:>8} {deals:>7} ${value:>13,.2f} {roas:>7.2f}x")

        # Generate recommendation
        if spend > 0:
            if deals > 0 and roas >= 2.0:
                action = "✅ KEEP ON"
                reason = f"Profitable: {roas:.2f}x ROAS, {deals} deals"
                priority = 1
            elif calls > 5 and deals == 0:
                action = "⚠️  MONITOR"
                reason = f"Getting calls ({calls}) but no deals yet"
                priority = 2
            elif spend > 500 and deals == 0 and calls < 3:
                action = "🔴 TURN OFF"
                reason = f"Burning ${spend:,.0f} with no results"
                priority = 3
            elif spend > 200 and roas < 1.0:
                action = "🔴 TURN OFF"
                reason = f"Unprofitable: {roas:.2f}x ROAS after ${spend:,.0f} spend"
                priority = 3
            elif spend > 100 and clicks < 5:
                action = "🔴 TURN OFF"
                reason = f"Poor engagement: Only {clicks} clicks for ${spend:,.0f}"
                priority = 3
            elif spend < 100:
                action = "⏸️  PAUSE"
                reason = "Low spend, needs more data or pause to save budget"
                priority = 2
            else:
                action = "⚠️  MONITOR"
                reason = "Needs more time to evaluate"
                priority = 2

            recommendations.append({
                'ad_group': ad_group,
                'action': action,
                'reason': reason,
                'priority': priority,
                'spend': spend,
                'roas': roas,
                'deals': deals,
                'calls': calls
            })

    # Print recommendations
    print("\n\n" + "=" * 160)
    print("🎯 RECOMMENDATIONS BY AD GROUP")
    print("=" * 160)

    # Group by action
    keep_on = [r for r in recommendations if '✅' in r['action']]
    monitor = [r for r in recommendations if '⚠️' in r['action']]
    turn_off = [r for r in recommendations if '🔴' in r['action']]
    pause = [r for r in recommendations if '⏸️' in r['action']]

    if keep_on:
        print(f"\n✅ KEEP ON ({len(keep_on)} ad groups):")
        for rec in sorted(keep_on, key=lambda x: x['roas'], reverse=True):
            print(f"   • {rec['ad_group']:<60} → {rec['reason']}")
    else:
        print(f"\n✅ KEEP ON (0 ad groups)")
        print(f"   • No profitable ad groups found")

    if monitor:
        print(f"\n⚠️  MONITOR ({len(monitor)} ad groups):")
        for rec in sorted(monitor, key=lambda x: x['calls'], reverse=True):
            print(f"   • {rec['ad_group']:<60} → {rec['reason']}")

    if pause:
        print(f"\n⏸️  PAUSE ({len(pause)} ad groups):")
        for rec in sorted(pause, key=lambda x: x['spend'], reverse=True):
            print(f"   • {rec['ad_group']:<60} → {rec['reason']}")

    if turn_off:
        print(f"\n🔴 TURN OFF ({len(turn_off)} ad groups):")
        for rec in sorted(turn_off, key=lambda x: x['spend'], reverse=True):
            print(f"   • {rec['ad_group']:<60} → {rec['reason']}")

    # Overall campaign recommendation
    print("\n\n" + "=" * 160)
    print("🎯 OVERALL CAMPAIGN RECOMMENDATION")
    print("=" * 160)

    if total_roas < 0.5 and total_spend > 2000:
        print(f"\n🔴 RECOMMENDATION: PAUSE ENTIRE CAMPAIGN")
        print(f"\n   Reason:")
        print(f"   • Spending ${total_spend:,.2f} with only ${total_value:,.2f} in return")
        print(f"   • ROAS: {total_roas:.2f}x (need at least 2.0x)")
        print(f"   • Only {int(total_deals)} deals from {int(total_calls)} calls")
        print(f"   • Burning ~${total_spend/23:.2f} per day with minimal return")
        print(f"\n   Alternative:")
        print(f"   • Pause campaign entirely and restructure")
        print(f"   • Focus budget on high-performing campaigns (Dozers, Forklift)")
        print(f"   • Potential savings: ~${total_spend*30/23:,.2f} per month")
    elif len(keep_on) > 0:
        print(f"\n✅ RECOMMENDATION: KEEP CAMPAIGN ACTIVE")
        print(f"\n   • {len(keep_on)} ad group(s) are profitable")
        print(f"   • Turn off {len(turn_off)} underperforming ad group(s)")
        print(f"   • Monitor {len(monitor)} ad group(s) for improvement")
    else:
        print(f"\n⚠️  RECOMMENDATION: MAJOR RESTRUCTURE NEEDED")
        print(f"\n   • No profitable ad groups found")
        print(f"   • Consider pausing and rebuilding with better keywords")
        print(f"   • Current ROAS {total_roas:.2f}x is not sustainable")

    # Action items
    print("\n\n" + "=" * 160)
    print("📋 ACTION ITEMS")
    print("=" * 160)

    print(f"\n⏱️  IMMEDIATE (Do this now):")
    if turn_off:
        for rec in sorted(turn_off, key=lambda x: x['spend'], reverse=True)[:5]:
            print(f"   ☐ Turn off: {rec['ad_group'][:70]}")
            print(f"      → Saving ${rec['spend']:,.2f} with {rec['roas']:.2f}x ROAS")
    else:
        print(f"   • No ad groups to turn off")

    print(f"\n📊 WITHIN 7 DAYS:")
    if monitor:
        print(f"   ☐ Review search terms for monitored ad groups")
        print(f"   ☐ Add negative keywords to improve quality")
        print(f"   ☐ Check if any monitored ad groups convert to deals")

    if total_roas < 0.5:
        print(f"   ☐ Consider pausing entire campaign if ROAS doesn't improve")

    print(f"\n🔄 LONG-TERM:")
    print(f"   ☐ Restructure campaign with learnings from Dozers campaign")
    print(f"   ☐ Focus on specific excavator types (mini, 50 ton+, etc.)")
    print(f"   ☐ Test with small budget ($500/week) before scaling")

# Summary across all campaigns
print("\n\n" + "=" * 160)
print("📊 EXCAVATOR CAMPAIGNS SUMMARY")
print("=" * 160)

print(f"\n✅ Analysis complete for {len(excavator_campaigns)} campaign(s)")
print(f"\n💡 KEY TAKEAWAYS:")
print(f"   1. Excavator campaigns have historically low ROAS")
print(f"   2. Most ad groups are burning budget without returns")
print(f"   3. Consider reallocating budget to Dozers/Forklift campaigns")
print(f"   4. If keeping active, focus only on profitable ad groups")

print("\n" + "=" * 160)
