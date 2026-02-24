import urllib.request
import json
from collections import defaultdict

# Metabase API Configuration
METABASE_URL = "https://starry-bolt.metabaseapp.com"
METABASE_KEY = "mb_XRBKMlQkz3Waw1jpgaNUVIYM+nEkF2bCexU1sUI0Uks="

def metabase_request(endpoint, method="GET", data=None):
    """Make request to Metabase API"""
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

def run_metabase_query(query_json):
    """Run a native MongoDB query via Metabase"""
    return metabase_request("/api/dataset", method="POST", data=query_json)

print("=" * 160)
print("STEP 1: HIGHEST GMV EQUIPMENT ANALYSIS (LAST 30 DAYS)")
print("=" * 160)

# Query invoices for equipment details
print("\n🔍 Querying Metabase for invoice data...")

query_invoices = {
    "database": 2,
    "type": "native",
    "native": {
        "query": json.dumps([
            {
                "$match": {
                    "createdDate": {
                        "$gte": {"$date": "2026-01-24T00:00:00.000Z"},
                        "$lte": {"$date": "2026-02-23T23:59:59.999Z"}
                    }
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "createdDate": 1,
                    "total": 1,
                    "status": 1,
                    "equipmentType": 1,
                    "equipment": 1,
                    "category": 1,
                    "items": 1,
                    "duration": 1,
                    "location": 1,
                    "city": 1,
                    "state": 1,
                    "rentalStartDate": 1,
                    "rentalEndDate": 1
                }
            }
        ]),
        "collection": "invoicesv2"
    }
}

invoices_result = run_metabase_query(query_invoices)

equipment_data = defaultdict(lambda: {
    'count': 0,
    'total_gmv': 0,
    'rentals': []
})

