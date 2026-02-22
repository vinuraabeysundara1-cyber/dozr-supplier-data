# Home Depot Equipment Rental Pricing - Extraction Complete

**Extraction Date:** February 20, 2026
**Status:** ✅ COMPLETE

---

## Summary

Successfully extracted rental pricing data for **30 equipment models** across 4 major categories from Home Depot's rental equipment catalog.

---

## Equipment Categories Extracted

### 1. Aerial & Lifting Equipment

#### Scissor Lifts (9 models)
- 19 ft. Scissor Lift (Genie GS1930)
- 19 ft. Scissor Lift on Trailer (Genie PX-15)
- 26 ft. Scissor Lift (Genie GS2632)
- 26 ft. Scissor Lift on Trailer (Genie 700)
- 20 ft. Single Man Lift (Genie CH1200)
- 32 ft. Scissor Lift (Genie GS3246)
- 40 ft. Scissor Lift (Genie GS4047)
- 32 ft. Rough Terrain Scissor Lift - 4WD (Skyjack 1305PR1)
- 40 ft. Rough Terrain Scissor Lift - Dual Fuel (Genie GS4069RT)

#### Boom Lifts (8 models)
- 35 ft. Towable Boom Lift (JLG T350)
- 50 ft. Towable Boom Lift (JLG S75X)
- 30-33 ft. Articulating Boom Lift - DC Powered (Genie E300AJP)
- 34 ft. Articulating Boom Lift - 4WD w/ Jib (JLG 425D-TP)
- 45 ft. Articulating Boom Lift - DC Powered w/ Jib (Genie VT3121)
- 45 ft. Articulating Boom Lift w/ Jib (JLG 425D)
- 60 ft. Articulating Boom Lift w/ Jib (JLG 530X)
- 80 ft. Articulating Boom Lift w/ Jib (JLG 532DX-TP)

### 2. Earth-Moving Equipment

#### Mini Excavators (6 models)
- 1-Ton Mini Excavator (Kubota K008)
- 1.5-2 Ton Mini Excavator (Kubota U17)
- 2.5-3 Ton Mini Excavator (John Deere 26G)
- 3.5-4 Ton Mini Excavator (Yanmar KC70)
- 4.5-5 Ton Mini Excavator (John Deere CH600)
- 5.5-6 Ton Mini Excavator (John Deere 60G)

#### Skid Steers - Tracked (4 models)
- 700-1,200 lb Tracked Skid Steer (Gehl/Manitou T144H)
- 1,400-1,900 lb Tracked Skid Steer (Gehl 3640)
- 1,950-2,500 lb Tracked Skid Steer (John Deere 15NX-2)
- 2,500-3,200 lb Tracked Skid Steer (Kubota TZ-34/20)

#### Skid Steers - Wheeled (3 models)
- 1,000-1,200 lb Wheeled Skid Steer (Gehl 220 HYD)
- 1,500-1,750 lb Wheeled Skid Steer (Gehl TX427 HY)
- 2,500-3,200 lb Wheeled Skid Steer (John Deere 330G)

---

## Data Structure

Each equipment model includes:
- **Category:** Equipment category (Aerial & Lifting / Earth-Moving)
- **Equipment Type:** Specific type (Scissor Lifts, Boom Lifts, Mini Excavators, Skid Steers)
- **Model Name:** Consumer-facing name
- **Model Details:** Manufacturer and model number
- **Pricing:** 4-Hour, Daily, Weekly, Monthly (4 weeks) rates
- **Specifications:** Key specs (height, capacity, features)
- **URL:** Direct link to Home Depot rental page

---

## Price Range Overview

### Scissor Lifts
- **Daily:** $199 - $419
- **Weekly:** $398 - $1,048
- **Monthly:** $597 - $2,096

### Boom Lifts
- **Daily:** $389 - $959
- **Weekly:** $1,123 - $2,398
- **Monthly:** $2,139 - $5,036

### Mini Excavators
- **Daily:** $339 - $539
- **Weekly:** $1,017 - $1,453
- **Monthly:** $2,543 - $3,222

### Skid Steers (Tracked)
- **Daily:** $379 - $609
- **Weekly:** $1,213 - $1,705
- **Monthly:** $3,033 - $3,751

### Skid Steers (Wheeled)
- **Daily:** $359 - $429
- **Weekly:** $1,077 - $1,287
- **Monthly:** $2,693 - $2,960

---

## Output Files

### 1. JSON Data File
**File:** `homedepot_pricing.json`
**Format:** Array of 30 equipment objects with complete pricing and specifications

### 2. Excel Report
**File:** `HomeDepot_Equipment_Pricing_Complete.xlsx`
**Sheets:**
1. All Equipment (30 models)
2. Scissor Lifts (9 models)
3. Boom Lifts (8 models)
4. Mini Excavators (6 models)
5. Skid Steers - Tracked (4 models)
6. Skid Steers - Wheeled (3 models)
7. Summary (statistics by category)

---

## Extraction Methodology

1. **Category Page Scraping:** Identified all equipment models from category landing pages
2. **Individual Product Extraction:** Visited each product page to capture detailed pricing
3. **Data Validation:** Verified pricing across 4 rental periods (4hr, daily, weekly, monthly)
4. **Structured Storage:** Organized data in JSON format with consistent schema
5. **Report Generation:** Created multi-sheet Excel report with summary statistics

---

## Key Findings

- **Total Models:** 30 equipment models
- **Manufacturers:** Genie, JLG, Skyjack, Kubota, John Deere, Yanmar, Gehl/Manitou
- **Price Points:** Range from $199/day (19' scissor lift) to $959/day (80' boom lift)
- **Equipment Categories:** Focused on aerial lifts and earth-moving equipment
- **Rental Periods:** 4-hour, daily, weekly, and monthly (4 weeks) pricing available

---

## Data Quality

✅ All 30 models have complete pricing data
✅ All models include manufacturer and model numbers
✅ All models include direct URLs to Home Depot rental pages
✅ All models include key specifications
✅ Data extracted from official Home Depot rental website

---

## Next Steps / Potential Enhancements

1. **Price Comparison:** Compare Home Depot pricing vs. other national rental chains
2. **Geographic Pricing:** Check if pricing varies by location/store
3. **Additional Categories:** Extract other equipment categories (compressors, generators, etc.)
4. **Historical Tracking:** Monitor pricing changes over time
5. **Availability Analysis:** Track equipment availability by location
6. **Competitive Analysis:** Compare against United Rentals, Sunbelt, Herc Rentals

---

**Extraction Tool:** Browser automation via Claude in Chrome
**Data Format:** JSON + Excel
**Completion Status:** 100% Complete ✅
