import urllib.request
import json

METABASE_URL = "https://starry-bolt.metabaseapp.com"
METABASE_KEY = "mb_XRBKMlQkz3Waw1jpgaNUVIYM+nEkF2bCexU1sUI0Uks="

def metabase_request(endpoint, method="GET", data=None):
    """Make a request to the Metabase API"""
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
        print(e.read().decode())
        raise
    except Exception as e:
        print(f"Error: {e}")
        raise

# Test connection by getting databases
print("Testing Metabase connection...")
print(f"Instance: {METABASE_URL}")
print("-" * 50)

try:
    # Get available databases
    databases = metabase_request("/api/database")
    print(f"\n✓ Connection successful!")

    # Check if response is a dict with 'data' key or a list
    if isinstance(databases, dict):
        if 'data' in databases:
            databases = databases['data']
        else:
            print(f"\nDatabase response structure: {databases.keys()}")

    if isinstance(databases, list):
        print(f"\nAvailable Databases ({len(databases)}):")
        for db in databases:
            print(f"  - ID: {db.get('id')}, Name: {db.get('name')}, Engine: {db.get('engine', 'N/A')}")
    else:
        print(f"\nDatabases (full response):")
        print(json.dumps(databases, indent=2)[:500])

    # Get collections
    collections = metabase_request("/api/collection")

    if isinstance(collections, dict) and 'data' in collections:
        collections = collections['data']

    if isinstance(collections, list):
        print(f"\nAvailable Collections ({len(collections)}):")
        for coll in collections[:10]:  # Show first 10
            print(f"  - ID: {coll.get('id')}, Name: {coll.get('name')}")
    else:
        print(f"\nCollections (sample):")
        print(json.dumps(collections, indent=2)[:500])

except Exception as e:
    import traceback
    print(f"\n✗ Connection failed: {e}")
    traceback.print_exc()
