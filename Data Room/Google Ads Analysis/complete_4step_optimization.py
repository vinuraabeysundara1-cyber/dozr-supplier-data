import urllib.request
import json
from collections import defaultdict
from datetime import datetime
from google.ads.googleads.client import GoogleAdsClient
import warnings
warnings.filterwarnings('ignore')

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

print("=" * 180)
print("STEP 1: TOP 10 HIGHEST GMV EQUIPMENT TYPES (SPECIFIC MODELS) - LAST 30 DAYS")
print("Period: January 24 - February 23, 2026")
print("=" * 180)

# Query invoices
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

print("\n🔍 Querying Metabase...")
result = run_metabase_query(query_invoices)

equipment_data = defaultdict(lambda: {
    'count': 0,
    'total_gmv': 0,
    'prices': [],
    'durations': [],
    'locations': defaultdict(int)
})

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
                    description = line.get('description', '').strip()
                    amount = float(line.get('amount', 0))
                    start_date = line.get('startDate', '')
                    end_date = line.get('endDate', '')

                    if description and amount > 0:
                        # Calculate duration
                        duration_days = 0
                        if start_date and end_date:
                            try:
                                start = datetime.fromisoformat(str(start_date).replace('Z', '+00:00'))
                                end = datetime.fromisoformat(str(end_date).replace('Z', '+00:00'))
                                duration_days = max(1, (end - start).days)
                            except:
                                duration_days = 1

                        equipment_data[description]['count'] += 1
                        equipment_data[description]['total_gmv'] += amount
                        equipment_data[description]['prices'].append(amount)
                        equipment_data[description]['locations'][region] += 1
                        if duration_days > 0:
                            equipment_data[description]['durations'].append(duration_days)

    print(f"✅ Processed {sum(d['count'] for d in equipment_data.values())} equipment rentals")

    # Sort by GMV
    sorted_equipment = sorted(equipment_data.items(), key=lambda x: x[1]['total_gmv'], reverse=True)
    total_gmv = sum(d['total_gmv'] for d in equipment_data.values())

    print("\n\n" + "=" * 180)
    print("📊 TOP 10 EQUIPMENT TYPES BY GMV")
    print("=" * 180)
    print(f"\n{'Rank':<6} {'Equipment Type/Model':<70} {'Rentals':>10} {'Total GMV':>14} {'Avg Price':>12} {'% Total':>10}")
    print("-" * 160)

    top_10 = []
    for rank, (equip, data) in enumerate(sorted_equipment[:10], 1):
        count = data['count']
        gmv = data['total_gmv']
        avg_price = gmv / count
        pct = (gmv / total_gmv * 100) if total_gmv > 0 else 0

        equip_display = equip[:67] + "..." if len(equip) > 70 else equip
        print(f"{rank:<6} {equip_display:<70} {count:>10} ${gmv:>13,.2f} ${avg_price:>11,.2f} {pct:>9.1f}%")

        top_10.append((equip, data))

    # Detailed breakdown
    print("\n\n" + "=" * 180)
    print("🔍 DETAILED INFORMATION - TOP 10 EQUIPMENT")
    print("=" * 180)

    for rank, (equip, data) in enumerate(top_10, 1):
        print(f"\n{'='*180}")
        print(f"#{rank}. {equip}")
        print(f"{'='*180}")

        prices = data['prices']
        durations = data['durations']

        print(f"\n💰 Pricing:")
        print(f"   • Total GMV: ${data['total_gmv']:,.2f}")
        print(f"   • Rental Count: {data['count']}")
        print(f"   • Average Price: ${sum(prices)/len(prices):,.2f}")
        print(f"   • Price Range: ${min(prices):,.2f} - ${max(prices):,.2f}")

        if durations:
            print(f"\n⏱️  Duration:")
            print(f"   • Average: {sum(durations)/len(durations):.1f} days")
            print(f"   • Range: {min(durations)}-{max(durations)} days")

        print(f"\n📍 Locations:")
        sorted_locs = sorted(data['locations'].items(), key=lambda x: x[1], reverse=True)
        for loc, cnt in sorted_locs[:5]:
            print(f"   • {loc}: {cnt} rentals")

print("\n\n" + "=" * 180)
print("STEP 2: CAMPAIGN OPTIMIZATION TARGETS")
print("=" * 180)

# Analyze which campaigns should target these equipment types
campaign_recommendations = {}

