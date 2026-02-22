#!/usr/bin/env python3
"""
Home Depot Equipment Pricing Extractor
Extracts pricing for all equipment in Aerial & Lifting and Earth-Moving categories
"""

import json
import time
from datetime import datetime

# All equipment URLs organized by category
EQUIPMENT_URLS = {
    "Scissor Lifts": [
        {
            "name": "19 ft. Scissor Lift",
            "url": "https://www.homedepot.com/p/rental/Genie-19-Scissor-Lift-Rental-GS1930/316821847",
            "model": "Genie GS1930"
        },
        {
            "name": "19 ft. Scissor Lift on Trailer",
            "url": "https://www.homedepot.com/p/rental/Genie-19-Scissor-Lift-Rental-PX-15/316821424",
            "model": "Genie PX-15"
        },
        {
            "name": "26 ft. Scissor Lift",
            "url": "https://www.homedepot.com/p/rental/26-Scissor-Lift-Rental-GS2632/316821928",
            "model": "Genie GS2632"
        },
        {
            "name": "26 ft. Scissor Lift on Trailer",
            "url": "https://www.homedepot.com/p/rental/Genie-26-Scissor-Lift-Rental-700/316821471",
            "model": "Genie 700"
        },
        {
            "name": "20 ft. Single Man Lift",
            "url": "https://www.homedepot.com/p/rental/Genie-20-Single-Man-Lift-Rental-CH1200/316821455",
            "model": "Genie CH1200"
        },
        {
            "name": "32 ft. Scissor Lift",
            "url": "https://www.homedepot.com/p/rental/32-Scissor-Lift-Rental-GS3246/315183107",
            "model": "Genie GS3246"
        },
        {
            "name": "40 ft. Scissor Lift",
            "url": "https://www.homedepot.com/p/rental/Genie-40-Scissor-Lift-Rental-GS4047/316821941",
            "model": "Genie GS4047"
        },
        {
            "name": "32 ft. Rough Terrain Scissor Lift - 4WD",
            "url": "https://www.homedepot.com/p/rental/Skyjack-32-Rough-Terrain-Scissor-Lift-1305PR1/316821500",
            "model": "Skyjack 1305PR1"
        },
        {
            "name": "40 ft. Rough Terrain Scissor Lift - Dual Fuel",
            "url": "https://www.homedepot.com/p/rental/Genie-40-Rough-Terrain-Scissor-Lift-Rental-GS4069RT/316821449",
            "model": "Genie GS4069RT"
        }
    ]
}

# Manually extracted data (to be filled in from browser)
EXTRACTED_DATA = [
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
        "specs": "Max platform height: 19', Max platform lift weight: 500 lbs, Overall width: 30\", Towing: 4480 lbs combined weight",
        "url": "https://www.homedepot.com/p/rental/Genie-19-Scissor-Lift-Rental-PX-15/316821424"
    }
]

def print_extraction_plan():
    """Print the extraction plan"""
    print("=" * 100)
    print("HOME DEPOT EQUIPMENT PRICING EXTRACTION PLAN")
    print("=" * 100)
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    print("SCISSOR LIFTS (9 models):")
    print("-" * 100)
    for i, item in enumerate(EQUIPMENT_URLS["Scissor Lifts"], 1):
        print(f"{i}. {item['name']} ({item['model']})")
        print(f"   URL: {item['url']}\n")

    print("\n" + "=" * 100)
    print("NEXT: Need to extract Boom Lifts, Mini Excavators, and Skid Steers")
    print("=" * 100)

def save_data():
    """Save extracted data to JSON"""
    output_file = "/Users/vinuraabeysundara/Desktop/ICG/DOZR/SupplierBranches/homedepot_pricing.json"

    with open(output_file, 'w') as f:
        json.dump(EXTRACTED_DATA, f, indent=2)

    print(f"\nSaved {len(EXTRACTED_DATA)} records to {output_file}")

if __name__ == "__main__":
    print_extraction_plan()
    print("\nNote: Use browser automation to extract remaining data")
    print("Currently have 2 out of 9 scissor lifts extracted.")
