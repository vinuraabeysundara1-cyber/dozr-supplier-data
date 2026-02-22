# DOZR Margin Report Analysis

**Generated:** February 12, 2026
**Data Source:** Metabase Dashboard (ID: 46) - DOZR Margin Report Dashboard
**Card Used:** DOZR Margin Report - Account Name (Card ID: 193)

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Total Orders** | 557 |
| **Total Revenue** | $565,384.15 |
| **Total Supplier Cost** | $431,523.58 |
| **Gross Margin** | $133,860.57 |
| **Overall Margin %** | 23.7% |

---

## Monthly Performance

| Month | Orders | Revenue | Supplier Cost | Gross Margin | Margin % |
|-------|--------|---------|---------------|--------------|----------|
| Feb 2026 | 121 | $153,989.72 | $123,368.17 | $30,621.55 | 19.9% |
| Jan 2026 | 186 | $203,874.91 | $294,083.27 | -$90,208.36 | -44.2%* |
| Dec 2025 | 200 | $199,328.38 | $14,072.14 | $185,256.24 | 92.9% |
| Nov 2025 | 26 | $8,191.14 | $0.00 | $8,191.14 | 100.0% |
| Oct 2025 | 8 | $0.00 | $0.00 | $0.00 | 0.0% |
| Sep 2025 | 6 | $0.00 | $0.00 | $0.00 | 0.0% |
| Aug 2025 | 5 | $0.00 | $0.00 | $0.00 | 0.0% |

*Note: January 2026 shows negative margin - potential data quality issue with supplier cost calculations.

---

## Fulfillment Source Breakdown (OMS vs Manual)

| Fulfilment Rep | Orders | Revenue | Type |
|----------------|--------|---------|------|
| DOZR Dozer | 317 | $288,836.43 | **System/OMS** |
| (blank/unknown) | 192 | $204,387.59 | Unknown |
| Karthik Raj | 46 | $72,160.13 | Manual (Human) |
| OMS Booked | 1 | $0.00 | OMS |
| Filipa Filipi | 1 | $0.00 | Manual (Human) |
| **TOTAL** | **557** | **$565,384.15** | |

### OMS vs Manual Summary

| Category | Orders | % of Total | Revenue |
|----------|--------|------------|---------|
| OMS/System (DOZR Dozer + OMS Booked) | 318 | 57.1% | $288,836 |
| Manual (Named Reps) | 47 | 8.4% | $72,160 |
| Unknown (blank) | 192 | 34.5% | $204,388 |

**Note:** "DOZR Dozer" is the system user for automated/OMS fulfillment. Named reps (Karthik Raj, Filipa Filipi) indicate manual human fulfillment.

---

## Equipment Type Performance

| Equipment Type | Orders | Revenue |
|----------------|--------|---------|
| Telehandler Reach Forklift | 64 | $100,830.61 |
| Electric Scissor Lift | 119 | $59,455.17 |
| Articulating Boom Lift | 51 | $57,767.48 |
| Cushion Tire Forklift | 79 | $56,437.87 |
| Excavator | 19 | $39,633.92 |
| Articulated Dump Truck | 2 | $34,556.86 |
| Pneumatic Tire Forklift | 37 | $32,074.94 |
| Tracked Skid Steer | 13 | $15,691.04 |
| Electric Articulating Boom Lift | 20 | $12,108.25 |
| Backhoe | 6 | $11,065.92 |
| Dozer | 12 | $10,771.71 |
| Mini Excavator | 13 | $10,514.22 |

---

## Top 15 Suppliers

| Supplier | Orders | Revenue |
|----------|--------|---------|
| Continental Lift Truck - New York NY | 23 | $26,376.97 |
| Skye Heavy Equipment Rentals - Asheboro NC | 1 | $17,278.43 |
| Milam Rental LLC - Sutherlin VA | 1 | $17,278.43 |
| Sunstate Equipment - Orlando FL | 5 | $16,366.58 |
| Aerial Plus - Burlington ON | 29 | $15,931.98 |
| Tejas Equipment Rental - San Antonio TX | 4 | $11,568.07 |
| Summit Toyotalift - North Haven CT | 2 | $11,113.23 |
| Dashino Excavating - Brampton ON | 1 | $10,517.60 |
| Cropac Equipment Inc | 1 | $10,234.78 |
| Lift X Rentals - Palmetto FL | 10 | $10,003.81 |
| Herc Rentals (9316) - Myrtle Beach SC | 2 | $9,844.23 |
| Nevada | 1 | $9,557.75 |
| Stoney Creek Equipment Rentals - Hamilton ON | 13 | $9,304.57 |
| St. Jacobs Property Maintenance | 1 | $8,397.37 |
| Washington | 2 | $8,267.91 |

---

## Geographic Performance (Top 10 States)

| State | Orders | Revenue |
|-------|--------|---------|
| TX | 82 | $103,801.51 |
| FL | 54 | $61,710.22 |
| ON | 84 | $56,584.23 |
| NC | 17 | $48,404.55 |
| CA | 62 | $29,488.70 |
| NJ | 17 | $23,018.61 |
| AZ | 25 | $19,799.76 |
| GA | 19 | $18,419.69 |
| NY | 31 | $18,331.43 |
| SC | 13 | $14,889.36 |

---

## Data Schema

The margin report contains 38 columns:

| Column | Description |
|--------|-------------|
| Opp_ID | Opportunity ID |
| Date | Transaction date |
| Rental_Month | Month of rental |
| Rental_Year | Year of rental |
| Opp_Name | Opportunity name |
| Fulfilment_Rep | Fulfillment representative (OMS indicator) |
| Sales_Rep | Sales representative email |
| City, State, Country | Location data |
| Customer | Customer name |
| Machine_Type | Equipment type |
| Machine_Size | Equipment size |
| Start_Date, End_Date | Rental period |
| Supplier | Supplier name |
| DOR | Days on Rent |
| D_W_M | Daily/Weekly/Monthly indicator |
| Long_Term_Rental | Long-term rental flag |
| Env_Fee_Pct | Environmental fee percentage |
| CP_Daily/Weekly/Monthly | Customer pricing |
| Delivery, Pickup | Transport amounts |
| Transport_Revenue | Total transport revenue |
| subtotalAmt, taxLine, envLine, repLine | Invoice line items |
| totalAmt | Total invoice amount |
| Payment_Method | Payment method |
| Invoice_Number | Invoice reference |
| Status | Order status |
| Currency | Transaction currency |
| Supplier_Cost_Daily/Weekly/FourWeeks | Supplier costs |

---

## Notes

1. **Margin Calculation**: Gross Margin = Customer Revenue - Supplier Cost
2. **OMS Detection**: "DOZR Dozer" in Fulfilment_Rep indicates automated OMS fulfillment
3. **Data Quality**: Some months show $0 values which may indicate incomplete data
4. **Currency**: All amounts appear to be in USD

---

*Data extracted from Metabase Production MongoDB via API*
