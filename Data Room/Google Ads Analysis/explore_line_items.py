import urllib.request
import json

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
print("EXPLORING LINE ITEMS STRUCTURE")
print("=" * 120)

# Query sample invoices with lines
query_sample = {
    "database": 2,
    "type": "native",
    "native": {
        "query": json.dumps([
            {
                "$match": {
                    "createdDate": {
                        "$gte": {"$date": "2026-02-01T00:00:00.000Z"},
                        "$lte": {"$date": "2026-02-23T23:59:59.999Z"}
                    },
                    "totalAmt": {"$gt": 100}
                }
            },
            {
                "$limit": 3
            }
        ]),
        "collection": "invoicesv2"
    }
}

result = run_metabase_query(query_sample)

if result and result.get('status') == 'completed':
    rows = result.get('data', {}).get('rows', [])
    cols = result.get('data', {}).get('cols', [])

    col_map = {}
    for i, col in enumerate(cols):
        field_name = col.get('name', col.get('display_name', f'field_{i}'))
        col_map[field_name] = i

    for row_idx, row in enumerate(rows[:3], 1):
        invoice = {}
        for field, idx in col_map.items():
            if idx < len(row):
                invoice[field] = row[idx]

        print(f"\n{'='*120}")
        print(f"INVOICE #{row_idx}")
        print(f"{'='*120}")
        print(f"Total Amount: ${invoice.get('totalAmt', 0):,.2f}")
        print(f"Region: {invoice.get('region', 'Unknown')}")
        print(f"Order Number: {invoice.get('orderNumber', 'Unknown')}")

        lines = invoice.get('lines', [])
        print(f"\nNumber of Line Items: {len(lines) if lines else 0}")

        if lines and isinstance(lines, list):
            for line_idx, line in enumerate(lines[:2], 1):  # Show first 2 line items
                print(f"\n--- Line Item #{line_idx} ---")
                if isinstance(line, dict):
                    # Print all fields in the line item
                    for key, value in line.items():
                        if key not in ['__v', '_id']:  # Skip internal fields
                            if isinstance(value, (str, int, float, bool)):
                                print(f"  {key}: {value}")
                            elif isinstance(value, dict):
                                print(f"  {key}: {json.dumps(value, indent=4)[:200]}...")
                            elif isinstance(value, list):
                                print(f"  {key}: [list with {len(value)} items]")
                else:
                    print(f"  Line item is {type(line)}: {str(line)[:100]}")

print("\n" + "=" * 120)
