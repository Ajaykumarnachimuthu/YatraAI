# YatraAI

**Personalized Multimodal Travel Intelligence & Journey Orchestration Engine for the Indian Subcontinent**

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status: Quality Control Verified](https://img.shields.io/badge/QC_Status-VERIFIED_&_FROZEN-brightgreen.svg)](reports/final/final_quality_control_report.md)

---

## 1. Executive Overview

**Yātrā AI** is an advanced multimodal travel intelligence platform designed to address the unique complexities of long-distance intercity transit across the Indian subcontinent. By bridging fragmented sovereign railway schedules, commercial aviation tariffs, historical delay distributions, and seasonal climatological indices, Yātrā AI models individual journey utility to recommend Pareto-optimal transit alternatives tailored to traveller preferences.

---

## 2. Repository Architecture

The repository is organized according to enterprise software and reproducible machine learning standards:

```text
YatraAI/
├── config/                  # Configuration YAMLs (logging, model parameters, synthetic simulation)
├── data/                    # Three-tier data pipeline architecture
│   ├── raw/                 # Immutable real-world public datasets (rail, air, delays, weather)
│   ├── processed/           # Canonical multimodal transit graph and corridor aggregations
│   ├── synthetic/           # Frozen behavioral choice simulation (5K travellers, 40K sessions)
│   └── external/            # Sovereign data registry & provenance metadata (sources_metadata.json)
├── src/                     # Modular Python source library
│   ├── data_collection.py   # Data provenance auditor and SHA-256 integrity verification
│   ├── data_cleaning.py     # Canonical graph building and coordinate normalization
│   ├── synthetic_generation.py # 7-D Travel DNA sampling and RUM/MNL choice simulation
│   ├── validation.py        # 5-tier statistical, structural, and econometric validation suite
│   ├── feature_engineering.py # Leakage-free pre-choice normalization and feature pipeline
│   ├── train_models.py      # Multi-model baseline trainers (LR, DT, RF, HistGB)
│   ├── phase4_baseline.py   # Baseline model experiment runner (Core & Extended)
│   ├── phase4_step2.py      # Constrained decision threshold optimizer (tau* = 0.30)
│   ├── evaluation.py        # Cross-model evaluation and metric reporting engine
│   ├── generate_evidence_assets.py # Visual renderer for 300 DPI formula and table cards
│   └── generate_presentation.py    # 12-slide PowerPoint presentation generator
├── notebooks/               # Populated, executable Jupyter analysis notebooks (01 to 06)
├── results/                 # Generated experimental outputs, model artifacts, and figures
│   ├── models/              # Serialized champion pipeline (champion_gb_core.joblib)
│   ├── figures/             # 35 visual evidence assets (formulas, tables, EDA, evaluation plots)
│   └── tables/              # Machine-readable evaluation CSVs and provenance registries
├── docs/                    # Architectural documentation, data dictionaries, and prompts
└── reports/                 # Comprehensive phase evidence reports and final viva defense
    ├── phase1/              # Phase 1: Real Public Data Foundation & Provenance
    ├── phase2/              # Phase 2: Canonical Transit Graph & Spatial Cleaning
    ├── phase3/              # Phase 3: Synthetic Behavioral Choice Simulation
    ├── phase4/              # Phase 4: Baseline Models & Threshold Optimization
    └── final/               # Phase 5: Master Comprehensive Report, Presentation & Viva Guide
```

---

## 3. Real / Public Data Foundation & Provenance

All foundational transit supply datasets in `data/raw/` are authentic, publicly verifiable datasets:

| Domain | Raw Local Asset | Records | Source / Sponsoring Platform | License |
|:---|:---|:---|:---|:---|
| **Rail Stations Topology** | `data/raw/railways/stations.json` | 8,990 | CRIS / IRCTC via GitHub (`prasenjit-27`) | MIT License |
| **Train Schedules & Halts** | `data/raw/railways/trains.json` | 5,208 (416K stops) | Indian Railways / IRCTC via GitHub (`prasenjit-27`) | MIT License |
| **Operational Train Delays**| `data/raw/delays/Train_List.csv` + 42 routes | 1,479 | NTES Historical Logs via GitHub (`ankitaanand28`) | Open Academic |
| **Domestic Aviation Fares** | `data/raw/flights/Clean_flight_data_Vivek.csv` | 300,261 | EaseMyTrip Metro Network (`vivek236` / Kaggle) | CC0 / Public Domain |
| **Climatological Rainfall** | `data/raw/environmental/rainfall_india_1901-2015.csv` | 4,116 | India Meteorological Department (`data.gov.in`) | GODL-India |

*Complete provenance metadata and verification scripts are available in [`src/data_collection.py`](src/data_collection.py) and [`notebooks/01_data_collection.ipynb`](notebooks/01_data_collection.ipynb).*

---

## 4. Machine Learning Formulation & Results

* **Problem Formulation**: Pointwise binary classification predicting journey adoption (`chosen ∈ {0, 1}`) across search session candidate sets.
* **Class Distribution**: Negative (`0`): 98,603 (71.14%) | Positive (`1`): 40,000 (28.86%).
* **Partitioning**: Strictly deterministic traveller-level 70/15/15 train/validation/test split (`seed=42`, zero traveller overlap).
* **Champion Model**: `HistGradientBoostingClassifier` trained on Core features (28 features) with decision threshold tuned to $\tau^* = 0.30$ under a business precision constraint ($\text{Precision} \ge 0.42$).

### Champion Performance on Frozen Test Partition:

| Metric | Baseline ($\tau = 0.50$) | Champion ($\tau^* = 0.30$) | Operational Gain |
|:---|:---:|:---:|:---|
| **Accuracy** | 0.7282 | **0.6537** | Balanced trade-off for surfacing preferred options |
| **Precision** | 0.5737 | **0.4323** | Satisfies $\ge 0.42$ business constraint |
| **Recall** | 0.2382 | **0.6265** | **+163.0% recovery** (3,759 preferred journeys vs 1,429) |
| **F1-Score** | 0.3366 | **0.5116** | **+52.0% harmonic improvement** |
| **ROC-AUC** | 0.6976 | **0.6976** | Consistent ranking concordance across thresholds |

---

## 5. Reproduction & Verification Commands

All phases can be executed and audited directly using the provided CLI modules:

```bash
# 1. Verify raw data source integrity & SHA-256 hashes
python -m src.data_collection

# 2. Run canonical data cleaning and transit graph construction
python -m src.data_cleaning

# 3. Run the 5-tier statistical, structural, and econometric validation suite
python -m src.validation

# 4. Train and evaluate baseline model families (70/15/15 split)
python -m src.phase4_baseline

# 5. Run threshold optimization and serialize the champion pipeline
python -m src.phase4_step2

# 6. Render all 35 publication-grade formula panels and evaluation table cards
python -m src.generate_evidence_assets

# 7. Generate the 12-slide executive presentation deck
python -m src.generate_presentation

# 8. Load the serialized champion artifact and test live inference
python -c "from src.train_models import load_champion_pipeline; engine = load_champion_pipeline(); print(engine.metadata)"
```

---

## 6. Key Deliverables & Reports

- **Final Quality Control & Freeze Report**: [`reports/final/final_quality_control_report.md`](reports/final/final_quality_control_report.md)
- **Master Comprehensive Technical Report**: [`reports/final/final_comprehensive_report.md`](reports/final/final_comprehensive_report.md)
- **Viva Defense Guide (20 Questions & Answers)**: [`reports/final/viva_questions_and_answers.md`](reports/final/viva_questions_and_answers.md)
- **Presentation Deck**: [`reports/final/Yatra_AI_Final_Presentation.pptx`](reports/final/Yatra_AI_Final_Presentation.pptx)
- **Serialized Champion Model**: [`results/models/champion_gb_core.joblib`](results/models/champion_gb_core.joblib)

---

## 7. Scientific Boundary Statement

> *The behavioural labels in this study originate from a documented synthetic Multinomial Logit (MNL) simulation grounded in authentic Indian transit supply networks rather than observed micro-level human choice ground truth. Therefore, the machine learning results demonstrate the feasibility, ranking fidelity, and structural integrity of the personalization pipeline under stated simulation assumptions, rather than universal real-world empirical behavioral validity.*
