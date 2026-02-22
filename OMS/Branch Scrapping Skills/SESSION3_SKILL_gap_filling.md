# Session 3: Fill Missing Data (Phones, Addresses, Emails)

## Overview
You already have branch data from a previous scrape, but some records are missing phone numbers, addresses, or other fields. This skill fills those gaps by going back to the supplier website or using Google Maps.

---

## When to Use This Skill
- Branch records exist but have missing phone numbers
- Branch records have city/state but no street address
- Branch records are missing zip codes, emails, or hours
- You need to enrich existing data, NOT scrape new branches

**If you need to find NEW branches → use Session 1**
**If you need equipment pricing or contacts → use Session 2**
**If you need to fill gaps in EXISTING data → use this (Session 3)**

---

## How to Use

Paste into Claude Code:

```
You have access to my browser via the Claude extension.

TASK: Fill missing data for [SUPPLIER NAME]
DATA FILE: [path to the Excel or JSON with incomplete data]
SUPPLIER WEBSITE: [URL to their locations page]
OUTPUT PREFIX: [e.g., "herc", "sunbelt"]

Here's what's missing:
- [X] rows missing phone numbers
- [X] rows missing addresses
- [X] rows missing [other field]

Follow the Session 3 gap-fill skill below.
```

---

## Critical Rules

### 1. Read the Existing Data First
Before doing ANYTHING, read the Excel/JSON file and print:
- Total rows
- How many are missing each field (phone, address, zip, email)
- Sample of 5 incomplete rows so you know what you're working with

### 2. Don't Re-Scrape Complete Records
Skip rows that already have all required fields. Only visit pages for rows with gaps.

### 3. Save After Every 20 Rows Filled
Same persistence rules as always. Files are memory.

---

## Method 1: Supplier Website (Best for Phones + Addresses)

1. Navigate to the supplier's location page
2. For each branch missing data:
   a. Search for the branch by city name or zip code
   b. Click the branch listing
   c. Click into the branch detail page
   d. Record the missing field(s)
3. Save to `{prefix}_gap_fills.json`

```json
{
  "branch_name": "Sunbelt Rentals - Houston Hempstead",
  "original_city": "Houston",
  "original_state": "TX",
  "phone_filled": "(713) 555-1234",
  "address_filled": "12416 Hempstead Rd",
  "zip_filled": "77092",
  "source": "Supplier Website"
}
```

## Method 2: Google Maps (Best Fallback, Works for Everything)

If the supplier website blocks you or doesn't show the data:

1. Go to https://www.google.com/maps
2. Search: `"[Supplier Name]" [city], [state]`
   - Example: `"Sunbelt Rentals" Houston, TX`
3. Google Maps shows: full address, phone number, hours, reviews
4. Click the listing for full details
5. Record the missing fields

**This is often faster than navigating the supplier's own website.**

## Method 3: Google Search (For Emails + Manager Names)

Search: `[Supplier Name] [city] [state] phone` or `[Supplier Name] [city] contact`

Useful for finding:
- Branch-specific email addresses
- Manager names (from LinkedIn, press releases)
- Alternate phone numbers

## Method 4: USPS Zip Code Lookup (For Missing Zips Only)

If you have street addresses but no zip codes:

1. Go to https://tools.usps.com/zip-code-lookup.htm
2. Enter: street address, city, state
3. It returns the exact zip code

**Fastest method for bulk zip code fills when you already have addresses.**

---

## Persistence

```
# Files:
{prefix}_gap_fills.json          # All filled data
{prefix}_gap_progress.txt        # Row-by-row tracking

# Progress format:
Supplier: Sunbelt Rentals
Total rows to fix: 91 missing phones, 71 missing zips

Phone fills:
  Row 1: Sunbelt Houston - Hempstead → (713) 555-1234 - DONE
  Row 2: Sunbelt Houston - Lamar → (713) 555-5678 - DONE
  Row 3: Sunbelt Dallas - Hampton → WEBSITE ERROR → trying Google Maps
  Row 3: Sunbelt Dallas - Hampton → (214) 555-9012 via Google Maps - DONE
  ...
CHECKPOINT: 45/91 phones filled
```

Save JSON after every 20 rows filled.

---

## Output

Create `{prefix}_data_gaps_filled.xlsx`:

| Sheet | Contents |
|-------|----------|
| **Filled Data** | All rows that were updated. Columns: Branch Name, City, State, Field Filled, Old Value, New Value, Source |
| **Still Missing** | Any rows that couldn't be filled (branch might be closed or data unavailable) |
| **Summary** | Total gaps, filled count, remaining gaps, fill rate % |

---

## Validation

Before creating output:
- [ ] 90%+ of phone gaps filled
- [ ] 90%+ of address gaps filled
- [ ] Every filled value looks valid (real phone format, real address)
- [ ] No accidental overwrites of data that was already correct
- [ ] Source noted for each fill (website vs Google Maps vs USPS)

---

## Resume Protocol

> **"Read {prefix}_gap_fills.json and {prefix}_gap_progress.txt. Print how many gaps have been filled so far and what's remaining. Then continue filling from where you left off."**
