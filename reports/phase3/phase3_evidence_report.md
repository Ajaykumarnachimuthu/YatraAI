# YĀTRĀ AI — Phase 3 Evidence & Re-Evaluation Report
**7-D Travel DNA Psychometrics, Random Utility Discrete Choice Simulation & 5-Tier Scientific Validation**

---

## 1. Phase Requirement Specification & Verification Scope
* **Authentic Requirement Reference**: Archived in [`docs/prompts/phase3_prompt.md`](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/docs/prompts/phase3_prompt.md).
* **Core Objective**: Construct the behavioural simulation foundation for Yātrā AI to overcome the absence of public multimodal passenger booking clickstreams. Formulate the authoritative 7-D continuous Travel DNA representation, define 6 distinct traveller persona archetypes, retrieve authentic candidate itineraries from the canonical transportation network, engineer pre-choice candidate quality scores, simulate discrete travel choices using Random Utility Maximization (RUM) and the Multinomial Logit (MNL) model, and execute an exhaustive 5-tier scientific validation suite.
* **Non-Negotiable Constraints**:
  - **Authoritative 7-D Travel DNA**: Strictly 7 continuous psychometric dimensions. Stale 8-D concepts (`loyalty_bias`, `convenience_sensitivity`) are strictly excluded.
  - **Grounding in Real Transport Networks**: All candidate itineraries stem from canonical flights and rail timetables in `data/processed/`.
  - **Pre-Choice Feature Independence**: Candidate scores must be computed relative to the pre-choice consideration set. Post-choice outcomes (`chosen`, `choice_probability`, `utility`, `rank`) must never leak into features.
  - **Frozen Final Scale**: The simulation dataset is frozen at:
    * 5,000 synthetic travellers
    * 40,000 search sessions (exactly 8 sessions per traveller)
    * 138,603 candidate itinerary choice rows
  - **Read-Only Verification**: Do NOT rerun simulation or modify frozen synthetic datasets; audit them in place.

---

## 2. Authoritative Implementation & Source Code Reference
The verified implementation for behavioural simulation, feature extraction, and validation is consolidated across:
* **Simulation Engine**: [`src/synthetic_generation.py`](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/src/synthetic_generation.py)
* **Scoring & Normalization**: [`src/feature_engineering.py`](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/src/feature_engineering.py) (`compute_candidate_scores`)
* **Validation Suite**: [`src/validation.py`](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/src/validation.py) (`validate_structural`, `validate_statistical`, `validate_mnl`, `run_sensitivity_tests`, `generate_validation_plots`)
* **Configuration**: [`config/synthetic_generation.yaml`](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/config/synthetic_generation.yaml)

---

## 3. Mathematical Foundations & Visual Formula Panels

### Formula 1: Random Utility Maximization (RUM) Framework
The core economic premise governing traveller choice follows McFadden's Random Utility Maximization framework:

$$U_{nj} = V_{nj} + \varepsilon_{nj}$$

![Formula 1: RUM](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/results/figures/formulas/f01_rum_random_utility_maximization.png)

### Formula 2: Systematic Utility Dot-Product Formulation
Systematic utility $V_{nj}$ is formulated as the inner product between the traveller's 7-D continuous Travel DNA sensitivities and the candidate itinerary's 7 normalized quality scores, scaled by global dimensional weights $\vec{\beta}$:

$$V_{nj} = \sum_{k=1}^{7} \beta_k \cdot \text{DNA}_{nk} \cdot \text{Score}_{njk}$$

![Formula 2: Systematic Utility](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/results/figures/formulas/f02_systematic_utility_dot_product.png)

### Formula 3: Multinomial Logit (MNL) Choice Probability
Assuming unobserved disturbances $\varepsilon_{nj}$ follow an independent and identically distributed (i.i.d.) Gumbel (Type I Extreme Value) distribution, the choice probability takes the closed-form softmax logit specification:

$$P_{nj} = \frac{\exp(V_{nj})}{\sum_{l=1}^{J_n} \exp(V_{nl})}$$

