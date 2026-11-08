"""
YATRA AI — Application Recommendation & ML Personalization Engine
Authoritative orchestration service connecting:
- Search query validation & hard operational constraints
- Authentic multimodal candidate retrieval from canonical transport datasets
- Pre-choice choice-set multi-attribute quality scoring
- Standalone inference using frozen HistGradientBoosting champion model (results/models/champion_gb_core.joblib)
- Continuous probability scoring, tau*=0.30 preference thresholding, and pointwise ranking
- Feature-grounded, honest recommendation explanation generation
"""

import os
import sys
import logging
import pandas as pd
import numpy as np

# Ensure repository root is on Python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Silence joblib/loky Windows CPU count warning
os.environ.setdefault("LOKY_MAX_CPU_COUNT", str(os.cpu_count() or 4))

try:
    from ml.synthetic_generation import preindex_real_data, retrieve_real_candidates, load_config
    from ml.feature_engineering import compute_candidate_scores, CORE_FEATURES, TRAVEL_DNA_FEATURES
    from ml.train_models import load_champion_pipeline, YatraChoiceInferenceEngine
except ImportError:
    from src.synthetic_generation import preindex_real_data, retrieve_real_candidates, load_config
    from src.feature_engineering import compute_candidate_scores, CORE_FEATURES, TRAVEL_DNA_FEATURES
    from src.train_models import load_champion_pipeline, YatraChoiceInferenceEngine

logger = logging.getLogger("yatra.recommendation_engine")


class HardConstraintViolation(ValueError):
    """Raised when travel query violates operational or geographic feasibility constraints."""
    pass


