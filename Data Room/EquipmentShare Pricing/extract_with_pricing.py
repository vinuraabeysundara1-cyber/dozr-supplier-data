#!/usr/bin/env python3
"""
EquipmentShare Price Extractor with Playwright
This script extracts complete equipment data INCLUDING pricing from EquipmentShare.com

Requirements:
    pip install playwright pandas openpyxl
    playwright install chromium
"""

import json
import time
from playwright.sync_api import sync_playwright
import pandas as pd

def extract_equipment_with_pricing():
    equipment_data = {
        "aerial": [],
        "earthmoving": [],
        "material_handling": []
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set to True for background
        page = browser.new_page()

        # Set location to Houston, TX
        print("Setting location to Houston, TX...")
        page.goto("https://www.equipmentshare.com/rent")
        page.wait_for_timeout(2000)

        try:
            page.click("text=Minneapolis, Minnesota")
            page.wait_for_timeout(1000)
            page.fill("input[placeholder*='Enter city']", "Houston, TX")
            page.wait_for_timeout(1000)
            page.click("text=Houston, TX")
            page.wait_for_timeout(2000)
        except:
            print("Location already set or selector changed")

        # Category URLs
        categories = [
            ("aerial", "https://www.equipmentshare.com/rent/categories/aerial-work-platform", "Aerial Work Platforms"),
            ("earthmoving", "https://www.equipmentshare.com/rent/categories/earthmoving", "Earthmoving"),
            ("material_handling", "https://www.equipmentshare.com/rent/categories/forklifts-material-handling", "Forklifts & Material Handling")
        ]

        for cat_key, cat_url, cat_name in categories:
            print(f"\n=== Extracting {cat_name} ===")
            page.goto(cat_url)
            page.wait_for_timeout(3000)

            # Scroll to bottom to load all equipment
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)

            # Get all equipment links
            links = page.eval_on_selector_all(
                'a[href*="/rent/equipment-classes/"]',
                '(elements) => elements.map(el => el.href)'
            )

            # Get unique links
            unique_links = list(set(links))
            print(f"Found {len(unique_links)} equipment items")

            # Extract data from each equipment page
            for idx, url in enumerate(unique_links[:20], 1):  # Limit to 20 for testing
                try:
                    print(f"  [{idx}/{min(20, len(unique_links))}] {url.split('/')[-1]}")
                    page.goto(url)
                    page.wait_for_timeout(2000)

                    # Extract data using JavaScript
                    data = page.evaluate('''() => {
                        const result = {
                            url: window.location.href,
                            category: null,
                            name: null,
                            price_daily: null,
                            price_weekly: null,
                            price_monthly: null,
                            brand_model: null,
                            specs: null
                        };

                        // Name
                        const nameEl = document.querySelector('h1');
                        if (nameEl) result.name = nameEl.textContent.trim();

                        // Category from breadcrumb
                        const breadcrumb = document.querySelector('a[href*="/categories/"]');
                        if (breadcrumb) result.category = breadcrumb.textContent.trim();

                        // Pricing
                        const bodyText = document.body.textContent;
                        const dayMatch = bodyText.match(/\\$(\\d+,?\\d*)\\s*\\/\\s*day/);
                        const weekMatch = bodyText.match(/\\$(\\d+,?\\d*)\\s*\\/\\s*week(?!\\s*-)/);
                        const monthMatch = bodyText.match(/\\$(\\d+,?\\d*)\\s*\\/\\s*4-week/);

                        if (dayMatch) result.price_daily = parseInt(dayMatch[1].replace(',', ''));
                        if (weekMatch) result.price_weekly = parseInt(weekMatch[1].replace(',', ''));
                        if (monthMatch) result.price_monthly = parseInt(monthMatch[1].replace(',', ''));

                        // Brand/Model from specs table
                        const table = document.querySelector('table');
                        const brands = [];
                        const models = [];
                        const specs = {};

                        if (table) {
                            const rows = table.querySelectorAll('tr');
                            rows.forEach(row => {
                                const cells = row.querySelectorAll('td, th');
                                if (cells.length >= 2) {
                                    const label = cells[0].textContent.trim();

                                    if (label === 'Equipment Make' || label === 'EQUIPMENT MAKE') {
                                        for (let i = 1; i < cells.length; i++) {
                                            const brand = cells[i].textContent.trim();
                                            if (brand && brand !== label) brands.push(brand);
                                        }
                                    } else if (label === 'Model Number' || label === 'MODEL NUMBER') {
                                        for (let i = 1; i < cells.length; i++) {
                                            const model = cells[i].textContent.trim();
                                            if (model && model !== label) models.push(model);
                                        }
                                    } else if (['Capacity', 'Max Working Height', 'Operating Weight'].includes(label)) {
                                        specs[label] = cells[1].textContent.trim();
                                    }
                                }
                            });
                        }

                        if (brands.length > 0) {
                            result.brand_model = brands.join(', ');
                            if (models.length > 0) {
                                result.brand_model += ' (' + models.join(', ') + ')';
                            }
                        }

                        if (Object.keys(specs).length > 0) {
                            result.specs = Object.entries(specs).map(([k, v]) => k + ': ' + v).join(', ');
                        }

                        return result;
                    }''')

                    if data['name']:
                        data['equipment_type'] = cat_name
                        equipment_data[cat_key].append(data)

                    time.sleep(0.5)  # Be respectful to the server

                except Exception as e:
                    print(f"    Error: {e}")
                    continue

            # Save category JSON
            filename = f"equipmentshare_{cat_key}_with_pricing.json"
            with open(filename, 'w') as f:
                json.dump(equipment_data[cat_key], f, indent=2)
            print(f"Saved {len(equipment_data[cat_key])} items to {filename}")

        browser.close()

    # Create Excel file
    create_excel(equipment_data)
    print("\n=== Extraction Complete ===")

