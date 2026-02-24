from google.ads.googleads.client import GoogleAdsClient
import urllib.request
import json
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Load Google Ads credentials
client = GoogleAdsClient.load_from_storage('/Users/vinuraabeysundara/Desktop/ICG/DOZR/Data Room/Config/google-ads.yaml')
ga_service = client.get_service('GoogleAdsService')
customer_id = '8531896842'

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

print("=" * 160)
print("DOZERS CAMPAIGN - LOCATION TARGETING ANALYSIS")
print("=" * 160)

# Step 1: Get current location targeting from Google Ads
print("\n\n📍 STEP 1: CURRENT GOOGLE ADS LOCATION TARGETING")
print("=" * 160)

# Query campaign settings
query_campaign = """
    SELECT
        campaign.id,
        campaign.name,
        campaign.status
    FROM campaign
    WHERE campaign.name LIKE '%Dozer%'
        AND campaign.name LIKE '%US%'
        AND campaign.name NOT LIKE '%Expansion%'
        AND campaign.status = 'ENABLED'
"""

response_campaign = ga_service.search(customer_id=customer_id, query=query_campaign)

campaign_id = None
campaign_name = None

for row in response_campaign:
    campaign_id = row.campaign.id
    campaign_name = row.campaign.name
    print(f"\n✅ Found Campaign: {campaign_name}")
    print(f"   Campaign ID: {campaign_id}")

if not campaign_id:
    print("❌ No active Dozers campaign found")
    exit()

# Get geo targeting for the campaign
print("\n📍 Current Location Targeting:")
print("-" * 160)

query_geo_targets = f"""
    SELECT
        campaign_criterion.location.geo_target_constant,
        campaign_criterion.negative,
        campaign_criterion.type,
        campaign_criterion.status
    FROM campaign_criterion
    WHERE campaign.id = {campaign_id}
        AND campaign_criterion.type = 'LOCATION'
"""

response_geo = ga_service.search(customer_id=customer_id, query=query_geo_targets)

targeted_locations = []
excluded_locations = []

for row in response_geo:
    geo_target = row.campaign_criterion.location.geo_target_constant
    is_negative = row.campaign_criterion.negative
    status = str(row.campaign_criterion.status)

    # Extract location ID from resource name
    location_id = geo_target.split('/')[-1] if geo_target else 'Unknown'

    if is_negative:
        excluded_locations.append(location_id)
    else:
        targeted_locations.append(location_id)

print(f"\n{'Type':<20} {'Count':<10} {'Location IDs'}")
print("-" * 100)
print(f"{'Targeted':<20} {len(targeted_locations):<10} {', '.join(targeted_locations[:10])}{'...' if len(targeted_locations) > 10 else ''}")
print(f"{'Excluded':<20} {len(excluded_locations):<10} {', '.join(excluded_locations[:5])}{'...' if len(excluded_locations) > 5 else ''}")

# Decode location IDs to names (common ones)
location_mapping = {
    '2840': 'United States',
    '21137': 'Texas',
    '1014221': 'Kentucky',
    '1023191': 'Utah',
    '9029378': 'Kansas',
    '1015116': 'Louisiana',
    '1023150': 'Indiana',
    '1023511': 'California',
    '1015297': 'Florida',
    '1022913': 'Arizona',
}

print("\n📋 Decoded Targeted Locations:")
for loc_id in targeted_locations[:20]:
    loc_name = location_mapping.get(loc_id, f'Unknown (ID: {loc_id})')
    print(f"   • {loc_name}")

# Step 2: Get actual GMV by location from Metabase
print("\n\n" + "=" * 160)
print("💰 STEP 2: ACTUAL DOZER GMV BY LOCATION (METABASE DATA)")
print("=" * 160)

# Query invoices for dozer equipment
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
                    }
                }
            }
        ]),
        "collection": "invoicesv2"
    }
}

print("\n🔍 Querying Metabase for dozer rentals...")
result = run_metabase_query(query_invoices)

location_gmv = defaultdict(lambda: {'count': 0, 'gmv': 0, 'equipment_types': set()})

