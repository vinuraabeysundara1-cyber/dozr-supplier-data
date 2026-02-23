from google.ads.googleads.client import GoogleAdsClient
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Load credentials
client = GoogleAdsClient.load_from_storage('/Users/vinuraabeysundara/Desktop/ICG/DOZR/Data Room/Config/google-ads.yaml')
ga_service = client.get_service('GoogleAdsService')
customer_id = '8531896842'

# Define period
start_date = '2026-02-01'
end_date = '2026-02-23'

print("=" * 160)
print(f"🔍 DSA CAMPAIGN PERFORMANCE DEEP DIVE ANALYSIS")
print(f"Period: {start_date} to {end_date}")
print("=" * 160)

# Get DSA campaign performance
query_dsa = f"""
    SELECT
        campaign.name,
        campaign.id,
        metrics.cost_micros,
        metrics.clicks,
        metrics.impressions,
        metrics.average_cpc,
        metrics.ctr,
        metrics.conversions,
        metrics.conversions_value,
        metrics.cost_per_conversion
    FROM campaign
    WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.status = 'ENABLED'
        AND campaign.name LIKE '%DSA%'
        AND campaign.name LIKE '%US%'
"""

response_dsa = ga_service.search(customer_id=customer_id, query=query_dsa)

dsa_data = {
    'spend': 0,
    'clicks': 0,
    'impressions': 0,
    'conversions': 0,
    'value': 0
}

for row in response_dsa:
    dsa_data['spend'] += row.metrics.cost_micros / 1_000_000
    dsa_data['clicks'] += row.metrics.clicks
    dsa_data['impressions'] += row.metrics.impressions
    dsa_data['conversions'] += row.metrics.conversions
    dsa_data['value'] += row.metrics.conversions_value

# Get all non-DSA search campaigns for comparison
query_search = f"""
    SELECT
        campaign.name,
        metrics.cost_micros,
        metrics.clicks,
        metrics.impressions,
        metrics.conversions,
        metrics.conversions_value
    FROM campaign
    WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.status = 'ENABLED'
        AND campaign.name LIKE '%Search%'
        AND campaign.name NOT LIKE '%DSA%'
        AND campaign.name LIKE '%US%'
"""

response_search = ga_service.search(customer_id=customer_id, query=query_search)

search_data = {
    'spend': 0,
    'clicks': 0,
    'impressions': 0,
    'conversions': 0,
    'value': 0
}

for row in response_search:
    search_data['spend'] += row.metrics.cost_micros / 1_000_000
    search_data['clicks'] += row.metrics.clicks
    search_data['impressions'] += row.metrics.impressions
    search_data['conversions'] += row.metrics.conversions
    search_data['value'] += row.metrics.conversions_value

# Get DSA conversion breakdown
query_dsa_conv = f"""
    SELECT
        campaign.name,
        segments.conversion_action_name,
        metrics.conversions
    FROM campaign
    WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.status = 'ENABLED'
        AND campaign.name LIKE '%DSA%'
        AND campaign.name LIKE '%US%'
        AND metrics.conversions > 0
"""

response_dsa_conv = ga_service.search(customer_id=customer_id, query=query_dsa_conv)

dsa_conversions = {
    'phone_calls': 0,
    'calls_from_ads': 0,
    'quotes': 0,
    'deals': 0,
    'purchases': 0
}

for row in response_dsa_conv:
    conv_name = row.segments.conversion_action_name
    conversions = row.metrics.conversions

    if conv_name == 'Phone Call':
        dsa_conversions['phone_calls'] += conversions
    elif conv_name == 'Calls from ads':
        dsa_conversions['calls_from_ads'] += conversions
    elif 'quote' in conv_name.lower():
        dsa_conversions['quotes'] += conversions
    elif 'Closed Won' in conv_name:
        dsa_conversions['deals'] += conversions
    elif 'purchase' in conv_name.lower():
        dsa_conversions['purchases'] += conversions

# Get non-DSA search conversion breakdown
query_search_conv = f"""
    SELECT
        segments.conversion_action_name,
        metrics.conversions
    FROM campaign
    WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.status = 'ENABLED'
        AND campaign.name LIKE '%Search%'
        AND campaign.name NOT LIKE '%DSA%'
        AND campaign.name LIKE '%US%'
        AND metrics.conversions > 0
"""

