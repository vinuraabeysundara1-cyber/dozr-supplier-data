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
        error_body = e.read().decode()
        print(error_body)
        return None

print("=" * 140)
print("💰 GMV ANALYSIS BY EQUIPMENT TYPE, WEIGHT CLASS, AND RENTAL DURATION")
print("=" * 140)

# First, let's explore what tables/collections are available
print("\n📊 Step 1: Exploring available tables in MongoDB...")

# Query to get table metadata
tables_query = {
    "database": 2,
    "type": "query",
    "query": {
        "source-table": "card__1"
    }
}

# Let's try to get the database metadata
db_metadata = metabase_request("/api/database/2/metadata")

if db_metadata:
    print("\n✅ Database metadata retrieved")

    # Look for tables related to orders, requests, or revenue
    if 'tables' in db_metadata:
        print(f"\n📋 Available Collections/Tables ({len(db_metadata['tables'])}):")
        for table in db_metadata['tables'][:20]:  # Show first 20
            table_name = table.get('name', 'N/A')
            table_id = table.get('id', 'N/A')
            display_name = table.get('display_name', 'N/A')
            print(f"   • ID: {table_id} | Name: {table_name} | Display: {display_name}")

            # Show fields for relevant tables
            if any(keyword in table_name.lower() for keyword in ['order', 'request', 'booking', 'revenue', 'supplier']):
                print(f"     → Relevant table found! Fields:")
                if 'fields' in table:
                    for field in table['fields'][:15]:  # Show first 15 fields
                        field_name = field.get('name', 'N/A')
                        field_type = field.get('base_type', 'N/A')
                        print(f"        - {field_name} ({field_type})")
else:
    print("❌ Could not retrieve database metadata")

print("\n" + "=" * 140)
print("✅ METADATA EXPLORATION COMPLETE")
print("=" * 140)
