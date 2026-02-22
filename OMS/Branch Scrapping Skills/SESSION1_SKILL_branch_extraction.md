# Session 1: Supplier Branch Location Extraction

## Overview
Extract ALL branch locations for an equipment rental supplier across the US. Produce structured, OMS-ready data with full address, phone, and service details for every branch.

---

## Critical Rules

### 1. NEVER Summarize — Capture Every Row
```
❌ "Found approximately 500 branches across the US"
❌ "Supplier has locations in 42 states"
❌ "OMS ONLY - No web extraction (316 branches from OMS)"
✅ Save every individual branch as a JSON object with all fields
```
Every branch = one JSON entry. No estimates, no summaries, no aggregates until ALL individual records are captured.

### 2. ALWAYS Scrape the Website — Never Just Use OMS Data
You MUST navigate to the supplier's website and extract branch data from it. The whole point is to find branches that are NOT in the OMS. Reading the OMS CSV and reporting it as "done" is a failure.

### 3. Save Obsessively — Files Are Memory
- Save JSON after every **20 branches** or **every completed state**
- Save progress log after every search/page
- If the browser disconnects, all unsaved work is **lost forever**
- On resume: **READ files first**, then continue from where you left off
- **Never trust memory. Files are truth.**

### 4. Click Into Every Branch for Full Details
Do NOT just grab branch names from a map overview. For EVERY branch:
- Click the map pin or list entry
- Click through to the branch detail page if the popup is incomplete
- Record the full address, phone number, zip code, and services
- If the detail page has an email, hours, or manager name, capture those too

### 5. Handle Website Blocking Gracefully
If the supplier website blocks, errors, or loads slowly:
1. Wait 10 seconds, retry
2. Try an alternate URL pattern (see Fallback Methods below)
3. If still failing, **skip to next state/city**, log the failure
4. Retry all failures at the end
5. **Never stop entirely — always move forward**

---

## How to Use This Skill

Paste the following into Claude Code, replacing the placeholders:

```
You have access to my browser via the Claude extension.

SUPPLIER: [Supplier Name]
LOCATION PAGE: [URL to their store finder / locations page]
OMS CSV: [File path to the OMS CSV for this supplier]
OUTPUT PREFIX: [e.g., "herc", "sunstate", "homedepot"]

Follow the Session 1 skill instructions below to extract ALL branch locations.
```

Then paste the rest of this document.

---

## Step 1: Read the OMS Baseline

Read the OMS CSV first to understand what we already have:
```
- Count total OMS branches
- Count enabled vs disabled
- List which states are covered
- Note the data format (branch name pattern, address format)
```
Save parsed OMS data to `{prefix}_oms_branches.json` for cross-referencing later.

## Step 2: Analyze the Supplier's Location Page

Navigate to the supplier's location/store-finder URL. Determine which extraction method to use:

| Page Type | Method | Example |
|-----------|--------|---------|
| **Interactive Map** | Zoom into regions, click every pin | Sunbelt, Sunstate |
| **Search Bar (zip/city)** | Search systematically by zip code | Herc, Home Depot |
| **State Directory** | Click state → city → branch | Home Depot, EquipmentShare |
| **Full List/Table** | Scroll/paginate through all | EquipmentShare |
| **API Available** | Call API directly (check Network tab) | Check F12 → Network |

**Always check for an API first:** Open dev tools (F12 → Network tab), search for a location, look for XHR/Fetch calls to `/api/locations` or similar. APIs are 10x faster than clicking.

## Step 3: Extract Branches

### For Search Bar / Map Sites — Use This Zip Code List

Search EVERY zip code below. Record ALL branches that appear in each search.

**SOUTHEAST:**
33101 Miami, 32099 Jacksonville, 33601 Tampa, 32801 Orlando, 30303 Atlanta, 31401 Savannah, 28202 Charlotte, 27601 Raleigh, 37201 Nashville, 38103 Memphis, 35203 Birmingham, 36602 Mobile, 70112 New Orleans, 70801 Baton Rouge, 39201 Jackson, 29201 Columbia, 29401 Charleston SC, 23220 Richmond, 23510 Norfolk, 72201 Little Rock, 39501 Gulfport

