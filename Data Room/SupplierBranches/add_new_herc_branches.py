#!/usr/bin/env python3
"""
Add new Herc branches extracted from Feb 19, 2026 session
"""

import json
import os

BASE_DIR = "/Users/vinuraabeysundara/Desktop/ICG/DOZR/SupplierBranches"

# New branches extracted this session
NEW_BRANCHES = [
    # Tulsa, OK (2)
    {"branch_number": "9459", "branch_name": "9459 - Tulsa, OK", "city": "Tulsa", "state": "OK", "zip": "74146", "phone": "918-221-3229", "services": "Earthmoving, General Rentals", "address": "4445 South Mingo Road"},
    {"branch_number": "4025", "branch_name": "4025 - Tulsa, OK", "city": "Tulsa", "state": "OK", "zip": "74107", "phone": "918-528-9023", "services": "General Rentals", "address": "5644 West 55th Street"},

    # Buffalo, NY (1)
    {"branch_number": "9147", "branch_name": "9147 - Buffalo, NY", "city": "Tonawanda", "state": "NY", "zip": "14150", "phone": "716-202-7840", "services": "General Rentals", "address": "125 Milens, NY"},

    # Syracuse, NY (1)
    {"branch_number": "9145", "branch_name": "9145 - Syracuse, NY", "city": "Liverpool", "state": "NY", "zip": "13088", "phone": "315-622-4939", "services": "General Rentals", "address": "4578 Buckley Road"},

    # Albany, NY (4)
    {"branch_number": "9539", "branch_name": "9539 - Albany, NY - PCT", "city": "Latham", "state": "NY", "zip": "12110", "phone": "844-222-5134", "services": "ProContractor", "address": "3 Avis Drive"},
    {"branch_number": "9569", "branch_name": "9569 - Albany, NY - ProSolutions", "city": "Latham", "state": "NY", "zip": "12110", "phone": "518-713-0805", "services": "ProSolutions", "address": "3 Avis Drive"},
    {"branch_number": "9139", "branch_name": "9139 - Albany, NY", "city": "Castleton-On-Hudson", "state": "NY", "zip": "12033", "phone": "518-957-4927", "services": "General Rentals", "address": "1200 US-9"},
    {"branch_number": "9682", "branch_name": "9682 - Albany NY - ProTruck", "city": "Albany", "state": "NY", "zip": "12203", "phone": "518-629-5008", "services": "ProTruck", "address": "120 Watervliet Ave"},

    # Hartford, CT (2)
    {"branch_number": "9267", "branch_name": "9267 - Bloomfield, CT", "city": "Bloomfield", "state": "CT", "zip": "06002", "phone": "860-901-2822", "services": "General Rentals", "address": "9 Belden Road"},
    {"branch_number": "9666", "branch_name": "9666 - Hartford, CT - ProTruck", "city": "Bloomfield", "state": "CT", "zip": "06002", "phone": "860-901-2822", "services": "ProTruck", "address": "9 Belden Road"},

    # Providence/Brockton, MA (2)
    {"branch_number": "9110", "branch_name": "9110 - Boston, MA - ProTruck", "city": "Brockton", "state": "MA", "zip": "02301", "phone": "774-539-4549", "services": "ProTruck", "address": "1675 Main Street"},
    {"branch_number": "9109", "branch_name": "9109 - Brockton, MA", "city": "Brockton", "state": "MA", "zip": "02301", "phone": "774-539-4549", "services": "General Rentals", "address": "1675 Main Street"},

    # Albuquerque, NM (2)
    {"branch_number": "4042", "branch_name": "4042 - Albuquerque", "city": "Albuquerque", "state": "NM", "zip": "87105", "phone": "505-990-1188", "services": "General Rentals", "address": "3801 Prince Street SE"},
    {"branch_number": "9604", "branch_name": "9604 - Albuquerque, NM", "city": "Albuquerque", "state": "NM", "zip": "87109", "phone": "505-887-1167", "services": "General Rentals", "address": "3601 Osuna Road NE"},

    # Milwaukee, WI (1)
    {"branch_number": "9141", "branch_name": "9141 - MILWAUKEE WI", "city": "OAK CREEK", "state": "WI", "zip": "53154", "phone": "414-485-2260", "services": "General Rentals", "address": "950 WEST RAWSON AVENUE"},

    # Omaha, NE (2)
    {"branch_number": "9448", "branch_name": "9448 - Omaha, NE", "city": "Omaha", "state": "NE", "zip": "68106", "phone": "402-971-2204", "services": "General Rentals", "address": "5604 Center Street"},
    {"branch_number": "4192", "branch_name": "4192 - Council Bluffs, IA", "city": "Council Bluffs", "state": "IA", "zip": "51503", "phone": "712-471-8268", "services": "General Rentals", "address": "19315 Portland Street"},

    # Tucson, AZ (2)
    {"branch_number": "4041", "branch_name": "4041 - Tucson, AZ", "city": "Tucson", "state": "AZ", "zip": "85706", "phone": "520-844-3617", "services": "General Rentals", "address": "6155 S Campbell Avenue"},
    {"branch_number": "9632", "branch_name": "9632 - Tuscson, AZ", "city": "Tucson", "state": "AZ", "zip": "85706", "phone": "520-593-7546", "services": "General Rentals", "address": "6902 S. Nogales Highway"},

    # Sacramento, CA (12)
    {"branch_number": "9730", "branch_name": "9730 - Sacramento, CA", "city": "W. Sacramento", "state": "CA", "zip": "95605", "phone": "916-633-5045", "services": "General Rentals", "address": "901 Stillwater"},
    {"branch_number": "4051", "branch_name": "4051 - Sacramento, CA", "city": "Sacramento", "state": "CA", "zip": "95838", "phone": "279-790-2535", "services": "General Rentals", "address": "4800 Straus Drive"},
    {"branch_number": "9757", "branch_name": "9757 - Sacramento, CA - Trench Solutions", "city": "Rancho Cordova", "state": "CA", "zip": "95670", "phone": "916-999-4614", "services": "Trench Solutions", "address": "2751 Kilgore Road"},
    {"branch_number": "9737", "branch_name": "9737 - Rancho Cordova, CA", "city": "Gold River", "state": "CA", "zip": "95670", "phone": "530-761-9445", "services": "General Rentals", "address": "2751 Kilgore Road"},
    {"branch_number": "9755", "branch_name": "9755 - Sacramento, CA - ProTruck", "city": "West Sacramento", "state": "CA", "zip": "95691", "phone": "916-503-7820", "services": "ProTruck", "address": "1701 Enterprise Blvd"},
    {"branch_number": "9720", "branch_name": "9720 - Sacramento, CA - ProSolutions", "city": "West Sacramento", "state": "CA", "zip": "95691", "phone": "916-633-5045", "services": "ProSolutions", "address": "901 Stillwater"},
    {"branch_number": "9760", "branch_name": "9760 - Sacramento, CA - ProSolutions CRC", "city": "Rancho Cordova", "state": "CA", "zip": "95670", "phone": "916-999-4614", "services": "ProSolutions CRC", "address": "2751 Kilgore Road"},
    {"branch_number": "4124", "branch_name": "4124 - Vacaville, CA", "city": "Vacaville", "state": "CA", "zip": "95688", "phone": "707-447-1600", "services": "General Rentals", "address": "500 Cernon Street"},
    {"branch_number": "9733", "branch_name": "9733 - Stockton, CA", "city": "Stockton", "state": "CA", "zip": "95206", "phone": "209-323-1199", "services": "General Rentals", "address": "1235 South Wilson Way"},
    {"branch_number": "9731", "branch_name": "9731 - Modesto, CA", "city": "Modesto", "state": "CA", "zip": "95354", "phone": "209-484-1078", "services": "General Rentals", "address": "2217 Yosemite Blvd."},
    {"branch_number": "9740", "branch_name": "9740 - Modesto, CA - Trench Solutions", "city": "Modesto", "state": "CA", "zip": "95354", "phone": "209-484-1078", "services": "Trench Solutions", "address": "2217 Yosemite Blvd."},
    {"branch_number": "9732", "branch_name": "9732 - Lodi, CA", "city": "Lodi", "state": "CA", "zip": "95240", "phone": "209-400-2009", "services": "General Rentals", "address": "1333 Industrial Way"},

    # Virginia Beach, VA (5)
    {"branch_number": "9120", "branch_name": "9120 - Virginia Beach, VA", "city": "Virginia Beach", "state": "VA", "zip": "23464", "phone": "757-828-0134", "services": "General Rentals", "address": "716 South Military Highway"},
    {"branch_number": "9259", "branch_name": "9259 - Virginia Beach, VA - ProSolutions CRC", "city": "Hampton", "state": "VA", "zip": "23669", "phone": "948-209-5734", "services": "ProSolutions CRC", "address": "402 Rip Rap Road"},
    {"branch_number": "9121", "branch_name": "9121 - Williamsburg, VA", "city": "Williamsburg", "state": "VA", "zip": "23185", "phone": "948-209-7612", "services": "General Rentals", "address": "1700 Endeavor Drive"},
    {"branch_number": "9122", "branch_name": "9122 - Williamsburg, VA - ProSolutions", "city": "Williamsburg", "state": "VA", "zip": "23185", "phone": "948-209-7612", "services": "ProSolutions", "address": "1700 Endeavor Drive"},
    {"branch_number": "9123", "branch_name": "9123 - Hampton, VA", "city": "Hampton", "state": "VA", "zip": "23669", "phone": "948-209-5734", "services": "General Rentals", "address": "402 Rip Rap Road"},

    # San Jose, CA (7)
    {"branch_number": "9738", "branch_name": "9738 - San Jose, CA", "city": "San Jose", "state": "CA", "zip": "95112", "phone": "669-900-9636", "services": "General Rentals", "address": "1695 North 4th St."},
    {"branch_number": "9729", "branch_name": "9729 - Union City, CA", "city": "Union City", "state": "CA", "zip": "94587", "phone": "510-892-5603", "services": "General Rentals", "address": "1333 Atlantic St."},
    {"branch_number": "9761", "branch_name": "9761 - Bay Area, CA - ProTruck", "city": "Fremont", "state": "CA", "zip": "94538", "phone": "510-824-8872", "services": "ProTruck", "address": "5120 Brandin Court"},
    {"branch_number": "9745", "branch_name": "9745 - Union City, CA - Trench Solutions", "city": "Union City", "state": "CA", "zip": "94587", "phone": "669-746-2865", "services": "Trench Solutions", "address": "1333 Atlantic St."},
    {"branch_number": "9739", "branch_name": "9739 - San Jose, CA - ProSolutions", "city": "San Jose", "state": "CA", "zip": "95112", "phone": "669-900-9636", "services": "ProSolutions", "address": "1695 North 4th St."},
    {"branch_number": "9756", "branch_name": "9756 - Bay Area, CA - ProSolutions CRC", "city": "Union City", "state": "CA", "zip": "94587", "phone": "510-892-5603", "services": "ProSolutions CRC", "address": "1333 Atlantic St."},
    {"branch_number": "4088", "branch_name": "4088 - Oakland, CA", "city": "Oakland", "state": "CA", "zip": "94621", "phone": "510-261-2700", "services": "General Rentals", "address": "7227 Edgewater Drive"},

    # St. Petersburg/Tampa, FL (11)
    {"branch_number": "9368", "branch_name": "9368 - Tampa, FL", "city": "Tampa", "state": "FL", "zip": "33619", "phone": "813-820-0611", "services": "General Rentals", "address": "5725 Adamo Drive"},
    {"branch_number": "9287", "branch_name": "9287 - Tampa, FL - Trench Solutions", "city": "Tampa", "state": "FL", "zip": "33619", "phone": "888-358-0431", "services": "Trench Solutions", "address": "5907 Adamo Drive"},
    {"branch_number": "4020", "branch_name": "4020 - Tampa, FL", "city": "Tampa", "state": "FL", "zip": "33619", "phone": "813-856-1698", "services": "General Rentals", "address": "6227 E Adamo Drive"},
    {"branch_number": "9349", "branch_name": "9349 - Tampa, FL - ProTruck", "city": "Tampa", "state": "FL", "zip": "33610", "phone": "813-551-0933", "services": "ProTruck", "address": "4420 N 40th Street"},
    {"branch_number": "9389", "branch_name": "9389 - Tampa, FL - ProSolutions", "city": "Tampa", "state": "FL", "zip": "33619", "phone": "813-820-0611", "services": "ProSolutions", "address": "5725 Adamo Drive"},
    {"branch_number": "9391", "branch_name": "9391 - Tampa, FL - ProSolutions CRC", "city": "Tampa", "state": "FL", "zip": "33619", "phone": "813-820-0611", "services": "ProSolutions CRC", "address": "5725 Adamo Drive"},
    {"branch_number": "9369", "branch_name": "9369 - St. Petersburg, FL", "city": "St. Petersburg", "state": "FL", "zip": "33714", "phone": "727-800-6303", "services": "General Rentals", "address": "4200 34th Street North"},
    {"branch_number": "9374", "branch_name": "9374 - Clearwater, FL", "city": "Clearwater", "state": "FL", "zip": "33760", "phone": "727-800-6305", "services": "General Rentals", "address": "13500 49th Street N"},
    {"branch_number": "9375", "branch_name": "9375 - Lakeland, FL", "city": "Lakeland", "state": "FL", "zip": "33805", "phone": "863-291-4540", "services": "General Rentals", "address": "2835 Frontage Road N"},
    {"branch_number": "9376", "branch_name": "9376 - Sarasota, FL", "city": "Sarasota", "state": "FL", "zip": "34234", "phone": "941-365-1100", "services": "General Rentals", "address": "6370 Parkland Drive"},
    {"branch_number": "9383", "branch_name": "9383 - Brandon, FL", "city": "Brandon", "state": "FL", "zip": "33510", "phone": "813-413-0844", "services": "General Rentals", "address": "610 W Lumsden Rd"},

    # West Palm Beach, FL (1)
    {"branch_number": "9351", "branch_name": "9351 - West Palm Beach, FL", "city": "Riviera Beach", "state": "FL", "zip": "33404", "phone": "561-928-2668", "services": "General Rentals", "address": "3849 West Blue Heron Blvd"},

    # Fort Lauderdale, FL (11)
    {"branch_number": "9588", "branch_name": "9588 - Fort Lauderdale, FL", "city": "Dania Beach", "state": "FL", "zip": "33312", "phone": "954-836-0399", "services": "General Rentals", "address": "3251 SW 26th Terrace"},
    {"branch_number": "9378", "branch_name": "9378 - Fort Lauderdale, FL - ProSolutions CRC", "city": "Dania Beach", "state": "FL", "zip": "33312", "phone": "954-836-0399", "services": "ProSolutions CRC", "address": "3251 SW 26th Terrace"},
    {"branch_number": "9341", "branch_name": "9341 - Fort Lauderdale, FL - Aerial", "city": "Dania Beach", "state": "FL", "zip": "33312", "phone": "954-836-0399", "services": "Aerial", "address": "3251 SW 26th Terrace"},
    {"branch_number": "9358", "branch_name": "9358 - Miami, FL - ProSolutions", "city": "Dania Beach", "state": "FL", "zip": "33312", "phone": "954-836-0399", "services": "ProSolutions", "address": "3251 SW 26th Terrace"},
    {"branch_number": "9342", "branch_name": "9342 - Pompano Beach, FL", "city": "Pompano Beach", "state": "FL", "zip": "33069", "phone": "954-933-2530", "services": "General Rentals", "address": "2041 NW 15th Street"},
    {"branch_number": "9343", "branch_name": "9343 - Boynton Beach, FL", "city": "Boynton Beach", "state": "FL", "zip": "33426", "phone": "561-600-4242", "services": "General Rentals", "address": "3560 High Ridge Rd"},
    {"branch_number": "9344", "branch_name": "9344 - Boca Raton, FL", "city": "Boca Raton", "state": "FL", "zip": "33431", "phone": "561-600-4545", "services": "General Rentals", "address": "1899 NW 1st Ave"},
    {"branch_number": "9345", "branch_name": "9345 - Delray Beach, FL", "city": "Delray Beach", "state": "FL", "zip": "33444", "phone": "561-376-2700", "services": "General Rentals", "address": "3955 NW 9th Ave"},
    {"branch_number": "9346", "branch_name": "9346 - Fort Pierce, FL", "city": "Fort Pierce", "state": "FL", "zip": "34946", "phone": "772-828-5599", "services": "General Rentals", "address": "5000 Okeechobee Rd"},
    {"branch_number": "9347", "branch_name": "9347 - Stuart, FL", "city": "Stuart", "state": "FL", "zip": "34994", "phone": "772-577-7100", "services": "General Rentals", "address": "3320 SE Dixie Highway"},
    {"branch_number": "9348", "branch_name": "9348 - Jupiter, FL", "city": "Jupiter", "state": "FL", "zip": "33458", "phone": "561-746-3255", "services": "General Rentals", "address": "1500 W Indiantown Rd"},

    # Fresno, CA (2)
    {"branch_number": "9644", "branch_name": "9644 - Fresno, CA", "city": "Fresno", "state": "CA", "zip": "93725", "phone": "559-497-1960", "services": "General Rentals", "address": "3057 S. Golden State Frontage"},
    {"branch_number": "4109", "branch_name": "4109 - Fresno", "city": "Fresno", "state": "CA", "zip": "93725", "phone": "559-570-6700", "services": "General Rentals", "address": "4199 E Jefferson Avenue"},
]

def main():
    json_file = os.path.join(BASE_DIR, "herc_web_branches.json")

    # Load existing data
    with open(json_file, 'r') as f:
        data = json.load(f)

    existing_branches = data.get('branches', [])
    existing_numbers = {b.get('branch_number') for b in existing_branches}

    print(f"Existing branches: {len(existing_branches)}")
    print(f"New branches to add: {len(NEW_BRANCHES)}")

    # Add new branches (deduplicate)
    added = 0
    for branch in NEW_BRANCHES:
        if branch['branch_number'] not in existing_numbers:
            existing_branches.append(branch)
            existing_numbers.add(branch['branch_number'])
            added += 1

    # Update data
    data['branches'] = existing_branches
    data['total_branches'] = len(existing_branches)
    data['extraction_date'] = "2026-02-19"
    data['status'] = "IN_PROGRESS"

    # Save
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Added {added} new branches (after deduplication)")
    print(f"Total branches now: {len(existing_branches)}")

if __name__ == "__main__":
    main()
