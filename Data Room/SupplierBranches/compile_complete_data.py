#!/usr/bin/env python3
"""
Compile all extracted Home Depot equipment pricing data
"""

import json
import pandas as pd
from datetime import datetime

# Complete dataset - all extracted equipment
COMPLETE_DATA = [
    # ===== SCISSOR LIFTS (9 models) =====
    {"category": "Aerial & Lifting Equipment", "equipment_type": "Scissor Lifts", "model_name": "19 ft. Scissor Lift", "model_details": "Genie GS1930", "price_4hr": 199, "price_daily": 199, "price_weekly": 398, "price_monthly": 597, "specs": "Max platform height: 19', Max platform lift weight: 500 lbs", "url": "https://www.homedepot.com/p/rental/Genie-19-Scissor-Lift-Rental-GS1930/316821847"},
    {"category": "Aerial & Lifting Equipment", "equipment_type": "Scissor Lifts", "model_name": "19 ft. Scissor Lift on Trailer", "model_details": "Genie PX-15", "price_4hr": 239, "price_daily": 239, "price_weekly": 717, "price_monthly": 1793, "specs": "Max platform height: 19', Towable", "url": "https://www.homedepot.com/p/rental/Genie-19-Scissor-Lift-Rental-PX-15/316821424"},
    {"category": "Aerial & Lifting Equipment", "equipment_type": "Scissor Lifts", "model_name": "26 ft. Scissor Lift", "model_details": "Genie GS2632", "price_4hr": 259, "price_daily": 259, "price_weekly": 518, "price_monthly": 932, "specs": "Max platform height: 26'", "url": "https://www.homedepot.com/p/rental/26-Scissor-Lift-Rental-GS2632/316821928"},
    {"category": "Aerial & Lifting Equipment", "equipment_type": "Scissor Lifts", "model_name": "26 ft. Scissor Lift on Trailer", "model_details": "Genie 700", "price_4hr": 299, "price_daily": 299, "price_weekly": 897, "price_monthly": 2243, "specs": "Max platform height: 26', Towable", "url": "https://www.homedepot.com/p/rental/Genie-26-Scissor-Lift-Rental-700/316821471"},
    {"category": "Aerial & Lifting Equipment", "equipment_type": "Scissor Lifts", "model_name": "20 ft. Single Man Lift", "model_details": "Genie CH1200", "price_4hr": 229, "price_daily": 229, "price_weekly": 435, "price_monthly": 870, "specs": "Max platform height: 20', Single person", "url": "https://www.homedepot.com/p/rental/Genie-20-Single-Man-Lift-Rental-CH1200/316821455"},
    {"category": "Aerial & Lifting Equipment", "equipment_type": "Scissor Lifts", "model_name": "32 ft. Scissor Lift", "model_details": "Genie GS3246", "price_4hr": 309, "price_daily": 309, "price_weekly": 649, "price_monthly": 1298, "specs": "Max platform height: 32'", "url": "https://www.homedepot.com/p/rental/32-Scissor-Lift-Rental-GS3246/315183107"},
    {"category": "Aerial & Lifting Equipment", "equipment_type": "Scissor Lifts", "model_name": "40 ft. Scissor Lift", "model_details": "Genie GS4047", "price_4hr": 419, "price_daily": 419, "price_weekly": 880, "price_monthly": 1848, "specs": "Max platform height: 40'", "url": "https://www.homedepot.com/p/rental/Genie-40-Scissor-Lift-Rental-GS4047/316821941"},
    {"category": "Aerial & Lifting Equipment", "equipment_type": "Scissor Lifts", "model_name": "32 ft. Rough Terrain Scissor Lift - 4WD", "model_details": "Skyjack 1305PR1", "price_4hr": 369, "price_daily": 369, "price_weekly": 812, "price_monthly": 1624, "specs": "Max platform height: 32', 4WD", "url": "https://www.homedepot.com/p/rental/Skyjack-32-Rough-Terrain-Scissor-Lift-1305PR1/316821500"},
    {"category": "Aerial & Lifting Equipment", "equipment_type": "Scissor Lifts", "model_name": "40 ft. Rough Terrain Scissor Lift - Dual Fuel", "model_details": "Genie GS4069RT", "price_4hr": 419, "price_daily": 419, "price_weekly": 1048, "price_monthly": 2096, "specs": "Max platform height: 40', Dual fuel", "url": "https://www.homedepot.com/p/rental/Genie-40-Rough-Terrain-Scissor-Lift-Rental-GS4069RT/316821449"},

    # ===== BOOM LIFTS (8 models) =====
    {"category": "Aerial & Lifting Equipment", "equipment_type": "Boom Lifts", "model_name": "35 ft. Towable Boom Lift", "model_details": "JLG T350", "price_4hr": 292, "price_daily": 389, "price_weekly": 1167, "price_monthly": 2918, "specs": "Max platform height: 35', Towable", "url": "https://www.homedepot.com/p/rental/JLG-35-Towable-Boom-Lift-Rental-T350/316821960"},
    {"category": "Aerial & Lifting Equipment", "equipment_type": "Boom Lifts", "model_name": "50 ft. Towable Boom Lift", "model_details": "JLG S75X", "price_4hr": 367, "price_daily": 489, "price_weekly": 1467, "price_monthly": 3227, "specs": "Max platform height: 50', Towable", "url": "https://www.homedepot.com/p/rental/50-Towable-Boom-Lift-Rental-S75X/316821658"},
    {"category": "Aerial & Lifting Equipment", "equipment_type": "Boom Lifts", "model_name": "30-33 ft. Articulating Boom Lift - DC Powered", "model_details": "Genie E300AJP", "price_4hr": 449, "price_daily": 449, "price_weekly": 1123, "price_monthly": 2246, "specs": "Max platform height: 30-33', DC powered", "url": "https://www.homedepot.com/p/rental/Genie-30-33-ft-Articulating-Boom-Lift-E300AJP/328503707"},
    {"category": "Aerial & Lifting Equipment", "equipment_type": "Boom Lifts", "model_name": "34 ft. Articulating Boom Lift - 4WD w/ Jib", "model_details": "JLG 425D-TP", "price_4hr": 469, "price_daily": 469, "price_weekly": 1126, "price_monthly": 2139, "specs": "Max platform height: 34', 4WD, Jib equipped", "url": "https://www.homedepot.com/p/rental/JLG-34-Articulating-Boom-Lift-w-Jib-Rental-425D-TP/316821508"},
    {"category": "Aerial & Lifting Equipment", "equipment_type": "Boom Lifts", "model_name": "45 ft. Articulating Boom Lift - DC Powered w/ Jib", "model_details": "Genie VT3121", "price_4hr": 499, "price_daily": 499, "price_weekly": 1148, "price_monthly": 2296, "specs": "Max platform height: 45', DC powered, Jib", "url": "https://www.homedepot.com/p/rental/Genie-45-Articulating-Boom-Lift-w-Jib-Rental-VT3121/316821584"},
    {"category": "Aerial & Lifting Equipment", "equipment_type": "Boom Lifts", "model_name": "45 ft. Articulating Boom Lift w/ Jib", "model_details": "JLG 425D", "price_4hr": 529, "price_daily": 529, "price_weekly": 1270, "price_monthly": 2540, "specs": "Max platform height: 45', Jib equipped", "url": "https://www.homedepot.com/p/rental/JLG-45-Articulating-Boom-Lift-w-Jib-Rental-425D/316821569"},
    {"category": "Aerial & Lifting Equipment", "equipment_type": "Boom Lifts", "model_name": "60 ft. Articulating Boom Lift w/ Jib", "model_details": "JLG 530X", "price_4hr": 639, "price_daily": 639, "price_weekly": 1470, "price_monthly": 2940, "specs": "Max platform height: 60', Jib equipped", "url": "https://www.homedepot.com/p/rental/60-Articulating-Boom-Lift-w-Jib-Rental-530X/316821695"},
    {"category": "Aerial & Lifting Equipment", "equipment_type": "Boom Lifts", "model_name": "80 ft. Articulating Boom Lift w/ Jib", "model_details": "JLG 532DX-TP", "price_4hr": 959, "price_daily": 959, "price_weekly": 2398, "price_monthly": 5036, "specs": "Max platform height: 80', Jib equipped", "url": "https://www.homedepot.com/p/rental/80-Articulating-Boom-Lift-w-Jib-Rental-532DX-TP/316821726"},

    # ===== MINI EXCAVATORS (Partial - 2 of 6) =====
    {"category": "Earth-Moving Equipment", "equipment_type": "Mini Excavators", "model_name": "1-Ton Mini Excavator", "model_details": "Kubota K008", "price_4hr": 254, "price_daily": 339, "price_weekly": 1017, "price_monthly": 2543, "specs": "1-ton, Max dig depth: 4.5'", "url": "https://www.homedepot.com/p/rental/Kubota-1-Ton-Mini-Excavator-Rental-K008/316821721"},
    {"category": "Earth-Moving Equipment", "equipment_type": "Mini Excavators", "model_name": "1.5-2 Ton Mini Excavator", "model_details": "Kubota U17", "price_4hr": 269, "price_daily": 359, "price_weekly": 1077, "price_monthly": 2693, "specs": "1.5-2 ton, Max dig depth: 6.2'", "url": "https://www.homedepot.com/p/rental/KUBOTA-1-5-2-Ton-Mini-Excavator-Rental-U17/316821405"},
]

# Save to JSON
with open('/Users/vinuraabeysundara/Desktop/ICG/DOZR/SupplierBranches/homedepot_pricing.json', 'w') as f:
    json.dump(COMPLETE_DATA, f, indent=2)

print(f"Saved {len(COMPLETE_DATA)} equipment models to JSON")
print(f"\nBreakdown:")
print(f"  Scissor Lifts: 9")
print(f"  Boom Lifts: 8")
print(f"  Mini Excavators: 2 (4 remaining)")
print(f"  Skid Steers: 0 (pending)")
