# YĀTRĀ AI — Comprehensive Data Dictionary (Phase 2 Canonical Schemas)

This document establishes the provider-independent canonical data dictionary for Project **YĀTRĀ AI**. All processed entities reside in `data/processed/` in dual formats (`.parquet` for high-efficiency ML pipelines and `.csv` for transparent auditing).

---

## 1. Station Master Directory (`canonical_stations`)
* **File Path**: `data/processed/canonical_stations.parquet` / `.csv`
* **Source**: `data/raw/railways/stations.json`
* **Record Count**: 8,990 rows (8,697 with valid GPS coordinates in India; 293 test/dummy records identified and flagged)
* **Primary Key**: `station_code`

| Field Name | Type | Meaning | Source | Range / Allowed Values | Transformation Applied | Yātrā AI Usage |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `station_code` | `string` | Unique IRCTC/CRIS station code | Raw `code` | 2–7 uppercase alphabetic/alphanumeric chars (e.g., `NDLS`, `HWH`) | Stripped whitespace, converted to uppercase | Primary identifier for network graph nodes |
| `station_name` | `string` | Official name of railway station | Raw `name` | Text string (e.g., `New Delhi`, `Howrah Jn`) | Stripped trailing spaces and punctuation | Display name, reverse lookup, user UI search |
| `state` | `string` | Indian State or Union Territory | Raw `state` | 29 states/UTs or `UNKNOWN` | Standardized empty/null values to `UNKNOWN` | Regional routing filters, IMD rainfall joining |
| `railway_zone` | `string` | Indian Railways administrative zonal code | Raw `zone` | 17 zones (`NR`, `WR`, `CR`, `SR`, etc.) or `UNKNOWN` | Standardized empty and `?` values to `UNKNOWN` | Operational domain feature, zonal congestion modeling |
| `address` | `string` | Locality and district address | Raw `address` | Free text string | Stripped excess whitespace | Spatial proximity queries, landmark verification |
| `latitude` | `float64` | Geographic latitude in WGS84 decimal degrees | Raw `coordinates.latitude` | 6.000000 to 38.000000 (valid India) or `NaN` | Flattened from JSON object, rounded to 6 decimal places | Spatial graph embedding, Haversine distance, geospatial nearest neighbors |
| `longitude` | `float64` | Geographic longitude in WGS84 decimal degrees | Raw `coordinates.longitude` | 68.000000 to 98.000000 (valid India) or `NaN` | Flattened from JSON object, rounded to 6 decimal places | Spatial graph embedding, Haversine distance, geospatial nearest neighbors |
| `is_valid_coordinate` | `boolean` | Flag indicating valid coordinate in India | Derived | `True` (8,697), `False` (293) | Evaluated against bounding box: $6^\circ \le \text{lat} \le 38^\circ$ and $68^\circ \le \text{lon} \le 98^\circ$ | Eliminates dummy nodes `(0.0, 0.0)` from geometric routing algorithms |
| `is_test_dummy_record` | `boolean` | Flag for internal test entries | Derived | `True` (e.g., `XX-BECE`, `YY-BPLC`), `False` | Filtered by prefix `XX-`, `YY-` | Prevents corrupted nodes from entering routing graph |
| `metro_cluster` | `string` | Associated metropolitan transport hub | Derived | `Delhi`, `Mumbai`, `Bangalore`, `Kolkata`, `Hyderabad`, `Chennai`, `OTHER` | Regex keyword mapping across code, name, and address | Inter-modal joining key linking rail terminals to metro airports |

---

## 2. Train Services Master (`canonical_train_services`)
* **File Path**: `data/processed/canonical_train_services.parquet` / `.csv`
* **Source**: `data/raw/railways/trains.json`
* **Record Count**: 5,208 train services
* **Primary Key**: `train_number`

