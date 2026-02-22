# Supplier-Specific Configuration Files

## How This Works

You have **two generic skills** that never change:
- `SESSION1_SKILL_branch_extraction.md` — the universal branch scraping framework
- `SESSION2_SKILL_equipment_contacts.md` — the universal equipment/contacts framework

For each new supplier, you create a **short config file** (this document shows you how) that tells Claude Code:
1. What URL to go to
2. How THAT specific website works
3. Any quirks, filters, or gotchas
4. Where the OMS data lives

**To run a scrape, paste into Claude Code:**
```
You have access to my browser via the Claude extension.
Follow the Session 1 skill for branch extraction.
Here is the supplier-specific config:

[paste the supplier config below]
```

---

## Template — Copy & Fill for Any New Supplier

```markdown
# Supplier Config: [SUPPLIER NAME]

## Basics
- **Supplier:** [Full name]
- **Location Page:** [URL]
- **OMS CSV:** /Users/vinuraabeysundara/Desktop/ICG/DOZR/SupplierBranches/[filename].csv
- **Output Prefix:** [lowercase, e.g., "herc"]
- **Expected Branch Count:** [approximate, from website or industry knowledge]
- **OMS Branch Count:** [number from CSV]

## Website Navigation
[Describe exactly how the location finder works on this specific website:]
- What type of page is it? (map, search bar, directory, list)
- What do you click first?
- Are there filters to apply? Which ones?
- How do you get to branch details?
- Is there a "view all" option?
- Any URL patterns for direct state/city access?

## Gotchas
[List anything that tripped us up or might trip up Claude Code:]
- Does the site block automated browsing?
- Do map pins only show names (requiring click-through for details)?
- Are there non-rental branches mixed in that should be skipped?
- Does the site have multiple service lines (some not relevant)?

## Service Filtering
[If the supplier has multiple service lines:]
- ✅ Relevant to DOZR: [list]
- ❌ Skip: [list]

## Contact Info Pattern
[If you know the email/phone pattern:]
- Email pattern: [e.g., city@supplier.com]
- All branches share: [e.g., same 855 number, same email]
- Branch-specific contacts found on: [detail page section]
```

---

## Example Configs (Based on Our Actual Sessions)

---

### Config: Home Depot

```markdown
# Supplier Config: Home Depot

## Basics
- **Supplier:** The Home Depot Rental
- **Location Page:** https://www.homedepot.com/l/storeDirectory
- **OMS CSV:** /Users/vinuraabeysundara/Desktop/ICG/DOZR/SupplierBranches/The-Home-Depot-Rental-19-Feb-26.csv
- **Output Prefix:** homedepot
- **Expected Branch Count:** ~2,000 stores (with rental services)
- **OMS Branch Count:** 767

## Website Navigation
- **Type:** State Directory
- **Method:** Go to https://www.homedepot.com/l/storeDirectory
  1. Click on a STATE name
  2. Page shows all cities in that state with Home Depot stores
  3. Click each CITY to see individual stores
  4. Each store listing shows: Store #, name, address, phone, services
  5. Check if "Tool & Truck Rental" is listed in services
- **Direct state URL:** https://www.homedepot.com/l/[STATE] (e.g., /l/TX, /l/CA)
- **Direct city URL:** https://www.homedepot.com/l/[City]-[STATE]/ (e.g., /l/Houston-TX/)

## Gotchas
- Not all Home Depot stores have rental departments — must check for "Tool & Truck Rental" or "Rental" in services
- Store numbers are 4 digits (e.g., #6851) — use these as the primary matching key
- Connection errors happen after ~30-40 rapid page loads — wait 10 sec and retry, or use direct URL pattern
- The storeDirectory page is more reliable than searching by zip code

## Service Filtering
- ✅ Stores with "Tool & Truck Rental" → relevant
- ❌ Stores without rental service → still record but flag has_rental: false

## Contact Info Pattern
- All rental branches share: thdrentalkeyaccount@homedepot.com
- Phone numbers are store-specific (on each store page)
- No branch manager names visible on website

## Equipment Pricing (Session 2)
- **Pricing Page:** https://www.homedepot.com/c/large_equipment_rental
- **Prices are UNIFORM across all stores** — only need to extract once
- Set store to Houston TX (77001) and extract from there
- Click equipment category → click model → click "Rent Now" → see 4 pricing tiers
- Tiers: 4-Hours, Per Day (24h), Per Week (7d), 4 Weeks (Monthly)
- Only extract: "Aerial & Lifting Equipment" and "Earth-Moving Equipment"
```

