# YĀTRĀ AI — Phase 2 Diagnostic, Normalization & ML Problem Definition Report

## Executive Summary

Phase 2 of **Project Yātrā AI** successfully transitioned our raw public transit, geographic, and climatological datasets into a provider-independent canonical data tier (`data/processed/`). We performed exhaustive diagnostic auditing, verified legitimate relational linkages without artificial joins, established a comprehensive data dictionary, evaluated 5 candidate machine learning formulations, and formulated a defensible multi-tier ML architecture.

In strict accordance with project constraints:
* **Zero synthetic data** was generated.
* **Zero machine learning models** were trained.
* **No frontend/backend code** was constructed prematurely.
* **Raw assets in `data/raw/` remain untouched and pristine.**

---

## 1. Raw Dataset Diagnostic & Profiling Results

| Raw Dataset | Rows | Columns | Memory / Size | Missing Values | Duplicate Rows | Key Anomalies Detected & Handled |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`stations.json`** | 8,990 | 6 attributes | 1.91 MB | 0 missing fields | 0 duplicates | **293 test/dummy records** with `(0.0, 0.0)` coordinates (e.g. `XX-BECE`, `YY-BPLC`). Flagged and isolated in canonical layer; 8,697 genuine stations verified within Indian bounding box. |
| **`trains.json`** | 5,208 services | 8 service keys; 7 stop keys | 96.67 MB | 27,647 null arr (origins); 27,638 null dep (terminals) | 0 duplicates | **416,637 stop records**. The `distance` field inside stop objects is 0; resolved by calculating true geodesic Haversine distance between consecutive station GPS coordinates. |
| **`Train_List.csv` + 42 `train_routes/*.csv`** | 42 trains; 1,479 halt records | 5 manifest cols; 7 route cols | ~77 KB total | 0 missing values | 0 duplicates | **6 renamed station codes** in NTES logs (`PRYJ` for `ALD`, `DDU` for `MGS`, `SMVB` for `SBC`, `PCOI` for `COI`, `NBJU` for `BJU`, `NKMG` for `KXJ`). Resolved via canonical alias map; 100% of delay stations reconciled to station graph. |
| **`Clean_flight_data_Vivek.csv`** | 300,261 | 11 columns | 22.21 MB | 0 missing values | **2 exact duplicate rows** | 2 duplicate rows identified and removed (300,259 canonical rows). Prices range from ₹1,105 to ₹123,071 across 6 major metro hubs. |
| **`rainfall_india_1901-2015.csv`** | 4,116 | 15 columns | 348 KB | 4–11 nulls per month (<0.3%) | 0 duplicates | Minor missing monthly readings across 115 years imputed using subdivisional historical medians. Derived 30-year climatological normal baseline (1986–2015). |

---

## 2. Processed Canonical Datasets Created (`data/processed/`)

All canonical entities are saved in dual formats: `.parquet` (high-performance columnar storage for ML pipelines) and `.csv` (transparent tabular auditing):

1. **`canonical_stations.parquet / .csv`** (8,990 records, 10 columns): Clean station master with geocoded coordinates, state, zone, validity flags, and metro cluster tags.
2. **`canonical_train_services.parquet / .csv`** (5,208 records, 8 columns): Train service directory with running day schedules and total route distances.
3. **`canonical_train_routes.parquet / .csv`** (416,637 records, 14 columns): Granular station halt sequence with calculated segment Haversine distance, cumulative distance, halt duration in minutes, and arrival/departure minutes from midnight.
4. **`canonical_train_delays.parquet / .csv`** (1,479 records, 15 columns): Empirical arrival delay distributions, mean delay minutes, delay probabilities (`p_on_time`, `p_slight_delay`, `p_severe_delay`, `p_cancelled`), multiclass risk categories, and binary transfer failure flags.
5. **`canonical_flights.parquet / .csv`** (300,259 records, 14 columns): Deduplicated flight itineraries with directional corridors, duration hours, cabin class, lead days, and price-per-duration-hour metrics.
6. **`canonical_subdivision_rainfall.parquet / .csv`** (4,116 records, 20 columns): Complete 115-year meteorological time-series with June–September monsoon intensity ratio and 30-year normal baselines.
7. **`canonical_corridor_multimodal.parquet / .csv`** (30 records, 15 columns): Multi-modal benchmark comparing direct Rail and Air options across all 30 directional pairs of India's top 6 metro cities.

