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
        print(e.read().decode())
        return None

print("=" * 120)
print("🔌 METABASE API CONNECTION TEST")
print("=" * 120)

# Test 1: Get current user info
print("\n1. Testing API Connection - Getting Current User Info...")
user_info = metabase_request("/api/user/current")
if user_info:
    print(f"   ✅ Connected successfully!")
    print(f"   User: {user_info.get('common_name', 'N/A')}")
    print(f"   Email: {user_info.get('email', 'N/A')}")
else:
    print("   ❌ Connection failed")

# Test 2: Get available databases
print("\n2. Getting Available Databases...")
databases = metabase_request("/api/database")
if databases:
    if isinstance(databases, dict) and 'data' in databases:
        db_list = databases['data']
    else:
        db_list = databases if isinstance(databases, list) else [databases]

    print(f"   ✅ Found {len(db_list)} database(s):")
    for db in db_list:
        if isinstance(db, dict):
            print(f"      • ID: {db.get('id', 'N/A')} | Name: {db.get('name', 'N/A')} | Engine: {db.get('engine', 'N/A')}")
else:
    print("   ❌ Failed to retrieve databases")

# Test 3: Get collections
print("\n3. Getting Available Collections...")
collections = metabase_request("/api/collection")
if collections:
    if isinstance(collections, dict) and 'data' in collections:
        coll_list = collections['data']
    else:
        coll_list = collections if isinstance(collections, list) else [collections]

    print(f"   ✅ Found {len(coll_list)} collection(s):")
    for coll in coll_list[:10]:  # Show first 10
        if isinstance(coll, dict):
            print(f"      • ID: {coll.get('id', 'N/A')} | Name: {coll.get('name', 'N/A')}")
else:
    print("   ❌ Failed to retrieve collections")

print("\n" + "=" * 120)
print("✅ CONNECTION TEST COMPLETE")
print("=" * 120)
