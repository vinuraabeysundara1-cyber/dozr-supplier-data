import urllib.request
import json
from datetime import datetime
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
        print(f"Error with request to {endpoint}: {e}")
        return None

def run_metabase_query(query_json):
    """Run a native MongoDB query via Metabase"""
    return metabase_request("/api/dataset", method="POST", data=query_json)

print("=" * 160)
print("🎯 COMPREHENSIVE DEALS BREAKDOWN - FEBRUARY 2026")
print("Period: February 1-23, 2026")
print("=" * 160)

# Step 1: Explore what collections we have
print("\n\n🔍 STEP 1: EXPLORING AVAILABLE DATA")
print("=" * 160)

db_id = 2  # Production MongoDB
db_metadata = metabase_request(f"/api/database/{db_id}/metadata")

if db_metadata:
    tables = db_metadata.get('tables', [])
    relevant_collections = []

    print("\n📊 Available Collections:")
    for table in tables:
        table_name = table.get('name', '')
        table_id = table.get('id')
        # Look for deal/opportunity related collections
        if any(keyword in table_name.lower() for keyword in ['request', 'opportunity', 'deal', 'invoice', 'order', 'booking']):
            relevant_collections.append((table_name, table_id))
            print(f"   ✓ {table_name} (ID: {table_id})")

    print(f"\n   Found {len(relevant_collections)} relevant collections")

# Step 2: Query supplier requests (this is typically where deals/orders are)
print("\n\n📊 STEP 2: QUERYING SUPPLIER REQUESTS / ORDERS")
print("=" * 160)

# Try querying supplierrequests collection for February
query_requests = {
    "database": 2,
    "type": "native",
    "native": {
        "query": json.dumps([
            {
                "$match": {
                    "createdDate": {
                        "$gte": {"$date": "2026-02-01T00:00:00.000Z"},
                        "$lte": {"$date": "2026-02-23T23:59:59.999Z"}
                    }
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "createdDate": 1,
                    "status": 1,
                    "totalPrice": 1,
                    "equipmentType": 1,
                    "category": 1,
                    "subcategory": 1,
                    "rentalDuration": 1,
                    "accounts": 1
                }
            }
        ]),
        "collection": "supplierrequests"
    }
}

print("\n🔍 Querying supplierrequests collection...")
requests_result = run_metabase_query(query_requests)