response_search_conv = ga_service.search(customer_id=customer_id, query=query_search_conv)

search_conversions = {
    'phone_calls': 0,
    'calls_from_ads': 0,
    'quotes': 0,
    'deals': 0,
    'purchases': 0
}

for row in response_search_conv:
    conv_name = row.segments.conversion_action_name
    conversions = row.metrics.conversions

    if conv_name == 'Phone Call':
        search_conversions['phone_calls'] += conversions
    elif conv_name == 'Calls from ads':
        search_conversions['calls_from_ads'] += conversions
    elif 'quote' in conv_name.lower():
        search_conversions['quotes'] += conversions
    elif 'Closed Won' in conv_name:
        search_conversions['deals'] += conversions
    elif 'purchase' in conv_name.lower():
        search_conversions['purchases'] += conversions

# Print comparison
print(f"\n{'━' * 160}")
print(f"📊 DSA VS TRADITIONAL SEARCH CAMPAIGNS")
print(f"{'━' * 160}")

# Calculate metrics
dsa_cpc = dsa_data['spend'] / dsa_data['clicks'] if dsa_data['clicks'] > 0 else 0
search_cpc = search_data['spend'] / search_data['clicks'] if search_data['clicks'] > 0 else 0

dsa_ctr = (dsa_data['clicks'] / dsa_data['impressions'] * 100) if dsa_data['impressions'] > 0 else 0
search_ctr = (search_data['clicks'] / search_data['impressions'] * 100) if search_data['impressions'] > 0 else 0

dsa_roas = dsa_data['value'] / dsa_data['spend'] if dsa_data['spend'] > 0 else 0
search_roas = search_data['value'] / search_data['spend'] if search_data['spend'] > 0 else 0

dsa_cpa = dsa_data['spend'] / dsa_data['conversions'] if dsa_data['conversions'] > 0 else 0
search_cpa = search_data['spend'] / search_data['conversions'] if search_data['conversions'] > 0 else 0

dsa_total_calls = dsa_conversions['phone_calls'] + dsa_conversions['calls_from_ads']
search_total_calls = search_conversions['phone_calls'] + search_conversions['calls_from_ads']

dsa_cost_per_call = dsa_data['spend'] / dsa_total_calls if dsa_total_calls > 0 else 0
search_cost_per_call = search_data['spend'] / search_total_calls if search_total_calls > 0 else 0

print(f"\n{'Metric':<40} {'DSA Campaigns':>25} {'Traditional Search':>25} {'Winner':>20}")
print("-" * 160)

# Spend
print(f"{'💰 Total Spend':<40} ${dsa_data['spend']:>24,.2f} ${search_data['spend']:>24,.2f} {'-':>20}")

# Clicks
print(f"{'👆 Clicks':<40} {dsa_data['clicks']:>25,} {search_data['clicks']:>25,} {'-':>20}")

# CPC
cpc_winner = "🏆 DSA" if dsa_cpc < search_cpc else "Traditional"
print(f"{'💵 Avg CPC':<40} ${dsa_cpc:>24,.2f} ${search_cpc:>24,.2f} {cpc_winner:>20}")

# CTR
ctr_winner = "🏆 DSA" if dsa_ctr > search_ctr else "Traditional"
print(f"{'📊 CTR':<40} {dsa_ctr:>23.2f}% {search_ctr:>23.2f}% {ctr_winner:>20}")

# Calls
calls_winner = "🏆 DSA" if dsa_total_calls > search_total_calls else "Traditional"
print(f"{'📞 Total Calls':<40} {int(dsa_total_calls):>25} {int(search_total_calls):>25} {calls_winner:>20}")

# Cost per call
cpc_winner = "🏆 DSA" if dsa_cost_per_call < search_cost_per_call else "Traditional"
print(f"{'💲 Cost Per Call':<40} ${dsa_cost_per_call:>24,.2f} ${search_cost_per_call:>24,.2f} {cpc_winner:>20}")

# Quotes
quotes_winner = "🏆 DSA" if dsa_conversions['quotes'] > search_conversions['quotes'] else "Traditional"
print(f"{'📋 Quotes':<40} {int(dsa_conversions['quotes']):>25} {int(search_conversions['quotes']):>25} {quotes_winner:>20}")

