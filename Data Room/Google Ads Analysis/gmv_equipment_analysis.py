import urllib.request
import json
from datetime import datetime, timedelta
from collections import defaultdict

METABASE_URL = "https://starry-bolt.metabaseapp.com"
METABASE_KEY = "mb_XRBKMlQkz3Waw1jpgaNUVIYM+nEkF2bCexU1sUI0Uks="

def metabase_request(endpoint, method="GET", data=None):
    url = f"{METABASE_URL}{endpoint}"
    headers = {"x-api-key": METABASE_KEY, "Content-Type": "application/json"}
    req = urllib.request.Request(url, headers=headers, method=method)
    if data:
        req.data = json.dumps(data).encode()

    try:
        response = urllib.request.urlopen(req)
        return json.loads(response.read())
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        return None

print("=" * 160)
print("💰 GMV ANALYSIS BY EQUIPMENT TYPE, WEIGHT CLASS, AND RENTAL DURATION")
print("=" * 160)

# Query orders from the Order table (ID: 26)
print("\n📊 Querying order data...")

# Build a Metabase native query using table ID
query_data = {
    "database": 2,
    "type": "query",
    "query": {
        "source-table": 26,  # Order table ID
        "limit": 100
    }
}

print("\n⏳ Fetching order data from Metabase...")
result = metabase_request("/api/dataset", method="POST", data=query_data)

if result and 'data' in result:
    print(f"✅ Retrieved {len(result['data'].get('rows', []))} orders")

    # Process the results
    orders_data = result['data']

    print("\n" + "=" * 160)
    print("📋 SAMPLE ORDERS DATA")
    print("=" * 160)

    # Display first few rows
    if 'rows' in orders_data and len(orders_data['rows']) > 0:
        print(f"\nShowing first 10 orders:")
        print(f"\n{'Order #':<15} {'Status':<15} {'Created Date':<25} {'Duration (days)':<20} {'Items':<10}")
        print("-" * 160)

        for i, row in enumerate(orders_data['rows'][:10]):
            order_num = row[1] if len(row) > 1 else 'N/A'
            status = row[2] if len(row) > 2 else 'N/A'
            created = row[3] if len(row) > 3 else 'N/A'
            duration = row[6] if len(row) > 6 else 'N/A'
            items = len(row[7]) if len(row) > 7 and row[7] else 0

            print(f"{str(order_num):<15} {str(status):<15} {str(created):<25} {str(duration):<20} {items:<10}")

    print("\n" + "=" * 160)
    print("🔍 Analyzing column structure...")
    print("=" * 160)

    if 'cols' in orders_data:
        print("\nAvailable columns:")
        for i, col in enumerate(orders_data['cols']):
            col_name = col.get('name', col.get('display_name', f'Column {i}'))
            col_type = col.get('base_type', 'unknown')
            print(f"   {i}: {col_name} ({col_type})")

else:
    print("❌ Failed to retrieve order data")
    if result:
        print(f"Response: {json.dumps(result, indent=2)[:500]}")

print("\n" + "=" * 160)
print("✅ INITIAL DATA RETRIEVAL COMPLETE")
print("=" * 160)
