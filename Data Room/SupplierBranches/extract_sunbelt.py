#!/usr/bin/env python3
"""
Extract all Sunbelt Rentals branch data from their website.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
import os

BASE_URL = "https://www.sunbeltrentals.com"
OUTPUT_FILE = "/Users/vinuraabeysundara/Desktop/ICG/DOZR/SupplierBranches/sunbelt_web_branches.json"

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/html, */*',
    'Accept-Language': 'en-US,en;q=0.9'
}

def get_page(url, as_json=False):
    """Fetch a page with retry logic"""
    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                return response.json() if as_json else response.text
            print(f"  Status {response.status_code} for {url}")
        except Exception as e:
            print(f"  Error: {e}")
        time.sleep(2)
    return None

def extract_from_api():
    """Try to extract from Sunbelt's location API"""
    # Sunbelt uses a store locator API
    api_url = "https://www.sunbeltrentals.com/api/locations"

    # Try different API endpoints
    endpoints = [
        "/api/locations",
        "/api/storelocator/stores",
        "/api/v1/locations",
        "/locations/api/search"
    ]

    for endpoint in endpoints:
        url = BASE_URL + endpoint
        print(f"Trying API: {url}")
        data = get_page(url, as_json=True)
        if data:
            print(f"  Got response: {type(data)}")
            return data

    return None

def extract_from_sitemap():
    """Extract location URLs from sitemap"""
    sitemap_url = f"{BASE_URL}/sitemap.xml"
    print(f"Checking sitemap: {sitemap_url}")

    html = get_page(sitemap_url)
    if not html:
        return []

    # Find location URLs in sitemap
    location_urls = re.findall(r'<loc>(https://www\.sunbeltrentals\.com/locations/[^<]+)</loc>', html)
    print(f"Found {len(location_urls)} location URLs in sitemap")
    return location_urls

def extract_from_directory():
    """Extract from the locations directory page"""
    url = f"{BASE_URL}/locations/"
    print(f"Checking directory: {url}")

    html = get_page(url)
    if not html:
        return []

    soup = BeautifulSoup(html, 'html.parser')

    # Look for state/region links
    branches = []

    # Try to find location cards or links
    location_links = soup.find_all('a', href=re.compile(r'/locations/'))
    print(f"Found {len(location_links)} location links")

    for link in location_links[:50]:  # Check first 50
        href = link.get('href', '')
        text = link.get_text(strip=True)
        print(f"  {text}: {href}")

    return branches

def extract_by_state():
    """Extract branches by visiting each state page"""
    # US state codes
    states = [
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
        'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
        'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
        'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC'
    ]

    all_branches = []

    for state in states:
        # Try state-specific URL
        url = f"{BASE_URL}/locations/{state.lower()}/"
        print(f"\nChecking {state}: {url}")

        html = get_page(url)
        if not html:
            continue

        soup = BeautifulSoup(html, 'html.parser')

        # Look for location cards
        cards = soup.find_all('div', class_=re.compile(r'location|store|branch', re.I))

        for card in cards:
            try:
                name_el = card.find(['h2', 'h3', 'h4', 'a'])
                name = name_el.get_text(strip=True) if name_el else ''

                # Get address
                addr_el = card.find(class_=re.compile(r'address|street', re.I))
                address = addr_el.get_text(strip=True) if addr_el else ''

                # Get phone
                phone_el = card.find('a', href=re.compile(r'^tel:'))
                phone = phone_el.get_text(strip=True) if phone_el else ''

                if name:
                    all_branches.append({
                        'branch_name': name,
                        'address': address,
                        'city': '',
                        'state': state,
                        'zip': '',
                        'phone': phone,
                        'services': ''
                    })
            except Exception as e:
                print(f"  Error: {e}")

        if cards:
            print(f"  Found {len(cards)} locations in {state}")

        time.sleep(0.5)

    return all_branches

