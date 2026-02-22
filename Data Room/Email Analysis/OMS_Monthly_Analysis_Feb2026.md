# OMS Supplier Request Analysis - February 2026

**Report Generated:** February 15, 2026
**Data Source:** Metabase (Production MongoDB - supplierrequests collection)
**Period:** Last 90 Days (November 17, 2025 - February 15, 2026)

---

## Executive Summary

Over the past 90 days, DOZR's OMS processed **5,074 supplier requests** with a **12.8% book rate** (648 orders booked). The book rate showed improvement from November (11.6%) to January (13.4%), indicating positive momentum in OMS performance.

---

## Monthly Performance Summary

| Month | Total Requests | Booked | Book Rate | MoM Change |
|-------|----------------|--------|-----------|------------|
| November 2025 | 988 | 115 | 11.6% | - |
| December 2025 | 1,566 | 201 | 12.8% | +1.2 pts |
| January 2026 | 1,590 | 213 | 13.4% | +0.6 pts |
| February 2026* | 930 | 119 | 12.8% | -0.6 pts |
| **TOTAL** | **5,074** | **648** | **12.8%** | - |

*February 2026 is month-to-date (15 days)

---

## Detailed Status Breakdown by Month

### November 2025
| Status | Count | % of Total |
|--------|-------|------------|
| cancelled | 244 | 24.7% |
| expired | 180 | 18.2% |
| active | 146 | 14.8% |
| declined | 143 | 14.5% |
| booked | 115 | 11.6% |
| order-lost | 93 | 9.4% |
| next-in-line-available | 51 | 5.2% |
| oms-booked-then-cancelled | 14 | 1.4% |
| pending | 2 | 0.2% |
| **Total** | **988** | **100%** |

### December 2025
| Status | Count | % of Total |
|--------|-------|------------|
| cancelled | 438 | 28.0% |
| active | 266 | 17.0% |
| expired | 208 | 13.3% |
| booked | 201 | 12.8% |
| declined | 178 | 11.4% |
| next-in-line-available | 133 | 8.5% |
| order-lost | 108 | 6.9% |
| oms-booked-then-cancelled | 23 | 1.5% |
| pending | 10 | 0.6% |
| next-in-line | 1 | 0.1% |
| **Total** | **1,566** | **100%** |

### January 2026
| Status | Count | % of Total |
|--------|-------|------------|
| cancelled | 394 | 24.8% |
| active | 277 | 17.4% |
| booked | 213 | 13.4% |
| expired | 196 | 12.3% |
| declined | 174 | 10.9% |
| next-in-line-available | 170 | 10.7% |
| order-lost | 135 | 8.5% |
| oms-booked-then-cancelled | 24 | 1.5% |
| pending | 7 | 0.4% |
| **Total** | **1,590** | **100%** |

### February 2026 (Month-to-Date)
| Status | Count | % of Total |
|--------|-------|------------|
| cancelled | 199 | 21.4% |
| active | 174 | 18.7% |
| declined | 139 | 14.9% |
| next-in-line-available | 130 | 14.0% |
| booked | 119 | 12.8% |
| expired | 97 | 10.4% |
| order-lost | 53 | 5.7% |
| oms-booked-then-cancelled | 10 | 1.1% |
| pending | 9 | 1.0% |
| **Total** | **930** | **100%** |

---

## Status Definitions

| Status | Description |
|--------|-------------|
| **booked** | Order successfully booked via OMS |
| **cancelled** | Supplier request was cancelled |
| **expired** | Request expired without supplier response |
| **declined** | Supplier declined the request |
| **active** | Request currently active/pending |
| **order-lost** | Order went to competitor or was lost |
| **next-in-line-available** | Next supplier in queue is available |
| **oms-booked-then-cancelled** | Initially booked via OMS, later cancelled |
| **pending** | Awaiting processing |
| **next-in-line** | Queued for next available supplier |

---

## Key Insights

### 1. Book Rate Trend
- Book rate improved **1.8 percentage points** from November (11.6%) to January (13.4%)
- January 2026 achieved the highest book rate in the 90-day period
- February tracking at 12.8%, consistent with overall average

### 2. Volume Analysis
- December and January saw highest request volumes (~1,550-1,590 requests)
- November had lower volume (988), possibly due to partial month in dataset
- February on pace for ~1,800+ requests if current rate continues

### 3. Cancellation Analysis
- Cancellation rate ranges from 21-28% across months
- December had highest cancellation rate (28.0%)
- February showing improvement with lowest cancellation rate (21.4%)

### 4. Expired Requests
- Expired requests trending down: 18.2% (Nov) → 13.3% (Dec) → 12.3% (Jan) → 10.4% (Feb)
- Indicates improved supplier response times or better request targeting

### 5. Lost Orders
- Order-lost rate: 9.4% (Nov) → 6.9% (Dec) → 8.5% (Jan) → 5.7% (Feb)
- February showing best performance in retaining orders

---

## 90-Day Totals by Status

| Status | Count | % of Total |
|--------|-------|------------|
| cancelled | 1,275 | 25.1% |
| active | 863 | 17.0% |
| expired | 681 | 13.4% |
| **booked** | **648** | **12.8%** |
| declined | 634 | 12.5% |
| next-in-line-available | 484 | 9.5% |
| order-lost | 389 | 7.7% |
| oms-booked-then-cancelled | 71 | 1.4% |
| pending | 28 | 0.6% |
| next-in-line | 1 | 0.0% |
| **TOTAL** | **5,074** | **100%** |

---

## Recommendations

1. **Reduce Cancellations** - At 25% of all requests, cancellations represent the largest opportunity. Investigate root causes (pricing, availability, timing).

2. **Improve Expiration Rate** - 13.4% of requests expire. Consider:
   - Shorter expiry windows
   - Better supplier matching
   - Automated follow-ups

3. **Address Declined Requests** - 12.5% declined rate suggests opportunity for better supplier-request matching or pricing alignment.

4. **Maintain January Momentum** - January's 13.4% book rate shows potential. Analyze what drove improvement.

---

*Report generated via Metabase API query on Production MongoDB*
