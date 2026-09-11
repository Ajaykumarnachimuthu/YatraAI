# YĀTRĀ AI — Phase 1 Research & Data Collection Report

## Executive Summary

Phase 1 of **Project Yātrā AI** established the real, public, and open government data foundation for our machine-learning-driven multi-modal travel recommendation and journey orchestration application for India.

In strict adherence to the project guidelines:
1. **Zero synthetic records** were generated.
2. **Zero ML models** were trained prematurely.
3. **Existing architecture was untouched**; raw datasets were downloaded unaltered into `data/raw/`.
4. Supporting canonical schemas and metadata were established in `data/external/` to guarantee **provider independence** (future-proofing against reliance on Kaggle, specific GitHub scrapers, or third-party proprietary APIs).

---

## 1. Candidates Investigated

During Phase 1, we executed targeted discovery across official Indian government open data platforms (data.gov.in, IMD, CRIS, NTES), open-source community repositories (DataMeet, GitHub Open Data), and vetted academic research archives:

1. **`prasenjit-27/Indian-Railway-Data`**: Open dataset containing 8,990 Indian Railway stations with geographic coordinates and 5,208 train services with complete halt schedules and inter-station distances under MIT License.
2. **`ankitaanand28/DA323_IndianRailwayTrainDelayDatasets`**: Academic research dataset logging station-by-station arrival delay distributions and cancellation rates for 42 major express trains along major metro corridors across 12 months (March 2023 – March 2024).
3. **`vivek236/Flight-Price-Prediction` (EaseMyTrip Corpus)**: Comprehensive domestic airline dataset covering 300,261 flight itineraries across India's top 6 metro hubs with pricing, booking windows, departure slots, and flight durations.
4. **`praghnanaidu/assignment_rainfall` (IMD / data.gov.in GODL)**: Official 115-year historical monthly and annual rainfall dataset from the India Meteorological Department across 36 meteorological subdivisions.
5. **`datameet/railways`**: Community-curated GeoJSON stations and railway routes.
6. **`fcecinati/india_automatic_weather_stations_hourly_data`**: Automatic weather station scraper.
7. **`oddboss23-dotcom/live-train-checking-2.0`**: Real-time train tracking scraper script.
8. **`unfazed-07/indian-cities-weather-dataset`**: Proposed Indian cities weather dataset.

---

## 2. Datasets Selected (KEEP)

Four high-value foundational datasets (spanning 5 discrete raw files/collections) were selected and downloaded directly into `data/raw/`:

| Dataset | Modality / Domain | Records | Size | Provenance & License |
| :--- | :--- | :--- | :--- | :--- |
| **Stations Directory** | Geographic / Station Coordinates | 8,990 stations | 1.91 MB | CRIS / IRCTC Timetables (MIT License) |
| **Trains Schedule & Route Master** | Rail Schedules & Mileage Network | 5,208 trains (416,637 halts) | 96.67 MB | Indian Railways Master Timetable (MIT License) |
| **Express Train Delay & Reliability** | Historical Delays & Punctuality | 42 trains (1,479 station halts) | ~77 KB | NTES Operational Logs (Open Academic) |
| **Domestic Flights Pricing & Itinerary** | Aviation / Multimodal Costs & Timing | 300,261 flight itineraries | 22.21 MB | EaseMyTrip Domestic Aggregation (CC0/Open) |
| **IMD Subdivisional Monsoon Rainfall** | Climate & Environmental Risk | 4,116 records (115 years) | 348 KB | India Meteorological Dept / data.gov.in (GODL) |

**Total Raw Data Collected**: ~121.2 MB across 5 distinct domains, providing complete nationwide coverage across rail, air, geography, and environmental weather.

---

## 3. Datasets Rejected and Why

| Dataset Candidate | Source | Decision | Technical Rationale for Rejection |
| :--- | :--- | :--- | :--- |
| **DataMeet Railways GeoJSON** | `datameet/railways` | **MAYBE / DEFERRED** | Older schema snapshot without unified halt sequence indexing. The selected `prasenjit-27` dataset directly extends and modernizes this with synchronized station codes and distances. Kept as external reference. |
| **India Weather Station Scraper** | `fcecinati` | **REJECT** | Repository contains only a scraping script with no static data archive. Violates offline reproducibility and data integrity criteria. |
| **Live Train Checking 2.0** | `oddboss23` | **REJECT** | Thin scraper wrapper dependent on reverse-engineered live APIs. Prone to breakage and lacks historical statistical depth needed for ML training. |
| **Unfazed-07 Weather Dataset** | `unfazed-07` | **REJECT** | Repository is broken/abandoned with HTTP 404 on data files. |
| **Social Media / Forum Travel Dumps** | Public Web Dumps | **REJECT** | Unstructured, high-noise sentiment scrapes lacking spatial and temporal ground truth. Violates directive C ("Do not collect random datasets just because they are large"). |

