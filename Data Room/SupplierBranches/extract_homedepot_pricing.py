#!/usr/bin/env python3
"""
Extract Home Depot rental pricing for all equipment models
Categories: Aerial & Lifting Equipment, Earth-Moving Equipment
"""

import json
import time
import re
from datetime import datetime

# Equipment URLs organized by category
EQUIPMENT_DATA = {
    "Scissor Lifts": [
        {"name": "19 ft. Scissor Lift", "url": "https://www.homedepot.com/p/rental/Genie-19-Scissor-Lift-Rental-GS1930/316821847"},
        {"name": "19 ft. Scissor Lift on Trailer", "url": "https://www.homedepot.com/p/rental/Genie-19-Scissor-Lift-Rental-PX-15/316821424"},
        {"name": "26 ft. Scissor Lift", "url": "https://www.homedepot.com/p/rental/26-Scissor-Lift-Rental-GS2632/316821928"},
        {"name": "26 ft. Scissor Lift on Trailer", "url": "https://www.homedepot.com/p/rental/Genie-26-Scissor-Lift-Rental-700/316821471"},
        {"name": "20 ft. Single Man Lift", "url": "https://www.homedepot.com/p/rental/Genie-20-Single-Man-Lift-Rental-CH1200/316821455"},
        {"name": "32 ft. Scissor Lift", "url": "https://www.homedepot.com/p/rental/32-Scissor-Lift-Rental-GS3246/315183107"},
        {"name": "40 ft. Scissor Lift", "url": "https://www.homedepot.com/p/rental/Genie-40-Scissor-Lift-Rental-GS4047/316821941"},
        {"name": "32 ft. Rough Terrain Scissor Lift - 4WD", "url": "https://www.homedepot.com/p/rental/Skyjack-32-Rough-Terrain-Scissor-Lift-1305PR1/316821500"},
        {"name": "40 ft. Rough Terrain Scissor Lift - Dual Fuel", "url": "https://www.homedepot.com/p/rental/Genie-40-Rough-Terrain-Scissor-Lift-Rental-GS4069RT/316821449"}
    ],
    "Boom Lifts": [],  # To be populated from category page
    "Mini Excavators": [],  # To be populated from category page
    "Skid Steers": []  # To be populated from category page
}

# Category listing pages
CATEGORY_PAGES = {
    "Boom Lifts": "https://www.homedepot.com/c/boom-lift-equipment-rental",
    "Mini Excavators": "https://www.homedepot.com/c/mini-excavator-rental",
    "Skid Steers": "https://www.homedepot.com/c/skid-steer-rental"
}

def main():
    """Main extraction function - to be run with browser automation"""
    print("=" * 80)
    print("HOME DEPOT EQUIPMENT PRICING EXTRACTION")
    print("=" * 80)
    print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nThis script provides the URLs to extract.")
    print("Use browser automation to extract pricing from each URL.")
    print("\n" + "=" * 80)

    # Display all URLs to extract
    print("\n\nSCISSOR LIFTS (9 models):")
    print("-" * 80)
    for i, item in enumerate(EQUIPMENT_DATA["Scissor Lifts"], 1):
        print(f"{i}. {item['name']}")
        print(f"   URL: {item['url']}")

    print("\n\nCATEGORY PAGES TO EXTRACT MODEL LISTS:")
    print("-" * 80)
    for category, url in CATEGORY_PAGES.items():
        print(f"\n{category}:")
        print(f"   URL: {url}")
        print(f"   Action: Extract all product links from this page")

    print("\n\n" + "=" * 80)
    print("EXTRACTION TEMPLATE FOR EACH MODEL:")
    print("=" * 80)
    print("""
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
    """)

    print("\n" + "=" * 80)
    print("PROGRESS TRACKING:")
    print("=" * 80)
    print("\nSave progress to: homedepot_pricing_progress.txt")
    print("Save all data to: homedepot_pricing.json")
    print("Generate report to: homedepot_equipment_pricing.xlsx")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
