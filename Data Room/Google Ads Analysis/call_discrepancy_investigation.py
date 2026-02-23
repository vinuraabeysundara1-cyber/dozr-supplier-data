import urllib.request
import json
from datetime import datetime, timedelta
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

print("=" * 160)
print("🔍 CALL DISCREPANCY INVESTIGATION")
print("=" * 160)
print("\n📊 Problem Summary:")
print("   • Call Rail unique calls: Feb 8-14 = 121, Feb 15-21 = 172 (+42%)")
print("   • Twilio sales calls: Feb 8-14 = 431, Feb 15-21 = 435 (flat)")
print("   • Google Ads Phone Calls: ~140 → ~210")
print("   • Conversion rate dropped from 17% to 12.6% around Feb 10")
print("\n" + "=" * 160)

# Step 1: Explore available databases and tables
print("\n🔍 STEP 1: EXPLORING METABASE DATA SOURCES")
print("=" * 160)

# Get list of databases
databases = metabase_request("/api/database")
if databases:
    print("\n📚 Available Databases:")
    for db in databases.get('data', []):
        print(f"   • {db.get('name')} (ID: {db.get('id')})")

# Get database metadata for MongoDB
db_id = 2  # Production MongoDB
db_metadata = metabase_request(f"/api/database/{db_id}/metadata")

if db_metadata:
    print(f"\n📋 Collections in Production MongoDB:")
    tables = db_metadata.get('tables', [])

    # Look for call-related collections
    call_related = []
    for table in tables:
        table_name = table.get('name', '').lower()
        if any(keyword in table_name for keyword in ['call', 'phone', 'twilio', 'rail', 'contact', 'lead', 'communication']):
            call_related.append(table)
            print(f"   ✓ {table.get('name')} (ID: {table.get('id')})")

    print(f"\n   Found {len(call_related)} potentially relevant collections")

    # Get detailed schema for call-related collections
    if call_related:
        print("\n🔍 Examining Call-Related Collections:")
        for table in call_related[:3]:  # Limit to first 3 to avoid overwhelming output
            table_id = table.get('id')
            table_name = table.get('name')
            print(f"\n   📊 Collection: {table_name}")

            # Get fields/schema
            fields = table.get('fields', [])
            if fields:
                print(f"      Fields ({len(fields)} total):")
                for field in fields[:10]:  # Show first 10 fields
                    field_name = field.get('name')
                    field_type = field.get('base_type', 'unknown')
                    print(f"         - {field_name} ({field_type})")

# Step 2: Search for existing saved questions/queries
print("\n\n🔍 STEP 2: SEARCHING FOR EXISTING QUERIES")
print("=" * 160)

# Search for call-related saved questions
search_terms = ['call', 'phone', 'twilio', 'rail', 'sales']
for term in search_terms:
    search_results = metabase_request(f"/api/search?q={term}")
    if search_results and search_results.get('data'):
        print(f"\n📝 Search results for '{term}':")
        for result in search_results.get('data', [])[:5]:  # Limit to 5 results
            print(f"   • {result.get('name')} (Type: {result.get('model')}, ID: {result.get('id')})")

# Step 3: Get collections list
print("\n\n🔍 STEP 3: AVAILABLE COLLECTIONS")
print("=" * 160)

collections = metabase_request("/api/collection")
if collections:
    print("\n📁 Collections:")
    for collection in collections:
        if isinstance(collection, dict):
            print(f"   • {collection.get('name')} (ID: {collection.get('id')})")

print("\n\n" + "=" * 160)
print("✅ DATA SOURCE EXPLORATION COMPLETE")
print("=" * 160)

print("\n\n📋 NEXT STEPS:")
print("   1. Identify the correct collection/table for call data")
print("   2. Query call logs for Feb 1-21 with routing information")
print("   3. Pull Google Ads call data for comparison")
print("   4. Analyze discrepancies and provide recommendations")

print("\n💡 Based on exploration, we need to:")
print("   • Check 'supplierrequests' or similar collection for call attribution")
print("   • Query any Twilio integration tables")
print("   • Cross-reference with Google Ads call conversion data")
print("   • Look for call routing/queue information")