---

### Config: Herc Rentals

```markdown
# Supplier Config: Herc Rentals

## Basics
- **Supplier:** Herc Rentals
- **Location Page:** https://www.hercrentals.com/us/locations.html
- **OMS CSV:** /Users/vinuraabeysundara/Desktop/ICG/DOZR/SupplierBranches/Herc-Rentals-19-Feb-26.csv
- **Output Prefix:** herc
- **Expected Branch Count:** ~822 branches
- **OMS Branch Count:** 316 (only 3 enabled!)

## Website Navigation
- **Type:** Search Bar + Interactive Map
- **Method:**
  1. Go to https://www.hercrentals.com/us/locations.html
  2. There's a search bar — enter a zip code or city name
  3. Results appear on map + in a list below/beside the map
  4. Click each branch listing to see details
  5. Branch detail page shows: branch number, address, phone, services, hours
- **Alternative search URL:** https://www.hercrentals.com/us/locations/search?query=[ZIP]
- **No directory page exists** — must search by zip code

## Gotchas
- Herc has MANY service lines — not all branches do general equipment rental
- Branch numbers (e.g., "9422") are in the branch name — use as primary key
- Some branches are co-located (same address, different service lines like ProSolutions and General)
- Canadian branches (ON, AB, BC, SK, MB) are mixed in — record them but note they're Canada
- Only 3 out of 316 OMS branches are enabled — massive untapped capacity

## Service Filtering
CRITICAL — check the Services section on each branch page:
- ✅ General Rentals → RELEVANT
- ✅ Aerial → RELEVANT
- ✅ Earthmoving → RELEVANT
- ✅ Material Handling → RELEVANT
- ✅ ProTruck → RELEVANT
- ❌ ProSolutions → not relevant (specialty industrial)
- ❌ Pump Power & Climate → not relevant
- ❌ Entertainment → not relevant
- ❌ CRC (Crash Recovery) → not relevant

Set relevant_to_dozr = true if branch has ANY ✅ service.

## Contact Info Pattern
- Email format varies: firstname.lastname@hercrentals.com
- Each branch has a unique phone number
- Branch managers sometimes listed on detail page
```

---

### Config: EquipmentShare

```markdown
# Supplier Config: EquipmentShare

## Basics
- **Supplier:** EquipmentShare
- **Location Page:** https://www.equipmentshare.com/location-directory
- **OMS CSV:** /Users/vinuraabeysundara/Desktop/ICG/DOZR/SupplierBranches/Equipment-Share-Inc-19-Feb-26.csv
- **Output Prefix:** equipmentshare
- **Expected Branch Count:** ~373
- **OMS Branch Count:** 194 (zero enabled!)

## Website Navigation
- **Type:** State-by-State Directory (CLEANEST of all suppliers)
- **Method:**
  1. Go to https://www.equipmentshare.com/location-directory
  2. Page lists all states with branches
  3. Click a state → see all branches in that state
  4. Each branch shows: name, address, city, state, zip, phone, services
  5. Branch names include a location number (e.g., "#15965")
- **This is the easiest site to scrape** — clean directory, no map interaction needed

## Gotchas
- Branch names include both city and a # number (e.g., "Birmingham - Alabaster #15965")
- Some cities have multiple branches with different service levels
- Services are listed as "Core Solutions" or "Advanced Solutions"
- Zero OMS branches are enabled — all 194 are disabled, plus ~179 are missing entirely

## Service Filtering
- ✅ Core Solutions → general equipment rental, RELEVANT
- ✅ Advanced Solutions → larger/specialty equipment, RELEVANT
- Both service types are relevant to DOZR

## Contact Info Pattern
- Each branch has its own phone number on the directory page
- No email visible on public pages
- Contact: eddie.parsons@equipmentshare.com appears across many OMS records (may be account rep, not branch)
```

---

### Config: Sunstate Equipment

