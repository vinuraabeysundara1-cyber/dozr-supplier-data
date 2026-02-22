#!/usr/bin/env python3
"""
Update Herc Rentals branches JSON with newly extracted data
"""

import json
import os
from datetime import datetime

BASE_DIR = "/Users/vinuraabeysundara/Desktop/ICG/DOZR/SupplierBranches"

# New branches extracted from browser session
NEW_BRANCHES = [
    # Chicago (7)
    {"branch_number": "9113", "branch_name": "9113 - Downtown Chicago, IL", "address": "4039 South Peoria St", "city": "Chicago", "state": "IL", "zip": "60609", "phone": "773-669-3942", "services": "General Rentals"},
    {"branch_number": "9116", "branch_name": "9116 - Chicago, IL - ProTruck", "address": "2090 Mannheim Road", "city": "Melrose Park", "state": "IL", "zip": "60160", "phone": "708-538-3980", "services": "ProTruck"},
    {"branch_number": "9124", "branch_name": "9124 - Chicago, IL - ProSolutions", "address": "4301 South Packers Avenue", "city": "Chicago", "state": "IL", "zip": "60609", "phone": "331-200-1240", "services": "ProSolutions"},
    {"branch_number": "9135", "branch_name": "9135 - Chicago, IL - Floor Care Solutions", "address": "4039 South Peoria Street", "city": "Chicago", "state": "IL", "zip": "60609", "phone": "773-669-3942", "services": "Floorcare"},
    {"branch_number": "9227", "branch_name": "9227 - Bensenville, IL", "address": "4430 West Armitage Ave", "city": "Melrose Park", "state": "IL", "zip": "60160", "phone": "630-576-0069", "services": "Aerial"},
    {"branch_number": "9263", "branch_name": "9263 - Streamwood, IL", "address": "1339 Yorkshire Drive", "city": "Streamwood", "state": "IL", "zip": "60107", "phone": "331-308-1576", "services": "General Rentals"},
    {"branch_number": "9137", "branch_name": "9137 - Naperville, IL", "address": "31W350 Diehl Road", "city": "Naperville", "state": "IL", "zip": "60563", "phone": "312-680-0860", "services": "Crawler Crane, Earthmoving, General Rentals"},

    # Dallas (14)
    {"branch_number": "4060", "branch_name": "4060 - Mesquite, TX", "address": "3550 US Highway 80 E", "city": "Mesquite", "state": "TX", "zip": "75149", "phone": "972-284-4200", "services": "General Rentals"},
    {"branch_number": "9488", "branch_name": "9488 - Dallas, TX - ProTruck", "address": "3606 E Jefferson Street", "city": "Grand Prairie", "state": "TX", "zip": "75051", "phone": "469-674-7300", "services": "ProTruck"},
    {"branch_number": "9582", "branch_name": "9582 - Dallas, TX - ProSolutions", "address": "3606 Jefferson St", "city": "Grand Prairie", "state": "TX", "zip": "75051", "phone": "833-967-6026", "services": "ProSolutions"},
    {"branch_number": "9481", "branch_name": "9481 - Dallas, TX", "address": "10966 Harry Hines Blvd", "city": "Dallas", "state": "TX", "zip": "75220", "phone": "214-352-4891", "services": "Earthmoving"},
    {"branch_number": "9486", "branch_name": "9486 - Dallas, TX - Floor Care Solutions", "address": "10966 Harry Hines Blvd", "city": "Dallas", "state": "TX", "zip": "75220", "phone": "214-352-4891", "services": "Floorcare"},
    {"branch_number": "9478", "branch_name": "9478 - Dallas, TX - ProSolutions", "address": "10966 Harry Hines Blvd", "city": "Dallas", "state": "TX", "zip": "75220", "phone": "214-352-4891", "services": "ProSolutions"},
    {"branch_number": "4115", "branch_name": "4115 - Fort Worth, TX", "address": "2024 W Pioneer Pkwy", "city": "Arlington", "state": "TX", "zip": "76013", "phone": "817-860-8060", "services": "General Rentals"},
    {"branch_number": "9490", "branch_name": "9490 - Fort Worth, TX - ProSolutions", "address": "2024 W Pioneer Pkwy", "city": "Arlington", "state": "TX", "zip": "76013", "phone": "817-860-8060", "services": "ProSolutions"},
    {"branch_number": "9452", "branch_name": "9452 - Carrollton, TX", "address": "2401 E Hebron Parkway", "city": "Carrollton", "state": "TX", "zip": "75010", "phone": "469-892-2700", "services": "General Rentals"},
    {"branch_number": "9460", "branch_name": "9460 - Dallas, TX", "address": "2401 E Hebron Parkway", "city": "Carrollton", "state": "TX", "zip": "75010", "phone": "469-892-2700", "services": "Aerial"},
    {"branch_number": "9453", "branch_name": "9453 - Carrollton, TX - Floor Care", "address": "2401 E Hebron Parkway", "city": "Carrollton", "state": "TX", "zip": "75010", "phone": "469-892-2700", "services": "Floorcare"},
    {"branch_number": "9427", "branch_name": "9427 - McKinney, TX", "address": "2641 N Central Expressway", "city": "McKinney", "state": "TX", "zip": "75070", "phone": "972-540-7827", "services": "General Rentals"},
    {"branch_number": "9484", "branch_name": "9484 - Frisco, TX - ProTruck", "address": "2641 N Central Expressway", "city": "McKinney", "state": "TX", "zip": "75070", "phone": "972-540-7827", "services": "ProTruck"},
    {"branch_number": "9426", "branch_name": "9426 - Rockwall, TX", "address": "2980 SH 66", "city": "Rockwall", "state": "TX", "zip": "75032", "phone": "972-722-2700", "services": "General Rentals"},

    # Phoenix (16)
    {"branch_number": "9428", "branch_name": "9428 - Glendale, AZ", "address": "12040 N 91st Ave", "city": "Peoria", "state": "AZ", "zip": "85345", "phone": "602-269-5931", "services": "General Rentals"},
    {"branch_number": "9429", "branch_name": "9429 - Glendale, AZ - ProSolutions", "address": "7637 N 67th Ave", "city": "Glendale", "state": "AZ", "zip": "85301", "phone": "623-760-0690", "services": "ProSolutions"},
    {"branch_number": "4040", "branch_name": "4040 - Phoenix, AZ", "address": "4010 S 22nd Street", "city": "Phoenix", "state": "AZ", "zip": "85040", "phone": "602-232-0600", "services": "General Rentals"},
    {"branch_number": "9630", "branch_name": "9630 - Phoenix, AZ", "address": "2010 N. Black Canyon Road", "city": "Phoenix", "state": "AZ", "zip": "85009", "phone": "602-269-5931", "services": "General Rentals"},
    {"branch_number": "9622", "branch_name": "9622 - Phoenix, AZ - HES", "address": "3640 West Whitton Ave", "city": "Phoenix", "state": "AZ", "zip": "85019", "phone": "602-233-3685", "services": "Entertainment"},
    {"branch_number": "9620", "branch_name": "9620 - Phoenix, AZ - Crane", "address": "4010 S 22nd Street", "city": "Phoenix", "state": "AZ", "zip": "85040", "phone": "602-269-5931", "services": "Crane"},
    {"branch_number": "9621", "branch_name": "9621 - Phoenix, AZ - ProSolutions", "address": "4010 S 22nd Street", "city": "Phoenix", "state": "AZ", "zip": "85040", "phone": "602-232-0600", "services": "ProSolutions"},
    {"branch_number": "9623", "branch_name": "9623 - Phoenix, AZ - Floor Care", "address": "4010 S 22nd Street", "city": "Phoenix", "state": "AZ", "zip": "85040", "phone": "602-232-0600", "services": "Floorcare"},
    {"branch_number": "9624", "branch_name": "9624 - Phoenix, AZ - ProTruck", "address": "4010 S 22nd Street", "city": "Phoenix", "state": "AZ", "zip": "85040", "phone": "602-232-0600", "services": "ProTruck"},
    {"branch_number": "9640", "branch_name": "9640 - Mesa, AZ", "address": "1960 S Country Club Drive", "city": "Mesa", "state": "AZ", "zip": "85210", "phone": "480-833-1900", "services": "General Rentals"},
    {"branch_number": "9641", "branch_name": "9641 - Mesa, AZ - ProSolutions", "address": "1960 S Country Club Drive", "city": "Mesa", "state": "AZ", "zip": "85210", "phone": "480-833-1900", "services": "ProSolutions"},
    {"branch_number": "9625", "branch_name": "9625 - Tempe, AZ", "address": "2020 E. University Drive", "city": "Tempe", "state": "AZ", "zip": "85281", "phone": "480-966-1550", "services": "General Rentals"},
    {"branch_number": "9627", "branch_name": "9627 - Scottsdale, AZ", "address": "8633 E Raintree Drive", "city": "Scottsdale", "state": "AZ", "zip": "85260", "phone": "480-860-0790", "services": "General Rentals"},
    {"branch_number": "9631", "branch_name": "9631 - Chandler, AZ", "address": "7265 W Detroit St", "city": "Chandler", "state": "AZ", "zip": "85226", "phone": "480-961-2010", "services": "General Rentals"},
    {"branch_number": "9635", "branch_name": "9635 - Tucson, AZ", "address": "3600 N Oracle Road", "city": "Tucson", "state": "AZ", "zip": "85705", "phone": "520-622-8650", "services": "General Rentals"},
    {"branch_number": "9636", "branch_name": "9636 - Tucson, AZ - ProSolutions", "address": "3600 N Oracle Road", "city": "Tucson", "state": "AZ", "zip": "85705", "phone": "520-622-8650", "services": "ProSolutions"},

    # Miami (6)
    {"branch_number": "9910", "branch_name": "9910 - West Miami, FL", "address": "7044 SW 8th Street", "city": "Miami", "state": "FL", "zip": "33144", "phone": "305-269-7799", "services": "General Rentals"},
    {"branch_number": "9365", "branch_name": "9365 - Miami, FL - Floor Care Solutions", "address": "7044 SW 8TH ST", "city": "Miami", "state": "FL", "zip": "33144", "phone": "954-970-6880", "services": "Floorcare"},
    {"branch_number": "9350", "branch_name": "9350 - Miami, FL", "address": "5850 Northwest 77th Court", "city": "Miami", "state": "FL", "zip": "33166", "phone": "305-592-5770", "services": "General Rentals"},
    {"branch_number": "9913", "branch_name": "9913 - Doral, FL", "address": "8490 NW 58th Street", "city": "Doral", "state": "FL", "zip": "33166", "phone": "305-639-6000", "services": "General Rentals"},
    {"branch_number": "9215", "branch_name": "9215 - South Miami - FL - ProSolutions", "address": "19380 SW 106th Ave", "city": "Cutler Bay", "state": "FL", "zip": "33157", "phone": "305-238-4600", "services": "ProSolutions"},
    {"branch_number": "9352", "branch_name": "9352 - South Miami, FL", "address": "19380 SW 106th Ave", "city": "Cutler Bay", "state": "FL", "zip": "33157", "phone": "305-238-4600", "services": "General Rentals"},

    # Denver (9)
    {"branch_number": "9921", "branch_name": "9921 - Denver, CO", "address": "220 East 56th Avenue", "city": "Denver", "state": "CO", "zip": "80216", "phone": "303-288-2271", "services": "General Rentals"},
    {"branch_number": "9673", "branch_name": "9673 - Denver, CO - ProSolutions", "address": "7750 E 96th Ave", "city": "Henderson", "state": "CO", "zip": "80640", "phone": "303-927-5303", "services": "ProSolutions"},
    {"branch_number": "9656", "branch_name": "9656 - Denver, CO - Earthmoving", "address": "7750 East 96th Ave", "city": "Henderson", "state": "CO", "zip": "80640", "phone": "303-650-9000", "services": "Heavy Earth"},
    {"branch_number": "9669", "branch_name": "9669 - Littleton, CO", "address": "13202 E. Adam Aircraft Circle", "city": "Englewood", "state": "CO", "zip": "80112", "phone": "888-238-3808", "services": "General Rentals"},
    {"branch_number": "9672", "branch_name": "9672 - Englewood, CO - Floor Care Solutions", "address": "13202 E Adam Aircraft Circle", "city": "Englewood", "state": "CO", "zip": "80112", "phone": "303-297-5300", "services": "Floorcare"},
    {"branch_number": "9657", "branch_name": "9657 - Denver, CO", "address": "7750 E 96th Ave", "city": "Henderson", "state": "CO", "zip": "80640", "phone": "303-650-9000", "services": "General Rentals"},
    {"branch_number": "9658", "branch_name": "9658 - Denver, CO - ProTruck", "address": "7750 E 96th Ave", "city": "Henderson", "state": "CO", "zip": "80640", "phone": "303-650-9000", "services": "ProTruck"},
    {"branch_number": "9670", "branch_name": "9670 - Colorado Springs, CO", "address": "2920 N Hancock Ave", "city": "Colorado Springs", "state": "CO", "zip": "80907", "phone": "719-633-2202", "services": "General Rentals"},
    {"branch_number": "9671", "branch_name": "9671 - Pueblo, CO", "address": "4411 N Elizabeth Street", "city": "Pueblo", "state": "CO", "zip": "81008", "phone": "719-544-8181", "services": "General Rentals"},

    # Seattle (6)
    {"branch_number": "9781", "branch_name": "9781 - Ballard, WA", "address": "4233 Leary Way NW", "city": "Seattle", "state": "WA", "zip": "98107", "phone": "206-782-4200", "services": "General Rentals"},
    {"branch_number": "9721", "branch_name": "9721 - Downtown Seattle, WA", "address": "5055 4th Avenue S", "city": "Seattle", "state": "WA", "zip": "98134", "phone": "206-934-5700", "services": "General Rentals"},
    {"branch_number": "9715", "branch_name": "9715 - Seattle, WA - Floor Care Solutions", "address": "5055 4th Avenue S", "city": "Seattle", "state": "WA", "zip": "98134", "phone": "206-934-5700", "services": "Floorcare"},
    {"branch_number": "9713", "branch_name": "9713 - Seattle, WA - ProTruck", "address": "9619 8th Avenue S", "city": "Seattle", "state": "WA", "zip": "98108", "phone": "206-834-3070", "services": "ProTruck"},
    {"branch_number": "9739", "branch_name": "9739 - Seattle, WA - Aerial", "address": "9619 8th Avenue S", "city": "Seattle", "state": "WA", "zip": "98108", "phone": "206-834-3070", "services": "Aerial"},
    {"branch_number": "9725", "branch_name": "9725 - Tukwila, WA", "address": "9619 8th Avenue S", "city": "Seattle", "state": "WA", "zip": "98108", "phone": "206-834-3070", "services": "General Rentals"},

    # Boston (4)
    {"branch_number": "9162", "branch_name": "9162 - Boston, MA", "address": "45 Gerard Street", "city": "Boston", "state": "MA", "zip": "02119", "phone": "617-442-4210", "services": "General Rentals"},
    {"branch_number": "9962", "branch_name": "9962 - Boston, MA - Trench Solutions", "address": "238E Cherry Street", "city": "Shrewsbury", "state": "MA", "zip": "01545", "phone": "508-842-2822", "services": "Trench Solutions"},
    {"branch_number": "9108", "branch_name": "9108 - Worcester, MA", "address": "183 Southwest Cutoff", "city": "Worcester", "state": "MA", "zip": "01604", "phone": "508-757-0620", "services": "Earthmoving"},
    {"branch_number": "9106", "branch_name": "9106 - Londonderry, NH - Floor Care Solutions", "address": "3 Symmes Drive", "city": "Londonderry", "state": "NH", "zip": "03053", "phone": "603-421-0000", "services": "Floorcare"},

    # Philadelphia (7)
    {"branch_number": "9101", "branch_name": "9101 - Philadelphia, PA - ProTruck", "address": "6951 Norwitch Drive", "city": "Philadelphia", "state": "PA", "zip": "19153", "phone": "215-749-1290", "services": "ProTruck"},
    {"branch_number": "9163", "branch_name": "9163 - Philadelphia, PA", "address": "6951 Norwitch Drive", "city": "Philadelphia", "state": "PA", "zip": "19153", "phone": "215-749-1290", "services": "General Rentals"},
    {"branch_number": "9164", "branch_name": "9164 - Philadelphia, PA - Floor Care Solutions", "address": "6951 Norwitch Drive", "city": "Philadelphia", "state": "PA", "zip": "19153", "phone": "215-749-1290", "services": "Floorcare"},
    {"branch_number": "9183", "branch_name": "9183 - Philadelphia, PA - ProSolutions", "address": "2500 Wheatsheaf Lane", "city": "Philadelphia", "state": "PA", "zip": "19137", "phone": "215-749-1290", "services": "ProSolutions"},
    {"branch_number": "4123", "branch_name": "4123 - Philadelphia, PA", "address": "2500 Wheatsheaf Lane", "city": "Philadelphia", "state": "PA", "zip": "19137", "phone": "445-222-6700", "services": "General Rentals"},
    {"branch_number": "9148", "branch_name": "9148 - King of Prussia, PA", "address": "601 South Henderson Road", "city": "King of Prussia", "state": "PA", "zip": "19406", "phone": "610-265-1320", "services": "General Rentals"},
    {"branch_number": "9180", "branch_name": "9180 - Wilmington, DE", "address": "601 N Justison St", "city": "Wilmington", "state": "DE", "zip": "19801", "phone": "302-658-1100", "services": "General Rentals"},

    # Detroit (7)
    {"branch_number": "8206", "branch_name": "8206 - Windsor, ON", "address": "5225 Cabana Road East", "city": "Windsor", "state": "ON", "zip": "N9G1A3", "phone": "519-972-8144", "services": "General Rentals"},
    {"branch_number": "9561", "branch_name": "9561 - Oak Park, MI", "address": "13133 Cloverdale Street", "city": "Oak Park", "state": "MI", "zip": "48237", "phone": "248-399-6600", "services": "Carry Deck Crane"},
    {"branch_number": "9130", "branch_name": "9130 - Detroit, MI - ProSolutions", "address": "12901 Cloverdale Street", "city": "Oak Park", "state": "MI", "zip": "48237", "phone": "248-648-6888", "services": "ProSolutions"},
    {"branch_number": "9119", "branch_name": "9119 - Detroit, MI - ProSolutions CRC", "address": "12901 Cloverdale Street", "city": "Oak Park", "state": "MI", "zip": "48237", "phone": "248-648-6890", "services": "ProSolutions"},
    {"branch_number": "9128", "branch_name": "9128 - Detroit, MI", "address": "29125 Smith Road", "city": "Romulus", "state": "MI", "zip": "48174", "phone": "734-595-7075", "services": "General Rentals"},
    {"branch_number": "9177", "branch_name": "9177 - Detroit, MI - ProTruck", "address": "29125 Smith Road", "city": "Romulus", "state": "MI", "zip": "48174", "phone": "734-595-7075", "services": "ProTruck"},
    {"branch_number": "9146", "branch_name": "9146 - Detroit, MI - Floor Care", "address": "29125 Smith Road", "city": "Romulus", "state": "MI", "zip": "48174", "phone": "734-595-7075", "services": "Floorcare"},

    # Tampa (11)
    {"branch_number": "9368", "branch_name": "9368 - Tampa, FL", "address": "5725 Adamo Drive", "city": "Tampa", "state": "FL", "zip": "33619", "phone": "813-623-6581", "services": "Earthmoving"},
    {"branch_number": "9287", "branch_name": "9287 - Tampa, FL - Trench Solutions", "address": "5907 Adamo Drive", "city": "Tampa", "state": "FL", "zip": "33619", "phone": "833-967-6026", "services": "Trench Solutions"},
    {"branch_number": "4020", "branch_name": "4020 - Tampa, FL", "address": "6227 E Adamo Drive", "city": "Tampa", "state": "FL", "zip": "33619", "phone": "813-635-9688", "services": "General Rentals"},
    {"branch_number": "9349", "branch_name": "9349 - Tampa, FL - ProTruck", "address": "6515 N 50th Street", "city": "Tampa", "state": "FL", "zip": "33610", "phone": "813-577-7850", "services": "ProTruck"},
    {"branch_number": "9359", "branch_name": "9359 - North Tampa, FL - Floor Care Solutions", "address": "6515 N 50th Street", "city": "Tampa", "state": "FL", "zip": "33610", "phone": "813-577-7850", "services": "Floorcare"},
    {"branch_number": "9361", "branch_name": "9361 - North Tampa, FL", "address": "6515 N 50th Street", "city": "Tampa", "state": "FL", "zip": "33610", "phone": "813-577-7850", "services": "General Rentals"},
    {"branch_number": "9362", "branch_name": "9362 - North Tampa, FL - ProSolutions", "address": "6515 N 50th Street", "city": "Tampa", "state": "FL", "zip": "33610", "phone": "813-577-7850", "services": "ProSolutions"},
    {"branch_number": "9374", "branch_name": "9374 - Clearwater, FL", "address": "14230 58th Street N", "city": "Clearwater", "state": "FL", "zip": "33760", "phone": "727-531-6900", "services": "General Rentals"},
    {"branch_number": "9376", "branch_name": "9376 - Lakeland, FL", "address": "1919 Reynolds Road", "city": "Lakeland", "state": "FL", "zip": "33801", "phone": "863-687-7700", "services": "General Rentals"},
    {"branch_number": "9378", "branch_name": "9378 - Sarasota, FL", "address": "7601 15th Street E", "city": "Sarasota", "state": "FL", "zip": "34243", "phone": "941-355-5800", "services": "General Rentals"},
    {"branch_number": "9379", "branch_name": "9379 - Fort Myers, FL", "address": "12830 Metro Pkwy", "city": "Fort Myers", "state": "FL", "zip": "33966", "phone": "239-561-1111", "services": "General Rentals"},

    # Orlando (8)
    {"branch_number": "9252", "branch_name": "9252 - Casselberry, FL", "address": "575 FL-436", "city": "Casselberry", "state": "FL", "zip": "32707", "phone": "407-331-1944", "services": "General Rentals"},
    {"branch_number": "9372", "branch_name": "9372 - Orlando, FL", "address": "10655 Central Port Drive", "city": "Orlando", "state": "FL", "zip": "32824", "phone": "407-240-2132", "services": "Earthmoving"},
    {"branch_number": "4021", "branch_name": "4021 - Orlando, FL", "address": "1102 Crown Park Circle", "city": "Winter Garden", "state": "FL", "zip": "34787", "phone": "407-905-5344", "services": "General Rentals"},
    {"branch_number": "9381", "branch_name": "9381 - Orlando, FL - ProTruck", "address": "950 Jetstream Drive", "city": "Orlando", "state": "FL", "zip": "32824", "phone": "407-544-6500", "services": "ProTruck"},
    {"branch_number": "4124", "branch_name": "4124 - South Orlando, FL", "address": "950 Jetstream Drive", "city": "Orlando", "state": "FL", "zip": "32824", "phone": "407-544-6500", "services": "General Rentals"},
    {"branch_number": "9383", "branch_name": "9383 - Orlando, FL - ProSolutions", "address": "950 Jetstream Drive", "city": "Orlando", "state": "FL", "zip": "32824", "phone": "407-544-6500", "services": "ProSolutions"},
    {"branch_number": "9384", "branch_name": "9384 - Orlando, FL - Floor Care", "address": "950 Jetstream Drive", "city": "Orlando", "state": "FL", "zip": "32824", "phone": "407-544-6500", "services": "Floorcare"},
    {"branch_number": "9386", "branch_name": "9386 - Daytona Beach, FL", "address": "1200 Mason Ave", "city": "Daytona Beach", "state": "FL", "zip": "32117", "phone": "386-253-0024", "services": "General Rentals"},

    # Minneapolis (4)
    {"branch_number": "9270", "branch_name": "9270 - Maple Grove, MN - ProSolutions", "address": "10939 89TH Avenue N", "city": "Maple Grove", "state": "MN", "zip": "55369", "phone": "763-347-3930", "services": "ProSolutions"},
    {"branch_number": "9271", "branch_name": "9271 - Maple Grove, MN - ProSolutions CRC", "address": "10939 89th Avenue N", "city": "Maple Grove", "state": "MN", "zip": "55369", "phone": "763-347-3930", "services": "ProSolutions"},
    {"branch_number": "9293", "branch_name": "9293 - Minneapolis, MN - ProTruck", "address": "10939 89th Avenue N", "city": "Maple Grove", "state": "MN", "zip": "55369", "phone": "763-347-3930", "services": "ProTruck"},
    {"branch_number": "9205", "branch_name": "9205 - Maple Grove, MN", "address": "10939 89th Avenue N", "city": "Maple Grove", "state": "MN", "zip": "55369", "phone": "763-347-3930", "services": "General Rentals"},

    # San Francisco (8)
    {"branch_number": "9749", "branch_name": "9749 - San Francisco, CA", "address": "435 South Van Ness Ave", "city": "San Francisco", "state": "CA", "zip": "94103", "phone": "415-865-4444", "services": "General Rentals"},
    {"branch_number": "9747", "branch_name": "9747 - Berkeley, CA", "address": "1475 Eastshore Highway", "city": "Berkeley", "state": "CA", "zip": "94710", "phone": "510-559-4444", "services": "General Rentals"},
    {"branch_number": "9740", "branch_name": "9740 - Corte Madera, CA", "address": "5750 Paradise Drive", "city": "Corte Madera", "state": "CA", "zip": "94925", "phone": "415-924-4444", "services": "General Rentals"},
    {"branch_number": "9705", "branch_name": "9705 - Oakland, CA - ProSolutions", "address": "7727 Oakport Street", "city": "Oakland", "state": "CA", "zip": "94621", "phone": "510-633-2040", "services": "ProSolutions"},
    {"branch_number": "9729", "branch_name": "9729 - Union City, CA", "address": "1333 Atlantic St.", "city": "Union City", "state": "CA", "zip": "94587", "phone": "510-324-2444", "services": "Earthmoving"},
    {"branch_number": "9730", "branch_name": "9730 - Oakland, CA", "address": "7727 Oakport Street", "city": "Oakland", "state": "CA", "zip": "94621", "phone": "510-633-2040", "services": "General Rentals"},
    {"branch_number": "9742", "branch_name": "9742 - San Jose, CA", "address": "255 Los Gatos Blvd", "city": "Los Gatos", "state": "CA", "zip": "95032", "phone": "408-377-4444", "services": "General Rentals"},
    {"branch_number": "9746", "branch_name": "9746 - Redwood City, CA", "address": "333 Industrial Road", "city": "Redwood City", "state": "CA", "zip": "94063", "phone": "650-367-4444", "services": "General Rentals"},

    # San Diego (7)
    {"branch_number": "1053", "branch_name": "1053 - San Diego", "address": "6006 Miramar Road", "city": "San Diego", "state": "CA", "zip": "92121", "phone": "619-938-1966", "services": "General Rentals"},
    {"branch_number": "9679", "branch_name": "9679 - San Diego, CA - ProSolutions", "address": "128 Mace Street", "city": "Chula Vista", "state": "CA", "zip": "91911", "phone": "858-566-5500", "services": "ProSolutions"},
    {"branch_number": "9619", "branch_name": "9619 - San Diego, CA - ProSolutions CRC", "address": "128 Mace Street", "city": "Chula Vista", "state": "CA", "zip": "91911", "phone": "858-566-5500", "services": "ProSolutions"},
    {"branch_number": "9932", "branch_name": "9932 - Chula Vista, CA", "address": "128 Mace Street", "city": "Chula Vista", "state": "CA", "zip": "91911", "phone": "619-500-9233", "services": "General Rentals"},
    {"branch_number": "9637", "branch_name": "9637 - San Diego, CA", "address": "8014 Miramar Road", "city": "San Diego", "state": "CA", "zip": "92126", "phone": "858-566-5500", "services": "General Rentals"},
    {"branch_number": "9526", "branch_name": "9526 - Escondido, CA", "address": "1951 W Valley Pkwy", "city": "Escondido", "state": "CA", "zip": "92029", "phone": "760-746-5500", "services": "General Rentals"},
    {"branch_number": "9639", "branch_name": "9639 - San Diego, CA - Floor Care", "address": "8014 Miramar Road", "city": "San Diego", "state": "CA", "zip": "92126", "phone": "858-566-5500", "services": "Floorcare"},

    # Las Vegas (5)
    {"branch_number": "4038", "branch_name": "4038 - Las Vegas, NV", "address": "4129 Losee Road", "city": "North Las Vegas", "state": "NV", "zip": "89030", "phone": "702-320-6500", "services": "General Rentals"},
    {"branch_number": "9661", "branch_name": "9661 - Las Vegas, NV", "address": "4555 Wynn Road", "city": "Las Vegas", "state": "NV", "zip": "89103", "phone": "702-791-1100", "services": "General Rentals"},
    {"branch_number": "9663", "branch_name": "9663 - Las Vegas, NV - ProSolutions", "address": "4555 Wynn Road", "city": "Las Vegas", "state": "NV", "zip": "89103", "phone": "702-791-1100", "services": "ProSolutions"},
    {"branch_number": "9617", "branch_name": "9617 - Las Vegas, NV - ProSolutions CRC", "address": "4555 Wynn Road", "city": "Las Vegas", "state": "NV", "zip": "89103", "phone": "702-791-1100", "services": "ProSolutions"},
    {"branch_number": "9664", "branch_name": "9664 - North Las Vegas, NV - ProTruck", "address": "3624 N. Goldfield Street", "city": "Las Vegas", "state": "NV", "zip": "89032", "phone": "702-843-2590", "services": "Floorcare"},

    # Nashville (9)
    {"branch_number": "4052", "branch_name": "4052 - Nashville, TN", "address": "2927 Brick Church Pike", "city": "Nashville", "state": "TN", "zip": "37207", "phone": "615-960-0709", "services": "General Rentals"},
    {"branch_number": "4149", "branch_name": "4149 - Nashville, TN - ProSolutions", "address": "2927 Brick Church Pike", "city": "Nashville", "state": "TN", "zip": "37207", "phone": "615-960-0709", "services": "ProSolutions"},
    {"branch_number": "9241", "branch_name": "9241 - Nashville, TN - ProTruck", "address": "1320 Murfreesboro Road", "city": "Nashville", "state": "TN", "zip": "37217", "phone": "615-949-4140", "services": "ProTruck"},
    {"branch_number": "9308", "branch_name": "9308 - Nashville, TN - Floor Care Solutions", "address": "1320 Murfreesboro Road", "city": "Nashville", "state": "TN", "zip": "37217", "phone": "615-543-5813", "services": "Floorcare"},
    {"branch_number": "9309", "branch_name": "9309 - Nashville, TN", "address": "1320 Murfreesboro Road", "city": "Nashville", "state": "TN", "zip": "37217", "phone": "615-949-4140", "services": "General Rentals"},
    {"branch_number": "9312", "branch_name": "9312 - Nashville, TN - Crane", "address": "1320 Murfreesboro Road", "city": "Nashville", "state": "TN", "zip": "37217", "phone": "615-949-4140", "services": "Crane"},
    {"branch_number": "9314", "branch_name": "9314 - Chattanooga, TN", "address": "1625 Riverside Drive", "city": "Chattanooga", "state": "TN", "zip": "37406", "phone": "423-622-5144", "services": "General Rentals"},
    {"branch_number": "9316", "branch_name": "9316 - Knoxville, TN", "address": "4616 Central Ave Pike", "city": "Knoxville", "state": "TN", "zip": "37912", "phone": "865-687-1445", "services": "General Rentals"},
    {"branch_number": "9319", "branch_name": "9319 - Jackson, TN", "address": "85 Vann Drive", "city": "Jackson", "state": "TN", "zip": "38305", "phone": "731-668-8100", "services": "General Rentals"},

    # Austin (7)
    {"branch_number": "9419", "branch_name": "9419 - Austin, TX", "address": "3737 Airport Blvd", "city": "Austin", "state": "TX", "zip": "78722", "phone": "737-702-5567", "services": "Electrical Trades"},
    {"branch_number": "9515", "branch_name": "9515 - Austin, TX - ProSolutions CRC", "address": "4812 N Interstate Hwy 35", "city": "Austin", "state": "TX", "zip": "78751", "phone": "737-600-0914", "services": "ProSolutions"},
    {"branch_number": "9474", "branch_name": "9474 - South Austin, TX - ProTruck", "address": "14701 S I-35 Frontage Road", "city": "Buda", "state": "TX", "zip": "78610", "phone": "737-353-0178", "services": "ProTruck"},
    {"branch_number": "9548", "branch_name": "9548 - Austin, TX", "address": "10926 S. US Highway 183", "city": "Austin", "state": "TX", "zip": "78747", "phone": "512-243-9822", "services": "General Rentals"},
    {"branch_number": "9470", "branch_name": "9470 - Austin, TX - ProSolutions", "address": "1200 N. Industrial Blvd", "city": "Round Rock", "state": "TX", "zip": "78681", "phone": "737-600-0914", "services": "ProSolutions"},
    {"branch_number": "9471", "branch_name": "9471 - Round Rock, TX", "address": "1200 N. Industrial Blvd", "city": "Round Rock", "state": "TX", "zip": "78681", "phone": "512-246-2474", "services": "General Rentals"},
    {"branch_number": "9472", "branch_name": "9472 - Georgetown, TX", "address": "4100 S Interstate 35", "city": "Georgetown", "state": "TX", "zip": "78626", "phone": "512-819-8200", "services": "General Rentals"},

    # San Antonio (7)
    {"branch_number": "9416", "branch_name": "9416 - San Antonio, TX", "address": "668 North WW White Road", "city": "San Antonio", "state": "TX", "zip": "78219", "phone": "210-661-4281", "services": "Earthmoving"},
    {"branch_number": "4133", "branch_name": "4133 - West San Antonio, TX", "address": "402 Callaghan Road", "city": "San Antonio", "state": "TX", "zip": "78228", "phone": "210-229-7900", "services": "General Rentals"},
    {"branch_number": "9408", "branch_name": "9408 - San Antonio, TX - ProSolutions", "address": "11500 N. North Loop Road", "city": "San Antonio", "state": "TX", "zip": "78216", "phone": "210-962-6497", "services": "ProSolutions"},
    {"branch_number": "9542", "branch_name": "9542 - San Antonio, TX", "address": "11500 N. North Loop Road", "city": "San Antonio", "state": "TX", "zip": "78216", "phone": "210-496-1227", "services": "General Rentals"},
    {"branch_number": "9514", "branch_name": "9514 - San Antonio, TX - ProSolutions CRC", "address": "11500 N. North Loop Road", "city": "San Antonio", "state": "TX", "zip": "78216", "phone": "210-962-6497", "services": "ProSolutions"},
    {"branch_number": "9544", "branch_name": "9544 - San Antonio, TX - Floor Care", "address": "11500 N. North Loop Road", "city": "San Antonio", "state": "TX", "zip": "78216", "phone": "210-496-1227", "services": "Floorcare"},
    {"branch_number": "9545", "branch_name": "9545 - San Antonio, TX - ProTruck", "address": "11500 N. North Loop Road", "city": "San Antonio", "state": "TX", "zip": "78216", "phone": "210-496-1227", "services": "ProTruck"},
]

