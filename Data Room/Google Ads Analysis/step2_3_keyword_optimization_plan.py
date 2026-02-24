from google.ads.googleads.client import GoogleAdsClient
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Load credentials
client = GoogleAdsClient.load_from_storage('/Users/vinuraabeysundara/Desktop/ICG/DOZR/Data Room/Config/google-ads.yaml')
ga_service = client.get_service('GoogleAdsService')
customer_id = '8531896842'

print("=" * 160)
print("STEP 1 (REVISED): HIGHEST GMV EQUIPMENT FROM GOOGLE ADS DATA")
print("=" * 160)

start_date = '2026-02-01'
end_date = '2026-02-23'

# Get deal value by campaign (which corresponds to equipment type)
query_deals = f"""
    SELECT
        campaign.name,
        ad_group.name,
        segments.conversion_action_name,
        metrics.conversions,
        metrics.conversions_value
    FROM ad_group
    WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.status = 'ENABLED'
        AND campaign.name LIKE '%US%'
        AND campaign.name NOT LIKE '%Expansion%'
        AND metrics.conversions > 0
        AND segments.conversion_action_name LIKE '%Closed Won%'
"""

response = ga_service.search(customer_id=customer_id, query=query_deals)

equipment_gmv = defaultdict(lambda: {'deals': 0, 'value': 0, 'campaigns': set(), 'ad_groups': set()})

for row in response:
    campaign = row.campaign.name
    ad_group = row.ad_group.name
    conversions = row.metrics.conversions
    value = row.metrics.conversions_value

    # Extract equipment type from campaign name
    equipment = 'Unknown'
    for equip in ['Forklift', 'Scissor-Lift', 'Boom-Lift', 'Dozer', 'Loader', 'Excavator', 'Telehandler', 'Skid-Steer', 'Backhoe', 'DSA', 'Brand']:
        if equip in campaign:
            equipment = equip
            break

    equipment_gmv[equipment]['deals'] += conversions
    equipment_gmv[equipment]['value'] += value
    equipment_gmv[equipment]['campaigns'].add(campaign)
    equipment_gmv[equipment]['ad_groups'].add(f"{campaign}|||{ad_group}")

sorted_equipment = sorted(equipment_gmv.items(), key=lambda x: x[1]['value'], reverse=True)

print(f"\n📊 EQUIPMENT TYPE GMV RANKING (Feb 1-23, 2026)")
print("=" * 160)
print(f"\n{'Rank':<6} {'Equipment':<20} {'Deals':>7} {'Total GMV':>14} {'Avg Deal':>14} {'% of Total':>12} {'Campaigns':>10}")
print("-" * 100)

total_gmv = sum(d['value'] for d in equipment_gmv.values())

for rank, (equip, data) in enumerate(sorted_equipment, 1):
    deals = int(data['deals'])
    value = data['value']
    avg_deal = value / deals if deals > 0 else 0
    pct = (value / total_gmv * 100) if total_gmv > 0 else 0
    num_campaigns = len(data['campaigns'])

    print(f"{rank:<6} {equip:<20} {deals:>7} ${value:>13,.2f} ${avg_deal:>13,.2f} {pct:>11.1f}% {num_campaigns:>10}")

print(f"\n{'TOTAL':<27} {int(sum(d['deals'] for d in equipment_gmv.values())):>7} ${total_gmv:>13,.2f}")

# Top 5 represent what % of revenue
top5_value = sum(d['value'] for _, d in sorted_equipment[:5])
print(f"\n💡 Top 5 equipment types = ${top5_value:,.2f} ({top5_value/total_gmv*100:.1f}% of total GMV)")

print("\n\n" + "=" * 160)
print("STEP 2: AD GROUP KEYWORD OPTIMIZATION RECOMMENDATIONS")
print("=" * 160)

