# YĀTRĀ AI — Phase 2 Requirement Specification & Prompt Archive

## 1. Phase Objective
Perform comprehensive diagnostic profiling, data cleaning, coordinate anomaly handling, geographic validation, and schema harmonization on the acquired raw datasets. Create a high-performance, provider-independent canonical data layer (`data/processed/`), define legitimate entity join strategies without artificial linkages, and rigorously evaluate candidate machine learning problem formulations.

---

## 2. Core Directives & Constraints
1. **Raw Data Remains Untouched**: Operations must read from `data/raw/` in read-only mode and output clean assets into `data/processed/`.
2. **Dual-Format Persistence**: Save all processed tables in both `.parquet` (columnar performance) and `.csv` (human/audit readability).
3. **No Premature ML or Synthetic Choices**: Strictly avoid synthetic choice generation or classifier training.
4. **Legitimate Joins Only**: Prohibit invalid row-level linkages between independent datasets (e.g. do not join domestic flights and train delays by arbitrary timestamps).
5. **Portability**: All file paths in data cleaning scripts must use repository-relative base directories.

---

## 3. Required Data Cleaning & Transformation Tasks
* **Stations Directory (`stations.json`)**:
  - Filter out dummy/test stations (e.g., coordinates at `0.0, 0.0`).
  - Validate coordinates within Indian bounding box ($6^\circ\text{N} \le \text{lat} \le 37^\circ\text{N}$, $68^\circ\text{E} \le \text{lon} \le 98^\circ\text{E}$).
  - Cluster metro stations into urban transit hubs (DEL, BOM, BLR, MAA, CCU, HYD).
* **Trains Timetable (`trains.json`)**:
  - Normalize 5,208 passenger train services and 416,637 halt stops.
  - Calculate inter-station geodesic Haversine distance in kilometers and cumulative route kilometers.
  - Calculate halt dwell times and arrival/departure minutes from midnight.
* **Flight Records (`Clean_flight_data_Vivek.csv`)**:
  - Identify and eliminate exact duplicate records.
  - Standardize duration into decimal hours and derive price-per-hour metrics.
* **Historical Delays (`Train_List.csv` + route files)**:
  - Reconcile legacy station code aliases (e.g., `ALD` $\to$ `PRYJ`, `MGS` $\to$ `DDU`, `SBC` $\to$ `SMVB`).
  - Compute delay probabilities (`p_on_time`, `p_slight_delay`, `p_severe_delay`, `p_cancelled`).
* **Monsoon Rainfall (`rainfall_india_1901-2015.csv`)**:
  - Impute sparse missing monthly values using historical subdivisional medians.
  - Calculate 30-year climatological normals (1986–2015) and seasonal monsoon ratios.
* **Multimodal Corridor Benchmark**:
  - Construct direct Rail vs. Air comparison metrics across 30 metro corridor pairs.

---

## 4. Required Deliverables
1. **Canonical Processed Tables** in `data/processed/` (Parquet + CSV).
2. **Data Dictionary**: Exhaustive variable definitions, units, types, and value bounds (`docs/data_dictionary.md`).
3. **Relational Join Strategy Document**: Explicit primary/foreign key mappings and prohibited joins (`docs/dataset_join_strategy.md`).
4. **ML Problem Formulation Analysis**: Formal mathematical evaluation of 5 candidate ML formulations (`docs/ml_problem_definition.md`).
5. **Phase 2 Technical Report**: Complete diagnostic audit report documenting anomalies, cleaning transformations, and ML architecture decisions.
