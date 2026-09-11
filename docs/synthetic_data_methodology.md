# Yātrā AI — Synthetic Traveller Behaviour & Travel DNA Methodology
**Phase 3 Technical Documentation & Final-Scale Specification**  
*Document Version: 2.0.0 (Final-Scale) | Generation Date: 2026-09-11 | Project: Yātrā AI*

---

> [!IMPORTANT]
> **SIMULATION & PROVENANCE DISCLAIMER**  
> The datasets described herein represent **synthetic behavioural data generated under explicitly documented simulation assumptions and internally validated for structural, statistical, mathematical, and behavioural consistency**. These simulation sampling assumptions are **NOT** claims about the real Indian population, nor do they represent observed real-world transaction labels. Candidate operational itineraries are grounded in real/canonical datasets, but behavioral preferences, choices, and proxy baseline ratings are strictly synthetic/simulation constructs.

---

## 1. Executive Summary & Core Principle

Yātrā AI employs a strict **Hybrid Data Strategy** for multi-modal travel recommendation and journey orchestration across the Indian subcontinent:

1. **Real / Public Foundation (Phase 1 & 2)**:
   - Railway stations, official codes, coordinates, zones: **100% Real** (8,990 Indian railway stations from `data/processed/canonical_stations.parquet`; 8,697 with verified coordinates).
   - Railway services and timetables: **100% Real** (5,208 train services from `canonical_train_services.parquet` and 416,637 station halt records from `canonical_train_routes.parquet`).
   - Historical railway delay and reliability distributions: **100% Real** (1,479 station halt delay observations across 42 express trains from `canonical_train_delays.parquet` derived from NTES punctuality logs).
   - Commercial domestic flight timetables and fares: **100% Real** (300,259 genuine commercial flight records spanning 6 major Indian metro corridors from `canonical_flights.parquet`).
   - Historical rainfall and environmental climate: **100% Real** (4,116 monthly meteorological records across 36 meteorological subdivisions from `canonical_subdivision_rainfall.parquet`).
   - Multi-modal corridor benchmarks: **100% Real** (30 directional pairs across India's top 6 metro cities from `canonical_corridor_multimodal.parquet`).

2. **Synthetic Behavioral Layer (Phase 3 Final Scale)**:
   - **Scale**: Exactly **5,000** unique travellers generating **8 search sessions each**, yielding exactly **40,000 search sessions** and **138,603 candidate/choice decision rows**.
   - **Synthetic ONLY**: Traveller demographic profiles, 7-dimensional Travel DNA psychometric attributes, multi-modal search sessions, and discrete choice selections.
   - **Provenance & Grounding Integrity**: Synthetic travellers search across genuine Indian city corridors. Candidate itineraries are retrieved directly from canonical flight and rail datasets.
   - **Operational Delay Reality**: Railway delay probabilities are grounded in empirical NTES logs where station halts exist. Domestic flight delay probabilities **do not exist** in public flight price datasets and are modeled as a **simulation proxy baseline** (`p_on_time: 0.88`, `p_slight: 0.08`, `p_severe: 0.03`, `p_cancelled: 0.01`).
   - **Fares & Carbon**: Flight fares are **observed market prices**; rail fares are **derived estimates** computed via official IRCTC distance slabs; carbon emissions are **derived estimates** based on citable UK DESNZ and Indian CEA emission factors.

---

## 2. Persona Archetypes & Final Population Mix

India's transportation landscape is characterized by extreme heterogeneity in income, time valuation, digital literacy, comfort expectations, and physical accessibility. To reflect this socio-economic spectrum, Phase 3 defines six persistent traveler personas.

The final population consists of **5,000 travellers** distributed as follows:

| Persona Archetype | Real-World Indian Travel Persona | Final Share | Final Count | Distinguishing Travel DNA Profile |
|---|---|:---:|:---:|---|
| **Cost-Sensitive Commuter** | Daily intercity commuters, students, unreserved/sleeper rail passengers, budget bus travelers. | **25.0%** | **1,250** | High `cost_sensitivity` ($\sim 0.82$), high `transfer_tolerance` ($\sim 0.80$), low `time_sensitivity` ($\sim 0.35$). |
| **Time-Sensitive Professional** | Corporate executives, IT consultants, corporate business travelers on metro routes (e.g. DEL-BOM, BLR-DEL). | **20.0%** | **1,000** | High `time_sensitivity` ($\sim 0.85$), extreme `reliability_sensitivity` ($\sim 0.90$), low `transfer_tolerance` ($\sim 0.25$). |
| **Car-Dependent Suburban** | Vehicle owners traveling intercity; accustomed to point-to-point convenience and door-to-door luggage transit. | **18.0%** | **900** | Low `transfer_tolerance` ($\sim 0.20$), high `comfort_preference` ($\sim 0.65$), moderate `time_sensitivity` ($\sim 0.55$). |
| **Occasional Leisure Traveler** | Families visiting hometowns (e.g., Diwali, Chhath, Pongal), vacationers traveling to hill stations or Goa. | **15.0%** | **750** | Moderate `cost_sensitivity` ($\sim 0.55$), high `comfort_preference` ($\sim 0.70$), high `departure_time_flexibility` ($\sim 0.80$). |
| **Eco-Conscious Urbanite** | Modern climate-aware urban professionals; youth seeking sustainable travel alternatives. | **12.0%** | **600** | High `sustainability_preference` ($\sim 0.88$), moderate `time_sensitivity` ($\sim 0.50$), high `transfer_tolerance` ($\sim 0.70$). |
| **Mobility-Constrained Traveler** | Senior citizens, persons with disabilities (Divyangjan), families with toddlers and heavy luggage. | **10.0%** | **500** | Extreme `comfort_preference` ($\sim 0.80$), high `reliability_sensitivity` ($\sim 0.90$), very low `transfer_tolerance` ($\sim 0.20$). |
| **Total Population** | | **100.0%** | **5,000** | |

*Note: These proportions represent simulation sampling assumptions, NOT claims about the real Indian demographic population.*

---

## 3. The 7-Dimensional Travel DNA Model

Each traveller $n$ is endowed with a persistent **Travel DNA vector**:
$$\mathbf{z}_n = \left( c_n,\, t_n,\, r_n,\, m_n,\, \tau_n,\, \phi_n,\, s_n \right) \in [0, 1]^7$$

To enforce continuous, strictly bounded, unimodal distributions with well-defined variances, each dimension is sampled from a **Beta Distribution**:
$$z_{n, d} \sim \text{Beta}(\alpha_d, \beta_d), \quad z_{n, d} \in (0, 1)$$

The theoretical mean and variance of dimension $d$ are:
$$\mathbb{E}[z] = \frac{\alpha}{\alpha + \beta}, \quad \text{Var}(z) = \frac{\alpha \beta}{(\alpha + \beta)^2 (\alpha + \beta + 1)}$$

### Beta Parameterizations by Persona (Approved Specification):

```yaml
Cost-Sensitive Commuter:
  cost_sensitivity:           Alpha: 9.0, Beta: 2.0  (E = 0.819, Std = 0.093)
  time_sensitivity:           Alpha: 3.5, Beta: 6.5  (E = 0.350, Std = 0.123)
  reliability_sensitivity:    Alpha: 6.5, Beta: 3.5  (E = 0.650, Std = 0.116)
  comfort_preference:         Alpha: 4.0, Beta: 4.0  (E = 0.500, Std = 0.139)
  transfer_tolerance:         Alpha: 8.0, Beta: 2.0  (E = 0.800, Std = 0.103)
  departure_time_flexibility: Alpha: 7.5, Beta: 2.5  (E = 0.750, Std = 0.112)
  sustainability_preference:  Alpha: 4.5, Beta: 6.0  (E = 0.429, Std = 0.132)

Time-Sensitive Professional:
  cost_sensitivity:           Alpha: 3.0, Beta: 7.0  (E = 0.300, Std = 0.118)
  time_sensitivity:           Alpha: 8.5, Beta: 1.5  (E = 0.850, Std = 0.087)
  reliability_sensitivity:    Alpha: 9.0, Beta: 1.0  (E = 0.900, Std = 0.073)
  comfort_preference:         Alpha: 7.5, Beta: 2.5  (E = 0.750, Std = 0.116)
  transfer_tolerance:         Alpha: 2.5, Beta: 7.5  (E = 0.250, Std = 0.112)
  departure_time_flexibility: Alpha: 3.5, Beta: 6.5  (E = 0.350, Std = 0.124)
  sustainability_preference:  Alpha: 3.5, Beta: 6.5  (E = 0.350, Std = 0.119)

Occasional Leisure Traveler:
  cost_sensitivity:           Alpha: 5.5, Beta: 4.5  (E = 0.550, Std = 0.129)
  time_sensitivity:           Alpha: 4.5, Beta: 5.5  (E = 0.450, Std = 0.129)
  reliability_sensitivity:    Alpha: 5.5, Beta: 4.5  (E = 0.550, Std = 0.124)
  comfort_preference:         Alpha: 7.0, Beta: 3.0  (E = 0.700, Std = 0.118)
  transfer_tolerance:         Alpha: 5.5, Beta: 4.5  (E = 0.550, Std = 0.129)
  departure_time_flexibility: Alpha: 8.0, Beta: 2.0  (E = 0.800, Std = 0.103)
  sustainability_preference:  Alpha: 5.0, Beta: 5.0  (E = 0.500, Std = 0.125)

Car-Dependent Suburban:
  cost_sensitivity:           Alpha: 4.5, Beta: 5.5  (E = 0.450, Std = 0.129)
  time_sensitivity:           Alpha: 5.5, Beta: 4.5  (E = 0.550, Std = 0.129)
  reliability_sensitivity:    Alpha: 5.5, Beta: 4.5  (E = 0.550, Std = 0.129)
  comfort_preference:         Alpha: 6.5, Beta: 3.5  (E = 0.650, Std = 0.119)
  transfer_tolerance:         Alpha: 2.0, Beta: 8.0  (E = 0.200, Std = 0.097)
  departure_time_flexibility: Alpha: 5.5, Beta: 4.5  (E = 0.550, Std = 0.129)
  sustainability_preference:  Alpha: 3.0, Beta: 7.0  (E = 0.300, Std = 0.115)

Eco-Conscious Urbanite:
  cost_sensitivity:           Alpha: 5.5, Beta: 4.5  (E = 0.550, Std = 0.129)
  time_sensitivity:           Alpha: 5.0, Beta: 5.0  (E = 0.500, Std = 0.129)
  reliability_sensitivity:    Alpha: 6.5, Beta: 3.5  (E = 0.650, Std = 0.116)
  comfort_preference:         Alpha: 5.5, Beta: 4.5  (E = 0.550, Std = 0.129)
  transfer_tolerance:         Alpha: 7.0, Beta: 3.0  (E = 0.700, Std = 0.115)
  departure_time_flexibility: Alpha: 7.5, Beta: 2.5  (E = 0.750, Std = 0.108)
  sustainability_preference:  Alpha: 8.8, Beta: 1.2  (E = 0.880, Std = 0.076)

Mobility-Constrained Traveler:
  cost_sensitivity:           Alpha: 6.0, Beta: 4.0  (E = 0.600, Std = 0.127)
  time_sensitivity:           Alpha: 3.5, Beta: 6.5  (E = 0.350, Std = 0.123)
  reliability_sensitivity:    Alpha: 9.0, Beta: 1.0  (E = 0.900, Std = 0.075)
  comfort_preference:         Alpha: 8.0, Beta: 2.0  (E = 0.800, Std = 0.100)
  transfer_tolerance:         Alpha: 2.0, Beta: 8.0  (E = 0.200, Std = 0.103)
  departure_time_flexibility: Alpha: 5.0, Beta: 5.0  (E = 0.500, Std = 0.129)
  sustainability_preference:  Alpha: 4.0, Beta: 6.0  (E = 0.400, Std = 0.123)
```

### 3.1 Inter-Variable Correlation Structure of Travel DNA

The correlation heatmap was inspected to characterize inter-variable dependencies. Moderate correlations are present because Travel DNA dimensions are generated using persona-conditioned sampling assumptions. These correlations are simulation-induced relationships and are not claims about empirical population psychology.

- **Intra-Persona Independence**: Within each individual persona archetype, all 7 dimensions are sampled from mutually independent Beta distributions (empirical intra-persona correlations $|r| \le 0.0886$, mean $|r| \approx 0.028$).
- **Macro Aggregate Correlations ($N = 5,000$)**: When pooled across the aggregate population, the distinct socio-economic mean vectors assigned to each persona induce moderate macro-correlations:
  - `cost_sensitivity` $\leftrightarrow$ `time_sensitivity`: **-0.6339** (trade-off between financial budget and travel speed)
  - `transfer_tolerance` $\leftrightarrow$ `departure_time_flexibility`: **+0.6227** (schedule flexibility correlates with transit patience)
  - `cost_sensitivity` $\leftrightarrow$ `transfer_tolerance`: **+0.6151** (willingness to accept multi-leg journeys for lower fares)
  - `time_sensitivity` $\leftrightarrow$ `departure_time_flexibility`: **-0.5271** (urgent travellers require specific departure windows)
  - `comfort_preference` $\leftrightarrow$ `transfer_tolerance`: **-0.5211** (premium comfort seekers avoid station transfers)
  - `reliability_sensitivity` $\leftrightarrow$ `departure_time_flexibility`: **-0.4753**

---

## 4. Search Session Generation

Each of the 5,000 travellers participates in **8 independent search occasions**, producing **40,000 search sessions**:
- **Corridor Universe**: The 30 directed pairs formed by India's top 6 metro cities:
  - *Delhi, Mumbai, Bangalore, Kolkata, Hyderabad, Chennai*.
- **Departure Windows**: Categorized into:
  - `Early Morning` (04:00–08:00)
  - `Morning` (08:00–12:00)
  - `Afternoon` (12:00–16:00)
  - `Evening` (16:00–20:00)
  - `Night` (20:00–04:00)
- **Trip Purposes**: Sampled probabilistically from persona profiles (not deterministic):
  - `Commute`, `Business`, `Leisure`, `Family / Personal`.
- **Party Size**: Sampled according to persona profile (1 to 4 travellers).
- **Lead Days**: Advance booking horizon in $[1, 49]$ days.

---

## 5. Candidate Itinerary Retrieval & Real Grounding

For each search session, Yātrā AI retrieves 2 to 5 genuine transportation alternatives directly from pre-indexed canonical datasets:
1. **Flights (`canonical_flights.parquet`)**:
   - Filtered by genuine origin and destination metro city.
   - **Observed Attributes**: Real airline carrier, flight number, duration, cabin class (Economy vs Business), number of stops, and real observed market ticket price in INR.
   - **Delay Probabilities (Simulation Proxy Baseline)**: Domestic aviation datasets in India record commercial booking prices and schedules, but **do not contain operational punctuality logs**. Flight delay probabilities are therefore explicitly classified as a **SIMULATION PROXY BASELINE** (`p_on_time: 0.88`, `p_slight_delay: 0.08`, `p_severe_delay: 0.03`, `p_cancelled: 0.01`), reflecting standard domestic aviation operational averages.
2. **Trains (`canonical_train_routes.parquet` & `canonical_train_delays.parquet`)**:
   - Filtered by origin and destination station metro clusters.
   - **Observed Attributes**: Real train number, train name, train service type, halt sequence, departure time window, and route schedule.
   - **Delay Probabilities (Derived / Real Station Delays)**: Linked to empirical punctuality records in `canonical_train_delays.parquet` (1,479 NTES halt observations across 42 express trains) by destination station code. Where a destination station lacks NTES logs, a neutral default distribution is assigned.
   - Synthetic candidate counts per session are bounded strictly between **2 and 5 genuine alternatives** (Mean: **3.465**).

---

## 6. Rail Fare Methodology (Derived Estimates)

Because public Indian Railways datasets record routes, stations, and timetables rather than commercial transaction databases or ticketing logs, train passenger fares are **DERIVED ESTIMATES** calculated using official Ministry of Railways / IRCTC distance-based passenger fare slabs:

$$\text{Estimated Rail Fare (INR)} = \left( \text{Route Distance (km)} \times \text{Class Rate per km} + \text{Surcharges} \right) \times \text{Train Multiplier}$$

- **Sleeper Class (SL)**: ₹0.52 / passenger-km (Base comfort proxy: 0.65)
- **AC 3-Tier (3A)**: ₹1.48 / passenger-km + ₹45 Superfast surcharge (Comfort proxy: 0.65)
- **AC 2-Tier (2A)**: ₹2.18 / passenger-km + ₹67.5 Superfast surcharge (Comfort proxy: 0.85)
- **Train Multipliers**:
  - Superfast Express: Flat ₹45 surcharge.
  - Premium services (Rajdhani / Shatabdi / Tejas / Duronto Express): $1.25\times$ base fare multiplier (Comfort proxy: 0.85).

---

## 7. Environmental Carbon Footprint Methodology (Derived Estimates)

Environmental carbon footprints ($\text{kg CO}_2\text{e}$) are **DERIVED ESTIMATES** computed by multiplying physical travel distances by recognized, citable operational emissions conversion factors:

$$\text{Estimated Carbon (kg CO}_2\text{e)} = \text{Distance (km)} \times \text{Carbon Emission Factor}$$

### Official Emission Factor Citations:
1. **Domestic Aviation**:
   - **Factor**: `0.1540 kg CO2e / passenger-km`
   - **Citation**: UK Department for Energy Security and Net Zero (DESNZ) & Department for Environment, Food and Rural Affairs (DEFRA) *Government Greenhouse Gas Conversion Factors for Company Reporting* (2023), Domestic Aviation (including radiative forcing index for high-altitude non-CO2 climate effects).
2. **Indian Electric Railways**:
   - **Factor**: `0.0320 kg CO2e / passenger-km`
   - **Citation**: Central Electricity Authority (CEA) of India, *CO2 Baseline Database for the Indian Power Sector* (Version 18, 2023) combined with the Ministry of Railways / Indian Railways Environment Directorate Annual Report (2022–2023), reflecting Indian Railways' >85% route electrification and average traction efficiency.

---

## 7B. Candidate Feature Provenance Classification Matrix

Every candidate and choice feature across the Phase 3 dataset is formally categorized into one of four provenance tiers:

| Feature Name | Primary Type | Provenance Description & Grounding Source |
|---|:---:|---|
| `mode` | **OBSERVED** | Genuine physical travel mode (`Flight` or `Rail`). |
| `carrier` / `airline_or_train` | **OBSERVED** | Genuine airline brand (from flight dataset) or train service type (from timetable). |
| `service_identifier` | **OBSERVED** | Genuine flight number (e.g. `UK-824`) or Indian Railways train number (e.g. `12645`). |
| `service_tier` (Flight) | **OBSERVED** | Genuine cabin class (`Economy`, `Business`) from flight dataset. |
| `service_tier` (Rail) | **SIMULATION PROXY** | Simulated passenger accommodation tier (`Standard Sleeper`, `3-Tier AC`, `2-Tier AC`). |
| `departure_window` (Flight) | **OBSERVED** | Categorical departure window recorded directly in the flight dataset. |
| `departure_window` (Rail) | **DERIVED** | Calculated by binning timetable departure minutes from midnight into 4-hour intervals. |
| `raw_cost` (Flight) | **OBSERVED** | Genuine commercial airfare in INR recorded in `canonical_flights.parquet`. |
| `raw_cost` (Rail) | **DERIVED ESTIMATE** | Calculated using official IRCTC distance-based tariff slabs from timetable track distance. |
| `raw_duration` (Flight) | **OBSERVED** | Scheduled flight duration hours from `canonical_flights.parquet`. |
| `raw_duration` (Rail) | **DERIVED** | Calculated from timetable arrival minus departure times across halt sequences. |
| `raw_distance` | **DERIVED** | Geodesic Haversine direct distance between airport / station coordinates. |
| `transfer_count` (Flight) | **OBSERVED** | Intermediate layovers (0, 1, 2) recorded in flight dataset. |
| `transfer_count` (Rail) | **DERIVED** | 0 for direct intercity express train options between metro clusters. |
| `p_on_time` (Rail) | **DERIVED / OBSERVED** | Station-level empirical punctuality from 1,479 NTES halt observations in `canonical_train_delays.parquet`. |
| `p_on_time` (Flight) | **SIMULATION PROXY BASELINE** | Baseline industry operational proxy (`0.88`), as flight dataset lacks delay logs. |
| `p_slight_delay`, `p_severe_delay`, `p_cancelled` | **DERIVED / PROXY** | Rail: Empirical NTES station distributions. Flight: Simulation proxy (`0.08`, `0.03`, `0.01`). |
| `carbon_estimate_kg` | **DERIVED ESTIMATE** | Calculated from route distance $\times$ UK DESNZ / Indian CEA emission factors. |
| `cost_score`, `time_score`, `carbon_score` | **DERIVED** | Choice-set min-max normalized attribute scores $\in [0, 1]$. |
| `transfer_score` | **DERIVED** | Non-linear decay score: $1 / (1 + \text{transfers})$. |
| `reliability_score` | **DERIVED** | Risk-penalized score: $1.0 - \text{Risk}(\mathbf{p})$. |
| `comfort_score` | **SIMULATION PROXY** | Calibrated proxy score mapped to accommodation class tier (0.65 to 0.95). |
| `departure_fit` | **DERIVED** | Window alignment score softened by traveller's departure flexibility. |
| `traveller_id`, `persona_type` | **SYNTHETIC** | Simulated synthetic individual and behavioral archetype. |
| `Travel DNA Vector` ($c_n, t_n, r_n, \dots$) | **SYNTHETIC** | Sampled from persona-conditioned theoretical Beta distributions. |
| `session_id`, `trip_purpose`, `party_size` | **SYNTHETIC** | Simulated trip search occasion and party composition. |
| `utility` ($V_{nj}$) | **SYNTHETIC / DERIVED** | Deterministic linear additive multi-attribute utility. |
| `choice_probability` ($P_{nj}$) | **SYNTHETIC / DERIVED** | Softmax Multinomial Logit choice probability. |
| `chosen` | **SYNTHETIC** | Probabilistically sampled binary discrete choice indicator $\in \{0, 1\}$. |
| `rank` | **SYNTHETIC** | Ordinal rank $\{1, \dots, J_s\}$ sorted by descending deterministic utility. |

---

## 8. Multi-Attribute Utility Function & MNL Formulation

For traveller $n$ choosing among $J_s$ genuine candidates in session $s$, the deterministic utility $V_{nj}$ is formulated as a linear additive multi-attribute function:

$$V_{nj} = \sum_{k=1}^7 w_{nk} \cdot X_{jk} + \text{ASC}_{\text{mode}}$$

### Feature Scoring Functions ($X_{jk} \in [0, 1]$):
1. **Cost Score ($X_{j, \text{cost}}$)**: Min-max normalized across candidates within the session:
   $$X_{j, \text{cost}} = 1.0 - \frac{\text{Cost}_j - \min(\text{Cost})}{\max(\text{Cost}) - \min(\text{Cost})}$$
2. **Time Score ($X_{j, \text{time}}$)**: Min-max normalized duration:
   $$X_{j, \text{time}} = 1.0 - \frac{\text{Duration}_j - \min(\text{Duration})}{\max(\text{Duration}) - \min(\text{Duration})}$$
3. **Reliability Score ($X_{j, \text{rel}}$)**: Risk-penalized score derived from delay probabilities:
   $$\text{Risk}_j = 0.60 \cdot P(\text{severe delay}) + 0.30 \cdot P(\text{cancelled}) + 0.10 \cdot P(\text{slight delay})$$
   $$X_{j, \text{rel}} = \max(0.0, 1.0 - \text{Risk}_j)$$
4. **Comfort Score ($X_{j, \text{comf}}$)**: Based on cabin tier (Flight Business: 0.95, Flight Economy: 0.80, Rail Premium: 0.85, Rail Standard: 0.65).
5. **Transfer Score ($X_{j, \text{trans}}$)**: $X_{j, \text{trans}} = \frac{1.0}{1.0 + \text{transfers}_j}$.
6. **Departure Fit ($X_{j, \text{dep}}$)**: Measures alignment with traveller's requested departure window, softened by `departure_time_flexibility`.
7. **Carbon Score ($X_{j, \text{carb}}$)**: Min-max normalized carbon emission savings (1.0 = lowest carbon).

### Dynamic Weight Normalization:
Travel DNA attributes directly dictate the relative importance weights $w_{nk}$:
$$\tilde{w}_{n, \text{cost}} = c_n, \quad \tilde{w}_{n, \text{time}} = t_n, \quad \tilde{w}_{n, \text{rel}} = r_n, \quad \tilde{w}_{n, \text{comf}} = m_n$$
$$\tilde{w}_{n, \text{trans}} = 1.0 - \tau_n, \quad \tilde{w}_{n, \text{dep}} = 1.0 - 0.50 \phi_n, \quad \tilde{w}_{n, \text{sust}} = s_n$$
$$w_{nk} = \frac{\tilde{w}_{nk}}{\sum_{m} \tilde{w}_{nm}}$$

### Multinomial Logit (MNL) Choice Probabilities:
Following discrete choice random utility theory ($U_{nj} = V_{nj} + \epsilon_{nj}$ where $\epsilon_{nj}$ is i.i.d. Gumbel distributed):
$$P_{nj} = \frac{\exp(\lambda \cdot V_{nj})}{\sum_{k=1}^{J_s} \exp(\lambda \cdot V_{nk})}$$
where $\lambda = 4.0$ is the choice sensitivity scale parameter, implemented with numerically stable softmax $\exp(V - \max(V))$.

**Choice Sampling**: Exactly one alternative per session is sampled via categorical sampling according to $P_{nj}$. Ranks are assigned in descending order of deterministic utility.

---

## 9. Utility Sensitivity Dynamics & Relative Effect Sizes

The automated behavioral sensitivity audit evaluates choice probability shifts across attributes under controlled counterfactual interventions:

| Intervention Experiment | Tested Behavioral Shift | Pilot $\Delta$ | Final Scale $\Delta$ | Directional Compliance |
|---|---|:---:|:---:|:---:|
| **Cost Sensitivity** | `cost_sensitivity` $0.50 \to 0.95$ | **+0.0989** | **+0.0989** | PASSED ($\Delta > 0$) |
| **Time Sensitivity** | `time_sensitivity` $0.50 \to 0.95$ | **+0.1696** | **+0.1696** | PASSED ($\Delta > 0$) |
| **Reliability Sensitivity** | `reliability_sensitivity` $0.50 \to 0.95$ | **+0.0203** | **+0.0203** | PASSED ($\Delta > 0$) |
| **Transfer Tolerance** | `transfer_tolerance` $0.50 \to 0.10$ | **+0.0118** | **+0.0118** | PASSED ($\Delta > 0$) |
| **Sustainability Preference** | `sustainability_preference` $0.50 \to 0.95$ | **+0.0459** | **+0.0459** | PASSED ($\Delta > 0$) |
| **Departure Flexibility** | `departure_time_flexibility` $0.50 \to 0.05$ | **+0.0587** | **+0.0587** | PASSED ($\Delta > 0$) |

*Audit Finding*: All six behavioral interventions operate with the expected positive economic sign, preserving directional rationality without artificial parameter tweaking.

### 9.1 Mathematical & Score-Range Dynamics of Behavioral Shifts

The exact physical attributes and derived score ranges in the implementation explain the precise ordering and magnitude of each probability delta:

#### A. Attribute Score Differences ($\Delta X = X_A - X_B$):
1. **Tests 1, 2, 4, 5, 6 (Multimodal Benchmark: Rail Alt A vs Flight Alt B)**:
   - **Cost**: Alt A (₹650) vs Alt B (₹5,500). Min-max normalized within session $\implies X_{\text{cost}, A} = 1.0000$, $X_{\text{cost}, B} = 0.0000 \implies \mathbf{\Delta X_{\text{cost}} = 1.0000}$.
   - **Time**: Alt A (18.0h) vs Alt B (2.5h). Min-max normalized $\implies X_{\text{time}, A} = 0.0000$, $X_{\text{time}, B} = 1.0000 \implies \mathbf{\Delta X_{\text{time}} = 1.0000}$.
   - **Transfer**: Non-linear decay $1 / (1 + \text{transfers})$. Alt A (0 stops) $= 1.0000$, Alt B (1 stop) $= 0.5000 \implies \mathbf{\Delta X_{\text{trans}} = 0.5000}$.
   - **Carbon**: Distance $\times$ factor (Rail 38.4 kg vs Flight 154.0 kg). Min-max normalized $\implies X_{\text{carb}, A} = 1.0000$, $X_{\text{carb}, B} = 0.0000 \implies \mathbf{\Delta X_{\text{carb}} = 1.0000}$.
   - **Departure Fit**: Session requested Morning. Alt A (Morning) fit $= 1.0000$. Alt B (Evening) has 2-window mismatch (raw mismatch $1.0$). At baseline flexibility ($0.50$), $\text{eff\_mismatch} = 1.0 \times (1 - 0.35) = 0.65 \implies X_{\text{dep}, B} = 0.3500$, yielding baseline $\mathbf{\Delta X_{\text{dep}} = 0.6500}$. Under the intervention ($\text{flex} = 0.05$), $\text{eff\_mismatch} = 1.0 \times (1 - 0.035) = 0.965 \implies X_{\text{dep}, B} = 0.0350$, widening spread to $\mathbf{\Delta X_{\text{dep}} = 0.9650}$.
2. **Test 3 (Isolated Reliability Benchmark: Rail Service High vs Rail Service Low)**:
   - Compares two identical rail services (1,000 km, 12.0h, ₹1,000, 0 transfers, Morning departure) where $\Delta X = 0.0000$ across all other 6 dimensions.
   - Delay risk formula: $\text{Risk} = 0.60 P_{\text{severe}} + 0.30 P_{\text{cancelled}} + 0.10 P_{\text{slight}}$.
   - High reliability ($95\%$ on-time, $1\%$ severe): $\text{Risk} = 0.010 \implies X_{\text{rel}, \text{high}} = \mathbf{0.9900}$.
   - Low reliability ($40\%$ on-time, $30\%$ severe, $10\%$ cancel): $\text{Risk} = 0.230 \implies X_{\text{rel}, \text{low}} = \mathbf{0.7700}$.
   - Exact reliability score spread: $\mathbf{\Delta X_{\text{rel}} = 0.9900 - 0.7700 = 0.2200}$.

#### B. Mathematical Mechanism of Probability Deltas:
- **Time ($\Delta = +0.1696$) vs Cost ($\Delta = +0.0989$)**:
  Both tests execute a compound two-attribute shift ($0.50 \to 0.95$ for primary, $0.50 \to 0.20$ for opposing). Because choice probabilities follow the logistic sigmoid $P(V) = 1 / (1 + e^{-\lambda \Delta V})$ with derivative $dP/d(\Delta V) = \lambda P(1 - P)$, the local gradient is steepest where $P \approx 0.50$ ($dP/d(\Delta V) \approx 1.00$). At baseline, Alt B has $P_B = 0.2190$ ($P(1-P) = 0.1710$), so the utility gain shifts $P_B$ from $0.2190$ to $0.3886$ ($\Delta = \mathbf{+0.1696}$). In contrast, Alt A starts at $P_A = 0.7810$, where increasing utility pushes into the upper saturated tail with lower derivative ($0.7810 \to 0.8799$, $\Delta = \mathbf{+0.0989}$).
- **Departure Flexibility ($\Delta = +0.0587$)**:
  Operates through two multiplying channels: reducing flexibility ($0.50 \to 0.05$) directly collapses Alt B's departure fit from $0.3500$ to $0.0350$ ($\Delta X_{\text{dep}}$ increases from $0.6500$ to $0.9650$) and simultaneously increases normalized departure weight $w_{\text{dep}}$ from $0.2000$ to $0.2453$. Utility difference widens from $0.3179$ to $0.4139$, yielding $\Delta P = \mathbf{+0.0587}$.
- **Sustainability Preference ($\Delta = +0.0459$)**:
  Single attribute shift ($0.50 \to 0.95$) over full carbon spread ($\Delta X_{\text{carb}} = 1.0000$). Normalized weight increases from $0.1333$ to $0.2262$, widening utility difference from $0.3179$ to $0.3910$, yielding $\Delta P = \mathbf{+0.0459}$.
- **Reliability Sensitivity ($\Delta = +0.0203$)**:
  Single attribute shift ($0.50 \to 0.95$) operating over the isolated spread $\Delta X_{\text{rel}} = 0.2200$ (with all other $\Delta X = 0$). Normalized weight increases from $0.1333$ to $0.2262$, shifting utility difference by $\Delta(\Delta V) = 0.0498 - 0.0293 = +0.0204$. With baseline $P = 0.5293$ where $\lambda P(1-P) \approx 0.996$, this produces $\Delta P \approx 0.996 \times 0.0204 = \mathbf{+0.0203}$.
- **Transfer Tolerance Reduction ($\Delta = +0.0118$)**:
  Single attribute shift ($\tau: 0.50 \to 0.10$) operating over transfer spread $\Delta X_{\text{trans}} = 0.5000$. Raw transfer avoidance weight $\tilde{w}_{\text{trans}} = 1.0 - \tau = 0.90$ (normalized: $0.1333 \to 0.2169$). This widens utility difference from $0.3179$ to $0.3354$, yielding $\Delta P = \mathbf{+0.0118}$.

---

## 10. Generated Artifacts & Cryptographic File Hashes

All final-scale datasets have been saved to `data/synthetic/` with deterministic random seed `42`:

| Dataset Filename | Format | Row Count | Column Count | Cryptographic SHA-256 Hash |
|---|:---:|:---:|:---:|---|
| `traveller_population.parquet` | Parquet | 5,000 | 9 | `7db83b4efed5371488761398e615be47ca660b5ee968556fdfa059ba82461beb` |
| `traveller_population.csv` | CSV | 5,000 | 9 | `92f576faf5c6fa1cedc4a116b75cc31f9e1dd0cb0e8d6350f4a0ef0881bf8b26` |
| `search_sessions.parquet` | Parquet | 40,000 | 10 | `9852016e19d15df5524b4d22c603fead6f9ab4450c1de7a44ed030253cef2e10` |
| `search_sessions.csv` | CSV | 40,000 | 10 | `8cc6dd2f3eab49e82316aaa3135c5b54ccd71ecde1675273131cf1e70290870f` |
| `itinerary_candidates.parquet` | Parquet | 138,603 | 25 | `f163377fd61b7abd2e46d30ff421f3b1e458258523ea96c9458f57b167ded7d4` |
| `itinerary_candidates.csv` | CSV | 138,603 | 25 | `e783dc42496123d3c7cff5843e0e221010cd8836769e1c2754e7821fea1e9480` |
| `choice_dataset.parquet` | Parquet | 138,603 | 36 | `43a49778bc01703f021283e4ce7340b5e0fb55f0324e619d62af5d2200876161` |
| `choice_dataset.csv` | CSV | 138,603 | 36 | `878b2b65cc96d3ef331c7983460dfefcc4f574a77e2306927688aa783e4df718` |

Pilot artifacts (`*_pilot.parquet`, `*_pilot.csv`) remain preserved separately in `data/synthetic/`.

---

## 11. Known Limitations

1. **Synthetic Choice Bounds**: Choices represent simulated utility-maximizing behavior governed by economic random utility theory, not empirical ticketing or booking records.
2. **Flight Delay Baseline**: Domestic flight delay probabilities are baseline simulation proxies (`0.88, 0.08, 0.03, 0.01`), not observed operational logs.
3. **Rail Fare Estimates**: Train fares are calculated using official IRCTC distance slabs, not dynamic fare booking logs.
4. **Carbon Footprint**: Carbon emissions are calculated estimates based on DESNZ and CEA conversion factors, not tailpipe measurements.
5. **Mode Coverage**: Available real transportation modes in the simulation are Rail and Flight across the 30 metro corridors. Complete bus/road networks are not fabricated.

---

**Phase 3 complete. Phase 4 not started.**
