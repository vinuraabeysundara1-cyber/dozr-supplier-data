# DOZR Campaign Duplication Instructions for Yoloclaude

## OVERVIEW

This document provides complete instructions to duplicate all DOZR US Google Ads campaigns for new geo markets. Follow these instructions exactly to ensure proper campaign structure, tracking, and geo-exclusions.

**Account ID:** 8531896842
**Date:** February 9, 2026
**Task:** Duplicate 10 enabled US campaigns for 14 new state markets

---

## SECTION 1: NEW GEO MARKETS TO TARGET

Add these 14 states to ALL new expansion campaigns:

| # | State | Abbrev | Key Market | Geo Target ID | Resource Name |
|---|-------|--------|------------|---------------|---------------|
| 1 | Colorado | CO | Denver | 21123 | geoTargetConstants/21123 |
| 2 | Indiana | IN | Indianapolis | 21140 | geoTargetConstants/21140 |
| 3 | Kansas | KS | Kansas City | 21147 | geoTargetConstants/21147 |
| 4 | Kentucky | KY | Louisville | 21148 | geoTargetConstants/21148 |
| 5 | Louisiana | LA | New Orleans | 21151 | geoTargetConstants/21151 |
| 6 | Minnesota | MN | Minneapolis | 21158 | geoTargetConstants/21158 |
| 7 | Missouri | MO | Kansas City | 21161 | geoTargetConstants/21161 |
| 8 | Nebraska | NE | Omaha | 21164 | geoTargetConstants/21164 |
| 9 | New Mexico | NM | Albuquerque | 21168 | geoTargetConstants/21168 |
| 10 | Nevada | NV | Las Vegas | 21166 | geoTargetConstants/21166 |
| 11 | Oklahoma | OK | Oklahoma City | 21172 | geoTargetConstants/21172 |
| 12 | Utah | UT | Salt Lake City | 21183 | geoTargetConstants/21183 |
| 13 | Washington | WA | Seattle | 21186 | geoTargetConstants/21186 |
| 14 | Iowa | IA | Omaha Metro | 21145 | geoTargetConstants/21145 |

---

## SECTION 2: CAMPAIGNS TO DUPLICATE

Duplicate these 10 ENABLED US campaigns:

### Campaign 1: Search-Scissor-Lift-Core-Geos-US
- **New Name:** Search-Scissor-Lift-Expansion-Geos-US
- **Current Bid Strategy:** MAXIMIZE_CONVERSIONS
- **New Bid Strategy:** MAXIMIZE_CONVERSIONS (keep same)
- **Current Daily Budget:** $350
- **New Daily Budget:** $75 (start conservative)
- **Current Geo Count:** 46 locations

### Campaign 2: Search-Forklift-Core-Geos-US
- **New Name:** Search-Forklift-Expansion-Geos-US
- **Current Bid Strategy:** MAXIMIZE_CONVERSION_VALUE
- **New Bid Strategy:** MAXIMIZE_CONVERSIONS (start with this, switch to Max Conv Value after 30+ conversions)
- **Current Daily Budget:** $400
- **New Daily Budget:** $75

### Campaign 3: Search-Excavator-Core-Geos-US
- **New Name:** Search-Excavator-Expansion-Geos-US
- **Current Bid Strategy:** MAXIMIZE_CONVERSIONS
- **New Bid Strategy:** MAXIMIZE_CONVERSIONS
- **Current Daily Budget:** $250
- **New Daily Budget:** $60

### Campaign 4: Search-Telehandler-Core-Geos-US
- **New Name:** Search-Telehandler-Expansion-Geos-US
- **Current Bid Strategy:** MAXIMIZE_CONVERSIONS
- **New Bid Strategy:** MAXIMIZE_CONVERSIONS
- **Current Daily Budget:** $100
- **New Daily Budget:** $50

### Campaign 5: Search-Dozers-Core-Geos-US-V3
- **New Name:** Search-Dozers-Expansion-Geos-US
- **Current Bid Strategy:** MAXIMIZE_CONVERSIONS
- **New Bid Strategy:** MAXIMIZE_CONVERSIONS
- **Current Daily Budget:** $200
- **New Daily Budget:** $50

### Campaign 6: Search-Backhoe-Core-Geos-US
- **New Name:** Search-Backhoe-Expansion-Geos-US
- **Current Bid Strategy:** MAXIMIZE_CONVERSIONS
- **New Bid Strategy:** MAXIMIZE_CONVERSIONS
- **Current Daily Budget:** $100
- **New Daily Budget:** $40

### Campaign 7: Search-Loader-Core-Geos-US
- **New Name:** Search-Loader-Expansion-Geos-US
- **Current Bid Strategy:** MAXIMIZE_CONVERSIONS
- **New Bid Strategy:** MAXIMIZE_CONVERSIONS
- **Current Daily Budget:** $150
- **New Daily Budget:** $50

