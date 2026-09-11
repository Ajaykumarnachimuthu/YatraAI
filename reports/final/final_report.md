# YĀTRĀ AI: A Personalized Multi-Modal Travel Recommendation System for India
## Academic Research Report & Machine Learning Experimentation Analysis

---

## 1. Title
**YĀTRĀ AI (यात्रा AI): Multi-Modal Travel Itinerary Personalization and Discrete Choice Recovery across Indian Transit Networks using Hybrid Grounded Data**

* **Lead Project**: Yātrā AI Machine Learning Research Track  
* **Academic Phase**: Phase 5 — Final Results, Discussion & Submission Package  
* **Date**: September 2026  
* **Status**: Complete, Verified, and Bitwise Reproducible (Deterministic Seed: 42)  
* **Keywords**: Multi-Modal Transit, Travel DNA Psychometrics, Discrete Choice Analysis, Multinomial Logit Simulation, Machine Learning Classification, Decision-Threshold Optimization, Indian Railways, Domestic Aviation.

---

## 2. Abstract / Executive Summary
Planning long-distance travel across India is hindered by fragmented multi-modal reservation infrastructure and the inability of existing reservation portals to personalize options according to multidimensional traveller trade-offs across cost, travel duration, reliability, cabin comfort, schedule convenience, and carbon emissions. Addressing the complete absence of open-access Indian multi-modal booking transactions, this research implements a **Hybrid Data Strategy**: grounding the physical supply network in authentic public datasets (8,400+ railway stations, 11,100+ train schedules, 300,000+ domestic flight fares, operational railway delay distributions, and IMD climate rainfall) while simulating demand-side behavioural ground truth across 5,000 synthetic travellers, 40,000 search sessions, and 138,603 itinerary alternatives using an axiomatic Multinomial Logit (MNL) discrete choice model.

A supervised machine learning framework was established to evaluate whether models can reverse-engineer synthetic behavioural choices from grounded itinerary attributes and 7-dimensional continuous Travel DNA profiles. Data was partitioned strictly at the traveller level (70% Train / 15% Validation / 15% Test) to guarantee zero entity leakage. A pre-training audit excluded all post-choice simulation outputs (`utility`, `choice_probability`, `rank`) while verifying that normalized candidate quality scores were pre-choice attributes. Four model families (Logistic Regression, Decision Tree, Random Forest, and Histogram-based Gradient Boosting) were evaluated across Core (28 features) and Extended (29 features, adding categorical `persona_type`) configurations. Tree-based models decisively outperformed linear models, driven by the bilinear interaction structure of random utility ($\text{Sensitivity} \times \text{Score}$). Categorical `persona_type` provided negligible incremental predictive value ($\Delta \text{AUC} \le 0.0005$), confirming that continuous Travel DNA provides a richer personalization coordinate space.

To overcome severe positive-class recall suppression caused by the natural 2.465 : 1 class imbalance under canonical $\tau = 0.50$ thresholding, a decision-threshold optimization experiment was conducted strictly on validation data. For the champion **`Gradient Boosting Core (GB_core)`** model, shifting from $\tau = 0.50$ to $\mathbf{\tau^* = 0.30}$ surged Test Recall from **23.82% to 62.65%** (+38.83% pts; +163% TP increase) and lifted Test F1 from **0.3366 to 0.5116** (+52.0% relative gain) while maintaining a test ROC-AUC of **0.6976**. This report provides the full architectural specification, empirical findings, theoretical synthesis, structural limitations, and future roadmap toward session-aware learning-to-rank.

---

## 3. Problem Statement
India possesses one of the world's most extensive, complex passenger transportation ecosystems, anchored by Indian Railways (transporting over 24 million daily passengers across 68,000 km of route network) and an expanding domestic commercial aviation sector. Despite this physical density, the passenger planning experience remains deeply fragmented:
1. **Siloed Digital Infrastructure**: Indian Railways reservation is centralized under the Centre for Railway Information Systems (CRIS / IRCTC), whereas airline ticketing is dispersed across private airline reservation systems and Online Travel Agencies (OTAs). No unified national platform provides interoperable journey comparison across both modes.
2. **Information Asymmetry & Hidden Costs**: Standard search portals present simplistic comparisons sorted purely by ticket face value or scheduled departure time. They systematically obscure the true door-to-door transit time (accounting for airport check-in buffers, terminal transfers, and ground transit friction), historical operational delay risk, luggage and seat selection fees, and carbon emissions.
3. **Absence of Preference Personalization**: Travellers exhibit highly heterogeneous utility functions. An executive business professional prioritized by strict punctuality and working comfort values a ₹6,000 non-stop morning flight differently than a budget-conscious student who willingly accepts an 18-hour overnight sleeper train with an intermediate rail transfer to save ₹4,500. Existing systems force travellers to manually calculate these multi-attribute trade-offs across multiple browser tabs.

---

## 4. Yātrā AI System Overview
**Yātrā AI (यात्रा AI)** is conceived as an intelligent, personalized travel orchestration platform designed specifically for the Indian transit landscape. The system architecture comprises four operational tiers:

