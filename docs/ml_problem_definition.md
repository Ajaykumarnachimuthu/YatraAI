# YĀTRĀ AI — Machine Learning Problem Definition & Formulation Analysis (Phase 2)

## Executive Summary

The central goal of **Project Yātrā AI** is to build a machine-learning-driven multi-modal travel recommendation and journey orchestration platform for India. 

In Phase 2, we conducted a rigorous diagnostic evaluation of candidate ML formulations against our verified canonical datasets (`canonical_stations`, `canonical_train_routes`, `canonical_train_delays`, `canonical_flights`, `canonical_subdivision_rainfall`, `canonical_corridor_multimodal`).

### Core Finding on Data Grounding
* **What Real Public Data Supports**: Operational transit performance, timetable network topology, intercity distances, real flight pricing distributions, historical delay distributions, and seasonal monsoon intensity.
* **What Real Public Data Does NOT Support**: Real traveler clickstream logs, user-level booking transactions, and individual mode-choice selections (these are proprietary to OTAs like MakeMyTrip/IRCTC and are absent from all public/open datasets).
* **Guiding Architectural Rule**: We do not invent arbitrary targets or pre-select algorithms. The ML task must be justified strictly by empirical target availability and valid join structures.

---

## 1. Systematic Evaluation of Candidate ML Formulations

We evaluated five distinct ML problem formulations against the inspected datasets:

```
+---------------------------------------------------------------------------------------------------+
| Formulation               | Target Variable                  | Real Target Availability | Feasibility |
+---------------------------------------------------------------------------------------------------+
| 1. Binary Classification  | is_high_transfer_risk (0 or 1)   | 1,479 real halt records  | FEASIBLE    |
| 2. Multiclass Classif.    | delay_risk_category (4 classes)  | 1,479 real halt records  | SKEWED      |
| 3. Continuous Regression  | mean_delay_minutes (1 to 570 min)| 1,479 real halt records  | FEASIBLE    |
| 4. Risk / Reliability     | P(Delay > Connection Buffer)     | 1,479 real halt records  | HIGHLY DEFENSIBLE |
| 5. Ranking / Choice Model | chosen_journey_id (1..K)         | 0 records (ABSENT)       | REQUIRES SYNTHETIC |
+---------------------------------------------------------------------------------------------------+
```

---

### Candidate 1: Binary Classification — High Transfer Risk Prediction

* **Target Variable**: `is_high_transfer_risk` $\in \{0, 1\}$
  * $y = 1$ if $\text{mean\_delay\_minutes} > 45$ OR $p_{\text{severe\_delay}} > 0.25$ OR $p_{\text{cancelled}} > 0.10$
  * $y = 0$ otherwise (reliable / manageable delay)
* **Input Features Available in Real Data**:
  * Route topology: `sequence` (halt index), `cumulative_haversine_km`, `total_halts`
  * Timetable features: `arrival_minutes_from_midnight`, `halt_duration_minutes`, `journey_day`
  * Operational features: `train_type` (Raj, SF, Exp, Mail), `railway_zone` (17 zones)
  * Environmental features: `baseline_normal_monsoon_rainfall_mm`, `monsoon_intensity_ratio`
* **Target Availability in Processed Data**:
  * Total labeled observations: **1,479**
  * Class breakdown: Class 1 = **1,148 (77.62%)**, Class 0 = **331 (22.38%)**
* **Empirical Assessment**:
  * *Strengths*: Directly supported by real NTES operational logs without any synthetic labels. Directly useful for flagging fragile connections in a journey planner.
  * *Limitations*: 77.6% positive skew occurs because the 42 monitored trains are long-distance cross-country expresses (Guwahati to Delhi/Mumbai/Chennai) where long delays are common. Imposes a somewhat arbitrary threshold boundary (45 minutes).

---

### Candidate 2: Multiclass Classification — Operational Delay Severity Category

* **Target Variable**: `delay_risk_category` $\in \{1, 2, 3, 4\}$
  * Class 1: `ON_TIME_RELIABLE` ($\le 15\text{ min delay and } P(\text{on-time}) \ge 0.70$)
  * Class 2: `MODERATE_DELAY` ($15 < \text{delay} \le 45\text{ min}$)
  * Class 3: `SEVERE_DELAY` ($> 45\text{ min delay}$)
  * Class 4: `CANCEL_DISRUPTED` ($P(\text{cancelled}) \ge 0.20$)
* **Input Features**: Same as Formulation 1.
* **Target Availability in Processed Data**:
  * Total labeled observations: **1,479**
  * Class distribution:
    * `SEVERE_DELAY`: **1,076 records (72.75%)**
    * `MODERATE_DELAY`: **292 records (19.74%)**
    * `ON_TIME_RELIABLE`: **56 records (3.79%)**
    * `CANCEL_DISRUPTED`: **55 records (3.72%)**
