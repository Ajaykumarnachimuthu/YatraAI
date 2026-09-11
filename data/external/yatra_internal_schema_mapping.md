# YĀTRĀ AI — Internal Unified Data Schema Mapping (Phase 1)

## Architectural Principle: Provider Agnosticism & Decoupled Ingestion

To ensure long-term architectural stability, **no downstream machine learning model, optimization algorithm, or orchestration service in Yātrā AI shall interact directly with provider-specific schemas** (such as raw Kaggle columns, GitHub repository-specific names, or third-party scraper exports).

Instead, Yātrā AI adopts an **Adapter & Canonical Schema** pattern:
1. **Raw Tier (`data/raw/`)**: Unaltered original files preserved exactly as collected.
2. **Standardization Tier (`data/processed/`)**: Schema normalization pipelines translate external data into unified Yātrā canonical entity schemas.
3. **Serving/Feature Tier (`src/`)**: Routing algorithms, feature extractors, and ML estimators operate exclusively on Yātrā canonical data types.
4. **Future Pluggability**: Government open data feeds (OGD data.gov.in) and real-time APIs (NTES, DGCA, Open-Meteo, TomTom/Google Maps API) can seamlessly replace or augment static datasets without modifying downstream application logic.

---

## Canonical Yātrā Entities & Field Mappings

### 1. `TransitStationNode` (Geographic & Station Network Topology)

| Canonical Yātrā Field | Type | Description | Mapped From `stations.json` | Future Government / Real-Time API |
| :--- | :--- | :--- | :--- | :--- |
| `station_id` | `str` (Primary Key) | Standard station code | `code` (`"NDLS"`) | IRCTC/CRIS Station Code |
| `station_name` | `str` | Normalized station name | `name` (`"New Delhi"`) | Official Railway Gazette Name |
| `state_ut` | `str` | State / Union Territory | `state` (`"Delhi"`) | Census / OGD State Master |
| `zone_division` | `str` | Railway administrative zone | `zone` (`"NR"`) | Indian Railways Zone (17 zones) |
| `locality_address` | `str` | Postal address / city context | `address` | Geospatial Reverse Geocode |
| `latitude` | `float` | WGS84 Latitude (-90 to +90) | `coordinates.latitude` | Survey of India / GPS sensor |
| `longitude` | `float` | WGS84 Longitude (-180 to +180) | `coordinates.longitude` | Survey of India / GPS sensor |

---

### 2. `TransitScheduleSegment` (Multi-Stop Intercity Rail Timetable)

| Canonical Yātrā Field | Type | Description | Mapped From `trains.json` | Future Government / Real-Time API |
| :--- | :--- | :--- | :--- | :--- |
| `service_id` | `str` | Identifier of train service | `trainNumber` (`"12951"`) | NTES Train Number |
| `service_name` | `str` | Name of the train | `trainName` (`"MUMBAI RAJDHANI"`) | CRIS Train Name |
| `service_type` | `str` | Train classification category | `type` (`"Raj"`, `"SF"`, `"Exp"`) | Indian Railways Train Class |
| `origin_station_id` | `str` | Source terminal code | `source.code` (`"MMCT"`) | Origin Station Code |
| `destination_station_id`| `str` | Destination terminal code | `destination.code` (`"NDLS"`) | Destination Station Code |
| `active_operating_days` | `list[str]` | Days of service operation | `runningDays` (`{"SUN": true...}`) | CRIS Weekly Running Schedule |
| `total_route_distance_km`| `float` | Total journey length | `overallDistanceKm` | Official Rail Mileage Chart |
| `stop_sequence_idx` | `int` | Sequential stop ordinal (1..N) | `completeOrderedRoute[].sequence` | Timetable Stop Sequence |
| `stop_station_id` | `str` | Intermediate station code | `completeOrderedRoute[].stationCode` | CRIS Station Identifier |
| `arrival_time_utc` | `str/time` | Scheduled arrival time | `completeOrderedRoute[].arrivalTime` | NTES Scheduled Arrival |
| `departure_time_utc` | `str/time` | Scheduled departure time | `completeOrderedRoute[].departureTime` | NTES Scheduled Departure |
| `cumulative_distance_km` | `float` | Distance from origin to stop | `completeOrderedRoute[].distance` | Mileage Track Distance |
| `journey_day_offset` | `int` | 1-based day count of journey | `completeOrderedRoute[].journeyDay` | Multi-day Journey Index |