### Campaign 8: Search-Demand-Boom-Lifts
- **New Name:** Search-Boom-Lifts-Expansion-Geos-US
- **Current Bid Strategy:** (Check current - likely Max Conversions or tROAS)
- **New Bid Strategy:** MAXIMIZE_CONVERSIONS
- **Current Daily Budget:** (Check current)
- **New Daily Budget:** $60

### Campaign 9: Search-Demand-Brand-US
- **New Name:** Search-Demand-Brand-Expansion-Geos-US
- **Current Bid Strategy:** TARGET_IMPRESSION_SHARE
- **New Bid Strategy:** TARGET_IMPRESSION_SHARE (keep same - brand protection)
- **Current Daily Budget:** $100
- **New Daily Budget:** $40
- **Note:** This is a brand campaign - maintain impression share targeting

### Campaign 10: DSA-AllPages-Tier1-New-US-2
- **New Name:** DSA-AllPages-Expansion-Geos-US
- **Current Bid Strategy:** MAXIMIZE_CONVERSION_VALUE
- **New Bid Strategy:** MAXIMIZE_CONVERSIONS (start with this)
- **Current Daily Budget:** $350
- **New Daily Budget:** $60

---

## SECTION 3: GEO EXCLUSIONS - CRITICAL

### 3.1 Add These EXCLUSIONS to NEW Expansion Campaigns

Exclude ALL current geos from the new expansion campaigns to prevent competition:

#### States to EXCLUDE (8 states):
| State | Geo Target ID |
|-------|---------------|
| Arizona | 21136 |
| California | 21137 |
| Florida | 21142 |
| Georgia | 21143 |
| New York | 21167 |
| North Carolina | 21160 |
| Tennessee | 21175 |
| Texas | 21176 |

#### DMA Regions to EXCLUDE (30 DMAs):
| DMA Region | Geo Target ID |
|------------|---------------|
| Albany-Schenectady-Troy, NY | 200532 |
| Atlanta, GA | 200524 |
| Austin, TX | 200635 |
| Buffalo, NY | 200514 |
| Charleston, SC | 200519 |
| Charlotte, NC | 200517 |
| Charlottesville, VA | 200584 |
| Dallas-Ft. Worth, TX | 200623 |
| Greensboro-High Point-Winston Salem, NC | 200518 |
| Greenville-Spartanburg, SC-Asheville, NC-Anderson, SC | 200567 |
| Houston, TX | 200618 |
| Knoxville, TN | 200557 |
| Los Angeles, CA | 200803 |
| Memphis, TN | 200640 |
| Miami-Ft. Lauderdale, FL | 200528 |
| Nashville, TN | 200659 |
| New York, NY | 200501 |
| Norfolk-Portsmouth-Newport News, VA | 200544 |
| Orlando-Daytona Beach-Melbourne, FL | 200534 |
| Raleigh-Durham (Fayetteville), NC | 200560 |
| Richmond-Petersburg, VA | 200556 |
| Rochester, NY | 200538 |
| San Antonio, TX | 200641 |
| San Diego, CA | 200825 |
| Savannah, GA | 200507 |
| Syracuse, NY | 200555 |
| Tampa-St Petersburg (Sarasota), FL | 200539 |
| Tri-Cities, TN-VA | 200531 |
| Waco-Temple-Bryan, TX | 200625 |
| West Palm Beach-Ft. Pierce, FL | 200548 |

#### Region to EXCLUDE:
| Region | Geo Target ID |
|--------|---------------|
| San Francisco Bay Area | 9073451 |

#### Counties to EXCLUDE:
| County | Geo Target ID |
|--------|---------------|
| Maricopa County, AZ | 9057037 |
| Pinal County, AZ | 9057040 |

#### Cities to EXCLUDE:
| City | Geo Target ID |
|------|---------------|
| Phoenix, AZ | 1013462 |
| Hesperia, CA | 1013857 |
| Loma Linda, CA | 1013954 |
| Elberton, GA | 1015339 |
| Stonecrest, GA | 9198538 |

### 3.2 Add These EXCLUSIONS to ALL CURRENT US Campaigns

Add the 14 new states as NEGATIVE location targets to ALL existing enabled US campaigns (not just Core-Geos):

**Apply to these 10 campaigns:**
- Search-Scissor-Lift-Core-Geos-US
- Search-Forklift-Core-Geos-US
- Search-Excavator-Core-Geos-US
- Search-Telehandler-Core-Geos-US
- Search-Dozers-Core-Geos-US-V3
- Search-Backhoe-Core-Geos-US
- Search-Loader-Core-Geos-US
- Search-Demand-Boom-Lifts
- Search-Demand-Brand-US
- DSA-AllPages-Tier1-New-US-2

