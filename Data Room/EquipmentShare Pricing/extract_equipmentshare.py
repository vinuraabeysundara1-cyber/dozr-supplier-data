import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class EquipmentShareScraper:
    def __init__(self):
        self.driver = None
        self.location = "Houston, TX"

    def setup_driver(self):
        """Initialize Chrome driver"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in background
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=options)

    def set_location(self):
        """Set location to Houston, TX"""
        self.driver.get("https://www.equipmentshare.com/rent")
        time.sleep(2)

        try:
            # Click location selector
            location_btn = self.driver.find_element(By.XPATH, "//div[contains(text(), 'Minnesota')]")
            location_btn.click()
            time.sleep(1)

            # Enter Houston, TX
            location_input = self.driver.find_element(By.XPATH, "//input[@placeholder='Enter city or zip code']")
            location_input.clear()
            location_input.send_keys("Houston, TX")
            time.sleep(1)

            # Select Houston from dropdown
            houston_option = self.driver.find_element(By.XPATH, "//div[contains(text(), 'Houston, TX')]")
            houston_option.click()
            time.sleep(2)
        except Exception as e:
            print(f"Error setting location: {e}")

    def extract_category_equipment(self, category_url, category_name):
        """Extract all equipment from a category"""
        equipment_list = []

        self.driver.get(category_url)
        time.sleep(3)

        # Scroll to bottom to load all items
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # Find all equipment links
        equipment_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/rent/equipment-classes/')]")

        unique_urls = set()
        for link in equipment_links:
            url = link.get_attribute('href')
            if url and '/rent/equipment-classes/' in url:
                unique_urls.add(url)

        print(f"Found {len(unique_urls)} equipment items in {category_name}")

        # Visit each equipment detail page
        for idx, url in enumerate(sorted(unique_urls), 1):
            try:
                print(f"  Extracting {idx}/{len(unique_urls)}: {url}")
                equipment_data = self.extract_equipment_details(url, category_name)
                if equipment_data:
                    equipment_list.append(equipment_data)
                time.sleep(1)  # Be respectful to the server
            except Exception as e:
                print(f"  Error extracting {url}: {e}")
                continue

        return equipment_list

    def extract_equipment_details(self, url, category_name):
        """Extract details from an equipment page"""
        self.driver.get(url)
        time.sleep(2)

        try:
            # Extract equipment name
            name_el = self.driver.find_element(By.XPATH, "//h1 | //h2[contains(@class, 'title')]")
            name = name_el.text.strip()

            # Extract category/type
            try:
                category_el = self.driver.find_element(By.XPATH, "//span[contains(@class, 'category')] | //div[contains(@class, 'category')]")
                equipment_type = category_el.text.strip()
            except:
                equipment_type = category_name

            # Extract pricing
            price_daily = None
            price_weekly = None
            price_monthly = None

            try:
                day_price_el = self.driver.find_element(By.XPATH, "//*[contains(text(), '/ day')]")
                price_daily = day_price_el.text.split('/')[0].strip().replace('$', '').replace(',', '')
            except:
                pass

            try:
                week_price_el = self.driver.find_element(By.XPATH, "//*[contains(text(), '/ week') and not(contains(text(), '4-week'))]")
                price_weekly = week_price_el.text.split('/')[0].strip().replace('$', '').replace(',', '')
            except:
                pass

            try:
                month_price_el = self.driver.find_element(By.XPATH, "//*[contains(text(), '/ 4-week')]")
                price_monthly = month_price_el.text.split('/')[0].strip().replace('$', '').replace(',', '')
            except:
                pass

            # Extract specs
            specs = {}
            try:
                # Look for specs table
                spec_rows = self.driver.find_elements(By.XPATH, "//table//tr | //div[contains(@class, 'spec')]//tr")
                for row in spec_rows:
                    cells = row.find_elements(By.TAG_NAME, 'td')
                    if len(cells) >= 2:
                        key = cells[0].text.strip()
                        value = cells[1].text.strip()
                        if key and value:
                            specs[key] = value
            except:
                pass

            # Extract models
            brand_models = []
            try:
                model_headers = self.driver.find_elements(By.XPATH, "//th[contains(text(), 'MEC') or contains(text(), 'JLG') or contains(text(), 'GENIE') or contains(text(), 'CAT') or contains(text(), 'BOBCAT')]")
                for header in model_headers:
                    brand = header.text.strip()
                    # Try to find model number in the row below
                    try:
                        model_row = header.find_element(By.XPATH, "./ancestor::thead/following-sibling::tbody//tr[1]//td[position()=count(./ancestor::table//th[text()='" + brand + "']/preceding-sibling::*)+1]")
                        model = model_row.text.strip()
                        if model:
                            brand_models.append(f"{brand} {model}")
                    except:
                        brand_models.append(brand)
            except:
                pass

            return {
                "category": category_name,
                "equipment_type": equipment_type,
                "name": name,
                "brand_model": ", ".join(brand_models) if brand_models else None,
                "price_daily": int(price_daily) if price_daily and price_daily.isdigit() else None,
                "price_weekly": int(price_weekly) if price_weekly and price_weekly.isdigit() else None,
                "price_monthly": int(price_monthly) if price_monthly and price_monthly.isdigit() else None,
                "specs": str(specs) if specs else None,
                "url": url
            }

        except Exception as e:
            print(f"    Error extracting details: {e}")
            return None

    def run(self):
        """Main extraction process"""
        try:
            self.setup_driver()
            self.set_location()

            categories = [
                {
                    "url": "https://www.equipmentshare.com/rent/categories/aerial-work-platform",
                    "name": "Aerial Work Platforms",
                    "output_file": "equipmentshare_aerial.json"
                },
                {
                    "url": "https://www.equipmentshare.com/rent/categories/earthmoving",
                    "name": "Earthmoving",
                    "output_file": "equipmentshare_earthmoving.json"
                },
                {
                    "url": "https://www.equipmentshare.com/rent/categories/forklifts-material-handling",
                    "name": "Forklifts & Material Handling",
                    "output_file": "equipmentshare_material_handling.json"
                }
            ]

            for category in categories:
                print(f"\n=== Extracting {category['name']} ===")
                equipment = self.extract_category_equipment(category['url'], category['name'])

                # Save to JSON
                with open(category['output_file'], 'w') as f:
                    json.dump(equipment, f, indent=2)
                print(f"Saved {len(equipment)} items to {category['output_file']}")

        finally:
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    scraper = EquipmentShareScraper()
    scraper.run()
    print("\n=== Extraction Complete ===")
