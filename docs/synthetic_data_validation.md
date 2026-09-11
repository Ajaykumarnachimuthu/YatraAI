# Yātrā AI — Synthetic Traveller Data Validation Report
**Phase 3 Automated Quality, Grounding & Behavioral Audit**  
*Document Version: 2.0.0 (Final-Scale) | Generation Date: 2026-09-11 | Project: Yātrā AI*

---

> [!IMPORTANT]
> **SIMULATION & PROVENANCE DISCLAIMER**  
> The datasets described herein represent **synthetic behavioural data generated under explicitly documented simulation assumptions and internally validated for structural, statistical, mathematical, and behavioural consistency**. These simulation sampling assumptions are **NOT** claims about the real Indian population, nor do they represent observed real-world transaction labels. Candidate operational itineraries are grounded in real/canonical datasets, but behavioral preferences, choices, and proxy baseline ratings are strictly synthetic/simulation constructs.

---

## 1. Audit Scope & Verification Summary

This document presents the complete validation audit of the Phase 3 final-scale dataset generated for Yātrā AI under random seed `42`.

### Final-Scale Configuration & Output Metrics:
- **Unique Travellers**: Exactly **5,000** distinct individuals across 6 approved persona archetypes:
  - Cost-Sensitive Commuter: **1,250** (25.0%)
  - Time-Sensitive Professional: **1,000** (20.0%)
  - Car-Dependent Suburban: **900** (18.0%)
  - Occasional Leisure Traveler: **750** (15.0%)
  - Eco-Conscious Urbanite: **600** (12.0%)
  - Mobility-Constrained Traveler: **500** (10.0%)
- **Search Sessions**: Exactly **40,000** choice occasions (exactly 8 sessions per traveller).
- **Candidate Itineraries Evaluated**: Exactly **138,603** genuine multi-modal alternatives.
- **Choice Rows (Long Format)**: Exactly **138,603** decision rows ($1 \text{ row} = \text{traveller} \times \text{session} \times \text{alternative}$).
- **Alternatives per Session**: Bounded strictly between **2 and 5** (Mean: **3.465**, Median: **3**, Std: **0.954**).
- **Pilot Baseline Preserved**: 600 travellers, 2,400 sessions, 8,388 alternatives preserved in `data/synthetic/*_pilot.*`.

### Automated Validation Suite Status:
| Validation Tier | Test Scope | Result | Key Metric |
|---|---|:---:|---|
| **Tier 1: Structural Integrity** | Primary keys, foreign keys, null checks, value bounds, date arithmetic | **PASSED** | 0 nulls, 100% referential integrity |
| **Tier 2: Persona Mix Validation** | Target count conformity across 6 personas | **PASSED** | Exact match: 1250, 1000, 900, 750, 600, 500 |
| **Tier 3: Statistical Distribution** | Empirical vs Theoretical Beta $(\alpha, \beta)$ Travel DNA moments | **PASSED** | Max mean diff: 0.0102 ($\le 0.06$ threshold) |
| **Tier 4: MNL Mathematical Axioms** | $0 \le P_{nj} \le 1$, $\sum P_{nj} = 1.0$, numerical stability | **PASSED** | Max sum discrepancy: $3.33 \times 10^{-16}$ |
| **Tier 5: Behavioral Sensitivity** | 6 controlled attribute intervention experiments | **PASSED** | 6 / 6 interventions passed with expected sign |
| **Tier 6: Real-Data Grounding** | Canonical source traceability, provenance classification | **PASSED** | 100% traceable, 0 invalid joins, proxies explicitly labeled |
| **Tier 7: Leakage & Determinism** | Persona non-determinism, label integrity | **PASSED** | No deterministic mode locks; Flight: 47.79%, Rail: 52.21% |
| **Tier 8: Bitwise Reproducibility** | Full regeneration from scratch with seed 42 | **PASSED** | Bitwise identical SHA-256 hashes across runs |

**FINAL AUDIT VERDICT: PASSED (100% COMPLIANT ACROSS ALL TIERS)**

---

## 2. Tier 1: Structural Integrity Audit

Automated assertions verified physical, relational, and logical invariants across all generated tables:

1. **Traveller Table (`data/synthetic/traveller_population.parquet` / `.csv`)**:
   - Total rows: $5,000$
   - Uniqueness: $5,000$ unique `traveller_id`s (Primary Key integrity: 100%).
   - Missing Values: $0$ null values across demographic and 7 Travel DNA fields.
   - Boundedness: All Travel DNA dimensions satisfy $0.0 < z < 1.0$.
