# YĀTRĀ AI — Data Sources Catalog & Registry (Phase 1)

This document provides a comprehensive, verified technical registry of all real, public, and open government datasets evaluated and collected during **Phase 1** of Project **YĀTRĀ AI**.

All raw files are permanently preserved in their original format under `data/raw/` with cryptographic SHA-256 checksums. External schemas and adapters are maintained under `data/external/`.

---

## 1. Indian Railways Stations Master Directory

* **Dataset Name**: Indian Railways Network Stations Dataset
* **Source**: `prasenjit-27/Indian-Railway-Data` (Compiled from CRIS/IRCTC official public timetable & geographical reference)
* **URL**: [https://github.com/prasenjit-27/Indian-Railway-Data](https://github.com/prasenjit-27/Indian-Railway-Data)
* **License**: MIT License (Permissive open source)
* **Download / Access Method**: Direct HTTP download via raw GitHub asset pipeline
* **Local File Path**: `data/raw/railways/stations.json`
* **File Size**: 1,910,928 bytes (~1.91 MB)
* **SHA-256 Checksum**: `885247a7bb3c3f7c3e75d80bc63717bc0b538203854fe981602683e85549efcd`
* **Number of Records**: 8,990 station entities
* **Number of Columns / Keys**: 6 top-level attributes (`code`, `name`, `state`, `zone`, `address`, `coordinates`)
* **Important Columns / Features**:
  * `code` (`str`): Unique IRCTC / CRIS railway station identifier code (e.g., `"NDLS"`, `"HWH"`, `"MAS"`, `"SBC"`).
  * `name` (`str`): Station name in title casing.
  * `state` (`str`): Indian State or Union Territory jurisdiction.
  * `zone` (`str`): Indian Railways administrative zonal code (17 zones, e.g., `NR`, `CR`, `WR`, `SR`, `ER`, `ECR`, `NWR`).
  * `address` (`str`): City / district / locality description.
  * `coordinates.latitude` (`float`): Geographic latitude in WGS84 decimal degrees.
  * `coordinates.longitude` (`float`): Geographic longitude in WGS84 decimal degrees.
* **Data Format**: JSON (Clean array of objects)
* **Date / Time Coverage**: Static baseline snapshot (aligned with current network topology)
* **Geographic Coverage**: Pan-India (All 28 States and 8 Union Territories)
* **Potential Yātrā Use**:
  * Forms the geospatial coordinate backbone of Yātrā's routing graph.
  * Serves as station lookup master for distance calculation, geographic nearest-neighbor search, and multimodal transfer hub identification.
* **Data Quality Concerns**:
  * Minor spelling variations in colonial vs. re-named stations (e.g., VT vs. CSMT, Madras vs. Chennai Central).
  * Minimal coordinate imprecision for minor rural halt stations (<0.5% of records).
* **Limitations**: Does not contain platform counts or passenger capacity data.
* **Classification**: **KEEP**

---

## 2. Indian Railways Trains Master Directory & Multi-Stop Timetable

* **Dataset Name**: Indian Railways Trains Schedule & Route Master
* **Source**: `prasenjit-27/Indian-Railway-Data` (Compiled from CRIS/IRCTC official timetables)
* **URL**: [https://github.com/prasenjit-27/Indian-Railway-Data](https://github.com/prasenjit-27/Indian-Railway-Data)
* **License**: MIT License (Permissive open source)
* **Download / Access Method**: Direct HTTP download via raw GitHub asset pipeline
* **Local File Path**: `data/raw/railways/trains.json`
* **File Size**: 96,667,263 bytes (~96.67 MB)
* **SHA-256 Checksum**: `0b68c11a490f31f4d6fbde1ec7a8d05124f763794f8d670242f339d8cc3fc008`
* **Number of Records**: 5,208 train services; **416,637 total intermediate halt records**
* **Number of Columns / Keys**: 8 service-level fields; 7 route-stop level fields
* **Important Columns / Features**:
  * `trainNumber` (`str`): 5-digit Indian Railways train identifier (e.g., `"12951"`).
  * `trainName` (`str`): Official train branding (e.g., `"MUMBAI TEJAS RAJDHANI"`).
  * `type` (`str`): Classification category (`Raj`, `SHT`, `DRNT`, `SF`, `Exp`, `Pass`).
  * `source` / `destination` (`dict`): Origin and terminal stations (`code`, `name`).
  * `runningDays` (`dict[str, bool]`): Weekly operating schedule across all 7 days.
  * `overallDistanceKm` (`int/float`): Total route distance in kilometers.
  * `completeOrderedRoute[]`:
    * `sequence` (`int`): Halt order (1..N).
    * `stationCode` (`str`): Cross-referenced with `stations.json`.
    * `stationName` (`str`): Name of halt station.
    * `arrivalTime` (`str/null`): Scheduled arrival time (`"HH:MM:SS"`, `null` at source).
    * `departureTime` (`str/null`): Scheduled departure time (`"HH:MM:SS"`, `null` at terminal).
    * `journeyDay` (`int`): Multi-day travel offset index.
    * `distance` (`float`): Cumulative distance from origin in kilometers.
* **Data Format**: JSON (Structured nested document collection)
* **Date / Time Coverage**: Static operational timetable
* **Geographic Coverage**: National Indian Railways passenger network
* **Potential Yātrā Use**:
  * Essential core for Yātrā's intercity path-finding engine and timetable graph (Dijkstra / CSA / RAPTOR algorithms).
  * Enables intermodal train-to-flight and train-to-bus transfer discovery.
* **Data Quality Concerns**: Special holiday express trains and temporary train cancellations not reflected dynamically in static JSON.
* **Limitations**: Does not contain live GPS coordinates or dynamic seat availability (reserved for Phase 3/4 live API integration).
* **Classification**: **KEEP**

---

## 3. Indian Railway Express Trains Delay & Reliability Dataset

* **Dataset Name**: Indian Railway Express Trains Delay Datasets (Guwahati–Metro Corridors 2023–2024)
* **Source**: `ankitaanand28/DA323_IndianRailwayTrainDelayDatasets` (Derived from NTES - National Train Enquiry System)
* **URL**: [https://github.com/ankitaanand28/DA323_IndianRailwayTrainDelayDatasets](https://github.com/ankitaanand28/DA323_IndianRailwayTrainDelayDatasets)
* **License**: Open Research / Public Educational Dataset (DA323 academic project, derived from NTES public data)
* **Download / Access Method**: Multi-file automated HTTPS fetch
* **Local File Path**: `data/raw/delays/Train_List.csv` and `data/raw/delays/train_routes/*.csv` (42 route files)
* **File Size**: Manifest: 1,819 bytes; 42 route CSVs: ~75 KB total
* **SHA-256 Checksum (Manifest)**: `1186745f901a950239700b264b5774270cce32e0667654378b84673503fcc5ec`
* **Number of Records**: 42 major express trains; 1,479 station halt delay observations
* **Number of Columns / Features**:
  * Manifest (`Train_List.csv`): 5 columns (`Train_Number`, `Train_Name`, `From_Station`, `To_Station`, `Type`).
  * Route Delay CSVs: 7 columns:
    * `Station` (`str`): Checkpoint station code.
    * `Station_Name` (`str`): Name of the station.
    * `Average_Delay(min)` (`int`): Empirical mean arrival delay in minutes.
    * `Right Time (0-15 min's)` (`float`): Percentage of journeys arriving within 15 minutes of schedule.
    * `Slight Delay (15-60 min's)` (`float`): Percentage of journeys experiencing 15 to 60 minutes delay.
    * `Significant Delay (>1 Hour)` (`float`): Percentage of journeys delayed beyond 60 minutes.
    * `Cancelled/Unknown` (`float`): Disruption or cancellation rate.
* **Data Format**: CSV (42 individual train route files indexed by train number)
* **Date / Time Coverage**: March 2023 to March 2024 (12 continuous months of historical train performance)
* **Geographic Coverage**: High-density trunk corridors connecting Northeast India (Guwahati) to National Capital Region (New Delhi), Western Hub (Mumbai), Southern Hub (Chennai), and Eastern Hub (Kolkata).
* **Potential Yātrā Use**:
  * Directly trains Yātrā's **Reliability & Delay Prediction ML Engine**.
  * Enables probability-weighted journey planning (recommending robust transfer buffers rather than unrealistically tight connections).
* **Data Quality Concerns**: Focused on long-distance express corridors; feeder branch lines require statistical imputation.
* **Limitations**: Sampled over 42 high-impact train services rather than the entire national catalog.
* **Classification**: **KEEP**

---

## 4. Indian Domestic Flights Pricing & Itinerary Dataset

* **Dataset Name**: Indian Domestic Flights Pricing & Schedule Dataset (EaseMyTrip Metro Network)
* **Source**: EaseMyTrip Domestic Flights Collection via `vivek236/Flight-Price-Prediction` / Kaggle
* **URL**: [https://github.com/vivek236/Flight-Price-Prediction](https://github.com/vivek236/Flight-Price-Prediction)
* **License**: Public Domain / CC0 / Open Academic Research
* **Download / Access Method**: Direct HTTP download via raw GitHub asset pipeline
* **Local File Path**: `data/raw/flights/Clean_flight_data_Vivek.csv`
* **File Size**: 22,211,377 bytes (~22.21 MB)
* **SHA-256 Checksum**: `8752438485eb2752169cba3c4ce3f5128e3a363372a6794cf98e7bdbcccbab28`
* **Number of Records**: 300,261 flight itinerary observations
* **Number of Columns**: 11 features
* **Important Columns / Features**:
  * `airline` (`str`): Carrier name (Indigo, Air India, Vistara, SpiceJet, GO FIRST, AirAsia, StarAir, Trujet).
  * `flight` (`str`): Operating flight identifier (e.g., `"SG-8709"`, `"UK-995"`, `"6E-5001"`).
  * `source_city` (`str`): Origin city (Delhi, Mumbai, Bangalore, Kolkata, Hyderabad, Chennai).
  * `departure_time` (`str`): Time window (`Early Morning`, `Morning`, `Afternoon`, `Evening`, `Night`).
  * `stops` (`int`): Non-stop (`0`), single stop (`1`), or multi-stop (`2+`).
  * `arrival_time` (`str`): Time window of landing.
  * `destination_city` (`str`): Destination city.
  * `class` (`str`): Cabin class (`Economy`, `Business`).
  * `duration` (`float`): Flight duration in decimal hours (e.g., `2.17`).
  * `days_left` (`int`): Advance booking window in days (1 to 49 days).
  * `price` (`float`): Actual booking ticket price in Indian Rupees (INR) (range: ₹1,105 to ₹123,071).
* **Data Format**: CSV (Clean, tabular, zero null values)
* **Date / Time Coverage**: 50 consecutive booking days covering domestic flights
* **Geographic Coverage**: India's top 6 metropolitan hubs (Delhi, Mumbai, Bangalore, Kolkata, Hyderabad, Chennai)
* **Potential Yātrā Use**:
  * Core multi-modal comparative engine: evaluates **Time vs. Cost vs. Carbon** trade-offs between High-Speed Rail (Vande Bharat / Rajdhani) and Domestic Aviation.
  * Powers dynamic flight fare forecasting and advance booking recommendations.
* **Data Quality Concerns**: Does not cover Tier-2/Tier-3 regional airports (e.g., Patna, Indore, Coimbatore).
* **Limitations**: Categorical departure/arrival time windows rather than exact minute timestamps.
* **Classification**: **KEEP**

---

## 5. IMD Historical Subdivisional Monthly & Annual Rainfall Dataset

* **Dataset Name**: India Meteorological Department (IMD) Subdivisional Monthly & Annual Rainfall (1901–2015)
* **Source**: India Meteorological Department (IMD) / Open Government Data Platform India (`data.gov.in`) via `praghnanaidu/assignment_rainfall`
* **URL**: [https://data.gov.in](https://data.gov.in) / [GitHub praghnanaidu/assignment_rainfall](https://github.com/praghnanaidu/assignment_rainfall)
* **License**: Government Open Data License - India (GODL)
* **Download / Access Method**: Direct HTTPS download
* **Local File Path**: `data/raw/environmental/rainfall_india_1901-2015.csv`
* **File Size**: 347,705 bytes (~348 KB)
* **SHA-256 Checksum**: `14ebe75d1cdc2aedaa02dd175afc34d396fce781849558a8ae55979c5e11c485`
* **Number of Records**: 4,116 annual subdivision climatology rows
* **Number of Columns**: 15 features
* **Important Columns / Features**:
  * `SUBDIVISION` (`str`): Meteorological subdivision name (36 subdivisions spanning the Indian subcontinent).
  * `YEAR` (`int`): Year of observation (1901 to 2015, 115 consecutive years).
  * `JAN` through `DEC` (`float`): Monthly cumulative precipitation in millimeters (mm).
  * `ANNUAL` (`float`): Total annual rainfall in mm.
* **Data Format**: CSV (Clean tabular records)
* **Date / Time Coverage**: 1901 to 2015 (115-year long-term baseline)
* **Geographic Coverage**: Entire Indian territory across 36 IMD subdivisions (from Jammu & Kashmir to Andaman & Nicobar)
* **Potential Yātrā Use**:
  * **Environmental Risk Conditioning**: Generates regional monsoon intensity and extreme weather disruption indices for transit route planning.
  * Allows Yātrā to dynamically penalize vulnerable rail and road corridors (e.g., Konkan Railway landslides, Assam flood zones) during high-monsoon months (JJAS).
* **Data Quality Concerns**: 26 missing values across 115 years in `ANNUAL` column (easily handled with subdivisional median imputation).
* **Limitations**: Subdivisional monthly aggregation rather than daily station-level readings.
* **Classification**: **KEEP**

---

## 6. Summary Evaluation of Other Investigated Candidates

| Candidate Dataset | Source | Evaluation | Reason for Decision |
| :--- | :--- | :--- | :--- |
| **DataMeet Railways GeoJSON** | `datameet/railways` | **MAYBE / SUPPORTING** | High quality open data, but older schema snapshot. Subsumed by `prasenjit-27/Indian-Railway-Data` which provides cleaner synchronized schedules and 8,990 stations. Retained as external reference. |
| **India Automatic Weather Stations Scraper** | `fcecinati/india_automatic_weather_stations_hourly_data` | **REJECT** | Repository only contains an unmaintained scraper script; no static data files archived. Violates reproducibility standard. |
| **Live Train Checking 2.0** | `oddboss23-dotcom/live-train-checking-2.0` | **REJECT** | Real-time reverse-engineered scraper without historical records; API key dependent and unreliable for foundational ML modeling. |
| **Unfazed-07 Indian Cities Weather** | `unfazed-07/indian-cities-weather-dataset` | **REJECT** | Incomplete repository with broken file links (HTTP 404). |
| **Random Large Travel Sentiment Scrapes** | Various Twitter / Reddit dumps | **REJECT** | High noise, lack of spatial ground truth, violates objective C ("Do not collect random datasets just because they are large"). |
