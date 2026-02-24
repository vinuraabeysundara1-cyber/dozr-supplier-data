import urllib.request
import json
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

print("=" * 120)
print("🚜 EXCAVATOR DEALS ANALYSIS - METABASE DATA")
print("Period: February 1-23, 2026")
print("=" * 120)

# Query invoices for excavator deals
print("\n\n📊 QUERYING INVOICES FOR EXCAVATOR DEALS...")
print("=" * 120)

query_invoices = {
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
                    "total": 1,
                    "status": 1,
                    "equipmentType": 1,
                    "equipment": 1,
                    "category": 1,
                    "items": 1
                }
            }
        ]),
        "collection": "invoicesv2"
    }
}

invoices_result = run_metabase_query(query_invoices)

excavator_deals = []

if invoices_result and invoices_result.get('status') == 'completed':
    rows = invoices_result.get('data', {}).get('rows', [])
    cols = invoices_result.get('data', {}).get('cols', [])

    print(f"✅ Found {len(rows)} total invoices in February")
    print(f"   Columns available: {[col.get('name', col.get('display_name', '')) for col in cols]}")

    # Look for excavator deals
    for row in rows:
        invoice_data = {}
        for i, col in enumerate(cols):
            if i < len(row):
                field_name = col.get('name', col.get('display_name', f'field_{i}'))
                invoice_data[field_name] = row[i]

        # Check if this is an excavator deal
        invoice_str = str(invoice_data).lower()
        if 'excavat' in invoice_str:
            excavator_deals.append(invoice_data)

    print(f"\n🚜 Excavator Deals Found: {len(excavator_deals)}")

    if excavator_deals:
        print("\n" + "=" * 120)
        print("EXCAVATOR DEAL DETAILS:")
        print("=" * 120)

        total_value = 0
        for i, deal in enumerate(excavator_deals, 1):
            created_date = deal.get('createdDate', 'N/A')
            if created_date and created_date != 'N/A':
                created_date = str(created_date)[:10]

            total = deal.get('total', 0) or 0
            total_value += float(total) if total else 0

            print(f"\nDeal #{i}:")
            print(f"  Date: {created_date}")
            print(f"  Total: ${float(total) if total else 0:,.2f}")
            print(f"  Status: {deal.get('status', 'N/A')}")
            print(f"  Equipment Type: {deal.get('equipmentType', 'N/A')}")
            print(f"  Category: {deal.get('category', 'N/A')}")

        print("\n" + "=" * 120)
        print(f"📊 TOTAL EXCAVATOR DEALS: {len(excavator_deals)}")
        print(f"💰 TOTAL VALUE: ${total_value:,.2f}")
        print(f"📈 AVERAGE DEAL VALUE: ${total_value / len(excavator_deals) if excavator_deals else 0:,.2f}")
    else:
        print("   ⚠️  No excavator deals found in invoices")

# Also check opportunities collection
print("\n\n📊 QUERYING OPPORTUNITIES FOR EXCAVATOR DEALS...")
print("=" * 120)

query_opportunities = {
    "database": 2,
    "type": "native",
    "native": {
        "query": json.dumps([
            {
                "$match": {
                    "createdAt": {
                        "$gte": {"$date": "2026-02-01T00:00:00.000Z"},
                        "$lte": {"$date": "2026-02-23T23:59:59.999Z"}
                    }
                }
            }
        ]),
        "collection": "opportunities"
    }
}

opps_result = run_metabase_query(query_opportunities)

excavator_opps = []

if opps_result and opps_result.get('status') == 'completed':
    rows = opps_result.get('data', {}).get('rows', [])
    cols = opps_result.get('data', {}).get('cols', [])

    print(f"✅ Found {len(rows)} total opportunities in February")

    # Look for excavator opportunities
    for row in rows:
        opp_data = {}
        for i, col in enumerate(cols):
            if i < len(row):
                field_name = col.get('name', col.get('display_name', f'field_{i}'))
                opp_data[field_name] = row[i]

        # Check if this is an excavator opportunity
        opp_str = str(opp_data).lower()
        if 'excavat' in opp_str:
            excavator_opps.append(opp_data)

    print(f"🚜 Excavator Opportunities Found: {len(excavator_opps)}")

    if excavator_opps:
        print(f"   (These may or may not have closed as deals)")

# Also check supplier requests
print("\n\n📊 QUERYING SUPPLIER REQUESTS FOR EXCAVATOR REQUESTS...")
print("=" * 120)

query_requests = {
    "database": 2,
    "type": "native",
    "native": {
        "query": json.dumps([
            {
                "$match": {
                    "createdAt": {
                        "$gte": {"$date": "2026-02-01T00:00:00.000Z"},
                        "$lte": {"$date": "2026-02-23T23:59:59.999Z"}
                    }
                }
            }
        ]),
        "collection": "supplierrequests"
    }
}

requests_result = run_metabase_query(query_requests)

excavator_requests = []

if requests_result and requests_result.get('status') == 'completed':
    rows = requests_result.get('data', {}).get('rows', [])
    cols = requests_result.get('data', {}).get('cols', [])

    print(f"✅ Found {len(rows)} total supplier requests in February")

    # Look for excavator requests
    for row in rows:
        req_data = {}
        for i, col in enumerate(cols):
            if i < len(row):
                field_name = col.get('name', col.get('display_name', f'field_{i}'))
                req_data[field_name] = row[i]

        # Check if this is an excavator request
        req_str = str(req_data).lower()
        if 'excavat' in req_str:
            excavator_requests.append(req_data)

    print(f"🚜 Excavator Requests Found: {len(excavator_requests)}")

print("\n\n" + "=" * 120)
print("📊 EXCAVATOR SUMMARY - FEB 1-23, 2026")
print("=" * 120)
print(f"✅ Confirmed Deals (Invoices): {len(excavator_deals)}")
print(f"📋 Opportunities: {len(excavator_opps)}")
print(f"📞 Supplier Requests: {len(excavator_requests)}")
print("\n💡 NOTE: Google Ads showed only $48.50 in excavator conversion value for this period")
print("   This suggests excavator campaigns are not generating closed deals effectively")
print("=" * 120)