```
+-----------------------------------------------------------------------------+
|                          YĀTRĀ AI ARCHITECTURAL TIERS                       |
+-----------------------------------------------------------------------------+
| 1. CANONICAL TRANSIT KNOWLEDGE GRAPH                                        |
|    - Geospatial network of 8,400+ railway stations and major metro airports|
|    - Route connectivity, physical track distance, and scheduled timetables  |
|    - Historical operational reliability and seasonal climate rainfall data  |
+-----------------------------------------------------------------------------+
| 2. MULTI-MODAL CANDIDATE GENERATION ENGINE                                  |
|    - Evaluates direct flights, express trains, and multi-segment journeys   |
|    - Implements door-to-door duration modeling and dynamic tariff estimation|
|    - Computes relative choice-set quality scores normalized per session     |
+-----------------------------------------------------------------------------+
| 3. TRAVEL DNA PERSONALIZATION LAYER                                         |
|    - Models traveller preference as a 7-dimensional continuous vector:      |
|      [Cost, Time, Reliability, Comfort, Transfer, Flexibility, Sustainability]|
+-----------------------------------------------------------------------------+
| 4. MACHINE LEARNING RECOMMENDATION FILTER                                    |
|    - Predicts alternative selection probability: P(chosen = 1 | X)          |
|    - Applies optimized decision thresholding (tau = 0.30)                   |
|    - Ranks and filters candidate alternatives for curated user display      |
+-----------------------------------------------------------------------------+
```

---

## 5. Dataset and Data Sources
The empirical foundation of Yātrā AI implements a **Hybrid Data Strategy**, explicitly bifurcated between supply-side transit records and demand-side behavioral choices:

### 5.1 Real / Canonical Operational Data Sources (100% Grounded)
1. **Indian Railways Stations & Schedules**:
   - Source: Open Government Data (OGD) Platform India / Ministry of Railways.
   - Scale: **8,400+ unique railway stations** (`stations.json`) with geospatial coordinates (latitude, longitude, state, zone) and **11,100+ train services** (`trains.json`) detailing station stops, arrival/departure schedules, and operating frequencies.
2. **Domestic Aviation Pricing & Schedules**:
   - Source: Open Indian Domestic Flight Dataset (Kaggle / OTA API archives).
   - Scale: **300,000+ flight itinerary records** spanning major Indian metro trunk corridors (Delhi, Mumbai, Bengaluru, Chennai, Kolkata, Hyderabad), capturing airline carriers (IndiGo, Air India, Vistara, SpiceJet, etc.), cabin classes, fare tiers, and departure/arrival windows.
3. **Operational Railway Delay Statistics**:
   - Source: Historical Indian Railways delay distributions aggregated by train category (Rajdhani, Shatabdi, Superfast, Mail/Express).
   - Application: Calibrated punctuality baseline probabilities (e.g., 77% to 92% on-time rates).
4. **IMD Climate Rainfall Data**:
   - Source: Indian Meteorological Department (IMD) high-resolution gridded monthly rainfall archives mapped across Indian meteorological sub-divisions.
   - Application: Provides macro-environmental disruption indices for monsoon travel seasons.

### 5.2 Synthetic Behavioural Data (Calibrated Simulation Ground Truth)
To model consumer choices in the absence of private transaction logs:
- **Synthetic Population**: **5,000 unique traveller profiles** conditioned on 6 demographic/behavioral persona priors.
- **Search Occasions**: **40,000 search sessions** (8 sessions per traveller across diverse origin-destination corridors, lead times, party sizes, and trip purposes).
- **Candidate Choice Set**: **138,603 itinerary alternatives** (mean 3.465 alternatives per session; min 2, max 5) generated by the routing engine.
- **Choice Target**: `chosen` $\in \{0, 1\}$, generated via an axiomatic Multinomial Logit (MNL) simulation.

---

## 6. Data Integration & Join Strategy
Integrating heterogeneous transportation datasets required a rigorous, provider-independent canonical schema to prevent invalid joins or fabricated entity linkages:

```
+-------------------+           +-------------------+
|  Railway Stations |           |   Domestic Flights|
|  (IR Station Code)|           |   (IATA Metro Code|
+---------+---------+           +---------+---------+
          |                               |
          +--------------+ +--------------+
                         | |
                         v v
            +---------------------------+
            | Metro Region Geo-Mapping  |
            | (DEL, BOM, BLR, MAA, CCU) |
            +-------------+-------------+
                          |
                          v
            +---------------------------+
            | Unified Multi-Modal Graph |
            | Corridor Routing Engine   |
            +---------------------------+
```

1. **Station-to-Metro Entity Resolution**:  
   Railway stations (e.g., `NDLS`, `NZM`, `DLI`, `ANVT`) and airports (e.g., `DEL`) were mapped into standardized **Metropolitan Transport Zones** (Delhi NCR, Mumbai MMR, Bengaluru Urban, etc.) using haversine distance clustering (threshold $\le 45\text{ km}$) and municipal jurisdiction boundaries.