for equip, data in top_10:
    equip_lower = equip.lower()

    # Determine which campaign should target this equipment
    recommended_campaigns = []

    if 'dozer' in equip_lower or 'bulldozer' in equip_lower:
        recommended_campaigns.append('Dozers Campaign')
    elif 'forklift' in equip_lower or 'telehandler' in equip_lower or 'reach forklift' in equip_lower:
        if 'telehandler' in equip_lower or 'reach' in equip_lower:
            recommended_campaigns.append('Telehandler Campaign')
        else:
            recommended_campaigns.append('Forklift Campaign')
    elif 'loader' in equip_lower:
        if 'skid' in equip_lower or 'compact' in equip_lower:
            recommended_campaigns.append('Loader Campaign (Skid Steer focus)')
        else:
            recommended_campaigns.append('Loader Campaign')
    elif 'excavator' in equip_lower:
        recommended_campaigns.append('Excavator Campaign (⚠️ Currently paused - needs restructure)')
    elif 'scissor' in equip_lower:
        recommended_campaigns.append('Scissor-Lift Campaign')
    elif 'boom' in equip_lower or 'aerial' in equip_lower:
        recommended_campaigns.append('Boom-Lift Campaign (if exists) or DSA')
    elif 'backhoe' in equip_lower:
        recommended_campaigns.append('Backhoe Campaign')
    else:
        recommended_campaigns.append('DSA Campaign (Dynamic catch-all)')

    campaign_recommendations[equip] = {
        'campaigns': recommended_campaigns,
        'gmv': data['total_gmv'],
        'count': data['count']
    }

print("\n📊 CAMPAIGN TARGETING RECOMMENDATIONS:")
print("-" * 180)

for rank, (equip, rec) in enumerate(sorted(campaign_recommendations.items(), key=lambda x: x[1]['gmv'], reverse=True), 1):
    equip_display = equip[:67] + "..." if len(equip) > 70 else equip
    print(f"\n{rank}. {equip_display}")
    print(f"   GMV: ${rec['gmv']:,.2f} | {rec['count']} rentals")
    print(f"   🎯 Target Campaigns: {', '.join(rec['campaigns'])}")

print("\n\n" + "=" * 180)
print("STEP 3: KEYWORD OPTIMIZATION PLAN")
print("=" * 180)

# Generate keyword recommendations for each equipment type
keyword_recommendations = {}