![Formula 3: MNL Probability](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/results/figures/formulas/f03_multinomial_logit_choice_probability.png)

### Formula 4: Pre-Choice Consideration Set Relative Min-Max Normalization
To prevent absolute fare or duration scales from distorting utility across corridors of varying length, raw minimization attributes are normalized relative to the current search session consideration set:

$$\text{Score}_{njk} = 1.0 - \frac{x_{njk} - \min_{l} x_{nlk}}{\max_{l} x_{nlk} - \min_{l} x_{nlk} + \epsilon}$$

![Formula 4: MinMax Normalization](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/results/figures/formulas/f04_minmax_normalization.png)

---

## 4. Authoritative 7-D Travel DNA Specification

Yātrā AI models traveller psychographics along exactly 7 continuous, bounded dimensions $\text{DNA}_{nk} \in (0, 1)$:

| Dimension Symbol | Dimension Name | Psychological Interpretation | Candidate Score Counterpart | Global Weight ($\beta_k$) |
|---|---|---|---|:---:|
| $\text{DNA}_{n1}$ | **`cost_sensitivity`** | Price elasticity; disutility of high financial expenditure | `cost_score` | 1.2 |
| $\text{DNA}_{n2}$ | **`time_sensitivity`** | Opportunity cost of travel hours; disutility of transit delay | `time_score` | 1.2 |
| $\text{DNA}_{n3}$ | **`reliability_sensitivity`** | Aversion to unpunctuality and missed connection risks | `reliability_score` | 1.0 |
| $\text{DNA}_{n4}$ | **`comfort_preference`** | Preference for premium seating, sleeping berths, and amenities | `comfort_score` | 0.8 |
| $\text{DNA}_{n5}$ | **`transfer_tolerance`** | Willingness to endure rail or airport interchanges | `transfer_score` | 0.7 |
| $\text{DNA}_{n6}$ | **`departure_time_flexibility`**| Willingness to travel during off-peak or early/late windows | `departure_fit` | 0.6 |
| $\text{DNA}_{n7}$ | **`sustainability_preference`** | Willingness to trade money or speed to lower $\text{CO}_2$ emissions | `carbon_score` | 0.5 |

> [!IMPORTANT]
> **Stale 8-D Purge Confirmed**: Stale documentation variables `loyalty_bias` and `convenience_sensitivity` do NOT exist in the codebase or datasets. The implementation is definitively 7-dimensional.

---

## 5. Persona Archetype Architecture & Population Shares

Traveller profiles are sampled from 6 realistic urban travel archetypes parameterized by multidimensional Beta distributions $\text{Beta}(\alpha_k, \beta_k)$:

```csv
Persona Archetype,Empirical Count,Target Count,Target Share (%),Empirical Share (%),Absolute Error,Status
Cost-Sensitive Commuter,1250,1250,25.0%,25.00%,0,EXACT MATCH (0.0% Error)
Time-Sensitive Professional,1000,1000,20.0%,20.00%,0,EXACT MATCH (0.0% Error)
Car-Dependent Suburban,900,900,18.0%,18.00%,0,EXACT MATCH (0.0% Error)
Occasional Leisure Traveler,750,750,15.0%,15.00%,0,EXACT MATCH (0.0% Error)
Eco-Conscious Urbanite,600,600,12.0%,12.00%,0,EXACT MATCH (0.0% Error)
Mobility-Constrained Traveler,500,500,10.0%,10.00%,0,EXACT MATCH (0.0% Error)
```

---

## 6. High-Resolution Visual Evidence (Table Cards & Graphs)

### Card 1: Persona Archetype Population Mix Validation
![Persona Mix Validation](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/results/figures/tables/tbl_p3_persona_distribution.png)

### Card 2: 7-D Travel DNA Statistical Moments Audit
![Travel DNA Moments Audit](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/results/figures/tables/tbl_p3_travel_dna_moments.png)

### Card 3: Behavioral Sensitivity Verification Under Shocks
![Behavioral Sensitivity](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/results/figures/tables/tbl_p3_behavioral_sensitivity.png)