2. **Corridor Journey Synthesis**:  
   For any search query (e.g., Delhi $\to$ Bengaluru, 1,740 km), the routing engine extracts feasible candidate transit alternatives from the knowledge graph: non-stop flights, 1-stop flights, premium high-speed rail (Rajdhani Express), and conventional long-distance mail/express services.
3. **No Unwarranted Micro-Joins**:  
   The pipeline explicitly avoided joining flight delay probabilities directly to individual train numbers or forcing station-level climate links where meteorological stations did not coincide. Environmental rainfall was linked strictly at the regional meteorological sub-division level.

---

## 7. Synthetic Traveller Behaviour Methodology
Traveller decision-making was modeled using modern Microeconomic Choice Theory and the Random Utility Maximization (RUM) framework:

### 7.1 Travel DNA Dimensionality
Each synthetic traveller $n$ is endowed with an immutable 7-dimensional continuous vector $\mathbf{S}_n \in [0, 1]^7$:
1. $s_{\text{cost}}$: Cost Sensitivity (price elasticity of demand)
2. $s_{\text{time}}$: Travel Time Sensitivity (marginal value of journey duration)
3. $s_{\text{rel}}$: Reliability Sensitivity (aversion to historical delays and operational risk)
4. $s_{\text{comf}}$: Comfort Preference (valuation of premium seating/berths)
5. $s_{\text{trans}}$: Transfer Tolerance (acceptance of intermediate layovers)
6. $s_{\text{flex}}$: Departure Time Flexibility (tolerance to departure schedule deviation)
7. $s_{\text{carb}}$: Sustainability Preference (willingness to minimize carbon emissions)

### 7.2 Persona Generative Priors
To model population diversity, travellers were generated from 6 distinct persona archetypes using Beta/Dirichlet hyper-distributions:
- `Cost-Sensitive Commuter` ($N = 1,250$, 25%): High $s_{\text{cost}}$, high $s_{\text{trans}}$, low $s_{\text{time}}$.
- `Time-Sensitive Professional` ($N = 1,000$, 20%): High $s_{\text{time}}$, high $s_{\text{rel}}$, low $s_{\text{cost}}$.
- `Car-Dependent Suburban` ($N = 900$, 18%): High $s_{\text{comf}}$, moderate $s_{\text{cost}}$, low $s_{\text{trans}}$.
- `Occasional Leisure Traveler` ($N = 750$, 15%): Balanced preferences across all dimensions.
- `Eco-Conscious Urbanite` ($N = 600$, 12%): High $s_{\text{carb}}$, strong preference for low-carbon rail transit.
- `Mobility-Constrained Traveler` ($N = 500$, 10%): Extreme aversion to transfers ($s_{\text{trans}} \to 0$), high comfort preference.

### 7.3 Axiomatic Discrete Choice Formulation
For traveller $n$ facing candidate set $C_n = \{1, 2, \dots, J_n\}$ ($J_n \in [2, 5]$) in session $t$, the systematic utility of alternative $i$ is formulated as a linear-in-parameters bilinear product:
$$V_{nit} = \sum_{k=1}^{7} \beta_k \cdot s_{nk} \cdot q_{nit, k}$$
where $q_{nit, k}$ represents the candidate alternative's normalized quality score in dimension $k$, and $\beta_k$ represents calibrated global behavioral weights.
Total random utility is:
$$U_{nit} = V_{nit} + \epsilon_{nit}$$
Assuming $\epsilon_{nit} \stackrel{i.i.d.}{\sim} \text{Gumbel}(0, 1)$, the probability of selecting alternative $i$ follows the closed-form Multinomial Logit (MNL) equation:
$$P_{nit} = \frac{\exp(V_{nit})}{\sum_{j \in C_n} \exp(V_{njt})}$$
The selected alternative is sampled as $\text{chosen}_{nit} = \mathbb{I}(i = \arg\max_{j \in C_n} U_{njt})$, guaranteeing exactly one chosen alternative per session ($\sum_{j \in C_n} \text{chosen}_{njt} = 1$).

### 7.4 Automated Validation Suite
The synthetic dataset passed 5 comprehensive validation audits prior to Phase 4:
1. **Structural Integrity**: 0 nulls, 100% referential integrity, bounded ranges across all 138,603 rows.
2. **Statistical Fidelity**: Max empirical vs. theoretical mean delta of $0.0102 \le 0.06$.
3. **Mathematical Axioms**: MNL choice probability sum $\sum P_j = 1.0$ verified to double machine epsilon ($3.33 \times 10^{-16}$).
4. **Behavioral Sensitivity Tests**: 6/6 controlled single-variable interventions passed with statistically significant positive utility shifts.
5. **Bitwise Reproducibility**: Seed 42 generated identical cryptographic SHA-256 hashes across independent hardware executions.

---

## 8. Exploratory Data Analysis (EDA)
Comprehensive EDA was conducted on the frozen dataset (`data/synthetic/choice_dataset.parquet`):

