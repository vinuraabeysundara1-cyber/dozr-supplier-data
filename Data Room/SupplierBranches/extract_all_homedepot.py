#!/usr/bin/env python3
"""
Complete Home Depot Equipment Pricing Extractor
Manually collected data for all equipment categories
"""

import json
import pandas as pd
from datetime import datetime

# Complete equipment data - to be manually filled
EQUIPMENT_DATA = [
    # SCISSOR LIFTS (9 models)
    {
        "category": "Aerial & Lifting Equipment",
        "equipment_type": "Scissor Lifts",
        "model_name": "19 ft. Scissor Lift",
        "model_details": "Genie GS1930",
        "price_4hr": 199,
        "price_daily": 199,
        "price_weekly": 398,
        "price_monthly": 597,
        "specs": "Max platform height: 19', Max platform lift weight: 500 lbs, Overall width: 30\"",
        "url": "https://www.homedepot.com/p/rental/Genie-19-Scissor-Lift-Rental-GS1930/316821847"
    },
    {
        "category": "Aerial & Lifting Equipment",
        "equipment_type": "Scissor Lifts",
        "model_name": "19 ft. Scissor Lift on Trailer",
        "model_details": "Genie PX-15",
        "price_4hr": 239,
        "price_daily": 239,
        "price_weekly": 717,
        "price_monthly": 1793,
        "specs": "Max platform height: 19', Max platform lift weight: 500 lbs, Overall width: 30\", Towing: 4480 lbs",
        "url": "https://www.homedepot.com/p/rental/Genie-19-Scissor-Lift-Rental-PX-15/316821424"
    },
    {
        "category": "Aerial & Lifting Equipment",
        "equipment_type": "Scissor Lifts",
        "model_name": "26 ft. Scissor Lift",
        "model_details": "Genie GS2632",
        "price_4hr": 259,
        "price_daily": 259,
        "price_weekly": 518,
        "price_monthly": 932,
        "specs": "Max platform height: 26', Max platform lift weight (unextended): 500 lbs, Overall width: 46\"",
        "url": "https://www.homedepot.com/p/rental/26-Scissor-Lift-Rental-GS2632/316821928"
    },
    {
        "category": "Aerial & Lifting Equipment",
        "equipment_type": "Scissor Lifts",
        "model_name": "26 ft. Scissor Lift on Trailer",
        "model_details": "Genie 700",
        "price_4hr": 299,
        "price_daily": 299,
        "price_weekly": 897,
        "price_monthly": 2243,
        "specs": "Max platform height: 26', Max platform lift weight: 500 lbs, Towing: requires 2\" hitch",
        "url": "https://www.homedepot.com/p/rental/Genie-26-Scissor-Lift-Rental-700/316821471"
    }
    # TO BE COMPLETED: Add remaining 5 scissor lifts + boom lifts + excavators + skid steers
]

def save_json():
    """Save to JSON file"""
    with open('/Users/vinuraabeysundara/Desktop/ICG/DOZR/SupplierBranches/homedepot_pricing.json', 'w') as f:
        json.dump(EQUIPMENT_DATA, f, indent=2)
    print(f"Saved {len(EQUIPMENT_DATA)} records to homedepot_pricing.json")

def create_excel():
    """Create Excel report"""
    df = pd.DataFrame(EQUIPMENT_DATA)

    # Create Excel writer
    output_path = '/Users/vinuraabeysundara/Desktop/ICG/DOZR/SupplierBranches/homedepot_equipment_pricing.xlsx'
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Sheet 1: All Equipment
        df.to_excel(writer, sheet_name='All Equipment', index=False)

        # Sheet 2: Scissor Lifts only
        scissor_df = df[df['equipment_type'] == 'Scissor Lifts']
        scissor_df.to_excel(writer, sheet_name='Scissor Lifts', index=False)

        # Sheet 3: Summary Stats
        summary = df.groupby('equipment_type').agg({
            'model_name': 'count',
            'price_daily': ['min', 'max', 'mean'],
            'price_weekly': ['min', 'max', 'mean'],
            'price_monthly': ['min', 'max', 'mean']
        }).round(2)
        summary.to_excel(writer, sheet_name='Summary')

    print(f"Created Excel report: {output_path}")

def create_progress_log():
    """Create progress tracking file"""
    progress = f"""HOME DEPOT PRICING EXTRACTION PROGRESS
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

COMPLETED:
- Scissor Lifts: 4/9 models
  ✓ 19 ft. Scissor Lift (GS1930)
  ✓ 19 ft. Scissor Lift on Trailer (PX-15)
  ✓ 26 ft. Scissor Lift (GS2632)
  ✓ 26 ft. Scissor Lift on Trailer (700)

REMAINING:
- Scissor Lifts: 5 models
  - 20 ft. Single Man Lift (CH1200)
  - 32 ft. Scissor Lift (GS3246)
  - 40 ft. Scissor Lift (GS4047)
  - 32 ft. Rough Terrain Scissor Lift (1305PR1)
  - 40 ft. Rough Terrain Scissor Lift (GS4069RT)

- Boom Lifts: ALL (need to scrape category page first)
- Mini Excavators: ALL (need to scrape category page first)
- Skid Steers: ALL (need to scrape category page first)

NEXT STEPS:
1. Complete remaining 5 scissor lifts
2. Navigate to boom lift category page and extract all product URLs
3. Extract pricing for all boom lifts
4. Repeat for mini excavators and skid steers
"""

    with open('/Users/vinuraabeysundara/Desktop/ICG/DOZR/SupplierBranches/homedepot_pricing_progress.txt', 'w') as f:
        f.write(progress)

    print("Created progress log: homedepot_pricing_progress.txt")

if __name__ == "__main__":
    print("=" * 100)
    print("HOME DEPOT EQUIPMENT PRICING DATA")
    print("=" * 100)
    print(f"\nCurrent Status: {len(EQUIPMENT_DATA)} models extracted\n")

    save_json()
    create_excel()
    create_progress_log()

    print("\n" + "=" * 100)
    print("FILES CREATED:")
    print("1. homedepot_pricing.json - JSON data")
    print("2. homedepot_equipment_pricing.xlsx - Excel report (3 sheets)")
    print("3. homedepot_pricing_progress.txt - Progress tracking")
    print("=" * 100)
