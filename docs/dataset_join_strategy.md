# YĀTRĀ AI — Dataset Relationship & Join Strategy (Phase 2)

## Architectural Principle: Grounded, Legitimate Linkages

In multi-modal journey orchestration, combining heterogeneous datasets is necessary to construct journey graphs and predict transit risks. However, **forcing invalid joins** (such as joining disparate modalities by arbitrary timestamps or assuming non-existent direct relationships) introduces severe data corruption and invalid ML targets.

This document formalizes the **Entity-Relationship Architecture** of Project YĀTRĀ AI, proving which datasets can legitimately be linked, the exact keys used, empirical key match statistics, and explicitly proscribed join anti-patterns.

---

## 1. Global Entity-Relationship Graph

```
+-----------------------------------+
|    canonical_stations.parquet     |
|      (8,990 Railway Stations)     |
| PK: station_code                  |
| Attr: lat, lon, state, zone,      |
|       metro_cluster               |
+-----------------------------------+
       ^                     ^
       | station_code        | state -> subdivision
       | (100% match)        | (100% mapped)
       |                     v
+--------------------+   +---------------------------------------+
| canonical_train_   |   | canonical_subdivision_rainfall.parquet|
| routes.parquet     |   | (36 IMD Subdivisions, 1901-2015)      |
| (416,637 Halts)    |   | Composite PK: (subdivision, year)     |
| PK: (train_num,seq)|   | Attr: monthly_mm, monsoon_ratio       |
+--------------------+   +---------------------------------------+
       ^
       | train_number
       | (47.7% train / 100% station match)
       v
+-----------------------------------+
|   canonical_train_delays.parquet  |
|      (1,479 Station Halts)        |
| PK: (train_number, station_code)  |
| Attr: mean_delay, p_on_time,      |
|       p_severe_delay, p_cancel    |
+-----------------------------------+

       =================================================
       CROSS-MODAL METRO CLUSTER LINKAGE (No row join!)
       =================================================

+-----------------------------------+       +-----------------------------------+
|    canonical_stations.parquet     |       |    canonical_flights.parquet      |
| Attr: metro_cluster               |       | Attr: source_city,                |
| (Delhi, Mumbai, Bangalore, etc.)  |       |       destination_city            |
+-----------------------------------+       +-----------------------------------+
                 \                                     /
                  \                                   /
                   v                                 v
          +---------------------------------------------------+
          |     canonical_corridor_multimodal.parquet         |
          |  Corridor: Origin_City - Destination_City         |
          |  (30 Metro Pairs: Air Fares/Dur vs Rail Dist/Dur) |
          +---------------------------------------------------+
```

---

## 2. Legitimate Linkages & Key Specifications

### Linkage 1: Station Code Join (`trains.json` $\longleftrightarrow$ `stations.json`)
* **Join Keys**: `canonical_train_routes.station_code` = `canonical_stations.station_code`
* **Cardinality**: Many-to-One ($N:1$). A single physical station serves hundreds of scheduled train halts.
* **Empirical Integrity**:
  * Total unique station codes referenced across 416,637 route halts: **8,539**
  * Matching station codes present in `canonical_stations`: **8,539 (100.00% match)**
  * Unmatched station codes: **0**
* **Information Transferred**: Precise WGS84 GPS coordinates (`latitude`, `longitude`), `state`, `railway_zone`, and `metro_cluster`.
* **Legitimacy Justification**: Station codes in India are standardized by CRIS/IRCTC across all operational publications. This join is mathematically and operationally exact.

---

### Linkage 2: Train Delay Service & Halt Join (`delays` $\longleftrightarrow$ `routes`)
* **Primary Key**: `(train_number, station_code)`
* **Empirical Integrity**:
  * Total delay halt records: **1,479**
  * Train numbers in delays strictly matching `canonical_train_services`: **18 / 42 trains (47.7% of delay rows)**
    * *Root Cause Analysis of remaining 24 trains*: 12 are festive/special clone trains with temporary numbers (prefixed with `0`, e.g., `02501`, `05639`), and 12 are recently inaugurated premium Tejas/Rajdhani services (e.g., `20501`, `20503`).
  * Station codes in delay records matching `canonical_stations`: **269 / 269 (100.00%)** after resolving 6 official IR station renamings:
    * `PRYJ` $\rightarrow$ `ALD` (Prayagraj / Allahabad)
    * `DDU` $\rightarrow$ `MGS` (Pt. Deen Dayal Upadhyaya / Mughalsarai)
    * `SMVB` $\rightarrow$ `SBC` (Sir M. Visvesvaraya Terminal / Bangalore)
    * `PCOI` $\rightarrow$ `COI` (Prayagraj Chheoki)
    * `NBJU` $\rightarrow$ `BJU` (New Barauni)
    * `NKMG` $\rightarrow$ `KXJ` (New Karimganj)
* **Information Transferred**: Historical delay distributions (`p_on_time`, `p_severe_delay`, `p_cancelled`, `mean_delay_minutes`) attached to scheduled route halts.
* **Legitimacy Justification**: Operating trains are identified by their 5-digit number and verified at specific station timing checkpoints. Where a train number is a seasonal special, the station-level empirical delay distribution still provides station reliability ground truth.

---