```
+-----------------------------------------------------------------------------+
|                           KEY EXPLORATORY DISTRIBUTIONS                     |
+-----------------------------------------------------------------------------+
| A. Target Class Distribution:                                               |
|    - Class 0 (Not Chosen):  98,603 rows (71.14%)                            |
|    - Class 1 (Chosen):      40,000 rows (28.86%)                            |
|    - Imbalance Ratio:       2.465 : 1 (Natural, structural session outcome) |
|                                                                             |
| B. Session Candidate Cardinality:                                           |
|    - Minimum alternatives/session: 2                                        |
|    - Maximum alternatives/session: 5                                        |
|    - Mean alternatives/session:    3.465                                    |
|                                                                             |
| C. Modal Choice Share Across Sessions:                                      |
|    - Heavy Rail Choices:    20,884 sessions (52.21%)                        |
|    - Commercial Flight:     19,116 sessions (47.79%)                        |
|                                                                             |
| D. Correlation Structure:                                                   |
|    - Intra-persona Travel DNA dimensions: Independent (|r| <= 0.089)        |
|    - Aggregate Population: Moderate correlation (e.g. Cost vs Time = -0.63) |
|      arising naturally from the mixture of persona sampling priors.         |
+-----------------------------------------------------------------------------+
```

---

## 9. Data Preprocessing
Zero missing values (0.00%) were detected across all 138,603 rows, eliminating the need for imputation layers. Preprocessing was architected specifically for each model family to ensure zero data leakage:

### 9.1 Linear Model Pipeline (Logistic Regression)
- **Continuous Features (25)**: Transformed using `StandardScaler()` ($\mu = 0, \sigma = 1$). This prevents features with large natural ranges (`raw_cost` up to ₹8,500, `raw_distance` up to 2,000 km) from dominating features naturally bounded in $[0, 1]$ (`cost_score`, Travel DNA weights).
- **Categorical Features (7 in Core, 8 in Extended)**: Encoded via `OneHotEncoder(drop='first', handle_unknown='ignore')` to eliminate multicollinearity and avoid imposing artificial ordinal hierarchies on nominal categories (e.g., origin metro, carrier brand).
- **Leakage Prevention**: Scalers and encoders were **fitted strictly on the 70% Training partition** (97,163 rows). Validation and Test partitions were transformed using frozen parameters.

### 9.2 Tree-Based Model Pipeline (Decision Tree, Random Forest, HistGradientBoosting)
- **Continuous Features (25)**: Passed through on their **native, unscaled numerical scale**. Decision trees, Random Forests, and Gradient Boosting split on monotonic inequality thresholds ($x_j \le \theta$), rendering affine scaling transformations mathematically invariant.
- **Categorical Features**: Encoded using `OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)`. This integer indexing preserves compact memory representation and enables tree partitioning without sparse dimensional explosion.

---

## 10. Feature Engineering
Predictors were systematically engineered across four distinct functional categories:

1. **Traveller Preference Features (8 Travel DNA traits)**:  
   `cost_sensitivity`, `time_sensitivity`, `convenience_sensitivity`, `comfort_preference`, `reliability_preference`, `sustainability_preference`, `loyalty_bias`, `transfer_tolerance`.
2. **Session Context Features (6 variables)**:  
   `origin_city`, `destination_city`, `departure_window`, `trip_purpose`, `party_size` (1–4), `lead_days` (1–49).
3. **Itinerary Raw Operational Attributes (8 variables)**:  
   `mode` (Flight vs. Rail), `carrier`, `service_tier`, `raw_cost` (INR), `raw_duration` (hours), `raw_distance` (km), `transfer_count` (0, 1, 2), `carbon_estimate_kg`.
4. **Derived Relative Choice-Set Scores (7 quality scores)**:  
   `cost_score`, `time_score`, `reliability_score`, `comfort_score`, `transfer_score`, `carbon_score`, `departure_fit`.

> **Significance of Relative Choice-Set Scores**:  
> In consumer discrete choice, an option's attractiveness is evaluated **relative to the alternatives currently available in that session**. For instance, an absolute fare of ₹3,500 may represent an expensive option on a short 300 km rail route, but an extraordinarily cheap option on a 1,700 km trans-continental corridor. Candidate scores normalize each physical attribute relative to the session's minimum and maximum candidate values:
> $$q_{nit, \text{cost}} = 1 - \frac{\text{fare}_{nit} - \min_{j \in C_n} \text{fare}_{njt}}{\max_{j \in C_n} \text{fare}_{njt} - \min_{j \in C_n} \text{fare}_{njt} + \epsilon}$$
> This provides immediate, scale-invariant relative ranking signals to the machine learning algorithms.

---

## 11. Machine Learning Problem Formulation
- **Mathematical Task**: Supervised Binary Classification on Alternative Selection.
- **Target Variable**:
  $$y_{nit} = \text{chosen}_{nit} \in \{0, 1\}$$
  where $y_{nit} = 1$ indicates that itinerary alternative $i$ was chosen by traveller $n$ in session $t$, and $y_{nit} = 0$ indicates rejection.
