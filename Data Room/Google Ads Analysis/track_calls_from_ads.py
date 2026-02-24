from google.ads.googleads.client import GoogleAdsClient
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Load credentials
client = GoogleAdsClient.load_from_storage('/Users/vinuraabeysundara/Desktop/DOZR/Data Room/Config/google-ads.yaml')
ga_service = client.get_service('GoogleAdsService')
customer_id = '8531896842'

# Get Sunday date
today = datetime.now()
days_since_sunday = (today.weekday() + 1) % 7
if days_since_sunday == 0:
    sunday_date = today
else:
    sunday_date = today - timedelta(days=days_since_sunday)

sunday_str = sunday_date.strftime('%Y-%m-%d')

print("=" * 100)
print(f"🔍 Tracking 'Calls from ads' Conversions - Sunday {sunday_date.strftime('%B %d, %Y')}")
print("=" * 100)

# Query to find which campaign had "Calls from ads" conversions
query = f"""
    SELECT
        campaign.name,
        campaign.id,
        segments.conversion_action_name,
        metrics.conversions
    FROM campaign
    WHERE segments.date = '{sunday_str}'
        AND segments.conversion_action_name = 'Calls from ads'
        AND metrics.conversions > 0
    ORDER BY metrics.conversions DESC
"""

print(f"\nSearching for campaigns with 'Calls from ads' conversions on {sunday_str}...\n")

response = ga_service.search(customer_id=customer_id, query=query)

total_calls = 0
campaigns_found = []

for row in response:
    campaign_name = row.campaign.name
    campaign_id = row.campaign.id
    conversions = row.metrics.conversions

    total_calls += conversions
    campaigns_found.append({
        'name': campaign_name,
        'id': campaign_id,
        'conversions': conversions
    })

    print(f"📞 Campaign: {campaign_name}")
    print(f"   Campaign ID: {campaign_id}")
    print(f"   Calls from ads: {int(conversions)}")
    print("-" * 100)

print(f"\n✅ Total 'Calls from ads': {int(total_calls)}")
print(f"✅ Campaigns with this conversion type: {len(campaigns_found)}")

# Now let's get more detailed info about ad groups and keywords for these campaigns
if campaigns_found:
    print("\n" + "=" * 100)
    print("🎯 DETAILED BREAKDOWN BY AD GROUP")
    print("=" * 100)

    for campaign in campaigns_found:
        print(f"\n📊 Campaign: {campaign['name']}")
        print("-" * 100)

        # Query ad group level data
        query_adgroup = f"""
            SELECT
                campaign.name,
                ad_group.name,
                ad_group.id,
                segments.conversion_action_name,
                metrics.conversions
            FROM ad_group
            WHERE segments.date = '{sunday_str}'
                AND campaign.id = {campaign['id']}
                AND segments.conversion_action_name = 'Calls from ads'
                AND metrics.conversions > 0
            ORDER BY metrics.conversions DESC
        """

        response_adgroup = ga_service.search(customer_id=customer_id, query=query_adgroup)

        for row in response_adgroup:
            ad_group_name = row.ad_group.name
            ad_group_id = row.ad_group.id
            conversions = row.metrics.conversions

            print(f"   Ad Group: {ad_group_name}")
            print(f"   Ad Group ID: {ad_group_id}")
            print(f"   Conversions: {int(conversions)}")
            print()

print("\n" + "=" * 100)
print("💡 NOTE: To see CallRail tracking details, you would need to:")
print("   1. Log into your CallRail dashboard")
print("   2. Filter calls by date: " + sunday_str)
print("   3. Look for calls tagged with the campaign/ad group names above")
print("=" * 100)