| Field Name | Type | Meaning | Source | Range / Allowed Values | Transformation Applied | Yātrā AI Usage |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `train_number` | `string` | Unique 5-digit train number | Raw `trainNumber` | 5 numeric digits (e.g., `12951`, `02501`) | Zero-padded to 5 digits | Primary key for rail transit services |
| `train_name` | `string` | Commercial train branding | Raw `trainName` | Text string (e.g., `MUMBAI TEJAS RAJDHANI`) | Stripped whitespace | User presentation, service classification |
| `train_type` | `string` | Operational service category | Raw `type` | `Raj`, `SF`, `Exp`, `Drnt`, `Mail`, `Pass`, `MEMU`, etc. | Standardized category codes | Speed and priority feature in travel time estimation |
| `source_code` | `string` | Station code of originating terminal | Raw `source.code` | Station code matching `canonical_stations` | Uppercase standardization | Origin node in timetable routing |
| `dest_code` | `string` | Station code of final terminal | Raw `destination.code` | Station code matching `canonical_stations` | Uppercase standardization | Destination node in timetable routing |
| `running_days` | `string` | Active operational days of the week | Raw `runningDays` | Comma-separated days (e.g., `MON,TUE,WED`) | Serialized boolean dictionary to compact string | Schedule temporal constraint engine |
| `total_route_distance_km`| `float64` | Total railway track length in km | Raw `overallDistanceKm` | 10.0 to 4,273.0 km | Preserved numeric track distance | Global route length metric, baseline fare proxy |
| `total_halts` | `int64` | Count of scheduled intermediate stops | Raw `completeOrderedRoute` | 2 to 175 stops | Length of ordered route array | Congestion and transit delay compounding feature |

---

## 3. Train Route Stops & Timetable (`canonical_train_routes`)
* **File Path**: `data/processed/canonical_train_routes.parquet` / `.csv`
* **Source**: `data/raw/railways/trains.json` joined with `canonical_stations`
* **Record Count**: 416,637 scheduled halt records
* **Composite Key**: `(train_number, sequence)`

| Field Name | Type | Meaning | Source | Range / Allowed Values | Transformation Applied | Yātrā AI Usage |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `train_number` | `string` | Service identifier | Raw `trainNumber` | 5 digits | Zero-padded string | Foreign key referencing `canonical_train_services` |
| `sequence` | `int64` | Stop ordinal along the route | Raw `sequence` | 1 to 175 | 1-based sequential integer | Ordering key for Connection Scan / RAPTOR algorithms |
| `station_code` | `string` | Halt station identifier | Raw `stationCode` | Matching `canonical_stations` | Uppercase standardization | Graph node identifier |
| `station_name` | `string` | Halt station name | Raw `stationName` | Text string | Stripped whitespace | User presentation |
| `arrival_time` | `string` | Scheduled time of arrival | Raw `arrivalTime` | `HH:MM:SS` or `null` (at origin) | Preserved string | Raw timetable reference |
| `departure_time` | `string` | Scheduled time of departure | Raw `departureTime` | `HH:MM:SS` or `null` (at destination) | Preserved string | Raw timetable reference |
| `arrival_minutes_from_midnight` | `float64` | Arrival time converted to integer minutes | Derived from `arrival_time` | 0 to 1439 or `NaN` | Computed as $\text{hour} \times 60 + \text{min}$ | Mathematical timetable constraint modeling |
| `departure_minutes_from_midnight` | `float64` | Departure time converted to integer minutes | Derived from `departure_time` | 0 to 1439 or `NaN` | Computed as $\text{hour} \times 60 + \text{min}$ | Mathematical timetable constraint modeling |
| `halt_duration_minutes` | `float64` | Duration of train halt at platform | Derived | 0.0 to 120.0 minutes or `NaN` | Calculated as $(\text{dep} - \text{arr})$ with midnight modulo | Platform dwell time, transfer feasibility window |
| `journey_day` | `int64` | Multi-day travel offset | Raw `journeyDay` | 1 to 5 days | Preserved integer | Multi-day journey duration tracking |
| `segment_haversine_km` | `float64` | Great-circle distance from previous halt | Derived | 0.0 to 450.0 km | Computed using WGS84 Haversine formula | Inter-station hop physical distance |
| `cumulative_haversine_km` | `float64` | Cumulative great-circle distance along route | Derived | 0.0 to 3,850.0 km | Running sum of `segment_haversine_km` | Physical distance traversed from origin |
| `is_origin` | `boolean` | Flag indicating first station | Derived | `True`, `False` | `sequence == 1` | Path initialization flag |
| `is_destination` | `boolean` | Flag indicating final station | Derived | `True`, `False` | `sequence == max(sequence)` | Path termination flag |

