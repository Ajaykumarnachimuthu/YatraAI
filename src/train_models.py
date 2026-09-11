"""
YĀTRĀ AI — Supervised Model Training & Serialization Engine
Authoritative module for:
- Standardized model instantiation across 4 families:
  1. Regularized Logistic Regression (L2, C=1.0)
  2. Regularized Decision Tree (max_depth=6, min_samples_leaf=20)
  3. Random Forest (n_estimators=100, max_depth=10, min_samples_leaf=10)
  4. Histogram-based Gradient Boosting (max_iter=100, max_depth=6, lr=0.1)
- Model training on Core (Model A, 28 features) vs Extended (Model B, 29 features)
- Champion inference pipeline packaging and serialization (.joblib)
"""

import os
import sys
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "results", "models")
os.makedirs(MODELS_DIR, exist_ok=True)

SEED = 42

# ==============================================================================
# 1. MODEL FACTORY
# ==============================================================================

def get_model_specs(seed=SEED):
    """
    Returns the authoritative dictionary of model specifications and estimators.
    Hyperparameters strictly preserved from baseline specifications.
    """
    return {
        "LR": {
            "name": "Logistic Regression",
            "matrix_type": "linear",
            "estimator": LogisticRegression(C=1.0, max_iter=1000, random_state=seed),
        },
        "DT": {
            "name": "Decision Tree",
            "matrix_type": "tree",
            "estimator": DecisionTreeClassifier(max_depth=6, min_samples_leaf=20, random_state=seed),
        },
        "RF": {
            "name": "Random Forest",
            "matrix_type": "tree",
            "estimator": RandomForestClassifier(n_estimators=100, max_depth=10, min_samples_leaf=10, random_state=seed, n_jobs=-1),
        },
        "GB": {
            "name": "Gradient Boosting",
            "matrix_type": "tree",
            "estimator": HistGradientBoostingClassifier(max_iter=100, max_depth=6, min_samples_leaf=20, learning_rate=0.1, random_state=seed),
        },
    }

# ==============================================================================
# 2. TRAINING ORCHESTRATION
# ==============================================================================

def train_all_models(matrices_dict, feature_config="core", seed=SEED):
    """
    Trains all four model families using pre-transformed feature matrices.
    Returns a dictionary of trained (model, feature_names).
    """
    specs = get_model_specs(seed=seed)
    trained = {}
    y_train = matrices_dict["y_train"]

    config_label = "Core (Model A)" if feature_config == "core" else "Extended (Model B)"

    for key, spec in specs.items():
        m_type = spec["matrix_type"]
        X_train = matrices_dict[m_type]["X_train"]
        feat_names = matrices_dict[m_type]["feature_names"]
        estimator = spec["estimator"]

        print(f"  Training {spec['name']} [{config_label}] on {X_train.shape[0]:,} samples x {X_train.shape[1]} features...")
        estimator.fit(X_train, y_train)

        model_id = f"{key}_{config_label}"
        trained[model_id] = (estimator, feat_names)

    return trained

# ==============================================================================
# 3. CHAMPION INFERENCE ENGINE & PIPELINE SERIALIZATION
# ==============================================================================

class YatraChoiceInferenceEngine:
    """
    Production-grade inference wrapper packaging preprocessor, trained estimator,
    and optimal decision threshold for real-time itinerary choice scoring.
    """
    def __init__(self, preprocessor, model, threshold=0.30, feature_config="core", metadata=None):
        self.preprocessor = preprocessor
        self.model = model
        self.threshold = float(threshold)
        self.feature_config = feature_config
        self.metadata = metadata or {}

    def predict_proba(self, df_candidates):
        """Transforms raw candidate records and outputs P(chosen == 1)."""
        X_trans = self.preprocessor.transform(df_candidates)
        if hasattr(self.model, "predict_proba"):
            return self.model.predict_proba(X_trans)[:, 1]
        return self.model.decision_function(X_trans)

    def predict(self, df_candidates):
        """Applies decision threshold to output binary recommendation (0 or 1)."""
        probs = self.predict_proba(df_candidates)
        return (probs >= self.threshold).astype(int)

    def rank_itineraries(self, df_candidates):
        """Scores and ranks a set of alternatives within a search session."""
        df_out = df_candidates.copy()
        probs = self.predict_proba(df_candidates)
        df_out["predicted_choice_probability"] = probs
        df_out["predicted_chosen"] = (probs >= self.threshold).astype(int)
        return df_out.sort_values("predicted_choice_probability", ascending=False)

def save_champion_pipeline(preprocessor, model, threshold=0.30, filepath=None, metadata=None):
    """
    Serializes complete production inference pipeline to results/models/.
    """
    if filepath is None:
        filepath = os.path.join(MODELS_DIR, "champion_gb_core.joblib")

    engine = YatraChoiceInferenceEngine(
        preprocessor=preprocessor,
        model=model,
        threshold=threshold,
        feature_config="core",
        metadata=metadata,
    )

    joblib.dump(engine, filepath)
    print(f"Saved champion inference engine to: {filepath}")
    return filepath

def load_champion_pipeline(filepath=None):
    """Loads serialized inference engine."""
    if filepath is None:
        filepath = os.path.join(MODELS_DIR, "champion_gb_core.joblib")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Model artifact not found at: {filepath}")
    return joblib.load(filepath)
