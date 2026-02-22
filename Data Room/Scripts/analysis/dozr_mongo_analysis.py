#!/usr/bin/env python3
"""
DOZR MongoDB Analysis: Contractor Behavior Patterns
Queries order, calls, supplierrequests, and contracts collections
to determine when contractors actually place orders and make calls.
All timestamps converted to US/Eastern.
"""

import pymongo
from datetime import datetime, timedelta
from collections import defaultdict
import sys

MONGO_URI = "mongodb+srv://metabase:iQfaEx77ipg1i2A1@production-dw-cluster.nnvqt.mongodb.net/dw"
DB_NAME = "dw"

# 6 months ago from today
SIX_MONTHS_AGO = datetime.utcnow() - timedelta(days=180)

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

def connect():
    print("Connecting to MongoDB...")
    client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=15000)
    # Force connection test
    client.admin.command('ping')
    print("Connected successfully.\n")
    return client[DB_NAME]

def print_separator(char="=", length=80):
    print(char * length)

def sample_document(db, collection_name):
    """Sample one document to discover available fields, especially timestamps."""
    coll = db[collection_name]
    doc = coll.find_one()
    if doc is None:
        print(f"  [No documents found in '{collection_name}']")
        return None, None

    print(f"\n  Available fields in '{collection_name}' (sample document):")
    timestamp_fields = []
    for key, value in sorted(doc.items()):
        type_name = type(value).__name__
        preview = str(value)[:80] if value is not None else "None"
        print(f"    {key:<30} ({type_name:<12}) = {preview}")
        if isinstance(value, datetime):
            timestamp_fields.append(key)

    print(f"\n  Timestamp fields found: {timestamp_fields if timestamp_fields else 'NONE'}")
    total = coll.estimated_document_count()
    print(f"  Estimated total documents: {total:,}")
    return doc, timestamp_fields