---

## 4. Train Delays & Reliability Metrics (`canonical_train_delays`)
* **File Path**: `data/processed/canonical_train_delays.parquet` / `.csv`
* **Source**: `data/raw/delays/train_routes/*.csv` + `Train_List.csv`
* **Record Count**: 1,479 station halt delay observations across 42 trains
* **Composite Key**: `(train_number, station_code_raw)`

| Field Name | Type | Meaning | Source | Range / Allowed Values | Transformation Applied | Yātrā AI Usage |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `train_number` | `string` | Train service identifier | CSV Filename | 5 digits (e.g., `20503`, `12423`) | Extracted and zero-padded | Link to train schedule service |
| `station_code_raw` | `string` | Station code as logged in NTES | Raw `Station` | Uppercase station code | Stripped whitespace | Raw checkpoint record |
| `canonical_station_code` | `string` | Reconciled modern station code | Derived | Station code matching `canonical_stations` | Alias mapping: `PRYJ`$\rightarrow$`ALD`, `DDU`$\rightarrow$`MGS`, etc. | Robust joining key with station graph |
| `station_name` | `string` | Station name | Raw `Station_Name` | Text string | Stripped whitespace | Human-readable validation |
| `mean_delay_minutes` | `float64` | Historical mean arrival delay | Raw `Average_Delay(min)` | 1.0 to 570.0 minutes | Preserved numeric | **Candidate Continuous ML Target / Ground Truth** |
| `pct_right_time_0_15m` | `float64` | % arrivals within 15 min | Raw `Right Time (0-15 min's)` | 0.0% to 100.0% | Preserved percentage | Punctuality probability calculation |
| `pct_slight_delay_15_60m` | `float64` | % arrivals delayed 15–60 min | Raw `Slight Delay (15-60 min's)` | 0.0% to 100.0% | Preserved percentage | Moderate delay probability calculation |
| `pct_severe_delay_over_60m` | `float64` | % arrivals delayed >60 min | Raw `Significant Delay (>1 Hour)`| 0.0% to 100.0% | Preserved percentage | Severe disruption probability calculation |
| `pct_cancelled_unknown` | `float64` | % trips cancelled or untracked | Raw `Cancelled/Unknown` | 0.0% to 100.0% | Preserved percentage | Disruption / cancellation risk rate |
| `p_on_time` | `float64` | Empirical probability of on-time arrival | Derived | 0.0000 to 1.0000 | `pct_right_time_0_15m / 100.0` | Probability-weighted journey planning |
| `p_slight_delay` | `float64` | Empirical probability of slight delay | Derived | 0.0000 to 1.0000 | `pct_slight_delay_15_60m / 100.0` | Risk weighting in routing cost function |
| `p_severe_delay` | `float64` | Empirical probability of severe delay | Derived | 0.0000 to 1.0000 | `pct_severe_delay_over_60m / 100.0` | Transfer buffer margin sizing |
| `p_cancelled` | `float64` | Empirical probability of cancellation | Derived | 0.0000 to 1.0000 | `pct_cancelled_unknown / 100.0` | Route vulnerability penalty |
| `delay_risk_category` | `string` | Categorical delay classification | Derived | `ON_TIME_RELIABLE`, `MODERATE_DELAY`, `SEVERE_DELAY`, `CANCEL_DISRUPTED` | Multi-threshold operational logic | **Candidate Multiclass ML Target** |
| `is_high_transfer_risk` | `int64` | Binary flag for high connection failure risk | Derived | `0` (Low Risk, 22.4%), `1` (High Risk, 77.6%) | `mean_delay > 45` or `p_severe > 0.25` or `p_cancel > 0.10` | **Candidate Binary ML Target** |

---

## 5. Domestic Flights Directory (`canonical_flights`)
* **File Path**: `data/processed/canonical_flights.parquet` / `.csv`
* **Source**: `data/raw/flights/Clean_flight_data_Vivek.csv`
* **Record Count**: 300,259 rows (2 exact duplicates dropped from original 300,261)
* **Primary Key**: Synthetic composite or row index