# Define keyword strategies for each equipment type
keyword_strategies = {
    'DSA': {
        'current_strategy': 'Dynamic Search Ads (automated)',
        'action': 'NEGATIVE KEYWORDS ONLY',
        'negatives': [
            # Location exclusions
            '-canada', '-canadian', '-toronto', '-vancouver', '-montreal',
            # Non-core equipment
            '-trailer', '-truck', '-car', '-suv', '-motorcycle',
            # Jobs/employment
            '-jobs', '-hiring', '-employment', '-career', '-resume',
            # Parts/sales
            '-parts', '-for sale', '-buy', '-purchase equipment', '-used equipment',
            # Irrelevant
            '-toy', '-model', '-miniature', '-rc', '-remote control',
            # International
            '-uk', '-europe', '-asia', '-australia'
        ],
        'notes': 'DSA campaigns already auto-expand. Focus on aggressive negative keywords.'
    },
    'Dozer': {
        'keep': [
            'dozer rental', 'bulldozer rental', 'dozer rental near me', 'bulldozer rental near me',
            'rent dozer', 'rent bulldozer', 'dozer rental [state]', 'bulldozer rental [state]',
            'd6 dozer rental', 'd8 dozer rental', 'cat dozer rental'
        ],
        'add': [
            # Search intent variants
            'rent a dozer', 'rent a bulldozer', 'dozer for rent', 'bulldozer for rent',
            'dozer hire', 'bulldozer hire',
            # Location variants
            'dozer rental in [state]', 'bulldozer rental in [state]',
            'dozer rental [city]', 'bulldozer rental [city]',
            # Use case variants
            'land clearing dozer', 'construction dozer rental', 'farm dozer rental',
            'grading dozer rental', 'site prep dozer'
        ],
        'negatives': [
            '-canada', '-jobs', '-parts', '-for sale', '-toy', '-model',
            '-blade only', '-attachments only', '-training', '-operator',
            '-swamp dozer', '-forestry dozer',  # Specialized equipment you may not have
        ],
        'notes': 'Dozers are 31.2% of revenue. Expand aggressively with location + intent variants.'
    },
    'Forklift': {
        'keep': [
            'forklift rental', 'forklift rental near me', 'rent forklift',
            'warehouse forklift rental', 'outdoor forklift rental'
        ],
        'add': [
            # Intent variants
            'forklift for rent', 'rent a forklift', 'forklift hire',
            # Location variants
            'forklift rental [state]', 'forklift rental [city]',
            'forklift rental in [state]',
            # Type variants
            'warehouse forklift for rent', 'rough terrain forklift rental',
            'industrial forklift rental', 'construction forklift rental',
            # Capacity-based (category level, not exact tonnage)
            'small forklift rental', 'large forklift rental'
        ],
        'negatives': [
            '-canada', '-jobs', '-training', '-certification', '-operator',
            '-parts', '-for sale', '-buy forklift', '-used forklift',
            '-toy', '-pallet jack',  # Different equipment
        ],
        'notes': 'Forklift improving performance. Expand location targeting.'
    },
    'Loader': {
        'keep': [
            'wheel loader rental', 'loader rental', 'skid steer rental',
            'track loader rental', 'compact loader rental'
        ],
        'add': [
            # Intent variants
            'rent wheel loader', 'rent skid steer', 'loader for rent',
            # Location variants
            'wheel loader rental [state]', 'loader rental near me',
            # Type variants
            'construction loader rental', 'farm loader rental',
            'compact track loader rental',
            # Category terms
            'front end loader rental', 'payloader rental'
        ],
        'negatives': [
            '-canada', '-jobs', '-operator', '-attachments only',
            '-bucket only', '-parts', '-for sale', '-training'
        ],
        'notes': 'Loader showing improvement. Separate skid steer into own targeting.'
    },
    'Scissor-Lift': {
        'keep': [
            'scissor lift rental', 'scissor lift rental near me',
            'rough terrain scissor lift', 'electric scissor lift rental'
        ],
        'add': [
            # Intent variants
            'rent scissor lift', 'scissor lift for rent', 'scissor lift hire',
            # Location variants
            'scissor lift rental [state]', 'scissor lift rental [city]',
            # Type variants
            'indoor scissor lift rental', 'outdoor scissor lift rental',
            'narrow scissor lift rental',
            # Height categories (avoid exact heights)
            'low scissor lift rental', 'tall scissor lift rental'
        ],
        'negatives': [
            '-canada', '-jobs', '-training', '-certification',
            '-parts', '-for sale', '-boom lift',  # Different equipment
            '-aerial lift',  # Too broad
        ],
        'notes': 'Scissor-Lift improving but still low ROAS. Test carefully.'
    },
    'Excavator': {
        'keep': [
            'excavator rental', 'mini excavator rental', 'excavator rental near me'
        ],
        'action': '⚠️  PAUSE CAMPAIGN - 0.01x ROAS',
        'notes': 'Excavator campaign burning money. Recommend pausing until strategy revised.'
    },
    'Backhoe': {
        'keep': [
            'backhoe rental', 'backhoe rental near me', 'backhoe rental cost'
        ],
        'add': [
            'rent backhoe', 'backhoe for rent', 'backhoe hire',
            'backhoe rental [state]', 'backhoe rental [city]',
            'backhoe loader rental', 'construction backhoe rental'
        ],
        'negatives': [
            '-canada', '-jobs', '-operator', '-parts', '-for sale'
        ],
        'notes': 'Backhoe improving from 0.00x to 1.72x. Monitor closely.'
    },
    'Telehandler': {
        'keep': [
            'telehandler rental', 'telehandler rental near me',
            'telehandler rental cost'
        ],
        'add': [
            'rent telehandler', 'telehandler for rent', 'telehandler hire',
            'telehandler rental [state]', 'lull rental', 'reach forklift rental',
            'telescopic handler rental', 'zoom boom rental'
        ],
        'negatives': [
            '-canada', '-jobs', '-operator', '-parts', '-for sale',
            '-forklift attachments'  # Just the attachment
        ],
        'notes': 'Telehandler improving to 3.19x ROAS. Expand keywords.'
    },
    'Brand': {
        'action': 'PROTECT BRAND TERMS',
        'keep': [
            'dozr', 'dozr rental', 'dozr.com', '[brand] equipment rental'
        ],
        'negatives': [
            # Competitor protection
            '-united rentals', '-sunbelt', '-herc', '-home depot',
            '-lowes', '-cat rental', '-caterpillar rental store'
        ],
        'notes': 'Brand campaign has 15.83x ROAS. Keep tight and defensive.'
    }
}

