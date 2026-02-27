#!/usr/bin/env python3
"""February 2026 Conversion Funnel Analysis"""

from google.ads.googleads.client import GoogleAdsClient
from collections import defaultdict
import warnings
warnings.filterwarnings("ignore")

client = GoogleAdsClient.load_from_storage("/Users/vinuraabeysundara/Desktop/ICG/DOZR/Data Room/Config/google-ads.yaml")
ga_service = client.get_service("GoogleAdsService")
cid = "8531896842"

def run_query(q):
    return list(ga_service.search(customer_id=cid, query=q))

# Test basic query
print("Testing API connection...")
test = run_query("SELECT campaign.name, metrics.clicks FROM campaign WHERE segments.date = '2026-02-20' LIMIT 3")
print(f"  Test query returned {len(test)} rows")
for r in test:
    print(f"  {r.campaign.name}: {r.metrics.clicks} clicks")

# Get traffic day by day
print("\nPulling traffic data day by day...")
traffic = defaultdict(lambda: {"clicks": 0, "cost": 0})

for day in range(1, 27):
    date_str = f"2026-02-{day:02d}"
    q = f"SELECT campaign.name, metrics.clicks, metrics.cost_micros FROM campaign WHERE campaign.status = 'ENABLED' AND segments.date = '{date_str}'"
    rows = run_query(q)
    day_total = 0
    for row in rows:
        if row.metrics.clicks > 0:
            traffic[row.campaign.name]["clicks"] += row.metrics.clicks
            traffic[row.campaign.name]["cost"] += row.metrics.cost_micros / 1_000_000
            day_total += row.metrics.clicks
    if day in [1, 10, 20, 26]:
        print(f"  Feb {day:02d}: {day_total} clicks")

# Get conversion data day by day
print("\nPulling conversion data...")
convs = defaultdict(lambda: {"phone": 0, "cfa": 0, "qual": 0, "quote": 0, "won": 0, "purch": 0})

for day in range(1, 27):
    date_str = f"2026-02-{day:02d}"
    q = f"SELECT campaign.name, segments.conversion_action_name, metrics.conversions FROM campaign WHERE campaign.status = 'ENABLED' AND segments.date = '{date_str}' AND metrics.conversions > 0"
    rows = run_query(q)
    for row in rows:
        n = row.campaign.name
        a = row.segments.conversion_action_name
        c = row.metrics.conversions
        if a == "Phone Call": convs[n]["phone"] += c
        elif a == "Calls from ads": convs[n]["cfa"] += c
        elif "Qualified" in a: convs[n]["qual"] += c
        elif "quote" in a.lower(): convs[n]["quote"] += c
        elif "Closed Won" in a: convs[n]["won"] += c
        elif "Purchase" in a: convs[n]["purch"] += c

# Combined table
print(f"\n{'Campaign':<42} {'Clicks':>6} {'$Spend':>8} {'Phone':>6} {'CfAds':>5} {'Qual':>5} {'Quote':>5} {'Won':>5} {'Prch':>4}")
print("=" * 100)

totals = [0]*8
for name in sorted(traffic.keys()):
    tr = traffic[name]
    cv = convs[name]
    if tr["cost"] > 50:
        vals = [tr["clicks"], tr["cost"], cv["phone"], cv["cfa"], cv["qual"], cv["quote"], cv["won"], cv["purch"]]
        print(f"{name:<42} {vals[0]:>6} ${vals[1]:>7.0f} {vals[2]:>6.1f} {vals[3]:>5.1f} {vals[4]:>5.1f} {vals[5]:>5.1f} {vals[6]:>5.1f} {vals[7]:>4.1f}")
        for i in range(8): totals[i] += vals[i]

print("=" * 100)
print(f"{'TOTAL':<42} {totals[0]:>6} ${totals[1]:>7.0f} {totals[2]:>6.1f} {totals[3]:>5.1f} {totals[4]:>5.1f} {totals[5]:>5.1f} {totals[6]:>5.1f} {totals[7]:>4.1f}")

clicks, cost, phone, cfa, qual, quote, won, purch = totals
total_calls = phone + cfa

if clicks > 0:
    print(f"\n\n{'='*60}")
    print(f"FEBRUARY 2026 (Feb 1-26) — CONVERSION FUNNEL")
    print(f"{'='*60}\n")
    print(f"  Clicks                     {clicks:>6}")
    print(f"    | {total_calls/clicks*100:.1f}% generate a call")
    print(f"  Total Calls                {total_calls:>6.0f}   (Phone {phone:.0f} + Call Ext {cfa:.0f})")
    if total_calls > 0:
        print(f"    | {qual/total_calls*100:.1f}% qualify")
    print(f"  Qualified Calls            {qual:>6.0f}")
    print(f"")
    print(f"  Quote Requests             {quote:>6.0f}   ({quote/clicks*100:.1f}% of clicks)")
    if quote > 0:
        print(f"    | {won/quote*100:.1f}% close")
    print(f"  Closed Won Deals           {won:>6.1f}   ({won/clicks*100:.2f}% of clicks)")
    print(f"")
    print(f"  GA4 Purchases              {purch:>6.0f}   ({purch/clicks*100:.2f}% of clicks)")

    print(f"\n  COST PER STAGE")
    print(f"  {'='*40}")
    print(f"  Cost per Click:            ${cost/clicks:.2f}")
    if total_calls > 0:
        print(f"  Cost per Call:             ${cost/total_calls:.2f}")
    if qual > 0:
        print(f"  Cost per Qualified Call:   ${cost/qual:.2f}")
    if quote > 0:
        print(f"  Cost per Quote:            ${cost/quote:.2f}")
    if won > 0:
        print(f"  Cost per Closed Won:       ${cost/won:.2f}")
    if purch > 0:
        print(f"  Cost per Purchase:         ${cost/purch:.2f}")

    # Per campaign funnel
    print(f"\n\n{'='*60}")
    print(f"PER CAMPAIGN FUNNEL RATES")
    print(f"{'='*60}\n")
    print(f"{'Campaign':<40} {'Clk>Call':>8} {'Call>Ql':>8} {'Clk>Qt':>8} {'Qt>Won':>8} {'$/Won':>10}")
    print("-" * 85)
    for name in sorted(traffic.keys()):
        tr = traffic[name]
        cv = convs[name]
        if tr["cost"] > 50:
            tc = cv["phone"] + cv["cfa"]
            c2c = f"{tc/tr['clicks']*100:.1f}%" if tr['clicks'] > 0 else "-"
            c2q = f"{cv['qual']/tc*100:.0f}%" if tc > 0 else "-"
            clk2qt = f"{cv['quote']/tr['clicks']*100:.1f}%" if tr['clicks'] > 0 else "-"
            q2w = f"{cv['won']/cv['quote']*100:.0f}%" if cv['quote'] > 0 else "-"
            cpw = f"${tr['cost']/cv['won']:.0f}" if cv['won'] > 0 else "-"
            print(f"{name:<40} {c2c:>8} {c2q:>8} {clk2qt:>8} {q2w:>8} {cpw:>10}")
else:
    print("\nNo data returned from API.")
