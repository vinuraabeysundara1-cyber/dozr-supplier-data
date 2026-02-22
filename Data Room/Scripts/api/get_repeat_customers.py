#!/usr/bin/env python3
"""Query Metabase to find repeat customers and their order patterns"""

import urllib.request
import json
from datetime import datetime
from collections import Counter

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
        error_body = e.read().decode()
        print(error_body)
        raise

def query_native_mongodb(collection, query_filter=None, limit=1000, projection=None):
    """Run a native MongoDB query via Metabase"""

    # Build the MongoDB query
    mongo_query = {
        "collection": collection,
        "find": json.dumps(query_filter) if query_filter else "{}",
        "limit": limit
    }

    if projection:
        mongo_query["project"] = json.dumps(projection)

    query_data = {
        "database": 2,  # MongoDB database ID
        "native": {
            "query": json.dumps(mongo_query),
            "template-tags": {}
        },
        "type": "native"
    }

    result = metabase_request("/api/dataset", method="POST", data=query_data)
    return result

def main():
    print("=" * 80)
    print("DOZR REPEAT CUSTOMER ANALYSIS")
    print("=" * 80)

    # First, let's explore what's in the accounts collection
    print("\n1. Sampling account structure...")
    print("-" * 80)

    try:
        # Get sample accounts
        sample_query = query_native_mongodb("accounts", limit=5)

        if 'data' in sample_query and 'rows' in sample_query['data']:
            print(f"\nFound {len(sample_query['data']['rows'])} sample accounts")
            print("\nColumns available:")
            for i, col in enumerate(sample_query['data']['cols']):
                print(f"  {i}: {col.get('name', col.get('display_name', 'unknown'))}")

            print("\n\nSample account (first row):")
            if sample_query['data']['rows']:
                first_row = sample_query['data']['rows'][0]
                for i, col in enumerate(sample_query['data']['cols']):
                    col_name = col.get('name', col.get('display_name', 'unknown'))
                    value = first_row[i] if i < len(first_row) else 'N/A'
                    # Truncate long values
                    if isinstance(value, str) and len(value) > 100:
                        value = value[:100] + "..."
                    print(f"  {col_name}: {value}")

        # Now let's look at supplierrequests to understand order patterns
        print("\n\n2. Analyzing supplier requests (orders)...")
        print("-" * 80)

        orders_query = query_native_mongodb("supplierrequests", limit=1000)

        if 'data' in orders_query and 'rows' in orders_query['data']:
            rows = orders_query['data']['rows']
            cols = orders_query['data']['cols']

            print(f"\nFound {len(rows)} orders")
            print("\nOrder columns:")
            for i, col in enumerate(cols):
                print(f"  {i}: {col.get('name', col.get('display_name', 'unknown'))}")

            # Try to find customer/account ID column
            account_col_idx = None
            for i, col in enumerate(cols):
                col_name = str(col.get('name', '')).lower()
                if 'account' in col_name or 'customer' in col_name or 'user' in col_name:
                    print(f"\n  → Found potential customer identifier: {col.get('name')} at index {i}")
                    account_col_idx = i

            if account_col_idx is not None:
                # Count orders per customer
                print("\n\n3. Analyzing repeat customers...")
                print("-" * 80)

                customer_orders = Counter()
                for row in rows:
                    if account_col_idx < len(row) and row[account_col_idx]:
                        customer_id = row[account_col_idx]
                        customer_orders[customer_id] += 1

                # Find repeat customers (2+ orders)
                repeat_customers = {k: v for k, v in customer_orders.items() if v >= 2}

                print(f"\nTotal unique customers: {len(customer_orders)}")
                print(f"Repeat customers (2+ orders): {len(repeat_customers)}")
                print(f"One-time customers: {len(customer_orders) - len(repeat_customers)}")
                print(f"Repeat customer rate: {len(repeat_customers)/len(customer_orders)*100:.1f}%")

                print(f"\n\nTop 20 Repeat Customers by Order Count:")
                print(f"{'Customer ID':<40} {'Orders':<10}")
                print("-" * 50)

                for customer_id, count in customer_orders.most_common(20):
                    # Truncate long IDs
                    display_id = str(customer_id)[:38] if len(str(customer_id)) > 38 else str(customer_id)
                    print(f"{display_id:<40} {count:<10}")

                # Distribution of order counts
                print(f"\n\nOrder Count Distribution:")
                order_count_dist = Counter(customer_orders.values())
                for order_count in sorted(order_count_dist.keys())[:15]:
                    num_customers = order_count_dist[order_count]
                    bar = "█" * min(50, num_customers)
                    print(f"{order_count:2d} orders: {num_customers:4d} customers {bar}")

    except Exception as e:
        print(f"\nError querying database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
