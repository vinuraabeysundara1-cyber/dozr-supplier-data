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
print("EXPLORING METABASE INVOICE DATA STRUCTURE")
print("=" * 120)

# Query just a few sample invoices
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
                    }
                }
            },
            {
                "$limit": 10
            }
        ]),
        "collection": "invoicesv2"
    }
}

result = run_metabase_query(query_sample)

if result and result.get('status') == 'completed':
    rows = result.get('data', {}).get('rows', [])
    cols = result.get('data', {}).get('cols', [])

    print(f"\n✅ Retrieved {len(rows)} sample invoices")
    print(f"\n📋 Available Columns ({len(cols)} total):")
    print("-" * 120)

    for i, col in enumerate(cols):
        field_name = col.get('name', col.get('display_name', f'field_{i}'))
        field_type = col.get('base_type', 'unknown')
        print(f"{i:>3}. {field_name:<40} ({field_type})")

    print("\n\n📊 SAMPLE DATA (First 3 Invoices):")
    print("=" * 120)

    for row_idx, row in enumerate(rows[:3], 1):
        print(f"\n--- Invoice #{row_idx} ---")
        for i, col in enumerate(cols):
            if i < len(row):
                field_name = col.get('name', col.get('display_name', f'field_{i}'))
                value = row[i]

                # Only print non-null values
                if value is not None and value != '':
                    # Truncate long values
                    if isinstance(value, str) and len(value) > 100:
                        value = value[:100] + "..."
                    elif isinstance(value, (list, dict)):
                        value = str(value)[:100] + "..."

                    print(f"  {field_name}: {value}")

else:
    print("❌ Failed to retrieve data")

print("\n" + "=" * 120)