if requests_result and requests_result.get('status') == 'completed':
    rows = requests_result.get('data', {}).get('rows', [])
    cols = requests_result.get('data', {}).get('cols', [])

    print(f"✅ Found {len(rows)} supplier requests in February")

    if len(rows) > 0:
        print(f"\n📋 Sample record:")
        for i, col in enumerate(cols[:10]):
            if i < len(rows[0]):
                print(f"   • {col.get('display_name')}: {rows[0][i]}")

    # Process the data
    daily_stats = defaultdict(lambda: {
        'requests': 0,
        'total_gmv': 0,
        'equipment_types': defaultdict(int),
        'equipment_gmv': defaultdict(float)
    })

    equipment_breakdown = defaultdict(lambda: {
        'count': 0,
        'total_gmv': 0,
        'deals': []
    })

    all_requests = []

    for row in rows:
        request_data = {}
        for i, col in enumerate(cols):
            if i < len(row):
                field_name = col.get('name', col.get('display_name', f'field_{i}'))
                request_data[field_name] = row[i]

        all_requests.append(request_data)

        # Extract date
        created_date = request_data.get('createdDate', '')
        if created_date:
            if isinstance(created_date, str):
                date_str = created_date[:10]
            else:
                date_str = str(created_date)[:10]

            # Get GMV
            gmv = 0
            if 'totalPrice' in request_data:
                gmv = float(request_data['totalPrice']) if request_data['totalPrice'] else 0

            # Get equipment type
            equipment = request_data.get('equipmentType') or request_data.get('category') or request_data.get('subcategory') or 'Unknown'
            if isinstance(equipment, dict):
                equipment = equipment.get('name', 'Unknown')

            # Update daily stats
            daily_stats[date_str]['requests'] += 1
            daily_stats[date_str]['total_gmv'] += gmv
            daily_stats[date_str]['equipment_types'][equipment] += 1
            daily_stats[date_str]['equipment_gmv'][equipment] += gmv

            # Update equipment breakdown
            equipment_breakdown[equipment]['count'] += 1
            equipment_breakdown[equipment]['total_gmv'] += gmv
            equipment_breakdown[equipment]['deals'].append({
                'date': date_str,
                'gmv': gmv,
                'status': request_data.get('status', 'Unknown')
            })

    # Display daily breakdown
    print("\n\n📅 DAILY BREAKDOWN")
    print("=" * 160)
    print(f"\n{'Date':<15} {'Requests':>10} {'GMV':>15} {'Avg GMV':>15}")
    print("-" * 80)

    sorted_dates = sorted(daily_stats.keys())
    total_requests = 0
    total_gmv = 0

    for date in sorted_dates:
        stats = daily_stats[date]
        avg_gmv = stats['total_gmv'] / stats['requests'] if stats['requests'] > 0 else 0

        print(f"{date:<15} {stats['requests']:>10} ${stats['total_gmv']:>14,.2f} ${avg_gmv:>14,.2f}")

        total_requests += stats['requests']
        total_gmv += stats['total_gmv']

    print("-" * 80)
    avg_overall = total_gmv / total_requests if total_requests > 0 else 0
    print(f"{'TOTAL':<15} {total_requests:>10} ${total_gmv:>14,.2f} ${avg_overall:>14,.2f}")

    # Display equipment breakdown
    print("\n\n🚜 EQUIPMENT TYPE BREAKDOWN")
    print("=" * 160)
    print(f"\n{'Equipment Type':<40} {'Count':>10} {'Total GMV':>15} {'Avg GMV':>15} {'% of Total':>12}")
    print("-" * 120)

    sorted_equipment = sorted(equipment_breakdown.items(), key=lambda x: x[1]['total_gmv'], reverse=True)

    for equipment, data in sorted_equipment:
        avg_gmv = data['total_gmv'] / data['count'] if data['count'] > 0 else 0
        pct = (data['total_gmv'] / total_gmv * 100) if total_gmv > 0 else 0

        equipment_short = equipment[:37] + '...' if len(equipment) > 40 else equipment
        print(f"{equipment_short:<40} {data['count']:>10} ${data['total_gmv']:>14,.2f} ${avg_gmv:>14,.2f} {pct:>11.1f}%")

    # Summary stats
    print("\n\n📊 SUMMARY STATISTICS")
    print("=" * 160)
    print(f"\n📈 Overall Performance:")
    print(f"   • Total Requests: {total_requests}")
    print(f"   • Total GMV: ${total_gmv:,.2f}")
    print(f"   • Average GMV per Request: ${avg_overall:,.2f}")
    print(f"   • Average Requests per Day: {total_requests / len(sorted_dates):.1f}")
    print(f"   • Average Daily GMV: ${total_gmv / len(sorted_dates):,.2f}")

    print(f"\n🚜 Equipment Insights:")
    print(f"   • Total Equipment Types: {len(equipment_breakdown)}")
    if sorted_equipment:
        top_equipment = sorted_equipment[0]
        print(f"   • Top Equipment by GMV: {top_equipment[0]} (${top_equipment[1]['total_gmv']:,.2f})")
        print(f"   • Top Equipment by Volume: {sorted(equipment_breakdown.items(), key=lambda x: x[1]['count'], reverse=True)[0][0]} ({sorted(equipment_breakdown.items(), key=lambda x: x[1]['count'], reverse=True)[0][1]['count']} requests)")

else:
    print("⚠️  Could not retrieve supplier requests data")
    print("   Trying alternative approach...")

# Step 3: Query opportunities/deals collection
print("\n\n📊 STEP 3: QUERYING OPPORTUNITIES COLLECTION")
print("=" * 160)