def aggregate_timing(db, collection_name, timestamp_field):
    """
    Aggregate documents by hour of day and day of week,
    converting to US/Eastern (UTC-5, simplified — MongoDB $subtract 5 hours).
    For proper DST handling we'd need a more complex approach, but UTC-5 covers
    most of Eastern Standard Time which is sufficient for pattern analysis.
    """
    coll = db[collection_name]

    # Count documents in the last 6 months
    recent_count = coll.count_documents({timestamp_field: {"$gte": SIX_MONTHS_AGO}})
    print(f"\n  Documents in last 6 months (since {SIX_MONTHS_AGO.strftime('%Y-%m-%d')}): {recent_count:,}")

    if recent_count == 0:
        # Try without date filter
        print("  No recent documents. Trying ALL documents...")
        date_filter = {}
        total_for_analysis = coll.estimated_document_count()
        if total_for_analysis == 0:
            print("  No documents at all. Skipping.")
            return
    else:
        date_filter = {timestamp_field: {"$gte": SIX_MONTHS_AGO}}

    # --- Aggregate by HOUR OF DAY (Eastern = UTC - 5 hours) ---
    pipeline_hour = [
        {"$match": date_filter} if date_filter else {"$match": {}},
        {"$project": {
            "easternTime": {
                "$subtract": [f"${timestamp_field}", 5 * 60 * 60 * 1000]  # subtract 5 hours in ms
            }
        }},
        {"$group": {
            "_id": {"$hour": "$easternTime"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]

    hour_results = list(coll.aggregate(pipeline_hour))

    # --- Aggregate by DAY OF WEEK (Eastern = UTC - 5 hours) ---
    pipeline_dow = [
        {"$match": date_filter} if date_filter else {"$match": {}},
        {"$project": {
            "easternTime": {
                "$subtract": [f"${timestamp_field}", 5 * 60 * 60 * 1000]
            }
        }},
        {"$group": {
            "_id": {"$dayOfWeek": "$easternTime"},  # 1=Sun, 2=Mon, ..., 7=Sat
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]

    dow_results = list(coll.aggregate(pipeline_dow))

    # --- Print Hour of Day Distribution ---
    total_hour = sum(r["count"] for r in hour_results)
    print(f"\n  HOUR OF DAY Distribution (Eastern Time) — Total: {total_hour:,}")
    print(f"  {'Hour':<8} {'Count':>10} {'Pct':>8}  Bar")
    print(f"  {'-'*6:<8} {'-'*10:>10} {'-'*6:>8}  {'-'*30}")

    hour_map = {r["_id"]: r["count"] for r in hour_results}
    max_count_hour = max(hour_map.values()) if hour_map else 1

    for h in range(24):
        count = hour_map.get(h, 0)
        pct = (count / total_hour * 100) if total_hour > 0 else 0
        bar_len = int((count / max_count_hour) * 40) if max_count_hour > 0 else 0
        bar = "#" * bar_len
        label = f"{h:02d}:00"
        print(f"  {label:<8} {count:>10,} {pct:>7.1f}%  {bar}")

    # Highlight peak hours
    if hour_map:
        sorted_hours = sorted(hour_map.items(), key=lambda x: x[1], reverse=True)
        top3 = sorted_hours[:3]
        print(f"\n  >> Peak hours: {', '.join(f'{h:02d}:00 ({c:,} = {c/total_hour*100:.1f}%)' for h, c in top3)}")

    # --- Print Day of Week Distribution ---
    total_dow = sum(r["count"] for r in dow_results)
    print(f"\n  DAY OF WEEK Distribution (Eastern Time) — Total: {total_dow:,}")
    print(f"  {'Day':<8} {'Count':>10} {'Pct':>8}  Bar")
    print(f"  {'-'*6:<8} {'-'*10:>10} {'-'*6:>8}  {'-'*30}")

    # MongoDB dayOfWeek: 1=Sun, 2=Mon, 3=Tue, 4=Wed, 5=Thu, 6=Fri, 7=Sat
    dow_map = {r["_id"]: r["count"] for r in dow_results}
    max_count_dow = max(dow_map.values()) if dow_map else 1

    dow_order = [2, 3, 4, 5, 6, 7, 1]  # Mon=2 through Sat=7, Sun=1
    dow_labels = {2: "Mon", 3: "Tue", 4: "Wed", 5: "Thu", 6: "Fri", 7: "Sat", 1: "Sun"}

    for d in dow_order:
        count = dow_map.get(d, 0)
        pct = (count / total_dow * 100) if total_dow > 0 else 0
        bar_len = int((count / max_count_dow) * 40) if max_count_dow > 0 else 0
        bar = "#" * bar_len
        label = dow_labels[d]
        print(f"  {label:<8} {count:>10,} {pct:>7.1f}%  {bar}")

    if dow_map:
        sorted_dow = sorted(dow_map.items(), key=lambda x: x[1], reverse=True)
        top_day = sorted_dow[0]
        weekday_total = sum(dow_map.get(d, 0) for d in [2, 3, 4, 5, 6])
        weekend_total = sum(dow_map.get(d, 0) for d in [1, 7])
        print(f"\n  >> Busiest day: {dow_labels.get(top_day[0], '?')} ({top_day[1]:,} = {top_day[1]/total_dow*100:.1f}%)")
        print(f"  >> Weekday vs Weekend: {weekday_total:,} ({weekday_total/total_dow*100:.1f}%) weekday | {weekend_total:,} ({weekend_total/total_dow*100:.1f}%) weekend")


def analyze_collection(db, collection_name, preferred_ts_fields=None):
    """Full analysis for a given collection."""
    print_separator("=")
    print(f"  COLLECTION: {collection_name}")
    print_separator("=")

    doc, ts_fields = sample_document(db, collection_name)
    if doc is None:
        return

    # Determine which timestamp field to use
    ts_field = None
    if preferred_ts_fields:
        for pf in preferred_ts_fields:
            if pf in doc and isinstance(doc.get(pf), datetime):
                ts_field = pf
                break

    if ts_field is None and ts_fields:
        # Use first detected datetime field, prefer 'createdAt' or 'created_at'
        for candidate in ["createdAt", "created_at", "createdat", "date", "timestamp"]:
            if candidate in ts_fields:
                ts_field = candidate
                break
        if ts_field is None:
            ts_field = ts_fields[0]

    if ts_field is None:
        print(f"\n  [WARNING] No datetime field found in '{collection_name}'. Skipping timing analysis.")
        return

    print(f"\n  Using timestamp field: '{ts_field}'")
    aggregate_timing(db, collection_name, ts_field)
    print()


def list_all_collections(db):
    """Show all collections in the database for reference."""
    colls = sorted(db.list_collection_names())
    print(f"All collections in '{DB_NAME}' database ({len(colls)} total):")
    for c in colls:
        print(f"  - {c}")
    print()
    return colls


def main():
    try:
        db = connect()
    except Exception as e:
        print(f"ERROR connecting to MongoDB: {e}")
        sys.exit(1)

    # List collections so we know what's available
    all_collections = list_all_collections(db)

    # Define target collections and their preferred timestamp fields
    targets = [
        ("orders",           ["createdAt", "created_at", "orderDate", "date"]),
        ("order",            ["createdAt", "created_at", "orderDate", "date"]),
        ("quotes",           ["createdAt", "created_at", "quoteDate", "date"]),
        ("calls",            ["createdAt", "created_at", "callDate", "date", "startTime"]),
        ("supplierrequests", ["createdAt", "created_at", "date", "requestDate"]),
        ("supplier_requests",["createdAt", "created_at", "date", "requestDate"]),
        ("contracts",        ["createdAt", "created_at", "date", "contractDate"]),
        ("contract",         ["createdAt", "created_at", "date", "contractDate"]),
    ]

    analyzed = set()
    for coll_name, ts_prefs in targets:
        # Check if collection exists (case-insensitive match)
        matched = None
        for ac in all_collections:
            if ac.lower() == coll_name.lower():
                matched = ac
                break
        if matched and matched not in analyzed:
            analyze_collection(db, matched, ts_prefs)
            analyzed.add(matched)

    # If none of the above matched, try fuzzy matches
    if not analyzed:
        print("\nNone of the target collections found by exact name.")
        print("Attempting to find collections containing 'order', 'call', 'supplier', 'contract'...")
        keywords = ["order", "call", "supplier", "contract", "quote", "deal"]
        for ac in all_collections:
            for kw in keywords:
                if kw in ac.lower() and ac not in analyzed:
                    analyze_collection(db, ac)
                    analyzed.add(ac)
                    break

    # ---- SUMMARY ----
    print_separator("=")
    print("  ANALYSIS COMPLETE")
    print_separator("=")
    print(f"  Collections analyzed: {len(analyzed)}")
    print(f"  Time window: Last 6 months (since {SIX_MONTHS_AGO.strftime('%Y-%m-%d')})")
    print(f"  Timezone: Eastern Time (UTC-5 approximation)")
    print()


if __name__ == "__main__":
    main()