**States to add as NEGATIVE location targets:**

| State | Geo Target ID |
|-------|---------------|
| Colorado | 21123 |
| Indiana | 21140 |
| Kansas | 21147 |
| Kentucky | 21148 |
| Louisiana | 21151 |
| Minnesota | 21158 |
| Missouri | 21161 |
| Nebraska | 21164 |
| New Mexico | 21168 |
| Nevada | 21166 |
| Oklahoma | 21172 |
| Utah | 21183 |
| Washington | 21186 |
| Iowa | 21145 |

### 3.3 Mirror Country Exclusions

Copy ALL country exclusions from the current campaigns. The current campaigns exclude 98 countries. Query the current exclusions and apply the same to expansion campaigns:

```
Query current campaign exclusions:
SELECT campaign_criterion.location.geo_target_constant
FROM campaign_criterion
WHERE campaign.name = 'Search-Scissor-Lift-Core-Geos-US'
AND campaign_criterion.negative = true
AND campaign_criterion.type = 'LOCATION'
```

Apply the same exclusions to all expansion campaigns.

---

## SECTION 4: CAMPAIGN STRUCTURE TO DUPLICATE

For each campaign, duplicate the EXACT structure:

### 4.1 Ad Groups

Query all ad groups from each source campaign:
```
SELECT ad_group.id, ad_group.name, ad_group.status, ad_group.type
FROM ad_group
WHERE campaign.name = '[SOURCE_CAMPAIGN_NAME]'
AND ad_group.status != 'REMOVED'
```

Create identical ad groups in the expansion campaign with the same names.

### 4.2 Ads

Query all ads from each ad group:
```
SELECT
    ad_group.name,
    ad_group_ad.ad.id,
    ad_group_ad.ad.type,
    ad_group_ad.ad.final_urls,
    ad_group_ad.ad.responsive_search_ad.headlines,
    ad_group_ad.ad.responsive_search_ad.descriptions,
    ad_group_ad.ad.responsive_search_ad.path1,
    ad_group_ad.ad.responsive_search_ad.path2
FROM ad_group_ad
WHERE campaign.name = '[SOURCE_CAMPAIGN_NAME]'
AND ad_group_ad.status != 'REMOVED'
```

Duplicate ALL ads with:
- Same headlines
- Same descriptions
- Same final URLs
- Same display paths

### 4.3 Keywords

Query all keywords from each campaign:
```
SELECT
    ad_group.name,
    ad_group_criterion.keyword.text,
    ad_group_criterion.keyword.match_type,
    ad_group_criterion.status,
    ad_group_criterion.final_url
FROM keyword_view
WHERE campaign.name = '[SOURCE_CAMPAIGN_NAME]'
AND ad_group_criterion.status != 'REMOVED'
```

Duplicate ALL keywords with:
- Same keyword text
- Same match type (BROAD, PHRASE, or EXACT)
- Same final URLs (if set at keyword level)

### 4.4 Negative Keywords

Query all negative keywords:
```
SELECT
    ad_group.name,
    ad_group_criterion.keyword.text,
    ad_group_criterion.keyword.match_type,
    ad_group_criterion.negative
FROM ad_group_criterion
WHERE campaign.name = '[SOURCE_CAMPAIGN_NAME]'
AND ad_group_criterion.negative = true
AND ad_group_criterion.type = 'KEYWORD'
```

Also query campaign-level negatives:
```
SELECT
    campaign_criterion.keyword.text,
    campaign_criterion.keyword.match_type
FROM campaign_criterion
WHERE campaign.name = '[SOURCE_CAMPAIGN_NAME]'
AND campaign_criterion.type = 'KEYWORD'
AND campaign_criterion.negative = true
```

Duplicate ALL negative keywords at both ad group and campaign levels.

---

## SECTION 5: TRACKING SETUP - DUPLICATE EXACTLY

### 5.1 Query Current Tracking Settings

Get account-level tracking:
```
SELECT
    customer.tracking_url_template,
    customer.final_url_suffix,
    customer.auto_tagging_enabled
FROM customer
```

Get campaign-level tracking:
```
SELECT
    campaign.name,
    campaign.tracking_url_template,
    campaign.final_url_suffix,
    campaign.url_custom_parameters
FROM campaign
WHERE campaign.name = '[SOURCE_CAMPAIGN_NAME]'
```

### 5.2 Apply Same Tracking to Expansion Campaigns

- Copy the tracking URL template exactly
- Copy the final URL suffix exactly
- Copy any custom parameters exactly
- Ensure auto-tagging is enabled

### 5.3 Conversion Actions

