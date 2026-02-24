from google.ads.googleads.client import GoogleAdsClient
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Load credentials
client = GoogleAdsClient.load_from_storage('/Users/vinuraabeysundara/Desktop/ICG/DOZR/Data Room/Config/google-ads.yaml')
ga_service = client.get_service('GoogleAdsService')
customer_id = '8531896842'

# Get Saturday and Sunday dates
today = datetime.now()
days_since_sunday = (today.weekday() + 1) % 7
if days_since_sunday == 0:
    sunday_date = today
    saturday_date = today - timedelta(days=1)
else:
    sunday_date = today - timedelta(days=days_since_sunday)
    saturday_date = sunday_date - timedelta(days=1)

saturday_str = saturday_date.strftime('%Y-%m-%d')
sunday_str = sunday_date.strftime('%Y-%m-%d')

print("=" * 100)
print(f"💰 WEEKEND ROAS ANALYSIS - February 21-22, 2026")
print("=" * 100)

# Query for conversion values
query = f"""
    SELECT
        segments.date,
        metrics.cost_micros,
        metrics.conversions,
        metrics.conversions_value,
        metrics.all_conversions_value
    FROM campaign
    WHERE segments.date BETWEEN '{saturday_str}' AND '{sunday_str}'
        AND campaign.status = 'ENABLED'
"""

response = ga_service.search(customer_id=customer_id, query=query)

totals = {
    saturday_str: {'spend': 0, 'conversions': 0, 'conv_value': 0, 'all_conv_value': 0},
    sunday_str: {'spend': 0, 'conversions': 0, 'conv_value': 0, 'all_conv_value': 0}
}

for row in response:
    date = row.segments.date
    totals[date]['spend'] += row.metrics.cost_micros / 1_000_000
    totals[date]['conversions'] += row.metrics.conversions
    totals[date]['conv_value'] += row.metrics.conversions_value
    totals[date]['all_conv_value'] += row.metrics.all_conversions_value

sat = totals[saturday_str]
sun = totals[sunday_str]

# Calculate ROAS
sat_roas = (sat['conv_value'] / sat['spend']) if sat['spend'] > 0 else 0
sun_roas = (sun['conv_value'] / sun['spend']) if sun['spend'] > 0 else 0

weekend_spend = sat['spend'] + sun['spend']
weekend_value = sat['conv_value'] + sun['conv_value']
weekend_roas = (weekend_value / weekend_spend) if weekend_spend > 0 else 0

print(f"\n{'Metric':<30} {'Saturday':>20} {'Sunday':>20} {'Weekend Total':>20}")
print("-" * 100)
print(f"{'💰 Ad Spend':<30} ${sat['spend']:>19.2f} ${sun['spend']:>19.2f} ${weekend_spend:>19.2f}")
print(f"{'📞 Conversions':<30} {int(sat['conversions']):>20} {int(sun['conversions']):>20} {int(sat['conversions'] + sun['conversions']):>20}")
print(f"{'💵 Conversion Value':<30} ${sat['conv_value']:>19.2f} ${sun['conv_value']:>19.2f} ${weekend_value:>19.2f}")
print(f"{'📊 ROAS':<30} {sat_roas:>19.2f}x {sun_roas:>19.2f}x {weekend_roas:>19.2f}x")

print("\n" + "=" * 100)
print("💡 ROAS INTERPRETATION")
print("=" * 100)

if weekend_value > 0:
    print(f"\n✅ Conversion values are being tracked!")
    print(f"   • For every $1 spent on Saturday, you generated ${sat_roas:.2f} in value")
    print(f"   • For every $1 spent on Sunday, you generated ${sun_roas:.2f} in value")
    print(f"   • Weekend overall ROAS: {weekend_roas:.2f}x")

    roi_percent = ((weekend_value - weekend_spend) / weekend_spend * 100) if weekend_spend > 0 else 0
    profit = weekend_value - weekend_spend

    print(f"\n💰 Weekend ROI: {roi_percent:.1f}%")
    print(f"   • Revenue: ${weekend_value:,.2f}")
    print(f"   • Ad Spend: ${weekend_spend:,.2f}")
    print(f"   • Profit: ${profit:,.2f}")
else:
    print(f"\n⚠️  No conversion values tracked in Google Ads")
    print(f"\n   This could mean:")
    print(f"   1. Conversion values haven't been set up in Google Ads")
    print(f"   2. Values are tracked elsewhere (CRM, sales system)")
    print(f"   3. Deals haven't been assigned values yet")

    print(f"\n📊 Manual ROAS Calculation:")
    print(f"   If you know the average deal value, we can calculate estimated ROAS:")
    print(f"   • Weekend conversions: {int(sat['conversions'] + sun['conversions'])}")
    print(f"   • Weekend spend: ${weekend_spend:,.2f}")
    print(f"\n   Example: If average deal value is $5,000:")
    print(f"   • Estimated revenue: {int(sat['conversions'] + sun['conversions'])} × $5,000 = ${int(sat['conversions'] + sun['conversions']) * 5000:,}")
    print(f"   • Estimated ROAS: ${int(sat['conversions'] + sun['conversions']) * 5000:,} / ${weekend_spend:,.2f} = {(int(sat['conversions'] + sun['conversions']) * 5000 / weekend_spend):.2f}x")

print("\n" + "=" * 100)

# Query conversion action values to see if any have values assigned
print("\n🔍 Checking Conversion Action Values...")
print("=" * 100)

query_conv_values = f"""
    SELECT
        segments.conversion_action_name,
        segments.date,
        metrics.conversions,
        metrics.conversions_value
    FROM campaign
    WHERE segments.date BETWEEN '{saturday_str}' AND '{sunday_str}'
        AND metrics.conversions > 0
"""

response_conv = ga_service.search(customer_id=customer_id, query=query_conv_values)

conv_values = {}
for row in response_conv:
    conv_name = row.segments.conversion_action_name
    value = row.metrics.conversions_value
    conversions = row.metrics.conversions

    if conv_name:
        if conv_name not in conv_values:
            conv_values[conv_name] = {'conversions': 0, 'value': 0}
        conv_values[conv_name]['conversions'] += conversions
        conv_values[conv_name]['value'] += value

if conv_values:
    print(f"\n{'Conversion Type':<60} {'Count':>15} {'Value':>20}")
    print("-" * 100)
    for conv_type, data in sorted(conv_values.items(), key=lambda x: x[1]['value'], reverse=True):
        print(f"{conv_type:<60} {int(data['conversions']):>15} ${data['value']:>19.2f}")

print("\n" + "=" * 100)
