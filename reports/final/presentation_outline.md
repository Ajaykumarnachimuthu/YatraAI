# YĀTRĀ AI: Academic Presentation Slide Outline
## Multi-Modal Intelligent Travel Recommendation System for India

**Total Slides**: 12  
**Presentation Time**: 15–20 minutes  
**Target Audience**: Academic Viva Committee / ML Evaluation Panel  

---

### Slide 1: Title & Project Identification
- **Title**: YĀTRĀ AI (यात्रा AI)
- **Subtitle**: A Personalized Multi-Modal Travel Itinerary Recommendation Engine for India Using Hybrid Grounded Data
- **Key Concepts**: Hybrid Data Strategy, Travel DNA Psychometrics, Multinomial Logit Simulation, Machine Learning Classification, Decision-Threshold Optimization
- **Reproducibility**: Python 3.11, scikit-learn, Deterministic Seed 42, Zero Post-Choice Data Leakage

---

### Slide 2: The Real-World Problem
- **Fragmentation in Indian Transit**: Separate, disconnected booking systems for rail (IRCTC) and commercial aviation.
- **The Information Overload Dilemma**: Travellers cannot easily compare true door-to-door transit time, dynamic pricing, transfer friction, delay probability, and carbon emissions.
- **Absence of Personalization**: Standard OTAs sort purely by price or departure time; they cannot capture nuanced multi-attribute trade-offs (e.g., budget backpacker vs. executive business traveller).

---

### Slide 3: The Yātrā AI Solution
- **Multi-Modal Candidate Engine**: Evaluates flight, express rail, premium rail, and multi-segment itineraries across high-density Indian intercity corridors.
- **Travel DNA Personalization**: Models individual preferences across 8 continuous dimensions: cost, time, reliability, comfort, transfer tolerance, departure flexibility, sustainability, and loyalty.
- **Normalized Candidate Scoring**: Scores each itinerary alternative relative to the specific search session's choice set bounds.

---

### Slide 4: Hybrid Data Architecture
- **Why Hybrid?**: Zero public access to real Indian multi-modal booking transactions due to commercial privacy constraints.
- **Grounded Public Transit Foundation (100% Real)**:
  - 8,400+ Railway Stations & 11,100+ Train Timetables (JSON)
  - 300,000+ Domestic Flight Fares & Schedules
  - Historical Indian Railways delay distributions & IMD climate rainfall baselines
- **Synthetic Behavioral Ground Truth**:
  - 5,000 unique traveller profiles & 40,000 search occasions
  - 138,603 discrete choice rows generated via Multinomial Logit (MNL) simulation

---

### Slide 5: Synthetic Behavioural Methodology & MNL Formulation
- **Utility-Maximizing Agent Simulation**:
  $$U_{ni} = V_{ni} + \epsilon_{ni}, \quad V_{ni} = \sum_{k} \beta_k \cdot \text{DNA}_{nk} \cdot \text{Score}_{nik}$$
  $$\epsilon_{ni} \sim \text{Gumbel}(0, 1) \implies P_{ni} = \frac{\exp(V_{ni})}{\sum_j \exp(V_{nj})}$$
- **Validation Rigor**: Passed 5 automated validation suites (structural, statistical mean deltas < 0.0102, MNL axiom verification to machine epsilon $3.33 \times 10^{-16}$, 6/6 behavioral sensitivity tests, and bitwise reproducibility).

---

### Slide 6: Exploratory Data Analysis (EDA) Highlights
- **Class Imbalance**: 28.86% Chosen (40,000) vs. 71.14% Not Chosen (98,603) — natural 2.465 : 1 ratio reflecting 1 choice among 2–5 candidates per session.
- **Travel DNA Correlation Reality**: Aggregate correlation between cost and time sensitivity is moderate ($r \approx -0.63$), reflecting persona mixture sampling; intra-persona dimensions are sampled independently.
- **Modal Distribution**: Balanced split across simulated choice occasions (52.2% Rail vs. 47.8% Flight).

---

