# Yātrā AI — Phase 4 Step 1: Pre-Training Dataset & Leakage Audit Report
**Supervised Machine Learning Data Foundation Audit**  
*Document Version: 1.0.0 | Date: 2026-09-11 | Project: Yātrā AI*

---

> [!IMPORTANT]
> **SIMULATION TARGET DISCLAIMER**  
> The target variable `chosen` is **synthetic behavioural ground truth** generated under explicitly documented random utility (MNL) simulation assumptions. It is used as a controlled benchmark to validate that Yātrā AI recommendation models can recover traveler preference-to-itinerary choice mappings. It must NOT be described as observed real-world booking transactions.

---

## 1. Dataset Dimensions & Inspection Overview

- **Source File**: `data/synthetic/choice_dataset.parquet`
- **Total Choice Instances (Rows)**: **138,603**
- **Total Columns**: **39**
- **Unique Travellers**: **5,000**
- **Search Sessions**: **40,000**
- **Missing / Null Values**: **0** (100% complete across all 39 columns)
- **Primary Classification Target**: `chosen` $\in \{0, 1\}$
  - Class 0 (Not Chosen): **98,603** rows (**71.14%**)
  - Class 1 (Chosen): **40,000** rows (**28.86%**)
  - Imbalance Ratio: **2.465 : 1** (natural session-level choice menu structure)

---

## 2. Feature Classification & Pre-Training Leakage Audit

Every single column has been formally classified into one of six audit tiers to prevent data leakage and target contamination:

| Column Name | Data Type | Audit Classification Tier | Status | Rationale & Operational Role |
|---|:---:|:---:|:---:|---|
| `chosen` | int64 | **TARGET** | **TARGET LABEL** | Binary choice outcome ($y$). |
| `choice_probability` | float64 | **LEAKAGE / POST-CHOICE** | **STRICTLY EXCLUDED** | Continuous MNL softmax probability $P_{nj}$. Directly reveals target likelihood. |
| `utility` | float64 | **LEAKAGE / SIMULATION OUTPUT** | **STRICTLY EXCLUDED** | Deterministic utility score $V_{nj}$ used to sample the target choice. |
| `rank` | int64 | **LEAKAGE / POST-CHOICE** | **STRICTLY EXCLUDED** | Ordinal rank $\{1, \dots, J_s\}$ assigned after sorting alternatives by utility. |
| `traveller_id` | object | **IDENTIFIER / PARTITION KEY** | **EXCLUDED FROM FEATURES** | Unique traveller key used strictly for 70/15/15 grouping splits. |
| `session_id` | object | **IDENTIFIER** | **EXCLUDED FROM FEATURES** | Session grouping key; not a generalizable predictive transit feature. |
| `alternative_id` | object | **IDENTIFIER** | **EXCLUDED FROM FEATURES** | Primary key of candidate row within session. |
| `service_identifier` | object | **HIGH-CARDINALITY IDENTIFIER** | **EXCLUDED FROM FEATURES** | Specific flight/train number (3,060 unique strings; risk of memorization). |
| `source_record_id` | object | **PROVENANCE IDENTIFIER** | **EXCLUDED FROM FEATURES** | Internal tracking key linking candidate back to canonical processed source tables. |
| `source_dataset` | object | **METADATA** | **EXCLUDED FROM FEATURES** | Name of canonical table; redundant with `mode`. |
| `persona_type` | object | **SYNTHETIC PERSONA** | **EVALUATED IN MODEL B ONLY** | 6 simulation archetypes; evaluated to test incremental value over Travel DNA. |
| `cost_sensitivity` | float64 | **TRAVELLER PREFERENCE (DNA)** | **SAFE PREDICTOR** | Continuous traveler sensitivity $\in [0, 1]$. Available pre-choice. |
| `time_sensitivity` | float64 | **TRAVELLER PREFERENCE (DNA)** | **SAFE PREDICTOR** | Continuous traveler sensitivity $\in [0, 1]$. Available pre-choice. |
| `reliability_sensitivity`| float64 | **TRAVELLER PREFERENCE (DNA)** | **SAFE PREDICTOR** | Continuous traveler sensitivity $\in [0, 1]$. Available pre-choice. |
| `comfort_preference` | float64 | **TRAVELLER PREFERENCE (DNA)** | **SAFE PREDICTOR** | Continuous traveler sensitivity $\in [0, 1]$. Available pre-choice. |
| `transfer_tolerance` | float64 | **TRAVELLER PREFERENCE (DNA)** | **SAFE PREDICTOR** | Continuous traveler sensitivity $\in [0, 1]$. Available pre-choice. |
| `departure_time_flexibility` | float64 | **TRAVELLER PREFERENCE (DNA)** | **SAFE PREDICTOR** | Continuous traveler sensitivity $\in [0, 1]$. Available pre-choice. |
| `sustainability_preference` | float64 | **TRAVELLER PREFERENCE (DNA)** | **SAFE PREDICTOR** | Continuous traveler sensitivity $\in [0, 1]$. Available pre-choice. |
| `origin_city` | object | **SESSION CONTEXT** | **SAFE PREDICTOR** | Origin metro city specified in query. |
| `destination_city` | object | **SESSION CONTEXT** | **SAFE PREDICTOR** | Destination metro city specified in query. |
| `departure_window` | object | **SESSION CONTEXT** | **SAFE PREDICTOR** | Requested departure window specified in query. |
| `trip_purpose` | object | **SESSION CONTEXT** | **SAFE PREDICTOR** | Stated trip purpose (Commute, Business, Leisure, Family). |
| `party_size` | int64 | **SESSION CONTEXT** | **SAFE PREDICTOR** | Number of passengers in travel party (1–4). |
| `lead_days` | int64 | **SESSION CONTEXT** | **SAFE PREDICTOR** | Booking horizon days (1–49). |
| `mode` | object | **ITINERARY ATTRIBUTE** | **SAFE PREDICTOR** | Travel mode (`Flight` vs `Rail`). |
| `carrier` | object | **ITINERARY ATTRIBUTE** | **SAFE PREDICTOR** | Airline brand or train service category. |
| `service_tier` | object | **ITINERARY ATTRIBUTE** | **SAFE PREDICTOR** | Cabin class / passenger accommodation tier. |
| `raw_cost` | float64 | **OPERATIONAL / ITINERARY** | **SAFE PREDICTOR** | Ticket fare in INR. |
| `raw_duration` | float64 | **OPERATIONAL / ITINERARY** | **SAFE PREDICTOR** | Journey duration in hours. |
| `raw_distance` | float64 | **OPERATIONAL / ITINERARY** | **SAFE PREDICTOR** | Geodesic route distance in km. |
| `carbon_estimate_kg` | float64 | **OPERATIONAL / ITINERARY** | **SAFE PREDICTOR** | Route carbon emissions estimate in kg CO2e. |
| `transfer_count` | int64 | **OPERATIONAL / ITINERARY** | **SAFE PREDICTOR** | Number of layovers / transfers (0, 1, 2). |
| `cost_score` | float64 | **DERIVED CANDIDATE SCORE** | **SAFE PREDICTOR** | Session-relative min-max normalized cost score $\in [0, 1]$. |
| `time_score` | float64 | **DERIVED CANDIDATE SCORE** | **SAFE PREDICTOR** | Session-relative min-max normalized duration score $\in [0, 1]$. |
| `reliability_score` | float64 | **DERIVED CANDIDATE SCORE** | **SAFE PREDICTOR** | Pre-choice operational reliability score $\in [0, 1]$. |
| `comfort_score` | float64 | **DERIVED CANDIDATE SCORE** | **SAFE PREDICTOR** | Accommodation tier proxy comfort score $\in [0, 1]$. |
| `transfer_score` | float64 | **DERIVED CANDIDATE SCORE** | **SAFE PREDICTOR** | Non-linear transfer penalty score $1 / (1 + \text{transfers})$. |
| `carbon_score` | float64 | **DERIVED CANDIDATE SCORE** | **SAFE PREDICTOR** | Session-relative min-max normalized carbon savings score $\in [0, 1]$. |
| `departure_fit` | float64 | **DERIVED CANDIDATE SCORE** | **SAFE PREDICTOR** | Pre-choice departure window alignment score $\in [0, 1]$. |

