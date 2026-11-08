"""
YĀTRĀ AI — Location Resolution & Autocomplete Service
Provides precise geographic coordinates, metro cluster mapping,
and nearest transit hub discovery across Indian transport networks.
"""

import math
from typing import List, Dict, Any, Optional

# Canonical Location Database with precise coordinates
LOCATIONS_DB: List[Dict[str, Any]] = [
    # --- METRO CLUSTERS (CENTRAL NODES) ---
    {
        "id": "delhi-center",
        "name": "Delhi NCR",
        "category": "city",
        "city": "Delhi",
        "state": "Delhi",
        "code": "DELHI",
        "lat": 28.6139,
        "lng": 77.2090,
        "description": "National Capital Region metro cluster",
    },
    {
        "id": "mumbai-center",
        "name": "Mumbai Metropolitan Region",
        "category": "city",
        "city": "Mumbai",
        "state": "Maharashtra",
        "code": "MUMBAI",
        "lat": 18.9878,
        "lng": 72.8364,
        "description": "Financial capital metro cluster",
    },
    {
        "id": "bangalore-center",
        "name": "Bengaluru (Bangalore)",
        "category": "city",
        "city": "Bangalore",
        "state": "Karnataka",
        "code": "BLR-CITY",
        "lat": 12.9716,
        "lng": 77.5946,
        "description": "Silicon Valley of India metro cluster",
    },
    {
        "id": "kolkata-center",
        "name": "Kolkata (Calcutta)",
        "category": "city",
        "city": "Kolkata",
        "state": "West Bengal",
        "code": "CCU-CITY",
        "lat": 22.5726,
        "lng": 88.3639,
        "description": "Eastern metropolis and cultural hub",
    },
    {
        "id": "hyderabad-center",
        "name": "Hyderabad",
        "category": "city",
        "city": "Hyderabad",
        "state": "Telangana",
        "code": "HYD-CITY",
        "lat": 17.3850,
        "lng": 78.4867,
        "description": "Cyberabad & Deccan transit junction",
    },
    {
        "id": "chennai-center",
        "name": "Chennai (Madras)",
        "category": "city",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "code": "MAA-CITY",
        "lat": 13.0827,
        "lng": 80.2707,
        "description": "Southern industrial & coastal metropolis",
    },

    # --- AIRPORTS (IATA) ---
    {
        "id": "del-airport",
        "name": "Indira Gandhi International Airport (DEL)",
        "category": "airport",
        "city": "Delhi",
        "state": "Delhi",
        "code": "DEL",
        "lat": 28.5562,
        "lng": 77.1000,
        "description": "Terminals 1, 2, 3 • Airport Express Metro connected",
    },
    {
        "id": "bom-airport",
        "name": "Chhatrapati Shivaji Maharaj International Airport (BOM)",
        "category": "airport",
        "city": "Mumbai",
        "state": "Maharashtra",
        "code": "BOM",
        "lat": 19.0896,
        "lng": 72.8656,
        "description": "Terminals 1 & 2 • Western Express Highway",
    },
    {
        "id": "blr-airport",
        "name": "Kempegowda International Airport (BLR)",
        "category": "airport",
        "city": "Bangalore",
        "state": "Karnataka",
        "code": "BLR",
        "lat": 13.1986,
        "lng": 77.7066,
        "description": "Terminals 1 & 2 • Vayu Vajra Airport Bus Hub",
    },
    {
        "id": "ccu-airport",
        "name": "Netaji Subhash Chandra Bose International Airport (CCU)",
        "category": "airport",
        "city": "Kolkata",
        "state": "West Bengal",
        "code": "CCU",
        "lat": 22.6547,
        "lng": 88.4467,
        "description": "Integrated Terminal • VIP Road & Belghoria Expressway",
    },
    {
        "id": "hyd-airport",
        "name": "Rajiv Gandhi International Airport (HYD)",
        "category": "airport",
        "city": "Hyderabad",
        "state": "Telangana",
        "code": "HYD",
        "lat": 17.2403,
        "lng": 78.4294,
        "description": "Shamshabad • Pushpak Airport Liner Hub",
    },
    {
        "id": "maa-airport",
        "name": "Chennai International Airport (MAA)",
        "category": "airport",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "code": "MAA",
        "lat": 12.9941,
        "lng": 80.1709,
        "description": "Meenambakkam • Airport Metro connected",
    },

    # --- RAILWAY STATIONS (IRCTC CODES) ---
    # Delhi
    {
        "id": "ndls-station",
        "name": "New Delhi Railway Station (NDLS)",
        "category": "rail_station",
        "city": "Delhi",
        "state": "Delhi",
        "code": "NDLS",
        "lat": 28.6426,
        "lng": 77.2205,
        "description": "Primary northern terminus • Yellow & Airport Express Metro",
    },
    {
        "id": "nzm-station",
        "name": "Hazrat Nizamuddin Railway Station (NZM)",
        "category": "rail_station",
        "city": "Delhi",
        "state": "Delhi",
        "code": "NZM",
        "lat": 28.5884,
        "lng": 77.2536,
        "description": "Rajdhani & Vande Bharat hub • Sarai Kale Khan Metro",
    },
    {
        "id": "anvt-station",
        "name": "Anand Vihar Terminal (ANVT)",
        "category": "rail_station",
        "city": "Delhi",
        "state": "Delhi",
        "code": "ANVT",
        "lat": 28.6508,
        "lng": 77.3152,
        "description": "Eastbound rail terminus • Blue & Pink Metro",
    },
    {
        "id": "dli-station",
        "name": "Old Delhi Railway Station (DLI)",
        "category": "rail_station",
        "city": "Delhi",
        "state": "Delhi",
        "code": "DLI",
        "lat": 28.6608,
        "lng": 77.2307,
        "description": "Historic Chandni Chowk terminus • Yellow Metro",
    },

    # Mumbai
    {
        "id": "csmt-station",
        "name": "Chhatrapati Shivaji Maharaj Terminus (CSMT)",
        "category": "rail_station",
        "city": "Mumbai",
        "state": "Maharashtra",
        "code": "CSMT",
        "lat": 18.9401,
        "lng": 72.8351,
        "description": "UNESCO World Heritage Central Railway terminus",
    },
    {
        "id": "mmct-station",
        "name": "Mumbai Central Railway Station (MMCT)",
        "category": "rail_station",
        "city": "Mumbai",
        "state": "Maharashtra",
        "code": "MMCT",
        "lat": 18.9696,
        "lng": 72.8193,
        "description": "Western Railway Rajdhani terminus • Western Suburban Line",
    },
    {
        "id": "bdts-station",
        "name": "Bandra Terminus (BDTS)",
        "category": "rail_station",
        "city": "Mumbai",
        "state": "Maharashtra",
        "code": "BDTS",
        "lat": 19.0622,
        "lng": 72.8427,
        "description": "Northbound Superfast & Express hub",
    },
    {
        "id": "ltt-station",
        "name": "Lokmanya Tilak Terminus (LTT Kurla)",
        "category": "rail_station",
        "city": "Mumbai",
        "state": "Maharashtra",
        "code": "LTT",
        "lat": 19.0697,
        "lng": 72.8906,
        "description": "Central & Southbound long-distance terminal",
    },

    # Bangalore
    {
        "id": "sbc-station",
        "name": "KSR Bengaluru City Railway Station (SBC)",
        "category": "rail_station",
        "city": "Bangalore",
        "state": "Karnataka",
        "code": "SBC",
        "lat": 12.9778,
        "lng": 77.5713,
        "description": "Majestic central junction • Namma Metro Purple & Green Line",
    },
    {
        "id": "ypr-station",
        "name": "Yesvantpur Junction (YPR)",
        "category": "rail_station",
        "city": "Bangalore",
        "state": "Karnataka",
        "code": "YPR",
        "lat": 13.0238,
        "lng": 77.5503,
        "description": "Northwest bypass rail terminus • Green Metro",
    },
    {
        "id": "smvb-station",
        "name": "Sir M. Visvesvaraya Terminal (SMVB)",
        "category": "rail_station",
        "city": "Bangalore",
        "state": "Karnataka",
        "code": "SMVB",
        "lat": 13.0039,
        "lng": 77.6534,
        "description": "Baiyappanahalli AC rail terminal",
    },

    # Kolkata
    {
        "id": "hwh-station",
        "name": "Howrah Junction (HWH)",
        "category": "rail_station",
        "city": "Kolkata",
        "state": "West Bengal",
        "code": "HWH",
        "lat": 22.5830,
        "lng": 88.3426,
        "description": "Busiest railway terminus in India • Green Metro Line",
    },
    {
        "id": "sdah-station",
        "name": "Sealdah Railway Station (SDAH)",
        "category": "rail_station",
        "city": "Kolkata",
        "state": "West Bengal",
        "code": "SDAH",
        "lat": 22.5675,
        "lng": 88.3712,
        "description": "Suburban & long-distance hub • Green Metro Line",
    },
    {
        "id": "koaa-station",
        "name": "Kolkata Railway Station (KOAA / Chitpur)",
        "category": "rail_station",
        "city": "Kolkata",
        "state": "West Bengal",
        "code": "KOAA",
        "lat": 22.6033,
        "lng": 88.3742,
        "description": "North Kolkata express terminal",
    },

    # Hyderabad
    {
        "id": "sc-station",
        "name": "Secunderabad Junction (SC)",
        "category": "rail_station",
        "city": "Hyderabad",
        "state": "Telangana",
        "code": "SC",
        "lat": 17.4339,
        "lng": 78.5029,
        "description": "South Central Railway headquarters • Blue Line Metro",
    },
    {
        "id": "hyb-station",
        "name": "Hyderabad Deccan Station (HYB / Nampally)",
        "category": "rail_station",
        "city": "Hyderabad",
        "state": "Telangana",
        "code": "HYB",
        "lat": 17.3920,
        "lng": 78.4697,
        "description": "Historic city center terminus • Red Line Metro",
    },
    {
        "id": "kcg-station",
        "name": "Kacheguda Railway Station (KCG)",
        "category": "rail_station",
        "city": "Hyderabad",
        "state": "Telangana",
        "code": "KCG",
        "lat": 17.3879,
        "lng": 78.4975,
        "description": "Express terminal for southern corridors",
    },

    # Chennai
    {
        "id": "mas-station",
        "name": "Puratchi Thalaivar Dr. MGR Central (MAS)",
        "category": "rail_station",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "code": "MAS",
        "lat": 13.0827,
        "lng": 80.2755,
        "description": "Southern Railway main terminus • Central Metro",
    },
    {
        "id": "ms-station",
        "name": "Chennai Egmore Railway Station (MS)",
        "category": "rail_station",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "code": "MS",
        "lat": 13.0802,
        "lng": 80.2612,
        "description": "Tamil Nadu intercity express terminus • Egmore Metro",
    },
    {
        "id": "tbm-station",
        "name": "Tambaram Railway Station (TBM)",
        "category": "rail_station",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "code": "TBM",
        "lat": 12.9252,
        "lng": 80.1205,
        "description": "South Chennai terminal & suburban nexus",
    },

    # --- INTERCITY BUS TERMINALS (ISBT / KSRTC / MSRTC) ---
    {
        "id": "kashmere-gate-isbt",
        "name": "Maharana Pratap ISBT (Kashmere Gate)",
        "category": "bus_terminal",
        "city": "Delhi",
        "state": "Delhi",
        "code": "ISBT-KG",
        "lat": 28.6665,
        "lng": 77.2285,
        "description": "Interstate bus terminal for Punjab, Haryana, Himachal & UP",
    },
    {
        "id": "anand-vihar-isbt",
        "name": "Swami Vivekanand ISBT (Anand Vihar)",
        "category": "bus_terminal",
        "city": "Delhi",
        "state": "Delhi",
        "code": "ISBT-AV",
        "lat": 28.6469,
        "lng": 77.3160,
        "description": "Interstate bus terminal for Eastern UP & Uttarakhand",
    },
    {
        "id": "majestic-bus-station",
        "name": "Kempegowda Bus Station (Majestic)",
        "category": "bus_terminal",
        "city": "Bangalore",
        "state": "Karnataka",
        "code": "KBS-MAJESTIC",
        "lat": 12.9774,
        "lng": 77.5729,
        "description": "KSRTC, BMTC & private intercity bus nerve center",
    },
    {
        "id": "shantinagar-bus-station",
        "name": "Shantinagar Bus Station (KSRTC)",
        "category": "bus_terminal",
        "city": "Bangalore",
        "state": "Karnataka",
        "code": "KSRTC-SNT",
        "lat": 12.9536,
        "lng": 77.5956,
        "description": "Intercity Volvo & Sleeper services to Tamil Nadu & Andhra",
    },
    {
        "id": "cmbt-bus-station",
        "name": "Chennai Mofussil Bus Terminus (CMBT Koyambedu)",
        "category": "bus_terminal",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "code": "CMBT",
        "lat": 13.0694,
        "lng": 80.2057,
        "description": "Major interstate bus terminus in South Asia",
    },
    {
        "id": "mgbs-bus-station",
        "name": "Mahatma Gandhi Bus Station (MGBS / Imlibun)",
        "category": "bus_terminal",
        "city": "Hyderabad",
        "state": "Telangana",
        "code": "MGBS",
        "lat": 17.3786,
        "lng": 78.4820,
        "description": "TSRTC & interstate coach hub",
    },
    {
        "id": "mumbai-central-bus-depot",
        "name": "Mumbai Central MSRTC Bus Depot",
        "category": "bus_terminal",
        "city": "Mumbai",
        "state": "Maharashtra",
        "code": "MSRTC-MMCT",
        "lat": 18.9696,
        "lng": 72.8193,
        "description": "Shivneri & intercity luxury coach departure depot",
    },
    {
        "id": "esplanade-bus-station",
        "name": "Esplanade Bus Terminus",
        "category": "bus_terminal",
        "city": "Kolkata",
        "state": "West Bengal",
        "code": "ESPLANADE",
        "lat": 22.5645,
        "lng": 88.3516,
        "description": "Central Kolkata intercity & regional bus terminus",
    },

    # --- PROMINENT LANDMARKS & BUSINESS DISTRICTS ---
    # Delhi NCR
    {
        "id": "connaught-place",
        "name": "Connaught Place (CP / Rajiv Chowk)",
        "category": "landmark",
        "city": "Delhi",
        "state": "Delhi",
        "code": "CP-DELHI",
        "lat": 28.6315,
        "lng": 77.2167,
        "description": "Central business district & Rajiv Chowk Metro Interchange",
    },
    {
        "id": "cyber-city-gurgaon",
        "name": "DLF Cyber City, Gurugram",
        "category": "landmark",
        "city": "Delhi",
        "state": "Haryana",
        "code": "CYBER-CITY",
        "lat": 28.4952,
        "lng": 77.0895,
        "description": "Global corporate tech hub • Rapid Metro connectivity",
    },
    {
        "id": "india-gate",
        "name": "India Gate & Central Vista",
        "category": "landmark",
        "city": "Delhi",
        "state": "Delhi",
        "code": "INDIA-GATE",
        "lat": 28.6129,
        "lng": 77.2295,
        "description": "National landmark & Rajpath cultural boulevard",
    },
    {
        "id": "noida-sec-18",
        "name": "Sector 18 Commercial District, Noida",
        "category": "landmark",
        "city": "Delhi",
        "state": "Uttar Pradesh",
        "code": "NOIDA-18",
        "lat": 28.5708,
        "lng": 77.3261,
        "description": "Retail & business district • Blue Line Metro",
    },

    # Mumbai
    {
        "id": "bkc-mumbai",
        "name": "Bandra Kurla Complex (BKC)",
        "category": "landmark",
        "city": "Mumbai",
        "state": "Maharashtra",
        "code": "BKC",
        "lat": 19.0657,
        "lng": 72.8679,
        "description": "Premier financial center, NSE, US Consulate • Metro 3 Line",
    },
    {
        "id": "colaba-gateway",
        "name": "Gateway of India & Colaba",
        "category": "landmark",
        "city": "Mumbai",
        "state": "Maharashtra",
        "code": "GATEWAY",
        "lat": 18.9220,
        "lng": 72.8347,
        "description": "South Mumbai heritage waterfront & Taj Mahal Palace",
    },
    {
        "id": "nariman-point",
        "name": "Nariman Point & Marine Drive",
        "category": "landmark",
        "city": "Mumbai",
        "state": "Maharashtra",
        "code": "NARIMAN-PT",
        "lat": 18.9256,
        "lng": 72.8242,
        "description": "Queen's Necklace promenade & banking headquarters",
    },
    {
        "id": "andheri-east-midc",
        "name": "MIDC & SEEPZ, Andheri East",
        "category": "landmark",
        "city": "Mumbai",
        "state": "Maharashtra",
        "code": "ANDHERI-EAST",
        "lat": 19.1197,
        "lng": 72.8697,
        "description": "Commercial & hospitality corridor near airport",
    },

    # Bangalore
    {
        "id": "whitefield-it-park",
        "name": "ITPB & Whitefield Tech Corridor",
        "category": "landmark",
        "city": "Bangalore",
        "state": "Karnataka",
        "code": "WHITEFIELD",
        "lat": 12.9698,
        "lng": 77.7499,
        "description": "Major technology corridor • Purple Metro Line",
    },
    {
        "id": "mg-road-bangalore",
        "name": "MG Road & Brigade Road",
        "category": "landmark",
        "city": "Bangalore",
        "state": "Karnataka",
        "code": "MG-ROAD-BLR",
        "lat": 12.9756,
        "lng": 77.6066,
        "description": "Downtown commercial heart • Purple Line Metro",
    },
    {
        "id": "electronic-city-blr",
        "name": "Electronic City Phase 1",
        "category": "landmark",
        "city": "Bangalore",
        "state": "Karnataka",
        "code": "ECITY-BLR",
        "lat": 12.8452,
        "lng": 77.6602,
        "description": "Infosys, Wipro campuses • Elevated Expressway & Yellow Line",
    },
    {
        "id": "indiranagar-blr",
        "name": "100ft Road, Indiranagar",
        "category": "landmark",
        "city": "Bangalore",
        "state": "Karnataka",
        "code": "INDIRANAGAR",
        "lat": 12.9719,
        "lng": 77.6412,
        "description": "Vibrant culinary, startup and shopping avenue",
    },

    # Hyderabad
    {
        "id": "hitec-city",
        "name": "HITEC City / Cyber Towers, Madhapur",
        "category": "landmark",
        "city": "Hyderabad",
        "state": "Telangana",
        "code": "HITEC-CITY",
        "lat": 17.4435,
        "lng": 78.3772,
        "description": "Major IT corridor • Blue Line Metro terminus",
    },
    {
        "id": "charminar-old-city",
        "name": "Charminar & Laad Bazaar",
        "category": "landmark",
        "city": "Hyderabad",
        "state": "Telangana",
        "code": "CHARMINAR",
        "lat": 17.3616,
        "lng": 78.4747,
        "description": "Historic landmark & Old City cultural district",
    },
    {
        "id": "gachibowli-financial-district",
        "name": "Financial District, Gachibowli",
        "category": "landmark",
        "city": "Hyderabad",
        "state": "Telangana",
        "code": "GACHIBOWLI",
        "lat": 17.4123,
        "lng": 78.3444,
        "description": "Fintech & corporate headquarters corridor",
    },

    # Chennai
    {
        "id": "omr-it-corridor",
        "name": "Old Mahabalipuram Road (OMR IT Corridor)",
        "category": "landmark",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "code": "OMR-CHENNAI",
        "lat": 12.9352,
        "lng": 80.2376,
        "description": "Tidel Park, Thoraipakkam, Siruseri IT Expressway",
    },
    {
        "id": "t-nagar-chennai",
        "name": "T. Nagar (Panagal Park / Ranganathan St)",
        "category": "landmark",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "code": "T-NAGAR",
        "lat": 13.0418,
        "lng": 80.2341,
        "description": "Retail hub • Mambalam railway station connectivity",
    },
    {
        "id": "marina-beach-chennai",
        "name": "Marina Beach & Santhome",
        "category": "landmark",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "code": "MARINA-BEACH",
        "lat": 13.0500,
        "lng": 80.2824,
        "description": "Second longest urban natural beach in the world",
    },

    # Kolkata
    {
        "id": "park-street-kolkata",
        "name": "Park Street (Mother Teresa Sarani)",
        "category": "landmark",
        "city": "Kolkata",
        "state": "West Bengal",
        "code": "PARK-STREET",
        "lat": 22.5510,
        "lng": 88.3524,
        "description": "Cultural, culinary & heritage boulevard • Blue Metro Line",
    },
    {
        "id": "salt-lake-sec-v",
        "name": "Sector V, Salt Lake (Bidhannagar)",
        "category": "landmark",
        "city": "Kolkata",
        "state": "West Bengal",
        "code": "SALT-LAKE-V",
        "lat": 22.5735,
        "lng": 88.4331,
        "description": "Electronics Complex & IT park • Green Line Metro",
    },
    {
        "id": "victoria-memorial",
        "name": "Victoria Memorial & Maidan",
        "category": "landmark",
        "city": "Kolkata",
        "state": "West Bengal",
        "code": "VICTORIA-MEM",
        "lat": 22.5448,
        "lng": 88.3426,
        "description": "Historic marble monument & sprawling urban park",
    },
]


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes great-circle distance between two coordinate pairs in kilometers."""
    r = 6371.0  # Earth's radius in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(r * c, 2)


class LocationService:
    def __init__(self):
        self.locations = LOCATIONS_DB

    def autocomplete(
        self, query: str, category: Optional[str] = None, limit: int = 8
    ) -> List[Dict[str, Any]]:
        """
        Fuzzy & substring autocomplete across names, codes, cities, and categories.
        """
        q = query.strip().lower()
        if not q:
            # Return top hub defaults
            defaults = [
                loc for loc in self.locations
                if loc["category"] in ("city", "airport", "rail_station")
            ]
            return defaults[:limit]

        matches = []
        for loc in self.locations:
            if category and loc["category"] != category:
                continue

            score = 0
            name_lower = loc["name"].lower()
            code_lower = str(loc.get("code", "")).lower()
            city_lower = loc["city"].lower()
            desc_lower = loc.get("description", "").lower()

            if q == code_lower:
                score += 100
            elif q == name_lower:
                score += 90
            elif q in code_lower:
                score += 70
            elif name_lower.startswith(q):
                score += 60
            elif q in name_lower:
                score += 50
            elif city_lower.startswith(q):
                score += 40
            elif q in city_lower:
                score += 30
            elif q in desc_lower:
                score += 20

            if score > 0:
                matches.append((score, loc))

        matches.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in matches[:limit]]

    def resolve_location(self, query_or_code: str) -> Dict[str, Any]:
        """
        Resolves an input string (e.g. 'NDLS', 'Connaught Place', 'Delhi', 'BOM')
        into an authoritative location record with nearest transit hubs.
        """
        q = query_or_code.strip().lower()

        # Check for explicit metro city in query
        detected_city = None
        for c in ["mumbai", "delhi", "bangalore", "bengaluru", "kolkata", "hyderabad", "chennai"]:
            if c in q:
                detected_city = "Bangalore" if c == "bengaluru" else c.capitalize()
                break

        best_loc = None
        best_score = -1

        for loc in self.locations:
            score = 0
            name_lower = loc["name"].lower()
            code_lower = str(loc.get("code", "")).lower()
            city_lower = loc["city"].lower()

            if q == code_lower:
                score += 200
            elif q == name_lower:
                score += 180
            elif code_lower and code_lower in q:
                score += 150
            elif name_lower in q:
                score += 120
            elif q in name_lower:
                score += 100
            
            # City boost
            if detected_city and loc["city"].lower() == detected_city.lower():
                score += 50
                # If query just specifies the city name
                if q in (detected_city.lower(), f"{detected_city.lower()} city") and loc["category"] == "city":
                    score += 150

            # Token matching
            tokens = [t.strip(",.()[]") for t in q.split() if len(t) > 2]
            for t in tokens:
                if t in name_lower:
                    score += 25
                if t in code_lower:
                    score += 35

            if score > best_score:
                best_score = score
                best_loc = loc

        if best_loc and best_score > 0:
            return self._attach_nearest_hubs(best_loc)

        if detected_city:
            for loc in self.locations:
                if loc["city"].lower() == detected_city.lower() and loc["category"] == "city":
                    return self._attach_nearest_hubs(loc)

        # Fallback: Assume Delhi if completely unrecognized
        fallback = self.locations[0]
        return self._attach_nearest_hubs(fallback)

    def _attach_nearest_hubs(self, loc: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates distance to nearest airport, rail station and bus terminal in same metro cluster."""
        city = loc["city"]
        lat = loc["lat"]
        lng = loc["lng"]

        airports = [
            l for l in self.locations if l["city"] == city and l["category"] == "airport"
        ]
        stations = [
            l for l in self.locations if l["city"] == city and l["category"] == "rail_station"
        ]
        bus_terms = [
            l for l in self.locations if l["city"] == city and l["category"] == "bus_terminal"
        ]

        def find_closest(items):
            if not items:
                return None
            closest = min(
                items,
                key=lambda x: haversine_distance_km(lat, lng, x["lat"], x["lng"]),
            )
            dist = haversine_distance_km(lat, lng, closest["lat"], closest["lng"])
            return {
                "id": closest["id"],
                "name": closest["name"],
                "code": closest.get("code"),
                "lat": closest["lat"],
                "lng": closest["lng"],
                "distance_km": dist,
            }

        res = dict(loc)
        res["nearest_airport"] = find_closest(airports)
        res["nearest_rail_station"] = find_closest(stations)
        res["nearest_bus_terminal"] = find_closest(bus_terms)
        return res

    def get_supported_corridors_with_coords(self) -> List[Dict[str, Any]]:
        """Returns popular intercity corridors with full geographic coordinates."""
        corridors = [
            {
                "id": "del-bom",
                "origin": "Delhi",
                "destination": "Mumbai",
                "title": "Delhi ➔ Mumbai Golden Corridor",
                "origin_coords": [28.6139, 77.2090],
                "dest_coords": [18.9878, 72.8364],
                "distance_km": 1137.1,
                "modes": ["Flight", "Rail", "Multimodal"],
                "fastest_time": "2h 10m (Air) / 15h 30m (Rail)",
                "lowest_fare": 2150,
                "popular_landmarks": ["Connaught Place", "Bandra Kurla Complex"],
            },
            {
                "id": "blr-del",
                "origin": "Bangalore",
                "destination": "Delhi",
                "title": "Bengaluru ➔ Delhi Tech-Capital Corridor",
                "origin_coords": [12.9716, 77.5946],
                "dest_coords": [28.6139, 77.2090],
                "distance_km": 1740.0,
                "modes": ["Flight", "Rail", "Multimodal"],
                "fastest_time": "2h 45m (Air) / 33h 00m (Rail)",
                "lowest_fare": 3400,
                "popular_landmarks": ["Whitefield", "Cyber City Gurugram"],
            },
            {
                "id": "del-ccu",
                "origin": "Delhi",
                "destination": "Kolkata",
                "title": "Delhi ➔ Kolkata Heritage Grand Trunk",
                "origin_coords": [28.6139, 77.2090],
                "dest_coords": [22.5726, 88.3639],
                "distance_km": 1305.0,
                "modes": ["Flight", "Rail", "Multimodal"],
                "fastest_time": "2h 15m (Air) / 17h 05m (Rajdhani)",
                "lowest_fare": 1850,
                "popular_landmarks": ["India Gate", "Park Street"],
            },
            {
                "id": "blr-maa",
                "origin": "Bangalore",
                "destination": "Chennai",
                "title": "Bengaluru ➔ Chennai Express Corridors",
                "origin_coords": [12.9716, 77.5946],
                "dest_coords": [13.0827, 80.2707],
                "distance_km": 350.0,
                "modes": ["Rail", "Bus", "Flight", "Multimodal"],
                "fastest_time": "4h 15m (Vande Bharat) / 5h 30m (Express Bus)",
                "lowest_fare": 480,
                "popular_landmarks": ["MG Road", "T. Nagar"],
            },
            {
                "id": "bom-blr",
                "origin": "Mumbai",
                "destination": "Bangalore",
                "title": "Mumbai ➔ Bengaluru Commercial Highway",
                "origin_coords": [18.9878, 72.8364],
                "dest_coords": [12.9716, 77.5946],
                "distance_km": 845.0,
                "modes": ["Flight", "Rail", "Multimodal"],
                "fastest_time": "1h 45m (Air) / 21h 15m (Udyan Express)",
                "lowest_fare": 1420,
                "popular_landmarks": ["BKC", "Electronic City"],
            },
            {
                "id": "hyd-blr",
                "origin": "Hyderabad",
                "destination": "Bangalore",
                "title": "Hyderabad ➔ Bengaluru Deccan Link",
                "origin_coords": [17.3850, 78.4867],
                "dest_coords": [12.9716, 77.5946],
                "distance_km": 570.0,
                "modes": ["Rail", "Flight", "Bus", "Multimodal"],
                "fastest_time": "1h 15m (Air) / 8h 30m (Vande Bharat)",
                "lowest_fare": 750,
                "popular_landmarks": ["HITEC City", "Indiranagar"],
            },
        ]
        return corridors


location_service = LocationService()
