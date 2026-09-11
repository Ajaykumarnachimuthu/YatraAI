"""
YĀTRĀ AI — Feature Engineering & Preprocessing Engine
Authoritative module for:
- Pre-choice candidate itinerary multi-attribute quality scoring
- Continuous Travel DNA (7-D) and session context feature definitions
- Leakage-safe deterministic traveller-level data partitioning (70/15/15)
- Scikit-Learn ColumnTransformer preprocessing pipelines (Linear & Tree)
- Pre-training feature leakage audits
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = 42

# ==============================================================================
# 1. CANONICAL FEATURE SPECIFICATIONS (7-D TRAVEL DNA ARCHITECTURE)
# ==============================================================================

TRAVEL_DNA_FEATURES = [
    "cost_sensitivity",
    "time_sensitivity",
    "reliability_sensitivity",
    "comfort_preference",
    "transfer_tolerance",
    "departure_time_flexibility",
    "sustainability_preference",
]

SESSION_CONTEXT_NUMERIC = [
    "party_size",
    "lead_days",
]

ITINERARY_PHYSICAL_FEATURES = [
    "raw_cost",
    "raw_duration",
    "raw_distance",
    "carbon_estimate_kg",
    "transfer_count",
]

DERIVED_QUALITY_SCORES = [
    "cost_score",
    "time_score",
    "reliability_score",
    "comfort_score",
    "transfer_score",
    "carbon_score",
    "departure_fit",
]

# Total Numeric: 7 + 2 + 5 + 7 = 21 features
NUMERIC_FEATURES = (
    TRAVEL_DNA_FEATURES
    + SESSION_CONTEXT_NUMERIC
    + ITINERARY_PHYSICAL_FEATURES
    + DERIVED_QUALITY_SCORES
)

CATEGORICAL_CORE = [
    "origin_city",
    "destination_city",
    "departure_window",
    "trip_purpose",
    "mode",
    "carrier",
    "service_tier",
]

# Core Features: 21 numeric + 7 categorical = 28 features
CORE_FEATURES = NUMERIC_FEATURES + CATEGORICAL_CORE

# Extended Features: 28 core + persona_type = 29 features
CATEGORICAL_EXTENDED = CATEGORICAL_CORE + ["persona_type"]
EXTENDED_FEATURES = NUMERIC_FEATURES + CATEGORICAL_EXTENDED

LEAKAGE_TARGET_COLUMNS = ["chosen", "choice_probability", "utility", "rank"]
IDENTIFIER_COLUMNS = [
    "traveller_id",
    "session_id",
    "alternative_id",
    "service_identifier",
    "source_record_id",
    "source_dataset",
]

# ==============================================================================
# 2. CANDIDATE QUALITY SCORE DERIVATION
# ==============================================================================

def compute_candidate_scores(candidates, session, traveller, config):
    """
    Computes pre-choice choice-set relative quality scores for a session's candidate alternatives.
    All scores are bounded in [0.0, 1.0] where 1.0 represents the most desirable state.
    """
    carbon_cfg = config["itinerary_attributes"]["carbon_emission_factors"]
    flight_factor = carbon_cfg["flight"]["factor_kg_per_pkm"]
    rail_factor = carbon_cfg["rail"]["factor_kg_per_pkm"]
    comfort_cfg = config["itinerary_attributes"]["comfort_proxy_mapping"]
    risk_weights = config["itinerary_attributes"]["delay_risk_weights"]

    # 1. Carbon estimation
    for c in candidates:
        if c["mode"] == "Flight":
            c["carbon_estimate"] = round(c["raw_distance"] * flight_factor, 2)
        else:
            c["carbon_estimate"] = round(c["raw_distance"] * rail_factor, 2)

    # 2. Choice-set min and max bounds for relative normalization
    costs = [c["raw_cost"] for c in candidates]
    durs = [c["raw_duration"] for c in candidates]
    carbs = [c["carbon_estimate"] for c in candidates]

    min_c, max_c = min(costs), max(costs)
    min_d, max_d = min(durs), max(durs)
    min_carb, max_carb = min(carbs), max(carbs)

    dep_win_order = {"Early Morning": 0, "Morning": 1, "Afternoon": 2, "Evening": 3, "Night": 4}
    pref_win = session.get("departure_window", "Morning")
    pref_idx = dep_win_order.get(pref_win, 1)
    flex = traveller.get("departure_time_flexibility", 0.50)

    for c in candidates:
        # Cost score (1.0 = cheapest in choice-set)
        if max_c > min_c:
            c["cost_score"] = round(1.0 - (c["raw_cost"] - min_c) / (max_c - min_c), 4)
        else:
            c["cost_score"] = 1.0000

        # Time score (1.0 = fastest in choice-set)
        if max_d > min_d:
            c["time_score"] = round(1.0 - (c["raw_duration"] - min_d) / (max_d - min_d), 4)
        else:
            c["time_score"] = 1.0000

        # Transfer score (non-linear decay with stops)
        c["transfer_score"] = round(1.0 / (1.0 + c["transfer_count"]), 4)

        # Reliability score (penalized for delay risk)
        risk = (
            risk_weights["w_severe"] * c.get("p_severe_delay", 0.0)
            + risk_weights["w_cancelled"] * c.get("p_cancelled", 0.0)
            + risk_weights["w_slight"] * c.get("p_slight_delay", 0.0)
        )
        c["reliability_score"] = round(max(0.0, min(1.0, 1.0 - risk)), 4)

        # Comfort score (accommodation tier proxy)
        tier = c.get("cabin_class_or_tier", "")
        if c["mode"] == "Flight":
            if "Business" in tier:
                c["comfort_score"] = comfort_cfg["flight_business"]
            else:
                c["comfort_score"] = comfort_cfg["flight_economy"]
        else:
            if "Premium" in tier:
                c["comfort_score"] = comfort_cfg["rail_premium"]
            else:
                c["comfort_score"] = comfort_cfg["rail_standard"]

        # Carbon score (1.0 = lowest carbon footprint in choice-set)
        if max_carb > min_carb:
            c["carbon_score"] = round(1.0 - (c["carbon_estimate"] - min_carb) / (max_carb - min_carb), 4)
        else:
            c["carbon_score"] = 1.0000

        # Departure fit (schedule alignment tempered by flexibility)
        cand_win = c.get("departure_window", "Morning")
        cand_idx = dep_win_order.get(cand_win, 1)
        diff = abs(pref_idx - cand_idx)
        if diff == 0:
            raw_mismatch = 0.0
        elif diff == 1 or diff == 4:
            raw_mismatch = 0.5
        else:
            raw_mismatch = 1.0

        eff_mismatch = raw_mismatch * (1.0 - 0.70 * flex)
        c["departure_fit"] = round(max(0.0, min(1.0, 1.0 - eff_mismatch)), 4)

    return candidates

# ==============================================================================
# 3. DETERMINISTIC TRAVELLER-LEVEL DATA SPLITTING
# ==============================================================================

def split_by_traveller(df, seed=SEED):
    """
    Splits choice dataset by unique traveller_id into:
    - Train: 70% of travellers (3,500)
    - Validation: 15% of travellers (750)
    - Test: 15% of travellers (750)
    Guarantees strict zero traveller leakage across partitions.
    """
    unique_travellers = df["traveller_id"].unique()
    rng = np.random.default_rng(seed)
    shuffled_travellers = rng.permutation(unique_travellers)

    n_total = len(shuffled_travellers)
    n_train = int(0.70 * n_total)
    n_val = int(0.15 * n_total)
    n_test = n_total - n_train - n_val

    train_tids = set(shuffled_travellers[:n_train])
    val_tids = set(shuffled_travellers[n_train:n_train + n_val])
    test_tids = set(shuffled_travellers[n_train + n_val:])

    # Invariant assertions: zero overlap
    assert len(train_tids.intersection(val_tids)) == 0, "Traveller overlap between Train and Validation!"
    assert len(train_tids.intersection(test_tids)) == 0, "Traveller overlap between Train and Test!"
    assert len(val_tids.intersection(test_tids)) == 0, "Traveller overlap between Validation and Test!"
    assert len(train_tids) + len(val_tids) + len(test_tids) == n_total, "Partition sum mismatch!"

    train_mask = df["traveller_id"].isin(train_tids)
    val_mask = df["traveller_id"].isin(val_tids)
    test_mask = df["traveller_id"].isin(test_tids)

    df_train = df[train_mask].copy()
    df_val = df[val_mask].copy()
    df_test = df[test_mask].copy()

    split_summary = [
        {
            "partition": "TRAIN",
            "traveller_count": len(train_tids),
            "traveller_pct": len(train_tids) / n_total * 100,
            "session_count": df_train["session_id"].nunique(),
            "total_rows": len(df_train),
            "row_pct": len(df_train) / len(df) * 100,
            "chosen_1_count": int((df_train["chosen"] == 1).sum()),
            "chosen_0_count": int((df_train["chosen"] == 0).sum()),
            "positive_rate_pct": float((df_train["chosen"] == 1).mean() * 100),
            "imbalance_ratio": round(float((df_train["chosen"] == 0).sum() / (df_train["chosen"] == 1).sum()), 3),
        },
        {
            "partition": "VALIDATION",
            "traveller_count": len(val_tids),
            "traveller_pct": len(val_tids) / n_total * 100,
            "session_count": df_val["session_id"].nunique(),
            "total_rows": len(df_val),
            "row_pct": len(df_val) / len(df) * 100,
            "chosen_1_count": int((df_val["chosen"] == 1).sum()),
            "chosen_0_count": int((df_val["chosen"] == 0).sum()),
            "positive_rate_pct": float((df_val["chosen"] == 1).mean() * 100),
            "imbalance_ratio": round(float((df_val["chosen"] == 0).sum() / (df_val["chosen"] == 1).sum()), 3),
        },
        {
            "partition": "TEST",
            "traveller_count": len(test_tids),
            "traveller_pct": len(test_tids) / n_total * 100,
            "session_count": df_test["session_id"].nunique(),
            "total_rows": len(df_test),
            "row_pct": len(df_test) / len(df) * 100,
            "chosen_1_count": int((df_test["chosen"] == 1).sum()),
            "chosen_0_count": int((df_test["chosen"] == 0).sum()),
            "positive_rate_pct": float((df_test["chosen"] == 1).mean() * 100),
            "imbalance_ratio": round(float((df_test["chosen"] == 0).sum() / (df_test["chosen"] == 1).sum()), 3),
        },
        {
            "partition": "TOTAL",
            "traveller_count": n_total,
            "traveller_pct": 100.0,
            "session_count": df["session_id"].nunique(),
            "total_rows": len(df),
            "row_pct": 100.0,
            "chosen_1_count": int((df["chosen"] == 1).sum()),
            "chosen_0_count": int((df["chosen"] == 0).sum()),
            "positive_rate_pct": float((df["chosen"] == 1).mean() * 100),
            "imbalance_ratio": round(float((df["chosen"] == 0).sum() / (df["chosen"] == 1).sum()), 3),
        },
    ]

    return df_train, df_val, df_test, pd.DataFrame(split_summary)

# ==============================================================================
# 4. PREPROCESSING PIPELINES & MATRIX CONSTRUCTION
# ==============================================================================

def create_linear_preprocessor(cat_cols, num_cols=NUMERIC_FEATURES):
    """Builds ColumnTransformer for linear models (StandardScaler + OneHotEncoder)."""
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_cols),
            ("cat", OneHotEncoder(drop="first", handle_unknown="ignore", sparse_output=False), cat_cols),
        ]
    )

def create_tree_preprocessor(cat_cols, num_cols=NUMERIC_FEATURES):
    """Builds ColumnTransformer for tree models (passthrough numerics + OrdinalEncoder)."""
    return ColumnTransformer(
        transformers=[
            ("num", "passthrough", num_cols),
            ("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1), cat_cols),
        ]
    )

def build_feature_matrices(df_train, df_val, df_test, feature_config="core"):
    """
    Transforms train, val, and test splits into matrices for:
    1. Linear model (StandardScaler on numerics, OneHotEncoder on categoricals)
    2. Tree models (Raw numerics, OrdinalEncoder on categoricals)
    Preprocessors are fitted strictly on df_train.
    """
    cat_cols = CATEGORICAL_CORE if feature_config == "core" else CATEGORICAL_EXTENDED
    num_cols = NUMERIC_FEATURES

    y_train = df_train["chosen"].values
    y_val = df_val["chosen"].values
    y_test = df_test["chosen"].values

    # Linear Pipeline
    linear_preprocessor = create_linear_preprocessor(cat_cols, num_cols)
    X_train_linear = linear_preprocessor.fit_transform(df_train)
    X_val_linear = linear_preprocessor.transform(df_val)
    X_test_linear = linear_preprocessor.transform(df_test)

    cat_feature_names = linear_preprocessor.named_transformers_["cat"].get_feature_names_out(cat_cols)
    linear_feature_names = list(num_cols) + list(cat_feature_names)

    # Tree Pipeline
    tree_preprocessor = create_tree_preprocessor(cat_cols, num_cols)
    X_train_tree = tree_preprocessor.fit_transform(df_train)
    X_val_tree = tree_preprocessor.transform(df_val)
    X_test_tree = tree_preprocessor.transform(df_test)
    tree_feature_names = list(num_cols) + list(cat_cols)

    return {
        "linear": {
            "X_train": X_train_linear,
            "X_val": X_val_linear,
            "X_test": X_test_linear,
            "feature_names": linear_feature_names,
            "preprocessor": linear_preprocessor,
        },
        "tree": {
            "X_train": X_train_tree,
            "X_val": X_val_tree,
            "X_test": X_test_tree,
            "feature_names": tree_feature_names,
            "preprocessor": tree_preprocessor,
        },
        "y_train": y_train,
        "y_val": y_val,
        "y_test": y_test,
    }

# ==============================================================================
# 5. PRE-TRAINING LEAKAGE AUDIT
# ==============================================================================

def perform_leakage_audit(df):
    """
    Classifies every column in choice_dataset and verifies zero leakage for predictors.
    """
    classifications = {
        "chosen": ("TARGET", "Primary binary classification target (1 = chosen, 0 = not chosen)", False, False),
        "choice_probability": ("LEAKAGE / POST-CHOICE", "Simulation MNL probability output P_nj", False, False),
        "utility": ("LEAKAGE / POST-CHOICE", "Simulation deterministic utility score V_nj", False, False),
        "rank": ("LEAKAGE / POST-CHOICE", "Simulation utility rank ordering (1 to 5)", False, False),
        "traveller_id": ("IDENTIFIER", "Unique traveller identifier used as partition key", False, False),
        "session_id": ("IDENTIFIER", "Search session choice occasion identifier", False, False),
        "alternative_id": ("IDENTIFIER", "Itinerary row primary key within session", False, False),
        "service_identifier": ("IDENTIFIER", "Flight/Train service number (high cardinality)", False, False),
        "source_record_id": ("IDENTIFIER", "Source dataset provenance tracking ID", False, False),
        "source_dataset": ("METADATA", "Source canonical dataset name (redundant with mode)", False, False),
        "persona_type": ("SYNTHETIC PERSONA", "Simulation behavioral archetype (6 personas)", False, True),
        "cost_sensitivity": ("TRAVELLER PREFERENCE (DNA)", "Persistent continuous cost sensitivity [0, 1]", True, True),
        "time_sensitivity": ("TRAVELLER PREFERENCE (DNA)", "Persistent continuous time sensitivity [0, 1]", True, True),
        "reliability_sensitivity": ("TRAVELLER PREFERENCE (DNA)", "Persistent continuous reliability sensitivity [0, 1]", True, True),
        "comfort_preference": ("TRAVELLER PREFERENCE (DNA)", "Persistent continuous comfort preference [0, 1]", True, True),
        "transfer_tolerance": ("TRAVELLER PREFERENCE (DNA)", "Persistent continuous transfer tolerance [0, 1]", True, True),
        "departure_time_flexibility": ("TRAVELLER PREFERENCE (DNA)", "Persistent continuous departure flexibility [0, 1]", True, True),
        "sustainability_preference": ("TRAVELLER PREFERENCE (DNA)", "Persistent continuous sustainability preference [0, 1]", True, True),
        "origin_city": ("SESSION CONTEXT", "Search query origin metro city", True, True),
        "destination_city": ("SESSION CONTEXT", "Search query destination metro city", True, True),
        "departure_window": ("SESSION CONTEXT", "Search query requested departure time window", True, True),
        "trip_purpose": ("SESSION CONTEXT", "Search occasion trip purpose", True, True),
        "party_size": ("SESSION CONTEXT", "Number of passengers in travel party (1-4)", True, True),
        "lead_days": ("SESSION CONTEXT", "Days between search date and travel date (1-49)", True, True),
        "mode": ("ITINERARY ATTRIBUTE", "Transit mode (Flight or Rail)", True, True),
        "carrier": ("ITINERARY ATTRIBUTE", "Transit carrier brand / service tier", True, True),
        "service_tier": ("ITINERARY ATTRIBUTE", "Cabin class / passenger accommodation tier", True, True),
        "raw_cost": ("OPERATIONAL / ITINERARY", "Ticket fare in INR (observed flight price or derived rail tariff)", True, True),
        "raw_duration": ("OPERATIONAL / ITINERARY", "Journey duration in hours", True, True),
        "raw_distance": ("OPERATIONAL / ITINERARY", "Geodesic route distance in km", True, True),
        "carbon_estimate_kg": ("OPERATIONAL / ITINERARY", "Derived carbon footprint estimate in kg CO2e", True, True),
        "transfer_count": ("OPERATIONAL / ITINERARY", "Number of intermediate layovers / stops (0, 1, 2)", True, True),
        "cost_score": ("DERIVED CANDIDATE SCORE", "Choice-set relative min-max normalized cost score [0, 1]", True, True),
        "time_score": ("DERIVED CANDIDATE SCORE", "Choice-set relative min-max normalized duration score [0, 1]", True, True),
        "reliability_score": ("DERIVED CANDIDATE SCORE", "Pre-choice risk-penalized operational reliability score [0, 1]", True, True),
        "comfort_score": ("DERIVED CANDIDATE SCORE", "Pre-choice accommodation tier proxy comfort score [0, 1]", True, True),
        "transfer_score": ("DERIVED CANDIDATE SCORE", "Pre-choice non-linear transfer decay score 1/(1+transfers)", True, True),
        "carbon_score": ("DERIVED CANDIDATE SCORE", "Choice-set relative min-max normalized carbon savings score [0, 1]", True, True),
        "departure_fit": ("DERIVED CANDIDATE SCORE", "Pre-choice departure window alignment score [0, 1]", True, True),
    }

    audit_records = []
    for col in df.columns:
        tier, desc, in_core, in_ext = classifications.get(col, ("UNKNOWN", "Unclassified column", False, False))
        audit_records.append({
            "column_name": col,
            "data_type": str(df[col].dtype),
            "classification_tier": tier,
            "description": desc,
            "null_count": int(df[col].isnull().sum()),
            "unique_values": int(df[col].nunique()),
            "in_core_model_a": in_core,
            "in_extended_model_b": in_ext,
        })

    df_audit = pd.DataFrame(audit_records)

    # Assert zero leakage
    for lcol in ["choice_probability", "utility", "rank"]:
        assert not df_audit.loc[df_audit["column_name"] == lcol, "in_core_model_a"].values[0]
        assert not df_audit.loc[df_audit["column_name"] == lcol, "in_extended_model_b"].values[0]

    return df_audit
