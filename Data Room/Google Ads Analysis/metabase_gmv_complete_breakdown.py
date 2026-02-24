import urllib.request
import json
from datetime import datetime
from collections import defaultdict
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

print("=" * 160)
print("🎯 COMPREHENSIVE DEALS & GMV BREAKDOWN - FEBRUARY 2026")
print("Period: February 1-23, 2026")
print("=" * 160)

# Pull Google Ads deal data first
print("\n\n📊 PART 1: GOOGLE ADS DEALS DATA")
print("=" * 160)

client = GoogleAdsClient.load_from_storage('/Users/vinuraabeysundara/Desktop/ICG/DOZR/Data Room/Config/google-ads.yaml')
ga_service = client.get_service('GoogleAdsService')
customer_id = '8531896842'

start_date = '2026-02-01'
end_date = '2026-02-23'

# Query for all deals
query_deals = f"""
    SELECT
        campaign.name,
        ad_group.name,
        segments.date,
        segments.conversion_action_name,
        metrics.conversions,
        metrics.conversions_value
    FROM ad_group
    WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.status = 'ENABLED'
        AND ad_group.status = 'ENABLED'
        AND campaign.name LIKE '%US%'
        AND metrics.conversions > 0
        AND segments.conversion_action_name LIKE '%Closed Won%'
"""

response = ga_service.search(customer_id=customer_id, query=query_deals)

google_ads_deals = []
google_ads_daily = defaultdict(lambda: {'deals': 0, 'value': 0})
google_ads_by_equipment = defaultdict(lambda: {'deals': 0, 'value': 0})

for row in response:
    campaign = row.campaign.name
    ad_group = row.ad_group.name
    date = row.segments.date
    conversions = row.metrics.conversions
    value = row.metrics.conversions_value

    # Extract equipment type from campaign name
    equipment = 'Unknown'
    for equip_type in ['Forklift', 'Scissor-Lift', 'Boom-Lift', 'Dozer', 'Loader', 'Excavator', 'Telehandler', 'Skid-Steer', 'Backhoe', 'DSA', 'Brand']:
        if equip_type in campaign:
            equipment = equip_type
            break

    google_ads_deals.append({
        'date': date,
        'campaign': campaign,
        'ad_group': ad_group,
        'equipment': equipment,
        'deals': int(conversions),
        'value': value
    })

    google_ads_daily[date]['deals'] += conversions
    google_ads_daily[date]['value'] += value

    google_ads_by_equipment[equipment]['deals'] += conversions
    google_ads_by_equipment[equipment]['value'] += value

total_ga_deals = sum(d['deals'] for d in google_ads_deals)
total_ga_value = sum(d['value'] for d in google_ads_deals)

print(f"\n✅ Google Ads: {len(google_ads_deals)} deal records ({int(total_ga_deals)} total deals)")
print(f"   • Total Deal Value: ${total_ga_value:,.2f}")
print(f"   • Average Deal Value: ${total_ga_value / total_ga_deals if total_ga_deals > 0 else 0:,.2f}")

# Pull Metabase data
print("\n\n📊 PART 2: METABASE DATA")
print("=" * 160)

# Query invoices for GMV
query_invoices = {
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
                "$project": {
                    "_id": 1,
                    "createdDate": 1,
                    "total": 1,
                    "status": 1
                }
            }
        ]),
        "collection": "invoicesv2"
    }
}

print("\n🔍 Querying invoices for GMV...")
invoices_result = run_metabase_query(query_invoices)

if invoices_result and invoices_result.get('status') == 'completed':
    rows = invoices_result.get('data', {}).get('rows', [])
    cols = invoices_result.get('data', {}).get('cols', [])

    print(f"✅ Found {len(rows)} invoices in February")

    invoices_daily = defaultdict(lambda: {'count': 0, 'total': 0})
    total_invoice_value = 0

    for row in rows:
        invoice_data = {}
        for i, col in enumerate(cols):
            if i < len(row):
                field_name = col.get('name', col.get('display_name', f'field_{i}'))
                invoice_data[field_name] = row[i]

        created_date = invoice_data.get('createdDate', '')
        if created_date:
            date_str = str(created_date)[:10]
            total = float(invoice_data.get('total', 0)) if invoice_data.get('total') else 0

            invoices_daily[date_str]['count'] += 1
            invoices_daily[date_str]['total'] += total
            total_invoice_value += total

    print(f"   • Total Invoice Value: ${total_invoice_value:,.2f}")
    print(f"   • Average Invoice Value: ${total_invoice_value / len(rows) if len(rows) > 0 else 0:,.2f}")

# Query calls
query_calls = {
    "database": 2,
    "type": "native",
    "native": {
        "query": json.dumps([
            {
                "$match": {
                    "callTime": {
                        "$gte": {"$date": "2026-02-01T00:00:00.000Z"},
                        "$lte": {"$date": "2026-02-23T23:59:59.999Z"}
                    }
                }
            }
        ]),
        "collection": "calls"
    }
}

print("\n🔍 Querying calls...")
calls_result = run_metabase_query(query_calls)