if invoices_result and invoices_result.get('status') == 'completed':
    rows = invoices_result.get('data', {}).get('rows', [])
    cols = invoices_result.get('data', {}).get('cols', [])

    print(f"✅ Found {len(rows)} invoices in last 30 days")

    # Parse columns
    col_map = {}
    for i, col in enumerate(cols):
        field_name = col.get('name', col.get('display_name', f'field_{i}'))
        col_map[field_name] = i

    for row in rows:
        invoice = {}
        for field, idx in col_map.items():
            if idx < len(row):
                invoice[field] = row[idx]

        # Extract equipment details
        equipment_type = invoice.get('equipmentType', 'Unknown')
        category = invoice.get('category', 'Unknown')
        total = float(invoice.get('total', 0)) if invoice.get('total') else 0
        items = invoice.get('items', [])
        location = invoice.get('location', {})
        city = invoice.get('city', 'Unknown')
        state = invoice.get('state', 'Unknown')
        duration = invoice.get('duration', 'Unknown')

        # Try to extract equipment model from items
        equipment_model = 'Unknown'
        if items and isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    equipment_model = item.get('equipment', {}).get('model', 'Unknown')
                    if equipment_model != 'Unknown':
                        break

        # Use equipment type or category
        equip_key = equipment_type if equipment_type and equipment_type != 'Unknown' else category

        if equip_key and equip_key != 'Unknown':
            equipment_data[equip_key]['count'] += 1
            equipment_data[equip_key]['total_gmv'] += total
            equipment_data[equip_key]['rentals'].append({
                'model': equipment_model,
                'price': total,
                'duration': duration,
                'city': city,
                'state': state,
                'date': str(invoice.get('createdDate', ''))[:10]
            })

    # Sort by GMV
    sorted_equipment = sorted(equipment_data.items(), key=lambda x: x[1]['total_gmv'], reverse=True)

    print("\n\n" + "=" * 160)
    print("📊 TOP EQUIPMENT TYPES BY GMV (LAST 30 DAYS)")
    print("=" * 160)

    print(f"\n{'Rank':<6} {'Equipment Type':<30} {'Rentals':>10} {'Total GMV':>14} {'Avg GMV':>14} {'% of Total':>12}")
    print("-" * 100)

    total_gmv = sum(d['total_gmv'] for d in equipment_data.values())

    for rank, (equip_type, data) in enumerate(sorted_equipment[:20], 1):
        count = data['count']
        gmv = data['total_gmv']
        avg_gmv = gmv / count if count > 0 else 0
        pct = (gmv / total_gmv * 100) if total_gmv > 0 else 0

        print(f"{rank:<6} {equip_type:<30} {count:>10} ${gmv:>13,.2f} ${avg_gmv:>13,.2f} {pct:>11.1f}%")

    # Detailed breakdown for top 10
    print("\n\n" + "=" * 160)
    print("🔍 DETAILED BREAKDOWN - TOP 10 EQUIPMENT TYPES")
    print("=" * 160)

    for rank, (equip_type, data) in enumerate(sorted_equipment[:10], 1):
        print(f"\n{'='*160}")
        print(f"#{rank}. {equip_type.upper()} - {data['count']} Rentals, ${data['total_gmv']:,.2f} Total GMV")
        print(f"{'='*160}")

        # Get top locations
        location_count = defaultdict(int)
        location_gmv = defaultdict(float)
        model_count = defaultdict(int)
        duration_count = defaultdict(int)

        for rental in data['rentals']:
            state = rental['state']
            city = rental['city']
            model = rental['model']
            duration = rental['duration']
            price = rental['price']

            if state and state != 'Unknown':
                location = f"{city}, {state}" if city and city != 'Unknown' else state
                location_count[location] += 1
                location_gmv[location] += price

            if model and model != 'Unknown':
                model_count[model] += 1

            if duration and duration != 'Unknown':
                duration_count[duration] += 1

        # Top locations
        print(f"\n📍 Top Locations:")
        sorted_locations = sorted(location_gmv.items(), key=lambda x: x[1], reverse=True)
        for loc, gmv in sorted_locations[:5]:
            count = location_count[loc]
            print(f"   • {loc}: {count} rentals, ${gmv:,.2f}")

        # Top models
        if model_count:
            print(f"\n🚜 Top Models:")
            sorted_models = sorted(model_count.items(), key=lambda x: x[1], reverse=True)
            for model, count in sorted_models[:5]:
                print(f"   • {model}: {count} rentals")

        # Durations
        if duration_count:
            print(f"\n⏱️  Rental Durations:")
            sorted_durations = sorted(duration_count.items(), key=lambda x: x[1], reverse=True)
            for dur, count in sorted_durations[:5]:
                print(f"   • {dur}: {count} rentals")

        # Price ranges
        prices = [r['price'] for r in data['rentals'] if r['price'] > 0]
        if prices:
            avg_price = sum(prices) / len(prices)
            min_price = min(prices)
            max_price = max(prices)
            print(f"\n💰 Price Analysis:")
            print(f"   • Average: ${avg_price:,.2f}")
            print(f"   • Range: ${min_price:,.2f} - ${max_price:,.2f}")

    # Summary statistics
    print("\n\n" + "=" * 160)
    print("📈 SUMMARY STATISTICS")
    print("=" * 160)

    print(f"\n✅ Total Invoices: {len(rows)}")
    print(f"✅ Total GMV: ${total_gmv:,.2f}")
    print(f"✅ Average Invoice Value: ${total_gmv / len(rows) if len(rows) > 0 else 0:,.2f}")

    # Top 5 revenue generators
    top5_gmv = sum(d['total_gmv'] for _, d in sorted_equipment[:5])
    top5_pct = (top5_gmv / total_gmv * 100) if total_gmv > 0 else 0

    print(f"\n🎯 Top 5 Equipment Types:")
    print(f"   • Generate ${top5_gmv:,.2f} ({top5_pct:.1f}% of total GMV)")
    for rank, (equip_type, data) in enumerate(sorted_equipment[:5], 1):
        print(f"   {rank}. {equip_type}: ${data['total_gmv']:,.2f}")

    # Export to CSV for Step 2
    import csv
    csv_file = 'highest_gmv_equipment_last30days.csv'
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Rank', 'Equipment Type', 'Rental Count', 'Total GMV', 'Avg GMV', '% of Total'])
        for rank, (equip_type, data) in enumerate(sorted_equipment, 1):
            count = data['count']
            gmv = data['total_gmv']
            avg_gmv = gmv / count if count > 0 else 0
            pct = (gmv / total_gmv * 100) if total_gmv > 0 else 0
            writer.writerow([rank, equip_type, count, f"{gmv:.2f}", f"{avg_gmv:.2f}", f"{pct:.1f}"])

    print(f"\n📄 Data exported to: {csv_file}")

else:
    print("❌ Failed to retrieve invoice data from Metabase")

print("\n" + "=" * 160)