The new campaigns will automatically use the same conversion actions as they're set at the account level. Verify conversions are tracking by checking:
```
SELECT
    conversion_action.name,
    conversion_action.type,
    conversion_action.status
FROM conversion_action
WHERE conversion_action.status = 'ENABLED'
```

---

## SECTION 6: STEP-BY-STEP IMPLEMENTATION

### Phase 1: Create New Campaigns (Do NOT enable yet)

1. For each of the 10 source campaigns:
   - Create new campaign with "Expansion" naming
   - Set status to PAUSED
   - Set bid strategy to MAXIMIZE_CONVERSIONS
   - Set daily budget (conservative amounts listed above)
   - Add the 14 new state geo targets
   - Add ALL geo exclusions (states, DMAs, cities, counties, region)
   - Copy country exclusions from source campaign

### Phase 2: Duplicate Structure

2. For each new campaign:
   - Create all ad groups (copy names exactly)
   - Create all ads in each ad group (copy all headlines, descriptions, URLs)
   - Add all keywords with same match types
   - Add all negative keywords (ad group and campaign level)

### Phase 3: Tracking & Settings

3. For each new campaign:
   - Copy tracking URL template from source
   - Copy final URL suffix from source
   - Copy any URL custom parameters
   - Verify conversion tracking is inherited

### Phase 4: Update ALL Current US Campaigns

4. For ALL 10 current enabled US campaigns (not just Core-Geos):
   - Add the 14 new states as NEGATIVE location targets
   - This prevents overlap/competition
   - Campaigns to update: Scissor-Lift, Forklift, Excavator, Telehandler, Dozers, Backhoe, Loader, Boom-Lifts, Brand-US, DSA

### Phase 5: Review & Enable

5. Final checks:
   - Verify geo targets are correct (14 new states)
   - Verify geo exclusions are complete (no overlap with current campaigns)
   - Verify ads are approved
   - Verify keywords are active
   - Set campaigns to ENABLED

---

## SECTION 7: CAMPAIGN SETTINGS REFERENCE

### Standard Settings for All Expansion Campaigns:

| Setting | Value |
|---------|-------|
| Campaign Type | Search |
| Networks | Google Search Network only (no partners) |
| Location Options | "Presence: People in your targeted locations" |
| Language | English |
| Ad Rotation | Optimize: Prefer best performing ads |
| Bid Strategy | Maximize Conversions (initially) |
| Target CPA | Do not set (let system learn) |
| Start Date | Immediate upon enabling |
| End Date | None |

### For DSA Campaign:

| Setting | Value |
|---------|-------|
| Campaign Type | Dynamic Search Ads |
| Dynamic ad targets | Copy from source campaign |
| Page feeds | Copy from source if used |

---

## SECTION 8: VERIFICATION CHECKLIST

After implementation, verify:

- [ ] 10 new expansion campaigns created
- [ ] Each has 14 state geo targets
- [ ] Each has all geo exclusions (no overlap with core campaigns)
- [ ] Ad groups match source campaigns
- [ ] Ads match source campaigns (all headlines/descriptions)
- [ ] Keywords match source campaigns (same text/match types)
- [ ] Negative keywords duplicated
- [ ] Tracking settings copied
- [ ] ALL 10 current US campaigns have 14 new states excluded
- [ ] All expansion campaigns set to PAUSED for review
- [ ] Ready to enable after final review

---

## SECTION 9: POST-LAUNCH MONITORING

### Week 1:
- Monitor daily for any disapprovals
- Check search terms report for irrelevant queries
- Verify conversions are tracking

### Week 2-4:
- Monitor CPA and ROAS by campaign
- Add negative keywords as needed
- Adjust budgets based on performance

### Week 5-6:
- Evaluate switching to Target ROAS if 30+ conversions achieved
- Compare expansion vs. core campaign performance

---

## QUICK REFERENCE: ALL GEO TARGET IDs

### New States to ADD:
21123, 21140, 21147, 21148, 21151, 21158, 21161, 21164, 21168, 21166, 21172, 21183, 21186, 21145

### States to EXCLUDE from expansion:
21136, 21137, 21142, 21143, 21167, 21160, 21175, 21176

### DMAs to EXCLUDE from expansion:
200532, 200524, 200635, 200514, 200519, 200517, 200584, 200623, 200518, 200567, 200618, 200557, 200803, 200640, 200528, 200659, 200501, 200544, 200534, 200560, 200556, 200538, 200641, 200825, 200507, 200555, 200539, 200531, 200625, 200548

### Other to EXCLUDE from expansion:
9073451 (SF Bay Area), 9057037 (Maricopa County), 9057040 (Pinal County), 1013462 (Phoenix), 1013857 (Hesperia), 1013954 (Loma Linda), 1015339 (Elberton), 9198538 (Stonecrest)

---

*Document generated: February 9, 2026*
*For DOZR Google Ads Account: 8531896842*
