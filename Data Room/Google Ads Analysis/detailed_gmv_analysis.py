import urllib.request
import json
from datetime import datetime
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
print("💰 DETAILED GMV ANALYSIS BY EQUIPMENT TYPE, WEIGHT CLASS, AND RENTAL DURATION")
print("=" * 160)

# Query orders - get recent orders
query_data = {
    "database": 2,
    "type": "query",
    "query": {
        "source-table": 26,  # Order table
        "limit": 1000
    }
}

print("\n⏳ Fetching order data...")
result = metabase_request("/api/dataset", method="POST", data=query_data)

if not result or 'data' not in result:
    print("❌ Failed to retrieve data")
    exit()

orders_data = result['data']
rows = orders_data.get('rows', [])

print(f"✅ Retrieved {len(rows)} orders with line items")

# Column indices
COL_ORDER_NUM = 68
COL_STATUS = 66
COL_LINE_ITEMS = 30
COL_ORDER_PRICING = 70
COL_RENTAL_DURATION = 51
COL_START_DAY = 65
COL_END_DAY = 25
COL_CREATED_DATE = 11

# Analyze equipment from line items
print("\n📊 Analyzing equipment data from line items...")

equipment_gmv = defaultdict(lambda: {
    'total_gmv': 0,
    'order_count': 0,
    'total_rental_days': 0,
    'rental_duration_breakdown': defaultdict(int),
    'equipment_details': defaultdict(int)
})

rental_duration_gmv = defaultdict(lambda: {'gmv': 0, 'count': 0})
processed_orders = 0

for row in rows:
    try:
        order_num = row[COL_ORDER_NUM] if len(row) > COL_ORDER_NUM else None
        status = row[COL_STATUS] if len(row) > COL_STATUS else None
        line_items = row[COL_LINE_ITEMS] if len(row) > COL_LINE_ITEMS else []
        order_pricing = row[COL_ORDER_PRICING] if len(row) > COL_ORDER_PRICING else []
        rental_duration = row[COL_RENTAL_DURATION] if len(row) > COL_RENTAL_DURATION else 0

        # Skip if no line items or invalid status
        if not line_items or not isinstance(line_items, list):
            continue

        # Calculate order GMV from pricing
        order_gmv = 0
        if order_pricing and isinstance(order_pricing, list):
            for pricing in order_pricing:
                if isinstance(pricing, dict) and 'total' in pricing:
                    order_gmv += float(pricing.get('total', 0))

        # Process each line item
        for item in line_items:
            if not isinstance(item, dict):
                continue

            # Extract equipment category/type
            equip_cat = item.get('category', {})
            if isinstance(equip_cat, dict):
                cat_name = equip_cat.get('name', 'Unknown')
            else:
                cat_name = 'Unknown'

            # Get item-specific details
            item_name = item.get('name', cat_name)
            weight_class = item.get('weightClass', 'N/A')

            # Group by category
            equipment_gmv[cat_name]['total_gmv'] += order_gmv / len(line_items)  # Split GMV across items
            equipment_gmv[cat_name]['order_count'] += 1 / len(line_items)
            equipment_gmv[cat_name]['total_rental_days'] += rental_duration or 0

            # Track rental duration breakdown
            if rental_duration:
                duration_bucket = (
                    "1-7 days" if rental_duration <= 7
                    else "8-14 days" if rental_duration <= 14
                    else "15-30 days" if rental_duration <= 30
                    else "31-60 days" if rental_duration <= 60
                    else "60+ days"
                )
                equipment_gmv[cat_name]['rental_duration_breakdown'][duration_bucket] += order_gmv / len(line_items)
                rental_duration_gmv[duration_bucket]['gmv'] += order_gmv / len(line_items)
                rental_duration_gmv[duration_bucket]['count'] += 1 / len(line_items)

            # Track specific equipment details
            if weight_class and weight_class != 'N/A':
                equip_detail = f"{item_name} ({weight_class})"
            else:
                equip_detail = item_name

            equipment_gmv[cat_name]['equipment_details'][equip_detail] += order_gmv / len(line_items)

        processed_orders += 1

    except Exception as e:
        continue

print(f"✅ Processed {processed_orders} orders")

# Display Results
print("\n" + "=" * 160)
print("📊 GMV BY EQUIPMENT TYPE")
print("=" * 160)

# Sort by GMV
sorted_equipment = sorted(equipment_gmv.items(), key=lambda x: x[1]['total_gmv'], reverse=True)

print(f"\n{'Equipment Type':<40} {'Total GMV':>15} {'Orders':>10} {'Avg GMV/Order':>15} {'Total Days':>12} {'Avg Days/Order':>15}")
print("-" * 160)

total_gmv = 0
total_orders = 0

for equip_type, data in sorted_equipment[:20]:  # Top 20
    avg_gmv = data['total_gmv'] / data['order_count'] if data['order_count'] > 0 else 0
    avg_days = data['total_rental_days'] / data['order_count'] if data['order_count'] > 0 else 0

    print(f"{equip_type:<40} ${data['total_gmv']:>14,.2f} {data['order_count']:>10.1f} ${avg_gmv:>14,.2f} {data['total_rental_days']:>12.0f} {avg_days:>15.1f}")

    total_gmv += data['total_gmv']
    total_orders += data['order_count']

print("-" * 160)
print(f"{'TOTAL':<40} ${total_gmv:>14,.2f} {total_orders:>10.1f}")

# GMV by Rental Duration
print("\n" + "=" * 160)
print("📊 GMV BY RENTAL DURATION")
print("=" * 160)

print(f"\n{'Duration':<20} {'Total GMV':>15} {'Orders':>10} {'Avg GMV/Order':>15}")
print("-" * 160)

sorted_durations = sorted(rental_duration_gmv.items(),
                          key=lambda x: ['1-7 days', '8-14 days', '15-30 days', '31-60 days', '60+ days'].index(x[0]) if x[0] in ['1-7 days', '8-14 days', '15-30 days', '31-60 days', '60+ days'] else 999)

for duration, data in sorted_durations:
    avg_gmv = data['gmv'] / data['count'] if data['count'] > 0 else 0
    print(f"{duration:<20} ${data['gmv']:>14,.2f} {data['count']:>10.1f} ${avg_gmv:>14,.2f}")

# Top equipment details by GMV
print("\n" + "=" * 160)
print("📊 TOP 20 EQUIPMENT BY GMV (WITH WEIGHT CLASS)")
print("=" * 160)

all_equipment_details = []
for equip_type, data in equipment_gmv.items():
    for detail, gmv in data['equipment_details'].items():
        all_equipment_details.append((detail, gmv, equip_type))

sorted_details = sorted(all_equipment_details, key=lambda x: x[1], reverse=True)

print(f"\n{'Equipment':<50} {'Category':<30} {'GMV':>15}")
print("-" * 160)

for detail, gmv, category in sorted_details[:20]:
    print(f"{detail:<50} {category:<30} ${gmv:>14,.2f}")

print("\n" + "=" * 160)
print("✅ GMV ANALYSIS COMPLETE")
print("=" * 160)
