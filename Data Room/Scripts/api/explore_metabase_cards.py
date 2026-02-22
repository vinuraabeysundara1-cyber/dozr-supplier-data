#!/usr/bin/env python3
"""Explore saved Metabase questions/cards to find customer-related queries"""

import urllib.request
import json

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
    print("EXPLORING METABASE SAVED QUERIES")
    print("=" * 80)

    # Get all saved questions/cards
    print("\n1. Getting saved questions...")
    cards = metabase_request("/api/card")

    if cards:
        print(f"\nFound {len(cards)} saved questions/cards")

        # Filter for customer/account/order related queries
        keywords = ['customer', 'account', 'order', 'repeat', 'retention', 'user']

        print("\n\nSaved queries related to customers/orders:")
        print("-" * 80)

        relevant_cards = []
        for card in cards:
            name = card.get('name', '').lower()
            description = str(card.get('description') or '').lower()

            if any(keyword in name or keyword in description for keyword in keywords):
                relevant_cards.append(card)
                print(f"\nID: {card.get('id')}")
                print(f"Name: {card.get('name')}")
                desc = card.get('description') or 'N/A'
                print(f"Description: {desc if len(desc) <= 100 else desc[:100] + '...'}")
                print(f"Collection: {card.get('collection', {}).get('name', 'N/A')}")

        # Get tables from database
        print("\n\n2. Getting database tables...")
        print("-" * 80)

        database = metabase_request("/api/database/2")

        if database:
            print(f"\nDatabase: {database.get('name')}")
            print(f"Engine: {database.get('engine')}")

        # Get tables
        tables = metabase_request("/api/database/2/metadata")

        if tables and 'tables' in tables:
            print(f"\n\nAvailable tables ({len(tables['tables'])}):")
            for table in tables['tables']:
                print(f"\n  {table.get('name')}")
                print(f"    ID: {table.get('id')}")
                print(f"    Rows: {table.get('rows', 'unknown')}")

                # Show some fields
                if 'fields' in table and table['fields']:
                    print(f"    Fields ({len(table['fields'])}):")
                    for field in table['fields'][:10]:  # Show first 10 fields
                        print(f"      - {field.get('name')} ({field.get('base_type', 'unknown')})")
                    if len(table['fields']) > 10:
                        print(f"      ... and {len(table['fields']) - 10} more fields")

    # Try to execute a simple card if any exist
    if relevant_cards:
        print("\n\n3. Trying to run a saved query...")
        print("-" * 80)

        first_card = relevant_cards[0]
        card_id = first_card.get('id')
        print(f"\nRunning card: {first_card.get('name')}")

        result = metabase_request(f"/api/card/{card_id}/query", method="POST", data={})

        if result and 'data' in result:
            print(f"\nQuery returned {len(result['data'].get('rows', []))} rows")
            if result['data'].get('cols'):
                print("\nColumns:")
                for col in result['data']['cols']:
                    print(f"  - {col.get('display_name', col.get('name', 'unknown'))}")

if __name__ == "__main__":
    main()