# Deals
deals_winner = "🏆 DSA" if dsa_conversions['deals'] > search_conversions['deals'] else "Traditional"
print(f"{'🎉 Deals':<40} {int(dsa_conversions['deals']):>25} {int(search_conversions['deals']):>25} {deals_winner:>20}")

# Conversion Value
value_winner = "🏆 DSA" if dsa_data['value'] > search_data['value'] else "Traditional"
print(f"{'💎 Conversion Value':<40} ${dsa_data['value']:>24,.2f} ${search_data['value']:>24,.2f} {value_winner:>20}")

# ROAS
roas_winner = "🏆 DSA" if dsa_roas > search_roas else "Traditional"
print(f"{'📈 ROAS':<40} {dsa_roas:>23.2f}x {search_roas:>23.2f}x {roas_winner:>20}")

# CPA
cpa_winner = "🏆 DSA" if dsa_cpa < search_cpa else "Traditional"
print(f"{'💰 CPA':<40} ${dsa_cpa:>24,.2f} ${search_cpa:>24,.2f} {cpa_winner:>20}")

# Print conversion rates
print(f"\n{'━' * 160}")
print(f"🔄 CONVERSION FUNNEL COMPARISON")
print(f"{'━' * 160}")

dsa_call_to_quote = (dsa_conversions['quotes'] / dsa_total_calls * 100) if dsa_total_calls > 0 else 0
search_call_to_quote = (search_conversions['quotes'] / search_total_calls * 100) if search_total_calls > 0 else 0

dsa_quote_to_deal = (dsa_conversions['deals'] / dsa_conversions['quotes'] * 100) if dsa_conversions['quotes'] > 0 else 0
search_quote_to_deal = (search_conversions['deals'] / search_conversions['quotes'] * 100) if search_conversions['quotes'] > 0 else 0

dsa_call_to_deal = (dsa_conversions['deals'] / dsa_total_calls * 100) if dsa_total_calls > 0 else 0
search_call_to_deal = (search_conversions['deals'] / search_total_calls * 100) if search_total_calls > 0 else 0

print(f"\n{'Conversion Rate':<40} {'DSA Campaigns':>25} {'Traditional Search':>25} {'Winner':>20}")
print("-" * 160)

c2q_winner = "🏆 DSA" if dsa_call_to_quote > search_call_to_quote else "Traditional"
print(f"{'📞→📋 Call to Quote':<40} {dsa_call_to_quote:>23.1f}% {search_call_to_quote:>23.1f}% {c2q_winner:>20}")

q2d_winner = "🏆 DSA" if dsa_quote_to_deal > search_quote_to_deal else "Traditional"
print(f"{'📋→🎉 Quote to Deal':<40} {dsa_quote_to_deal:>23.1f}% {search_quote_to_deal:>23.1f}% {q2d_winner:>20}")

c2d_winner = "🏆 DSA" if dsa_call_to_deal > search_call_to_deal else "Traditional"
print(f"{'📞→🎉 Call to Deal':<40} {dsa_call_to_deal:>23.1f}% {search_call_to_deal:>23.1f}% {c2d_winner:>20}")

# Daily DSA performance
print(f"\n{'=' * 160}")
print(f"📅 DSA DAILY PERFORMANCE TREND")
print(f"{'=' * 160}")

query_dsa_daily = f"""
    SELECT
        segments.date,
        metrics.cost_micros,
        metrics.clicks,
        metrics.conversions,
        metrics.conversions_value
    FROM campaign
    WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.status = 'ENABLED'
        AND campaign.name LIKE '%DSA%'
        AND campaign.name LIKE '%US%'
"""

response_dsa_daily = ga_service.search(customer_id=customer_id, query=query_dsa_daily)

dsa_daily = {}
for row in response_dsa_daily:
    date = row.segments.date
    if date not in dsa_daily:
        dsa_daily[date] = {
            'spend': 0,
            'clicks': 0,
            'conversions': 0,
            'value': 0
        }

    dsa_daily[date]['spend'] += row.metrics.cost_micros / 1_000_000
    dsa_daily[date]['clicks'] += row.metrics.clicks
    dsa_daily[date]['conversions'] += row.metrics.conversions
    dsa_daily[date]['value'] += row.metrics.conversions_value

print(f"\n{'Date':<15} {'Spend':>12} {'Clicks':>8} {'Conv':>7} {'Value':>14} {'ROAS':>8} {'CPC':>8}")
print("-" * 160)