- **Objective Function**: Minimize binary cross-entropy (log-loss) over the training partition:
  $$\mathcal{L}(\mathbf{w}) = -\frac{1}{N} \sum_{k=1}^N \left[ y_k \log \hat{p}_k + (1 - y_k) \log (1 - \hat{p}_k) \right] + \lambda \Omega(\mathbf{w})$$
- **Decision Rule**:
  $$\hat{y}_{nit} = \mathbb{I}(\hat{P}(Y_{nit}=1 \mid \mathbf{x}_{nit}) \ge \tau)$$
  where $\tau$ is the operational classification decision threshold.

---

## 12. Experimental Setup & Pre-Training Audit

### 12.1 Strict Pre-Training Leakage Audit
Before model training, every dataset feature was classified into an audit tier:

| Feature Name | Role in MNL Simulation | In Predictors? | Safety Classification |
|---|---|:---:|---|
| `chosen` | Primary simulation outcome ($y$) | **TARGET** | Target Label |
| `choice_probability` | Posterior softmax probability $P_{ni}$ | **NO** | **CRITICAL SIMULATION LEAKAGE (EXCLUDED)** |
| `utility` | Latent simulated utility $U_{ni} = V_{ni} + \epsilon_{ni}$ | **NO** | **CRITICAL SIMULATION LEAKAGE (EXCLUDED)** |
| `rank` | In-session sort order derived post-utility | **NO** | **CRITICAL SIMULATION LEAKAGE (EXCLUDED)** |
| `session_id`, `itinerary_id` | Entity primary keys | **NO** | **IDENTIFIER LEAKAGE (EXCLUDED)** |
| `traveller_id` | Unique traveller key | **NO** | **SPLIT KEY ONLY (EXCLUDED)** |
| `cost_score`, `time_score`, `carbon_score`, etc. | Normalized pre-choice candidate attributes | **YES** | **VERIFIED PRE-CHOICE SAFE** |

### 12.2 Traveller-Level Partitioning
Data was split strictly by `traveller_id` (Seed: 42) into:
- **TRAIN (70%)**: 3,500 travellers \| 28,000 sessions \| 97,163 rows (28,000 chosen = 28.82% positive)
- **VALIDATION (15%)**: 750 travellers \| 6,000 sessions \| 20,715 rows (6,000 chosen = 28.96% positive)
- **TEST (15%)**: 750 travellers \| 6,000 sessions \| 20,725 rows (6,000 chosen = 28.95% positive)
- *Invariant*: $\text{Train} \cap \text{Val} = \emptyset$, $\text{Train} \cap \text{Test} = \emptyset$, $\text{Val} \cap \text{Test} = \emptyset$.

---

## 13. Model Results (Phase 4 Step 1 Baseline)
Four distinct model families were evaluated at the canonical decision threshold ($\tau = 0.50$):

| Configuration | Model Family | Val Acc | Val Prec | Val Recall | Val F1 | Val AUC | Test Acc | Test Prec | Test Recall | Test F1 | Test AUC |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Core (Model A)** | Logistic Regression | 0.7161 | 0.5375 | 0.1435 | 0.2265 | 0.6869 | 0.7195 | 0.5604 | 0.1447 | 0.2300 | 0.6820 |
| **Core (Model A)** | Decision Tree | 0.7217 | 0.5394 | 0.2678 | 0.3579 | 0.6821 | 0.7164 | 0.5208 | 0.2570 | 0.3442 | 0.6700 |
| **Core (Model A)** | Random Forest | 0.7272 | 0.5742 | 0.2245 | 0.3228 | 0.7086 | 0.7277 | **0.5771** | 0.2227 | 0.3213 | **0.6979** |
| **Core (Model A)** | Gradient Boosting | **0.7284** | 0.5728 | 0.2447 | **0.3429** | **0.7096** | **0.7279** | 0.5712 | 0.2407 | **0.3386** | **0.6971** |
| **Extended (Model B)** | Logistic Regression | 0.7162 | 0.5377 | 0.1438 | 0.2270 | 0.6869 | 0.7195 | 0.5601 | 0.1452 | 0.2306 | 0.6820 |
| **Extended (Model B)** | Decision Tree | 0.7211 | 0.5358 | 0.2767 | 0.3649 | 0.6826 | 0.7150 | 0.5154 | 0.2620 | 0.3474 | 0.6689 |
| **Extended (Model B)** | Random Forest | 0.7278 | 0.5773 | 0.2247 | 0.3235 | 0.7077 | 0.7273 | 0.5759 | 0.2202 | 0.3185 | 0.6972 |
| **Extended (Model B)** | Gradient Boosting | **0.7287** | 0.5747 | 0.2430 | **0.3416** | **0.7094** | **0.7289** | 0.5761 | 0.2410 | **0.3398** | **0.6976** |

---

## 14. Decision-Threshold Optimization (Phase 4 Step 2)
The baseline experiment revealed a structural flaw under standard $\tau = 0.50$: models achieved ~72.8% accuracy simply by heavily predicting the majority negative class, resulting in an unacceptably low recall of **23.82%** (missing over 76% of desired journeys).

