#!/usr/bin/env python3
"""
Home Depot Store Extraction Script
Extracts all Home Depot stores from the Store Directory for Priority 1 states
"""

import urllib.request
import json
import re
import time
from datetime import datetime

# Priority 1 States (Zero OMS Coverage)
PRIORITY_1_STATES = [
    ("AK", "Alaska"), ("AL", "Alabama"), ("AR", "Arkansas"), ("DC", "District of Columbia"),
    ("HI", "Hawaii"), ("IA", "Iowa"), ("ID", "Idaho"), ("KY", "Kentucky"),
    ("ME", "Maine"), ("MN", "Minnesota"), ("MT", "Montana"), ("ND", "North Dakota"),
    ("NE", "Nebraska"), ("NV", "Nevada"), ("SD", "South Dakota"), ("VT", "Vermont"),
    ("WV", "West Virginia"), ("WY", "Wyoming")
]

# All US States
ALL_STATES = [
    ("AL", "Alabama"), ("AK", "Alaska"), ("AZ", "Arizona"), ("AR", "Arkansas"),
    ("CA", "California"), ("CO", "Colorado"), ("CT", "Connecticut"), ("DE", "Delaware"),
    ("DC", "District of Columbia"), ("FL", "Florida"), ("GA", "Georgia"), ("HI", "Hawaii"),
    ("ID", "Idaho"), ("IL", "Illinois"), ("IN", "Indiana"), ("IA", "Iowa"),
    ("KS", "Kansas"), ("KY", "Kentucky"), ("LA", "Louisiana"), ("ME", "Maine"),
    ("MD", "Maryland"), ("MA", "Massachusetts"), ("MI", "Michigan"), ("MN", "Minnesota"),
    ("MS", "Mississippi"), ("MO", "Missouri"), ("MT", "Montana"), ("NE", "Nebraska"),
    ("NV", "Nevada"), ("NH", "New Hampshire"), ("NJ", "New Jersey"), ("NM", "New Mexico"),
    ("NY", "New York"), ("NC", "North Carolina"), ("ND", "North Dakota"), ("OH", "Ohio"),
    ("OK", "Oklahoma"), ("OR", "Oregon"), ("PA", "Pennsylvania"), ("RI", "Rhode Island"),
    ("SC", "South Carolina"), ("SD", "South Dakota"), ("TN", "Tennessee"), ("TX", "Texas"),
    ("UT", "Utah"), ("VT", "Vermont"), ("VA", "Virginia"), ("WA", "Washington"),
    ("WV", "West Virginia"), ("WI", "Wisconsin"), ("WY", "Wyoming")
]

# Manually extracted Alaska data from browser
ALASKA_STORES = [
    {"store_name": "Anchorage", "address": "515 E Tudor Rd", "city": "Anchorage", "state": "AK", "zip": "99503", "phone": "(907)563-9800", "has_rentals": True},
    {"store_name": "NE Anchorage", "address": "400 Rodeo Place", "city": "Anchorage", "state": "AK", "zip": "99508", "phone": "(907)276-2006", "has_rentals": True},
    {"store_name": "SE Anchorage", "address": "1715 Abbott Road", "city": "Anchorage", "state": "AK", "zip": "99507", "phone": "(907)644-5646", "has_rentals": True},
    {"store_name": "Fairbanks", "address": "1301 Old Steese Hwy", "city": "Fairbanks", "state": "AK", "zip": "99701", "phone": "(907)451-9003", "has_rentals": True},
    {"store_name": "Wasilla", "address": "1255 E Palmer Wasilla Hwy", "city": "Wasilla", "state": "AK", "zip": "99654", "phone": "(907)357-8181", "has_rentals": True},
    {"store_name": "Kenai", "address": "10480 Spur Hwy", "city": "Kenai", "state": "AK", "zip": "99611", "phone": "(907)283-2228", "has_rentals": True},
    {"store_name": "Juneau", "address": "5201 Commercial Blvd", "city": "Juneau", "state": "AK", "zip": "99801", "phone": "(907)463-5034", "has_rentals": True},
]

