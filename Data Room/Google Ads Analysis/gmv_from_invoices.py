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
    except Exception as e:
        print(f"Error: {e}")
        return None

print("=" * 160)
print("💰 GMV ANALYSIS FROM INVOICES")
print("=" * 160)

# Query invoices table (ID: 37)
print("\n📊 Querying invoice data...")
query_data = {
    "database": 2,
    "type": "query",
    "query": {
        "source-table": 37,  # Invoices table
        "limit": 1000
    }
}

result = metabase_request("/api/dataset", method="POST", data=query_data)

if not result or 'data' not in result:
    print("❌ Failed to retrieve data")
    exit()

invoices_data = result['data']
rows = invoices_data.get('rows', [])
cols = invoices_data.get('cols', [])

print(f"✅ Retrieved {len(rows)} invoices")

# Find column indices
col_map = {}
for i, col in enumerate(cols):
    col_name = col.get('name', col.get('display_name', ''))
    col_map[col_name] = i

print(f"\n🔍 Available columns: {list(col_map.keys())[:20]}")

# Extract key columns
col_order_id = col_map.get('orderId', col_map.get('orderNumber', None))
col_total = col_map.get('totalAmt', col_map.get('total', None))
col_subtotal = col_map.get('subtotalAmt', col_map.get('subtotal', None))
col_lines = col_map.get('lines', None)
col_start_date = col_map.get('startDate', None)
col_end_date = col_map.get('endDate', None)
col_created_date = col_map.get('createdDate', None)

print(f"\nColumn indices:")
print(f"  Order ID: {col_order_id}")
print(f"  Total: {col_total}")
print(f"  Subtotal: {col_subtotal}")
print(f"  Lines: {col_lines}")
print(f"  Start Date: {col_start_date}")
print(f"  End Date: {col_end_date}")

# Analyze invoices
total_gmv = 0
invoice_count = 0
equipment_gmv = defaultdict(lambda: {'gmv': 0, 'count': 0, 'rental_days': 0})
duration_gmv = defaultdict(lambda: {'gmv': 0, 'count': 0})

for row in rows:
    try:
        total_amt = row[col_total] if col_total and len(row) > col_total else 0
        lines = row[col_lines] if col_lines and len(row) > col_lines else []
        start_date = row[col_start_date] if col_start_date and len(row) > col_start_date else None
        end_date = row[col_end_date] if col_end_date and len(row) > col_end_date else None

        if not total_amt or total_amt == 0:
            continue

        total_gmv += float(total_amt)
        invoice_count += 1

        # Calculate rental duration
        rental_days = None
        if start_date and end_date:
            try:
                if isinstance(start_date, str):
                    start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                else:
                    start_dt = datetime.fromtimestamp(start_date / 1000) if start_date > 10000000000 else datetime.fromtimestamp(start_date)

                if isinstance(end_date, str):
                    end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                else:
                    end_dt = datetime.fromtimestamp(end_date / 1000) if end_date > 10000000000 else datetime.fromtimestamp(end_date)

                rental_days = (end_dt - start_dt).days
            except:
                pass

        # Duration bucket
        if rental_days:
            duration_bucket = (
                "1-7 days" if rental_days <= 7
                else "8-14 days" if rental_days <= 14
                else "15-30 days" if rental_days <= 30
                else "31-60 days" if rental_days <= 60
                else "60+ days"
            )
            duration_gmv[duration_bucket]['gmv'] += float(total_amt)
            duration_gmv[duration_bucket]['count'] += 1

        # Analyze line items
        if lines and isinstance(lines, list):
            for line in lines:
                if isinstance(line, dict):
                    description = line.get('description', line.get('name', 'Unknown'))
                    line_amt = line.get('amount', total_amt / len(lines))

                    equipment_gmv[description]['gmv'] += float(line_amt) if line_amt else 0
                    equipment_gmv[description]['count'] += 1
                    if rental_days:
                        equipment_gmv[description]['rental_days'] += rental_days

    except Exception as e:
        continue

print(f"\n{'=' * 160}")
print(f"💰 GMV SUMMARY")
print(f"{'=' * 160}")
print(f"\nTotal GMV: ${total_gmv:,.2f}")
print(f"Total Invoices: {invoice_count:,}")
print(f"Average Invoice Value: ${(total_gmv / invoice_count if invoice_count > 0 else 0):,.2f}")

# GMV by Equipment Type
print(f"\n{'=' * 160}")
print(f"📊 TOP EQUIPMENT TYPES BY GMV")
print(f"{'=' * 160}")

sorted_equipment = sorted(equipment_gmv.items(), key=lambda x: x[1]['gmv'], reverse=True)

print(f"\n{'Equipment Type':<60} {'Total GMV':>15} {'Count':>10} {'Avg GMV':>15}")
print(f"{'-' * 160}")

for equip_type, data in sorted_equipment[:25]:
    avg_gmv = data['gmv'] / data['count'] if data['count'] > 0 else 0
    print(f"{equip_type:<60} ${data['gmv']:>14,.2f} {data['count']:>10,.0f} ${avg_gmv:>14,.2f}")

# GMV by Rental Duration
print(f"\n{'=' * 160}")
print(f"📊 GMV BY RENTAL DURATION")
print(f"{'=' * 160}")

print(f"\n{'Duration':<20} {'Total GMV':>15} {'Count':>10} {'Avg GMV':>15} {'% of Total':>12}")
print(f"{'-' * 160}")

sorted_durations = sorted(duration_gmv.items(),
                          key=lambda x: ['1-7 days', '8-14 days', '15-30 days', '31-60 days', '60+ days'].index(x[0]) if x[0] in ['1-7 days', '8-14 days', '15-30 days', '31-60 days', '60+ days'] else 999)

for duration, data in sorted_durations:
    avg_gmv = data['gmv'] / data['count'] if data['count'] > 0 else 0
    pct = (data['gmv'] / total_gmv * 100) if total_gmv > 0 else 0
    print(f"{duration:<20} ${data['gmv']:>14,.2f} {data['count']:>10,.0f} ${avg_gmv:>14,.2f} {pct:>11.1f}%")

print(f"\n{'=' * 160}")
print("✅ ANALYSIS COMPLETE")
print(f"{'=' * 160}")
