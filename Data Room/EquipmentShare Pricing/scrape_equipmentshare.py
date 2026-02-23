#!/usr/bin/env python3
"""
EquipmentShare.com Web Scraper
Extracts equipment data from Aerial Work Platforms, Earthmoving, and Forklifts categories
"""

import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Category URLs
CATEGORIES = {
    "aerial": "https://www.equipmentshare.com/rent/categories/aerial-work-platform",
    "earthmoving": "https://www.equipmentshare.com/rent/categories/earthmoving",
    "material_handling": "https://www.equipmentshare.com/rent/categories/forklifts-material-handling"
}

def setup_driver():
    """Setup Chrome driver with options"""
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    # options.add_argument('--headless')  # Uncomment for headless mode
    driver = webdriver.Chrome(options=options)
    return driver

def scroll_to_bottom(driver):
    """Scroll to bottom of page to load all equipment"""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def extract_price(text):
    """Extract numeric price from text like '$222 / day'"""
    import re
    match = re.search(r'\$?([\d,]+)', text)
    if match:
        return int(match.group(1).replace(',', ''))
    return None

def get_equipment_urls(driver, category_url):
    """Get all equipment URLs from a category page"""
    print(f"Loading category page: {category_url}")
    driver.get(category_url)
    time.sleep(3)

    # Scroll to load all items
    scroll_to_bottom(driver)

    # Find all equipment links
    links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/rent/equipment-classes/"]')
    urls = list(set([link.get_attribute('href') for link in links if link.get_attribute('href')]))

    print(f"Found {len(urls)} equipment URLs")
    return urls

def extract_equipment_data(driver, url, category_name):
    """Extract data from an equipment detail page"""
    print(f"  Extracting: {url}")

    try:
        driver.get(url)
        time.sleep(2)

        data = {
            "url": url,
            "category": category_name
        }

        # Extract equipment name
        try:
            name_el = driver.find_element(By.TAG_NAME, 'h1')
            data["name"] = name_el.text.strip()
        except NoSuchElementException:
            data["name"] = ""

        # Extract equipment type from breadcrumb or page structure
        try:
            breadcrumbs = driver.find_elements(By.CSS_SELECTOR, 'nav a, [aria-label="Breadcrumb"] a')
            if breadcrumbs:
                data["equipment_type"] = breadcrumbs[-1].text.strip() if breadcrumbs else ""
        except:
            data["equipment_type"] = ""

        # Extract pricing - look for elements containing price info
        try:
            # Try to find pricing elements
            price_texts = driver.find_elements(By.XPATH, "//*[contains(text(), '/day') or contains(text(), '/week') or contains(text(), '4-week')]")

            for elem in price_texts:
                text = elem.text
                if '/day' in text and 'price_daily' not in data:
                    data["price_daily"] = extract_price(text)
                elif '/week' in text and '4-week' not in text and 'price_weekly' not in data:
                    data["price_weekly"] = extract_price(text)
                elif '4-week' in text and 'price_monthly' not in data:
                    data["price_monthly"] = extract_price(text)
        except:
            pass

        # Extract specs from specs table
        try:
            specs_items = []
            # Look for specification tables or lists
            spec_elements = driver.find_elements(By.CSS_SELECTOR, 'table tr, .specs li, [class*="spec"] li')

            for elem in spec_elements[:10]:  # Limit to first 10 specs
                text = elem.text.strip()
                if text and ':' in text:
                    specs_items.append(text)

            data["specs"] = ", ".join(specs_items) if specs_items else ""

            # Try to extract brand/model
            brand_keywords = ['MEC', 'JLG', 'Genie', 'CAT', 'Caterpillar', 'Bobcat', 'John Deere',
                            'Kubota', 'Yanmar', 'Takeuchi', 'Skyjack', 'Terex', 'Gradall']

            page_text = driver.find_element(By.TAG_NAME, 'body').text
            found_brands = [brand for brand in brand_keywords if brand in page_text]
            data["brand_model"] = ", ".join(found_brands) if found_brands else ""

        except:
            data["specs"] = ""
            data["brand_model"] = ""

        return data

    except Exception as e:
        print(f"    Error extracting {url}: {e}")
        return None

def scrape_category(driver, category_url, category_name, output_file):
    """Scrape all equipment from a category"""
    print(f"\n{'='*60}")
    print(f"Scraping category: {category_name}")
    print(f"{'='*60}")

    # Get all equipment URLs
    urls = get_equipment_urls(driver, category_url)

    # Filter URLs based on category
    if category_name == "Aerial Work Platforms":
        # Filter for aerial-related equipment only
        urls = [u for u in urls if any(keyword in u.lower() for keyword in
                ['lift', 'boom', 'scissor', 'atrium', 'mast'])]
        # Exclude forklifts and material handling
        urls = [u for u in urls if not any(keyword in u.lower() for keyword in
                ['forklift', 'telehandler', 'excavator', 'skid', 'dozer', 'crane',
                 'carrier', 'aerator', 'chipper', 'compressor', 'trencher', 'grinder', 'utility-vehicle'])]

    print(f"Processing {len(urls)} equipment items...")

    all_data = []
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}]", end=" ")
        data = extract_equipment_data(driver, url, category_name)
        if data:
            all_data.append(data)
        time.sleep(1)  # Be polite

    # Save to JSON
    with open(output_file, 'w') as f:
        json.dump(all_data, f, indent=2)

    print(f"\nSaved {len(all_data)} items to {output_file}")
    return all_data

def main():
    """Main scraping function"""
    driver = setup_driver()

    try:
        # Scrape Aerial Work Platforms
        aerial_data = scrape_category(
            driver,
            CATEGORIES["aerial"],
            "Aerial Work Platforms",
            "equipmentshare_aerial.json"
        )

        # Scrape Earthmoving
        earthmoving_data = scrape_category(
            driver,
            CATEGORIES["earthmoving"],
            "Earthmoving",
            "equipmentshare_earthmoving.json"
        )

        # Scrape Forklifts & Material Handling
        material_handling_data = scrape_category(
            driver,
            CATEGORIES["material_handling"],
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

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