---

## 3. Dataset Join & Linkage Strategy

We formally mapped the relational architecture in [dataset_join_strategy.md](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/docs/dataset_join_strategy.md):
* **Station Code Join**: `canonical_train_routes.station_code` $\longleftrightarrow$ `canonical_stations.station_code` (**100% match across 8,539 unique route stations**).
* **Train Service Join**: `canonical_train_delays.train_number` $\longleftrightarrow$ `canonical_train_services.train_number` (47.7% strict service match; remaining 24 trains are seasonal specials/new Rajdhanis whose station sequences are 100% reconciled).
* **Regional Climate Join**: `canonical_stations.state` $\longleftrightarrow$ `canonical_subdivision_rainfall.subdivision` (100% of Indian stations map to meteorological subdivisions).
* **Cross-Modal Corridor Mapping**: `canonical_flights.source_city` $\longleftrightarrow$ `canonical_stations.metro_cluster` (aggregating multi-station urban rail terminals like NDLS/DLI/NZM/ANVT to airport cities without invalid row-level joins).
* **Explicitly Prohibited Joins**: Prohibited joining flights and train delays by arbitrary timestamps or generating synthetic user IDs to force clickstream merges.

---

## 4. Evaluation of Candidate ML Formulations

In [ml_problem_definition.md](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/docs/ml_problem_definition.md), we evaluated 5 candidate ML formulations:

1. **Binary Classification (`is_high_transfer_risk`)**:
   * Feasible on real data (1,479 records).
   * 77.6% positive skew due to long-distance express corridors; requires handling class imbalance.
2. **Multiclass Classification (`delay_risk_category`)**:
   * Feasible on real data, but exhibits severe class imbalance (`ON_TIME_RELIABLE` is 3.79%, `CANCEL_DISRUPTED` is 3.72%, while `SEVERE_DELAY` is 72.75%).
3. **Continuous Regression (`mean_delay_minutes`)**:
   * Fully supported by real data (1,479 records, mean: 122.7m, median: 95.0m, skewness: 1.28).
   * Log-transformed target $\log(1 + y)$ normalizes the distribution and directly provides dynamic edge delay costs for routing engines.
4. **Probabilistic Risk Prediction ($P(\text{Delay} > \text{Buffer})$)**:
   * Highly defensible and grounded in real empirical probability distributions (`p_on_time`, `p_slight_delay`, `p_severe_delay`, `p_cancelled`).
   * Directly answers the traveler's question: *"Will I miss my transfer at this interchange?"*
5. **Multi-Modal Journey Ranking / Recommendation**:
   * **Completely unsupported by real public datasets alone** (0 user profiles, 0 search logs, 0 booking choice records exist).
   * Legitimate only as a **Tier 2 hybrid model** in Phase 3/4 utilizing simulated traveler personas.

---

## 5. Answers to Mandatory Phase 2 Questions

### A. What the Datasets CAN Support
1. **National Spatial Rail Routing Graph**: 8,990 station nodes with WGS84 GPS coordinates and 416,637 timetable edges with calculated Haversine hop distances, halt durations, and scheduled departure/arrival constraints.
2. **Empirical Transit Delay & Reliability Estimation**: Continuous expected delay prediction and transfer failure risk modeling across major trunk corridors using 1,479 real NTES station observations.
3. **Multi-Modal Corridor Benchmarking**: Realistic travel duration, frequency, and fare distributions between domestic aviation (300,259 flights) and express rail (5,208 services) across 30 major Indian metro pairs.
4. **Regional Climatological Risk Context**: Seasonal monsoon intensity ratios and 30-year precipitation normals across 36 meteorological subdivisions to penalize flood- and landslide-vulnerable transit corridors.