for equip, data in top_10[:10]:
    equip_lower = equip.lower()

    keywords_to_add = []
    negative_keywords = []

    # Parse equipment description to extract key terms
    if 'dozer' in equip_lower or 'bulldozer' in equip_lower:
        # Extract weight class if present
        if '40,000' in equip or '40000' in equip or '40k' in equip_lower:
            keywords_to_add.extend([
                'large dozer rental',
                'heavy dozer rental',
                'd8 dozer rental',
                'd9 dozer rental',
                'cat d8 rental',
                '40000 lb dozer',
                'large bulldozer rental'
            ])
        elif '20,000' in equip or '20000' in equip:
            keywords_to_add.extend([
                'medium dozer rental',
                'd6 dozer rental',
                'd7 dozer rental',
                'cat d6 rental'
            ])

        # General dozer keywords
        keywords_to_add.extend([
            'dozer rental [city]',
            'bulldozer rental [city]',
            'dozer for rent',
            'rent bulldozer',
            'land clearing dozer',
            'site prep dozer',
            'grading dozer rental'
        ])

        negative_keywords.extend([
            '-toy dozer',
            '-model dozer',
            '-blade only',
            '-parts',
            '-for sale'
        ])

    elif 'telehandler' in equip_lower or 'reach forklift' in equip_lower:
        # Extract capacity
        if '5000' in equip or '5k' in equip_lower:
            keywords_to_add.extend([
                '5000 lb telehandler',
                '5k telehandler rental',
                'small telehandler rental'
            ])
        elif '8000' in equip or '10000' in equip:
            keywords_to_add.extend([
                'large telehandler rental',
                '10k telehandler rental'
            ])

        keywords_to_add.extend([
            'telehandler rental [city]',
            'reach forklift rental',
            'lull rental',
            'zoom boom rental',
            'telescopic handler rental',
            'telehandler for rent',
            'rent telehandler'
        ])

        negative_keywords.extend([
            '-forklift attachments',
            '-parts',
            '-training'
        ])

    elif 'forklift' in equip_lower:
        if 'warehouse' in equip_lower or 'indoor' in equip_lower:
            keywords_to_add.extend([
                'warehouse forklift rental',
                'indoor forklift rental',
                'electric forklift rental'
            ])
        elif 'rough terrain' in equip_lower or 'outdoor' in equip_lower:
            keywords_to_add.extend([
                'outdoor forklift rental',
                'rough terrain forklift',
                'construction forklift rental'
            ])

        keywords_to_add.extend([
            'forklift rental [city]',
            'forklift for rent',
            'rent forklift',
            'forklift hire'
        ])

        negative_keywords.extend([
            '-pallet jack',
            '-hand truck',
            '-training',
            '-certification'
        ])

    elif 'loader' in equip_lower:
        if 'wheel' in equip_lower:
            keywords_to_add.extend([
                'wheel loader rental',
                'front end loader rental',
                'payloader rental'
            ])
        elif 'skid' in equip_lower or 'compact' in equip_lower:
            keywords_to_add.extend([
                'skid steer rental',
                'compact loader rental',
                'bobcat rental',
                'skid loader rental'
            ])

        keywords_to_add.extend([
            'loader rental [city]',
            'loader for rent',
            'rent loader'
        ])

        negative_keywords.extend([
            '-bucket only',
            '-attachments only'
        ])

    elif 'scissor' in equip_lower:
        # Extract height if present
        if any(x in equip_lower for x in ['19', '20', '25', '26']):
            keywords_to_add.extend([
                'tall scissor lift rental',
                '20 ft scissor lift',
                '25 ft scissor lift'
            ])

        if 'rough terrain' in equip_lower:
            keywords_to_add.append('rough terrain scissor lift')
        elif 'electric' in equip_lower:
            keywords_to_add.append('electric scissor lift rental')

        keywords_to_add.extend([
            'scissor lift rental [city]',
            'scissor lift for rent',
            'rent scissor lift'
        ])

        negative_keywords.extend([
            '-boom lift',
            '-aerial lift'
        ])

    elif 'excavator' in equip_lower:
        if 'mini' in equip_lower or 'compact' in equip_lower:
            keywords_to_add.extend([
                'mini excavator rental',
                'compact excavator rental',
                'small excavator rental'
            ])

        keywords_to_add.extend([
            'excavator rental [city]',
            'excavator for rent',
            'rent excavator'
        ])

    elif 'backhoe' in equip_lower:
        keywords_to_add.extend([
            'backhoe rental [city]',
            'backhoe loader rental',
            'backhoe for rent',
            'rent backhoe'
        ])

    # Universal negative keywords
    negative_keywords.extend([
        '-canada',
        '-jobs',
        '-hiring',
        '-for sale',
        '-buy'
    ])

    keyword_recommendations[equip] = {
        'add': list(set(keywords_to_add)),  # Remove duplicates
        'negative': list(set(negative_keywords))
    }

print("\n📝 KEYWORD RECOMMENDATIONS BY EQUIPMENT TYPE:")
print("-" * 180)

for rank, (equip, keywords) in enumerate(keyword_recommendations.items(), 1):
    equip_display = equip[:67] + "..." if len(equip) > 70 else equip
    print(f"\n{rank}. {equip_display}")

    if keywords['add']:
        print(f"\n   ✅ KEYWORDS TO ADD ({len(keywords['add'])}):")
        for kw in sorted(keywords['add'])[:15]:  # Show top 15
            print(f"      • {kw}")

    if keywords['negative']:
        print(f"\n   ❌ NEGATIVE KEYWORDS TO ADD ({len(keywords['negative'])}):")
        for neg in sorted(set(keywords['negative']))[:10]:  # Show top 10
            print(f"      • {neg}")

print("\n\n" + "=" * 180)
print("STEP 4: ACTION PLAN")
print("=" * 180)

