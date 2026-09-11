# YĀTRĀ AI: Complete Project Lifecycle Walkthrough & Technical Audit
## Multi-Modal Intelligent Travel Recommendation System for India

**Lead System**: Yātrā AI (यात्रा AI)  
**Status**: COMPLETE, FROZEN & REPRODUCIBLE (Seed: 42)  
**Academic Phase**: Phase 1 through Phase 5 Comprehensive Walkthrough  
**Date**: September 2026  

---

## 1. Project Lifecycle Overview

The Yātrā AI research initiative was executed across five sequential, rigorous engineering and machine learning phases:

```
+-----------------------------------------------------------------------------+
|                           YĀTRĀ AI 5-PHASE LIFECYCLE                        |
+-----------------------------------------------------------------------------+
| PHASE 1: Real-World Public Data Sourcing & Inventory                        |
|   * Sourced 8,400+ railway stations & 11,100+ train schedules (JSON)        |
|   * Acquired 300,000+ domestic flight fares & historical delay distributions|
|   * Sourced IMD high-resolution gridded monthly rainfall archives           |
+-----------------------------------------------------------------------------+
| PHASE 2: Data Normalization, Join Strategy & ML Problem Formulation         |
|   * Established canonical metro corridor mapping (haversine clustering)     |
|   * Formulated provider-independent multi-modal transit schemas             |
|   * Defined ML task: Binary classification on alternative selection (chosen)|
+-----------------------------------------------------------------------------+
| PHASE 3: Synthetic Traveller Behaviour & Travel DNA Generation              |
|   * Generated 5,000 unique traveller profiles with 7-D continuous Travel DNA|
|   * Synthesized 40,000 multi-modal search sessions across 6 metro corridors |
|   * Generated 138,603 itinerary rows with Multinomial Logit (MNL) choices   |
|   * Passed 5/5 automated validation suites (statistical, axiom, sensitivity)|
+-----------------------------------------------------------------------------+
| PHASE 4: Supervised ML Experimentation & Threshold Optimization             |
|   * Step 1: Pre-training leakage audit & 70/15/15 traveller-level split    |
|             Trained 4 model families across Core (28) & Extended (29) sets  |
|   * Step 2: Decision-threshold optimization strictly on validation data     |
|             Selected Gradient Boosting Core (GB_core) at tau = 0.30         |
|             Surged Test Recall from 23.8% to 62.7% (F1: 0.3366 -> 0.5116)  |
+-----------------------------------------------------------------------------+
| PHASE 5: Final Synthesis, Comprehensive Reports & Submission Package         |
|   * Master 22-section academic research report (final_report.md)            |
|   * Executive summary, limitations, presentation outline, and viva guide    |
|   * Machine-readable results and feature importance tables                  |
+-----------------------------------------------------------------------------+
```

---

## 2. Phase-by-Phase Verification & Key Deliverables

### Phase 1: Real / Public Operational Data Foundation
- **Objective**: Build a supply-side transit foundation grounded in real-world Indian infrastructure.
- **Key Artifacts**:
  - `data/raw/railway/stations.json` (8,400+ Indian railway stations with GPS coordinates)
  - `data/raw/railway/trains.json` (11,100+ train services and route schedules)
  - `data/raw/flights/` (300,000+ domestic flight itinerary records across Indian metros)
  - `data/raw/railway/delays/` (Historical category delay distributions)
  - `data/raw/weather/` (IMD monthly gridded precipitation)
- **Documentation**: [`docs/phase1_report.md`](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/docs/phase1_report.md), [`docs/data_sources.md`](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/docs/data_sources.md).

### Phase 2: Data Normalization & ML Problem Definition
- **Objective**: Link heterogeneous datasets legitimately without fabricated micro-joins and specify canonical schemas.
- **Key Outcomes**:
  - Identified legitimate join keys: `Metro Region` (Origin/Destination) and `Time / Season`.
  - Formulated provider-independent canonical schemas for Stations, Routes, Flights, Delays, and Weather.
  - Specified the primary ML task: Binary classification on alternative selection (`chosen` $\in \{0, 1\}$).
- **Documentation**: [`docs/phase2_report.md`](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/docs/phase2_report.md), [`docs/dataset_join_strategy.md`](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/docs/dataset_join_strategy.md), [`docs/data_dictionary.md`](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/docs/data_dictionary.md).

