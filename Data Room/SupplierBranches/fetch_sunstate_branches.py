#!/usr/bin/env python3
"""
Script to fetch Sunstate Equipment branch data from their website.
This script will visit each branch page and extract detailed information.
"""

import requests
import json
import re
import time
from bs4 import BeautifulSoup
from urllib.parse import quote

# All 108 Sunstate branch URLs
BRANCH_URLS = [
    # Arizona (13 branches)
    "https://www.sunstateequip.com/locations/AZ/Apache%20Jct/APA",
    "https://www.sunstateequip.com/locations/AZ/Buckeye/BUC",
    "https://www.sunstateequip.com/locations/AZ/Casa%20Grande/CAS",
    "https://www.sunstateequip.com/locations/AZ/Phoenix/DRV",  # Deer Valley
    "https://www.sunstateequip.com/locations/AZ/Flagstaff/FLG",
    "https://www.sunstateequip.com/locations/AZ/Mesa/MES",
    "https://www.sunstateequip.com/locations/AZ/Peoria/PEO",
    "https://www.sunstateequip.com/locations/AZ/Phoenix/PHX",
    "https://www.sunstateequip.com/locations/AZ/Prescott%20Valley/PRS",
    "https://www.sunstateequip.com/locations/AZ/Scottsdale/SDL",
    "https://www.sunstateequip.com/locations/AZ/Phoenix/720",  # Trench - Phoenix
    "https://www.sunstateequip.com/locations/AZ/Tucson/721",  # Trench - Tucson
    "https://www.sunstateequip.com/locations/AZ/Tucson/TUC",

    # California (19 branches)
    "https://www.sunstateequip.com/locations/CA/Anaheim/ANA",
    "https://www.sunstateequip.com/locations/CA/Benicia/BEN",
    "https://www.sunstateequip.com/locations/CA/Burbank/BUR",
    "https://www.sunstateequip.com/locations/CA/Gardena/CSN",  # Carson
    "https://www.sunstateequip.com/locations/CA/Colton/COL",
    "https://www.sunstateequip.com/locations/CA/El%20Cajon/ELC",
    "https://www.sunstateequip.com/locations/CA/Fremont/FRE",
    "https://www.sunstateequip.com/locations/CA/Los%20Angeles/MON",  # Montebello
    "https://www.sunstateequip.com/locations/CA/Oakland/OAK",
    "https://www.sunstateequip.com/locations/CA/Romoland/ROM",
    "https://www.sunstateequip.com/locations/CA/Roseville/ROS",
    "https://www.sunstateequip.com/locations/CA/Sacramento/SAC",
    "https://www.sunstateequip.com/locations/CA/San%20Diego/SND",
    "https://www.sunstateequip.com/locations/CA/San%20Jose/SNJ",
    "https://www.sunstateequip.com/locations/CA/Stockton/STO",
    "https://www.sunstateequip.com/locations/CA/Baldwin%20Park/730",  # Trench - Baldwin Park
    "https://www.sunstateequip.com/locations/CA/Romoland/731",  # Trench - Romoland
    "https://www.sunstateequip.com/locations/CA/San%20Bernardino/732",  # Trench - San Bernardino
    "https://www.sunstateequip.com/locations/CA/San%20Diego/733",  # Trench - San Diego

    # Colorado (7 branches)
    "https://www.sunstateequip.com/locations/CO/Colorado%20Springs/COS",
    "https://www.sunstateequip.com/locations/CO/Denver/DEN",
    "https://www.sunstateequip.com/locations/CO/Denver/DVY",  # Dove Valley
    "https://www.sunstateequip.com/locations/CO/Fort%20Collins/FTC",
    "https://www.sunstateequip.com/locations/CO/Grand%20Junction/GRJ",
    "https://www.sunstateequip.com/locations/CO/Mead/MEA",
    "https://www.sunstateequip.com/locations/CO/Pueblo/PUE",

    # Florida (5 branches)
    "https://www.sunstateequip.com/locations/FL/Bradenton/BRA",
    "https://www.sunstateequip.com/locations/FL/Jacksonville/JAX",
    "https://www.sunstateequip.com/locations/FL/Orlando/ORL",
    "https://www.sunstateequip.com/locations/FL/Tampa/TAM",
    "https://www.sunstateequip.com/locations/FL/Jacksonville/740",  # Trench - Jacksonville

    # Georgia (5 branches)
    "https://www.sunstateequip.com/locations/GA/Buford/BUF",
    "https://www.sunstateequip.com/locations/GA/Conley/CON",
    "https://www.sunstateequip.com/locations/GA/Marietta/MAR",
    "https://www.sunstateequip.com/locations/GA/Atlanta/750",  # Trench - Atlanta
    "https://www.sunstateequip.com/locations/GA/Gainesville/751",  # Trench - Gainesville

    # Louisiana (2 branches)
    "https://www.sunstateequip.com/locations/LA/Baton%20Rouge/BTR",
    "https://www.sunstateequip.com/locations/LA/Sulphur/SUL",

    # North Carolina (5 branches)
    "https://www.sunstateequip.com/locations/NC/Charlotte/CHA",
    "https://www.sunstateequip.com/locations/NC/Greensboro/GBO",
    "https://www.sunstateequip.com/locations/NC/Raleigh/RAL",
    "https://www.sunstateequip.com/locations/NC/Charlotte/760",  # Trench - Charlotte
    "https://www.sunstateequip.com/locations/NC/Raleigh/761",  # Trench - Raleigh

    # New Mexico (1 branch)
    "https://www.sunstateequip.com/locations/NM/Rio%20Rancho/RIO",

    # Nevada (2 branches)
    "https://www.sunstateequip.com/locations/NV/Las%20Vegas/LAS",
    "https://www.sunstateequip.com/locations/NV/Reno/REN",

    # Oklahoma (2 branches)
    "https://www.sunstateequip.com/locations/OK/Oklahoma%20City/OKC",
    "https://www.sunstateequip.com/locations/OK/Tulsa/TUL",

    # Oregon (3 branches)
    "https://www.sunstateequip.com/locations/OR/Portland/POR",
    "https://www.sunstateequip.com/locations/OR/Portland/770",  # Trench - Portland
    "https://www.sunstateequip.com/locations/OR/Salem/771",  # Trench - Salem

    # South Carolina (1 branch)
    "https://www.sunstateequip.com/locations/SC/North%20Charleston/NTC",

    # Tennessee (3 branches)
    "https://www.sunstateequip.com/locations/TN/La%20Vergne/LAV",
    "https://www.sunstateequip.com/locations/TN/Memphis/MEM",
    "https://www.sunstateequip.com/locations/TN/Nashville/NAS",

    # Texas (30 branches)
    "https://www.sunstateequip.com/locations/TX/Austin/AUS",
    "https://www.sunstateequip.com/locations/TX/Balch%20Springs/BAL",
    "https://www.sunstateequip.com/locations/TX/Beaumont/BEA",
    "https://www.sunstateequip.com/locations/TX/Bryan/BRY",
    "https://www.sunstateequip.com/locations/TX/Buda/BUD",
    "https://www.sunstateequip.com/locations/TX/Carrollton/CAR",
    "https://www.sunstateequip.com/locations/TX/Conroe/CNR",
    "https://www.sunstateequip.com/locations/TX/Corpus%20Christi/CRP",
    "https://www.sunstateequip.com/locations/TX/Duncanville/DUN",
    "https://www.sunstateequip.com/locations/TX/El%20Paso/ELP",
    "https://www.sunstateequip.com/locations/TX/Fort%20Worth/FTW",
    "https://www.sunstateequip.com/locations/TX/Fort%20Worth/FWS",  # Fort Worth - South
    "https://www.sunstateequip.com/locations/TX/Freeport/FPT",
    "https://www.sunstateequip.com/locations/TX/Friendswood/FRW",
    "https://www.sunstateequip.com/locations/TX/Houston/HOU",
    "https://www.sunstateequip.com/locations/TX/Houston/HO2",  # Houston-2
    "https://www.sunstateequip.com/locations/TX/Houston/HO4",  # Houston-4
    "https://www.sunstateequip.com/locations/TX/Killeen/KIL",
    "https://www.sunstateequip.com/locations/TX/Krum/KRU",
    "https://www.sunstateequip.com/locations/TX/La%20Porte/LAP",
    "https://www.sunstateequip.com/locations/TX/McKinney/MCK",
    "https://www.sunstateequip.com/locations/TX/Odessa/ODE",
    "https://www.sunstateequip.com/locations/TX/Rosenberg/RSB",
    "https://www.sunstateequip.com/locations/TX/San%20Antonio/SAT",
    "https://www.sunstateequip.com/locations/TX/Southlake/SLK",
    "https://www.sunstateequip.com/locations/TX/El%20Paso/780",  # Trench - El Paso
    "https://www.sunstateequip.com/locations/TX/Austin/781",  # Trench - Austin
    "https://www.sunstateequip.com/locations/TX/Fort%20Worth/782",  # Trench - Dallas-Fort Worth
    "https://www.sunstateequip.com/locations/TX/Houston/783",  # Trench - Houston
    "https://www.sunstateequip.com/locations/TX/San%20Antonio/784",  # Trench - San Antonio

    # Utah (3 branches)
    "https://www.sunstateequip.com/locations/UT/Lindon/LIN",
    "https://www.sunstateequip.com/locations/UT/Ogden/OGD",
    "https://www.sunstateequip.com/locations/UT/Salt%20Lake%20City/SLC",

    # Washington (7 branches)
    "https://www.sunstateequip.com/locations/WA/Kent/KNT",
    "https://www.sunstateequip.com/locations/WA/Lakewood/LKW",
    "https://www.sunstateequip.com/locations/WA/Kent/790",  # Trench - Kent
    "https://www.sunstateequip.com/locations/WA/Olympia/791",  # Trench - Olympia
    "https://www.sunstateequip.com/locations/WA/Pasco/792",  # Trench - Pasco
    "https://www.sunstateequip.com/locations/WA/Woodinville/793",  # Trench - Woodinville
    "https://www.sunstateequip.com/locations/WA/Woodinville/WDV",
]