print("""
┌────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: IMMEDIATE ACTIONS (WEEK 1)                                        │
└────────────────────────────────────────────────────────────────────────────┘

🎯 PRIORITY 1: OPTIMIZE HIGH-GMV EQUIPMENT CAMPAIGNS

Based on the top 10 equipment types identified, focus on these campaigns:

1. DOZERS CAMPAIGN (if Dozers are in top 10)
   ☐ Add 15-20 new keywords from recommendations above
   ☐ Add weight-class specific keywords (D6, D8, D9, large/medium)
   ☐ Add location modifiers for top states (TX, CA, etc.)
   ☐ Add 10+ negative keywords
   ☐ Split ad groups by:
      • Heavy dozers (40k+ lbs)
      • Medium dozers (20-40k lbs)
      • Location-based targeting

2. TELEHANDLER CAMPAIGN (if Telehandlers are in top 10)
   ☐ Add "reach forklift", "lull", "zoom boom" variants
   ☐ Add capacity-based keywords (5k lb, 10k lb)
   ☐ Add height-based targeting (15-19 ft, 20+ ft)
   ☐ Expand location targeting

3. FORKLIFT CAMPAIGN (if Forklifts are in top 10)
   ☐ Split warehouse vs outdoor/rough terrain
   ☐ Add 12+ keyword variants
   ☐ Add capacity modifiers (small, large)
   ☐ Expand location targeting

4. LOADER CAMPAIGN (if Loaders are in top 10)
   ☐ Separate wheel loaders from skid steers
   ☐ Add "bobcat rental" for skid steers
   ☐ Add "payloader" and "front end loader" variants
   ☐ Add location modifiers

5. SCISSOR-LIFT CAMPAIGN (if Scissor Lifts are in top 10)
   ☐ Add height-specific keywords (20 ft, 25 ft, etc.)
   ☐ Separate rough terrain from electric
   ☐ Add location variants

☐ ADD UNIVERSAL NEGATIVE KEYWORDS (ALL CAMPAIGNS):
   • -canada, -canadian, -jobs, -hiring, -career
   • -parts, -for sale, -buy, -used
   • -training, -certification, -operator
   • -toy, -model, -miniature

┌────────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: AD COPY & TARGETING (WEEKS 2-3)                                  │
└────────────────────────────────────────────────────────────────────────────┘

6. CREATE EQUIPMENT-SPECIFIC AD COPY
   ☐ Write ads highlighting specific equipment in top 10
   ☐ Include capacity/size in headlines (e.g., "5000 lb Telehandler")
   ☐ Add pricing/availability CTAs
   ☐ Use location-specific copy for top regions

7. LOCATION TARGETING OPTIMIZATION
   ☐ Analyze top locations from Step 1
   ☐ Increase bids +20% for high-performing locations
   ☐ Add location extensions
   ☐ Create location-specific ad groups for top markets

8. RESTRUCTURE AD GROUPS BY EQUIPMENT TYPE
   ☐ Create specific ad groups for each top 10 equipment type
   ☐ Match ad copy to equipment specifications
   ☐ Use more specific landing pages if available

┌────────────────────────────────────────────────────────────────────────────┐
│ PHASE 3: ADVANCED OPTIMIZATION (WEEKS 3-4)                                │
└────────────────────────────────────────────────────────────────────────────┘

9. BIDDING STRATEGY ADJUSTMENTS
   ☐ For campaigns with 30+ conversions, switch to tROAS
   ☐ Set target ROAS based on equipment GMV margins
   ☐ Adjust bids based on equipment profitability

10. SEARCH TERM MINING
    ☐ Review search terms weekly for equipment-specific queries
    ☐ Add high-performing searches as exact/phrase match
    ☐ Identify new equipment types customers are searching for
    ☐ Add 5-10 new negative keywords weekly

11. PERFORMANCE MONITORING
    ☐ Track GMV by equipment type
    ☐ Compare to Metabase data weekly
    ☐ Adjust bids for high-GMV equipment types
    ☐ Pause ad groups for low-GMV equipment

┌────────────────────────────────────────────────────────────────────────────┐
│ SUCCESS METRICS                                                            │
└────────────────────────────────────────────────────────────────────────────┘

📊 Track Weekly:
   • GMV for each top 10 equipment type
   • Number of rentals for each type
   • Average deal size by equipment
   • ROAS by equipment category
   • Cost per conversion by equipment type

🎯 30-Day Goals:
   • Increase rentals for top 10 equipment by 25%
   • Improve overall ROAS from 2.83x to 3.5x+
   • Reduce cost per deal by 15%
   • Increase GMV by $25,000+ (to $135k+)

📈 Expected Impact:
   • Keyword expansion: +20% traffic for high-GMV equipment
   • Negative keywords: -15% wasted spend
   • Ad group restructure: +10% conversion rate
   • Location optimization: +15% efficiency

   Total Expected GMV Increase: +$25,000-$30,000/month

""")

print("=" * 180)
print("✅ COMPLETE 4-STEP OPTIMIZATION PLAN GENERATED")
print("=" * 180)
print("\n📄 Summary:")
print(f"   • Top 10 equipment types identified from Metabase")
print(f"   • Campaign targeting mapped to high-GMV equipment")
print(f"   • {sum(len(k['add']) for k in keyword_recommendations.values())} keywords to add")
print(f"   • {sum(len(k['negative']) for k in keyword_recommendations.values())} negative keywords to add")
print(f"   • 3-phase action plan with specific tasks")
print("\n⏱️  Implementation Timeline: 3-4 weeks")
print("💰 Expected Monthly GMV Increase: $25,000-$30,000")
print("\n" + "=" * 180)