### Phase 3: Synthetic Traveller Behaviour & Travel DNA
- **Objective**: Implement demand-side microeconomic choice simulation to generate discrete choice labels.
- **Key Outcomes**:
  - 5,000 travellers generated across 6 demographic persona archetypes.
  - 40,000 multi-modal search sessions (8 per traveller).
  - 138,603 multi-modal candidate alternatives (min 2, max 5, mean 3.465 per session).
  - Passed 5 automated validation suites: Structural integrity, statistical mean deltas $\le 0.0102$, MNL axiom verification to $3.33 \times 10^{-16}$, 6/6 behavioral sensitivity tests, and bitwise reproducibility (Seed 42).
- **Frozen Datasets & Cryptographic Hashes**:
  - `choice_dataset.parquet`: `43a49778bc01703f021283e4ce7340b5e0fb55f0324e619d62af5d2200876161`
  - `choice_dataset.csv`: `878b2b65cc96d3ef331c7983460dfefcc4f574a77e2306927688aa783e4df718`
- **Documentation**: [`docs/synthetic_data_methodology.md`](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/docs/synthetic_data_methodology.md), [`docs/synthetic_data_validation.md`](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/docs/synthetic_data_validation.md).

### Phase 4: Supervised ML Experimentation & Model Selection
- **Objective**: Train leakage-safe baselines and optimize decision thresholds.
- **Key Outcomes**:
  - **Step 1 Baseline**: Evaluated Logistic Regression, Decision Tree, Random Forest, and HistGradientBoosting across Core (28 features) and Extended (29 features) sets. Proved that tree models outperform linear models by +47.2% F1, and confirmed that `persona_type` adds negligible value over continuous Travel DNA traits ($\Delta \text{AUC} \le 0.0005$).
  - **Step 2 Optimization**: Evaluated decision thresholds strictly on validation data. Identified $\mathbf{\tau^* = 0.30}$ as optimal for `Gradient Boosting Core (GB_core)`.
  - **Final Champion Performance (Test Set)**:
    - **Test ROC-AUC**: **0.6976**
    - **Test F1 Score**: **0.5116** (+52.0% gain over baseline 0.3366)
    - **Test Recall**: **62.65%** (+38.83% pts gain over baseline 23.82%)
    - **Test Accuracy**: **65.37%**
    - **Generalization Gap**: Minimal train-test AUC gap of **0.0235**.
- **Documentation & Visuals**:
  - [`reports/phase4/model_metrics_table.csv`](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/reports/phase4/model_metrics_table.csv)
  - [`reports/phase4/final_model_comparison.csv`](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/reports/phase4/final_model_comparison.csv)
  - [`reports/phase4/threshold_comparison.png`](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/reports/phase4/threshold_comparison.png)
  - [`reports/phase4/final_confusion_matrix.png`](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/reports/phase4/final_confusion_matrix.png)

### Phase 5: Final Submission Package & Synthesis
- **Objective**: Synthesize all research findings into an academically defensible, structured package.
- **Key Deliverables in `reports/final/`**:
  1. [`reports/final/final_report.md`](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/reports/final/final_report.md) (Full 22-section research report)
  2. [`reports/final/executive_summary.md`](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/reports/final/executive_summary.md) (Executive overview)
  3. [`reports/final/final_results_table.csv`](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/reports/final/final_results_table.csv) (Champion model default vs. tuned metrics)
  4. [`reports/final/model_comparison_table.csv`](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/reports/final/model_comparison_table.csv) (Comprehensive 11-model comparison table)
  5. [`reports/final/feature_importance_summary.csv`](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/reports/final/feature_importance_summary.csv) (Feature importance and regression coefficients)
  6. [`reports/final/limitations_and_future_work.md`](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/reports/final/limitations_and_future_work.md) (Research boundaries and roadmap)
  7. [`reports/final/presentation_outline.md`](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/reports/final/presentation_outline.md) (12-slide viva presentation guide)
  8. [`reports/final/viva_questions_and_answers.md`](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/reports/final/viva_questions_and_answers.md) (20-question oral defense guide)

---

## 3. Final Quality & Consistency Verification
- [x] **No Fabricated Metrics**: All metrics match exact computed outputs from `src/phase4_step2.py` and `src/phase4_baseline.py`.
- [x] **Zero Dataset Drift**: Phase 3 datasets verified bitwise identical against initial hashes.
- [x] **Zero Test-Set Leakage**: Decision threshold ($\tau = 0.30$) was swept and locked exclusively using validation data before one-time test evaluation.
- [x] **Scientific Boundaries Respected**: Target `chosen` explicitly documented as synthetic simulation ground truth; no claims of real-world booking conversions.
- [x] **Reproducibility Guarantee**: Complete pipeline executable via Seed 42.

**Project Status: Phase 5 Complete. Yātrā AI Machine Learning Research Track Frozen & Finalized.**
