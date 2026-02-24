import urllib.request
import json
from collections import defaultdict
from datetime import datetime

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

print("=" * 180)
print("STEP 1: TOP 10 HIGHEST GMV EQUIPMENT TYPES (SPECIFIC MODELS) - LAST 30 DAYS")
print("=" * 180)

# Query all invoices with full details
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
                    },
                    "totalAmt": {"$gt": 0}
                }
            },
            {
                "$project": {
                    "totalAmt": 1,
                    "lines": 1,
                    "region": 1,
                    "startDate": 1,
                    "endDate": 1,
                    "createdDate": 1
                }
            }
        ]),
        "collection": "invoicesv2"
    }
}

print("\n🔍 Querying Metabase invoices...")
result = run_metabase_query(query_invoices)

equipment_details = defaultdict(lambda: {
    'count': 0,
    'total_gmv': 0,
    'rentals': [],
    'locations': defaultdict(int),
    'durations': [],
    'prices': []
})

if result and result.get('status') == 'completed':
    rows = result.get('data', {}).get('rows', [])
    cols = result.get('data', {}).get('cols', [])

    print(f"✅ Retrieved {len(rows)} invoices")

    # Build column mapping
    col_map = {}
    for i, col in enumerate(cols):
        field_name = col.get('name', col.get('display_name', f'field_{i}'))
        col_map[field_name] = i

    processed_count = 0

    for row in rows:
        invoice = {}
        for field, idx in col_map.items():
            if idx < len(row):
                invoice[field] = row[idx]

        total_amt = float(invoice.get('totalAmt', 0)) if invoice.get('totalAmt') else 0
        lines = invoice.get('lines', [])
        region = invoice.get('region', 'Unknown')
        start_date = invoice.get('startDate', '')
        end_date = invoice.get('endDate', '')
        created_date = invoice.get('createdDate', '')

        # Calculate duration
        duration_days = 'Unknown'
        if start_date and end_date:
            try:
                start = datetime.fromisoformat(str(start_date).replace('Z', '+00:00'))
                end = datetime.fromisoformat(str(end_date).replace('Z', '+00:00'))
                duration_days = (end - start).days
            except:
                pass

        # Parse line items to get equipment details
        if lines and isinstance(lines, list):
            for line_item in lines:
                if isinstance(line_item, dict):
                    # Try to get equipment info from line item
                    line_total = float(line_item.get('totalAmt', 0)) if line_item.get('totalAmt') else 0

                    # Equipment could be nested in different ways
                    equipment_name = None
                    equipment_category = None

                    # Try different field paths
                    if 'equipment' in line_item and isinstance(line_item['equipment'], dict):
                        equipment_name = line_item['equipment'].get('name', None)
                        equipment_category = line_item['equipment'].get('category', None)
                    elif 'equipmentName' in line_item:
                        equipment_name = line_item.get('equipmentName')
                    elif 'description' in line_item:
                        equipment_name = line_item.get('description')

                    # Use name or category as equipment identifier
                    equipment_type = equipment_name or equipment_category or 'Unknown Equipment'

                    if equipment_type != 'Unknown Equipment' and line_total > 0:
                        equipment_details[equipment_type]['count'] += 1
                        equipment_details[equipment_type]['total_gmv'] += line_total
                        equipment_details[equipment_type]['locations'][region] += 1
                        equipment_details[equipment_type]['prices'].append(line_total)
                        if duration_days != 'Unknown':
                            equipment_details[equipment_type]['durations'].append(duration_days)

                        equipment_details[equipment_type]['rentals'].append({
                            'price': line_total,
                            'location': region,
                            'duration': duration_days,
                            'date': str(created_date)[:10] if created_date else 'Unknown'
                        })

                        processed_count += 1

    print(f"✅ Processed {processed_count} equipment line items")

    # Sort by GMV
    sorted_equipment = sorted(equipment_details.items(), key=lambda x: x[1]['total_gmv'], reverse=True)

    total_gmv = sum(d['total_gmv'] for d in equipment_details.values())

    print("\n\n" + "=" * 180)
    print("📊 TOP 10 EQUIPMENT TYPES BY GMV")
    print("=" * 180)

    print(f"\n{'Rank':<6} {'Equipment Type/Model':<50} {'Rentals':>10} {'Total GMV':>14} {'Avg Price':>14} {'% of Total':>12}")
    print("-" * 130)

    for rank, (equip_type, data) in enumerate(sorted_equipment[:10], 1):
        count = data['count']
        gmv = data['total_gmv']
        avg_price = gmv / count if count > 0 else 0
        pct = (gmv / total_gmv * 100) if total_gmv > 0 else 0

        # Truncate long equipment names
        equip_display = equip_type[:47] + "..." if len(equip_type) > 50 else equip_type

        print(f"{rank:<6} {equip_display:<50} {count:>10} ${gmv:>13,.2f} ${avg_price:>13,.2f} {pct:>11.1f}%")

    # Detailed breakdown
    print("\n\n" + "=" * 180)
    print("🔍 DETAILED BREAKDOWN - TOP 10 EQUIPMENT TYPES")
    print("=" * 180)

    for rank, (equip_type, data) in enumerate(sorted_equipment[:10], 1):
        print(f"\n{'='*180}")
        print(f"#{rank}. {equip_type}")
        print(f"{'='*180}")

        count = data['count']
        gmv = data['total_gmv']
        avg_price = gmv / count if count > 0 else 0
        prices = data['prices']

        print(f"\n📊 Summary:")
        print(f"   • Total Rentals: {count}")
        print(f"   • Total GMV: ${gmv:,.2f}")
        print(f"   • Average Price: ${avg_price:,.2f}")
        print(f"   • Min Price: ${min(prices):,.2f}" if prices else "   • Min Price: N/A")
        print(f"   • Max Price: ${max(prices):,.2f}" if prices else "   • Max Price: N/A")

        # Top locations
        if data['locations']:
            print(f"\n📍 Locations:")
            sorted_locations = sorted(data['locations'].items(), key=lambda x: x[1], reverse=True)
            for loc, cnt in sorted_locations[:5]:
                print(f"   • {loc}: {cnt} rentals")

        # Duration analysis
        if data['durations']:
            durations = data['durations']
            avg_duration = sum(durations) / len(durations)
            print(f"\n⏱️  Rental Duration:")
            print(f"   • Average: {avg_duration:.1f} days")
            print(f"   • Range: {min(durations)}-{max(durations)} days")

    # Export to CSV
    print("\n\n" + "=" * 180)
    print("💾 EXPORTING DATA...")
    print("=" * 180)

    import csv
    csv_file = 'top_equipment_types_detailed.csv'
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Rank', 'Equipment Type/Model', 'Rentals', 'Total GMV', 'Avg Price', '% of Total', 'Top Location', 'Avg Duration (days)'])

        for rank, (equip_type, data) in enumerate(sorted_equipment[:10], 1):
            count = data['count']
            gmv = data['total_gmv']
            avg_price = gmv / count if count > 0 else 0
            pct = (gmv / total_gmv * 100) if total_gmv > 0 else 0

            top_location = max(data['locations'].items(), key=lambda x: x[1])[0] if data['locations'] else 'Unknown'
            avg_duration = sum(data['durations']) / len(data['durations']) if data['durations'] else 0

            writer.writerow([
                rank,
                equip_type,
                count,
                f"{gmv:.2f}",
                f"{avg_price:.2f}",
                f"{pct:.1f}",
                top_location,
                f"{avg_duration:.1f}"
            ])

    print(f"✅ Data exported to: {csv_file}")

else:
    print("❌ Failed to retrieve invoice data")

print("\n" + "=" * 180)
