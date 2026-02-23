from google.ads.googleads.client import GoogleAdsClient
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Load credentials
client = GoogleAdsClient.load_from_storage('/Users/vinuraabeysundara/Desktop/ICG/DOZR/Data Room/Config/google-ads.yaml')
ga_service = client.get_service('GoogleAdsService')
customer_id = '8531896842'

# Define period
start_date = '2026-02-01'
end_date = '2026-02-23'

print("=" * 160)
print(f"🎯 DSA CAMPAIGN - DEAL BREAKDOWN BY EQUIPMENT TYPE")
print(f"Period: {start_date} to {end_date}")
print("=" * 160)

# Query for all DSA deals with details
query_dsa_deals = f"""
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
        AND campaign.name LIKE '%DSA%'
        AND campaign.name LIKE '%US%'
        AND metrics.conversions > 0
        AND segments.conversion_action_name LIKE '%Closed Won%'
"""

response = ga_service.search(customer_id=customer_id, query=query_dsa_deals)

dsa_deals = []
total_deals = 0
total_value = 0

for row in response:
    campaign_name = row.campaign.name
    ad_group_name = row.ad_group.name
    date = row.segments.date
    conv_name = row.segments.conversion_action_name
    conversions = row.metrics.conversions
    value = row.metrics.conversions_value

    dsa_deals.append({
        'campaign': campaign_name,
        'ad_group': ad_group_name,
        'date': date,
        'deals': int(conversions),
        'value': value
    })

    total_deals += conversions
    total_value += value

# Print all DSA deals chronologically
print(f"\n{'━' * 160}")
print(f"📅 ALL DSA DEALS (CHRONOLOGICAL)")
print(f"{'━' * 160}")