# More cities to add - Jacksonville, Columbus, Cleveland, Pittsburgh, Baltimore, Kansas City, St. Louis, New Orleans, Indianapolis, Raleigh, Portland, Richmond, Cincinnati, Louisville, Birmingham, Memphis, Salt Lake City
MORE_BRANCHES = [
    # Jacksonville (5)
    {"branch_number": "4072", "branch_name": "4072 - Jacksonville, FL", "address": "240 Hammond Boulevard", "city": "Jacksonville", "state": "FL", "zip": "32254", "phone": "904-479-7100", "services": "General Rentals"},
    {"branch_number": "9273", "branch_name": "9273 - North Jacksonville, FL", "address": "11400 New Berlin Road", "city": "Jacksonville", "state": "FL", "zip": "32226", "phone": "904-865-6707", "services": "General Rentals"},
    {"branch_number": "9387", "branch_name": "9387 - Jacksonville, FL - ProSolutions", "address": "11400 New Berlin Road", "city": "Jacksonville", "state": "FL", "zip": "32226", "phone": "904-262-5838", "services": "ProSolutions"},
    {"branch_number": "9373", "branch_name": "9373 - Jacksonville, FL", "address": "11451 Phillips Highway", "city": "Jacksonville", "state": "FL", "zip": "32256", "phone": "904-262-5838", "services": "General Rentals"},
    {"branch_number": "9284", "branch_name": "9284 - Jacksonville, FL - ProSolutions CRC", "address": "11451 Phillips Highway", "city": "Jacksonville", "state": "FL", "zip": "32256", "phone": "904-262-5838", "services": "ProSolutions"},

    # Columbus (6)
    {"branch_number": "9131", "branch_name": "9131 - Columbus, OH", "address": "523 Stimmel Road", "city": "Columbus", "state": "OH", "zip": "43223", "phone": "614-683-7104", "services": "Crawler Crane"},
    {"branch_number": "9218", "branch_name": "9218 - Columbus, OH - ProTruck", "address": "2290 Ayers Drive", "city": "Reynoldsburg", "state": "OH", "zip": "43068", "phone": "614-683-7104", "services": "ProTruck"},
    {"branch_number": "9219", "branch_name": "9219 - Columbus, OH - ProSolutions", "address": "523 Stimmel Road", "city": "Columbus", "state": "OH", "zip": "43223", "phone": "614-683-7104", "services": "ProSolutions"},
    {"branch_number": "9202", "branch_name": "9202 - Columbus, OH - ProSolutions CRC", "address": "523 Stimmel Road", "city": "Columbus", "state": "OH", "zip": "43223", "phone": "203-309-1099", "services": "ProSolutions"},
    {"branch_number": "4170", "branch_name": "4170 - Columbus, OH", "address": "6390 Shier Rings Rd", "city": "Dublin", "state": "OH", "zip": "43106", "phone": "380-800-7114", "services": "General Rentals"},
    {"branch_number": "9547", "branch_name": "9547 - Columbus, OH", "address": "2290 Ayers Drive", "city": "Reynoldsburg", "state": "OH", "zip": "43068", "phone": "614-866-7770", "services": "General Rentals"},

    # Cleveland (4)
    {"branch_number": "9154", "branch_name": "9154 - Cleveland, OH", "address": "21913 Aurora Road", "city": "Bedford Heights", "state": "OH", "zip": "44146", "phone": "216-435-0739", "services": "General Rentals"},
    {"branch_number": "9563", "branch_name": "9563 - Berea, OH", "address": "1004 W. Bagley Road", "city": "Berea", "state": "OH", "zip": "44017", "phone": "440-467-4743", "services": "Carry Deck Crane"},
    {"branch_number": "9527", "branch_name": "9527 - Cleveland, OH - ProSolutions", "address": "1004 W. Bagley Road", "city": "Berea", "state": "OH", "zip": "44017", "phone": "440-202-7741", "services": "ProSolutions"},
    {"branch_number": "9528", "branch_name": "9528 - Cleveland, OH - ProSolutions CRC", "address": "1004 W. Bagley Road", "city": "Berea", "state": "OH", "zip": "44017", "phone": "440-202-7741", "services": "ProSolutions"},

    # Pittsburgh (6)
    {"branch_number": "9105", "branch_name": "9105 - Pittsburgh, PA - ProTruck", "address": "2001 William Flynn Highway", "city": "Glenshaw", "state": "PA", "zip": "15116", "phone": "412-960-8109", "services": "ProTruck"},
    {"branch_number": "9159", "branch_name": "9159 - Pittsburgh, PA - ProSolutions", "address": "492 Avenue B", "city": "Leetsdale", "state": "PA", "zip": "15056", "phone": "412-492-4082", "services": "ProSolutions"},
    {"branch_number": "9161", "branch_name": "9161 - Pittsburgh, PA", "address": "2001 William Flynn Hwy", "city": "Glenshaw", "state": "PA", "zip": "15116", "phone": "412-960-8109", "services": "General Rentals"},
    {"branch_number": "9189", "branch_name": "9189 - Pittsburgh, PA - ProSolutions CRC", "address": "492 Avenue B", "city": "Leetsdale", "state": "PA", "zip": "15056", "phone": "412-492-4082", "services": "ProSolutions"},
    {"branch_number": "9149", "branch_name": "9149 - Pittsburgh, PA - Floor Care Solutions", "address": "2001 William Flynn Hwy", "city": "Glenshaw", "state": "PA", "zip": "15116", "phone": "412-960-8109", "services": "Floorcare"},
    {"branch_number": "9150", "branch_name": "9150 - Pittsburgh, PA", "address": "492 Avenue B", "city": "Leetsdale", "state": "PA", "zip": "15056", "phone": "412-492-4082", "services": "General Rentals"},

    # Baltimore (9)
    {"branch_number": "9112", "branch_name": "9112 - Baltimore, MD", "address": "2111 Grays Road", "city": "Dundalk", "state": "MD", "zip": "21222", "phone": "443-496-3533", "services": "General Rentals"},
    {"branch_number": "9261", "branch_name": "9261 - Baltimore, MD - ProSolutions", "address": "1200 Chesapeake Ave", "city": "Curtis Bay", "state": "MD", "zip": "21226", "phone": "240-927-4744", "services": "ProSolutions"},
    {"branch_number": "9279", "branch_name": "9279 - Baltimore, MD - ProTruck", "address": "2111 Grays Road", "city": "Dundalk", "state": "MD", "zip": "21222", "phone": "443-496-3533", "services": "ProTruck"},
    {"branch_number": "4366", "branch_name": "4366 - Baltimore, MD - ProSolutions, Chiller", "address": "1200 Chesapeake Ave", "city": "Baltimore", "state": "MD", "zip": "21226", "phone": "877-750-0072", "services": "ProSolutions"},
    {"branch_number": "9972", "branch_name": "9972 - Pasadena, MD", "address": "8004 Jumpers Hole Road", "city": "Pasadena", "state": "MD", "zip": "21122", "phone": "667-470-2876", "services": "General Rentals"},
    {"branch_number": "9262", "branch_name": "9262 - Baltimore, MD - ProSolutions CRC", "address": "1200 Chesapeake Ave", "city": "Curtis Bay", "state": "MD", "zip": "21226", "phone": "240-927-4744", "services": "ProSolutions"},
    {"branch_number": "9113", "branch_name": "9113 - Baltimore, MD - Floor Care", "address": "2111 Grays Road", "city": "Dundalk", "state": "MD", "zip": "21222", "phone": "443-496-3533", "services": "Floorcare"},
    {"branch_number": "9280", "branch_name": "9280 - DC Metro", "address": "7401 Accole Place", "city": "Landover", "state": "MD", "zip": "20785", "phone": "301-322-8700", "services": "General Rentals"},
    {"branch_number": "9282", "branch_name": "9282 - DC Metro - ProSolutions", "address": "7401 Accole Place", "city": "Landover", "state": "MD", "zip": "20785", "phone": "301-322-8700", "services": "ProSolutions"},

    # Kansas City (8)
    {"branch_number": "9414", "branch_name": "9414 - Kansas City, MO - Floor Care Solutions", "address": "707 E 16th Street", "city": "Kansas City", "state": "MO", "zip": "64108", "phone": "816-800-9858", "services": "Floorcare"},
    {"branch_number": "9422", "branch_name": "9422 - Kansas City, MO", "address": "707 East 16t Street", "city": "Kansas City", "state": "MO", "zip": "64108", "phone": "816-800-9858", "services": "Carry Deck Crane"},
    {"branch_number": "9440", "branch_name": "9440 - Kansas City, MO - ProTruck", "address": "4100 N Kimball Drive", "city": "Kansas City", "state": "MO", "zip": "64161", "phone": "816-800-9858", "services": "ProTruck"},
    {"branch_number": "9424", "branch_name": "9424 - Kansas City. MO - ProSolutions", "address": "1460 SE Hamblen Road", "city": "Lees Summit", "state": "MO", "zip": "64081", "phone": "816-666-9409", "services": "ProSolutions"},
    {"branch_number": "9437", "branch_name": "9437 - Kansas City, MO - ProSolutions CRC", "address": "1460 SE Hamblen Road", "city": "Lees Summit", "state": "MO", "zip": "64081", "phone": "816-666-9409", "services": "ProSolutions"},
    {"branch_number": "9423", "branch_name": "9423 - Kansas City, MO", "address": "4100 N Kimball Drive", "city": "Kansas City", "state": "MO", "zip": "64161", "phone": "816-453-0600", "services": "General Rentals"},
    {"branch_number": "9441", "branch_name": "9441 - Lees Summit, MO", "address": "1460 SE Hamblen Road", "city": "Lees Summit", "state": "MO", "zip": "64081", "phone": "816-666-9409", "services": "General Rentals"},
    {"branch_number": "9442", "branch_name": "9442 - Olathe, KS", "address": "221 N Lindenwood Drive", "city": "Olathe", "state": "KS", "zip": "66062", "phone": "913-782-7600", "services": "General Rentals"},

    # St. Louis (9)
    {"branch_number": "9456", "branch_name": "9456 - St Louis, MO", "address": "3030 Market Street", "city": "St Louis", "state": "MO", "zip": "63103", "phone": "314-987-0418", "services": "General Rentals"},
    {"branch_number": "4371", "branch_name": "4371 - St. Louis, MO - ProResources", "address": "1087 State Route 3", "city": "National Stock Yards", "state": "IL", "zip": "62071", "phone": "833-591-7563", "services": "ProResources"},
    {"branch_number": "1304", "branch_name": "1304 - Saint Louis", "address": "1087 State Route 3", "city": "Fairmont City", "state": "IL", "zip": "62071", "phone": "618-500-5903", "services": "General Rentals"},
    {"branch_number": "9901", "branch_name": "9901 - Hazelwood, MO", "address": "183 James S. McDonnell Blvd", "city": "Hazelwood", "state": "MO", "zip": "63042", "phone": "314-652-3288", "services": "General Rentals"},
    {"branch_number": "4188", "branch_name": "4188 - West St. Louis, MO", "address": "10022 Meeks Boulevard", "city": "St. Louis", "state": "MO", "zip": "63132", "phone": "557-467-6905", "services": "General Rentals"},
    {"branch_number": "9443", "branch_name": "9443 - St. Louis, MO - ProSolutions", "address": "183 James S. McDonnell Blvd", "city": "Hazelwood", "state": "MO", "zip": "63042", "phone": "314-652-3288", "services": "ProSolutions"},
    {"branch_number": "9444", "branch_name": "9444 - St. Louis, MO - Floor Care", "address": "183 James S. McDonnell Blvd", "city": "Hazelwood", "state": "MO", "zip": "63042", "phone": "314-652-3288", "services": "Floorcare"},
    {"branch_number": "9454", "branch_name": "9454 - St. Louis, MO - ProTruck", "address": "183 James S. McDonnell Blvd", "city": "Hazelwood", "state": "MO", "zip": "63042", "phone": "314-652-3288", "services": "ProTruck"},
    {"branch_number": "9457", "branch_name": "9457 - Springfield, MO", "address": "3009 N Glenstone Ave", "city": "Springfield", "state": "MO", "zip": "65803", "phone": "417-831-3100", "services": "General Rentals"},

    # New Orleans (5)
    {"branch_number": "4070", "branch_name": "4070 - New Orleans, LA", "address": "4202 Almonaster Avenue", "city": "New Orleans", "state": "LA", "zip": "70126", "phone": "504-689-6027", "services": "General Rentals"},
    {"branch_number": "9288", "branch_name": "9288 - New Orleans, LA - ProSolutions", "address": "1421 MacArthur Avenue", "city": "Harvey", "state": "LA", "zip": "70058", "phone": "504-298-9650", "services": "ProSolutions"},
    {"branch_number": "9209", "branch_name": "9209 - New Orleans, LA - ProSolutions CRC", "address": "1421 MacArthur Avenue", "city": "Harvey", "state": "LA", "zip": "70058", "phone": "504-298-9650", "services": "ProSolutions"},
    {"branch_number": "4112", "branch_name": "4112 - Kenner, LA - ProSolutions", "address": "212 E Airline Highway", "city": "Kenner", "state": "LA", "zip": "70062", "phone": "504-502-8230", "services": "ProSolutions"},
    {"branch_number": "9242", "branch_name": "9242 - New Orleans, LA", "address": "141 West Airline HIghway", "city": "Kenner", "state": "LA", "zip": "70062", "phone": "504-539-4157", "services": "Big Air"},

    # Indianapolis (5)
    {"branch_number": "9529", "branch_name": "9529 - SW Indianapolis, IN", "address": "4301 West Morris Street", "city": "Indianapolis", "state": "IN", "zip": "46241", "phone": "463-296-5205", "services": "General Rentals"},
    {"branch_number": "9651", "branch_name": "9651 - Indianapolis, IN - ProTruck", "address": "4301 West Morris Street", "city": "Indianapolis", "state": "IN", "zip": "46241", "phone": "463-296-5205", "services": "ProTruck"},
    {"branch_number": "1308", "branch_name": "1308 - Indianapolis, IN", "address": "5520 W 96th Street", "city": "Zionsville", "state": "IN", "zip": "46077", "phone": "463-307-2979", "services": "General Rentals"},
    {"branch_number": "9132", "branch_name": "9132 - Northeast Indianapolis, IN", "address": "9010 Corporation Drive", "city": "Indianapolis", "state": "IN", "zip": "46256", "phone": "463-895-5416", "services": "General Rentals"},
    {"branch_number": "9199", "branch_name": "9199 - Indianapolis, IN - ProSolutions", "address": "9010 Corporation Drive", "city": "Indianapolis", "state": "IN", "zip": "46256", "phone": "463-895-5416", "services": "ProSolutions"},

    # Raleigh (16 branches - large area)
    {"branch_number": "9325", "branch_name": "9325 - Raleigh, NC", "address": "1409 Capital Blvd", "city": "Raleigh", "state": "NC", "zip": "27603", "phone": "984-276-1110", "services": "General Rentals"},
    {"branch_number": "9303", "branch_name": "9303 - Raleigh, NC - Aerial", "address": "1409 Capital Blvd", "city": "Raleigh", "state": "NC", "zip": "27603", "phone": "984-276-1110", "services": "Aerial"},
    {"branch_number": "9315", "branch_name": "9315 - Raleigh, NC - Floor Care Solutions", "address": "1409 Capital Blvd", "city": "Raleigh", "state": "NC", "zip": "27603", "phone": "984-276-1110", "services": "Floorcare"},
    {"branch_number": "1117", "branch_name": "1117 - Raleigh", "address": "3821 Generosity Court", "city": "Garner", "state": "NC", "zip": "27529", "phone": "984-326-6162", "services": "General Rentals"},
    {"branch_number": "4102", "branch_name": "4102 - North Raleigh", "address": "2701 Connector Drive", "city": "Wake Forest", "state": "NC", "zip": "27587", "phone": "984-339-2191", "services": "General Rentals"},
    {"branch_number": "4152", "branch_name": "4152 - Durham, NC", "address": "1011 Slater Road", "city": "Durham", "state": "NC", "zip": "27703", "phone": "984-242-2101", "services": "General Rentals"},
    {"branch_number": "9326", "branch_name": "9326 - Greensboro, NC", "address": "3801 W Wendover Ave", "city": "Greensboro", "state": "NC", "zip": "27407", "phone": "336-855-3550", "services": "General Rentals"},
    {"branch_number": "9327", "branch_name": "9327 - Winston-Salem, NC", "address": "2930 N Patterson Ave", "city": "Winston-Salem", "state": "NC", "zip": "27105", "phone": "336-722-4770", "services": "General Rentals"},
    {"branch_number": "9328", "branch_name": "9328 - High Point, NC", "address": "250 Pendleton St", "city": "High Point", "state": "NC", "zip": "27260", "phone": "336-885-9100", "services": "General Rentals"},
    {"branch_number": "9329", "branch_name": "9329 - Fayetteville, NC", "address": "1914 Bragg Blvd", "city": "Fayetteville", "state": "NC", "zip": "28303", "phone": "910-484-8410", "services": "General Rentals"},
    {"branch_number": "9330", "branch_name": "9330 - Wilmington, NC", "address": "4210 US Highway 421", "city": "Wilmington", "state": "NC", "zip": "28401", "phone": "910-762-4212", "services": "General Rentals"},
    {"branch_number": "9333", "branch_name": "9333 - Raleigh, NC - ProSolutions", "address": "1409 Capital Blvd", "city": "Raleigh", "state": "NC", "zip": "27603", "phone": "984-276-1110", "services": "ProSolutions"},
    {"branch_number": "9334", "branch_name": "9334 - Raleigh, NC - ProTruck", "address": "1409 Capital Blvd", "city": "Raleigh", "state": "NC", "zip": "27603", "phone": "984-276-1110", "services": "ProTruck"},
    {"branch_number": "9335", "branch_name": "9335 - Charlotte, NC - ProSolutions", "address": "4429 Equipment Drive", "city": "Charlotte", "state": "NC", "zip": "28269", "phone": "704-598-0241", "services": "ProSolutions"},
    {"branch_number": "9338", "branch_name": "9338 - Greensboro, NC - ProSolutions", "address": "3801 W Wendover Ave", "city": "Greensboro", "state": "NC", "zip": "27407", "phone": "336-855-3550", "services": "ProSolutions"},
    {"branch_number": "9339", "branch_name": "9339 - Wilmington, NC - ProSolutions", "address": "4210 US Highway 421", "city": "Wilmington", "state": "NC", "zip": "28401", "phone": "910-762-4212", "services": "ProSolutions"},

    # Portland (9)
    {"branch_number": "9700", "branch_name": "9700 - Portland, OR - ProSolutions CRC", "address": "2900 NE Marine Drive", "city": "Portland", "state": "OR", "zip": "97211", "phone": "971-369-9056", "services": "ProSolutions"},
    {"branch_number": "9701", "branch_name": "9701 - Portland, OR - ProSolutions", "address": "2900 NE Marine Drive", "city": "Portland", "state": "OR", "zip": "97211", "phone": "971-369-9056", "services": "ProSolutions"},
    {"branch_number": "9723", "branch_name": "9723 - Portland, OR - Floor Care Solutions", "address": "2900 NE Marine Drive", "city": "Portland", "state": "OR", "zip": "97211", "phone": "503-964-6718", "services": "Floorcare"},
    {"branch_number": "9724", "branch_name": "9724 - Portland, OR", "address": "5730 NE 138th Avenue", "city": "Portland", "state": "OR", "zip": "97230", "phone": "503-964-6718", "services": "General Rentals"},
    {"branch_number": "9787", "branch_name": "9787 - Portland, OR - Trench Solutions", "address": "2900 NE Marine Drive", "city": "Portland", "state": "OR", "zip": "97230", "phone": "971-369-9056", "services": "Trench Solutions"},
    {"branch_number": "9726", "branch_name": "9726 - Portland, OR - ProTruck", "address": "2900 NE Marine Drive", "city": "Portland", "state": "OR", "zip": "97211", "phone": "971-369-9056", "services": "ProTruck"},
    {"branch_number": "9727", "branch_name": "9727 - Salem, OR", "address": "3985 Fairview Industrial Dr", "city": "Salem", "state": "OR", "zip": "97302", "phone": "503-390-0900", "services": "General Rentals"},
    {"branch_number": "9728", "branch_name": "9728 - Eugene, OR", "address": "1155 South Bertelsen Road", "city": "Eugene", "state": "OR", "zip": "97402", "phone": "541-686-4477", "services": "General Rentals"},
    {"branch_number": "9780", "branch_name": "9780 - Vancouver, WA", "address": "12506 NE 112th Ave", "city": "Vancouver", "state": "WA", "zip": "98682", "phone": "360-254-5000", "services": "General Rentals"},

    # Richmond (7)
    {"branch_number": "9160", "branch_name": "9160 - South Richmond, VA", "address": "9300 Burge Avenue", "city": "Richmond", "state": "VA", "zip": "23237", "phone": "804-583-1340", "services": "General Rentals"},
    {"branch_number": "9260", "branch_name": "9260 - Richmond, VA - ProSolutions", "address": "10990 Airpark Road", "city": "Ashland", "state": "VA", "zip": "23005", "phone": "804-999-7041", "services": "ProSolutions"},
    {"branch_number": "9264", "branch_name": "9264 - North Richmond, VA", "address": "10990 Airpark Road", "city": "Ashland", "state": "VA", "zip": "23005", "phone": "804-988-5534", "services": "General Rentals"},
    {"branch_number": "9276", "branch_name": "9276 - Richmond, VA - ProTruck", "address": "10990 Airpark Road", "city": "Ashland", "state": "VA", "zip": "23005", "phone": "804-988-5534", "services": "ProTruck"},
    {"branch_number": "9206", "branch_name": "9206 - Richmond, VA - ProSolutions CRC", "address": "10990 Airpark Road", "city": "Ashland", "state": "VA", "zip": "23005", "phone": "888-358-0431", "services": "ProSolutions"},
    {"branch_number": "9265", "branch_name": "9265 - Richmond, VA - Floor Care", "address": "10990 Airpark Road", "city": "Ashland", "state": "VA", "zip": "23005", "phone": "804-988-5534", "services": "Floorcare"},
    {"branch_number": "9267", "branch_name": "9267 - Norfolk, VA", "address": "1320 Diamond Springs Road", "city": "Virginia Beach", "state": "VA", "zip": "23455", "phone": "757-622-6321", "services": "General Rentals"},

    # Cincinnati (4)
    {"branch_number": "9111", "branch_name": "9111 - Cincinnati, OH - Floorcare Solutions", "address": "1438 E. Galbraith Road", "city": "Cincinnati", "state": "OH", "zip": "45215", "phone": "513-938-2748", "services": "Floorcare"},
    {"branch_number": "9153", "branch_name": "9153 - Cincinnati, OH", "address": "1438 E. Galbraith Road", "city": "Cincinnati", "state": "OH", "zip": "45215", "phone": "513-938-2748", "services": "General Rentals"},
    {"branch_number": "4195", "branch_name": "4195 - Harrison, OH", "address": "9117 Kilby Road", "city": "Harrison", "state": "OH", "zip": "45030", "phone": "513-975-4980", "services": "General Rentals"},
    {"branch_number": "4380", "branch_name": "4380 - Cincinnati, OH - ProSolutions", "address": "9117 Kilby Rd", "city": "Harrison", "state": "OH", "zip": "45030", "phone": "888-559-0417", "services": "ProSolutions"},

    # Louisville (6)
    {"branch_number": "4137", "branch_name": "4137 - Louisville, KY - ProSolutions", "address": "3650 Cane Run Road", "city": "Louisville", "state": "KY", "zip": "40211", "phone": "502-790-0800", "services": "ProSolutions"},
    {"branch_number": "9266", "branch_name": "9266 - South Louisville, KY", "address": "130 Outer Loop", "city": "Louisville", "state": "KY", "zip": "40214", "phone": "502-977-4661", "services": "General Rentals"},
    {"branch_number": "9880", "branch_name": "9880 - Louisville, KY - ProTruck", "address": "10700 Bluegrass Parkway", "city": "Louisville", "state": "KY", "zip": "40299", "phone": "502-963-3523", "services": "ProTruck"},
    {"branch_number": "1307", "branch_name": "1307 - Louisville, KY", "address": "10700 Bluegrass Parkway", "city": "Louisville", "state": "KY", "zip": "40299", "phone": "502-963-3523", "services": "General Rentals"},
    {"branch_number": "9166", "branch_name": "9166 - Louisville, KY", "address": "13159 Middletown Ind. Blvd", "city": "Louisville", "state": "KY", "zip": "40223", "phone": "502-443-9056", "services": "General Rentals"},
    {"branch_number": "9168", "branch_name": "9168 - Lexington, KY", "address": "1021 Floyd Drive", "city": "Lexington", "state": "KY", "zip": "40505", "phone": "859-253-2400", "services": "General Rentals"},

    # Birmingham (7)
    {"branch_number": "9380", "branch_name": "9380 - Bessemer, AL - ProSolutions", "address": "2501 Fivestar Pkwy", "city": "Bessemer", "state": "AL", "zip": "35022", "phone": "205-744-9199", "services": "ProSolutions"},
    {"branch_number": "9390", "branch_name": "9390 - Bessemer, AL - ProSolutions CRC", "address": "2501 Fivestar Pkwy", "city": "Bessemer", "state": "AL", "zip": "35022", "phone": "205-744-9199", "services": "ProSolutions"},
    {"branch_number": "9354", "branch_name": "9354 - Pelham, AL", "address": "2150 Pelham Parkway", "city": "Pelham", "state": "AL", "zip": "35124", "phone": "205-988-8530", "services": "General Rentals"},
    {"branch_number": "9248", "branch_name": "9248 - Birmingham, AL - Floor Care Solutions", "address": "2150 Pelham Parkway", "city": "Pelham", "state": "AL", "zip": "35124", "phone": "205-988-8530", "services": "Floorcare"},
    {"branch_number": "4317", "branch_name": "4317 - Birmingham, AL - ProTruck", "address": "806 Labarge Drive", "city": "Bessemer", "state": "AL", "zip": "35022", "phone": "833-967-6026", "services": "ProTruck"},
    {"branch_number": "9355", "branch_name": "9355 - Birmingham, AL", "address": "806 Labarge Drive", "city": "Bessemer", "state": "AL", "zip": "35022", "phone": "205-744-9199", "services": "General Rentals"},
    {"branch_number": "9357", "branch_name": "9357 - Huntsville, AL", "address": "3225 Meridian St N", "city": "Huntsville", "state": "AL", "zip": "35811", "phone": "256-534-8585", "services": "General Rentals"},

    # Memphis (5)
    {"branch_number": "9201", "branch_name": "9201 - Memphis, TN", "address": "673 East Brooks Road", "city": "Memphis", "state": "TN", "zip": "38116", "phone": "901-398-4372", "services": "General Rentals"},
    {"branch_number": "9226", "branch_name": "9226 - Memphis, TN - Floor Care Solutions", "address": "673 East Brooks Road", "city": "Memphis", "state": "TN", "zip": "38116", "phone": "901-398-4372", "services": "Floorcare"},
    {"branch_number": "9207", "branch_name": "9207 - Memphis, TN - ProSolutions", "address": "3850 Old Getwell Road", "city": "Memphis", "state": "TN", "zip": "38116", "phone": "901-214-9300", "services": "ProSolutions"},
    {"branch_number": "9208", "branch_name": "9208 - Memphis, TN - ProSolutions CRC", "address": "3850 Old Getwell Road", "city": "Memphis", "state": "TN", "zip": "38116", "phone": "901-214-9300", "services": "ProSolutions"},
    {"branch_number": "4028", "branch_name": "4028 - Memphis, TN", "address": "5245 Highway 78", "city": "Memphis", "state": "TN", "zip": "38118", "phone": "901-375-4902", "services": "General Rentals"},

    # Salt Lake City (5)
    {"branch_number": "9609", "branch_name": "9609 - Salt Lake City, UT - ProTruck", "address": "2120 S 3600 W", "city": "West Valley City", "state": "UT", "zip": "84119", "phone": "866-287-8001", "services": "ProTruck"},
    {"branch_number": "9614", "branch_name": "9614 - Salt Lake CIty, UT - ProSolutions", "address": "2120 3600 W", "city": "West Valley City", "state": "UT", "zip": "84119", "phone": "801-977-9944", "services": "ProSolutions"},
    {"branch_number": "9615", "branch_name": "9615 - Salt Lake City, UT", "address": "2120 3600 W", "city": "West Valley City", "state": "UT", "zip": "84119", "phone": "801-977-9944", "services": "General Rentals"},
    {"branch_number": "9616", "branch_name": "9616 - Salt Lake City, UT - Floor Care Solutions", "address": "2120 3600 W", "city": "West Valley", "state": "UT", "zip": "84119", "phone": "801-977-9944", "services": "Floorcare"},
    {"branch_number": "4034", "branch_name": "4034 - Salt Lake City, UT", "address": "5052 West 2400 S, Building A", "city": "Salt Lake City", "state": "UT", "zip": "84120", "phone": "801-908-6400", "services": "General Rentals"},
]