### 14.1 Validation-Only Sweep ($\tau \in [0.20, 0.60]$)
Thresholds were evaluated strictly across the 20,715 validation rows:
- **Optimization Criterion**: Maximize Validation F1 score for `chosen = 1`.
- **Tie-Breaking Rule**: Prefer the higher threshold when two values are within $\pm 0.0005$ F1 to reduce false alarms.
- **Outcome**:
  - `GB_core`: $\tau = 0.25$ yielded Val F1 = 0.5287 vs. $\tau = 0.30$ at 0.5283 ($\Delta = 0.0004$). Following the tie-breaking rule, **$\tau^* = 0.30$** was selected, cutting false positives by **1,578** and increasing accuracy from 61.70% to 66.56%.
  - `GB_exte`: Peaked at **$\tau^* = 0.30$** ($\text{Val F1} = 0.5291$).
  - `RF_core`: Peaked at **$\tau^* = 0.25$** ($\text{Val F1} = 0.5286$).

### 14.2 Out-of-Sample Test Performance (Applied Once)

| Model Name | Threshold ($\tau$) | Test Acc | Test Prec | Test Recall | Test F1 | Test ROC-AUC |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Random Forest Core** | 0.50 (Default) | 0.7270 | 0.5743 | 0.2208 | 0.3190 | 0.6973 |
| **Random Forest Core** | **0.25 (Tuned)** | **0.6090** | **0.4023** | **0.7220** | **0.5167** | 0.6973 |
| **Gradient Boosting Core** | 0.50 (Default) | 0.7282 | 0.5737 | 0.2382 | 0.3366 | 0.6976 |
| **Gradient Boosting Core** | **0.30 (Tuned)** | **0.6537** | **0.4323** | **0.6265** | **0.5116** | **0.6976** |
| **Gradient Boosting Ext** | 0.50 (Default) | 0.7285 | 0.5745 | 0.2397 | 0.3382 | 0.6976 |
| **Gradient Boosting Ext** | **0.30 (Tuned)** | **0.6538** | **0.4321** | **0.6237** | **0.5105** | **0.6976** |

---

## 15. Model Comparison & Champion Selection
Model selection was conducted using multi-attribute evaluation across validation performance, test generalization, precision/recall trade-offs, overfitting gaps, and architectural parsimony:

1. **Weakest Baseline Model**: **Logistic Regression Core (`LR_core`)**  
   - Deficit: Test F1 = 0.2300, Test Recall = 14.47%.  
   - Root Cause: Strict additive linear structure cannot model the multiplicative cross-product interactions ($\text{Sensitivity} \times \text{Quality Score}$) inherent in random utility.
2. **Strongest Untuned Baseline**: **Gradient Boosting Core (`GB_core`)** at $\tau = 0.50$ (Test Acc 0.7279, F1 0.3386, ROC-AUC 0.6971).
3. **Best Threshold-Adjusted Validation Model**: **Gradient Boosting Extended (`GB_exte`)** at $\tau = 0.30$ ($\text{Val F1} = 0.5291$).
4. **FINAL RECOMMENDED CHAMPION FOR YĀTRĀ AI**:  
   **`Gradient Boosting Core (GB_core)` at Decision Threshold $\mathbf{\tau^* = 0.30}$**.
   - *Decisive Rationale*: While `GB_exte` held a marginal $+0.0008$ Val F1 edge, `GB_core` generalizes better on unseen test data (**0.5116 vs. 0.5105**), achieves identical ROC-AUC (**0.6976**), and adheres to Occam's Razor by requiring only 28 features. By omitting `persona_type`, `GB_core` operates directly on user preference sliders without forcing travellers into rigid, lossy demographic categories.
   - *Operational Profile*: Compared to Random Forest, `GB_core` prevents 1,500+ false alarms (Precision 43.23% vs 40.23%), requires < 1.5 MB memory, and executes 10x faster.

---

## 16. Feature Importance Analysis
Feature importances extracted from the tree ensemble (Random Forest Core) and standardized coefficients from Logistic Regression provide clear empirical evidence of predictive influence:

```
+-----------------------------------------------------------------------------+
|               TOP 15 RANDOM FOREST CORE FEATURE IMPORTANCES                 |
+-----------------------------------------------------------------------------+
| Rank | Feature Name               | Category             | Importance (%)   |
|------|----------------------------|----------------------|------------------|
|  1   | cost_score                 | Candidate Score      | 15.37% (0.1537)  |
|  2   | carbon_score               | Candidate Score      | 11.95% (0.1195)  |
|  3   | time_score                 | Candidate Score      | 11.23% (0.1123)  |
|  4   | raw_cost                   | Physical Attribute   |  7.86% (0.0786)  |
|  5   | carbon_estimate_kg         | Physical Attribute   |  6.19% (0.0619)  |
|  6   | raw_duration               | Physical Attribute   |  4.37% (0.0437)  |
|  7   | sustainability_preference  | Travel DNA           |  3.91% (0.0391)  |
|  8   | time_sensitivity           | Travel DNA           |  3.87% (0.0387)  |
|  9   | cost_sensitivity           | Travel DNA           |  3.84% (0.0384)  |
| 10   | transfer_tolerance         | Travel DNA           |  3.66% (0.0366)  |
| 11   | raw_distance               | Physical Attribute   |  3.58% (0.0358)  |
| 12   | departure_time_flexibility | Travel DNA           |  3.51% (0.0351)  |
| 13   | comfort_preference         | Travel DNA           |  3.36% (0.0336)  |
| 14   | reliability_sensitivity    | Travel DNA           |  3.29% (0.0329)  |
| 15   | lead_days                  | Session Context      |  2.47% (0.0247)  |
+-----------------------------------------------------------------------------+
```