2. **Search Sessions Table (`data/synthetic/search_sessions.parquet` / `.csv`)**:
   - Total rows: $40,000$
   - Uniqueness: $40,000$ unique `session_id`s.
   - Referential Integrity: Every `traveller_id` references a valid record in `traveller_population`.
   - Balanced Sessions: Exactly $8$ search sessions per traveller.
   - Origin-Destination Validity: $\text{origin\_city} \ne \text{destination\_city}$ for all 40,000 sessions across the 30 directed pairs of India's top 6 metro corridors.
   - Advance Booking Bounds: `lead_days` strictly in $[1, 49]$ days.
   - Date Consistency: $\text{travel\_date} = \text{search\_date} + \text{lead\_days}$ for 100% of sessions.
3. **Itinerary Candidates & Choice Records (`choice_dataset.parquet` / `.csv`)**:
   - Total choice rows: $138,603$.
   - Candidates per session: Minimum = $2$, Maximum = $5$, Mean = $3.465$.
   - Exactly one chosen alternative per session ($\sum_{j} \text{chosen}_{sj} = 1$ for all 40,000 sessions).
   - Ranks are strictly ordinal: $\{1, \dots, J_s\}$ for each session without ties or omissions.
   - Source Traceability: 100% non-null `source_dataset` and `source_record_id` tracing back to `canonical_flights.parquet` and `canonical_train_routes.parquet`.

---

## 3. Tier 2: Persona Archetype Distribution Audit

| Persona Archetype | Theoretical Share (%) | Target Count | Generated Count | Empirical Share (%) | Discrepancy |
|---|:---:|:---:|:---:|:---:|:---:|
| **Cost-Sensitive Commuter** | 25.0% | 1,250 | 1,250 | 25.00% | 0.00% |
| **Time-Sensitive Professional** | 20.0% | 1,000 | 1,000 | 20.00% | 0.00% |
| **Car-Dependent Suburban** | 18.0% | 900 | 900 | 18.00% | 0.00% |
| **Occasional Leisure Traveler** | 15.0% | 750 | 750 | 15.00% | 0.00% |
| **Eco-Conscious Urbanite** | 12.0% | 600 | 600 | 12.00% | 0.00% |
| **Mobility-Constrained Traveler** | 10.0% | 500 | 500 | 10.00% | 0.00% |
| **Total Population** | **100.0%** | **5,000** | **5,000** | **100.00%** | **0.00%** |

---

## 4. Tier 3: Statistical Distribution Audit (Empirical vs. Theoretical Beta Moments)

Across the $N=5,000$ population, empirical sample moments were evaluated against theoretical Beta distribution parameters for all 42 persona-variable pairs:

$$\mathbb{E}_{\text{theoretical}} = \frac{\alpha}{\alpha + \beta}, \quad \text{Std}_{\text{theoretical}} = \sqrt{\frac{\alpha \beta}{(\alpha + \beta)^2 (\alpha + \beta + 1)}}$$

### Complete Empirical vs. Theoretical Comparison (N = 5,000):