```markdown
# Supplier Config: Sunstate Equipment

## Basics
- **Supplier:** Sunstate Equipment Co.
- **Location Page:** https://www.sunstateequip.com/locations
- **OMS CSV:** /Users/vinuraabeysundara/Desktop/ICG/DOZR/SupplierBranches/Sunstate-Equipment-Co-19-Feb-26.csv
- **Output Prefix:** sunstate
- **Expected Branch Count:** ~109 branches
- **OMS Branch Count:** 84 (all 84 enabled — model supplier!)

## Website Navigation
- **Type:** Interactive Map (NO search bar, NO directory)
- **Method:**
  1. Go to https://www.sunstateequip.com/locations
  2. An interactive map shows all branch locations as pins
  3. Zoom into each region to see individual pins
  4. Click each pin → popup shows branch name and city
  5. **MUST click through to branch detail page** for full address + phone
  6. The popup alone does NOT have phone numbers or full addresses
- **No filters available** — all branches are general rental
- **Work region by region:** zoom into Southwest, then Southeast, then West Coast, etc.

## Gotchas
- **CRITICAL:** Map popups only show name + city — you MUST click "View Details" or similar for phone/address
- Previous scrape captured 216 entries but ALL were missing phone numbers because it didn't click through
- Some entries are sub-locations like "Trench Safety - Phoenix" — record them separately
- State names on the website are full names ("Arizona") not abbreviations ("AZ") — normalize to 2-letter codes
- Sunstate operates in ~16 states (AZ, CA, CO, FL, GA, NC, NV, NM, OR, SC, TN, TX, UT, VA, WA + a few more)

## Service Filtering
- All Sunstate branches are general equipment rental — ALL are relevant to DOZR
- No filtering needed

## Contact Info Pattern
- All branches share: dozr@sunstateequip.com (dedicated DOZR email!)
- All branches share: 855-808-8875 (but may also have branch-specific numbers)
- The shared number/email is already in OMS — look for branch-specific contacts on detail pages
```

---

### Config: Sunbelt Rentals

```markdown
# Supplier Config: Sunbelt Rentals

## Basics
- **Supplier:** Sunbelt Rentals
- **Location Page:** https://www.sunbeltrentals.com/location/
- **OMS CSV:** /Users/vinuraabeysundara/Desktop/ICG/DOZR/SupplierBranches/Sunbelt-Rental--Inc-19-Feb-26.csv
- **Output Prefix:** sunbelt
- **Expected Branch Count:** ~700+ (should roughly match OMS)
- **OMS Branch Count:** 707 (zero enabled!)

## Website Navigation
- **Type:** Interactive Map with Filters
- **Method:**
  1. Go to https://www.sunbeltrentals.com/location/
  2. Apply filters FIRST (critical):
     ✅ Aerial Work Equipment
     ✅ Earth Moving Solutions
     ✅ General Equipment & Tools
  3. Zoom into regions on the map
  4. Click pins to see branch details
  5. Each pin shows: branch name, address, phone, services

## Gotchas
- **SITE BLOCKS AUTOMATED BROWSING** — this was the hardest site to scrape
- Previous attempts got blocked after ~150 branches
- If blocked: switch to Google Maps fallback ("Sunbelt Rentals [city], [state]")
- OMS has 707 branches, website should match ~1:1 — if counts are close, verify rather than full re-scrape
- 87% of OMS records are missing zip codes (have addresses though)
- Zero OMS branches are enabled — massive untapped capacity

## Service Filtering
Apply the map filters listed above. Only capture branches that appear with those filters active.

## Contact Info Pattern
- Each branch has its own phone number
- No universal email pattern visible
- Many OMS records have phone numbers already — focus on filling gaps
```

---

## Creating a New Config

When you get a new supplier to scrape:

1. **Open their website** in your browser
2. **Find their location finder** — look for "Locations", "Find a Branch", "Store Locator"
3. **Spend 2 minutes clicking around** — understand how the page works
4. **Copy the template** above and fill it in
5. **Note any quirks** — does it need filters? Does it block bots? Are there multiple service lines?
6. **Paste the config + the Session 1 skill** into Claude Code

This takes ~5 minutes per supplier and saves hours of re-prompting when Claude Code doesn't know how to navigate the site.