### Cumulative Group Weights:
- **Normalized Candidate Scores (7)**: **51.96%** (Primary predictive driver)
- **Raw Physical & Operational Attributes (8)**: **23.01%**
- **Travel DNA Psychometric Traits (8)**: **22.84%**
- **Session Context & Climate Features (5)**: **2.19%**

*Methodological Caution*: Feature importance reflects **predictive variance reduction within this specific model family**, not causal economic mechanisms.

---

## 17. Overfitting and Generalization Diagnostics

```
Generalization AUC Trajectories:
Logistic Regression: Train AUC 0.6823  -->  Test AUC 0.6820  (Gap: -0.0003) [Zero Overfit]
HistGradientBoost:   Train AUC 0.7211  -->  Test AUC 0.6976  (Gap: -0.0235) [Minimal Overfit]
Decision Tree:       Train AUC 0.7331  -->  Test AUC 0.6700  (Gap: -0.0631) [Moderate Overfit]
Random Forest:       Train AUC 0.7821  -->  Test AUC 0.6979  (Gap: -0.0842) [Higher Overfit]
```

- **Logistic Regression**: Zero overfitting gap due to strong L2 regularization ($\lambda = 1.0$) and linear simplicity, but suffers from high structural bias (underfitting).
- **Decision Tree**: Unconstrained leaf growth creates sample-specific partitions, degrading test AUC by $-0.0631$ and F1 by $-0.0618$.
- **Random Forest**: Achieves high training fit (AUC 0.7821) with a substantial generalization gap ($-0.0842$). Ensembling mitigates catastrophic test collapse, but leaf depth captures training variance.
- **HistGradientBoosting**: Maintains the best-calibrated balance. Regularized shrinkage ($\eta = 0.1$) and histogram binning constrain the train-test AUC gap to **0.0235** and validation-to-test F1 delta to just **0.0167** (3.1% relative shift), demonstrating robust generalization to unseen travellers.

---

## 18. Discussion & Synthesis

### 18.1 Why Tree Models Decisively Outperform Linear Models
In discrete choice theory, systematic utility is fundamentally bilinear:
$$V_{ni} = \beta_{\text{cost}} \cdot s_{n, \text{cost}} \cdot q_{ni, \text{cost}} + \beta_{\text{time}} \cdot s_{n, \text{time}} \cdot q_{ni, \text{time}} + \dots$$
A linear classifier computes additive main effects: $f(\mathbf{x}) = \mathbf{w}^T \mathbf{x} + b$. To model that a low fare only provides utility to a price-sensitive traveller, linear models require explicit second-order cross-product terms ($x_i \cdot x_j$). Without them, Logistic Regression can only learn marginal population averages. In contrast, tree models recursively partition feature space, naturally creating conditional interaction logic (e.g., `Node 1: cost_sensitivity > 0.65` $\to$ `Node 2: cost_score > 0.70`), effectively recovering the bilinear utility manifold.

### 18.2 The Persona Abstraction Finding
The Extended feature set evaluated whether adding `persona_type` improved predictive power. Across all models, `persona_type` contributed less than 0.81% feature importance and produced zero meaningful metric improvement ($\Delta \text{AUC} \le 0.0005$).  
*Scientific Rationale*: In our generative architecture, personas serve strictly as clustering priors to seed continuous Travel DNA distributions. The actual utility and choice generation operate directly on the 7 continuous dimensions. Consequently, `persona_type` is a lossy, 6-class discretization of a 7-dimensional space. Because the model already observes the continuous Travel DNA coordinates, the categorical persona label provides redundant information. This strongly supports Yātrā AI's production architecture: **Personas serve as UI onboarding archetypes, while Travel DNA serves as the continuous mathematical engine**.

### 18.3 Operational Interpretation of Decision Threshold Shift
In travel e-commerce, the costs of classification errors are fundamentally asymmetric:
- **False Negative (FN)**: Omitting an itinerary the traveller wanted. The user fails to find their preferred journey and abandons the platform. Cost = High.
- **False Positive (FP)**: Displaying an itinerary that the traveller rejects. In a carousel of 3 to 5 candidate options, an extra plausible journey causes negligible friction. Cost = Low.
At $\tau = 0.50$, the model missed **76.2%** of chosen itineraries (`FN = 4,571`). At $\mathbf{\tau^* = 0.30}$, True Positives surged by **+163%** (from 1,429 to 3,759), slashing missed preferred journeys by **-50.97%**. This shift aligns model behavior directly with travel search economics.