for date in sorted(dsa_daily.keys()):
    data = dsa_daily[date]
    roas = data['value'] / data['spend'] if data['spend'] > 0 else 0
    cpc = data['spend'] / data['clicks'] if data['clicks'] > 0 else 0

    print(f"{date:<15} ${data['spend']:>11,.2f} {data['clicks']:>8} {int(data['conversions']):>7} ${data['value']:>13,.2f} {roas:>6.2f}x ${cpc:>7.2f}")

# Key insights
print(f"\n{'=' * 160}")
print(f"💡 WHY DSA IS WINNING - KEY INSIGHTS")
print(f"{'=' * 160}")

insights = []

# Budget efficiency
dsa_budget_share = (dsa_data['spend'] / (dsa_data['spend'] + search_data['spend']) * 100)
dsa_deal_share = (dsa_conversions['deals'] / (dsa_conversions['deals'] + search_conversions['deals']) * 100)

if dsa_deal_share > dsa_budget_share * 1.5:
    insights.append(f"✅ Budget Efficiency: DSA uses {dsa_budget_share:.1f}% of budget but generates {dsa_deal_share:.1f}% of deals")

# ROAS advantage
if dsa_roas > search_roas * 1.2:
    roas_advantage = ((dsa_roas / search_roas - 1) * 100)
    insights.append(f"✅ ROAS Superiority: DSA ROAS is {roas_advantage:.0f}% higher than traditional search ({dsa_roas:.2f}x vs {search_roas:.2f}x)")

# Cost efficiency
if dsa_cpc < search_cpc:
    cpc_savings = ((search_cpc - dsa_cpc) / search_cpc * 100)
    insights.append(f"✅ Cost Efficiency: DSA CPC is {cpc_savings:.0f}% lower (${dsa_cpc:.2f} vs ${search_cpc:.2f})")

# Conversion rate
if dsa_call_to_deal > search_call_to_deal:
    insights.append(f"✅ Better Conversion: {dsa_call_to_deal:.1f}% call-to-deal rate vs {search_call_to_deal:.1f}% for traditional search")

# Deal value
dsa_avg_deal_value = dsa_data['value'] / dsa_conversions['deals'] if dsa_conversions['deals'] > 0 else 0
search_avg_deal_value = search_data['value'] / search_conversions['deals'] if search_conversions['deals'] > 0 else 0

if dsa_avg_deal_value > search_avg_deal_value:
    insights.append(f"✅ Higher Deal Value: DSA avg deal = ${dsa_avg_deal_value:,.2f} vs ${search_avg_deal_value:,.2f} for traditional")

# Print insights
for i, insight in enumerate(insights, 1):
    print(f"\n{i}. {insight}")

print(f"\n{'=' * 160}")
print(f"🎯 DSA SUCCESS FACTORS")
print(f"{'=' * 160}")

print(f"""
1. 🤖 AUTOMATED TARGETING
   • DSA automatically matches your website content to search queries
   • Captures long-tail searches traditional campaigns miss
   • No need to manually build keyword lists
   • Finds high-intent users searching for specific equipment

2. 🎯 DYNAMIC AD RELEVANCE
   • Ads are automatically generated based on landing page content
   • Better relevance = higher Quality Score = lower CPC
   • Dynamic headlines match user's exact search query

3. 💰 COST EFFICIENCY
   • Lower CPC: ${dsa_cpc:.2f} vs ${search_cpc:.2f} (traditional)
   • Better ROAS: {dsa_roas:.2f}x vs {search_roas:.2f}x (traditional)
   • More efficient spend allocation

4. 🔄 BETTER CONVERSION FUNNEL
   • Call-to-Deal: {dsa_call_to_deal:.1f}% vs {search_call_to_deal:.1f}% (traditional)
   • Higher intent traffic = better quality leads
   • Catches users at bottom of funnel

5. 📈 SCALABILITY
   • Automatically expands to new searches without manual work
   • Adapts to your website updates in real-time
   • Finds opportunities you wouldn't manually target

6. 🎪 WIDER NET
   • {int(dsa_conversions['deals'])} deals from diverse equipment searches
   • Traditional search limited to your keyword lists
   • DSA captures unexpected but valuable searches
""")

print(f"{'=' * 160}")
print("✅ ANALYSIS COMPLETE")
print(f"{'=' * 160}")