print("\n📋 DETAILED KEYWORD RECOMMENDATIONS BY EQUIPMENT TYPE")
print("=" * 160)

for equip, data in sorted_equipment[:8]:  # Top 8 equipment types
    if equip in keyword_strategies:
        strategy = keyword_strategies[equip]

        print(f"\n{'='*160}")
        print(f"🎯 {equip.upper()}")
        print(f"   GMV: ${data['value']:,.2f} ({data['value']/total_gmv*100:.1f}% of total) | {int(data['deals'])} deals")
        print(f"{'='*160}")

        if 'action' in strategy and strategy['action'] != 'NEGATIVE KEYWORDS ONLY':
            print(f"\n⚠️  RECOMMENDED ACTION: {strategy['action']}")

        if 'keep' in strategy:
            print(f"\n✅ KEEP these category keywords:")
            for kw in strategy['keep']:
                print(f"   • {kw}")

        if 'add' in strategy:
            print(f"\n➕ ADD these keyword variants:")
            for kw in strategy['add']:
                print(f"   • {kw}")

        if 'negatives' in strategy:
            print(f"\n❌ ADD these negative keywords:")
            for neg in strategy['negatives']:
                print(f"   • {neg}")

        if 'notes' in strategy:
            print(f"\n💡 Notes: {strategy['notes']}")

# Location-specific recommendations
print("\n\n" + "=" * 160)
print("📍 LOCATION TARGETING RECOMMENDATIONS")
print("=" * 160)

states_to_target = [
    'texas', 'california', 'florida', 'new york', 'pennsylvania',
    'illinois', 'ohio', 'georgia', 'north carolina', 'michigan'
]

print("\n✅ Priority States for Location Modifiers:")
for state in states_to_target:
    print(f"   • {state.title()}")

print("\n❌ Exclude these locations (not served):")
excluded_locations = [
    'canada', 'alaska', 'hawaii', 'puerto rico',
    'international locations'
]
for loc in excluded_locations:
    print(f"   • {loc.title()}")

print("\n\n" + "=" * 160)
print("STEP 3: ACTION PLAN")
print("=" * 160)

