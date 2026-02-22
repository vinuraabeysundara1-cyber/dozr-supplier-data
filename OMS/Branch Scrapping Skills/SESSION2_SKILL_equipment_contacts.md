# Session 2: Equipment Types, Pricing & Branch Contacts

## Overview
After Session 1 has captured all branch locations, Session 2 extracts:
1. **Equipment types & rental pricing** from the supplier's catalog
2. **Contact details** (phone, email, manager) for each branch
3. **Service classifications** — which branches carry which equipment categories

---

## Prerequisites
Session 1 must be completed first. You need:
- `{prefix}_branches.json` — all branches from Session 1
- `{prefix}_branch_database.xlsx` — the cross-referenced Excel
- The "New to Add to OMS" list — these branches are highest priority for contacts

---

## Critical Rules

### 1. Capture Every Model and Every Price
```
❌ "They offer mini excavators starting at $250/day"
❌ "Pricing varies by location"
✅ One JSON object per model with all 3-4 pricing tiers
```

### 2. Click Into Every Branch for Contacts
Don't just grab the phone number from the location listing. The branch detail page often has:
- Rental-specific phone number (different from general)
- Email address
- Manager name
- Hours of operation
- Specific services/equipment available at that branch

### 3. Save After Every Equipment Type or Every 20 Branches
Same persistence rules as Session 1. Files are memory.

---

## How to Use This Skill

Paste the following into Claude Code:

```
You have access to my browser via the Claude extension.

SUPPLIER: [Supplier Name]
EQUIPMENT PAGE: [URL to their equipment/rental catalog]
BRANCH DATA: [Path to Session 1 JSON or Excel]
OMS CSV: [Path to OMS CSV]
OUTPUT PREFIX: [e.g., "herc", "sunstate", "homedepot"]

Follow the Session 2 skill instructions below.
```

---

## Part A: Equipment Types & Pricing

### Step 1: Navigate to Equipment Catalog

Go to the supplier's equipment rental or catalog page. Identify what's available.

**Only extract equipment in these DOZR-relevant categories:**
- ✅ Aerial & Lifting (scissor lifts, boom lifts, towable lifts, man lifts)
- ✅ Earth-Moving (mini excavators, excavators, skid steers, compact track loaders, backhoes, dozers)
- ✅ Material Handling (forklifts, telehandlers, reach forklifts)
- ✅ Compaction (rollers, compactors, plate tampers)
- ❌ Skip: generators, light towers, HVAC, pumps, hand tools, trucks, trailers

### Step 2: Extract Pricing (If Available)

For suppliers with public pricing (e.g., Home Depot):

#### Process:
1. Select a location (use Houston TX / zip 77001 as default — prices are usually uniform)
2. Navigate to the first equipment category
3. For each equipment TYPE within the category:
   a. Click to see available MODELS
   b. For each model:
      - Click **"Rent Now"** / **"View Pricing"** / **"Get Quote"**
      - Record ALL pricing tiers shown on the page
      - Go back, do next model
4. Move to next equipment type
5. Move to next category

#### Data Format:
```json
{
  "category": "Earth-Moving Equipment",
  "equipment_type": "Mini Excavators",
  "model_name": "1-Ton Mini Excavator",
  "model_details": "Kubota K008-3",
  "price_4hr": 254,
  "price_daily": 339,
  "price_weekly": 1017,
  "price_monthly": 2543,
  "specs": "1-ton, Max dig depth: 4.5', Bucket width: 12\"",
  "url": "https://www.supplier.com/rental/..."
}
```

**Capture the EXACT prices shown. Don't round.** If prices have an asterisk (*), still record them and note "estimated" in specs.

#### Save: `{prefix}_equipment_pricing.json` after each equipment type.

### Step 3: Extract Equipment Types (If No Public Pricing)

For suppliers without public pricing (most rental companies):

1. Navigate to their equipment or fleet page
2. List every equipment category and type they offer
3. Note any size ranges, brands, or specs mentioned

```json
{
  "category": "Aerial",
  "equipment_type": "Scissor Lifts",
  "size_range": "19ft to 53ft",
  "brands_mentioned": ["Genie", "JLG", "Skyjack"],
  "available_at": "All branches",
  "pricing_available": false,
  "notes": "Must call branch for pricing"
}
```

### Step 4: Equipment Output

Create `{prefix}_equipment_pricing.xlsx`:

| Sheet | Contents |
|-------|----------|
| **All Equipment** | Every model sorted by Category → Type → Model. Columns: Category, Equipment Type, Model Name, Details, 4-Hr Price, Daily, Weekly, Monthly, Specs |
| **With Margin (+10%)** | Same data with a margin column next to each price showing price × 1.10 (rounded up) |
| **Pricing Summary** | Per equipment type: model count, daily price range, monthly price range, avg daily rate |

---

## Part B: Branch Contact Details

### Step 1: Prioritize Branches

Read the Session 1 data. Work through branches in this priority order:
1. **NEW branches** (not in OMS) — highest priority, these need full contact info for onboarding
2. **OMS branches with missing data** (no phone, no email) — fill gaps
3. **Remaining branches** — capture contacts for completeness

### Step 2: Extract Contact Details

For each branch, navigate to its detail page on the supplier website.