**TEXAS & SOUTH CENTRAL:**
77001 Houston, 75201 Dallas, 78701 Austin, 78201 San Antonio, 76101 Fort Worth, 79901 El Paso, 78401 Corpus Christi, 79401 Lubbock, 79701 Midland, 73102 Oklahoma City, 74103 Tulsa, 64101 Kansas City, 63101 St Louis, 76701 Waco, 75701 Tyler, 77701 Beaumont, 79101 Amarillo

**WEST COAST:**
90001 Los Angeles, 94102 San Francisco, 92101 San Diego, 95814 Sacramento, 93721 Fresno, 93301 Bakersfield, 92501 Riverside, 98101 Seattle, 99201 Spokane, 98402 Tacoma, 97201 Portland, 97401 Eugene, 85004 Phoenix, 85701 Tucson, 84101 Salt Lake City, 89101 Las Vegas, 87101 Albuquerque, 80202 Denver, 96801 Honolulu

**NORTHEAST:**
10001 New York, 11201 Brooklyn, 14201 Buffalo, 12201 Albany, 07102 Newark, 07302 Jersey City, 19102 Philadelphia, 15222 Pittsburgh, 02101 Boston, 06103 Hartford, 21201 Baltimore, 20001 Washington DC, 19801 Wilmington, 03101 Manchester, 04101 Portland ME, 02901 Providence, 05401 Burlington, 25301 Charleston WV

**MIDWEST:**
60601 Chicago, 48226 Detroit, 43215 Columbus, 44113 Cleveland, 45202 Cincinnati, 46204 Indianapolis, 53202 Milwaukee, 55401 Minneapolis, 50301 Des Moines, 68102 Omaha, 58102 Fargo, 52401 Cedar Rapids, 52801 Davenport

**MOUNTAIN & RURAL:**
83701 Boise, 59101 Billings, 82001 Cheyenne, 57101 Sioux Falls, 99501 Anchorage, 99701 Fairbanks, 59801 Missoula, 57701 Rapid City

**SECONDARY CITIES (search after primary to catch suburbs):**
- TX: 75601 Longview, 76501 Temple, 77301 Conroe, 78130 New Braunfels
- CA: 95202 Stockton, 95354 Modesto, 96001 Redding, 93101 Santa Barbara, 93401 San Luis Obispo
- FL: 32501 Pensacola, 32401 Panama City, 32301 Tallahassee, 33901 Fort Myers, 34470 Ocala, 34952 Port St Lucie
- NY: 14604 Rochester, 13201 Syracuse, 12601 Poughkeepsie, 13901 Binghamton, 10601 White Plains
- OH: 43604 Toledo, 44503 Youngstown, 44702 Canton, 45501 Springfield
- PA: 16501 Erie, 18503 Scranton, 19601 Reading, 17101 Harrisburg, 17601 Lancaster
- IL: 61602 Peoria, 61820 Champaign, 61701 Bloomington, 62521 Decatur
- MI: 49007 Kalamazoo, 48601 Saginaw, 48502 Flint, 49684 Traverse City
- GA: 31901 Columbus, 31201 Macon, 30901 Augusta, 30601 Athens
- NC: 28401 Wilmington, 28801 Asheville, 27101 Winston-Salem, 28301 Fayetteville
- TN: 37902 Knoxville, 37402 Chattanooga, 37040 Clarksville, 37130 Murfreesboro
- MO: 65801 Springfield, 65201 Columbia, 64801 Joplin
- VA: 24011 Roanoke, 24501 Lynchburg, 22401 Fredericksburg, 22901 Charlottesville
- MD: 21701 Frederick, 21740 Hagerstown, 21801 Salisbury
- IN: 46601 South Bend, 47708 Evansville, 47401 Bloomington, 47901 Lafayette
- WI: 54301 Green Bay, 54911 Appleton, 54701 Eau Claire
- MN: 55901 Rochester, 55801 Duluth, 56301 St Cloud
- KS: 67202 Wichita, 66204 Overland Park, 66603 Topeka
- SC: 29601 Greenville, 29577 Myrtle Beach, 29301 Spartanburg
- KY: 40202 Louisville, 40507 Lexington, 42101 Bowling Green, 41042 Florence
- NJ: 08002 Cherry Hill, 08753 Toms River, 08401 Atlantic City, 08817 Edison

