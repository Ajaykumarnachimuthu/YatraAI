# YĀTRĀ AI — Phase 3 Requirement Specification & Prompt Archive

## 1. Phase Objective
Construct the behavioral simulation foundation for Yātrā AI to bridge the cold-start gap in public multimodal travel datasets. Formulate an authoritative 7-D continuous Travel DNA representation, define 6 distinct traveller persona archetypes, retrieve real candidate itineraries from canonical transport networks, engineer pre-choice candidate quality scores, simulate realistic discrete itinerary choices under Random Utility Maximization (RUM) and the Multinomial Logit (MNL) model, and execute a rigorous 5-tier validation suite.

---

## 2. Core Directives & Constraints
1. **Definitive 7-D Travel DNA**: The representation is strictly 7-dimensional:
   - `cost_sensitivity`
   - `time_sensitivity`
   - `reliability_sensitivity`
   - `comfort_preference`
   - `transfer_tolerance`
   - `departure_time_flexibility`
   - `sustainability_preference`
   *Stale 8-D concepts (`loyalty_bias`, `convenience_sensitivity`) are strictly prohibited.*
2. **Grounding in Real Transit Data**: Candidate itineraries must reflect real flight schedules, train services, fares, durations, and historical delays from `data/processed/`.
3. **No Target Leakage**: Candidate scores (`cost_score`, `time_score`, `carbon_score`, `reliability_score`, `comfort_score`, `transfer_score`, `departure_fit`) must be calculated strictly relative to the pre-choice consideration set. Choice indicators, utilities, and ranks must NOT leak into features.
4. **Frozen Final Scale**: The final-scale simulation dataset is frozen at:
   - 5,000 synthetic travellers
   - 40,000 search sessions (8 sessions per traveller)
   - 138,603 candidate itinerary choice rows
5. **Read-Only Dataset Verification**: Do not rerun or overwrite the frozen synthetic datasets. Audit and validate them in place.

---

## 3. Mathematical & Algorithmic Formulation
* **Random Utility Maximization (RUM)**:
  $$U_{nj} = V_{nj} + \varepsilon_{nj}$$
* **Systematic Utility Dot Product**:
  $$V_{nj} = \sum_{k=1}^7 \beta_k \cdot \text{DNA}_{nk} \cdot \text{Score}_{njk}$$
* **Multinomial Logit (MNL) Choice Probability**:
  $$P_{nj} = \frac{\exp(V_{nj})}{\sum_{l=1}^{J_n} \exp(V_{nl})}$$
* **Gumbel Extreme Value Error**: Choice simulated either via sampling from $P_{nj}$ or argmax over $U_{nj}$.
* **Relative Candidate Score Normalization**:
  $$\text{Score}_{njk} = 1.0 - \frac{x_{njk} - \min_{l} x_{nlk}}{\max_{l} x_{nlk} - \min_{l} x_{nlk} + \epsilon} \quad (\text{for cost, duration, carbon, transfer})$$

---

## 4. Required Deliverables
1. **Frozen Synthetic Datasets** in `data/synthetic/` (`traveller_population`, `search_sessions`, `itinerary_candidates`, `choice_dataset` in `.parquet` and `.csv`).
2. **Configuration File**: `config/synthetic_generation.yaml` declaring persona Beta distribution hyperparameters and scaling factors.
3. **5-Tier Validation Suite**:
   - Tier 1: Structural Integrity (schema, cardinality, missing values, primary/foreign keys).
   - Tier 2: Persona Archetype Distribution (empirical share vs. target share).
   - Tier 3: Statistical Moments (empirical mean and standard deviation vs. theoretical Beta moments).
   - Tier 4: MNL Axiomatic & Behavioral Sensitivity (price surge, delay shock, green penalty directionality).
   - Tier 5: Reproducibility & Non-Determinism audit.
4. **Validation Visualizations**: Persona boxplots, modal choice shares, correlation heatmaps.
5. **Phase 3 Technical & Validation Reports**: Complete documentation in `docs/synthetic_data_methodology.md` and `docs/synthetic_data_validation.md`.