---

## 4. Mapping Datasets to Future YĀTRĀ AI Components

Each selected dataset maps directly to a core architectural component of the Yātrā AI application:

```
+-------------------------------------------------------------------------+
|                              YĀTRĀ AI                                   |
|               Multi-Modal Recommendation & Orchestration               |
+-------------------------------------------------------------------------+
       |                         |                       |
       v                         v                       v
[1. Topology & Router]   [2. Delay Predictor]   [3. Mode Optimizer]
  - stations.json          - train_routes/*.csv   - Clean_flight_data_Vivek.csv
  - trains.json            - Train_List.csv       - rainfall_india_1901-2015.csv
       |                         |                       |
       +-------------------------+-----------------------+
                                 |
                                 v
               +-----------------------------------+
               | Unified Canonical Yātrā Schemas   |
               | (Provider-Agnostic Adapter Tier)  |
               +-----------------------------------+
```

### Component A: Transit Graph Topology & Path-Finding Router
* **Input Data**: `data/raw/railways/stations.json` (8,990 nodes) + `data/raw/railways/trains.json` (416,637 directed edges).
* **Future Yātrā Role**: Constructs the national multi-modal spatial graph. Nodes represent physical stations with WGS84 GPS coordinates; edges represent scheduled train hops with departure/arrival constraints and cumulative track distances.
* **Algorithms**: Timetable-constrained Dijkstra, Connection Scan Algorithm (CSA), and RAPTOR.

### Component B: Journey Reliability & Delay Prediction ML Engine
* **Input Data**: `data/raw/delays/Train_List.csv` + `data/raw/delays/train_routes/*.csv` (1,479 station halt records with empirical delay distributions).
* **Future Yātrā Role**: Provides ground-truth historical distributions (`Average_Delay`, `Right Time`, `Slight Delay`, `Significant Delay`, `Cancelled/Unknown`). Trains ML estimators (e.g., LightGBM / XGBoost) to compute dynamic risk scores for transfers and recommend safe buffer windows between legs.

### Component C: Multi-Modal Air vs. Rail Trade-off Engine
* **Input Data**: `data/raw/flights/Clean_flight_data_Vivek.csv` (300,261 itineraries).
* **Future Yātrā Role**: Powers Pareto-optimal trade-off analysis between High-Speed / Express Rail (Vande Bharat, Rajdhani, Tejas) and Domestic Flights on major corridors (Delhi–Mumbai, Bangalore–Delhi, Chennai–Kolkata, etc.), balancing **Travel Duration**, **Monetary Fare**, **Carbon Footprint**, and **Reliability**.

### Component D: Environmental & Seasonal Disruption Contextualizer
* **Input Data**: `data/raw/environmental/rainfall_india_1901-2015.csv` (115 years of meteorological subdivision data).
* **Future Yātrā Role**: Informs seasonal vulnerability models. During high-risk monsoon periods (June–September), routing weights adjust to favor climate-resilient transport corridors and proactively warn travelers of flood/landslide-prone transit corridors.

---

## 5. Architectural Safeguard: Provider-Agnostic Schema Strategy

In accordance with Yātrā's strict architectural requirement, the system is decoupled from any third-party source:
* All raw datasets remain in untouched original format under `data/raw/`.
* A formal mapping specification has been created in `data/external/yatra_internal_schema_mapping.md`.
* In Phase 2 (Data Cleaning & Preprocessing), translation adapters will transform raw records into canonical Yātrā entities (`TransitStationNode`, `TransitScheduleSegment`, `TransitReliabilityProfile`, `MultiModalFlightOffer`, `EnvironmentalClimateRisk`).
* Downstream ML models and routing algorithms will interface exclusively with these canonical types, allowing seamless swapping with official government feeds (OGD Platform India) or live APIs (NTES, DGCA, Open-Meteo) without altering core application code.