---

## 3. Strict Pre-Choice Verification of Derived Candidate Scores

The pre-training audit explicitly confirmed that the 7 derived candidate scores (`cost_score`, `time_score`, `reliability_score`, `comfort_score`, `transfer_score`, `carbon_score`, and `departure_fit`):
1. Are calculated **strictly from candidate transit attributes and search query context** within the session's candidate menu.
2. Have **zero mathematical or algorithmic dependency** on `chosen`, `choice_probability`, `utility`, or `rank`.
3. Are known and available to the recommendation system at inference time *before* the user makes a choice.
4. Are verified safe predictors that do not induce target leakage.

---

## 4. Two Evaluated Feature Configurations

1. **Configuration A: Core Itinerary Model (28 Features)**
   - 7 Travel DNA Continuous Variables
   - 6 Session Context Variables (4 categorical, 2 numeric)
   - 3 Transit Categoricals (`mode`, `carrier`, `service_tier`)
   - 5 Itinerary Operational Numerics (`raw_cost`, `raw_duration`, `raw_distance`, `carbon_estimate_kg`, `transfer_count`)
   - 7 Derived Quality Scores (`cost_score`, `time_score`, `reliability_score`, `comfort_score`, `transfer_score`, `carbon_score`, `departure_fit`)
   - *Excludes*: `persona_type`
2. **Configuration B: Extended Model (29 Features)**
   - All 28 Core features + `persona_type`
   - *Objective*: Measure whether coarse synthetic persona archetypes provide incremental predictive signal over continuous Travel DNA dimensions.