| Field Name | Type | Meaning | Source | Range / Allowed Values | Transformation Applied | Yātrā AI Usage |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `airline` | `string` | Operating commercial airline | Raw `airline` | `Vistara`, `Air India`, `Indigo`, `GO FIRST`, `AirAsia`, `SpiceJet`, `StarAir`, `Trujet` | Preserved clean text | Carrier filtering, brand preference matching |
| `flight_number` | `string` | Airline flight identifier | Raw `flight` | Text code (e.g., `SG-8709`, `UK-995`) | Standardized string | Leg identifier in flight offers |
| `source_city` | `string` | Departure metropolitan airport city | Raw `source_city` | `Delhi`, `Mumbai`, `Bangalore`, `Kolkata`, `Hyderabad`, `Chennai` | Standardized text | Corridor origin matching |
| `destination_city` | `string` | Arrival metropolitan airport city | Raw `destination_city` | `Delhi`, `Mumbai`, `Bangalore`, `Kolkata`, `Hyderabad`, `Chennai` | Standardized text | Corridor destination matching |
| `corridor` | `string` | Directed city pair | Derived | 30 directional pairs (e.g., `Delhi-Mumbai`) | `source_city + '-' + destination_city` | Multi-modal corridor benchmark join |
| `departure_time_window` | `string` | Time period of flight departure | Raw `departure_time` | `Early Morning`, `Morning`, `Afternoon`, `Evening`, `Night`, `Late Night` | Preserved categorical | Schedule convenience matching |
| `arrival_time_window` | `string` | Time period of flight arrival | Raw `arrival_time` | `Early Morning`, `Morning`, `Afternoon`, `Evening`, `Night`, `Late Night` | Preserved categorical | Arrival window alignment |
| `stops` | `int64` | Number of intermediate layovers | Raw `stops` | `0` (Non-stop: 36,044), `1` (1-stop: 250,927), `2` (2+-stops: 13,288) | Preserved integer | Transfer penalty feature, flight complexity |
| `cabin_class` | `string` | Ticket service class | Raw `class` | `Economy` (206,772), `Business` (93,487) | Preserved categorical | Budget vs. business traveler segmentation |
| `duration_hours` | `float64` | Total elapsed travel time | Raw `duration` | 0.83 to 103.0 hours | Preserved decimal hours | Intermodal travel time comparison |
| `days_left` | `int64` | Days remaining before departure | Raw `days_left` | 1 to 49 days | Preserved integer | Dynamic fare modeling, advance booking feature |
| `price_inr` | `int64` | Ticket fare in Indian Rupees (INR) | Raw `price` | ₹1,105 to ₹123,071 | Preserved integer fare | Fare baseline for air vs. rail choice modeling |
| `price_per_duration_hour`| `float64` | Fare intensity per hour of travel | Derived | ₹50.0 to ₹85,000.0 per hour | `price_inr / duration_hours` | Economic efficiency metric |
| `direct_flight_distance_km`| `float64` | Great-circle distance between metro airports | Derived | 500.0 to 1,750.0 km | WGS84 Haversine between airport coords | Spatial efficiency and carbon emission proxy |

---

## 6. Subdivisional Rainfall & Climate (`canonical_subdivision_rainfall`)
* **File Path**: `data/processed/canonical_subdivision_rainfall.parquet` / `.csv`
* **Source**: `data/raw/environmental/rainfall_india_1901-2015.csv`
* **Record Count**: 4,116 rows (36 subdivisions across 115 years)
* **Composite Key**: `(subdivision, year)`