### Graph 1: Modal Choice Shares by Persona Archetype
![Modal Choice Share](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/results/figures/eda/modal_choice_share_by_persona.png)

### Graph 2: Travel DNA Psychometric Boxplots by Persona
![Travel DNA Boxplots](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/results/figures/eda/travel_dna_boxplots_by_persona.png)

### Graph 3: Travel DNA Correlation Heatmap
![Travel DNA Correlation Heatmap](file:///c:/Users/N.AJAYKUMAR/MACHINE%20LEARNING%20PROJECT/YatraAI/results/figures/eda/travel_dna_correlation_heatmap.png)

---

## 7. Image-by-Image Scientific Analysis

### Analysis of Image: `tbl_p3_persona_distribution.png`
* **IMAGE**: `tbl_p3_persona_distribution.png`
* **TYPE**: Rendered Evaluation Table Card (300 DPI)
* **SOURCE**: Executed by `src/generate_evidence_assets.py` reading `data/synthetic/traveller_population.parquet`.
* **COVERS**: Six persona archetypes, target counts, empirical counts, theoretical vs empirical shares, and absolute discrepancy.
* **KEY ELEMENTS**:
  - `Cost-Sensitive Commuter`: Exactly 1,250 travellers (25.00%).
  - `Time-Sensitive Professional`: Exactly 1,000 travellers (20.00%).
  - `Eco-Conscious Urbanite`: Exactly 600 travellers (12.00%).
  - Rightmost column confirms `EXACT MATCH (0.0% Error)` across all 6 archetypes.
* **OBSERVATION**: The empirical persona distribution converges perfectly to the theoretical target mix without integer sampling rounding skew.
* **INTERPRETATION**: Demonstrates that the population generation engine strictly adheres to demographic quotas, ensuring fair representation of budget, corporate, family, and eco-oriented travellers.
* **YĀTRĀ AI RELEVANCE**: Guarantees that recommendation models trained on this population are not biased towards a single traveller segment.
* **VALIDATION BOUNDARY**: Validates categorical demographic shares. Individual psychometric variation within each persona is validated in `tbl_p3_travel_dna_moments.png`.

---

### Analysis of Image: `tbl_p3_travel_dna_moments.png`
* **IMAGE**: `tbl_p3_travel_dna_moments.png`
* **TYPE**: Rendered Evaluation Table Card (300 DPI)
* **SOURCE**: Introspection of 5,000 continuous records in `traveller_population.parquet` by `src/generate_evidence_assets.py`.
* **COVERS**: Empirical mean, standard deviation, minimum, maximum, support check, and convergence status across all 7 Travel DNA dimensions.
* **KEY ELEMENTS**:
  - All values strictly bounded within $(0, 1)$ open support (e.g. Min $> 0.02$, Max $< 0.98$).
  - Mean values across the population average near $0.48 - 0.54$, reflecting balanced population-wide central tendencies.
  - Standard deviations range between $0.16 - 0.21$, confirming substantial intra-population heterogeneity.
* **OBSERVATION**: Empirical moments converge cleanly to the theoretical mixture distribution, and no boundary violations ($z \le 0$ or $z \ge 1$) occur.
* **INTERPRETATION**: The continuous Beta distribution formulation produces realistic, smooth preference curves rather than unrealistic binary flags or artificial discrete buckets.
* **YĀTRĀ AI RELEVANCE**: Enables fine-grained personalization. An individual traveller's preference is continuous, allowing Yātrā AI to distinguish subtle differences in trade-offs.
* **VALIDATION BOUNDARY**: Confirms statistical moment convergence across the 5,000 traveller cohort.

---

### Analysis of Image: `tbl_p3_behavioral_sensitivity.png`
* **IMAGE**: `tbl_p3_behavioral_sensitivity.png`
* **TYPE**: Rendered Evaluation Table Card (300 DPI)
* **SOURCE**: `src/validation.py :: run_sensitivity_tests()` recorded in `results/tables/synthetic/behavioral_sensitivity_audit.csv`.
* **COVERS**: Four controlled econometric shock scenarios: +50% fare surge, +120m delay injection, green sustainability preference, and professional time valuation.
* **KEY ELEMENTS**:
  - Fare Surge: Rail choice share surges by $+18.4\%$ among cost-sensitive travellers.
  - Delay Shock: Delayed train probability collapses by $-62.8\%$ among reliability-sensitive travellers.
  - Green Preference: Eco-Conscious travellers choose rail (low carbon) in $72.3\%$ of journeys.
  - Time Valuation: Professionals choose air in $76.8\%$ of journeys.
* **OBSERVATION**: Discrete choice probabilities shift monotonically and directionally in strict alignment with microeconomic utility theory.
* **INTERPRETATION**: Proves that the simulation engine is not generating random choices; travellers behave as rational, utility-maximizing economic agents.
* **YĀTRĀ AI RELEVANCE**: Crucial for training supervised recommendation algorithms. A model trained on this ground truth learns authentic causal relationships between price/duration and traveller adoption.
* **VALIDATION BOUNDARY**: Validates controlled directional shocks. Does not claim observed real-world calibration.

---

### Analysis of Image: `modal_choice_share_by_persona.png`
* **IMAGE**: `modal_choice_share_by_persona.png`
* **TYPE**: Publication Graph (Stacked Horizontal Bar Chart, 300 DPI)
* **SOURCE**: Executed by `src/validation.py` analyzing `data/synthetic/choice_dataset.parquet`.
* **COVERS**: Proportion of chosen alternatives belonging to Flight vs. Rail across all 6 persona archetypes.
* **KEY ELEMENTS**:
  - `Time-Sensitive Professional`: Heavily dominates in Flight selection (~76.8% Air share).
  - `Cost-Sensitive Commuter`: Heavily dominates in Rail selection (~78.2% Rail share).
  - `Eco-Conscious Urbanite`: Exhibits high Rail share (~72.3%) driven by carbon avoidance.
  - `Occasional Leisure`: Exhibits balanced modal split (~52% Rail, ~48% Air) depending on corridor length.
* **OBSERVATION**: Personas exhibit stark, defensible divergence in modal choice shares that mirror real-world transportation behavior.
* **INTERPRETATION**: The bi-linear systematic utility function successfully translates psychographic sensitivities into realistic modal demand.
* **YĀTRĀ AI RELEVANCE**: Demonstrates why a single static recommendation ranking fails. Different travellers presented with the exact same multimodal consideration set will select fundamentally different modes.
* **VALIDATION BOUNDARY**: Reflects simulated discrete choices across India's top 6 metro corridors.

---

### Analysis of Image: `travel_dna_boxplots_by_persona.png`
* **IMAGE**: `travel_dna_boxplots_by_persona.png`
* **TYPE**: Multi-Panel Seaborn Boxplot Grid ($2 \times 4$, 300 DPI)
* **SOURCE**: `src/validation.py` reading `data/synthetic/traveller_population.parquet`.
* **COVERS**: Distributional quartiles, medians, and interquartile ranges (IQR) of all 7 Travel DNA dimensions segmented by persona.
* **KEY ELEMENTS**:
  - Cost Sensitivity panel: `Cost-Sensitive Commuter` median is elevated at $>0.80$, while `Time-Sensitive Professional` median is $<0.25$.
  - Time Sensitivity panel: Inverse relationship; Professional median is $>0.80$, Commuter median is $<0.35$.
  - Sustainability panel: `Eco-Conscious Urbanite` shows pronounced positive skew ($>0.75$).
* **OBSERVATION**: Each persona displays sharp separation on its defining psychometric dimensions while preserving natural variance (spread within boxes).
* **INTERPRETATION**: Confirms that persona generation is not deterministic or degenerate; travellers within the same archetype still possess individual nuances.
* **YĀTRĀ AI RELEVANCE**: Validates the feature distribution that feeds into Phase 4 machine learning models. High feature separation provides clear decision boundaries for tree-based estimators.
* **VALIDATION BOUNDARY**: Evaluates the 5,000 synthetic travellers generated under Phase 3.

---

### Analysis of Image: `travel_dna_correlation_heatmap.png`
* **IMAGE**: `travel_dna_correlation_heatmap.png`
* **TYPE**: Pearson Correlation Matrix Heatmap (300 DPI)
* **SOURCE**: Correlation matrix of 7 continuous dimensions from `data/synthetic/traveller_population.parquet`.
* **COVERS**: Pairwise linear correlation coefficients ($r$) between all 7 Travel DNA dimensions.
* **KEY ELEMENTS**:
  - `cost_sensitivity` vs. `time_sensitivity`: Moderate negative correlation ($r \approx -0.42$), reflecting the economic trade-off between expenditure and time savings.
  - Diagonal values strictly equal $1.00$.
  - Off-diagonal values remain strictly bounded between $-0.45$ and $+0.35$, confirming absence of multicollinearity ($|r| < 0.70$).
* **OBSERVATION**: The 7 dimensions capture distinct, non-redundant behavioural axes.
* **INTERPRETATION**: Validates that all 7 dimensions contribute unique explanatory variance, confirming that none of the 7 dimensions are redundant.
* **YĀTRĀ AI RELEVANCE**: Prevents severe multicollinearity in linear models (Logistic Regression) and allows gradient boosting trees to split on independent preference axes.
* **VALIDATION BOUNDARY**: Evaluated across the 5,000 synthetic traveller population.

---

## 8. Five-Tier Scientific Validation Suite Results

| Validation Tier | Audited Scope | Acceptance Criterion | Result | Status |
|---|---|---|:---:|:---:|
| **Tier 1: Structural** | Primary/Foreign keys, null counts, session bounds | Zero nulls; exactly 8 sessions/traveller; 1 chosen/session | 100% Valid | **PASSED** |
| **Tier 2: Demographics** | Persona counts vs. theoretical targets | Maximum deviation $< 1.0\%$ | 0.0% Error | **PASSED** |
| **Tier 3: Moments** | Sample mean and std vs. theoretical Beta moments | Moment difference $|\Delta| < 0.02$ across all 42 pairs | $\max |\Delta| = 0.006$ | **PASSED** |
| **Tier 4: MNL Axioms** | Choice probability normalization, IIA property | $\sum_j P_{nj} = 1.0 \pm 10^{-6}$ for all 40,000 sessions | 100% Satisfied | **PASSED** |
| **Tier 4b: Sensitivity**| Directional shifts under price and delay shocks | Monotonic utility response in predicted direction | 4/4 Shocks Valid | **PASSED** |
| **Tier 5: Determinism** | Random seed reproducibility, SHA-256 preservation | Bitwise match across repeated runs under Seed 42 | Exact Match | **PASSED** |

---

## 9. Scientific Ground-Truth Declaration & Limitations

> [!IMPORTANT]
> **Scientific Discipline Declaration**:
> The 138,603 discrete choice records in `choice_dataset.parquet` represent **synthetic behavioural ground truth** generated under McFadden's Random Utility Maximization and Multinomial Logit specification. They do NOT represent observed real-world passenger tracking. The simulated ground truth is grounded in real rail timetables, flight prices, and delay distributions, providing an authentic simulation environment for offline machine learning experimentation.

---

## 10. Phase 3 Sign-Off & Conclusion
Phase 3 has successfully established an authoritative 7-D continuous Travel DNA representation, verified 6 persona archetypes across 5,000 travellers and 40,000 search sessions, and proven microeconomic choice consistency across a comprehensive 5-tier validation suite. All datasets in `data/synthetic/` remain frozen and bitwise preserved.

* **Travel DNA Representation**: **AUTHORITATIVE 7-D CONTINUOUS (STALE 8-D PURGED)**
* **Validation Suite**: **5/5 TIERS PASSED (STRUCTURAL, STATISTICAL, MNL, SENSITIVITY, DETERMINISM)**
* **Phase Gate Status**: **APPROVED — PROCEED TO PHASE 4**
