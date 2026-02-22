#!/usr/bin/env python3
"""
Extract all EquipmentShare branch data from their website.
Uses requests + BeautifulSoup for efficient extraction.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
import os

BASE_URL = "https://www.equipmentshare.com"
OUTPUT_FILE = "/Users/vinuraabeysundara/Desktop/ICG/DOZR/SupplierBranches/equipmentshare_web_branches.json"
PROGRESS_FILE = "/Users/vinuraabeysundara/Desktop/ICG/DOZR/SupplierBranches/equipmentshare_progress.txt"

# States to skip (already captured)
COMPLETED_STATES = ["AL"]  # Alabama already done

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_page(url):
    """Fetch a page with retry logic"""
    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                return response.text
            print(f"  Status {response.status_code} for {url}")
        except Exception as e:
            print(f"  Error: {e}")
        time.sleep(2)
    return None

def extract_states():
    """Get all state URLs from the directory page"""
    html = get_page(f"{BASE_URL}/location-directory")
    if not html:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    states = []

    for link in soup.find_all('a', href=re.compile(r'/location-directory/[a-z]{2}$')):
        href = link.get('href')
        text = link.get_text(strip=True)
        match = re.match(r'^([A-Za-z\s]+)\s*\((\d+)\)?$', text)
        if match:
            state_name = match.group(1).strip()
            count = int(match.group(2))
        else:
            state_name = text
            count = 0

        state_code = href.split('/')[-1].upper()
        states.append({
            'name': state_name,
            'code': state_code,
            'url': BASE_URL + href,
            'expected_count': count
        })

    return states

def extract_cities(state_url, state_code):
    """Get all city URLs from a state page"""
    html = get_page(state_url)
    if not html:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    cities = []

    pattern = re.compile(rf'/location-directory/{state_code.lower()}/[a-z-]+$')
    for link in soup.find_all('a', href=pattern):
        href = link.get('href')
        city_name = link.get_text(strip=True)
        # Remove count if present
        city_name = re.sub(r'\s*\(\d+\)$', '', city_name)
        cities.append({
            'name': city_name,
            'url': BASE_URL + href
        })

    return cities

def extract_branches(city_url, state_code):
    """Extract all branch details from a city page"""
    html = get_page(city_url)
    if not html:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    branches = []

    # Find all branch containers
    branch_divs = soup.find_all('div', class_='location-directory__list--branch')

    for div in branch_divs:
        try:
            # Get branch name from h2
            h2 = div.find('h2')
            if not h2:
                continue
            branch_name = h2.get_text(strip=True)

            # Get phone from tel: link
            phone_link = div.find('a', href=re.compile(r'^tel:'))
            phone = phone_link.get_text(strip=True) if phone_link else ''

            # Get text content
            text = div.get_text('\n', strip=True)
            lines = [l.strip() for l in text.split('\n') if l.strip()]

            address = ''
            city = ''
            state = state_code
            zip_code = ''
            services = []

            for line in lines:
                # Skip branch name and phone
                if '#' in line or re.match(r'^\(\d{3}\)', line):
                    continue
                # Street address
                if re.match(r'^\d+\s+[A-Za-z]', line) and not address:
                    address = line
                # City, State Zip
                elif re.search(r',\s*[A-Z]{2}\s+\d{5}$', line):
                    m = re.match(r'^(.+),\s*([A-Z]{2})\s+(\d{5})$', line)
                    if m:
                        city = m.group(1).strip()
                        state = m.group(2)
                        zip_code = m.group(3)
                # Services
                elif line.endswith('Solutions'):
                    services.append(line)

            branches.append({
                'branch_name': branch_name,
                'services': ', '.join(services) if services else None,
                'address': address,
                'city': city,
                'state': state,
                'zip': zip_code,
                'phone': phone
            })
        except Exception as e:
            print(f"    Error parsing branch: {e}")

    return branches

def save_progress(state_code, branches_count):
    """Save progress to file"""
    with open(PROGRESS_FILE, 'a') as f:
        f.write(f"{state_code}: {branches_count} branches\n")

def main():
    print("EquipmentShare Branch Extraction")
    print("=" * 50)

    # Load existing data if any
    all_branches = []
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r') as f:
            data = json.load(f)
            all_branches = data.get('branches', [])
            print(f"Loaded {len(all_branches)} existing branches")

    # Get all states
    print("\nFetching state list...")
    states = extract_states()
    print(f"Found {len(states)} states")

    # Process each state
    for state in states:
        state_code = state['code']

        # Skip completed states
        if state_code in COMPLETED_STATES:
            print(f"\nSkipping {state['name']} ({state_code}) - already done")
            continue

        print(f"\n{state['name']} ({state_code}) - expecting {state['expected_count']} branches")

        # Get cities in this state
        cities = extract_cities(state['url'], state_code)
        print(f"  Found {len(cities)} cities")

        state_branches = []
        for city in cities:
            branches = extract_branches(city['url'], state_code)
            if branches:
                print(f"    {city['name']}: {len(branches)} branches")
                state_branches.extend(branches)
            time.sleep(0.5)  # Be nice to the server

        print(f"  Total: {len(state_branches)} branches from {state['name']}")
        all_branches.extend(state_branches)
        save_progress(state_code, len(state_branches))

        # Save after each state
        output_data = {
            'supplier': 'EquipmentShare',
            'extraction_date': '2026-02-19',
            'total_locations': len(all_branches),
            'branches': all_branches
        }
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"  Saved (total: {len(all_branches)} branches)")

    print("\n" + "=" * 50)
    print(f"COMPLETE: {len(all_branches)} total branches extracted")
    print(f"Output: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
