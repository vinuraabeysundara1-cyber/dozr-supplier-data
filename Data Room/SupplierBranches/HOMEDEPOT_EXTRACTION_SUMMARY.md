# Home Depot Equipment Pricing Extraction - Summary Report

**Generated:** February 20, 2026
**Project:** DOZR Supplier Analysis
**Location:** West Albuquerque #3504

---

## Executive Summary

Successfully extracted rental pricing for **9 Scissor Lift models** from Home Depot's rental equipment catalog. Identified additional equipment categories (Boom Lifts, Mini Excavators, Skid Steers) with URLs ready for extraction.

---

## Completed Extractions

### Scissor Lifts (9 Models) ✓

| Model | Model Details | 4-Hour | Daily | Weekly | Monthly |
|-------|--------------|--------|-------|--------|---------|
| 19 ft. Scissor Lift | Genie GS1930 | $199 | $199 | $398 | $597 |
| 19 ft. Scissor Lift on Trailer | Genie PX-15 | $239 | $239 | $717 | $1,793 |
| 26 ft. Scissor Lift | Genie GS2632 | $259 | $259 | $518 | $932 |
| 26 ft. Scissor Lift on Trailer | Genie 700 | $299 | $299 | $897 | $2,243 |
| 20 ft. Single Man Lift | Genie CH1200 | $229 | $229 | $435 | $870 |
| 32 ft. Scissor Lift | Genie GS3246 | $309 | $309 | $649 | $1,298 |
| 40 ft. Scissor Lift | Genie GS4047 | $419 | $419 | $880 | $1,848 |
| 32 ft. Rough Terrain Scissor Lift - 4WD | Skyjack 1305PR1 | $369 | $369 | $812 | $1,624 |
| 40 ft. Rough Terrain Scissor Lift - Dual Fuel | Genie GS4069RT | $419 | $419 | $1,048 | $2,096 |

**Average Scissor Lift Pricing:**
- 4-Hour: $304
- Daily: $304
- Weekly: $706
- Monthly: $1,483

---

## Identified Equipment (URLs Ready for Extraction)

### Boom Lifts (8 Models)

**Towable Booms (2):**
1. 35 ft. Towable Boom Lift (JLG T350) - [URL](https://www.homedepot.com/p/rental/JLG-35-Towable-Boom-Lift-Rental-T350/316821960)
2. 50 ft. Towable Boom Lift (S75X) - [URL](https://www.homedepot.com/p/rental/50-Towable-Boom-Lift-Rental-S75X/316821658)

**Articulating Booms (6):**
3. 30-33 ft. Articulating Boom Lift - DC (Genie E300AJP) - [URL](https://www.homedepot.com/p/rental/Genie-30-33-ft-Articulating-Boom-Lift-E300AJP/328503707)
4. 34 ft. Articulating Boom Lift - 4WD (JLG 425D-TP) - [URL](https://www.homedepot.com/p/rental/JLG-34-Articulating-Boom-Lift-w-Jib-Rental-425D-TP/316821508)
5. 45 ft. Articulating Boom Lift - DC (Genie VT3121) - [URL](https://www.homedepot.com/p/rental/Genie-45-Articulating-Boom-Lift-w-Jib-Rental-VT3121/316821584)
6. 45 ft. Articulating Boom Lift (JLG 425D) - [URL](https://www.homedepot.com/p/rental/JLG-45-Articulating-Boom-Lift-w-Jib-Rental-425D/316821569)
7. 60 ft. Articulating Boom Lift (530X) - [URL](https://www.homedepot.com/p/rental/60-Articulating-Boom-Lift-w-Jib-Rental-530X/316821695)
8. 80 ft. Articulating Boom Lift (JLG 532DX-TP) - [URL](https://www.homedepot.com/p/rental/80-Articulating-Boom-Lift-w-Jib-Rental-532DX-TP/316821726)

### Mini Excavators (TBD)
**Category Page:** https://www.homedepot.com/c/mini-excavator-rental
**Action:** Navigate to page and extract all product URLs

### Skid Steers (TBD)
**Category Page:** https://www.homedepot.com/c/skid-steer-rental
**Action:** Navigate to page and extract all product URLs

---

## Output Files

1. **homedepot_pricing.json** - JSON array with 9 extracted scissor lift records
2. **homedepot_equipment_pricing.xlsx** - Excel report with 3 sheets:
   - Sheet 1: All Equipment
   - Sheet 2: Scissor Lifts (detailed view)
   - Sheet 3: Summary Statistics
3. **homedepot_pricing_progress.txt** - Detailed progress log with all URLs
4. **HOMEDEPOT_EXTRACTION_SUMMARY.md** - This summary document

---

## Key Insights

### Pricing Patterns (Scissor Lifts)
- **Entry Level** (19-20 ft): $199-$229 daily
- **Mid Range** (26-32 ft): $259-$369 daily
- **Large Models** (40 ft): $419 daily
- **Specialty** (Rough Terrain, Trailers): Premium pricing

### Equipment Manufacturers
- **Genie:** Dominant supplier (7 of 9 models)
- **Skyjack:** Rough terrain specialist (1 model)
- Other brands identified in Boom Lifts: JLG

### Rental Period Multipliers
- Weekly Rate: ~2.3x daily rate
- Monthly Rate: ~4.9x daily rate
- 4-Hour Rate: Typically matches daily rate

---

## Next Steps

### Immediate Actions:
1. Extract pricing for 8 identified Boom Lift models
2. Navigate to Mini Excavator category and identify all models
3. Extract pricing for all Mini Excavator models
4. Navigate to Skid Steer category and identify all models
5. Extract pricing for all Skid Steer models
6. Update Excel report with complete dataset

### Estimated Completion:
- Boom Lifts: 8 models × 2 min = 16 minutes
- Mini Excavators: Est. 6-8 models × 2 min = 12-16 minutes
- Skid Steers: Est. 4-6 models × 2 min = 8-12 minutes
- **Total:** ~40-50 minutes additional work

---

## Technical Notes

### Extraction Methodology:
1. Navigate to product URL
2. Wait 2 seconds for page load
3. Screenshot verification
4. Extract: Model name, specs, all four pricing tiers
5. Save to JSON format

### Data Structure:
```json
{
  "category": "Aerial & Lifting Equipment",
  "equipment_type": "Scissor Lifts",
  "model_name": "19 ft. Scissor Lift",
  "model_details": "Genie GS1930",
  "price_4hr": 199,
  "price_daily": 199,
  "price_weekly": 398,
  "price_monthly": 597,
  "specs": "Max platform height: 19', Max platform lift weight: 500 lbs",
  "url": "https://..."
}
```

### Location Note:
All pricing is for **West Albuquerque #3504**. Pricing may vary by location.

---

## Project Context

This extraction supports DOZR's supplier analysis comparing Home Depot's rental equipment against:
- Sunbelt Rentals
- Herc Rentals
- Equipment Share
- United Rentals
- Other major rental suppliers

Data will be used for competitive pricing analysis and market positioning strategy.

---

**Status:** Partial Completion (35% - Scissor Lifts Complete)
**Files Ready:** JSON, Excel, Progress Log
**Next Phase:** Boom Lifts, Excavators, Skid Steers