| Persona Archetype | Variable | Theoretical Mean | Empirical Mean | Mean $\Delta$ | Theoretical Std | Empirical Std |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **Cost-Sensitive Commuter** ($N=1250$) | `cost_sensitivity` | 0.8187 | 0.8210 | +0.0023 | 0.0934 | 0.0927 |
| | `time_sensitivity` | 0.3500 | 0.3478 | -0.0022 | 0.1232 | 0.1190 |
| | `reliability_sensitivity` | 0.6500 | 0.6498 | -0.0002 | 0.1157 | 0.1189 |
| | `comfort_preference` | 0.5000 | 0.4939 | -0.0061 | 0.1387 | 0.1422 |
| | `transfer_tolerance` | 0.8000 | 0.7998 | -0.0002 | 0.1033 | 0.1036 |
| | `departure_time_flexibility` | 0.7500 | 0.7515 | +0.0015 | 0.1118 | 0.1138 |
| | `sustainability_preference` | 0.4231 | 0.4222 | -0.0009 | 0.1320 | 0.1334 |
| **Time-Sensitive Professional** ($N=1000$) | `cost_sensitivity` | 0.3000 | 0.3038 | +0.0038 | 0.1183 | 0.1212 |
| | `time_sensitivity` | 0.8500 | 0.8489 | -0.0011 | 0.0866 | 0.0877 |
| | `reliability_sensitivity` | 0.9000 | 0.8998 | -0.0002 | 0.0728 | 0.0685 |
| | `comfort_preference` | 0.7500 | 0.7497 | -0.0003 | 0.1157 | 0.1187 |
| | `transfer_tolerance` | 0.2500 | 0.2446 | -0.0054 | 0.1118 | 0.1078 |
| | `departure_time_flexibility` | 0.3571 | 0.3637 | +0.0066 | 0.1237 | 0.1262 |
| | `sustainability_preference` | 0.3500 | 0.3461 | -0.0039 | 0.1192 | 0.1182 |
| **Occasional Leisure Traveler** ($N=750$) | `cost_sensitivity` | 0.5500 | 0.5516 | +0.0016 | 0.1285 | 0.1302 |
| | `time_sensitivity` | 0.4500 | 0.4524 | +0.0024 | 0.1285 | 0.1219 |
| | `reliability_sensitivity` | 0.5500 | 0.5548 | +0.0048 | 0.1244 | 0.1226 |
| | `comfort_preference` | 0.7000 | 0.7050 | +0.0050 | 0.1183 | 0.1166 |
| | `transfer_tolerance` | 0.5500 | 0.5501 | +0.0001 | 0.1285 | 0.1255 |
| | `departure_time_flexibility` | 0.8000 | 0.7987 | -0.0013 | 0.1033 | 0.1081 |
| | `sustainability_preference` | 0.5000 | 0.4970 | -0.0030 | 0.1250 | 0.1256 |
| **Car-Dependent Suburban** ($N=900$) | `cost_sensitivity` | 0.4500 | 0.4482 | -0.0018 | 0.1285 | 0.1315 |
| | `time_sensitivity` | 0.5500 | 0.5602 | +0.0102 | 0.1285 | 0.1248 |
| | `reliability_sensitivity` | 0.5500 | 0.5500 | 0.0000 | 0.1285 | 0.1257 |
| | `comfort_preference` | 0.6500 | 0.6563 | +0.0063 | 0.1192 | 0.1206 |
| | `transfer_tolerance` | 0.2000 | 0.2002 | +0.0002 | 0.0970 | 0.0988 |
| | `departure_time_flexibility` | 0.5500 | 0.5508 | +0.0008 | 0.1285 | 0.1262 |
| | `sustainability_preference` | 0.3000 | 0.2997 | -0.0003 | 0.1146 | 0.1159 |
| **Eco-Conscious Urbanite** ($N=600$) | `cost_sensitivity` | 0.5500 | 0.5491 | -0.0009 | 0.1285 | 0.1265 |
| | `time_sensitivity` | 0.5000 | 0.5058 | +0.0058 | 0.1291 | 0.1281 |
| | `reliability_sensitivity` | 0.6500 | 0.6507 | +0.0007 | 0.1157 | 0.1184 |
| | `comfort_preference` | 0.5500 | 0.5510 | +0.0010 | 0.1285 | 0.1315 |
| | `transfer_tolerance` | 0.7000 | 0.7002 | +0.0002 | 0.1146 | 0.1131 |
| | `departure_time_flexibility` | 0.7500 | 0.7570 | +0.0070 | 0.1083 | 0.1071 |
| | `sustainability_preference` | 0.8824 | 0.8840 | +0.0017 | 0.0759 | 0.0789 |
| **Mobility-Constrained Traveler** ($N=500$) | `cost_sensitivity` | 0.6000 | 0.6017 | +0.0017 | 0.1265 | 0.1278 |
| | `time_sensitivity` | 0.3500 | 0.3436 | -0.0064 | 0.1232 | 0.1248 |
| | `reliability_sensitivity` | 0.9000 | 0.9005 | +0.0005 | 0.0750 | 0.0766 |
| | `comfort_preference` | 0.8000 | 0.7977 | -0.0023 | 0.1000 | 0.0976 |
| | `transfer_tolerance` | 0.2000 | 0.2004 | +0.0004 | 0.1033 | 0.1066 |
| | `departure_time_flexibility` | 0.5000 | 0.4979 | -0.0021 | 0.1291 | 0.1320 |
| | `sustainability_preference` | 0.4000 | 0.4012 | +0.0012 | 0.1225 | 0.1303 |

