import re
from collections import defaultdict

# Parse the addresses
addresses_raw = """3900 South Lima Street Denver Colorado 80239
306 North Farish Street Jackson Mississippi 39202-3226 United States
7120 Brittmoore Road Houston Texas 77041
16 Trinity Point Drive Washington Pennsylvania 15301
769 Ctc Boulevard Louisville Colorado 80027 United States
7220 South Union Park Center Midvale Utah 84047 United States
80 8th Avenue New York New York 10011-
9292 Florida 228 Macclenny Florida 32063-4738 United States
820 South Rampart Boulevard Las Vegas Nevada 89145-4825 United States
8641 West 95th Street, Hickory Hills, Illinois 60457
750 Spice Islands Drive Sparks, Nevada, 89431-7101
18206 West Tina Lane Surprise Arizona 85387-1513 United States
17150 Smoke Tree Street Hesperia California 92345
1650 East Freeway Service Road Baytown Texas 77521
370 South Main Street Yuma Arizona 85364 United States
7595 Markham Road Unit #5 Markham Ontario L3S 0B6 Canada
128 Crews Drive Columbia South Carolina 29210-7202 United States
9292 Florida 228 Macclenny Florida 32063-4738 United States
4000 Northeast Loop 820 Haltom City Texas 76117
302 South Howard Avenue Tampa Florida 33606-1729 United States
1057 Fisherman Drive North Crystal Beach Texas 77650 United States
100 Gwynns Chapel Road Pelham North Carolina 27311 United States
201 Clay Road Suite 100 Sunnyvale Texas 75182
7601 Riviera Boulevard Miramar Florida 33023-6574 United States
1314 South Grand Avenue Waukesha Wisconsin 53186-6623 United States
500 Hamilton Avenue Brooklyn NY 11232
595 Route 131 Notre-Dame-des-Prairies Quebec J6E 0M1 Canada
2401 East University Boulevard Brownsville Texas 78521 United States
7840 Northwest 57th Street Doral Florida 33166 United States
500 West Butler Lane Ashland Oregon 97520
9641 Brookdale Drive Charlotte North Carolina 28215
1440 Springview Road Santa Ysabel California 92070-9700 United States
2014 Northwest Miami Court Miami Florida 33127-4920 United States
8641 West 95th Street, Hickory Hills, Illinois 60457
1488 Bells Ferry Road Marietta Georgia 30066
1024 Northeast 4th Street Hubbard Texas 76648 United States
1421 Orion Road Crawford Texas 76638 United States
8401 Range Road fort Dix New Jersey 08640 United States
4610 South 44th Place Phoenix Arizona 85040 United States
636 N Lake Grove Rd Lake Placid Florida 33852 United States
201 Logistics Drive Kyle Texas 78640 United States
39437 Bradbury Lane Prairieville Louisiana 70769-4973 United States
3795 56 Avenue East Nisku Alberta T9E 0V4 Canada
83 Heathcote Avenue Toronto Ontario M2L 1Z3
1512 Military Road Benton Arkansas 72015 United States
3791 Victoria Park Avenue Unit 12 Toronto Ontario M1W 3K6 Canada
330 Fowling Street Playa del rey California 90293-7730 United States
4042 Bennett Road Toledo Ohio 43612-1981 United States
320 West King Street East Berlin Pennsylvania 17316
14 Garner Road East Hamilton Ontario L9G 3L1 Canada
1555 West Maple Avenue Denver Colorado 80223-1737 United States
5199 Bright Road Hernando Mississippi 38632 United States
621 Uptown Boulevard Cedar Hill Texas 75104-3508 United States
1026 West Elizabeth Avenue Linden New Jersey 07036
1324 Camino De Cruz Blanca, Santa Fe, New Mexico 87505
11601 Shady Oaks Lane Beaumont Texas 77705
120 Disco Road Toronto Ontario M9W 1M4
4255 East Constance Way Phoenix Arizona 85042
800 Linger Lane Austin Texas 78721
7425 East Gainey Ranch Road Scottsdale Arizona 85258
3536 West Kingsley Road Garland Texas 75041 United States
255 Intermarket Road Cambridge Ontario N3H 4R6 Canada
10-37 49th Avenue Queens New York 11101
1264 Lancaster Drive Southeast Salem Oregon 97317 United States
286 Toronto Street South Uxbridge Ontario L9P 0C6 Canada
10-37 49th Avenue Queens New York 11101
1812 West Rio Salado Parkway Mesa Arizona 85201-7662 United States
1823 Fourth Street Berkeley California 94710-1910 United States
70 Oakbrook Center Oak Brook Illinois 60523 United States
13300 Howard Boulevard Kathleen Florida 33849
21 Babcock Hill Road Windham Connecticut 06266
3511 North Geraldine Avenue Oklahoma City Oklahoma 73112-2807 United States
5060 North 19th Avenue Phoenix Arizona 85015
7201 Aaron Aronov Drive Fairfield Alabama 35064 United States
903 North 2nd Street Phoenix Arizona 85004-1906 United States
365 U.S. 206 Bridgewater New Jersey 08807
125 Newark Street Newark New Jersey 07103
505 New Jersey 33 Millstone Township New Jersey 08535-
1090 Main Street Roseville California 95678-2067 United States
5100 Kings Plaza Brooklyn New York 11234 United States
28849 Chagrin Boulevard Woodmere Ohio 44122-4603 United States
2862 South Signal Butte Road Mesa Arizona 85212-2443 United States
4701 Commerce Road Richmond Virginia 23234 United States
6164 15th Street East Bradenton Florida 34203 United States
334 Glenn Road West Palm Beach Florida 33405 United States
101 Simona Drive Bolton Ontario L7E 4E8
1500 Market Place Drive Great Falls Montana 59404
2725 Radio Way Missoula Montana 59808
4909 Highway 6 Missouri City Texas 77459-4197 United States
614 Spring Cypress Road Spring Texas 77373 United States
203 Wapello Street Altadena California 91001-4442 United States
251 Vintage Way Novato California 94945-5004 United States
695 Rock Cliff Court Stone Mountain Georgia 30087 United States
133 East Krauss Street St. Louis Missouri 63111-2925 United States
10035 South Memorial Drive Tulsa Oklahoma 74133-6451 United States
28th Street gate 330 11th St, Gulfport, MS, 39501 Gulfport Mississippi 39501 United States
1150 Sherbrook Avenue Suite B 101 Indian Land South Carolina 29707
626 Buttonwood Drive Longboat Key Florida 34228
36349 South Grays Airport Road Fruitland Park Florida 34731 United States
1760 62nd Avenue South St. Petersburg Florida 33712-
2860 Farm to Market Road 880 Putnam Texas 76469
3760 Northeast 199th ter Aventura Florida 33180-3409 United States
421 Lafayette Street New York New York 10003 United States
6 Linden Avenue East Jersey City New Jersey 07305 United States
4996 Yonge Street Toronto Ontario M2N 7J8
16 Thacker Loop Oxford Mississippi 38655-8541 United States
16276 Slover Avenue Fontana California 92337
2310 East Gladwick Street Rancho Dominguez California 90220
40 Larkfield Dr, North York, ON
5358 Old Winter Garden Road Orlando Florida 32811-1521 United States
188 Macedonia Road White Georgia 30184
70 University Avenue Toronto Ontario M5J 2M4 Canada
1153 West 37th Drive Los Angeles California 90007
2721 White Horse Road Greenville South Carolina 29611-6132 United States
3501 Lancaster Hutchins Road Hutchins Texas 75141
4041 Bahia Vista Street Sarasota Florida 34232 United States
3127 Cabaniss Parkway Corpus Christi Texas 78415-5907 United States
20831 Bower Road Dade City Florida 33523 United States
1 Titus Place Walton New York 13856
3528 Pasadena dr San Mateo, CA 94403
3546 Philadelphus Road Pembroke North Carolina 28372-7384 United States
3141 Parrott Avenue Northwest Atlanta Georgia 30318
886 Clearbrook Road Abbotsford British Columbia V2T 5X3 Canada
22435 Glenn Drive Sterling Virginia 20164 United States
571 Long Prairie Road suite 200 Flower Mound Texas 75022 United States
1300 Desert Willow Road Northwest Los Lunas New Mexico 87031 United States
29 Charleswood Drive Toronto Ontario M3H 1X3 Canada
1280 East 92nd Street Brooklyn New York 11236
345 Wilson Avenue Toronto Ontario M3H 5W1
1030 Airport Drive Presque Isle Maine 04769-2048 United States
19 Deer Run Trail Sherman Connecticut 06784-2032 United States
22921 Ridge Route Drive Lake Forest California 92630 United States
500 West Lake Kennedy Drive Cape Coral Florida 33991-2061 United States
3410 Andrews Drive Pleasanton California 94588 United States
E 91st St New York New York 10128 United States
2330 East 3300 South Salt Lake City Utah 84109-2766 United States
5 Federation Way Irvine California 92603-0100 United States
3301 Preston Road Plano Texas 75093-7405 United States
156 Williamsburg Street Northeast Aiken South Carolina 29801-4543 United States
6010 Valley Lane Towson Maryland 21286
1245 Dupont Street Toronto Ontario M6H 0E5
100 Armory Road New Boston Texas 75570
1805 Record Crossing Road Dallas Texas 75235
10301 201 Street Langley Township British Columbia V1M 3G8
42 Pinewood Pl Mims Florida United States
10612 15th Avenue Southwest Seattle Washington 98146-2139 United States
2900 Nieman Avenue Baltimore Maryland 21230-2718 United States
4420 Holland Avenue Dallas Texas 75219-5746 United States
250 North El Cielo Road Palm Springs California 92262 United States
182 Foust Lane Rocky Top Tennessee 37769-5816 United States
23182 Alcalde Drive Laguna Hills California 92653
201 Logistics Drive Kyle Texas 78640 United States
2301 shelly circle Costa Mesa California United States
2280 Chancery Lane West Oakville Ontario L6J 6A3 Canada
7225 Power Road Queen Creek Arizona 85142 United States
1172 North Main Street Franklin Indiana 46131-1251 United States
14000 Northwest 37th Avenue Opa-locka Florida 33054-6324 United States
6426 Crystal Run San Antonio Texas 78238 United States
500 South Florence Street Wichita Kansas 67209-2501 United States"""

