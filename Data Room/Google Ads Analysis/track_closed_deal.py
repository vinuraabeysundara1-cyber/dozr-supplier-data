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
print(f"🎯 Tracking Closed Won Deal - Sunday {sunday_date.strftime('%B %d, %Y')}")
print("=" * 100)

# Query to find which campaign had the closed won deal
query = f"""
    SELECT
        campaign.name,
        campaign.id,
        segments.conversion_action_name,
        metrics.conversions
    FROM campaign
    WHERE segments.date = '{sunday_str}'
        AND segments.conversion_action_name LIKE '%Closed Won%'
        AND metrics.conversions > 0
    ORDER BY metrics.conversions DESC
"""

print(f"\nSearching for campaigns with 'Closed Won Deal' conversions on {sunday_str}...\n")

response = ga_service.search(customer_id=customer_id, query=query)

deals_found = False

for row in response:
    deals_found = True
    campaign_name = row.campaign.name
    campaign_id = row.campaign.id
    conversion_name = row.segments.conversion_action_name
    conversions = row.metrics.conversions

    print(f"🎉 CLOSED DEAL FOUND!")
    print(f"   Campaign: {campaign_name}")
    print(f"   Campaign ID: {campaign_id}")
    print(f"   Conversion Type: {conversion_name}")
    print(f"   Number of Deals: {int(conversions)}")
    print("-" * 100)

    # Now get ad group details
    print(f"\n🔍 Ad Group Breakdown for: {campaign_name}")
    print("-" * 100)

    query_adgroup = f"""
        SELECT
            ad_group.name,
            ad_group.id,
            segments.conversion_action_name,
            metrics.conversions
        FROM ad_group
        WHERE segments.date = '{sunday_str}'
            AND campaign.id = {campaign_id}
            AND segments.conversion_action_name LIKE '%Closed Won%'
            AND metrics.conversions > 0
    """

    response_adgroup = ga_service.search(customer_id=customer_id, query=query_adgroup)

    for adgroup_row in response_adgroup:
        ad_group_name = adgroup_row.ad_group.name
        ad_group_id = adgroup_row.ad_group.id
        adgroup_conversions = adgroup_row.metrics.conversions

        print(f"   Ad Group: {ad_group_name}")
        print(f"   Ad Group ID: {ad_group_id}")
        print(f"   Deals: {int(adgroup_conversions)}")

if not deals_found:
    print("❌ No closed won deals found on this date.")

print("\n" + "=" * 100)