### Linkage 3: Spatial Subdivision Join (`stations.json` $\longleftrightarrow$ `rainfall.csv`)
* **Join Keys**: `canonical_stations.state` $\longrightarrow$ State-to-Subdivision Crosswalk Table $\longrightarrow$ `canonical_subdivision_rainfall.subdivision`
* **Cardinality**: One-to-Many ($1:M$) or Many-to-One ($N:1$) depending on state size:
  * Single-state subdivisions: e.g., `BIHAR` $\leftrightarrow$ Bihar, `KERALA` $\leftrightarrow$ Kerala, `PUNJAB` $\leftrightarrow$ Punjab.
  * Multi-state subdivisions: e.g., `HARYANA DELHI & CHANDIGARH` $\leftrightarrow$ Haryana, Delhi NCT, Chandigarh.
  * Multi-subdivision states: e.g., Maharashtra $\leftrightarrow$ `KONKAN & GOA`, `MADHYA MAHARASHTRA`, `MATATHWADA`, `VIDARBHA` (resolved via station district/zone or state mean).
* **Empirical Integrity**: **100%** of stations in Indian States map to one or more meteorological subdivisions.
* **Information Transferred**: Climatological baseline normals (`baseline_normal_annual_rainfall_mm`, `baseline_normal_monsoon_rainfall_mm`, `monsoon_intensity_ratio`).
* **Legitimacy Justification**: Weather disruption risks (e.g. landslides in Konkan, flooding in Assam/Bihar) are regional phenomena best captured at the meteorological subdivision level.

---

### Linkage 4: Metropolitan Corridor Hub Mapping (`flights.csv` $\longleftrightarrow$ `stations.json`)
* **Join Keys**: `canonical_flights.source_city` $\longleftrightarrow$ `canonical_stations.metro_cluster`
* **Cardinality**: Many-to-Many ($M:N$) via corridor aggregation.
* **Empirical Cluster Definition**:
  * **Delhi Hub**: Major Terminals: `NDLS`, `DLI`, `NZM`, `ANVT` (Airport: DEL / Indira Gandhi Intl)
  * **Mumbai Hub**: Major Terminals: `MMCT`, `BCT`, `CSMT`, `BDTS`, `LTT` (Airport: BOM / Chhatrapati Shivaji Maharaj Intl)
  * **Bangalore Hub**: Major Terminals: `SBC`, `YPR`, `SMVB` (Airport: BLR / Kempegowda Intl)
  * **Kolkata Hub**: Major Terminals: `HWH`, `SDAH`, `KOAA`, `SHM` (Airport: CCU / Netaji Subhash Chandra Bose Intl)
  * **Hyderabad Hub**: Major Terminals: `SC`, `HYB`, `KCG` (Airport: HYD / Rajiv Gandhi Intl)
  * **Chennai Hub**: Major Terminals: `MAS`, `MS`, `TBM` (Airport: MAA / Chennai Intl)
* **Information Transferred**: Corridor-level mode comparison (airfare distribution vs. rail journey time and distance across 30 metro pairs).
* **Legitimacy Justification**: Travelers do not choose between a flight and a train station; they choose between city-to-city transportation corridors. Aggregating multi-station clusters to metropolitan regions preserves genuine multi-modal substitution choices without false row-level joins.

---

## 3. Explicitly Prohibited Join Anti-Patterns

To maintain scientific integrity and prevent data leakage, the following joins are **strictly prohibited**:

| Prohibited Join | Why It Is Illegitimate | Consequence If Attempted |
| :--- | :--- | :--- |
| **Row-level join of Flights and Train Timetables on Date/Time** | Flights and trains operate on different schedules. Flights in our dataset are sampled airline itineraries across 50 advance booking days; train timetables are recurring weekly schedules. | Creates completely fabricated itineraries where a flight and a train "coincide" by coincidence of timestamp, introducing synthetic noise. |
| **Joining Train Delays to Unmonitored Branch Line Trains** | The 1,479 delay records come from 42 long-distance express trains on Northeast–Metro corridors. Merging these delays directly onto local passenger trains in Tamil Nadu or Rajasthan is ungrounded. | Distorts local train performance by imputing multi-thousand kilometer express train delay statistics onto 50 km local commuters. |
| **Row-level Station Weather Attribution from Monthly Rainfall** | IMD rainfall data represents monthly historical subdivisional totals (1901–2015), not hourly precipitation at individual platform tracks. | Spurious correlation: treating a monthly regional rainfall figure as if it were the exact weather at the minute a train departed a station. |
| **Inventing Synthetic User IDs to Join Flights and Rail** | Real public datasets contain zero user accounts or traveler transaction IDs. | Claiming a real user "chose" a flight over a train when no such observation exists in the data. |

---

## 4. Legitimate Multi-Modal Corridor Matrix (Sample)

Below is an empirical sample from `canonical_corridor_multimodal.parquet`, demonstrating how Rail and Flight options legitimately compare across major Indian metro pairs without invalid row joins:

| Corridor | Direct Flight Options | Non-stop Flights | Median Flight Duration | Median Econ Flight Fare | Direct Train Services | Rail Track Distance | Available Train Types |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Delhi–Mumbai** | 15,282 | 1,762 | 2.17 hrs | ₹5,953 | 24 trains | 1,366 km | `Raj, SF, Exp, GR` |
| **Delhi–Kolkata** | 11,048 | 1,120 | 2.25 hrs | ₹6,060 | 28 trains | 1,441 km | `Raj, SF, Exp, Drnt` |
| **Delhi–Bangalore** | 13,091 | 1,450 | 2.67 hrs | ₹7,425 | 14 trains | 2,276 km | `Raj, SF, Exp, Drnt` |
| **Mumbai–Chennai** | 10,114 | 980 | 1.92 hrs | ₹4,890 | 18 trains | 1,281 km | `SF, Exp, Mail` |
| **Kolkata–Chennai** | 9,842 | 890 | 2.25 hrs | ₹5,840 | 12 trains | 1,662 km | `SF, Exp, Mail` |
| **Bangalore–Hyderabad**| 8,920 | 1,210 | 1.17 hrs | ₹3,150 | 16 trains | 570 km | `Exp, SF, Pass` |
