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
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        return None

print("=" * 140)
print("🔍 EXPLORING METABASE TABLES FOR GMV ANALYSIS")
print("=" * 140)

db_metadata = metabase_request("/api/database/2/metadata")

if db_metadata and 'tables' in db_metadata:
    # Filter for relevant tables
    relevant_keywords = ['order', 'request', 'booking', 'revenue', 'supplier', 'invoice', 'rental', 'opportunity']

    relevant_tables = []
    for table in db_metadata['tables']:
        table_name = table.get('name', '').lower()
        if any(keyword in table_name for keyword in relevant_keywords):
            relevant_tables.append(table)

    print(f"\n📋 Found {len(relevant_tables)} relevant tables for GMV analysis:\n")

    for table in relevant_tables:
        table_name = table.get('name', 'N/A')
        table_id = table.get('id', 'N/A')
        display_name = table.get('display_name', 'N/A')

        print(f"{'━' * 140}")
        print(f"📊 Table: {display_name} (ID: {table_id}, Collection: {table_name})")
        print(f"{'━' * 140}")

        if 'fields' in table:
            print(f"\nFields ({len(table['fields'])}):")
            for field in table['fields']:
                field_name = field.get('name', 'N/A')
                field_type = field.get('base_type', 'N/A')
                display = field.get('display_name', field_name)
                print(f"   • {display} ({field_name}) - Type: {field_type}")

        print()

print("\n" + "=" * 140)
print("✅ EXPLORATION COMPLETE")
print("=" * 140)