* **Empirical Assessment**:
  * *Strengths*: Granular classification of transit reliability states.
  * *Limitations*: **Severe class imbalance**. The reliable and cancelled classes each represent under 3.8% of observations. Training a 4-class classifier would suffer from severe minority class sparsity unless heavily resampled or re-grouped.

---

### Candidate 3: Continuous Regression — Expected Arrival Delay Minutes

* **Target Variable**: Continuous arrival delay $y = \text{mean\_delay\_minutes} \in [1.0, 570.0]$
  * Normalized transformation: $y_{\text{log}} = \log(1 + \text{mean\_delay\_minutes})$
* **Input Features Available in Real Data**:
  * Segment metrics: `cumulative_haversine_km`, `segment_haversine_km`, `sequence / total_halts`
  * Temporal metrics: Scheduled time of day (cyclic sin/cos encoding of minutes from midnight)
  * Network metrics: Railway administrative zone, origin terminal cluster, train priority class
  * Environmental: Subdivisional monsoon intensity index
* **Target Availability & Statistical Properties**:
  * Count: **1,479 observations**
  * Mean: **122.66 min**, Median: **95.00 min**, Std: **98.43 min**
  * Percentiles: 25% = 46.0m, 75% = 172.5m, 90% = 266.0m, 99% = 456.2m
  * Skewness: **1.28** (moderately right-skewed; transformed to near-normal via log1p)
* **Empirical Assessment**:
  * *Strengths*: 100% supported by real data. Completely eliminates artificial discretization thresholds. Expected delay minutes can be added directly into graph path-finding algorithms (e.g., dynamic edge cost $c_e = t_{\text{scheduled}} + \hat{d}_e$).
  * *Limitations*: Does not inherently capture variance / tail risk (e.g. probability of extreme 4-hour delay) unless paired with quantile loss or variance estimation.

---

### Candidate 4: Probabilistic Risk Prediction — Connection Buffer Failure Probability

* **Target Variable**: Probability that incoming leg delay exceeds the scheduled transfer buffer $\Delta T$ at an interchange station:
  $$P(\text{Transfer Failure}) = P(D_{\text{leg}} > \Delta T) = 1 - F_{D}(\Delta T)$$
  where $\Delta T = t_{\text{dep, leg2}} - t_{\text{arr, leg1}}$.
* **Input Features**:
  * Timetable buffer $\Delta T$ (minutes) between scheduled arrival of Leg 1 and departure of Leg 2.
  * Empirical cumulative delay distribution: `p_on_time` ($\le 15\text{m}$), `p_slight_delay` ($15\text{--}60\text{m}$), `p_severe_delay` ($> 60\text{m}$), and `p_cancelled`.
  * Interchange station complexity: `metro_cluster`, `total_halts`.
* **Target Availability & Grounding**:
  * For every station halt in our delay records, we have the exact discrete probability mass vector:
    $$\mathbf{p} = [p_{\le 15\text{m}}, p_{15\text{--}60\text{m}}, p_{> 60\text{m}}, p_{\text{cancel}}]$$
* **Empirical Assessment**:
  * *Strengths*: Mathematically rigorous and directly aligned with Yātrā's core value proposition ("journey orchestration"). Protects travelers from booking "ghost connections" that look good on paper but fail in reality.
  * *Feasibility*: 100% computable from real operational data.

---

### Candidate 5: Ranking / Recommendation — Multi-Modal Journey Choice Modeling

* **Target Variable**: Chosen Journey Flag $y_i \in \{0, 1\}$ within candidate journey choice set $\{J_1, \dots, J_K\}$ for a given trip search query.
* **Input Features**:
  * Itinerary attributes: Total travel time, total fare (INR), modal breakdown (Rail vs. Flight vs. Multi-Leg), number of transfers, carbon emission proxy.
  * Traveler persona attributes: Time value of money ($\alpha$), budget sensitivity ($\beta$), risk aversion ($\gamma$), travel party type.
* **Target Availability in Inspected Data**:
  * **0 records (COMPLETELY ABSENT)**.
  * Comprehensive audit of raw and processed datasets confirmed: **zero user IDs, zero click logs, zero booking transactions, and zero customer ratings exist in real public transit datasets**.
* **Empirical Assessment**:
  * *Strengths*: Represents the ultimate consumer-facing product vision of Yātrā AI.
  * *Fatal Limitation for Real Data Alone*: **Cannot be trained solely on current real datasets without generating synthetic traveler behavior**. If attempted in Phase 2, ground-truth choice labels would have to be fabricated, violating project principles.

---

## 2. Definitive Recommendation: Two-Tier Architecture

To preserve scientific rigor, ensure complete grounding in real data, and avoid fabricating user choices, we recommend a **Two-Tier Decoupled ML & Decision Architecture**:

```
+=============================================================================+
|                      YĀTRĀ AI TWO-TIER ML ARCHITECTURE                      |
+=============================================================================+

  [TIER 1: REAL-DATA GROUNDED OPERATIONAL ENGINE]  <--- PHASE 2 & 4 (Real Data)
  ---------------------------------------------------------------------------
  Task: Multi-Modal Transit Delay & Transfer Failure Estimator
  Formulation:
    • Primary: Continuous Expected Delay Regression (log1p minutes)
    • Complementary: Probabilistic Transfer Failure Estimator P(Delay > Buffer)
  Ground Truth: 1,479 real NTES station delay observations + 416,637 timetable halts
  Features: Cumulative Haversine distance, scheduled time, railway zone, 
            train priority, monsoon intensity ratio, interchange buffer.
  Role: Produces an objective, calibrated "Reliability & Risk Score" (0.0 to 1.0)
        for every scheduled transit leg and interchange in India.

                                      |
                                      | Outputs: Expected Delay & Risk Score
                                      v

  [TIER 2: HYBRID MULTI-MODAL JOURNEY ORCHESTRATOR] <--- PHASE 3 & 4 (Hybrid)
  ---------------------------------------------------------------------------
  Task: Multi-Criteria Itinerary Recommendation & Utility Ranking
  Formulation: Learning-to-Rank / Multi-Attribute Utility Optimization
  Inputs:
    1. Flight & Rail Real Metrics: Duration (hrs), Fare (INR), Carbon footprint
    2. Tier 1 Output: Leg Delay & Connection Failure Risk Score
    3. Phase 3 Synthetic Persona: Traveler sensitivity weights (Time vs. Cost vs. Risk)
  Target: Personalized Itinerary Utility Ranking across Pareto-optimal candidates
```

### Why This Formulation is Most Defensible:
1. **Zero Fake Operational Data**: Tier 1 is trained 100% on real government and public records (NTES, CRIS timetables, IMD rainfall normals).
2. **Explicit Separation of Concerns**: Isolates the *physics of transit delays* (objective reality) from *traveler subjective preferences* (where synthetic generation is legitimate).
3. **No Invalid Joins**: Does not force spurious row-level joins between flight bookings and train running status.
4. **Direct Applicability to Yātrā's Core Value**: Solves the real traveler problem in India: *"Will I make my connection, and is the flight worth 3x the train fare given expected delays?"*

---

## 3. Specification of Synthetic Data Required for Phase 3

In strict compliance with instructions, **zero synthetic records have been generated in Phase 2**. 

Below is the precise specification of what synthetic data will be required in **Phase 3**:

| Synthetic Entity | Why Real Data is Unavailable | Mathematical Structure / Generation Model | Role in Future Model |
| :--- | :--- | :--- | :--- |
| **Traveler Persona Profiles** | Privacy laws and OTA proprietary ownership prevent public release of user profiles. | Parametric distribution of traveler types: Business ($\text{high } \alpha_T, \text{low } \beta_C$), Budget Leisure ($\text{low } \alpha_T, \text{high } \beta_C$), Family ($\text{low tolerance for transfers}$), Senior Citizen. | Provides user context vectors for personalized ranking. |
| **Search Queries & Preference Sessions** | Search session logs are proprietary to OTAs (MakeMyTrip, Cleartrip). | Simulated search queries across 30 metro corridors with origin-destination, travel dates, lead days (1–49 days), and party size. | Query groups (`qid`) for Learning-to-Rank datasets. |
| **Discrete Choice Decisions** | Real conversion/booking clickstreams are proprietary. | Standard Econometric Discrete Choice Model (Multinomial Logit): $$U_{ij} = -\alpha_i \cdot \text{Cost}_j - \beta_i \cdot \text{Duration}_j - \gamma_i \cdot \text{Risk}_j + \epsilon_{ij}$$ | Ground-truth ranking target for Tier 2 evaluation. |

---

## 4. Evaluation Metrics for the Recommended ML Tasks

### For Tier 1: Operational Delay Regression & Risk Estimation
* **Regression Metrics**:
  * Mean Absolute Error (MAE) in minutes
  * Root Mean Squared Error (RMSE)
  * Median Absolute Percentage Error (MdAPE)
* **Risk Probability Calibration Metrics**:
  * Brier Score (mean squared error of probability forecasts)
  * Expected Calibration Error (ECE)
  * Area Under the ROC Curve (ROC-AUC) on high-risk transfers

### For Tier 2: Multi-Modal Journey Ranking (Phase 4)
* **Ranking Quality Metrics**:
  * Normalized Discounted Cumulative Gain (NDCG@3 and NDCG@5)
  * Mean Reciprocal Rank (MRR)
  * Pareto-Efficiency Rate (% of top-ranked recommendations on the non-dominated Pareto frontier of Time, Cost, and Risk)