---

### 3. `TransitReliabilityProfile` (Empirical Delays & On-Time Performance)

| Canonical Yātrā Field | Type | Description | Mapped From `train_routes/*.csv` | Future Government / Real-Time API |
| :--- | :--- | :--- | :--- | :--- |
| `service_id` | `str` | Train identification number | Filename `<Train_Number>.csv` | NTES Historical Delay Log |
| `station_id` | `str` | Station code at delay checkpoint | `Station` (`"GHY"`) | NTES Tracking Station |
| `mean_delay_minutes` | `float` | Mean delay in minutes | `Average_Delay(min)` | Live NTES Delay Average |
| `prob_on_time` | `float` | Probability of arrival ≤15 min | `Right Time (0-15 min's)` / 100.0 | NTES P(delay ≤ 15m) |
| `prob_slight_delay` | `float` | Probability of 15–60 min delay | `Slight Delay (15-60 min's)` / 100.0 | NTES P(15m < delay ≤ 60m) |
| `prob_severe_delay` | `float` | Probability of >60 min delay | `Significant Delay (>1 Hour)` / 100.0 | NTES P(delay > 60m) |
| `prob_cancellation` | `float` | Cancellation / disruption risk | `Cancelled/Unknown` / 100.0 | NTES Cancellation Feed |

---

### 4. `MultiModalFlightOffer` (Intercity Air Travel Segment)

| Canonical Yātrā Field | Type | Description | Mapped From `Clean_flight_data_Vivek.csv` | Future Government / Commercial API |
| :--- | :--- | :--- | :--- | :--- |
| `carrier_name` | `str` | Operating airline name | `airline` (`"Indigo"`, `"Vistara"`) | DGCA / Amadeus / Skyscanner |
| `flight_number` | `str` | Flight route code | `flight` (`"6E-5001"`) | Live Flight Tracking (FlightRadar/Cirium) |
| `origin_city` | `str` | Origin airport city | `source_city` (`"Delhi"`) | IATA Origin City Code |
| `destination_city` | `str` | Destination airport city | `destination_city` (`"Mumbai"`) | IATA Destination City Code |
| `departure_time_window` | `str` | Time slot of departure | `departure_time` (`"Morning"`) | Exact UTC Scheduled Departure |
| `arrival_time_window` | `str` | Time slot of arrival | `arrival_time` (`"Night"`) | Exact UTC Scheduled Arrival |
| `num_intermediate_stops`| `int` | Layover stop count | `stops` (`0`, `1`, `2`) | Flight Leg Count |
| `cabin_class` | `str` | Travel class tier | `class` (`"Economy"`, `"Business"`) | Fare Class Hierarchy |
| `duration_hours` | `float` | Total flight transit hours | `duration` (`2.17`) | Block Time Duration |
| `booking_lead_days` | `int` | Days prior to travel | `days_left` (`1`..`49`) | Dynamic Fare Window |
| `fare_inr` | `float` | Ticket base price in INR | `price` (`5953.0`) | Live Fare Quote API |

---

### 5. `EnvironmentalClimateRisk` (Subdivisional Meteorological Context)

| Canonical Yātrā Field | Type | Description | Mapped From `rainfall_india_1901-2015.csv` | Future Government / Open API |
| :--- | :--- | :--- | :--- | :--- |
| `subdivision_region` | `str` | Meteorological zone name | `SUBDIVISION` | IMD Region Boundary / GeoJSON |
| `historical_year` | `int` | Observation calendar year | `YEAR` (1901–2015) | IMD Annual Climatology Archive |
| `monthly_rainfall_mm` | `dict[str, float]` | Monthly precipitation in mm | `JAN` .. `DEC` | IMD Gridded Rainfall Data (0.25° x 0.25°) |
| `annual_rainfall_mm` | `float` | Total annual precipitation | `ANNUAL` | Open-Meteo Historical Climate API |
| `monsoon_intensity_idx`| `float` | Computed JJAS monsoon load | `(JUN+JUL+AUG+SEP) / ANNUAL` | ECMWF ERA5 Precipitation Index |
