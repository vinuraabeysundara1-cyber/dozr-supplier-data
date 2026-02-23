#!/usr/bin/env python3
"""
EquipmentShare.com Simple Scraper using requests and BeautifulSoup
"""

import json
import time
import re
import requests
from bs4 import BeautifulSoup

# Headers to mimic a browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

def extract_price(text):
    """Extract numeric price from text"""
    match = re.search(r'\$?([\d,]+)', text)
    if match:
        return int(match.group(1).replace(',', ''))
    return None

def get_equipment_urls(category_url):
    """Get all equipment URLs from a category page"""
    print(f"Fetching category: {category_url}")
    response = requests.get(category_url, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all links to equipment detail pages
    links = soup.find_all('a', href=re.compile(r'/rent/equipment-classes/'))
    urls = list(set([link['href'] if link['href'].startswith('http') else f"https://www.equipmentshare.com{link['href']}" for link in links if link.get('href')]))

    print(f"Found {len(urls)} equipment URLs")
    return urls

def extract_equipment_data(url, category_name):
    """Extract data from an equipment detail page"""
    print(f"  Extracting: {url}")

    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        data = {
            "url": url,
            "category": category_name
        }

        # Extract equipment name
        h1 = soup.find('h1')
        if h1:
            data["name"] = h1.get_text(strip=True)
        else:
            data["name"] = ""

        # Extract equipment type from breadcrumb
        breadcrumbs = soup.find_all('a')
        equipment_type = ""
        for link in breadcrumbs:
            text = link.get_text(strip=True)
            if any(keyword in text for keyword in ['Scissor', 'Boom', 'Lift', 'Excavator', 'Forklift', 'Telehandler']):
                equipment_type = text
                break
        data["equipment_type"] = equipment_type or category_name

        # Extract pricing
        page_text = soup.get_text()
        day_match = re.search(r'\$(\d+,?\d*)\s*\/\s*day', page_text)
        week_match = re.search(r'\$(\d+,?\d*)\s*\/\s*week', page_text)
        month_match = re.search(r'\$(\d+,?\d*)\s*\/\s*4-week', page_text)

        data["price_daily"] = extract_price(day_match.group(0)) if day_match else None
        data["price_weekly"] = extract_price(week_match.group(0)) if week_match else None
        data["price_monthly"] = extract_price(month_match.group(0)) if month_match else None

        # Extract brand/model and specs from table
        table = soup.find('table')
        brands = []
        models = []
        specs = {}

        if table:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True)

                    if label == 'Equipment Make':
                        for i in range(1, len(cells)):
                            brand = cells[i].get_text(strip=True)
                            if brand and brand not in brands:
                                brands.append(brand)
                    elif label == 'Model Number':
                        for i in range(1, len(cells)):
                            model = cells[i].get_text(strip=True)
                            if model and model not in models:
                                models.append(model)
                    elif label in ['Capacity', 'Max Working Height', 'Operating Weight', 'Dig Depth', 'Reach Height', 'Lift Capacity']:
                        specs[label] = cells[1].get_text(strip=True)

        data["brand_model"] = ', '.join(brands) + (' (' + ', '.join(models) + ')' if models else '')
        data["specs"] = ', '.join([f"{k}: {v}" for k, v in specs.items()])

        return data

    except Exception as e:
        print(f"    Error: {e}")
        return None

def scrape_category(category_url, category_name, output_file, filter_keywords=None, exclude_keywords=None):
    """Scrape all equipment from a category"""
    print(f"\n{'='*60}")
    print(f"Scraping: {category_name}")
    print(f"{'='*60}")

    # Get all equipment URLs
    urls = get_equipment_urls(category_url)

    # Filter URLs if specified
    if filter_keywords:
        urls = [u for u in urls if any(kw in u.lower() for kw in filter_keywords)]

    if exclude_keywords:
        urls = [u for u in urls if not any(kw in u.lower() for kw in exclude_keywords)]

    print(f"Processing {len(urls)} equipment items...")

    all_data = []
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}]", end=" ")
        data = extract_equipment_data(url, category_name)
        if data:
            all_data.append(data)
        time.sleep(1)  # Be polite

    # Save to JSON
    with open(output_file, 'w') as f:
        json.dump(all_data, f, indent=2)

    print(f"\nSaved {len(all_data)} items to {output_file}")
    return all_data

def main():
    """Main function"""
    # Scrape Aerial Work Platforms
    aerial_data = scrape_category(
        "https://www.equipmentshare.com/rent/categories/aerial-work-platform",
        "Aerial Work Platforms",
        "equipmentshare_aerial.json",
        filter_keywords=['lift', 'boom', 'scissor', 'atrium', 'mast'],
        exclude_keywords=['forklift', 'telehandler', 'excavator', 'skid', 'dozer', 'crane',
                         'carrier', 'aerator', 'chipper', 'compressor', 'trencher', 'grinder', 'utility-vehicle']
    )

    # Scrape Earthmoving
    earthmoving_data = scrape_category(
        "https://www.equipmentshare.com/rent/categories/earthmoving",
        "Earthmoving",
        "equipmentshare_earthmoving.json"
    )

    # Scrape Forklifts & Material Handling
    material_handling_data = scrape_category(
        "https://www.equipmentshare.com/rent/categories/forklift-material-handling",
        "Forklifts & Material Handling",
        "equipmentshare_material_handling.json"
    )

    # Create progress file
    with open("equipmentshare_progress.txt", 'w') as f:
        f.write(f"EquipmentShare Scraping Progress\n")
        f.write(f"{'='*50}\n\n")
        f.write(f"Aerial Work Platforms: {len(aerial_data)} items ✓\n")
        f.write(f"Earthmoving: {len(earthmoving_data)} items ✓\n")
        f.write(f"Forklifts & Material Handling: {len(material_handling_data)} items ✓\n")
        f.write(f"\nTotal: {len(aerial_data) + len(earthmoving_data) + len(material_handling_data)} items\n")

    print(f"\n{'='*60}")
    print("SCRAPING COMPLETE!")
    print(f"{'='*60}")
    print(f"Total items scraped: {len(aerial_data) + len(earthmoving_data) + len(material_handling_data)}")

if __name__ == "__main__":
    main()
