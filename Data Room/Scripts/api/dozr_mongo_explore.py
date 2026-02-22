#!/usr/bin/env python3
"""Explore MongoDB structure to find deal data"""

from pymongo import MongoClient
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

MONGO_URI = "mongodb+srv://metabase:iQfaEx77ipg1i2A1@production-dw-cluster.nnvqt.mongodb.net/dw"

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
db = client['dw']

print("Collections in dw database:")
print("-" * 40)
for col in sorted(db.list_collection_names()):
    try:
        count = db[col].estimated_document_count()
        print(f"{col}: ~{count:,} docs")
    except:
        print(f"{col}: (error)")

client.close()