def extract_branch_data(html_content, url):
    """Extract branch data from HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text(separator='\n')

    # Get branch name from h1
    h1 = soup.find('h1')
    branch_name = h1.get_text().strip() if h1 else ''

    # Determine service type
    services = 'General Rental'
    if 'Trench Safety' in text or 'Trench Safety & Shoring' in text:
        services = 'Trench Safety'

    # Extract address using regex
    # Pattern: street address followed by city, state zip
    address_pattern = r'\n\n(\d+[^\n]+)\n\n([^,\n]+),\s*([A-Z]{2})\s+(\d{5})\n'
    match = re.search(address_pattern, text)

    address = ''
    city = ''
    state = ''
    zip_code = ''

    if match:
        address = match.group(1).strip()
        city = match.group(2).strip()
        state = match.group(3)
        zip_code = match.group(4)

    # Extract phone number
    phone = ''
    phone_pattern = r'Phone Number\n\n(\d{3}[.\-]\d{3}[.\-]\d{4})'
    phone_match = re.search(phone_pattern, text)
    if phone_match:
        phone = phone_match.group(1)

    return {
        'branch_name': branch_name,
        'address': address,
        'city': city,
        'state': state,
        'zip': zip_code,
        'phone': phone,
        'services': services
    }

def fetch_all_branches():
    """Fetch data for all branches."""
    all_branches = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }

    print(f"Fetching {len(BRANCH_URLS)} branches...")

    for i, url in enumerate(BRANCH_URLS):
        try:
            print(f"  [{i+1}/{len(BRANCH_URLS)}] Fetching: {url}")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            branch_data = extract_branch_data(response.text, url)
            all_branches.append(branch_data)

            # Be nice to the server
            time.sleep(0.5)

            # Save progress every 20 branches
            if (i + 1) % 20 == 0:
                print(f"    Saving progress... ({i+1} branches)")
                save_branches(all_branches, 'sunstate_branches_partial.json')

        except Exception as e:
            print(f"    Error fetching {url}: {e}")
            all_branches.append({
                'branch_name': '',
                'address': '',
                'city': '',
                'state': '',
                'zip': '',
                'phone': '',
                'services': '',
                'error': str(e),
                'url': url
            })

    return all_branches

def save_branches(branches, filename):
    """Save branches to JSON file."""
    filepath = f'/Users/vinuraabeysundara/Desktop/ICG/DOZR/SupplierBranches/{filename}'
    with open(filepath, 'w') as f:
        json.dump(branches, f, indent=2)
    print(f"Saved {len(branches)} branches to {filepath}")

if __name__ == '__main__':
    branches = fetch_all_branches()
    save_branches(branches, 'sunstate_all_branches.json')

    # Print summary
    print(f"\nSummary:")
    print(f"  Total branches: {len(branches)}")

    # Count by state
    state_counts = {}
    for b in branches:
        state = b.get('state', 'Unknown')
        state_counts[state] = state_counts.get(state, 0) + 1

    print(f"  By state:")
    for state, count in sorted(state_counts.items()):
        print(f"    {state}: {count}")