#### What to capture:
```json
{
  "branch_name": "Supplier - Houston East",
  "branch_number": "1234",
  "general_phone": "(713) 555-1234",
  "rental_phone": "(713) 555-5678",
  "fax": "(713) 555-9999",
  "general_email": "houston.east@supplier.com",
  "rental_email": "rentals.houston@supplier.com",
  "manager_name": "John Smith",
  "manager_title": "Branch Manager",
  "hours_weekday": "7:00 AM - 5:00 PM",
  "hours_saturday": "7:00 AM - 12:00 PM",
  "hours_sunday": "Closed",
  "services": ["General Rentals", "Aerial", "Earthmoving", "Delivery"],
  "equipment_categories": ["Scissor Lifts", "Boom Lifts", "Mini Excavators", "Skid Steers"],
  "notes": ""
}
```

**At minimum capture:** phone, email (if shown), hours, services.
Not every branch page will have all fields — capture what's available.

#### Efficiency tips:
- If the supplier has a consistent email pattern (e.g., `city@supplier.com` or `rentals.city@supplier.com`), note the pattern after confirming it on 5+ branches
- If hours are the same across all branches, note "Standard hours: Mon-Fri 7-5" after confirming on 5+ branches
- Focus extra time on branches where contacts differ from the pattern

### Step 3: Service Classification

For suppliers with multiple service lines, classify each branch's relevance to DOZR:

| Service Line | DOZR Relevant? | Notes |
|-------------|---------------|-------|
| General Rentals / General Equipment | ✅ YES | Core rental services |
| Aerial / Aerial Work Platforms | ✅ YES | Scissor lifts, boom lifts |
| Earthmoving / Earth Moving Solutions | ✅ YES | Excavators, skid steers, dozers |
| Material Handling | ✅ YES | Forklifts, telehandlers |
| ProTruck / Truck Rental | ✅ YES | Commercial truck rental |
| Compaction | ✅ YES | Rollers, compactors |
| Landscaping | ✅ YES | Compact equipment |
| Entertainment / Events | ❌ No | Tents, staging |
| Pump Power & Climate / HVAC | ❌ No | Specialty |
| ProSolutions / Specialty | ⚠️ Partial | Check specifics |
| CRC / Crash Recovery | ❌ No | Specialty |
| Trench Safety | ⚠️ Partial | Niche |

Set `relevant_to_dozr: true` if the branch offers ANY ✅ service.

### Step 4: Contact Output

Create `{prefix}_branch_contacts.xlsx`:

| Sheet | Contents |
|-------|----------|
| **All Branch Contacts** | Every branch with all contact fields. Sorted State → City. Columns: Branch Name, Branch #, City, State, General Phone, Rental Phone, Email, Manager, Hours (Weekday), Hours (Sat), Services, Relevant to DOZR |
| **New Branches — Full Details** | Only NEW branches (not in OMS) with complete contact + service info. This is the onboarding-ready sheet. |
| **Service Summary** | Per branch: which equipment categories are available. Useful for knowing what to list on DOZR. |
| **Contact Gaps** | Branches still missing phone or email after extraction — may need manual follow-up |

---

## Part C: Combined Final Deliverable

After both Part A and Part B are complete, create a master file:

`{prefix}_complete_supplier_profile.xlsx`:

| Sheet | Contents |
|-------|----------|
| **Summary** | Supplier overview: total branches, new to add, equipment types, pricing summary |
| **New Branches to Onboard** | All new branches with address, phone, email, hours, services, equipment categories — ready for OMS import |
| **Equipment Catalog** | All equipment types with pricing (if available) |
| **Equipment + Margin** | Pricing with 10% margin column for each tier |
| **All Branch Contacts** | Complete contact directory |
| **Service by Branch** | Matrix: branches × equipment categories |

---

## Persistence Protocol

Same as Session 1:

```
# Files:
{prefix}_equipment_pricing.json     # Equipment + pricing data
{prefix}_branch_contacts.json       # Contact details per branch
{prefix}_equipment_progress.txt     # Equipment extraction progress
{prefix}_contacts_progress.txt      # Contact extraction progress

# Save after:
- Every equipment type completed
- Every 20 branches contacted
- Every state completed
```

## Resume Protocol

If interrupted:

> **"Read all existing JSON and progress files for [SUPPLIER]. Print what equipment and contacts have been captured so far. Then continue from where you left off."**

---

## Validation Checklist

### Equipment:
- [ ] All DOZR-relevant categories covered (aerial, earthmoving, material handling at minimum)
- [ ] Each model has pricing for all available tiers (4hr, daily, weekly, monthly)
- [ ] No duplicate model entries
- [ ] Specs captured where available

### Contacts:
- [ ] 90%+ of new branches have phone numbers
- [ ] 50%+ of new branches have email addresses (not all suppliers show emails)
- [ ] Services/equipment categories noted for 80%+ of branches
- [ ] Hours captured for 80%+ of branches

### Classification:
- [ ] Every branch has `relevant_to_dozr` flag set
- [ ] Service classification follows the DOZR relevance table above

---

## Common Mistakes to Avoid

| Mistake | Prevention |
|---------|------------|
| Recording only general phone, missing rental-specific number | Check for separate "Rentals" or "Sales" phone on detail page |
| Assuming all branches have same services | Click into each branch — some are specialty-only (e.g., Herc ProSolutions vs General) |
| Skipping pricing tiers | Always click "Rent Now" to see ALL tiers, not just the price shown on the listing page |
| Not flagging DOZR relevance | Always classify services — branches with only Entertainment/HVAC shouldn't go to DOZR |
| Capturing equipment list but not per-branch availability | Note which equipment categories each individual branch carries |
