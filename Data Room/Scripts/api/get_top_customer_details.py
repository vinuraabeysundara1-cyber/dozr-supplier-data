#!/usr/bin/env python3
"""Get detailed information about top repeat customers"""

import urllib.request
import json
import csv
from datetime import datetime

METABASE_URL = "https://starry-bolt.metabaseapp.com"
METABASE_KEY = "mb_XRBKMlQkz3Waw1jpgaNUVIYM+nEkF2bCexU1sUI0Uks="

# Top customer IDs from previous query
TOP_CUSTOMER_IDS = [
    "62c5b859add7a3e6943e2e1e",  # 28 orders
    "67506645f7316c43a313d9d6",  # 17 orders
    "670d717d725e5dd4b1d2abe6",  # 16 orders
    "68dd41ad4a82f9ebd68a50f9",  # 15 orders
    "680b98a240d4214e74db820b",  # 14 orders
    "68936bad2e9bc80ccdc3dbf9",  # 13 orders
    "68a384f1b735fffb5d8c1e99",  # 12 orders
    "654916266dfbf56d1dc5de78",  # 12 orders
    "659d5e807fb02d00f7fc5fbd",  # 12 orders
    "6703d5dfb0ff75099a1e374b",  # 10 orders
]

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

def query_metabase(query):
    """Execute a native query on Metabase"""
    query_data = {
        "database": 2,
        "native": {
            "query": query,
            "template-tags": {}
        },
        "type": "native"
    }

    result = metabase_request("/api/dataset", method="POST", data=query_data)
    return result

def get_customer_details(customer_id):
    """Get details for a specific customer from accounts collection"""
    # MongoDB query to find account by ID
    query = json.dumps({
        "collection": "accounts",
        "find": json.dumps({"_id": {"$oid": customer_id}}),
        "limit": 1
    })

    result = query_metabase(query)

    if result and 'data' in result and result['data'].get('rows'):
        cols = result['data']['cols']
        row = result['data']['rows'][0]

        # Build a dict of the customer data
        customer = {}
        for i, col in enumerate(cols):
            col_name = col.get('name', col.get('display_name', f'col_{i}'))
            customer[col_name] = row[i] if i < len(row) else None

        return customer

    return None

def get_customer_orders(customer_id):
    """Get order history for a specific customer"""
    # Query for orders by this customer
    query = json.dumps({
        "collection": "orders",
        "find": json.dumps({"accountId": {"$oid": customer_id}}),
        "limit": 100,
        "sort": json.dumps({"createdAt": -1})
    })

    result = query_metabase(query)

    if result and 'data' in result:
        return result['data']

    return None

def main():
    print("=" * 80)
    print("TOP REPEAT CUSTOMERS - DETAILED ANALYSIS")
    print("=" * 80)

    all_customer_details = []

    for i, customer_id in enumerate(TOP_CUSTOMER_IDS, 1):
        print(f"\n{'=' * 80}")
        print(f"Customer #{i} - ID: {customer_id}")
        print(f"{'=' * 80}")

        # Get customer account details
        customer = get_customer_details(customer_id)

        if customer:
            print("\nAccount Details:")
            print("-" * 80)

            # Display key fields
            key_fields = ['name', 'email', 'phone', 'companyName', 'firstName',
                         'lastName', 'city', 'state', 'country', 'createdAt',
                         'lastOrderAt', 'totalOrders', 'totalSpent']

            customer_summary = {'customer_id': customer_id, 'rank': i}

            for field in key_fields:
                value = customer.get(field)
                if value:
                    print(f"  {field:20s}: {value}")
                    customer_summary[field] = value

            # Show other interesting fields
            print("\n  Other fields:")
            for key, value in customer.items():
                if key not in key_fields and value is not None:
                    # Only show non-empty, non-dict, non-list values
                    if not isinstance(value, (dict, list)) and str(value).strip():
                        str_val = str(value)
                        if len(str_val) > 100:
                            str_val = str_val[:100] + "..."
                        print(f"    {key}: {str_val}")
                        customer_summary[key] = value

            all_customer_details.append(customer_summary)

        else:
            print(f"  Could not retrieve customer details")
            all_customer_details.append({'customer_id': customer_id, 'rank': i, 'status': 'Not found'})

        # Get recent orders
        print("\n  Recent Order History:")
        print("  " + "-" * 78)

        orders = get_customer_orders(customer_id)
        if orders and orders.get('rows'):
            print(f"  Total orders found: {len(orders['rows'])}")
            print(f"\n  Latest 5 orders:")

            cols = orders.get('cols', [])
            for j, order_row in enumerate(orders['rows'][:5], 1):
                print(f"\n  Order {j}:")
                for k, col in enumerate(cols[:10]):  # Show first 10 columns
                    col_name = col.get('name', col.get('display_name', f'col_{k}'))
                    value = order_row[k] if k < len(order_row) else None
                    if value:
                        str_val = str(value)
                        if len(str_val) > 60:
                            str_val = str_val[:60] + "..."
                        print(f"    {col_name:20s}: {str_val}")
        else:
            print("  No orders found")

    # Export summary to CSV
    if all_customer_details:
        output_file = "/Users/vinuraabeysundara/Desktop/ICG/DOZR/top_repeat_customers_details.csv"

        # Get all unique keys
        all_keys = set()
        for customer in all_customer_details:
            all_keys.update(customer.keys())

        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
            writer.writeheader()
            writer.writerows(all_customer_details)

        print(f"\n\n{'=' * 80}")
        print(f"✓ Exported detailed customer data to: top_repeat_customers_details.csv")
        print(f"{'=' * 80}")

if __name__ == "__main__":
    main()
