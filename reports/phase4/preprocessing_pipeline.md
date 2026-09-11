# Phase 4 Step 1: Preprocessing Pipeline & Feature Transformation Specification

**Project**: YĀTRĀ AI  
**Phase**: 4 — Machine Learning Experimentation  
**Step**: 1 — Lock Task + Build Leakage-Safe Baseline  
**Date**: September 2026  
**Status**: APPROVED & EXECUTED  

---

## 1. Objective & Scope

The objective of this preprocessing pipeline is to transform the frozen Phase 3 synthetic choice dataset (`data/synthetic/choice_dataset.parquet`) into numeric matrix representations suitable for baseline machine learning models, adhering strictly to zero-leakage standards:
1. **Zero Data Leakage**: All scalers, encoders, and transformers are fitted **strictly on the 70% Training partition** (3,500 travellers / 97,163 rows). Validation and Test partitions are transformed using the pre-fitted parameters without refitting.
2. **Architectural Differentiation**: Two specialized transformation pipelines are implemented:
   - **Linear Models (Logistic Regression)**: Requires standard scaling for continuous features to ensure uniform gradient descent and interpretable regularization; uses One-Hot Encoding (`drop='first'`) for nominal categorical features to eliminate artificial ordinal hierarchy and avoid multicollinearity.
   - **Tree-Based Models (Decision Tree, Random Forest, HistGradientBoosting)**: Preserves original scale of continuous features (trees are scale-invariant, retaining natural feature thresholds); uses Ordinal Encoding for categorical features.

---

## 2. Feature Configurations

Two distinct feature sets are evaluated to rigorously quantify the incremental predictive value of categorical persona abstractions over continuous psychometric dimensions:

### 2.1 Core Feature Set (Model A — 28 Features)
- **Continuous Travel DNA Dimensions (8)**:
  `cost_sensitivity`, `time_sensitivity`, `convenience_sensitivity`, `comfort_preference`, `reliability_preference`, `sustainability_preference`, `loyalty_bias`, `transfer_tolerance`
- **Itinerary Normalized Candidate Scores (7)**:
  `cost_score`, `time_score`, `reliability_score`, `comfort_score`, `transfer_score`, `carbon_score`, `departure_fit`
- **Itinerary Raw Attribute Features (8)**:
  `raw_cost`, `raw_duration`, `num_segments`, `layover_duration_min`, `rail_segments`, `air_segments`, `carbon_estimate_kg`, `punctuality_baseline`
- **Context & Environmental Features (5)**:
  `booking_lead_bracket` (categorical), `distance_km` (continuous), `origin_monthly_rainfall` (continuous), `dominant_climate` (categorical), `season` (categorical)

### 2.2 Extended Feature Set (Model B — 29 Features)
- Contains all 28 Core features above, PLUS:
- **`persona_type`** (Categorical — 6 levels):
  `BUDGET_CONSCIOUS`, `CORPORATE_BUSINESS`, `LEISURE_FAMILY`, `STUDENT_BACKPACKER`, `ECO_CONSCIOUS`, `SENIOR_CITIZEN`

---

## 3. Strict Pre-Training Leakage Audit

Before model construction, every candidate feature was verified against the ground-truth simulation pipeline.

| Feature Name | Role in MNL Simulation | In Choice Function? | Excluded from Features? | Safety Status |
|---|---|---|---|---|
| `chosen` | Primary simulation outcome (sampled from MNL choice probabilities) | Target Variable | **YES (TARGET)** | **TARGET** |
| `choice_probability` | Softmax probability $\frac{e^{V_{ni}}}{\sum_j e^{V_{nj}}}$ | Ground-truth posterior | **YES (EXCLUDED)** | **CRITICAL LEAKAGE** |
| `utility` | Systematic + Gumbel simulated utility $V_{ni} + \epsilon_{ni}$ | Ground-truth choice driver | **YES (EXCLUDED)** | **CRITICAL LEAKAGE** |
| `rank` | In-session sort order determined post-utility | Ground-truth derivative | **YES (EXCLUDED)** | **CRITICAL LEAKAGE** |
| `session_id`, `itinerary_id`, `traveller_id` | Identifiers | Session/Entity keys | **YES (EXCLUDED)** | **KEY LEAKAGE** |
| `cost_score`, `time_score`, `reliability_score`, `comfort_score`, `transfer_score`, `carbon_score`, `departure_fit` | Pre-choice candidate-set attributes normalized relative to session bounds | Input to utility function | **NO (SAFE INPUT)** | **VERIFIED SAFE** |