# State name to abbreviation mapping
state_abbrev = {
    'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR', 'california': 'CA',
    'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE', 'florida': 'FL', 'georgia': 'GA',
    'hawaii': 'HI', 'idaho': 'ID', 'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA',
    'kansas': 'KS', 'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME', 'maryland': 'MD',
    'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN', 'mississippi': 'MS', 'missouri': 'MO',
    'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV', 'new hampshire': 'NH', 'new jersey': 'NJ',
    'new mexico': 'NM', 'new york': 'NY', 'north carolina': 'NC', 'north dakota': 'ND', 'ohio': 'OH',
    'oklahoma': 'OK', 'oregon': 'OR', 'pennsylvania': 'PA', 'rhode island': 'RI', 'south carolina': 'SC',
    'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT', 'vermont': 'VT',
    'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV', 'wisconsin': 'WI', 'wyoming': 'WY',
    'ontario': 'ON', 'quebec': 'QC', 'british columbia': 'BC', 'alberta': 'AB'
}

# Parse addresses
locations = []
for line in addresses_raw.strip().split('\n'):
    line = line.strip()
    if not line:
        continue
    
    # Try to extract city and state
    # Common patterns: "City State ZIP" or "City, State, ZIP"
    line_clean = line.replace(',', ' ').replace('United States', '').replace('Canada', '').strip()
    
    # Find state
    found_state = None
    found_city = None
    
    for state_name, abbrev in state_abbrev.items():
        if state_name in line_clean.lower():
            found_state = abbrev
            # Extract city (word(s) before state name)
            idx = line_clean.lower().find(state_name)
            before_state = line_clean[:idx].strip()
            # City is usually the last 1-3 words before state
            words = before_state.split()
            if len(words) >= 1:
                # Try to find city name (skip numbers/zips)
                city_words = []
                for w in reversed(words):
                    if not w.replace('-', '').isdigit() and len(w) > 1:
                        city_words.insert(0, w)
                        if len(city_words) >= 3:
                            break
                if city_words:
                    found_city = ' '.join(city_words)
            break
    
    # Also check for state abbreviations
    if not found_state:
        for abbrev in ['TX', 'CA', 'FL', 'NY', 'AZ', 'CO', 'ON', 'BC', 'AB', 'QC']:
            if f' {abbrev} ' in line_clean or line_clean.endswith(f' {abbrev}'):
                found_state = abbrev
                break
    
    if found_city and found_state:
        locations.append({'city': found_city.title(), 'state': found_state, 'raw': line[:60]})

# Aggregate by city/state
location_counts = defaultdict(int)
state_counts = defaultdict(int)

for loc in locations:
    key = f"{loc['city']}, {loc['state']}"
    location_counts[key] += 1
    state_counts[loc['state']] += 1

print("="*80)
print(f"PARSED {len(locations)} ADDRESSES")
print("="*80)

print(f"\nUnique locations: {len(location_counts)}")
print(f"Unique states: {len(state_counts)}")

print("\n" + "="*60)
print("BY STATE (Order Count)")
print("="*60)
for state, count in sorted(state_counts.items(), key=lambda x: -x[1]):
    print(f"  {state}: {count}")

print("\n" + "="*60)
print("BY CITY (Multiple Orders)")
print("="*60)
for loc, count in sorted(location_counts.items(), key=lambda x: -x[1]):
    if count > 1:
        print(f"  {loc}: {count}")

# Save for cross-reference with ads
import json
with open('/Users/vinuraabeysundara/dozr_address_locations.json', 'w') as f:
    json.dump({
        'locations': list(location_counts.keys()),
        'location_counts': dict(location_counts),
        'state_counts': dict(state_counts)
    }, f, indent=2)

print(f"\n[Saved {len(location_counts)} unique locations]")
