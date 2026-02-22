#!/usr/bin/env python3
"""Find and run Metabase queries that show customer details"""

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

def main():
    print("=" * 80)
    print("SEARCHING FOR CUSTOMER DETAIL QUERIES")
    print("=" * 80)

    # Get all cards
    cards = metabase_request("/api/card")

    if not cards:
        print("Could not retrieve cards")
        return

    # Look for queries with customer details
    keywords = ['top customer', 'customer detail', 'customer by', 'customer list',
                'active customer', 'best customer', 'customer name', 'customer email']

    relevant_cards = []
    for card in cards:
        name = str(card.get('name', '')).lower()
        if any(keyword in name for keyword in keywords):
            relevant_cards.append(card)

    print(f"\nFound {len(relevant_cards)} potentially relevant queries:")
    print("-" * 80)

    for card in relevant_cards:
        print(f"\nID: {card.get('id'):4d} | {card.get('name')}")

    # Try running a few promising ones
    if relevant_cards:
        print("\n\n" + "=" * 80)
        print("RUNNING CUSTOMER DETAIL QUERIES")
        print("=" * 80)

        for card in relevant_cards[:5]:  # Try first 5
            card_id = card.get('id')
            card_name = card.get('name')

            print(f"\n\n{'=' * 80}")
            print(f"{card_name} (ID: {card_id})")
            print(f"{'=' * 80}")

            result = metabase_request(f"/api/card/{card_id}/query", method="POST", data={})

            if result and 'data' in result:
                data = result['data']
                rows = data.get('rows', [])
                cols = data.get('cols', [])

                print(f"\nReturned {len(rows)} rows")

                if rows and len(rows) > 0:
                    # Print headers
                    headers = [col.get('display_name', col.get('name', f'col_{i}'))
                              for i, col in enumerate(cols)]
                    print("\nColumns: " + ", ".join(headers))

                    # Print first 10 rows
                    print("\nFirst 10 rows:")
                    print("-" * 80)

                    for i, row in enumerate(rows[:10], 1):
                        print(f"\nRow {i}:")
                        for j, (header, value) in enumerate(zip(headers, row)):
                            if value is not None:
                                str_val = str(value)
                                if len(str_val) > 80:
                                    str_val = str_val[:80] + "..."
                                print(f"  {header:30s}: {str_val}")

                    # Export if this looks like customer details
                    if any('email' in h.lower() or 'name' in h.lower() or 'phone' in h.lower()
                          for h in headers):
                        filename = f"customer_data_{card_id}.csv"
                        filepath = f"/Users/vinuraabeysundara/Desktop/ICG/DOZR/{filename}"

                        with open(filepath, 'w', newline='') as f:
                            writer = csv.writer(f)
                            writer.writerow(headers)
                            writer.writerows(rows)

                        print(f"\n  ✓ Exported to: {filename}")

    # Also try to get the accounts table directly
    print("\n\n" + "=" * 80)
    print("TRYING DIRECT TABLE ACCESS")
    print("=" * 80)

    # Get table metadata
    tables = metabase_request("/api/database/2/metadata")

    if tables and 'tables' in tables:
        accounts_table = None
        orders_table = None

        for table in tables['tables']:
            if table.get('name') == 'accounts':
                accounts_table = table
            elif table.get('name') == 'orders':
                orders_table = table

        if accounts_table:
            table_id = accounts_table.get('id')
            print(f"\nFound 'accounts' table (ID: {table_id})")
            print(f"Rows: {accounts_table.get('rows', 'unknown')}")
            print("\nFields:")
            for field in accounts_table.get('fields', [])[:20]:
                print(f"  - {field.get('name')} ({field.get('base_type')})")

            # Try to query it
            print("\nAttempting to query accounts table...")

            query_data = {
                "database": 2,
                "type": "query",
                "query": {
                    "source-table": table_id,
                    "limit": 100
                }
            }

            result = metabase_request("/api/dataset", method="POST", data=query_data)

            if result and 'data' in result:
                data = result['data']
                rows = data.get('rows', [])
                cols = data.get('cols', [])

                print(f"\n✓ Retrieved {len(rows)} accounts")

                if rows:
                    headers = [col.get('display_name', col.get('name', f'col_{i}'))
                              for i, col in enumerate(cols)]

                    print("\nSample accounts:")
                    for i, row in enumerate(rows[:5], 1):
                        print(f"\nAccount {i}:")
                        for j, (header, value) in enumerate(zip(headers, row)):
                            if value is not None and j < 15:  # Show first 15 fields
                                str_val = str(value)
                                if len(str_val) > 60:
                                    str_val = str_val[:60] + "..."
                                print(f"  {header:25s}: {str_val}")

                    # Export
                    filepath = "/Users/vinuraabeysundara/Desktop/ICG/DOZR/all_accounts_sample.csv"
                    with open(filepath, 'w', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(headers)
                        writer.writerows(rows)

                    print(f"\n✓ Exported to: all_accounts_sample.csv")

if __name__ == "__main__":
    main()
