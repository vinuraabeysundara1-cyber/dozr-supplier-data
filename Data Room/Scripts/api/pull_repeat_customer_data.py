#!/usr/bin/env python3
"""Pull repeat customer data from saved Metabase queries"""

import urllib.request
import json
import csv

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
        return None

def run_saved_query(card_id, card_name):
    """Run a saved Metabase query and display results"""
    print(f"\n{'=' * 80}")
    print(f"{card_name}")
    print(f"{'=' * 80}")

    result = metabase_request(f"/api/card/{card_id}/query", method="POST", data={})

    if not result or 'data' not in result:
        print("No data returned")
        return None

    data = result['data']
    rows = data.get('rows', [])
    cols = data.get('cols', [])

    print(f"\nReturned {len(rows)} rows\n")

    if not rows:
        print("No data available")
        return None

    # Print column headers
    headers = [col.get('display_name', col.get('name', f'col_{i}')) for i, col in enumerate(cols)]
    print("  ".join(f"{h:>20}" for h in headers))
    print("-" * (22 * len(headers)))

    # Print rows (limit to first 50)
    for row in rows[:50]:
        formatted_row = []
        for i, val in enumerate(row):
            if val is None:
                formatted_row.append("N/A")
            elif isinstance(val, (int, float)):
                if isinstance(val, float):
                    formatted_row.append(f"{val:.2f}")
                else:
                    formatted_row.append(str(val))
            else:
                # Truncate long strings
                str_val = str(val)
                formatted_row.append(str_val if len(str_val) <= 20 else str_val[:18] + "..")

        print("  ".join(f"{v:>20}" for v in formatted_row))

    if len(rows) > 50:
        print(f"\n... and {len(rows) - 50} more rows")

    return {'headers': headers, 'rows': rows}

def main():
    print("=" * 80)
    print("DOZR REPEAT CUSTOMER DATA")
    print("=" * 80)

    # Query IDs from exploration
    queries = [
        (272, "6.1 Unique Customers (Period)"),
        (273, "6.2 Repeat Customers"),
        (274, "6.3 Repeat Order Rate (%)"),
        (276, "6.5 Top Customers by Volume"),
    ]

    results = {}

    for card_id, card_name in queries:
        result = run_saved_query(card_id, card_name)
        if result:
            results[card_name] = result

    # Export to CSV if we got top customers data
    if "6.5 Top Customers by Volume" in results:
        data = results["6.5 Top Customers by Volume"]
        output_file = "/Users/vinuraabeysundara/Desktop/ICG/DOZR/repeat_customers_by_volume.csv"

        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(data['headers'])
            writer.writerows(data['rows'])

        print(f"\n\n✓ Exported top customers to: repeat_customers_by_volume.csv")

if __name__ == "__main__":
    main()