if result and result.get('status') == 'completed':
    rows = result.get('data', {}).get('rows', [])
    cols = result.get('data', {}).get('cols', [])

    print(f"✅ Retrieved {len(rows)} invoices")

    col_map = {}
    for i, col in enumerate(cols):
        field_name = col.get('name', col.get('display_name', f'field_{i}'))
        col_map[field_name] = i

    for row in rows:
        invoice = {}
        for field, idx in col_map.items():
            if idx < len(row):
                invoice[field] = row[idx]

        lines = invoice.get('lines', [])
        region = invoice.get('region', 'Unknown')

        if lines and isinstance(lines, list):
            for line in lines:
                if isinstance(line, dict) and line.get('type') == 'rental' and not line.get('isCanceled'):
                    description = line.get('description', '').strip().lower()
                    amount = float(line.get('amount', 0))

                    # Check if it's dozer equipment
                    if description and amount > 0 and ('dozer' in description or 'bulldozer' in description):
                        location_gmv[region]['count'] += 1
                        location_gmv[region]['gmv'] += amount
                        location_gmv[region]['equipment_types'].add(description)

    # Sort by GMV
    sorted_locations = sorted(location_gmv.items(), key=lambda x: x[1]['gmv'], reverse=True)

    print("\n📊 Dozer GMV by Location:")
    print("-" * 160)
    print(f"\n{'Rank':<6} {'State/Region':<15} {'Rentals':>10} {'Total GMV':>15} {'Avg GMV':>15} {'% of Total':>12}")
    print("-" * 90)

    total_gmv = sum(d['gmv'] for d in location_gmv.values())
    total_rentals = sum(d['count'] for d in location_gmv.values())

    for rank, (location, data) in enumerate(sorted_locations, 1):
        rentals = data['count']
        gmv = data['gmv']
        avg_gmv = gmv / rentals if rentals > 0 else 0
        pct = (gmv / total_gmv * 100) if total_gmv > 0 else 0

        print(f"{rank:<6} {location:<15} {rentals:>10} ${gmv:>14,.2f} ${avg_gmv:>14,.2f} {pct:>11.1f}%")

    print("-" * 90)
    print(f"{'TOTAL':<22} {total_rentals:>10} ${total_gmv:>14,.2f}")

    # State code mapping to full names and Google Ads geo target IDs
    state_mapping = {
        'TX': ('Texas', '21137'),
        'KY': ('Kentucky', '1014221'),
        'YT': ('Yukon Territory (Canada)', 'N/A'),
        'ON': ('Ontario (Canada)', 'N/A'),
        'AB': ('Alberta (Canada)', 'N/A'),
        'LA': ('Louisiana', '1015116'),
        'UT': ('Utah', '1023191'),
        'CA': ('California', '1023511'),
        'FL': ('Florida', '1015297'),
        'KS': ('Kansas', '9029378'),
        'IN': ('Indiana', '1023150'),
        'AZ': ('Arizona', '1022913'),
        'CO': ('Colorado', '1014032'),
        'TN': ('Tennessee', '1006381'),
        'AL': ('Alabama', '1014210'),
        'MO': ('Missouri', '1025149'),
        'OK': ('Oklahoma', '1021206'),
        'BC': ('British Columbia (Canada)', 'N/A'),
    }

    # Step 3: Cross-reference and recommendations
    print("\n\n" + "=" * 160)
    print("🔍 STEP 3: LOCATION TARGETING ANALYSIS & RECOMMENDATIONS")
    print("=" * 160)

    # Analyze top GMV locations
    print("\n✅ TOP GMV LOCATIONS (Should be targeted):")
    print("-" * 160)

    top_5_gmv = 0
    for rank, (location, data) in enumerate(sorted_locations[:10], 1):
        gmv = data['gmv']
        rentals = data['count']
        pct = (gmv / total_gmv * 100) if total_gmv > 0 else 0

        if rank <= 5:
            top_5_gmv += gmv

        state_info = state_mapping.get(location, (location, 'Unknown'))
        state_name = state_info[0]
        geo_id = state_info[1]

        is_canada = 'Canada' in state_name
        is_targeted = geo_id in targeted_locations if geo_id != 'N/A' and geo_id != 'Unknown' else False

        status = "✅ TARGETED" if is_targeted else "❌ NOT TARGETED" if not is_canada else "🇨🇦 CANADA"

        print(f"{rank}. {state_name:<35} ${gmv:>12,.2f} ({pct:>5.1f}%) | {rentals:>3} rentals | {status}")
        if not is_canada and not is_targeted and geo_id != 'Unknown':
            print(f"   ⚠️  RECOMMENDATION: Add geo target ID {geo_id} to campaign")

    top_5_pct = (top_5_gmv / total_gmv * 100) if total_gmv > 0 else 0
    print(f"\n💡 Top 5 locations = ${top_5_gmv:,.2f} ({top_5_pct:.1f}% of total dozer GMV)")

    # Identify Canadian traffic (should be excluded)
    canadian_locations = [(loc, data) for loc, data in sorted_locations if loc in ['YT', 'ON', 'AB', 'BC', 'QC', 'MB', 'SK', 'NS', 'NB', 'PE', 'NL']]

    if canadian_locations:
        print("\n\n🇨🇦 CANADIAN TRAFFIC (Should be excluded):")
        print("-" * 160)
        canadian_gmv = sum(data['gmv'] for _, data in canadian_locations)
        canadian_rentals = sum(data['count'] for _, data in canadian_locations)
        canadian_pct = (canadian_gmv / total_gmv * 100) if total_gmv > 0 else 0

        print(f"   • Total Canadian GMV: ${canadian_gmv:,.2f} ({canadian_pct:.1f}% of total)")
        print(f"   • Total Canadian Rentals: {canadian_rentals}")
        print(f"   • Locations: {', '.join([state_mapping[loc][0] for loc, _ in canadian_locations])}")
        print(f"\n   ⚠️  RECOMMENDATION: Add location exclusions for Canada")
        print(f"      - Add geo target 2124 (Canada) as excluded location")

    # Summary recommendations
    print("\n\n" + "=" * 160)
    print("📋 SUMMARY RECOMMENDATIONS")
    print("=" * 160)

    print("\n✅ LOCATIONS TO ADD (High GMV, currently not targeted):")
    for rank, (location, data) in enumerate(sorted_locations[:10], 1):
        state_info = state_mapping.get(location, (location, 'Unknown'))
        state_name = state_info[0]
        geo_id = state_info[1]

        is_canada = 'Canada' in state_name
        is_targeted = geo_id in targeted_locations if geo_id != 'N/A' and geo_id != 'Unknown' else False

        if not is_canada and not is_targeted and geo_id not in ['Unknown', 'N/A']:
            pct = (data['gmv'] / total_gmv * 100) if total_gmv > 0 else 0
            print(f"   • {state_name:<30} Geo ID: {geo_id:<12} GMV: ${data['gmv']:>12,.2f} ({pct:>5.1f}%)")

    print("\n❌ LOCATIONS TO EXCLUDE (Canadian traffic):")
    if canadian_locations:
        print(f"   • Canada (Geo ID: 2124) - ${canadian_gmv:,.2f} wasted spend")
    else:
        print(f"   • No Canadian traffic detected ✅")

    print("\n📊 TARGETING EFFICIENCY:")
    us_locations = [(loc, data) for loc, data in sorted_locations if loc not in ['YT', 'ON', 'AB', 'BC', 'QC', 'MB', 'SK', 'NS', 'NB', 'PE', 'NL']]
    us_gmv = sum(data['gmv'] for _, data in us_locations)
    us_pct = (us_gmv / total_gmv * 100) if total_gmv > 0 else 0

    print(f"   • US GMV: ${us_gmv:,.2f} ({us_pct:.1f}%)")
    print(f"   • Canadian GMV: ${canadian_gmv if canadian_locations else 0:,.2f} ({canadian_pct if canadian_locations else 0:.1f}%)")
    print(f"   • Focus on top 5 US states for maximum efficiency")

    print("\n\n🎯 ACTION ITEMS:")
    print("=" * 160)
    print("\n1. ✅ Verify current location targeting includes:")
    for rank, (location, data) in enumerate(sorted_locations[:5], 1):
        state_info = state_mapping.get(location, (location, 'Unknown'))
        state_name = state_info[0]
        geo_id = state_info[1]
        if 'Canada' not in state_name and geo_id not in ['Unknown', 'N/A']:
            print(f"   ☐ {state_name} (Geo ID: {geo_id})")

    print("\n2. ❌ Add location exclusions:")
    if canadian_locations:
        print(f"   ☐ Canada (Geo ID: 2124)")
        print(f"      Reason: ${canadian_gmv:,.2f} in wasted spend")

    print("\n3. 📊 Consider adding these secondary markets:")
    for rank, (location, data) in enumerate(sorted_locations[5:10], 6):
        state_info = state_mapping.get(location, (location, 'Unknown'))
        state_name = state_info[0]
        geo_id = state_info[1]
        if 'Canada' not in state_name and geo_id not in ['Unknown', 'N/A']:
            pct = (data['gmv'] / total_gmv * 100) if total_gmv > 0 else 0
            print(f"   ☐ {state_name} (Geo ID: {geo_id}) - ${data['gmv']:,.2f} ({pct:.1f}%)")

    print("\n4. 🎚️  Bid adjustments by location:")
    print("   Based on GMV performance, consider these bid modifiers:")
    for rank, (location, data) in enumerate(sorted_locations[:5], 1):
        state_info = state_mapping.get(location, (location, 'Unknown'))
        state_name = state_info[0]
        if 'Canada' not in state_name:
            pct = (data['gmv'] / total_gmv * 100) if total_gmv > 0 else 0
            if pct > 30:
                bid_adj = "+30% to +50%"
            elif pct > 15:
                bid_adj = "+15% to +30%"
            elif pct > 5:
                bid_adj = "+10% to +15%"
            else:
                bid_adj = "0% (baseline)"
            print(f"   ☐ {state_name:<30} {bid_adj:>20} ({pct:.1f}% of GMV)")

else:
    print("❌ Failed to retrieve Metabase data")

print("\n" + "=" * 160)
print("✅ LOCATION ANALYSIS COMPLETE")
print("=" * 160)