# Alabama stores extracted from browser
ALABAMA_STORES = [
    {"store_name": "West Mobile", "address": "755 Schillinger Rd S", "city": "Mobile", "state": "AL", "zip": "36695", "phone": "(251)634-0351", "has_rentals": True},
    {"store_name": "Foley", "address": "2899 S Mckenzie St", "city": "Foley", "state": "AL", "zip": "36535", "phone": "(251)955-2401", "has_rentals": True},
    {"store_name": "Prattville", "address": "2710 Legends Parkway", "city": "Prattville", "state": "AL", "zip": "36066", "phone": "(334)285-1693", "has_rentals": True},
    {"store_name": "Dothan", "address": "3489 Ross Clark Cir", "city": "Dothan", "state": "AL", "zip": "36303", "phone": "(334)677-2790", "has_rentals": True},
    {"store_name": "East Montgomery", "address": "10655 Chantilly Pkwy", "city": "Montgomery", "state": "AL", "zip": "36117", "phone": "(334)260-8702", "has_rentals": True},
    {"store_name": "Auburn (Opelika)", "address": "2190 Tigertown Parkway", "city": "Opelika", "state": "AL", "zip": "36801", "phone": "(334)745-4242", "has_rentals": True},
    {"store_name": "Mobile", "address": "851 Montlimar Dr", "city": "Mobile", "state": "AL", "zip": "36609", "phone": "(251)380-0017", "has_rentals": True},
    {"store_name": "Oxford", "address": "350 Crystal Water Drive", "city": "Oxford", "state": "AL", "zip": "36203", "phone": "(256)832-2279", "has_rentals": True},
    {"store_name": "Hoover", "address": "3670 Galleria Circle", "city": "Birmingham", "state": "AL", "zip": "35244", "phone": "(205)988-8141", "has_rentals": True},
    {"store_name": "Fairfield", "address": "6405 Flintridge Dr", "city": "Fairfield", "state": "AL", "zip": "35064", "phone": "(205)781-0110", "has_rentals": True},
    {"store_name": "South Huntsville", "address": "10012 Memorial Pkwy Sw", "city": "Huntsville", "state": "AL", "zip": "35803", "phone": "(256)881-8270", "has_rentals": True},
    {"store_name": "Alexander City", "address": "1460 Hwy 280", "city": "Alexander City", "state": "AL", "zip": "35010", "phone": "(256)234-6399", "has_rentals": True},
    {"store_name": "West Huntsville", "address": "4045 Lawson Ridge Dr", "city": "Madison", "state": "AL", "zip": "35757", "phone": "(256)837-6658", "has_rentals": True},
    {"store_name": "North Huntsville", "address": "1035 Memorial Pkwy Nw", "city": "Huntsville", "state": "AL", "zip": "35801", "phone": "(256)536-2216", "has_rentals": True},
    {"store_name": "Sylacauga", "address": "41310 Us Hwy 280", "city": "Sylacauga", "state": "AL", "zip": "35150", "phone": "(256)245-4953", "has_rentals": True},
    {"store_name": "Jasper", "address": "1808 Hwy 78 E", "city": "Jasper", "state": "AL", "zip": "35501", "phone": "(205)221-0367", "has_rentals": True},
    {"store_name": "Scottsboro", "address": "24635 John T Reid Pkwy", "city": "Scottsboro", "state": "AL", "zip": "35768", "phone": "(256)575-2100", "has_rentals": True},
    {"store_name": "Phenix City", "address": "3784 Us Highway 431 N", "city": "Phenix City", "state": "AL", "zip": "36867", "phone": "(334)297-2045", "has_rentals": True},
    {"store_name": "Pell City", "address": "289 Vaughan Lane", "city": "Pell City", "state": "AL", "zip": "35125", "phone": "(205)338-1070", "has_rentals": True},
    {"store_name": "Inverness", "address": "4995 Highway 280", "city": "Birmingham", "state": "AL", "zip": "35242", "phone": "(205)995-9357", "has_rentals": True},
    {"store_name": "Tuscaloosa", "address": "1601 13th Ave East", "city": "Tuscaloosa", "state": "AL", "zip": "35404", "phone": "(205)633-2038", "has_rentals": True},
    {"store_name": "Eastwood", "address": "7001 Crestwood Blvd, Suite 1300", "city": "Birmingham", "state": "AL", "zip": "35210", "phone": "(205)595-7780", "has_rentals": True},
    {"store_name": "Montgomery", "address": "2312 Eastern Blvd", "city": "Montgomery", "state": "AL", "zip": "36117", "phone": "(334)272-8552", "has_rentals": True},
    {"store_name": "Decatur", "address": "1225 Wimberly Dr Sw", "city": "Decatur", "state": "AL", "zip": "35603", "phone": "(256)353-2031", "has_rentals": True},
    {"store_name": "Trussville", "address": "1600 Gadsden Hwy", "city": "Trussville", "state": "AL", "zip": "35173", "phone": "(205)661-9415", "has_rentals": True},
    {"store_name": "Florence", "address": "351 Seville St", "city": "Florence", "state": "AL", "zip": "35630", "phone": "(256)764-5037", "has_rentals": True},
    {"store_name": "Pelham", "address": "3191 Pelham Pkwy", "city": "Pelham", "state": "AL", "zip": "35124", "phone": "(205)685-1837", "has_rentals": True},
    {"store_name": "Daphne", "address": "7100 Hwy 90", "city": "Daphne", "state": "AL", "zip": "36526", "phone": "(251)625-0890", "has_rentals": True},
]