### B. What the Datasets CANNOT Support
1. **Real User-Level Choice / Conversion Modeling**: Zero personal traveler IDs, booking transactions, willingness-to-pay clickstreams, or user feedback ratings exist in public datasets.
2. **Live Dynamic Seat Availability**: Public datasets contain static timetables and fare snapshots; real-time IRCTC quota availability (Tatkal, RAC, WL) is not available without live authenticated private APIs.
3. **Micro-Weather at Platform Level**: Rainfall data is monthly and subdivisional; it cannot support predicting rain at an exact station minute.
4. **Feeder Bus / Last-Mile Road Schedules**: Real static GTFS feeds for state road transport corporations (SRTCs) are fragmented and not universally available across India.

### C. Exactly What Synthetic Data We Need in Phase 3
To enable personalized multi-modal journey recommendation without violating data grounding principles, Phase 3 must generate **Traveler Behavior Personas ONLY**:
1. **Traveler Persona Vectors**: Parametric representations of traveler segments:
   * *Business Traveler*: High time sensitivity ($\alpha_{\text{time}} \gg 0$), low price sensitivity ($\beta_{\text{cost}} \approx 0$), high reliability requirement ($\gamma_{\text{risk}} \gg 0$).
   * *Budget Leisure Traveler*: High price sensitivity ($\beta_{\text{cost}} \gg 0$), low time sensitivity, flexible schedule.
   * *Family / Senior Traveler*: High penalty for intermediate transfers ($\delta_{\text{transfer}} \gg 0$), preference for daytime travel and comfort tiers.
2. **Synthetic Trip Search Queries**: Simulated origin, destination, departure time preferences, party size, and booking lead days across our 30 canonical corridors.
3. **Discrete Choice Utility Decisions**: Synthetic ground-truth ranking targets generated via standard Econometric Random Utility Models (Multinomial Logit) combining real trip attributes (duration, fare, Tier 1 risk score) with traveler persona preferences.

### D. Recommended Primary ML Target and Why
**Primary Operational Target**: **Continuous Expected Arrival Delay ($\log(1 + \text{mean\_delay\_minutes})$) and Transfer Buffer Failure Probability ($P(\text{Delay} > \Delta T)$)**.
* **Why**:
  1. It is **100% grounded in real public operational data** (1,479 verified NTES observations, 416,637 timetable halts).
  2. It avoids the arbitrary threshold boundaries of binary classification and the severe class imbalance of 4-class classification.
  3. It directly supplies the objective "Reliability Cost" required by routing algorithms to prevent travelers from selecting fragile, easily broken multi-leg itineraries.
  4. It serves as the foundation for the Phase 4 Recommendation Engine.

### E. Whether Current Data is Sufficient for That Target
**YES.** 
For the primary operational delay and risk target, the canonical datasets (`canonical_train_delays`, `canonical_train_routes`, `canonical_stations`, `canonical_subdivision_rainfall`) provide complete feature coverage with zero missing values across critical predictors. 

For the secondary ranking and recommendation layer, the current data is sufficient for the **operational itinerary features** (duration, fare, distance, risk), and will be paired with the specified Phase 3 traveler personas.

---

## 6. Verification & Phase 2 Checklist

- [x] All 5 raw datasets safely loaded, audited, and profiled.
- [x] All anomalies (dummy coordinates, station renamings, flight duplicates, rainfall nulls) diagnosed and resolved.
- [x] Canonical processed schemas created and written in dual formats (`.parquet` and `.csv`) under `data/processed/`.
- [x] Complete Data Dictionary published in [docs/data_dictionary.md](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/docs/data_dictionary.md).
- [x] Relational Join Strategy and prohibited anti-patterns documented in [docs/dataset_join_strategy.md](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/docs/dataset_join_strategy.md).
- [x] 5 ML formulations empirically analyzed and primary target recommended in [docs/ml_problem_definition.md](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/docs/ml_problem_definition.md).
- [x] Zero synthetic data generated. Zero ML models trained. Stopped after Phase 2.