*Audit Finding*: Across all 42 variables (6 personas $\times$ 7 dimensions), the maximum absolute mean deviation is **0.0102** (Car-Dependent Suburban `time_sensitivity`: 0.5500 theoretical vs 0.5602 empirical), vastly superior to the pilot's 0.0347 and well below the configured threshold of $\le 0.06$. Empirical standard deviations track theoretical values within standard sampling tolerances.

### 4.1 Travel DNA Inter-Variable Correlation Structure

The correlation heatmap was inspected to characterize inter-variable dependencies. Moderate correlations are present because Travel DNA dimensions are generated using persona-conditioned sampling assumptions. These correlations are simulation-induced relationships and are not claims about empirical population psychology.

#### Aggregate Population Pearson Correlation Matrix ($N = 5,000$):

| Travel DNA Dimension | Cost Sens. | Time Sens. | Rel. Sens. | Comf. Pref. | Trans. Tol. | Dep. Flex. | Sust. Pref. |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **`cost_sensitivity`** | **1.0000** | -0.6339 | -0.2433 | -0.4117 | +0.6151 | +0.5054 | +0.1265 |
| **`time_sensitivity`** | -0.6339 | **1.0000** | +0.3102 | +0.2862 | -0.4583 | -0.5271 | -0.1586 |
| **`reliability_sensitivity`** | -0.2433 | +0.3102 | **1.0000** | +0.2649 | -0.2904 | -0.4753 | -0.1134 |
| **`comfort_preference`** | -0.4117 | +0.2862 | +0.2649 | **1.0000** | -0.5211 | -0.3690 | -0.1932 |
| **`transfer_tolerance`** | +0.6151 | -0.4583 | -0.2904 | -0.5211 | **1.0000** | +0.6227 | +0.4048 |
| **`departure_time_flexibility`**| +0.5054 | -0.5271 | -0.4753 | -0.3690 | +0.6227 | **1.0000** | +0.3633 |
| **`sustainability_preference`** | +0.1265 | -0.1586 | -0.1134 | -0.1932 | +0.4048 | +0.3633 | **1.0000** |

#### Key Correlation Characteristics & Mathematical Origin:
1. **Prominent Correlated Pairs**:
   - `cost_sensitivity` $\leftrightarrow$ `time_sensitivity`: **-0.6339** (strong trade-off between price and speed)
   - `transfer_tolerance` $\leftrightarrow$ `departure_time_flexibility`: **+0.6227** (schedule flexibility aligns with transfer patience)
   - `cost_sensitivity` $\leftrightarrow$ `transfer_tolerance`: **+0.6151** (cost sensitivity co-occurs with willingness to accept multi-leg transit)
   - `time_sensitivity` $\leftrightarrow$ `departure_time_flexibility`: **-0.5271** (time-sensitive travellers demand strict departure scheduling)
   - `comfort_preference` $\leftrightarrow$ `transfer_tolerance`: **-0.5211** (comfort seekers avoid station/airport transfers)
   - `cost_sensitivity` $\leftrightarrow$ `departure_time_flexibility`: **+0.5054**
   - `reliability_sensitivity` $\leftrightarrow$ `departure_time_flexibility`: **-0.4753**
2. **Mixture Distribution Effect (Intra-Persona Independence)**:
   - Within any individual persona archetype, all 7 dimensions are sampled from independent Beta distributions. Empirical intra-persona correlation checks confirm that the maximum absolute correlation within any single persona is $\le 0.0886$ (mean intra-persona $|r| \approx 0.028$).
   - The moderate aggregate correlations arise entirely as an **aggregate mixture distribution phenomenon** caused by the distinct mean vectors defined for each persona archetype (e.g., Cost-Sensitive Commuters have high cost sensitivity and high transfer tolerance, whereas Time-Sensitive Professionals have low cost sensitivity and low transfer tolerance).

---

## 5. Tier 4: MNL Mathematical Axiom Audit

The Multinomial Logit choice probabilities were verified across all 40,000 search sessions:
1. **Probability Boundedness**:
   $$0.0 \le P_{nj} \le 1.0, \quad \forall n, j$$
   *Result*: **100% compliant** (0 violations across 138,603 choice alternatives).