def save_progress(data, filename="homedepot_extraction_progress.json"):
    """Save extraction progress to JSON file"""
    filepath = f"/Users/vinuraabeysundara/Desktop/ICG/DOZR/SupplierBranches/{filename}"
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Progress saved to {filepath}")


def main():
    """Main extraction function"""
    print("=" * 60)
    print("HOME DEPOT STORE EXTRACTION")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Initialize data structure
    extraction_data = {
        "extraction_date": datetime.now().strftime("%Y-%m-%d"),
        "extraction_method": "browser_automation",
        "equipment_focus": ["Aerial & Lifting Equipment", "Earth-Moving Equipment"],
        "priority_1_states": [s[0] for s in PRIORITY_1_STATES],
        "states_data": {},
        "summary": {
            "total_stores": 0,
            "states_completed": 0,
            "states_remaining": len(PRIORITY_1_STATES)
        }
    }

    # Add Alaska data
    extraction_data["states_data"]["AK"] = {
        "state_name": "Alaska",
        "total_stores": len(ALASKA_STORES),
        "stores": ALASKA_STORES
    }
    extraction_data["summary"]["total_stores"] += len(ALASKA_STORES)
    extraction_data["summary"]["states_completed"] += 1
    extraction_data["summary"]["states_remaining"] -= 1

    print(f"\nAlaska: {len(ALASKA_STORES)} stores extracted")

    # Add Alabama data
    extraction_data["states_data"]["AL"] = {
        "state_name": "Alabama",
        "total_stores": len(ALABAMA_STORES),
        "stores": ALABAMA_STORES
    }
    extraction_data["summary"]["total_stores"] += len(ALABAMA_STORES)
    extraction_data["summary"]["states_completed"] += 1
    extraction_data["summary"]["states_remaining"] -= 1

    print(f"Alabama: {len(ALABAMA_STORES)} stores extracted")

    # Save progress
    save_progress(extraction_data)

    print("\n" + "=" * 60)
    print("EXTRACTION SUMMARY")
    print("=" * 60)
    print(f"Total stores extracted: {extraction_data['summary']['total_stores']}")
    print(f"States completed: {extraction_data['summary']['states_completed']}")
    print(f"States remaining: {extraction_data['summary']['states_remaining']}")
    print("\nNote: Remaining states require browser automation to extract.")
    print("=" * 60)


if __name__ == "__main__":
    main()