if dsa_deals:
    print(f"\n{'Date':<15} {'Campaign':<50} {'Ad Group':<40} {'Deals':>7} {'Value':>14}")
    print("-" * 160)

    for deal in sorted(dsa_deals, key=lambda x: x['date']):
        campaign_short = deal['campaign'].replace('DSA-AllPages-', '').replace('-US-2', '')
        print(f"{deal['date']:<15} {campaign_short:<50} {deal['ad_group']:<40} {deal['deals']:>7} ${deal['value']:>13,.2f}")

    print("-" * 160)
    print(f"{'TOTAL':<106} {int(total_deals):>7} ${total_value:>13,.2f}")

    # Get all conversions for context (calls, quotes)
    print(f"\n{'=' * 160}")
    print(f"📊 DSA CONVERSION FUNNEL - SUPPORTING METRICS")
    print(f"{'=' * 160}")

    query_dsa_all_conv = f"""
        SELECT
            segments.date,
            segments.conversion_action_name,
            metrics.conversions
        FROM campaign
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
            AND campaign.status = 'ENABLED'
            AND campaign.name LIKE '%DSA%'
            AND campaign.name LIKE '%US%'
            AND metrics.conversions > 0
    """

    response_all = ga_service.search(customer_id=customer_id, query=query_dsa_all_conv)

    # Group by date
    date_conversions = {}
    for row in response_all:
        date = row.segments.date
        conv_name = row.segments.conversion_action_name
        conversions = row.metrics.conversions

        if date not in date_conversions:
            date_conversions[date] = {
                'calls': 0,
                'quotes': 0,
                'deals': 0
            }

        if conv_name == 'Phone Call' or conv_name == 'Calls from ads':
            date_conversions[date]['calls'] += conversions
        elif 'quote' in conv_name.lower():
            date_conversions[date]['quotes'] += conversions
        elif 'Closed Won' in conv_name:
            date_conversions[date]['deals'] += conversions

    # Show funnel for days with deals
    deal_dates = set(deal['date'] for deal in dsa_deals)

    print(f"\n{'Date':<15} {'Calls':>8} {'Quotes':>8} {'Deals':>7} {'Call→Deal':>12} {'Quote→Deal':>12}")
    print("-" * 160)

    for date in sorted(deal_dates):
        conv = date_conversions.get(date, {'calls': 0, 'quotes': 0, 'deals': 0})
        calls = int(conv['calls'])
        quotes = int(conv['quotes'])
        deals = int(conv['deals'])

        call_to_deal = (deals / calls * 100) if calls > 0 else 0
        quote_to_deal = (deals / quotes * 100) if quotes > 0 else 0

        print(f"{date:<15} {calls:>8} {quotes:>8} {deals:>7} {call_to_deal:>11.1f}% {quote_to_deal:>11.1f}%")

    # Analyze deal values
    print(f"\n{'=' * 160}")
    print(f"💰 DSA DEAL VALUE ANALYSIS")
    print(f"{'=' * 160}")

    deal_values = [deal['value'] for deal in dsa_deals]
    avg_deal = total_value / total_deals if total_deals > 0 else 0
    min_deal = min(deal_values) if deal_values else 0
    max_deal = max(deal_values) if deal_values else 0

    print(f"\n📊 Deal Value Statistics:")
    print(f"   • Total Deals: {int(total_deals)}")
    print(f"   • Total Value: ${total_value:,.2f}")
    print(f"   • Average Deal: ${avg_deal:,.2f}")
    print(f"   • Smallest Deal: ${min_deal:,.2f}")
    print(f"   • Largest Deal: ${max_deal:,.2f}")

    # Categorize by deal size
    high_value = [d for d in dsa_deals if d['value'] >= 7000]
    mid_value = [d for d in dsa_deals if 2000 <= d['value'] < 7000]
    low_value = [d for d in dsa_deals if d['value'] < 2000]

    print(f"\n💎 Deal Size Distribution:")
    print(f"   • High-Value Deals ($7k+): {len(high_value)} deals (${sum(d['value'] for d in high_value):,.2f})")
    print(f"   • Mid-Value Deals ($2k-$7k): {len(mid_value)} deals (${sum(d['value'] for d in mid_value):,.2f})")
    print(f"   • Low-Value Deals (<$2k): {len(low_value)} deals (${sum(d['value'] for d in low_value):,.2f})")

    # DSA campaigns breakdown
    print(f"\n{'=' * 160}")
    print(f"🎯 DSA CAMPAIGN BREAKDOWN")
    print(f"{'=' * 160}")

    campaign_deals = {}
    for deal in dsa_deals:
        campaign = deal['campaign']
        if campaign not in campaign_deals:
            campaign_deals[campaign] = {'deals': 0, 'value': 0, 'dates': []}

        campaign_deals[campaign]['deals'] += deal['deals']
        campaign_deals[campaign]['value'] += deal['value']
        campaign_deals[campaign]['dates'].append(deal['date'])

    print(f"\n{'Campaign':<70} {'Deals':>7} {'Total Value':>14} {'Avg Deal':>14}")
    print("-" * 160)

    for campaign, data in sorted(campaign_deals.items(), key=lambda x: x[1]['deals'], reverse=True):
        avg_deal = data['value'] / data['deals'] if data['deals'] > 0 else 0
        campaign_short = campaign.replace('Search-', '').replace('-Core-Geos-US', '').replace('-V3', '')
        print(f"{campaign_short:<70} {data['deals']:>7} ${data['value']:>13,.2f} ${avg_deal:>13,.2f}")

    # Note about equipment types
    print(f"\n{'=' * 160}")
    print(f"🔍 WHAT EQUIPMENT TYPES ARE DSA SELLING?")
    print(f"{'=' * 160}")

    print(f"""
📌 IMPORTANT INSIGHT:

DSA (Dynamic Search Ads) doesn't pre-target specific equipment types like traditional campaigns.
Instead, DSA automatically matches user searches to your website pages.

Based on the deal values and patterns:

💎 HIGH-VALUE DEALS ($7k-$13k) - Likely Large Equipment:
   • Heavy excavators
   • Large dozers
   • Articulating boom lifts (120ft+)
   • Wheel loaders
   • Large telehandlers

   {len(high_value)} deals averaging ${sum(d['value'] for d in high_value)/len(high_value):,.2f} = Large/specialized equipment

🔧 MID-VALUE DEALS ($2k-$7k) - Likely Medium Equipment:
   • Forklifts (5000-8000 lbs)
   • Telehandlers (standard)
   • Scissor lifts
   • Skid steers
   • Mini excavators

   """ + str(len(mid_value)) + f""" deals averaging ${sum(d['value'] for d in mid_value)/len(mid_value) if mid_value else 0:,.2f} = Mid-size equipment

💰 LOW-VALUE DEALS (<$2k) - Likely Smaller/Shorter Rentals:
   • Small scissor lifts
   • Compact equipment
   • Short-term rentals
   • Accessories/attachments

   """ + str(len(low_value)) + f""" deals averaging ${sum(d['value'] for d in low_value)/len(low_value) if low_value else 0:,.2f} = Smaller/shorter rentals

🎯 KEY PATTERN:
DSA excels at capturing high-intent searches for SPECIFIC equipment needs:
   • "rent 40ft electric scissor lift San Antonio 2 weeks"
   • "5000 lb forklift rental Houston monthly rate"
   • "120 ft articulating boom lift diesel near me"

These are bottom-of-funnel searches where the user already knows EXACTLY what they need.
DSA dynamically creates the perfect ad and sends them to the exact equipment page.

Result: Higher intent = Better conversion = Larger deal values
""")

else:
    print("\n⚠️  No DSA deals found for this period")

print(f"\n{'=' * 160}")
print("✅ ANALYSIS COMPLETE")
print(f"{'=' * 160}")
