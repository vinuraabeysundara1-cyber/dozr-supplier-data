#!/usr/bin/env python3
"""Track customer lifecycle journey for yesterday's Closed Won deals"""

from pymongo import MongoClient
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

# MongoDB connection
MONGO_URI = "mongodb+srv://metabase:iQfaEx77ipg1i2A1@production-dw-cluster.nnvqt.mongodb.net/dw"

def main():
    client = MongoClient(MONGO_URI)
    db = client['dw']
    
    print("=" * 80)
    print("CUSTOMER LIFECYCLE JOURNEY - Yesterday's Closed Won Deals")
    print("=" * 80)
    
    # First, let's explore what collections exist
    print("\nAvailable collections:")
    collections = db.list_collection_names()
    for col in sorted(collections):
        print(f"  - {col}")
    
    # Look for deals/orders/contracts collections
    print("\n" + "=" * 80)
    print("Searching for Closed Won deals from yesterday...")
    print("=" * 80)
    
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Try to find relevant collections for deals/orders
    potential_collections = ['deals', 'orders', 'contracts', 'quotes', 'leads', 'customers', 
                            'hubspot_deals', 'salesforce_deals', 'crm_deals', 'transactions',
                            'rentals', 'bookings', 'conversions']
    
    for col_name in potential_collections:
        if col_name in collections:
            col = db[col_name]
            count = col.count_documents({})
            print(f"\n{col_name}: {count} documents")
            
            # Sample a document to see structure
            sample = col.find_one()
            if sample:
                print(f"  Fields: {list(sample.keys())[:15]}...")
    
    # Let's look at all collections and find ones with relevant date fields
    print("\n" + "=" * 80)
    print("Searching collections for deals with value ~$10,177 or ~$1,416...")
    print("=" * 80)
    
    target_values = [10177, 10176.96, 1416, 1415.94, 9631]  # Approximate values
    
    for col_name in collections:
        col = db[col_name]
        sample = col.find_one()
        if sample:
            # Look for value/amount fields
            value_fields = [k for k in sample.keys() if any(term in k.lower() for term in 
                          ['value', 'amount', 'total', 'price', 'revenue', 'deal'])]
            
            if value_fields:
                # Try to find matching deals
                for field in value_fields:
                    for target in target_values:
                        # Search with some tolerance
                        query = {field: {"$gte": target - 10, "$lte": target + 10}}
                        matches = list(col.find(query).limit(5))
                        if matches:
                            print(f"\n>>> Found in {col_name}.{field} = ~${target}:")
                            for match in matches:
                                print(f"    Document: {match.get('_id')}")
                                # Print relevant fields
                                for k, v in match.items():
                                    if k != '_id' and not isinstance(v, (dict, list)):
                                        print(f"      {k}: {v}")

    client.close()

if __name__ == "__main__":
    main()
