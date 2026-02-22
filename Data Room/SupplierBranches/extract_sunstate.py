#!/usr/bin/env python3
"""
Extract all Sunstate Equipment branch data from their website.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
import os

BASE_URL = "https://www.sunstateequip.com"
OUTPUT_FILE = "/Users/vinuraabeysundara/Desktop/ICG/DOZR/SupplierBranches/sunstate_web_branches.json"

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# State name mappings
STATE_CODES = {
    'AZ': 'Arizona', 'CA': 'California', 'CO': 'Colorado', 'FL': 'Florida',
    'GA': 'Georgia', 'LA': 'Louisiana', 'NC': 'North Carolina', 'NM': 'New Mexico',
    'NV': 'Nevada', 'OK': 'Oklahoma', 'OR': 'Oregon', 'SC': 'South Carolina',
    'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'WA': 'Washington'
}

def get_page(url):
    """Fetch a page with retry logic"""
    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                return response.text
        except Exception as e:
            print(f"  Error: {e}")
        time.sleep(1)
    return None

def get_all_branch_urls():
    """Get all branch URLs from the locations page"""
    url = f"{BASE_URL}/locations"
    html = get_page(url)
    if not html:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    branches = []

    # Find all branch links
    current_state = None
    for el in soup.find_all(['h4', 'a']):
        if el.name == 'h4':
            state_text = el.get_text(strip=True)
            if state_text and state_text != 'All Branches':
                current_state = state_text
        elif el.name == 'a' and current_state:
            href = el.get('href', '')
            text = el.get_text(strip=True)
            if '/locations/' in href and re.search(r'/[A-Z]{2}/', href):
                if text and text not in ['Visit page', 'Browse all locations'] and 'Set my branch' not in text:
                    branches.append({
                        'state_name': current_state,
                        'city': text,
                        'url': BASE_URL + href if href.startswith('/') else href
                    })

    return branches

def extract_branch_details(url, state_name, city_name):
    """Extract full details from a branch page"""
    html = get_page(url)
    if not html:
        return None

    soup = BeautifulSoup(html, 'html.parser')

    branch = {
        'branch_name': f"Sunstate Equipment - {city_name}",
        'address': '',
        'city': city_name,
        'state': state_name,
        'zip': '',
        'phone': '',
        'services': ''
    }

    # Look for address information
    # Try multiple selectors
    address_selectors = [
        '.location-address', '.address', '[class*="address"]',
        'div.branch-info', '.location-details'
    ]

    for selector in address_selectors:
        addr_el = soup.select_one(selector)
        if addr_el:
            text = addr_el.get_text('\n', strip=True)
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            for line in lines:
                # Street address
                if re.match(r'^\d+\s+[A-Za-z]', line) and not branch['address']:
                    branch['address'] = line
                # City, State Zip
                elif re.search(r',\s*[A-Z]{2}\s+\d{5}', line):
                    m = re.match(r'^(.+),\s*([A-Z]{2})\s+(\d{5})', line)
                    if m:
                        branch['city'] = m.group(1).strip()
                        branch['state'] = m.group(2)
                        branch['zip'] = m.group(3)
            break

    # Get phone from tel: link
    phone_link = soup.find('a', href=re.compile(r'^tel:'))
    if phone_link:
        branch['phone'] = phone_link.get_text(strip=True)

    # Also try to find address in the page text
    page_text = soup.get_text()

    # Look for phone pattern
    if not branch['phone']:
        phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', page_text)
        if phone_match:
            branch['phone'] = phone_match.group()

    # Look for address pattern
    if not branch['address']:
        addr_match = re.search(r'(\d+\s+[A-Za-z][A-Za-z\s]+(?:Road|Rd|Street|St|Avenue|Ave|Boulevard|Blvd|Drive|Dr|Way|Lane|Ln|Court|Ct))', page_text)
        if addr_match:
            branch['address'] = addr_match.group(1)

    # Look for zip code
    if not branch['zip']:
        zip_match = re.search(r'\b(\d{5})\b', page_text)
        if zip_match:
            branch['zip'] = zip_match.group(1)

    return branch

def main():
    print("Sunstate Equipment Branch Extraction")
    print("=" * 50)

    # Get all branch URLs
    print("\nFetching branch list...")
    branch_urls = get_all_branch_urls()
    print(f"Found {len(branch_urls)} branches")

    if not branch_urls:
        print("No branches found!")
        return

    # Extract details for each branch
    all_branches = []
    for i, branch_info in enumerate(branch_urls):
        url = branch_info['url']
        state = branch_info['state_name']
        city = branch_info['city']

        print(f"[{i+1}/{len(branch_urls)}] {city}, {state}...")

        details = extract_branch_details(url, state, city)
        if details:
            all_branches.append(details)

        # Save progress every 20 branches
        if (i + 1) % 20 == 0:
            save_data(all_branches)
            print(f"  Saved progress ({len(all_branches)} branches)")

        time.sleep(0.3)  # Be nice to the server

    # Final save
    save_data(all_branches)

    print("\n" + "=" * 50)
    print(f"COMPLETE: {len(all_branches)} branches extracted")
    print(f"Output: {OUTPUT_FILE}")

def save_data(branches):
    """Save branch data to JSON file"""
    output_data = {
        'supplier': 'Sunstate Equipment',
        'extraction_date': '2026-02-19',
        'extraction_method': 'Web scraping',
        'total_branches': len(branches),
        'branches': branches
    }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output_data, f, indent=2)

if __name__ == "__main__":
    main()
