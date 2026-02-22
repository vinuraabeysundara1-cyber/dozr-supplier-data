#!/usr/bin/env python3
"""
Generate comprehensive Home Depot equipment rental pricing report
Completed: Feb 20, 2026
"""

import json
import pandas as pd
from datetime import datetime

# Load complete data
with open('/Users/vinuraabeysundara/Desktop/ICG/DOZR/SupplierBranches/homedepot_pricing.json', 'r') as f:
    equipment_data = json.load(f)

# Create DataFrame
df = pd.DataFrame(equipment_data)

# Create Excel writer
excel_file = '/Users/vinuraabeysundara/Desktop/ICG/DOZR/SupplierBranches/HomeDepot_Equipment_Pricing_Complete.xlsx'
writer = pd.ExcelWriter(excel_file, engine='openpyxl')

# Sheet 1: All Equipment
df_all = df.copy()
df_all.to_excel(writer, sheet_name='All Equipment', index=False)

# Sheet 2: Scissor Lifts
df_scissor = df[df['equipment_type'] == 'Scissor Lifts'].copy()
df_scissor.to_excel(writer, sheet_name='Scissor Lifts', index=False)

# Sheet 3: Boom Lifts
df_boom = df[df['equipment_type'] == 'Boom Lifts'].copy()
df_boom.to_excel(writer, sheet_name='Boom Lifts', index=False)

# Sheet 4: Mini Excavators
df_mini_ex = df[df['equipment_type'] == 'Mini Excavators'].copy()
df_mini_ex.to_excel(writer, sheet_name='Mini Excavators', index=False)

# Sheet 5: Skid Steers (Tracked)
df_skid_tracked = df[df['equipment_type'] == 'Skid Steers - Tracked'].copy()
df_skid_tracked.to_excel(writer, sheet_name='Skid Steers - Tracked', index=False)

# Sheet 6: Skid Steers (Wheeled)
df_skid_wheeled = df[df['equipment_type'] == 'Skid Steers - Wheeled'].copy()
df_skid_wheeled.to_excel(writer, sheet_name='Skid Steers - Wheeled', index=False)

# Sheet 7: Summary Statistics
summary_data = {
    'Equipment Type': ['Scissor Lifts', 'Boom Lifts', 'Mini Excavators', 'Skid Steers - Tracked', 'Skid Steers - Wheeled', 'TOTAL'],
    'Count': [
        len(df_scissor),
        len(df_boom),
        len(df_mini_ex),
        len(df_skid_tracked),
        len(df_skid_wheeled),
        len(df)
    ],
    'Avg Daily Rate': [
        f"${df_scissor['price_daily'].mean():.2f}" if len(df_scissor) > 0 else "$0",
        f"${df_boom['price_daily'].mean():.2f}" if len(df_boom) > 0 else "$0",
        f"${df_mini_ex['price_daily'].mean():.2f}" if len(df_mini_ex) > 0 else "$0",
        f"${df_skid_tracked['price_daily'].mean():.2f}" if len(df_skid_tracked) > 0 else "$0",
        f"${df_skid_wheeled['price_daily'].mean():.2f}" if len(df_skid_wheeled) > 0 else "$0",
        f"${df['price_daily'].mean():.2f}"
    ],
    'Avg Weekly Rate': [
        f"${df_scissor['price_weekly'].mean():.2f}" if len(df_scissor) > 0 else "$0",
        f"${df_boom['price_weekly'].mean():.2f}" if len(df_boom) > 0 else "$0",
        f"${df_mini_ex['price_weekly'].mean():.2f}" if len(df_mini_ex) > 0 else "$0",
        f"${df_skid_tracked['price_weekly'].mean():.2f}" if len(df_skid_tracked) > 0 else "$0",
        f"${df_skid_wheeled['price_weekly'].mean():.2f}" if len(df_skid_wheeled) > 0 else "$0",
        f"${df['price_weekly'].mean():.2f}"
    ],
    'Avg Monthly Rate': [
        f"${df_scissor['price_monthly'].mean():.2f}" if len(df_scissor) > 0 else "$0",
        f"${df_boom['price_monthly'].mean():.2f}" if len(df_boom) > 0 else "$0",
        f"${df_mini_ex['price_monthly'].mean():.2f}" if len(df_mini_ex) > 0 else "$0",
        f"${df_skid_tracked['price_monthly'].mean():.2f}" if len(df_skid_tracked) > 0 else "$0",
        f"${df_skid_wheeled['price_monthly'].mean():.2f}" if len(df_skid_wheeled) > 0 else "$0",
        f"${df['price_monthly'].mean():.2f}"
    ]
}
df_summary = pd.DataFrame(summary_data)
df_summary.to_excel(writer, sheet_name='Summary', index=False)

# Save and close
writer.close()

print(f"\n{'='*60}")
print(f"HOME DEPOT EQUIPMENT RENTAL PRICING - EXTRACTION COMPLETE")
print(f"{'='*60}")
print(f"\nReport Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
print(f"\nTotal Equipment Models Extracted: {len(df)}")
print(f"\nBreakdown by Category:")
print(f"  - Scissor Lifts: {len(df_scissor)} models")
print(f"  - Boom Lifts: {len(df_boom)} models")
print(f"  - Mini Excavators: {len(df_mini_ex)} models")
print(f"  - Skid Steers (Tracked): {len(df_skid_tracked)} models")
print(f"  - Skid Steers (Wheeled): {len(df_skid_wheeled)} models")
print(f"\nFiles Generated:")
print(f"  1. JSON Data: homedepot_pricing.json")
print(f"  2. Excel Report: HomeDepot_Equipment_Pricing_Complete.xlsx")
print(f"     - 7 sheets: All Equipment, Scissor Lifts, Boom Lifts,")
print(f"       Mini Excavators, Skid Steers (Tracked/Wheeled), Summary")
print(f"\n{'='*60}\n")