> **Audit Confirmation**:
> All normalized candidate scores are strictly pre-choice attributes computed from candidate itinerary characteristics and session constraints *prior* to utility calculation and discrete choice sampling. They contain zero information about whether an alternative was selected (`chosen`), its rank, or its choice probability.

---

## 4. Pipeline Architecture & Implementation

### 4.1 Missing Value Handling
- An exhaustive audit confirmed **0 missing values (0.00%)** across all 138,603 rows and 39 columns.
- Consequently, explicit imputation layers (e.g., SimpleImputer) were omitted to avoid unnecessary computational overhead and artificial variance shifts.

### 4.2 Linear Model Pipeline (`Pipeline_Linear`)
```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

linear_preprocessor = ColumnTransformer(
    transformers=[
        (
            'num',
            StandardScaler(),
            continuous_features,
        ),  # 25 features for Core / 25 for Ext
        (
            'cat',
            OneHotEncoder(drop='first', sparse_output=False),
            categorical_features,
        ),
    ],
    remainder='drop',
)
```
- **StandardScaler**: Centers numerical features to zero mean ($\mu = 0$) and unit variance ($\sigma = 1$), preventing features with large raw scales (`raw_cost` up to ₹8,500, `distance_km` up to 2,000 km) from dominating features scaled in [0, 1] (`cost_score`, Travel DNA dimensions).
- **OneHotEncoder(`drop='first'`)**: One level is dropped for each categorical feature to prevent the dummy variable trap (perfect multicollinearity) in unpenalized or L2-regularized linear models.

### 4.3 Tree-Based Model Pipeline (`Pipeline_Tree`)
```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder

tree_preprocessor = ColumnTransformer(
    transformers=[
        (
            'cat',
            OrdinalEncoder(
                handle_unknown='use_encoded_value', unknown_value=-1
            ),
            categorical_features,
        ),
    ],
    remainder='passthrough',  # Continuous features pass through unaltered
)
```
- **Scale Invariance**: Numerical features are passed through without modification. Decision trees, Random Forests, and HistGradientBoosting split on monotonic inequality thresholds ($x_j \le \theta$), making affine transformations mathematically invariant.
- **OrdinalEncoder**: Transforms nominal string labels into integer indices $[0, k-1]$. This compact encoding avoids dimensional explosion and allows tree algorithms to partition categorical categories efficiently.

---

## 5. Fit & Transform Verification

To ensure strict execution compliance:
1. `preprocessor.fit(X_train)` executed strictly on `X_train` (97,163 rows).
2. `X_train_trans = preprocessor.transform(X_train)`
3. `X_val_trans = preprocessor.transform(X_val)`
4. `X_test_trans = preprocessor.transform(X_test)`
5. Feature names and transformed array shapes were validated:
   - **Core Linear**: 97,163 rows $\times$ 35 columns (25 continuous + 10 one-hot columns).
   - **Core Tree**: 97,163 rows $\times$ 28 columns (25 continuous + 3 ordinal columns).
   - **Extended Linear**: 97,163 rows $\times$ 40 columns (25 continuous + 15 one-hot columns).
   - **Extended Tree**: 97,163 rows $\times$ 29 columns (25 continuous + 4 ordinal columns).

This guarantees 100% isolation across train, validation, and test datasets.