2. **Exhaustive Sum Axiom**:
   $$\sum_{j=1}^{J_s} P_{nj} = 1.0, \quad \forall s$$
   *Result*: **100% compliant**. The maximum absolute discrepancy across all 40,000 sessions is:
   $$\max_s \left| \sum_{j} P_{sj} - 1.0 \right| = 3.33 \times 10^{-16}$$
   (equivalent to double-precision machine epsilon).

---

## 6. Tier 5: Behavioral Sensitivity Audit (Pilot vs. Final-Scale Comparison)

To confirm that the utility formulation preserves directional economic rationality, the six approved controlled sensitivity interventions were evaluated on the benchmark corridor alternatives:

| Experiment | Tested Behavioral Intervention | Baseline $P$ | Intervention $P$ | Pilot Delta ($\Delta$) | Final Delta ($\Delta$) | Verification Status |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **1. Cost Sensitivity** | Increasing `cost_sensitivity` ($0.50 \to 0.95$) increases choice probability of cheaper rail option over expensive flight. | 0.7810 | 0.8799 | **+0.0989** | **+0.0989** | **PASSED** |
| **2. Time Sensitivity** | Increasing `time_sensitivity` ($0.50 \to 0.95$) increases choice probability of fast flight option over slow rail. | 0.2190 | 0.3886 | **+0.1696** | **+0.1696** | **PASSED** |
| **3. Reliability Sensitivity** | Increasing `reliability_sensitivity` ($0.50 \to 0.95$) increases choice probability of 95% on-time service over 40% on-time service. | 0.5293 | 0.5496 | **+0.0203** | **+0.0203** | **PASSED** |
| **4. Transfer Tolerance** | Reducing `transfer_tolerance` ($0.50 \to 0.10$) increases choice probability of direct service over 1-transfer flight. | 0.7810 | 0.7928 | **+0.0118** | **+0.0118** | **PASSED** |
| **5. Sustainability Preference** | Increasing `sustainability_preference` ($0.50 \to 0.95$) increases choice probability of low-carbon rail over high-carbon flight. | 0.7810 | 0.8269 | **+0.0459** | **+0.0459** | **PASSED** |
| **6. Departure Flexibility** | Reducing `departure_time_flexibility` ($0.50 \to 0.05$) penalizes mismatched departure window (Morning search vs Evening flight). | 0.7810 | 0.8397 | **+0.0587** | **+0.0587** | **PASSED** |

### 6.1 Mathematical & Score-Range Analysis of Behavioral Shifts

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

All six behavioral interventions operate strictly in the expected economic direction ($\partial P / \partial z_k > 0$), fully consistent with random utility theory and the underlying code implementation.

---

## 7. Tier 6: Real-Data Grounding & Provenance Classification

All candidate features in the final-scale dataset conform strictly to the four-tier audited provenance classification:

| Feature Name | Provenance Tier | Concrete Source / Grounding Method | Operational Meaning / Caveats |
|---|---|---|---|
| `raw_cost` (Flight) | **OBSERVED** | `canonical_flights.parquet` (`price` column) | Actual commercial airfares recorded on booking engines. |
| `raw_cost` (Rail) | **DERIVED ESTIMATE** | IRCTC official distance-based telescopic fare formulas | Deterministic estimate based on track-km and service tier. Not real passenger ticket transactions. |
| `raw_duration` (Flight) | **OBSERVED** | `canonical_flights.parquet` (`duration` column) | Published scheduled flight durations. |
| `raw_duration` (Rail) | **DERIVED** | `canonical_train_routes.parquet` | Cumulative runtime calculated between origin and destination station halts. |
| `raw_distance` | **DERIVED** | Geodesic Great-Circle distance between station/airport lat/lon | Physical distance calculated via Haversine formula. |
| `p_on_time`, `p_delay` (Flight) | **SIMULATION PROXY BASELINE** | Fixed domestic aviation operational baseline (`0.88, 0.08, 0.03, 0.01`) | **Explicit simulation proxy**. Public flight pricing datasets do not contain delay logs. |
| `p_on_time`, `p_delay` (Rail) | **DERIVED / EMPIRICAL** | Historical NTES punctuality observations (`canonical_train_delays.parquet`) | Derived empirical delay probabilities where station halt records exist. |
| `comfort_score` | **SIMULATION PROXY** | Calibrated cabin/tier proxy mapping (`0.65, 0.80, 0.85, 0.95`) | Qualitative ordinal comfort representation. |
| `carbon_estimate_kg` | **DERIVED ESTIMATE** | UK DESNZ (0.1540 kg/pkm flight) & CEA/BEE India (0.0320 kg/pkm rail) | Deterministic engineering estimate. Not directly measured onboard tailpipe emissions. |
| `Travel DNA` (7 dimensions) | **SYNTHETIC** | Persona Beta distribution random variates | Synthetic psychometric preferences. |
| `utility`, `choice_probability` | **SYNTHETIC / DERIVED** | Additive multi-attribute utility & MNL softmax | Deterministic mathematical simulation output. |
| `chosen` | **SYNTHETIC** | Probabilistic multinomial draw ($P_{nj}$) | Discrete simulation choice outcome. |

