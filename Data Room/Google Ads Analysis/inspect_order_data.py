import urllib.request
import json

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
    except Exception as e:
        print(f"Error: {e}")
        return None

print("=" * 160)
print("🔍 INSPECTING ORDER DATA STRUCTURE")
print("=" * 160)

# Query orders
query_data = {
    "database": 2,
    "type": "query",
    "query": {
        "source-table": 26,  # Order table
        "limit": 5
    }
}

result = metabase_request("/api/dataset", method="POST", data=query_data)

if not result or 'data' not in result:
    print("❌ Failed to retrieve data")
    exit()

orders_data = result['data']
rows = orders_data.get('rows', [])

print(f"\n✅ Retrieved {len(rows)} sample orders")

# Column indices
COL_ORDER_NUM = 68
COL_LINE_ITEMS = 30
COL_ORDER_PRICING = 70
COL_STATUS = 66
COL_RENTAL_DURATION = 51

print("\n" + "=" * 160)
print("📋 SAMPLE ORDER DATA")
print("=" * 160)

for i, row in enumerate(rows):
    print(f"\n{'━' * 160}")
    print(f"ORDER #{i+1}")
    print(f"{'━' * 160}")

    order_num = row[COL_ORDER_NUM] if len(row) > COL_ORDER_NUM else None
    status = row[COL_STATUS] if len(row) > COL_STATUS else None
    line_items = row[COL_LINE_ITEMS] if len(row) > COL_LINE_ITEMS else None
    order_pricing = row[COL_ORDER_PRICING] if len(row) > COL_ORDER_PRICING else None
    rental_duration = row[COL_RENTAL_DURATION] if len(row) > COL_RENTAL_DURATION else None

    print(f"Order Number: {order_num}")
    print(f"Status: {status}")
    print(f"Rental Duration: {rental_duration} days")

    print(f"\n📦 LINE ITEMS:")
    if line_items and isinstance(line_items, list):
        for idx, item in enumerate(line_items[:3]):  # Show first 3 items
            print(f"\n  Item {idx+1}:")
            if isinstance(item, dict):
                print(f"    Name: {item.get('name', 'N/A')}")
                print(f"    Category: {item.get('category', {})}")
                print(f"    Weight Class: {item.get('weightClass', 'N/A')}")
                print(f"    Price: {item.get('price', 'N/A')}")
                print(f"    Daily Rate: {item.get('dailyRate', 'N/A')}")
                print(f"    Weekly Rate: {item.get('weeklyRate', 'N/A')}")
                print(f"    Monthly Rate: {item.get('monthlyRate', 'N/A')}")
                print(f"    Total: {item.get('total', 'N/A')}")
                print(f"    All keys: {list(item.keys())[:15]}")
    else:
        print("  No line items")

    print(f"\n💰 ORDER PRICING:")
    if order_pricing and isinstance(order_pricing, list):
        for idx, pricing in enumerate(order_pricing[:2]):  # Show first 2 pricing entries
            print(f"\n  Pricing {idx+1}:")
            if isinstance(pricing, dict):
                print(f"    {json.dumps(pricing, indent=6)}")
    elif order_pricing and isinstance(order_pricing, dict):
        print(f"  {json.dumps(order_pricing, indent=4)}")
    else:
        print(f"  No pricing data (type: {type(order_pricing)})")

print("\n" + "=" * 160)
print("✅ INSPECTION COMPLETE")
print("=" * 160)