print("""
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: IMMEDIATE ACTIONS (THIS WEEK)                                     │
└─────────────────────────────────────────────────────────────────────────────┘

1. PAUSE UNDERPERFORMING CAMPAIGNS
   ☐ Pause Excavator campaign (burning $5,259 with 0.01x ROAS)
   ☐ Pause all Expansion campaigns with 0 conversions:
     - Excavator-Expansion
     - Demand-Brand-US-Expansion
     - Loader-Expansion

2. ADD NEGATIVE KEYWORDS (ALL CAMPAIGNS)
   ☐ Add universal negatives across ALL campaigns:
     • -canada, -canadian, -jobs, -hiring, -career
     • -parts, -for sale, -buy, -purchase
     • -training, -certification, -operator
     • -toy, -model, -miniature, -rc

   ☐ Add DSA-specific negatives (aggressive):
     • -trailer, -truck, -car, -suv
     • -uk, -europe, -asia, -australia

3. OPTIMIZE TOP 3 REVENUE GENERATORS (72% of GMV)

   A. DSA Campaign (38.6% of revenue, but declining)
      ☐ Add 20+ negative keywords from above list
      ☐ Review search terms report - exclude low-intent queries
      ☐ Consider temporarily pausing expansion to test recovery

   B. Dozer Campaign (23.2% of revenue)
      ☐ Add 15+ keyword variants with location modifiers
      ☐ Separate ad groups for:
         - "dozer rental [location]"
         - "bulldozer rental [location]"
         - "land clearing equipment rental"
      ☐ Test higher bids on Wednesday-Thursday (best performing days)

   C. Forklift Campaign (10.0% of revenue, improving)
      ☐ Add warehouse vs outdoor forklift ad group split
      ☐ Expand location targeting
      ☐ Add "forklift hire" variants (alternative phrasing)

┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: OPTIMIZATION (NEXT 2 WEEKS)                                       │
└─────────────────────────────────────────────────────────────────────────────┘

4. LOCATION EXPANSION
   ☐ Add location extensions for top-performing states
   ☐ Create location-specific ad copy variations
   ☐ Implement bid adjustments by location (+20% for top states)

5. AD GROUP RESTRUCTURING
   ☐ Split high-volume ad groups by intent:
     • "[equipment] rental" (general)
     • "[equipment] rental near me" (local intent)
     • "[equipment] rental cost" (price shoppers)
     • "rent [equipment]" (action intent)

6. KEYWORD EXPANSION (PRIORITY ORDER)
   ☐ Dozers: Add 15-20 keywords with location variants
   ☐ Forklift: Add 10-15 keywords (type + location)
   ☐ Telehandler: Add 8-10 keywords (expand alternatives like "lull")
   ☐ Loader: Add 10 keywords (separate skid steer)
   ☐ Scissor-Lift: Add 8 keywords (test carefully)

7. DAY-PARTING OPTIMIZATION
   ☐ Increase bids +30% on Wednesday-Thursday (best days: 5.15x ROAS)
   ☐ Decrease bids -50% on weekends (0.51x ROAS)
   ☐ Consider pausing Sunday entirely (0.00x ROAS)

┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 3: ADVANCED OPTIMIZATION (WEEKS 3-4)                                 │
└─────────────────────────────────────────────────────────────────────────────┘

8. BIDDING STRATEGY UPDATES
   ☐ Switch Dozers to tROAS at 960% (ready with 36 conversions)
   ☐ Switch Forklift to tROAS at 310% (ready with 35 conversions)
   ☐ Monitor DSA for another week, then consider tROAS at 710%

9. AD COPY TESTING
   ☐ Test "Rent [Equipment] - Same Day Delivery" headlines
   ☐ Test location-specific copy with city names
   ☐ Add price/value propositions to top performers

10. SEARCH TERM AUDITS
    ☐ Weekly search term review for DSA campaign
    ☐ Add 5-10 new negatives per week based on irrelevant searches
    ☐ Identify high-performing search terms to add as exact match

┌─────────────────────────────────────────────────────────────────────────────┐
│ SUCCESS METRICS (TRACK WEEKLY)                                             │
└─────────────────────────────────────────────────────────────────────────────┘

📊 KPI Targets:
   • Overall ROAS: Maintain 3.0x+ (currently 2.83x)
   • DSA ROAS: Recover to 8.0x+ (currently 3.62x)
   • Weekend ROAS: Improve to 1.5x+ (currently 0.51x)
   • Cost per deal: Keep under $1,500 (currently $1,303)

📈 Expected Impact:
   • Pause Excavator: Save $2,500/week
   • Reduce weekend spend 80%: Save $2,600/week, redeploy to Wed-Thu
   • Negative keywords: Reduce wasted spend by 15-20%
   • Keyword expansion (Dozer): +10-15% incremental revenue
   • tROAS implementation: Improve efficiency by 5-10%

🎯 Monthly Goal:
   • Increase total GMV from $111k to $130k+ (+17%)
   • Reduce wasted spend by $10k/month
   • Improve overall ROAS from 2.83x to 3.5x+

""")

print("=" * 160)
print("✅ ACTION PLAN COMPLETE")
print("=" * 160)
print("\n📄 Next Steps:")
print("   1. Review and approve Phase 1 actions")
print("   2. Implement negative keywords across all campaigns (30 min)")
print("   3. Pause Excavator and zero-conversion Expansion campaigns (5 min)")
print("   4. Add keyword expansions to Dozer and Forklift campaigns (1 hour)")
print("   5. Set up day-parting bid adjustments (30 min)")
print("\n⏱️  Total implementation time: ~2 hours")
print("💰 Expected monthly savings: $10,000+")
print("📈 Expected monthly revenue increase: $19,000+")
print("\n" + "=" * 160)