---

## 8. Tier 7: Leakage & Non-Determinism Verification

To ensure that machine learning models in Phase 4 are not trained on trivial or leaked relationships:
1. **No Persona Determinism**: Persona is an archetype guide, NOT a deterministic mode selector. Across 40,000 sessions, every persona exhibits balanced, probabilistic modal choices:
   - **Time-Sensitive Professional**: 52.05% Flight, 47.95% Rail (highest flight share, yet 47.95% choose rail on short/medium corridors or premium services).
   - **Eco-Conscious Urbanite**: 44.02% Flight, 55.98% Rail (highest rail share, yet 44.02% choose flight when rail duration is prohibitive).
   - **Cost-Sensitive Commuter**: 46.76% Flight, 53.24% Rail.
   - **Car-Dependent Suburban**: 47.96% Flight, 52.04% Rail.
   - **Mobility-Constrained Traveler**: 47.03% Flight, 52.98% Rail.
   - **Occasional Leisure Traveler**: 47.15% Flight, 52.85% Rail.
   - **Overall Population Choice Share**: **47.79% Flight, 52.21% Rail**.
2. **No Data Leakage**: Target columns (`utility`, `choice_probability`, `chosen`) are simulation labels and will be segregated before Phase 4 model training.
3. **No Synthetic ID Falsification**: No synthetic user identity has been linked to real passenger PNR or booking records.

---

## 9. Tier 8: Bitwise Reproducibility & Final Artifact SHA-256 Hashes

Independent regeneration from scratch using `seed: 42` produced bitwise identical datasets.

### Cryptographic SHA-256 Hashes of Final-Scale Artifacts:

```text
====================================================================================================
PHASE 3 FINAL-SCALE DATASET ARTIFACTS (data/synthetic/)
====================================================================================================
traveller_population.parquet : 7db83b4efed5371488761398e615be47ca660b5ee968556fdfa059ba82461beb
traveller_population.csv     : 92f576faf5c6fa1cedc4a116b75cc31f9e1dd0cb0e8d6350f4a0ef0881bf8b26
search_sessions.parquet      : 9852016e19d15df5524b4d22c603fead6f9ab4450c1de7a44ed030253cef2e10
search_sessions.csv          : 8cc6dd2f3eab49e82316aaa3135c5b54ccd71ecde1675273131cf1e70290870f
itinerary_candidates.parquet : f163377fd61b7abd2e46d30ff421f3b1e458258523ea96c9458f57b167ded7d4
itinerary_candidates.csv     : e783dc42496123d3c7cff5843e0e221010cd8836769e1c2754e7821fea1e9480
choice_dataset.parquet       : 43a49778bc01703f021283e4ce7340b5e0fb55f0324e619d62af5d2200876161
choice_dataset.csv           : 878b2b65cc96d3ef331c7983460dfefcc4f574a77e2306927688aa783e4df718
====================================================================================================
```

### Generated Graphical Artifacts (`docs/images/`):
- `travel_dna_boxplots_by_persona.png` (246,578 bytes)
- `modal_choice_share_by_persona.png` (71,882 bytes)
- `travel_dna_correlation_heatmap.png` (123,259 bytes)

---

## 10. Audit Conclusion & Phase Gate Sign-Off

All verification criteria for Phase 3 Final-Scale Generation have been successfully satisfied:
- Structural integrity: **PASSED**
- Persona mix fidelity: **PASSED**
- Statistical moment convergence: **PASSED**
- MNL axiomatic consistency: **PASSED**
- Directional behavioural sensitivity: **PASSED**
- Grounding and provenance taxonomy: **PASSED**
- Leakage and non-determinism bounds: **PASSED**
- Bitwise reproducibility: **PASSED**

**Phase 3 complete. Phase 4 not started.**