calls_daily = defaultdict(int)
if calls_result and calls_result.get('status') == 'completed':
    rows = calls_result.get('data', {}).get('rows', [])
    cols = calls_result.get('data', {}).get('cols', [])

    for row in rows:
        call_data = {}
        for i, col in enumerate(cols):
            if i < len(row):
                field_name = col.get('name', col.get('display_name', f'field_{i}'))
                call_data[field_name] = row[i]

        call_time = call_data.get('callTime', '')
        if call_time:
            date_str = str(call_time)[:10]
            calls_daily[date_str] += 1

    print(f"✅ Found {len(rows)} calls in February")

# Combined daily report
print("\n\n📅 DAILY PERFORMANCE BREAKDOWN")
print("=" * 160)
print(f"\n{'Date':<15} {'Calls':>8} {'Deals':>8} {'Invoice GMV':>14} {'Deal Value':>14} {'Avg Deal':>14} {'Conv%':>8}")
print("-" * 120)

all_dates = sorted(set(list(google_ads_daily.keys()) + list(invoices_daily.keys()) + list(calls_daily.keys())))

total_calls = 0
total_deals = 0
total_invoice_gmv = 0
total_deal_value = 0

for date in all_dates:
    calls = calls_daily.get(date, 0)
    deals = int(google_ads_daily.get(date, {}).get('deals', 0))
    invoice_gmv = invoices_daily.get(date, {}).get('total', 0)
    deal_value = google_ads_daily.get(date, {}).get('value', 0)
    avg_deal = deal_value / deals if deals > 0 else 0
    conv_pct = (deals / calls * 100) if calls > 0 else 0

    print(f"{date:<15} {calls:>8} {deals:>8} ${invoice_gmv:>13,.2f} ${deal_value:>13,.2f} ${avg_deal:>13,.2f} {conv_pct:>7.1f}%")

    total_calls += calls
    total_deals += deals
    total_invoice_gmv += invoice_gmv
    total_deal_value += deal_value

print("-" * 120)
avg_deal_overall = total_deal_value / total_deals if total_deals > 0 else 0
conv_overall = (total_deals / total_calls * 100) if total_calls > 0 else 0
print(f"{'TOTAL':<15} {total_calls:>8} {total_deals:>8} ${total_invoice_gmv:>13,.2f} ${total_deal_value:>13,.2f} ${avg_deal_overall:>13,.2f} {conv_overall:>7.1f}%")

# Equipment breakdown
print("\n\n🚜 EQUIPMENT TYPE BREAKDOWN (FROM GOOGLE ADS)")
print("=" * 160)
print(f"\n{'Equipment':<30} {'Deals':>8} {'Deal Value':>14} {'Avg Deal':>14} {'% of Total':>12}")
print("-" * 100)

sorted_equipment = sorted(google_ads_by_equipment.items(), key=lambda x: x[1]['value'], reverse=True)

for equipment, data in sorted_equipment:
    avg_deal = data['value'] / data['deals'] if data['deals'] > 0 else 0
    pct = (data['value'] / total_ga_value * 100) if total_ga_value > 0 else 0

    print(f"{equipment:<30} {int(data['deals']):>8} ${data['value']:>13,.2f} ${avg_deal:>13,.2f} {pct:>11.1f}%")

# Summary
print("\n\n📊 SUMMARY STATISTICS")
print("=" * 160)

print(f"\n💰 Financial Performance:")
print(f"   • Total Calls: {total_calls:,}")
print(f"   • Total Deals (Google Ads): {int(total_deals)}")
print(f"   • Total Deal Value (Google Ads): ${total_deal_value:,.2f}")
print(f"   • Total Invoice GMV (Metabase): ${total_invoice_gmv:,.2f}")
print(f"   • Average Deal Value: ${avg_deal_overall:,.2f}")
print(f"   • Call → Deal Conversion: {conv_overall:.1f}%")

print(f"\n📅 Daily Averages:")
print(f"   • Avg Calls/Day: {total_calls / len(all_dates):.1f}")
print(f"   • Avg Deals/Day: {total_deals / len(all_dates):.1f}")
print(f"   • Avg Daily GMV (Invoices): ${total_invoice_gmv / len(all_dates):,.2f}")
print(f"   • Avg Daily Deal Value: ${total_deal_value / len(all_dates):,.2f}")

print(f"\n🎯 Top Performers:")
if sorted_equipment:
    print(f"   • #1 Equipment by Value: {sorted_equipment[0][0]} (${sorted_equipment[0][1]['value']:,.2f})")
    print(f"   • #1 Equipment by Volume: {sorted(google_ads_by_equipment.items(), key=lambda x: x[1]['deals'], reverse=True)[0][0]} ({int(sorted(google_ads_by_equipment.items(), key=lambda x: x[1]['deals'], reverse=True)[0][1]['deals'])} deals)")

# Best and worst days
best_day = max(google_ads_daily.items(), key=lambda x: x[1]['value'])
worst_day = min([d for d in google_ads_daily.items() if d[1]['deals'] > 0], key=lambda x: x[1]['value'])

print(f"\n📈 Best & Worst Days:")
print(f"   • Best Day: {best_day[0]} (${best_day[1]['value']:,.2f}, {int(best_day[1]['deals'])} deals)")
print(f"   • Worst Day: {worst_day[0]} (${worst_day[1]['value']:,.2f}, {int(worst_day[1]['deals'])} deals)")

print("\n\n" + "=" * 160)
print("✅ COMPREHENSIVE BREAKDOWN COMPLETE")
print("=" * 160)
