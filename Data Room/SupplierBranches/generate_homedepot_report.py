#!/usr/bin/env python3
"""
Generate Home Depot Equipment Pricing Report
Creates Excel report from extracted JSON data
"""

import json
import pandas as pd
from datetime import datetime

# Load extracted data
with open('/Users/vinuraabeysundara/Desktop/ICG/DOZR/SupplierBranches/homedepot_pricing.json', 'r') as f:
    data = json.load(f)

print("=" * 100)
print("HOME DEPOT EQUIPMENT PRICING REPORT GENERATOR")
print("=" * 100)
print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"\nLoaded {len(data)} equipment records\n")

# Create DataFrame
df = pd.DataFrame(data)

# Create Excel writer
output_path = '/Users/vinuraabeysundara/Desktop/ICG/DOZR/SupplierBranches/homedepot_equipment_pricing.xlsx'

with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    # Sheet 1: All Equipment
    df_display = df[['equipment_type', 'model_name', 'model_details', 'price_4hr', 'price_daily', 'price_weekly', 'price_monthly', 'specs']].copy()
    df_display.to_excel(writer, sheet_name='All Equipment', index=False)

    # Format the sheet
    worksheet = writer.sheets['All Equipment']
    worksheet.column_dimensions['A'].width = 20
    worksheet.column_dimensions['B'].width = 35
    worksheet.column_dimensions['C'].width = 20
    worksheet.column_dimensions['D'].width = 12
    worksheet.column_dimensions['E'].width = 12
    worksheet.column_dimensions['F'].width = 12
    worksheet.column_dimensions['G'].width = 12
    worksheet.column_dimensions['H'].width = 60

    # Sheet 2: Scissor Lifts Detail
    scissor_df = df[df['equipment_type'] == 'Scissor Lifts'].copy()
    scissor_df_display = scissor_df[['model_name', 'model_details', 'price_4hr', 'price_daily', 'price_weekly', 'price_monthly', 'specs']].copy()
    scissor_df_display.to_excel(writer, sheet_name='Scissor Lifts', index=False)

    worksheet = writer.sheets['Scissor Lifts']
    worksheet.column_dimensions['A'].width = 35
    worksheet.column_dimensions['B'].width = 20
    worksheet.column_dimensions['C'].width = 12
    worksheet.column_dimensions['D'].width = 12
    worksheet.column_dimensions['E'].width = 12
    worksheet.column_dimensions['F'].width = 12
    worksheet.column_dimensions['G'].width = 60

    # Sheet 3: Summary Statistics
    summary_data = {
        'Equipment Type': ['Scissor Lifts'],
        'Total Models': [len(scissor_df)],
        'Avg 4-Hour Price': [f"${scissor_df['price_4hr'].mean():.0f}"],
        'Avg Daily Price': [f"${scissor_df['price_daily'].mean():.0f}"],
        'Avg Weekly Price': [f"${scissor_df['price_weekly'].mean():.0f}"],
        'Avg Monthly Price': [f"${scissor_df['price_monthly'].mean():.0f}"],
        'Min Daily Price': [f"${scissor_df['price_daily'].min()}"],
        'Max Daily Price': [f"${scissor_df['price_daily'].max()}"]
    }

    summary_df = pd.DataFrame(summary_data)
    summary_df.to_excel(writer, sheet_name='Summary', index=False)

    worksheet = writer.sheets['Summary']
    for col in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
        worksheet.column_dimensions[col].width = 18

print("=" * 100)
print("REPORT GENERATED SUCCESSFULLY")
print("=" * 100)
print(f"\nOutput file: {output_path}")
print("\nReport Contents:")
print("  - Sheet 1: All Equipment (all extracted models)")
print("  - Sheet 2: Scissor Lifts (detailed view)")
print("  - Sheet 3: Summary (statistics)")
print("\n" + "=" * 100)
print("EXTRACTION STATUS")
print("=" * 100)
print("\nCompleted:")
print("  ✓ Scissor Lifts: 9 models")
print("\nPending:")
print("  - Boom Lifts: 8 models (URLs identified)")
print("  - Mini Excavators: TBD (need to extract from category page)")
print("  - Skid Steers: TBD (need to extract from category page)")
print("\n" + "=" * 100)
