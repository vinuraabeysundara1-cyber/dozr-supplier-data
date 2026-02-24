from google.ads.googleads.client import GoogleAdsClient
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("🔌 Testing Google Ads API Connection")
print("=" * 80)

try:
    # Load credentials
    print("\n1. Loading credentials from config file...")
    client = GoogleAdsClient.load_from_storage('/Users/vinuraabeysundara/Desktop/DOZR/Data Room/Config/google-ads.yaml')
    print("   ✅ Credentials loaded successfully")

    # Get service
    print("\n2. Initializing Google Ads Service...")
    ga_service = client.get_service('GoogleAdsService')
    print("   ✅ Service initialized")

    # Test query - get account info
    print("\n3. Testing API connection with account query...")
    customer_id = '8531896842'

    query = """
        SELECT
            customer.id,
            customer.descriptive_name,
            customer.currency_code,
            customer.time_zone,
            customer.status
        FROM customer
        LIMIT 1
    """

    response = ga_service.search(customer_id=customer_id, query=query)

    for row in response:
        print("   ✅ Connection successful!")
        print("\n" + "=" * 80)
        print("📋 Account Information")
        print("=" * 80)
        print(f"   Customer ID: {row.customer.id}")
        print(f"   Account Name: {row.customer.descriptive_name}")
        print(f"   Currency: {row.customer.currency_code}")
        print(f"   Time Zone: {row.customer.time_zone}")
        print(f"   Status: {row.customer.status.name}")

    # Test recent data availability
    print("\n4. Testing data availability (checking today's campaigns)...")
    today = datetime.now().strftime('%Y-%m-%d')

    query_data = f"""
        SELECT
            campaign.name,
            campaign.status,
            metrics.impressions
        FROM campaign
        WHERE segments.date = '{today}'
        LIMIT 5
    """

    response_data = ga_service.search(customer_id=customer_id, query=query_data)
    count = 0
    for row in response_data:
        count += 1

    print(f"   ✅ Found {count} campaigns with data for today")

    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED - Google Ads API is connected and working!")
    print("=" * 80)

except Exception as e:
    print(f"\n❌ Connection failed!")
    print(f"Error: {str(e)}")
    print("\n" + "=" * 80)