def main():
    print("Updating Herc Rentals branches JSON...")

    # Load existing data
    json_path = os.path.join(BASE_DIR, "herc_web_branches.json")

    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            data = json.load(f)
    else:
        data = {
            "supplier": "Herc Rentals",
            "extraction_date": datetime.now().strftime('%Y-%m-%d'),
            "extraction_method": "Browser automation - city search",
            "status": "IN_PROGRESS",
            "branches": [],
            "regions_searched": []
        }

    existing_branches = data.get('branches', [])
    existing_numbers = {b.get('branch_number') for b in existing_branches}

    print(f"Existing branches: {len(existing_branches)}")

    # Combine all new branches
    all_new = NEW_BRANCHES + MORE_BRANCHES

    # Add new branches (deduplicate by branch_number)
    added = 0
    for branch in all_new:
        if branch.get('branch_number') not in existing_numbers:
            existing_branches.append(branch)
            existing_numbers.add(branch.get('branch_number'))
            added += 1

    print(f"Added {added} new branches")

    # Update data
    data['branches'] = existing_branches
    data['total_branches'] = len(existing_branches)
    data['extraction_date'] = datetime.now().strftime('%Y-%m-%d')
    data['status'] = 'UPDATED'
    data['regions_searched'] = [
        "Los Angeles CA", "Houston TX", "New York NY/NJ", "Atlanta GA",
        "Chicago IL", "Dallas TX", "Phoenix AZ", "Miami FL", "Denver CO",
        "Seattle WA", "Boston MA", "Philadelphia PA", "Detroit MI",
        "Tampa FL", "Orlando FL", "Minneapolis MN", "San Francisco CA",
        "San Diego CA", "Las Vegas NV", "Nashville TN", "Austin TX",
        "San Antonio TX", "Jacksonville FL", "Columbus OH", "Cleveland OH",
        "Pittsburgh PA", "Baltimore MD", "Kansas City MO", "St. Louis MO",
        "New Orleans LA", "Indianapolis IN", "Raleigh NC", "Portland OR",
        "Richmond VA", "Cincinnati OH", "Louisville KY", "Birmingham AL",
        "Memphis TN", "Salt Lake City UT"
    ]

    # Save updated data
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\nTotal branches now: {len(existing_branches)}")
    print(f"Saved to: {json_path}")


if __name__ == "__main__":
    main()
