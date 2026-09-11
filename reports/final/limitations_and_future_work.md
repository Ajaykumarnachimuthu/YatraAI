# YĀTRĀ AI: Methodological Limitations & Future Research Directions

**Project**: YĀTRĀ AI  
**Academic Phase**: Phase 5 — Final Results & Submission Package  
**Date**: September 2026  
**Document**: Methodological Limitations & Future Roadmap  

---

## 1. Academic & Methodological Boundaries

Transparent disclosure of research boundaries is essential for scientific integrity. The findings, performance metrics, and conclusions of Yātrā AI are subject to specific structural, computational, and empirical constraints:

### 1.1 Synthetic Behavioural Ground Truth
All target choice labels (`chosen`) are generated through synthetic simulation using a Random Utility Maximization (RUM) framework based on the Multinomial Logit (MNL) formulation:
$$P_{ni} = \frac{\exp(V_{ni})}{\sum_{j \in C_n} \exp(V_{nj})}$$
While grounded in calibrated behavioral economics literature, these labels represent **simulated agent choices**, not observed, empirical booking transactions from real-world Indian travellers. High model performance indicates successful reverse-engineering of the underlying mathematical utility function; it must **never** be cited as an empirical conversion rate for actual consumer booking behavior.

### 1.2 Public Operational Dataset Boundaries & Simulation Proxies
Although the underlying transit network is grounded in authentic public datasets, specific attributes relied on derived estimations or proxy baselines due to public data unavailability:
1. **Flight Delay Baselines (Simulation Proxy)**:  
   Because real DGCA/airline historical OTP (On-Time Performance) records at the individual flight-number level are proprietary and not publicly accessible, flight punctuality metrics were assigned as **calibrated simulation proxy baselines** (e.g., tier-based punctuality baselines of 82%–88%), rather than empirical operational delay logs.
2. **Rail Fare Methodology (Derived Estimates)**:  
   Indian Railways ticket transactions are protected by IRCTC. Candidate train ticket fares were calculated using an **explicit distance-and-class tariff derivation matrix** calibrated to official Indian Railway Conference Association (IRCA) telescopic fare charts, rather than observed ticket sales receipts.
3. **Environmental Carbon Footprints (Derived Estimates)**:  
   Carbon emissions per passenger-kilometer ($g\text{CO}_2/\text{p-km}$) were calculated using standardized emission factors (DGCA/ICAO averages for domestic aviation; Central Electricity Authority grid-average factors for electrified rail). These are derived estimates, not direct sensor measurements.
4. **Cabin Comfort Scores (Simulation Proxy)**:  
   Comfort ratings across classes (e.g., Sleeper vs. 3AC vs. 1AC vs. Airline Economy) represent fixed, ordinal quality proxies assigned based on seating/berth ergonomics, rather than crowdsourced passenger sentiment surveys.

### 1.3 Geographic & Modal Coverage Constraints
1. **Route Corridor Focus**: The transit network foundation incorporates India's busiest intercity corridors connecting 6 major metropolitan regions (Delhi, Mumbai, Bengaluru, Chennai, Kolkata, Hyderabad). While capturing the vast majority of high-density trunk traffic, secondary intercity and rural feeder routes are omitted.
2. **Modal Scope**: The current operational implementation evaluates heavy rail (IRCTC network) and domestic commercial aviation. Regional bus transit, shared cab intercity corridors, and suburban feeder modes are excluded due to the absence of standardized, open-access national GTFS feeds.

### 1.4 Architectural Limitation: Independent Binary Choice vs. Closed Choice Sets
A primary algorithmic constraint of the Phase 4 formulation is the **pointwise independence assumption**:
- The binary classifier evaluates each candidate itinerary alternative $i$ as an independent Bernoulli trial:
  $$\hat{Y}_{ni} \sim \text{Bernoulli}(P(Y_{ni}=1 \mid \mathbf{x}_{ni}))$$
- However, the ground-truth decision process is a **closed-set discrete choice over $C_n$** where **exactly one alternative is chosen**:
  $$\sum_{j \in C_n} Y_{nj} = 1 \quad \forall n$$
- Because independent binary classification does not condition on the session grouping or enforce the sum-to-one constraint, the model may predict zero chosen alternatives for an unappealing session, or predict multiple chosen alternatives for a highly attractive session. Threshold tuning ($\tau = 0.30$) shifts the operating point to optimize recall, but does not alter the fundamental pointwise mathematical formulation.

---

## 2. Future Engineering & Research Roadmap

The foundational work completed across Phases 1 through 5 provides a robust architectural baseline. The following staged extensions represent the natural production and academic evolution of Yātrā AI:

### Stage 1: Transition to Session-Aware Learning-to-Rank (LTR)
To eliminate the independent Bernoulli limitation, the next modeling evolution will implement **Listwise and Pairwise Learning-to-Rank**:
- **Algorithm Family**: LightGBM Ranker / LambdaMART, XGBoost Ranking, and CatBoost YetiRank.
- **Objective Formulation**: Optimize ranking metrics that natively condition on the query group (`session_id`), specifically:
  $$\text{NDCG@1} = \frac{\text{DCG@1}}{\text{IDCG@1}}, \quad \text{MRR} = \frac{1}{|Q|} \sum_{q=1}^{|Q|} \frac{1}{\text{rank}_q}$$
- **Architectural Advantage**: Guarantees a single ranked sequence of alternatives for every search query, with the top-ranked alternative presented as the primary recommendation.

### Stage 2: Econometric Discrete Choice Estimation
Complementing machine learning rankers, the system will implement econometric **Mixed Logit (Random Parameters Logit)** and **Nested Logit** estimators:
- Estimates full parameter distributions across the population to capture unobserved preference heterogeneity.
- Provides closed-form substitution elasticities and cross-elasticities between rail and air modes under varying price and carbon tax scenarios.

### Stage 3: Real User Interaction & Production Telemetry
Subject to institutional ethics approval and privacy-by-design principles:
- **Clickstream Telemetry**: Capture implicit feedback (dwell time, clicks, expands, itinerary shares) from live beta users.
- **Reciprocal Recommendation Filtering**: Incorporate collaborative filtering signals (e.g., Matrix Factorization / Two-Tower Neural Embeddings) alongside content-based Travel DNA traits.
- **Dynamic Online Learning**: Update individual Travel DNA preference vectors sequentially via Bayesian updating or contextual multi-armed bandits (e.g., LinUCB) based on user choices over time.

### Stage 4: Live Transit API Integrations
Transition from static processed schedules to dynamic, real-time data ingestion pipelines:
- **Live Airline GDS / OTA Integrations**: Real-time fare volatility and seat inventory feeds.
- **Live Rail Operational Feeds**: Integration with National Train Enquiry System (NTES) APIs for real-time tracking, live platform status, and dynamic waitlist confirmation probability estimation.
- **Dynamic Weather & Climate Disruption**: Real-time integration with Indian Meteorological Department (IMD) radar feeds to dynamically discount reliability scores during active monsoon storm events.

### Stage 5: Multimodal Door-to-Door Journey Orchestration
Expand the graph routing engine to solve complete, multi-segment "first-mile / long-haul / last-mile" journeys:
- Integrate urban metro rail, app-based ride-hailing (Ola/Uber), and regional state transport buses.
- Model multi-segment transfer friction, guaranteed minimum connection times (MCT), and cross-modal baggage transfer logistics.