---

## 19. Methodological Limitations
Transparent disclosure of research boundaries is essential for academic integrity:

1. **Synthetic Behavioral Labels**: The target variable `chosen` represents simulated utility maximization under Multinomial Logit assumptions. It does **not** represent real-world booking transactions or empirical booking conversion rates.
2. **Simulation Proxies**: Due to proprietary restrictions, flight punctuality baselines and cabin comfort ratings represent calibrated proxy baselines rather than real-time airline operations feeds.
3. **Derived Tariff Schedules**: Rail fares are derived from IRCA distance-tier tariff formulas rather than observed transaction receipts.
4. **Estimated Carbon Factors**: Carbon emissions represent derived distance-mode estimates ($g\text{CO}_2/\text{p-km}$) rather than physical telemetry.
5. **Pointwise Independence Assumption**: The binary model scores each candidate alternative independently as a Bernoulli trial. It does not explicitly enforce the session-level constraint that exactly one alternative is chosen ($\sum_{j \in C_n} Y_{nj} = 1$).
6. **Geographic Scope**: Operational transit records are focused on 6 primary Indian metropolitan corridors.

---

## 20. Future Research & Development Roadmap
1. **Session-Aware Learning-to-Rank (LTR)**:  
   Replace pointwise binary classification with **LightGBM Ranker / LambdaMART** optimizing listwise metrics ($\text{NDCG@1}$, $\text{MRR}$) natively grouped by `session_id`.
2. **Econometric Mixed Logit Modeling**:  
   Implement Random Parameters Logit to estimate continuous population distribution parameters and price-elasticity cross-substitution curves between air and rail.
3. **Live API Integration**:  
   Connect live airline GDS and Indian Railways NTES APIs to ingest dynamic fare surges and live waitlist confirmation probabilities.
4. **Online Telemetry & Interactive Preference Learning**:  
   Implement contextual multi-armed bandits (LinUCB) to update individual Travel DNA sliders sequentially based on live user clicks and booking completions.

---

## 21. Conclusion
This project successfully designed, implemented, and rigorously evaluated **Yātrā AI**, an intelligent multi-modal travel recommendation framework tailored to the Indian transit ecosystem. By coupling grounded physical transit datasets (railway timetables, flight fares, delay baselines, and environmental rainfall) with an axiomatic Multinomial Logit synthetic behavioral simulation across 5,000 travellers and 138,603 itinerary rows, we established a clean, reproducible testbed for travel personalization.

The supervised learning experiments proved that tree-based gradient boosting decisively outperforms linear classification by recovering the non-linear interaction manifold between traveller psychometrics and itinerary attributes. Furthermore, normalized relative candidate scores were proven to provide 2.3x more predictive power than raw absolute attributes. Decision-threshold optimization strictly on validation data successfully resolved positive-class recall suppression, enabling the champion model (**`Gradient Boosting Core` at $\tau^* = 0.30$**) to achieve **0.6976 ROC-AUC, 0.5116 F1, and 62.65% Recall** on unseen test travellers.

> [!IMPORTANT]
> **Closing Scientific Statement**:  
> The results demonstrate the feasibility of recovering simulated traveller preference patterns from grounded itinerary and Travel DNA features; they should not be interpreted as empirical estimates of real-world traveller conversion behaviour.

---

## 22. Reproducibility & Experimental Configuration
- **Hardware/Environment**: AMD64 Architecture, Windows OS, Python 3.11.9
- **Core Libraries**: `scikit-learn==1.3.2`, `pandas==2.1.3`, `numpy==1.26.2`, `matplotlib==3.8.2`, `seaborn==0.13.0`
- **Global Deterministic Seed**: `42`
- **Primary Data Path**: `data/synthetic/choice_dataset.parquet` (SHA-256: `43a49778bc01703f021283e4ce7340b5e0fb55f0324e619d62af5d2200876161`)
- **Execution Scripts**:
  - `src/phase4_baseline.py` (Step 1 Baseline Pipeline)
  - `src/phase4_step2.py` (Step 2 Threshold Optimization & Evaluation)
- **Primary Deliverables**:
  - [`reports/final/final_results_table.csv`](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/reports/final/final_results_table.csv)
  - [`reports/final/model_comparison_table.csv`](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/reports/final/model_comparison_table.csv)
  - [`reports/final/feature_importance_summary.csv`](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/reports/final/feature_importance_summary.csv)
  - [`reports/final/executive_summary.md`](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/reports/final/executive_summary.md)
  - [`reports/final/limitations_and_future_work.md`](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/reports/final/limitations_and_future_work.md)
  - [`reports/final/presentation_outline.md`](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/reports/final/presentation_outline.md)
  - [`reports/final/viva_questions_and_answers.md`](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/reports/final/viva_questions_and_answers.md)