def create_excel(data):
    """Create Excel file with all categories"""
    print("\nCreating Excel file...")

    with pd.ExcelWriter('equipmentshare_equipment_pricing.xlsx', engine='openpyxl') as writer:
        # Sheet 1: Aerial Work Platforms
        if data['aerial']:
            df_aerial = pd.DataFrame(data['aerial'])
            df_aerial = df_aerial.sort_values(['name'])
            df_aerial.to_excel(writer, sheet_name='Aerial Work Platforms', index=False)

        # Sheet 2: Earthmoving
        if data['earthmoving']:
            df_earth = pd.DataFrame(data['earthmoving'])
            df_earth = df_earth.sort_values(['name'])
            df_earth.to_excel(writer, sheet_name='Earthmoving', index=False)

        # Sheet 3: Material Handling
        if data['material_handling']:
            df_material = pd.DataFrame(data['material_handling'])
            df_material = df_material.sort_values(['name'])
            df_material.to_excel(writer, sheet_name='Material Handling', index=False)

        # Sheet 4: All Equipment Combined
        all_equipment = []
        for cat_data in data.values():
            all_equipment.extend(cat_data)

        if all_equipment:
            df_all = pd.DataFrame(all_equipment)
            df_all = df_all.sort_values(['equipment_type', 'name'])
            df_all.to_excel(writer, sheet_name='All Equipment', index=False)

            # Sheet 5: Pricing Summary
            summary = df_all.groupby('equipment_type').agg({
                'name': 'count',
                'price_daily': ['min', 'max', 'mean'],
                'price_weekly': ['min', 'max', 'mean'],
                'price_monthly': ['min', 'max', 'mean']
            }).round(2)
            summary.to_excel(writer, sheet_name='Pricing Summary')

    print("Excel file created: equipmentshare_equipment_pricing.xlsx")

if __name__ == "__main__":
    extract_equipment_with_pricing()