def scrape_location_finder():
    """Use the location finder with coordinates to get all locations"""
    # Sunbelt's location finder likely uses lat/lng coordinates
    # We'll query major cities across the US

    major_cities = [
        (40.7128, -74.0060, "New York"),     # NYC
        (34.0522, -118.2437, "Los Angeles"), # LA
        (41.8781, -87.6298, "Chicago"),      # Chicago
        (29.7604, -95.3698, "Houston"),      # Houston
        (33.4484, -112.0740, "Phoenix"),     # Phoenix
        (29.4241, -98.4936, "San Antonio"),  # San Antonio
        (32.7767, -96.7970, "Dallas"),       # Dallas
        (37.7749, -122.4194, "San Francisco"), # SF
        (47.6062, -122.3321, "Seattle"),     # Seattle
        (39.7392, -104.9903, "Denver"),      # Denver
        (25.7617, -80.1918, "Miami"),        # Miami
        (33.7490, -84.3880, "Atlanta"),      # Atlanta
        (42.3601, -71.0589, "Boston"),       # Boston
        (38.9072, -77.0369, "Washington DC"), # DC
    ]

    all_branches = []
    seen_names = set()

    for lat, lng, city_name in major_cities:
        # Try store locator API with coordinates
        api_url = f"{BASE_URL}/api/storelocator/search?latitude={lat}&longitude={lng}&radius=500"
        print(f"\nSearching near {city_name}...")

        data = get_page(api_url, as_json=True)
        if data and isinstance(data, list):
            for store in data:
                name = store.get('name', store.get('storeName', ''))
                if name and name not in seen_names:
                    seen_names.add(name)
                    all_branches.append({
                        'branch_name': name,
                        'address': store.get('address', store.get('street', '')),
                        'city': store.get('city', ''),
                        'state': store.get('state', ''),
                        'zip': store.get('zip', store.get('postalCode', '')),
                        'phone': store.get('phone', ''),
                        'services': store.get('services', store.get('categories', ''))
                    })
            print(f"  Found {len(data)} locations")
        elif data and isinstance(data, dict):
            stores = data.get('stores', data.get('locations', data.get('results', [])))
            for store in stores:
                name = store.get('name', store.get('storeName', ''))
                if name and name not in seen_names:
                    seen_names.add(name)
                    all_branches.append({
                        'branch_name': name,
                        'address': store.get('address', store.get('street', '')),
                        'city': store.get('city', ''),
                        'state': store.get('state', ''),
                        'zip': store.get('zip', store.get('postalCode', '')),
                        'phone': store.get('phone', ''),
                        'services': store.get('services', '')
                    })
            print(f"  Found {len(stores)} locations")

        time.sleep(1)

    return all_branches

def main():
    print("Sunbelt Rentals Branch Extraction")
    print("=" * 50)

    all_branches = []

    # Method 1: Try API
    print("\n1. Trying API endpoints...")
    api_data = extract_from_api()

    # Method 2: Try sitemap
    print("\n2. Checking sitemap...")
    sitemap_urls = extract_from_sitemap()

    # Method 3: Try location finder with coordinates
    print("\n3. Trying location finder API...")
    finder_branches = scrape_location_finder()
    all_branches.extend(finder_branches)

    # Method 4: Try state-by-state
    if len(all_branches) < 100:
        print("\n4. Trying state-by-state extraction...")
        state_branches = extract_by_state()
        all_branches.extend(state_branches)

    # Method 5: Try directory page
    if len(all_branches) < 100:
        print("\n5. Checking directory page...")
        dir_branches = extract_from_directory()
        all_branches.extend(dir_branches)

    # Remove duplicates
    seen = set()
    unique_branches = []
    for b in all_branches:
        key = (b['branch_name'], b.get('address', ''))
        if key not in seen:
            seen.add(key)
            unique_branches.append(b)

    print(f"\n" + "=" * 50)
    print(f"TOTAL: {len(unique_branches)} unique branches found")

    if unique_branches:
        # Save results
        output_data = {
            'supplier': 'Sunbelt Rentals',
            'extraction_date': '2026-02-19',
            'extraction_method': 'Web scraping',
            'total_branches': len(unique_branches),
            'branches': unique_branches
        }

        with open(OUTPUT_FILE, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"Saved to: {OUTPUT_FILE}")
    else:
        print("No branches extracted - Sunbelt may require browser automation")
        print("Their site likely uses JavaScript rendering or requires authentication")

if __name__ == "__main__":
    main()
