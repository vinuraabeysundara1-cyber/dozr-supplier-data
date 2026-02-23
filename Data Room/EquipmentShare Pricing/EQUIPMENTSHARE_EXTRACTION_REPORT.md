# EquipmentShare.com Data Extraction Report

**Date**: February 23, 2026
**Location**: Houston, Texas
**Status**: Completed with limitations

## Summary

Successfully extracted equipment data from EquipmentShare.com across three categories. A total of **121 equipment items** were scraped and saved to JSON files.

## Extraction Results

### Categories Scraped

1. **Aerial Work Platforms** - 21 items
   - File: `equipmentshare_aerial.json`
   - Category URL: https://www.equipmentshare.com/rent/categories/aerial-work-platform

2. **Earthmoving** - 49 items
   - File: `equipmentshare_earthmoving.json`
   - Category URL: https://www.equipmentshare.com/rent/categories/earthmoving

3. **Forklifts & Material Handling** - 51 items
   - File: `equipmentshare_material_handling.json`
   - Category URL: https://www.equipmentshare.com/rent/categories/forklift-material-handling

**Total**: 121 equipment items

## Data Fields Extracted

For each equipment item, the following data was extracted:

### Successfully Extracted:
- ✓ **Equipment Name** - Full equipment name (e.g., "Electric Scissor Lift, 19' Narrow")
- ✓ **Category** - Main category classification
- ✓ **Brand/Model** - Manufacturer and model numbers (e.g., "MEC, JLG, GENIE (1930SE, ES1932, GS-1930)")
- ✓ **Specs** - Key specifications (Capacity, Max Working Height, Operating Weight, etc.)
- ✓ **URL** - Direct link to equipment detail page
- ✓ **Equipment Type** - Subcategory or type classification

### Limitation - Pricing Data:
- ✗ **price_daily** - Daily rental rate ($/day)
- ✗ **price_weekly** - Weekly rental rate ($/week)
- ✗ **price_monthly** - Monthly rental rate ($/4-week)

**Reason**: EquipmentShare.com loads pricing dynamically using JavaScript. The `requests` + `BeautifulSoup` approach cannot execute JavaScript, so pricing data shows as `null` in the JSON files.

## Technical Approach

### Method Used:
- Python 3.9
- Libraries: `requests`, `BeautifulSoup4`
- Script: `scrape_equipmentshare_simple.py`

### Process:
1. Fetched category pages using HTTP requests
2. Extracted all equipment URLs from each category
3. Filtered URLs based on keywords (for Aerial category only)
4. Visited each equipment detail page
5. Parsed HTML to extract equipment data
6. Saved results to JSON files

## Solutions for Pricing Data

To extract pricing data, one of the following approaches would be needed:

### Option 1: Selenium WebDriver (Recommended)
- Install ChromeDriver or use Selenium with Chrome
- Execute JavaScript to load dynamic content
- Script provided: `scrape_equipmentshare.py` (requires Selenium + ChromeDriver)

### Option 2: Browser Console Extraction
- Use the JavaScript extraction script in browser console
- Manual but works with location-specific pricing
- Can extract pricing for Houston, Texas location

### Option 3: API Inspection
- Inspect network requests to find pricing API endpoints
- Directly query the API for pricing data
- May require authentication or session tokens

## Files Delivered

1. **equipmentshare_aerial.json** - 21 aerial work platform equipment items
2. **equipmentshare_earthmoving.json** - 49 earthmoving equipment items
3. **equipmentshare_material_handling.json** - 51 forklift & material handling items
4. **equipmentshare_progress.txt** - Extraction progress summary
5. **scrape_equipmentshare_simple.py** - Python scraper script (requests + BS4)
6. **scrape_equipmentshare.py** - Advanced Selenium script (requires ChromeDriver)
7. **extract_equipmentshare.js** - Browser-based JavaScript extractor

## Data Quality

### Strengths:
- Complete equipment names and URLs
- Comprehensive brand/model information where available
- Detailed specifications for most equipment
- Proper categorization

### Limitations:
- Pricing data missing (requires JavaScript execution)
- Some cross-category equipment appears in multiple files
- Equipment type classification sometimes inconsistent

## Sample Data

### Example: Electric Scissor Lift, 19' Narrow

```json
{
  "url": "https://www.equipmentshare.com/rent/equipment-classes/electric-scissor-lift-19-narrow",
  "category": "Aerial Work Platforms",
  "name": "Electric Scissor Lift, 19' Narrow",
  "equipment_type": "Electric Scissor Lift",
  "price_daily": null,
  "price_weekly": null,
  "price_monthly": null,
  "brand_model": "MEC, JLG, GENIE (1930SE, ES1932, GS-1930)",
  "specs": "Capacity: 500 lbs, Max Working Height: 19 ft, Operating Weight: 3130 lbs"
}
```

### With Pricing (when extracted via browser):
```json
{
  "url": "https://www.equipmentshare.com/rent/equipment-classes/electric-scissor-lift-26-micro",
  "category": "Aerial Work Platforms",
  "name": "Electric Scissor Lift, 26' Micro",
  "equipment_type": "Electric Scissor Lift",
  "price_daily": 272,
  "price_weekly": 544,
  "price_monthly": 1087,
  "brand_model": "MEC (Micro 26)",
  "specs": "Capacity: 500 lbs, Max Working Height: 31 ft, Operating Weight: 4190 lbs"
}
```

## Next Steps

To complete the data extraction with pricing:

1. **Install ChromeDriver**:
   ```bash
   brew install chromedriver  # macOS
   ```

2. **Run Selenium Script**:
   ```bash
   python3 scrape_equipmentshare.py
   ```

3. **Or use browser extraction**:
   - Open browser console on EquipmentShare.com (Houston, TX location)
   - Load equipment URLs from JSON files
   - Extract pricing using JavaScript
   - Update JSON files with pricing data

## Conclusion

The extraction successfully captured **121 equipment items** across three major categories with comprehensive equipment details, specifications, and brand information. Pricing data requires JavaScript execution and can be added using Selenium or browser-based extraction.

---
**Generated**: February 23, 2026
**Location**: /Users/vinuraabeysundara/Desktop/ICG/DOZR/
