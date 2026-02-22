#!/usr/bin/env python3
"""Convert OMS supplier CSV files to JSON format with complete branch details."""

import csv
import json
import re
from pathlib import Path

# Define file mappings
CSV_FILES = {
    "Sunstate-Equipment-Co-19-Feb-26.csv": ("sunstate_oms_branches.json", "Sunstate Equipment Co."),
    "Herc-Rentals-19-Feb-26.csv": ("herc_oms_branches.json", "Herc Rentals"),
    "Sunbelt-Rental--Inc-19-Feb-26.csv": ("sunbelt_oms_branches.json", "Sunbelt Rentals"),
    "Equipment-Share-Inc-19-Feb-26.csv": ("equipmentshare_oms_branches.json", "EquipmentShare"),
}

# US state mappings (full name to abbreviation)
US_STATES = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY"
}

# Canadian provinces (full name to abbreviation)
CA_PROVINCES = {
    "Alberta": "AB", "British Columbia": "BC", "Manitoba": "MB",
    "New Brunswick": "NB", "Newfoundland and Labrador": "NL",
    "Northwest Territories": "NT", "Nova Scotia": "NS", "Nunavut": "NU",
    "Ontario": "ON", "Prince Edward Island": "PE", "Quebec": "QC",
    "Saskatchewan": "SK", "Yukon": "YT"
}

# All valid state/province abbreviations
ALL_STATE_ABBREVS = set(US_STATES.values()) | set(CA_PROVINCES.values())


def extract_state_from_branch_name(branch_name):
    """Extract state abbreviation from branch name like 'Sunstate Equipment - Houston TX'."""
    if not branch_name:
        return None

    # Look for 2-letter state code at the end of the branch name
    # Pattern: ends with space + 2 uppercase letters, or has state code before location details
    match = re.search(r'\b([A-Z]{2})\s*(?:\([^)]*\))?\s*$', branch_name)
    if match:
        state = match.group(1)
        if state in ALL_STATE_ABBREVS:
            return state

    # Also check for pattern like "City ST" anywhere in name
    match = re.search(r'\b\w+\s+([A-Z]{2})\b', branch_name)
    if match:
        state = match.group(1)
        if state in ALL_STATE_ABBREVS:
            return state

    return None


def parse_address(address_str, branch_name=None):
    """Parse branchAddress into components: street, city, state, zip."""
    if not address_str:
        return {"street": "", "city": "", "state": "", "zip": ""}

    parts = [p.strip() for p in address_str.split(",")]

    result = {
        "street": "",
        "city": "",
        "state": "",
        "zip": ""
    }

    # Common patterns:
    # "5121 Oates Road, Houston, Texas, United States, 77013"
    # "12905 Garvey Ave, Baldwin Park, US"
    # "4460 Moreland Ave, Conley, US"
    # "West 1350 South, Ogden, Utah, United States, 84401"

    if len(parts) >= 1:
        result["street"] = parts[0]

    if len(parts) >= 2:
        result["city"] = parts[1]

    # Look for state and zip
    for i, part in enumerate(parts):
        part_clean = part.strip()

        if part_clean in US_STATES:
            result["state"] = US_STATES[part_clean]
        elif part_clean in US_STATES.values():
            result["state"] = part_clean
        elif part_clean in CA_PROVINCES:
            result["state"] = CA_PROVINCES[part_clean]
        elif part_clean in CA_PROVINCES.values():
            result["state"] = part_clean

        # Check for zip code (5 digits or 5+4 format)
        zip_match = re.search(r'\b(\d{5}(-\d{4})?)\b', part_clean)
        if zip_match:
            result["zip"] = zip_match.group(1)

        # Canadian postal code
        ca_zip_match = re.search(r'\b([A-Z]\d[A-Z]\s?\d[A-Z]\d)\b', part_clean, re.IGNORECASE)
        if ca_zip_match:
            result["zip"] = ca_zip_match.group(1).upper()

    # If state not found in address, try to extract from branch name
    if not result["state"] and branch_name:
        state_from_name = extract_state_from_branch_name(branch_name)
        if state_from_name:
            result["state"] = state_from_name

    # Validate zip - make sure it's not picking up street numbers
    if result["zip"] and len(result["zip"]) == 5:
        # If the zip appears in the street address, it's probably wrong
        if result["zip"] in result["street"]:
            result["zip"] = ""

    return result


def format_phone(phone_str):
    """Clean and format phone number."""
    if not phone_str:
        return ""

    # Remove common prefixes and clean
    phone = phone_str.strip()
    phone = re.sub(r'^\+1', '', phone)
    phone = re.sub(r'^1', '', phone)

    # Extract digits
    digits = re.sub(r'\D', '', phone)

    if len(digits) == 10:
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"{digits[1:4]}-{digits[4:7]}-{digits[7:]}"

    return phone_str.strip()


def convert_csv_to_json(csv_path, output_path, supplier_display_name):
    """Convert a single CSV file to JSON format."""
    branches = []
    oms_enabled_count = 0

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Parse address (pass branch name for state inference)
            addr = parse_address(row.get('branchAddress', ''), row.get('branchName', ''))

            # Check OMS enabled
            oms_enabled = row.get('omsEnabled', '').upper() == 'TRUE'
            if oms_enabled:
                oms_enabled_count += 1

            # Build hours object
            hours = {}
            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            for day in days:
                hours_val = row.get(f'hours{day.capitalize()}', '')
                hours[day] = hours_val if hours_val else None

            # Get first email from OMS email addresses
            oms_emails = row.get('omsEmailAddresses', '')
            email = oms_emails.split(',')[0].strip() if oms_emails else row.get('branchEmailAddress', '')

            branch = {
                "branch_id": row.get('branchId', ''),
                "branch_name": row.get('branchName', ''),
                "address": addr["street"],
                "city": addr["city"],
                "state": addr["state"],
                "zip": addr["zip"],
                "phone": format_phone(row.get('branchPhoneNumber', '')),
                "email": email.strip() if email else "",
                "oms_enabled": oms_enabled,
                "hours": hours
            }

            branches.append(branch)

    # Build output JSON
    output = {
        "supplier": supplier_display_name,
        "source": "OMS Export",
        "export_date": "2026-02-19",
        "total_branches": len(branches),
        "oms_enabled_count": oms_enabled_count,
        "branches": branches
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    return len(branches), oms_enabled_count


def main():
    base_dir = Path(__file__).parent

    print("Converting OMS supplier CSV files to JSON...")
    print("=" * 60)

    for csv_name, (json_name, display_name) in CSV_FILES.items():
        csv_path = base_dir / csv_name
        json_path = base_dir / json_name

        if not csv_path.exists():
            print(f"WARNING: {csv_name} not found, skipping...")
            continue

        total, enabled = convert_csv_to_json(csv_path, json_path, display_name)
        print(f"{display_name}:")
        print(f"  Total branches: {total}")
        print(f"  OMS enabled: {enabled}")
        print(f"  Output: {json_name}")
        print()

    print("=" * 60)
    print("Conversion complete!")


if __name__ == "__main__":
    main()