### For Directory-Based Sites
Use direct URL patterns when available:
```
https://www.supplier.com/locations/[STATE]
https://www.supplier.com/l/[STATE]
https://www.supplier.com/l/storeDirectory
```
Click through every state → every city → every branch.

## Step 4: Data Format

For EVERY branch, capture:

```json
{
  "branch_name": "Supplier Name - City",
  "branch_number": "1234",
  "address": "123 Main St",
  "city": "Houston",
  "state": "TX",
  "zip": "77001",
  "phone": "(713) 555-1234",
  "email": "branch@supplier.com",
  "services": ["General Rentals", "Aerial", "Earthmoving"],
  "hours": "Mon-Fri 7:00-17:00",
  "relevant_to_dozr": true,
  "source": "Website"
}
```

**Required (never leave blank without trying):** branch_name, address, city, state, phone
**Important:** zip, services, branch_number, email, hours

## Step 5: Persistence

```
# File structure:
{prefix}_branches.json            # Array of all branch objects
{prefix}_progress.txt             # Search-by-search log
{prefix}_retry_list.json          # Failed searches to retry

# Progress log format:
Region: Southeast
  33101 (Miami FL) - searched, 5 branches found - DONE
  32099 (Jacksonville FL) - searched, 3 branches found - DONE
  33601 (Tampa FL) - CONNECTION ERROR - added to retry
  ...
CHECKPOINT: 150 branches captured across 12 states
```

Save JSON after every **20 branches** or every completed state.
Save progress log after every search.

## Step 6: Deduplication

After all searches, remove duplicate branches:
- Primary key: branch_number (if available)
- Fallback key: full address (street + city + state)
- Log: "Removed 23 duplicates, 412 unique branches remain"

## Step 7: Cross-Reference with OMS

Read the OMS CSV. Match branches by:
1. Branch number (if present in both)
2. Street number + city name
3. Normalized address similarity

Classify each:
- **MATCHED** — in both OMS and website
- **NEW — ADD TO OMS** — on website but NOT in OMS
- **OMS ONLY — VERIFY** — in OMS but not found on website

## Step 8: Final Output

Create `{prefix}_branch_database.xlsx`:

| Sheet | Contents |
|-------|----------|
| **Summary** | Total counts, key findings |
| **All Branches** | Every unique branch, sorted State → City |
| **New to Add to OMS** | Only branches NOT in OMS — this is the deliverable |
| **Already in OMS** | Matched branches (confirmation) |
| **State Summary** | Per-state: Website count, OMS count, New, Matched |

## Step 9: Validation

Before creating the Excel:
- [ ] JSON has branches in **30+ states** (national suppliers) or expected state count (regional)
- [ ] **90%+ rows have phone numbers** — if not, go back and click into branch details
- [ ] **90%+ rows have full street addresses** — if not, use Google Maps to fill gaps
- [ ] **No duplicates remain**
- [ ] Cross-reference math adds up: matched + new + OMS-only = total unique

---

## Fallback Methods (when primary site fails)

1. **API discovery:** F12 → Network → search a location → look for API calls
2. **Google Maps:** Search `"[Supplier]" [city], [state]` — shows address, phone, hours
3. **Google Search:** `[Supplier] locations [state]` — may find state-specific pages
4. **USPS Zip Lookup:** `tools.usps.com/zip-code-lookup.htm` — fill missing zips from addresses
5. **Yelp/Yellow Pages:** Search supplier name for branches with contacts

---

## Resume Protocol

If interrupted (rate limit, disconnect, error), paste this:

> **"Read all existing JSON and progress files in your working directory for [SUPPLIER]. Print what's been captured — how many branches, which states are done. Then continue from where you left off at [LOCATION URL]."**

---

## Common Mistakes to Avoid

| Mistake | What Happens | Prevention |
|---------|-------------|------------|
| Only grabbing names from map | 0% phone numbers, 30%+ missing addresses | Click into EVERY branch detail page |
| Using OMS data as "complete" | Misses all new branches (the whole point) | Prompt explicitly says DO NOT just use OMS |
| Not saving frequently | Browser disconnect = total data loss | Save after every 20 branches |
| Skipping secondary cities | Miss 30-40% of suburban branches | Use the full zip code list including secondaries |
| Stopping on website errors | Miss entire regions | Skip + log + retry later |
| Summarizing instead of recording | No usable data rows | "Every branch = one JSON object" |