### Slide 7: Supervised ML Formulation & Zero-Leakage Architecture
- **Supervised Task**: Binary classification predicting alternative selection (`chosen` $\in \{0, 1\}$).
- **Traveller-Level Partitioning**: 70% Train (3,500 travellers / 97,163 rows), 15% Validation (750 travellers / 20,715 rows), 15% Test (750 travellers / 20,725 rows).
- **Strict Leakage Audit**: Excluded `choice_probability`, `utility`, `rank`, and entity keys (`session_id`, `traveller_id`).
- **Pre-Choice Candidate Scores**: Verified mathematically that `cost_score`, `time_score`, `reliability_score`, etc., are strictly pre-choice attributes computed prior to discrete choice sampling.

---

### Slide 8: Baseline Models & Comparative Analysis
- **Four Model Families Evaluated**: Logistic Regression, Decision Tree, Random Forest, HistGradientBoosting across Core (28 features) and Extended (29 features) sets.
- **Key Finding 1 — Non-Linearity Wins**: Tree models achieve +47.2% relative F1 gain over Logistic Regression because discrete choice utility is bilinear ($\beta \cdot \text{DNA} \cdot \text{Score}$).
- **Key Finding 2 — Persona Redundancy**: `persona_type` adds negligible predictive gain ($\Delta \text{AUC} \le 0.0005$) because continuous Travel DNA traits already supply complete, granular coordinates.
- **Key Finding 3 — Candidate Scores Dominate**: Relative scores represent 51.96% of total feature importance, out-predicting raw physical attributes by 2.3x.

---

### Slide 9: The Decision-Threshold Optimization
- **The Problem**: Default threshold $\tau = 0.50$ produces high accuracy (~72.8%) but severe positive recall deficit (23.82%), missing 76% of itineraries travellers wanted.
- **Validation-Only Tuning**: Swept $\tau \in [0.20, 0.60]$ strictly on validation data. Selected $\mathbf{\tau^* = 0.30}$ using validation F1 and false-positive tie-breaker rule.
- **One-Time Test Application**:
  - Test F1: **0.3366 $\to$ 0.5116 (+52.0% relative gain)**
  - Test Recall: **23.82% $\to$ 62.65% (+38.83% pts)**
  - False Negatives: **4,571 $\to$ 2,241 (slashed by -50.97%)**
  - Test ROC-AUC: **0.6976 (invariant)**

---

### Slide 10: Final Model Selection: Gradient Boosting Core (`GB_core`)
- **Champion Architecture**: `HistGradientBoostingClassifier` on Core 28 features at $\tau^* = 0.30$.
- **Why Not Random Forest?**: RF has higher train-test AUC overfit gap ($\Delta = 0.0848$ vs. $0.0235$) and produces 1,500+ more false alarms at its tuned threshold ($\tau=0.25$).
- **Why Not Extended Model?**: Core model achieves higher test generalization F1 (0.5116 vs. 0.5105) with fewer features and eliminates unnecessary persona pipeline coupling.
- **Operational Profile**: Sub-millisecond inference latency, < 1.5 MB memory footprint.

---

### Slide 11: Limitations & Future Roadmap
- **Synthetic Ground Truth Boundary**: Target labels represent simulated utility maximizers, not real consumer booking receipts.
- **Public Data Proxies**: Flight punctuality baselines and rail fare tables are calibrated approximations.
- **Pointwise vs. Listwise Constraint**: The binary classifier treats alternatives independently; it does not explicitly enforce the session constraint that exactly one option is chosen.
- **Future Roadmap**: Transition to Session-Aware Learning-to-Rank (LightGBM Ranker / LambdaMART), live API integration (IRCTC/Airline GDS), and multimodal first-mile/last-mile graph routing.

---

### Slide 12: Conclusion & Summary Takeaways
- **What Was Built**: An end-to-end, reproducible multi-modal recommendation engine grounded in Indian transit data.
- **Core ML Outcome**: Successfully demonstrated the recovery of simulated utility preferences using tree-based gradient boosting, achieving **0.6976 ROC-AUC** and **0.5116 F1** at $\tau = 0.30$.
- **Scientific Conclusion**: Relative choice-set scoring and continuous psychometrics form the optimal feature architecture for personalized travel recommendations.
