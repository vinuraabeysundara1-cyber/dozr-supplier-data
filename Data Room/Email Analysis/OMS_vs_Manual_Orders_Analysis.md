# OMS vs Manual Orders Analysis

**Generated:** February 12, 2026
**Data Source:** Metabase (Production MongoDB)
**Collection:** `supplierrequests`

---

## Executive Summary

Analysis of order fulfillment comparing OMS (automated) vs Manual processing for the last 90 days and previous 90 days.

---

## Current Period (Nov 14, 2025 - Feb 12, 2026)

### Requests Sent

| Type | Requests | % of Total |
|------|----------|------------|
| OMS (autoSelectAccounts=true) | 3,029 | 61.3% |
| Manual | 1,910 | 38.7% |
| **Total** | **4,939** | 100% |

### Booked Orders

| Type | Booked | % of Booked | Book Rate |
|------|--------|-------------|-----------|
| OMS | 137 | 21.2% | 4.5% |
| Manual | 509 | 78.8% | 26.6% |
| **Total** | **646** | 100% | 13.1% |

### OMS Request Status Breakdown

| Status | Count |
|--------|-------|
| booked | 137 |
| cancelled | 1,240 |
| declined | 542 |
| expired | 621 |
| next-in-line-available | 433 |
| oms-booked-then-cancelled | 19 |
| pending | 17 |
| active | 14 |
| order-lost | 5 |
| next-in-line | 1 |
| **Total OMS Requests** | **3,029** |

---

## Period Comparison (using autoSelectAccounts field)

### Last 90 Days vs Previous 90 Days

| Category | Previous 90d | Current 90d | Change |
|----------|--------------|-------------|--------|
| OMS (Auto-Select) | 268 (23.9%) | 135 (21.1%) | -49.6% |
| Manual | 854 (76.1%) | 506 (78.9%) | -40.7% |
| **Total Booked** | **1,122** | **641** | **-42.9%** |

### OMS Auto-Select Rate Trend

- Previous 90 days: 23.9%
- Current 90 days: 21.1%
- Change: -2.8 percentage points

---

## Key Metrics

| Metric | Value |
|--------|-------|
| OMS Book Rate | 4.5% |
| Manual Book Rate | 26.6% |
| Overall Book Rate | 13.1% |
| OMS Share of Booked Orders | 21.2% |
| Manual Share of Booked Orders | 78.8% |

---

## Data Field Definitions

| Field | Description |
|-------|-------------|
| `autoSelectAccounts` | Boolean - True indicates OMS automatically selected supplier accounts |
| `status.value` | Order status (booked, cancelled, declined, expired, etc.) |
| `status.time` | Timestamp when status was set |
| `status.respondedFrom` | Source of response (Supplier Hub, Graham, System Process, etc.) |
| `liteOMS` | Boolean - Indicates Lite OMS processing |

### Response Source Classification (status.respondedFrom)

| Source | Description |
|--------|-------------|
| Supplier Hub | Supplier responded via Supplier Hub portal |
| Graham | Manual entry via Graham admin interface |
| System Process | Automated system processing |
| Order Manager Tablet | OMS tablet responses |

---

## Notes

1. **OMS Book Rate vs Share of Booked Orders**:
   - OMS Book Rate (4.5%) = OMS orders booked / OMS requests sent
   - OMS Share of Booked (21.2%) = OMS orders booked / Total orders booked

2. **Data Discrepancy**: The `respondedFrom` field shows who responded to the order, not how it was initiated. The `autoSelectAccounts` field is a more accurate indicator of OMS vs Manual order initiation.

3. **Period Comparison**: Both periods show a significant decline in total orders (-42.9%), with OMS orders declining faster (-49.6%) than manual orders (-40.7%).

---

## Query Details

```javascript
// MongoDB Aggregation Pipeline Used
[
  {
    "$match": {
      "status.value": "booked",
      "status.time": {"$gte": {"$date": "2025-11-14T00:00:00.000Z"}}
    }
  },
  {
    "$group": {
      "_id": "$autoSelectAccounts",
      "count": {"$sum": 1}
    }
  }
]
```

---

*Analysis performed via Metabase API connected to Production MongoDB*
