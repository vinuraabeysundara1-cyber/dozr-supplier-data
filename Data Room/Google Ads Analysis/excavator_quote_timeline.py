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
print("EXCAVATOR CAMPAIGN - QUOTE TIMELINE ANALYSIS")
print("Period: January 24 - February 23, 2026 (30 days)")
print("=" * 160)

start_date = '2026-01-24'
end_date = '2026-02-23'

# Get Excavator campaign ID
query_campaigns = """
    SELECT
        campaign.id,
        campaign.name
    FROM campaign
    WHERE campaign.name LIKE '%Excavator%'
        AND campaign.name LIKE '%Core%'
        AND campaign.name NOT LIKE '%Expansion%'
"""

response_campaigns = ga_service.search(customer_id=customer_id, query=query_campaigns)
campaign_id = None

for row in response_campaigns:
    campaign_id = row.campaign.id
    campaign_name = row.campaign.name
    print(f"\n✅ Campaign: {campaign_name}")
    break

# Get quotes by date for specific ad groups
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

print("\n\n📊 QUOTE TIMELINE BY AD GROUP")
print("=" * 160)

target_ad_groups = ['Large-Excavator-Rental', 'Mini-Excavator']

for ad_group in target_ad_groups:
    if ad_group in ad_group_quotes:
        quotes = ad_group_quotes[ad_group]
        total_quotes = sum(q['conversions'] for q in quotes)

        print(f"\n🔍 {ad_group}")
        print(f"   Total Quotes: {int(total_quotes)}")
        print("-" * 160)
        print(f"   {'Date':<12} {'Days Ago':<10} {'Conversion Type':<50} {'Count':>8}")
        print("-" * 160)

        for quote in sorted(quotes, key=lambda x: x['date'], reverse=True):
            date_obj = datetime.strptime(quote['date'], '%Y-%m-%d')
            today = datetime(2026, 2, 23)
            days_ago = (today - date_obj).days

            print(f"   {quote['date']:<12} {days_ago:<10} {quote['conv_name']:<50} {int(quote['conversions']):>8}")

        # Calculate freshness
        most_recent = min(quotes, key=lambda x: x['date'])
        most_recent_date = datetime.strptime(most_recent['date'], '%Y-%m-%d')
        days_since_last = (datetime(2026, 2, 23) - most_recent_date).days

        print(f"\n   💡 Assessment:")
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
        print(f"\n🔍 {ad_group}")
        print(f"   No quotes found in this period")

# Also check for deals to see conversion timeline
print("\n\n📊 DEALS TIMELINE FOR CONTEXT")
print("=" * 160)

query_deals = f"""
    SELECT
        ad_group.name,
        segments.date,
        segments.conversion_action_name,
        metrics.conversions,
        metrics.conversions_value
    FROM ad_group
    WHERE campaign.id = {campaign_id}
        AND segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND metrics.conversions > 0
        AND segments.conversion_action_name LIKE '%Closed Won%'
    ORDER BY segments.date DESC
"""

response_deals = ga_service.search(customer_id=customer_id, query=query_deals)

deal_count = 0
for row in response_deals:
    deal_count += 1
    ad_group = row.ad_group.name
    date = row.segments.date
    conv_name = row.segments.conversion_action_name
    conversions = row.metrics.conversions
    value = row.metrics.conversions_value

    date_obj = datetime.strptime(date, '%Y-%m-%d')
    days_ago = (datetime(2026, 2, 23) - date_obj).days

    print(f"\n✅ {ad_group}")
    print(f"   Date: {date} ({days_ago} days ago)")
    print(f"   Conversion: {conv_name}")
    print(f"   Value: ${value:,.2f}")

if deal_count == 0:
    print("\n   No deals with 'Closed Won' in name found")

# Summary recommendation
print("\n\n" + "=" * 160)
print("📋 RECOMMENDATION BASED ON QUOTE FRESHNESS")
print("=" * 160)

for ad_group in target_ad_groups:
    if ad_group in ad_group_quotes:
        quotes = ad_group_quotes[ad_group]
        most_recent = min(quotes, key=lambda x: x['date'])
        most_recent_date = datetime.strptime(most_recent['date'], '%Y-%m-%d')
        days_since_last = (datetime(2026, 2, 23) - most_recent_date).days
        total_quotes = sum(q['conversions'] for q in quotes)

        print(f"\n• {ad_group}:")
        print(f"  {int(total_quotes)} quotes, most recent {days_since_last} days ago")

        if days_since_last <= 7:
            print(f"  ✅ ACTION: KEEP ON - Fresh quotes, high conversion potential")
        elif days_since_last <= 14:
            print(f"  ⚠️  ACTION: MONITOR for 7 more days, then reassess")
        else:
            print(f"  🔴 ACTION: Consider turning off if no deals by end of week")

print("\n" + "=" * 160)