class RecommendationEngine:
    """
    Application-level orchestration layer for personalized travel journey recommendations.
    Decoupled from model specifics by relying on YatraChoiceInferenceEngine.
    """

    def __init__(self, config_path=None, model_path=None):
        logger.info("Initializing Yatra AI Recommendation Engine...")
        self.config = load_config(config_path) if config_path else load_config()
        self.indexed_data = preindex_real_data()
        self.engine: YatraChoiceInferenceEngine = load_champion_pipeline(model_path)
        self.metro_cities = self.config["session_space"]["metro_cities"]
        self.departure_windows = self.config["session_space"]["departure_windows"]
        logger.info(
            "Recommendation Engine successfully initialized with champion model (threshold=%.2f, features=%s)",
            self.engine.threshold,
            self.engine.feature_config,
        )

    def get_supported_corridors(self):
        """Returns list of supported metro cities and directed corridors."""
        corridors = [
            {"origin": c1, "destination": c2}
            for c1 in self.metro_cities
            for c2 in self.metro_cities
            if c1 != c2
        ]
        return {
            "metro_cities": self.metro_cities,
            "corridors_count": len(corridors),
            "corridors": corridors,
        }

    def get_supported_personas(self):
        """
        Returns persona archetypes with their statistical mean Travel DNA coordinates
        derived analytically from the validated Beta distribution parameters (mean = a / (a + b)).
        """
        personas_out = []
        for p in self.config["personas"]:
            name = p["name"]
            beta_params = p["beta_params"]
            mean_dna = {}
            for dim in TRAVEL_DNA_FEATURES:
                a, b = beta_params[dim]
                mean_dna[dim] = round(float(a / (a + b)), 4)
            personas_out.append({
                "persona_name": name,
                "travel_dna": mean_dna,
                "purpose_distribution": p.get("purpose_distribution", {}),
            })
        return personas_out

    def validate_hard_constraints(self, query: dict):
        """
        Enforces operational and geographic feasibility constraints before ML scoring.
        ML personalization must never override operational feasibility.
        """
        orig = query.get("origin_city")
        dest = query.get("destination_city")
        dep_win = query.get("departure_window", "Morning")
        party_sz = query.get("party_size", 1)
        lead_days = query.get("lead_days", 14)

        if not orig or orig not in self.metro_cities:
            raise HardConstraintViolation(
                f"Invalid origin city '{orig}'. Must be one of: {', '.join(self.metro_cities)}"
            )

        if not dest or dest not in self.metro_cities:
            raise HardConstraintViolation(
                f"Invalid destination city '{dest}'. Must be one of: {', '.join(self.metro_cities)}"
            )

        if orig == dest:
            raise HardConstraintViolation(
                f"Origin and destination cannot be the same city ({orig}). Inter-city transit requires distinct endpoints."
            )

        if dep_win not in self.departure_windows:
            raise HardConstraintViolation(
                f"Invalid departure window '{dep_win}'. Must be one of: {', '.join(self.departure_windows)}"
            )

        if not (1 <= party_sz <= 10):
            raise HardConstraintViolation(
                f"Party size {party_sz} is out of allowable booking range [1, 10]."
            )

        if not (0 <= lead_days <= 120):
            raise HardConstraintViolation(
                f"Lead days {lead_days} is outside valid advance booking window [0, 120]."
            )

    def _normalize_travel_dna(self, raw_dna: dict) -> dict:
        """Ensures all 7 Travel DNA dimensions exist and are clipped to [0.0, 1.0]."""
        normalized = {}
        for dim in TRAVEL_DNA_FEATURES:
            val = raw_dna.get(dim, 0.50)
            try:
                f_val = float(val)
            except (ValueError, TypeError):
                f_val = 0.50
            normalized[dim] = round(max(0.0, min(1.0, f_val)), 4)
        return normalized

    def _generate_feature_reasons(self, cand: dict, all_cands: list) -> list:
        """
        Derives human-interpretable recommendation explanations strictly from candidate features.
        Zero fabricated reasons: every reason reflects an empirical attribute or comparative rank.
        """
        reasons = []

        # Comparative duration
        min_dur = min(c["raw_duration"] for c in all_cands)
        if cand["raw_duration"] <= min_dur + 0.1:
            reasons.append(f"Fastest travel time in choice set ({cand['raw_duration']:.1f} hrs)")

        # Comparative fare
        min_cost = min(c["raw_cost"] for c in all_cands)
        if cand["raw_cost"] <= min_cost + 10.0:
            reasons.append(f"Lowest fare option available (₹{cand['raw_cost']:,.0f})")

        # Zero transfers / direct connection
        if cand.get("transfer_count", 0) == 0:
            reasons.append("Direct non-stop service (no intermediate transfers)")

        # Operational punctuality
        ontime = cand.get("p_on_time", 0.0)
        sev_delay = cand.get("p_severe_delay", 0.0)
        if ontime >= 0.80 and sev_delay <= 0.05:
            reasons.append(f"High historical punctuality ({ontime * 100:.0f}% on-time arrival rate)")

        # Carbon footprint
        min_carbon = min(c.get("carbon_estimate", c.get("carbon_estimate_kg", 999)) for c in all_cands)
        c_val = cand.get("carbon_estimate", cand.get("carbon_estimate_kg", 0))
        if c_val <= min_carbon + 2.0:
            reasons.append(f"Eco-friendly choice with lowest carbon emissions ({c_val:.1f} kg CO₂)")

        # Departure window alignment
        dep_fit = cand.get("departure_fit", 0.0)
        if dep_fit >= 0.95:
            reasons.append(f"Optimal departure schedule matching {cand['departure_window']}")

        # Premium comfort tier
        tier = str(cand.get("cabin_class_or_tier", ""))
        if "Business" in tier or "Premium" in tier or "1AC" in tier or "2AC" in tier:
            reasons.append(f"Enhanced journey comfort tier ({tier})")

        if not reasons:
            reasons.append("Balanced multi-attribute journey option")

        return reasons

    def recommend(self, query: dict, traveller_dna: dict, seed: int = None) -> dict:
        """
        End-to-end recommendation workflow:
        1. Hard constraint validation
        2. Real candidate retrieval from indexed transport corpus
        3. Choice-set relative quality score calculation
        4. Feature matrix assembly matching the 28 Core features
        5. Pointwise inference using champion HistGradientBoosting model
        6. Candidate ranking based on continuous P(chosen)
        7. Feature-grounded explanation generation
        """
        # Step 1: Validate hard operational constraints
        self.validate_hard_constraints(query)

        dna = self._normalize_travel_dna(traveller_dna or {})
        session = {
            "origin_city": query["origin_city"],
            "destination_city": query["destination_city"],
            "departure_window": query.get("departure_window", "Morning"),
            "trip_purpose": query.get("trip_purpose", "Leisure"),
            "party_size": int(query.get("party_size", 1)),
            "lead_days": int(query.get("lead_days", 14)),
        }

        # Step 2: Retrieve authentic candidates
        raw_candidates = retrieve_real_candidates(
            session=session,
            indexed_data=self.indexed_data,
            config=self.config,
            seed=seed,
        )

        if not raw_candidates:
            raise RuntimeError(
                f"No transport candidates found for corridor {session['origin_city']} -> {session['destination_city']}."
            )

        # Step 3: Compute pre-choice choice-set relative quality scores
        # Deep copy to ensure idempotent evaluation
        cands_copy = [dict(c) for c in raw_candidates]
        scored_candidates = compute_candidate_scores(
            candidates=cands_copy,
            session=session,
            traveller=dna,
            config=self.config,
        )

        # Step 4: Construct DataFrame conforming strictly to the 28 Core Features
        feature_rows = []
        for c in scored_candidates:
            row = {
                # 7 Travel DNA features
                "cost_sensitivity": dna["cost_sensitivity"],
                "time_sensitivity": dna["time_sensitivity"],
                "reliability_sensitivity": dna["reliability_sensitivity"],
                "comfort_preference": dna["comfort_preference"],
                "transfer_tolerance": dna["transfer_tolerance"],
                "departure_time_flexibility": dna["departure_time_flexibility"],
                "sustainability_preference": dna["sustainability_preference"],
                # 2 Session context numerics
                "party_size": session["party_size"],
                "lead_days": session["lead_days"],
                # 5 Physical candidate features
                "raw_cost": float(c["raw_cost"]),
                "raw_duration": float(c["raw_duration"]),
                "raw_distance": float(c["raw_distance"]),
                "carbon_estimate_kg": float(c.get("carbon_estimate", c.get("carbon_estimate_kg", 0.0))),
                "transfer_count": int(c["transfer_count"]),
                # 7 Derived relative quality scores
                "cost_score": float(c["cost_score"]),
                "time_score": float(c["time_score"]),
                "reliability_score": float(c["reliability_score"]),
                "comfort_score": float(c["comfort_score"]),
                "transfer_score": float(c["transfer_score"]),
                "carbon_score": float(c["carbon_score"]),
                "departure_fit": float(c["departure_fit"]),
                # 7 Categorical core features
                "origin_city": session["origin_city"],
                "destination_city": session["destination_city"],
                "departure_window": session["departure_window"],
                "trip_purpose": session["trip_purpose"],
                "mode": str(c["mode"]),
                "carrier": str(c["airline_or_train"]),
                "service_tier": str(c["cabin_class_or_tier"]),
            }
            feature_rows.append(row)

        df_features = pd.DataFrame(feature_rows)

        # Verify all 28 core features are present
        missing = [f for f in CORE_FEATURES if f not in df_features.columns]
        if missing:
            raise ValueError(f"Feature schema mismatch. Missing features: {missing}")

        # Step 5 & 6: ML inference and pointwise ranking
        ranked_df = self.engine.rank_itineraries(df_features)

        # Step 7: Assemble application response
        ranked_itineraries = []
        for rank_idx, (orig_idx, row) in enumerate(ranked_df.iterrows(), start=1):
            cand_meta = scored_candidates[orig_idx]
            ml_prob = float(row["predicted_choice_probability"])
            is_chosen_binary = bool(row["predicted_chosen"])

            itinerary_item = {
                "rank": rank_idx,
                "is_recommended": rank_idx == 1,
                "preference_threshold_met": is_chosen_binary,
                "ml_personalization_score": round(ml_prob, 4),
                "mode": cand_meta["mode"],
                "carrier": cand_meta["airline_or_train"],
                "service_identifier": str(cand_meta["service_identifier"]),
                "service_tier": cand_meta["cabin_class_or_tier"],
                "departure_window": cand_meta["departure_window"],
                "cost_inr": round(float(cand_meta["raw_cost"]), 2),
                "duration_hours": round(float(cand_meta["raw_duration"]), 2),
                "distance_km": round(float(cand_meta["raw_distance"]), 1),
                "transfer_count": int(cand_meta["transfer_count"]),
                "carbon_estimate_kg": round(float(cand_meta.get("carbon_estimate", cand_meta.get("carbon_estimate_kg", 0.0))), 2),
                "historical_punctuality_rate": round(float(cand_meta.get("p_on_time", 0.85)), 2),
                "relative_quality_scores": {
                    "cost": cand_meta["cost_score"],
                    "time": cand_meta["time_score"],
                    "reliability": cand_meta["reliability_score"],
                    "comfort": cand_meta["comfort_score"],
                    "carbon": cand_meta["carbon_score"],
                    "departure_fit": cand_meta["departure_fit"],
                },
                "feature_reasons": self._generate_feature_reasons(cand_meta, scored_candidates),
            }
            ranked_itineraries.append(itinerary_item)

        recommended = ranked_itineraries[0] if ranked_itineraries else None

        return {
            "status": "success",
            "search_query": session,
            "traveller_dna": dna,
            "total_candidates": len(ranked_itineraries),
            "recommended_journey": recommended,
            "itineraries": ranked_itineraries,
            "scoring_metadata": {
                "model_family": "HistGradientBoostingClassifier",
                "feature_configuration": "Core (28 features)",
                "decision_threshold": self.engine.threshold,
                "ranking_method": "Pointwise choice probability",
            },
        }


# Global singleton instance for high-efficiency reuse across API queries
_singleton_engine = None


def get_recommendation_engine() -> RecommendationEngine:
    """Returns or lazily creates global RecommendationEngine singleton."""
    global _singleton_engine
    if _singleton_engine is None:
        _singleton_engine = RecommendationEngine()
    return _singleton_engine