query_opportunities = {
    "database": 2,
    "type": "native",
    "native": {
        "query": json.dumps([
            {
                "$match": {
                    "CreatedDate": {
                        "$gte": {"$date": "2026-02-01T00:00:00.000Z"},
                        "$lte": {"$date": "2026-02-23T23:59:59.999Z"}
                    }
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "CreatedDate": 1,
                    "StageName": 1,
                    "Amount": 1,
                    "Type": 1,
                    "CloseDate": 1
                }
            }
        ]),
        "collection": "opportunities"
    }
}

print("\n🔍 Querying opportunities collection...")
opportunities_result = run_metabase_query(query_opportunities)

if opportunities_result and opportunities_result.get('status') == 'completed':
    rows = opportunities_result.get('data', {}).get('rows', [])
    cols = opportunities_result.get('data', {}).get('cols', [])

    print(f"✅ Found {len(rows)} opportunities in February")

    if len(rows) > 0:
        # Process opportunities
        stage_breakdown = defaultdict(lambda: {'count': 0, 'amount': 0})

        for row in rows:
            opp_data = {}
            for i, col in enumerate(cols):
                if i < len(row):
                    field_name = col.get('name', col.get('display_name', f'field_{i}'))
                    opp_data[field_name] = row[i]

            stage = opp_data.get('StageName', 'Unknown')
            amount = float(opp_data.get('Amount', 0)) if opp_data.get('Amount') else 0

            stage_breakdown[stage]['count'] += 1
            stage_breakdown[stage]['amount'] += amount

        print(f"\n📊 Opportunities by Stage:")
        print(f"\n{'Stage':<40} {'Count':>10} {'Total Amount':>15}")
        print("-" * 80)

        for stage, data in sorted(stage_breakdown.items(), key=lambda x: x[1]['amount'], reverse=True):
            print(f"{stage:<40} {data['count']:>10} ${data['amount']:>14,.2f}")
else:
    print("⚠️  Could not retrieve opportunities data")

# Step 4: Query calls data
print("\n\n📞 STEP 4: QUERYING CALLS DATA")
print("=" * 160)

query_calls = {
    "database": 2,
    "type": "native",
    "native": {
        "query": json.dumps([
            {
                "$match": {
                    "callTime": {
                        "$gte": {"$date": "2026-02-01T00:00:00.000Z"},
                        "$lte": {"$date": "2026-02-23T23:59:59.999Z"}
                    }
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "callTime": 1,
                    "callDuration": 1,
                    "callMedium": 1,
                    "campaignName": 1
                }
            }
        ]),
        "collection": "calls"
    }
}

print("\n🔍 Querying calls collection...")
calls_result = run_metabase_query(query_calls)

if calls_result and calls_result.get('status') == 'completed':
    rows = calls_result.get('data', {}).get('rows', [])

    print(f"✅ Found {len(rows)} calls in February")

    # Process calls by day
    daily_calls = defaultdict(int)

    if len(rows) > 0:
        cols = calls_result.get('data', {}).get('cols', [])

        for row in rows:
            call_data = {}
            for i, col in enumerate(cols):
                if i < len(row):
                    field_name = col.get('name', col.get('display_name', f'field_{i}'))
                    call_data[field_name] = row[i]

            call_time = call_data.get('callTime', '')
            if call_time:
                date_str = str(call_time)[:10]
                daily_calls[date_str] += 1

        print(f"\n📅 Daily Call Volume:")
        print(f"\n{'Date':<15} {'Calls':>10}")
        print("-" * 30)

        total_calls = 0
        for date in sorted(daily_calls.keys()):
            print(f"{date:<15} {daily_calls[date]:>10}")
            total_calls += daily_calls[date]

        print("-" * 30)
        print(f"{'TOTAL':<15} {total_calls:>10}")
        print(f"{'AVG/DAY':<15} {total_calls / len(daily_calls):>10.1f}")
else:
    print("⚠️  Could not retrieve calls data")

print("\n\n" + "=" * 160)
print("✅ METABASE DATA EXTRACTION COMPLETE")
print("=" * 160)

print("\n\n💡 DATA SUMMARY:")
print("   • Pulled supplier requests/orders for Feb 1-23")
print("   • Equipment type breakdown with GMV")
print("   • Daily performance metrics")
print("   • Opportunities pipeline data")
print("   • Call volume by day")