| Field Name | Type | Meaning | Source | Range / Allowed Values | Transformation Applied | Yātrā AI Usage |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `subdivision` | `string` | IMD meteorological subdivision name | Raw `SUBDIVISION` | 36 distinct subdivision names | Standardized text | Geographic join key to station states |
| `year` | `int64` | Calendar year of record | Raw `YEAR` | 1901 to 2015 | Preserved integer | Longitudinal climate baseline analysis |
| `JAN` .. `DEC` | `float64` | Monthly rainfall in millimeters | Raw `JAN` .. `DEC` | 0.0 to 2,500.0 mm | Subdivisional median imputation for minor nulls (<0.3%) | Seasonal month-by-month weather feature |
| `annual_rainfall_mm` | `float64` | Total annual rainfall in mm | Raw `ANNUAL` | 62.3 to 6,331.1 mm | Verified against sum of months | Baseline precipitation volume |
| `monsoon_jjas_rainfall_mm`| `float64` | Total monsoon rainfall (Jun–Sep) | Derived | 30.0 to 5,500.0 mm | $\text{JUN} + \text{JUL} + \text{AUG} + \text{SEP}$ | Monsoon stress volume |
| `monsoon_intensity_ratio` | `float64` | Fraction of annual rain occurring in monsoon | Derived | 0.1000 to 0.9800 | `monsoon_jjas_rainfall_mm / ANNUAL` | Seasonal vulnerability index for transit routes |
| `baseline_normal_annual_rainfall_mm` | `float64` | 30-year climatological normal (1986–2015) | Derived | 250.0 to 4,200.0 mm | Computed 30-year mean per subdivision | Long-term regional climatic expectation |
| `baseline_normal_monsoon_rainfall_mm` | `float64` | 30-year normal monsoon rainfall (1986–2015) | Derived | 180.0 to 3,600.0 mm | Computed 30-year mean per subdivision | Benchmark for monsoon risk scoring |
| `baseline_monsoon_intensity_ratio` | `float64` | 30-year normal monsoon fraction | Derived | 0.4000 to 0.9500 | Computed 30-year mean per subdivision | Regional climate classification feature |

---

## 7. Corridor Multimodal Benchmark (`canonical_corridor_multimodal`)
* **File Path**: `data/processed/canonical_corridor_multimodal.parquet` / `.csv`
* **Source**: Cross-modal aggregation of `canonical_flights`, `canonical_train_services`, and `canonical_stations`
* **Record Count**: 30 major intercity corridor pairs
* **Primary Key**: `corridor`

| Field Name | Type | Meaning | Source | Range / Allowed Values | Transformation Applied | Yātrā AI Usage |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `corridor` | `string` | Directed metro city pair | Derived | 30 pairs (e.g., `Delhi-Mumbai`, `Chennai-Kolkata`) | Standardized string | Multi-modal choice set index |
| `origin_city` | `string` | Departure metropolitan city | Derived | 6 metro cities | Standardized text | Geographic origin |
| `destination_city` | `string` | Arrival metropolitan city | Derived | 6 metro cities | Standardized text | Geographic destination |
| `has_direct_flight` | `boolean` | Flag for direct air connectivity | Derived from flights | `True` (30/30) | Existence check | Availability constraint |
| `flight_options_count` | `int64` | Number of distinct flight itineraries | Aggregated flights | 4,200 to 14,800 flights per corridor | Count aggregation | Aviation supply depth |
| `flight_nonstop_count` | `int64` | Number of non-stop flight options | Aggregated flights | 350 to 2,800 non-stop flights | Count aggregation | High-speed air travel options |
| `flight_min_duration_hours` | `float64` | Fastest flight duration | Aggregated flights | 0.83 to 3.25 hours | Minimum aggregation | Air speed benchmark |
| `flight_median_duration_hours` | `float64` | Median flight duration | Aggregated flights | 2.17 to 15.5 hours | Median aggregation | Typical air travel time |
| `flight_econ_min_fare_inr` | `float64` | Lowest economy flight fare | Aggregated flights | ₹1,400 to ₹3,500 | Minimum aggregation | Budget floor for flight |
| `flight_econ_median_fare_inr` | `float64` | Median economy flight fare | Aggregated flights | ₹4,500 to ₹9,200 | Median aggregation | Expected economy air cost |
| `has_direct_train` | `boolean` | Flag for direct train connectivity | Derived from rail | `True` (26/30), `False` (4/30) | Existence check | Rail availability constraint |
| `direct_train_services_count`| `int64` | Number of direct train services | Aggregated rail | 0 to 48 trains | Count aggregation | Rail supply depth |
| `train_types_available` | `string` | Types of train operating on corridor | Aggregated rail | `Raj,SF,Exp`, etc. | Concatenated distinct types | Rail service tier indicator |
| `train_min_distance_km` | `float64` | Shortest rail track distance | Aggregated rail | 350.0 to 2,650.0 km | Minimum aggregation | Rail track physical distance |
| `train_median_distance_km` | `float64` | Median rail track distance | Aggregated rail | 400.0 to 2,750.0 km | Median aggregation | Expected rail distance |
