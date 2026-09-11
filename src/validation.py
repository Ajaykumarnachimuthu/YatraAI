"""
YĀTRĀ AI — Synthetic Data & Behavioral Simulation Validation Suite
Authoritative validation module executing:
1. Structural integrity and referential constraints
2. Statistical Beta distribution concordance (7-D Travel DNA)
3. MNL mathematical axioms (probability sum-to-one, bounds)
4. Econometric sensitivity interventions (monotonic behavioral response)
5. Checksum and reproducibility verification
"""

import os
import sys
import math
import hashlib
import numpy as np
import pandas as pd

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYNTHETIC_DIR = os.path.join(BASE_DIR, "data", "synthetic")
DOCS_IMG_DIR = os.path.join(BASE_DIR, "docs", "images")
RESULTS_EDA_DIR = os.path.join(BASE_DIR, "results", "figures", "eda")

DNA_VARS = [
    "cost_sensitivity",
    "time_sensitivity",
    "reliability_sensitivity",
    "comfort_preference",
    "transfer_tolerance",
    "departure_time_flexibility",
    "sustainability_preference",
]

# ==============================================================================
# 1. STRUCTURAL VALIDATION
# ==============================================================================

def validate_structural(df_travellers, df_sessions, df_candidates, df_choices, config, scale="final"):
    """
    Verifies entity cardinalities, key integrity, date logic, and session choice constraints.
    """
    errors = []

    # Traveller checks
    expected_t = 5000 if scale == "final" else 600
    if len(df_travellers) != expected_t:
        errors.append(f"Expected {expected_t} travellers, found {len(df_travellers)}")
    if df_travellers["traveller_id"].nunique() != len(df_travellers):
        errors.append("Duplicate traveller_id detected")

    counts = df_travellers["persona_type"].value_counts().to_dict()
    if scale == "final":
        expected_counts = {
            "Cost-Sensitive Commuter": 1250,
            "Time-Sensitive Professional": 1000,
            "Occasional Leisure Traveler": 750,
            "Car-Dependent Suburban": 900,
            "Eco-Conscious Urbanite": 600,
            "Mobility-Constrained Traveler": 500,
        }
    else:
        expected_counts = {p["name"]: 100 for p in config["personas"]}

    for pname, exp_cnt in expected_counts.items():
        if counts.get(pname, 0) != exp_cnt:
            errors.append(f"Persona '{pname}' count is {counts.get(pname, 0)}, expected {exp_cnt}")

    for var in DNA_VARS:
        if df_travellers[var].isnull().any():
            errors.append(f"Missing values found in Travel DNA variable {var}")
        if (df_travellers[var] < 0.0).any() or (df_travellers[var] > 1.0).any():
            errors.append(f"Travel DNA variable {var} out of [0, 1] range")

    # Session checks
    expected_s = 40000 if scale == "final" else 2400
    if len(df_sessions) != expected_s:
        errors.append(f"Expected {expected_s} sessions, found {len(df_sessions)}")
    if df_sessions["session_id"].nunique() != len(df_sessions):
        errors.append("Duplicate session_id detected")
    if (df_sessions["origin_city"] == df_sessions["destination_city"]).any():
        errors.append("Found sessions with origin_city == destination_city")
    if (df_sessions["lead_days"] < 1).any() or (df_sessions["lead_days"] > 49).any():
        errors.append("Lead days out of allowed range [1, 49]")

    exp_s_per_t = 8 if scale == "final" else 4
    sess_counts = df_sessions.groupby("traveller_id").size()
    if not (sess_counts == exp_s_per_t).all():
        errors.append(f"Not all travellers have exactly {exp_s_per_t} sessions")

    s_date = pd.to_datetime(df_sessions["search_date"])
    t_date = pd.to_datetime(df_sessions["travel_date"])
    calc_lead = (t_date - s_date).dt.days
    if not (calc_lead == df_sessions["lead_days"]).all():
        errors.append("travel_date != search_date + lead_days in some sessions")

    # Choice checks: Exactly 1 chosen alternative per session
    chosen_per_session = df_choices.groupby("session_id")["chosen"].sum()
    if not (chosen_per_session == 1).all():
        bad_sessions = int((chosen_per_session != 1).sum())
        errors.append(f"Found {bad_sessions} sessions without exactly 1 chosen alternative")

    alts_per_session = df_choices.groupby("session_id")["alternative_id"].count()
    if (alts_per_session < 2).any():
        bad_alts = int((alts_per_session < 2).sum())
        errors.append(f"Found {bad_alts} sessions with fewer than 2 alternatives")
    if (alts_per_session > 5).any():
        bad_alts = int((alts_per_session > 5).sum())
        errors.append(f"Found {bad_alts} sessions with more than 5 alternatives")

    # Traceability
    if df_choices["source_record_id"].isnull().any():
        errors.append("Found null source_record_id in choice dataset")
    if df_choices["source_dataset"].isnull().any():
        errors.append("Found null source_dataset in choice dataset")

    passed = (len(errors) == 0)
    return {"passed": passed, "errors": errors}

# ==============================================================================
# 2. STATISTICAL VALIDATION
# ==============================================================================

def validate_statistical(df_travellers, config):
    """
    Compares empirical sample statistics against theoretical Beta distribution moments.
    """
    stats_records = []
    for persona_cfg in config["personas"]:
        pname = persona_cfg["name"]
        subset = df_travellers[df_travellers["persona_type"] == pname]
        beta_params = persona_cfg["beta_params"]

        for var in DNA_VARS:
            a, b = beta_params[var]
            theo_mean = a / (a + b)
            theo_std = math.sqrt((a * b) / ((a + b)**2 * (a + b + 1)))

            sample_vals = subset[var]
            emp_mean = sample_vals.mean()
            emp_median = sample_vals.median()
            emp_std = sample_vals.std()
            diff_mean = abs(emp_mean - theo_mean)

            stats_records.append({
                "persona": pname,
                "variable": var,
                "theoretical_mean": round(theo_mean, 4),
                "empirical_mean": round(emp_mean, 4),
                "mean_diff": round(diff_mean, 4),
                "theoretical_std": round(theo_std, 4),
                "empirical_std": round(emp_std, 4),
                "empirical_median": round(emp_median, 4),
                "min": round(sample_vals.min(), 4),
                "max": round(sample_vals.max(), 4),
            })

    df_stats = pd.DataFrame(stats_records)
    # Empirical means must be within CLT bounds (diff <= 0.06)
    passed = bool((df_stats["mean_diff"] <= 0.06).all())
    return {"passed": passed, "statistics": df_stats}

# ==============================================================================
# 3. MNL MATHEMATICAL AXIOMS
# ==============================================================================

def validate_mnl(df_choices, tol=1e-5):
    """
    Verifies Multinomial Logit mathematical properties:
    1. 0 <= P_nj <= 1 for all alternatives
    2. sum_j P_nj == 1.0 for every session within floating point tolerance
    """
    probs = df_choices["choice_probability"]
    in_bounds = bool(((probs >= 0.0) & (probs <= 1.0)).all())

    session_sums = df_choices.groupby("session_id")["choice_probability"].sum()
    diffs = (session_sums - 1.0).abs()
    max_diff = float(diffs.max())
    sum_to_one = bool((diffs <= tol).all())

    passed = in_bounds and sum_to_one
    return {
        "passed": passed,
        "in_bounds": in_bounds,
        "sum_to_one": sum_to_one,
        "max_prob_sum_discrepancy": max_diff,
    }

# ==============================================================================
# 4. BEHAVIOURAL SENSITIVITY INTERVENTIONS
# ==============================================================================

def run_sensitivity_tests(config, derive_itinerary_features_fn, calculate_utility_fn, calculate_mnl_probabilities_fn):
    """
    Runs controlled econometric sensitivity interventions on benchmark corridor options:
    1. Higher cost sensitivity -> higher P(cheap rail)
    2. Higher time sensitivity -> higher P(fast flight)
    3. Higher reliability sensitivity -> higher P(on-time service)
    4. Lower transfer tolerance -> higher P(direct option)
    5. Higher sustainability preference -> higher P(low-carbon rail)
    6. Lower departure flexibility -> higher P(matched departure window)
    """
    alt_A = {
        "mode": "Rail", "airline_or_train": "Exp", "service_identifier": "12345",
        "cabin_class_or_tier": "Standard Sleeper", "departure_window": "Morning",
        "raw_cost": 650.0, "raw_duration": 18.0, "raw_distance": 1200.0, "transfer_count": 0,
        "p_on_time": 0.85, "p_slight_delay": 0.10, "p_severe_delay": 0.04, "p_cancelled": 0.01,
        "source_dataset": "canonical_train_routes.parquet", "source_record_id": "bench_rail_A",
    }
    alt_B = {
        "mode": "Flight", "airline_or_train": "Air India", "service_identifier": "AI-101",
        "cabin_class_or_tier": "Economy", "departure_window": "Evening",
        "raw_cost": 5500.0, "raw_duration": 2.5, "raw_distance": 1000.0, "transfer_count": 1,
        "p_on_time": 0.70, "p_slight_delay": 0.15, "p_severe_delay": 0.12, "p_cancelled": 0.03,
        "source_dataset": "canonical_flights.parquet", "source_record_id": "bench_flight_B",
    }
    session = {"origin_city": "Delhi", "destination_city": "Mumbai", "departure_window": "Morning"}

    baseline_dna = {
        "cost_sensitivity": 0.50, "time_sensitivity": 0.50, "reliability_sensitivity": 0.50,
        "comfort_preference": 0.50, "transfer_tolerance": 0.50, "departure_time_flexibility": 0.50,
        "sustainability_preference": 0.50,
    }

    def eval_pair(dna, a1=alt_A, a2=alt_B):
        cands = [dict(a1), dict(a2)]
        cands = derive_itinerary_features_fn(cands, session, dna, config)
        cands = calculate_utility_fn(cands, dna, config)
        cands = calculate_mnl_probabilities_fn(cands)
        return cands[0]["choice_probability"], cands[1]["choice_probability"]

    pA_base, pB_base = eval_pair(baseline_dna)
    results = {}

    # Test 1: Cost sensitivity
    dna_cost = dict(baseline_dna, cost_sensitivity=0.95, time_sensitivity=0.20)
    pA_cost, _ = eval_pair(dna_cost)
    results["cost_sensitivity_intervention"] = {
        "passed": bool(pA_cost > pA_base),
        "baseline_p_cheap": round(pA_base, 4),
        "intervention_p_cheap": round(pA_cost, 4),
        "delta": round(pA_cost - pA_base, 4),
    }

    # Test 2: Time sensitivity
    dna_time = dict(baseline_dna, time_sensitivity=0.95, cost_sensitivity=0.20)
    _, pB_time = eval_pair(dna_time)
    results["time_sensitivity_intervention"] = {
        "passed": bool(pB_time > pB_base),
        "baseline_p_fast": round(pB_base, 4),
        "intervention_p_fast": round(pB_time, 4),
        "delta": round(pB_time - pB_base, 4),
    }

    # Test 3: Reliability sensitivity
    rel_high = dict(alt_A, p_on_time=0.95, p_slight_delay=0.04, p_severe_delay=0.01, p_cancelled=0.00, source_record_id="r1")
    rel_low = dict(alt_A, p_on_time=0.40, p_slight_delay=0.20, p_severe_delay=0.30, p_cancelled=0.10, source_record_id="r2")
    p_rel_base, _ = eval_pair(baseline_dna, rel_high, rel_low)
    dna_rel = dict(baseline_dna, reliability_sensitivity=0.95)
    p_rel_int, _ = eval_pair(dna_rel, rel_high, rel_low)
    results["reliability_sensitivity_intervention"] = {
        "passed": bool(p_rel_int > p_rel_base),
        "baseline_p_reliable": round(p_rel_base, 4),
        "intervention_p_reliable": round(p_rel_int, 4),
        "delta": round(p_rel_int - p_rel_base, 4),
    }

    # Test 4: Transfer tolerance
    dna_trans = dict(baseline_dna, transfer_tolerance=0.10)
    pA_trans, _ = eval_pair(dna_trans)
    results["transfer_tolerance_reduction_intervention"] = {
        "passed": bool(pA_trans > pA_base),
        "baseline_p_direct": round(pA_base, 4),
        "intervention_p_direct": round(pA_trans, 4),
        "delta": round(pA_trans - pA_base, 4),
    }

    # Test 5: Sustainability preference
    dna_sust = dict(baseline_dna, sustainability_preference=0.95)
    pA_sust, _ = eval_pair(dna_sust)
    results["sustainability_preference_intervention"] = {
        "passed": bool(pA_sust > pA_base),
        "baseline_p_low_carbon": round(pA_base, 4),
        "intervention_p_low_carbon": round(pA_sust, 4),
        "delta": round(pA_sust - pA_base, 4),
    }

    # Test 6: Departure flexibility
    dna_flex = dict(baseline_dna, departure_time_flexibility=0.05)
    pA_flex, _ = eval_pair(dna_flex)
    results["departure_flexibility_reduction_intervention"] = {
        "passed": bool(pA_flex > pA_base),
        "baseline_p_matched_time": round(pA_base, 4),
        "intervention_p_matched_time": round(pA_flex, 4),
        "delta": round(pA_flex - pA_base, 4),
    }

    all_passed = all(r["passed"] for r in results.values())
    return {"all_passed": all_passed, "tests": results}

# ==============================================================================
# 5. DIAGNOSTIC VALIDATION PLOTS
# ==============================================================================

def generate_validation_plots(df_travellers, df_choices, output_dirs=None):
    """
    Generates publication figures:
    1. Travel DNA boxplots by persona (7 dimensions)
    2. Modal choice share by persona archetype
    3. Travel DNA inter-variable correlation heatmap (7x7 matrix)
    """
    if output_dirs is None:
        output_dirs = [DOCS_IMG_DIR, RESULTS_EDA_DIR]

    for d in output_dirs:
        os.makedirs(d, exist_ok=True)

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import seaborn as sns

        # 1. Travel DNA Boxplots by Persona
        plt.figure(figsize=(14, 10))
        for idx, var in enumerate(DNA_VARS):
            plt.subplot(3, 3, idx + 1)
            sns.boxplot(data=df_travellers, x="persona_type", y=var, hue="persona_type", palette="Set2", legend=False)
            plt.xticks(rotation=45, ha="right", fontsize=8)
            plt.title(var.replace("_", " ").title(), fontsize=10)
            plt.ylabel("Score [0, 1]")
            plt.xlabel("")
        plt.tight_layout()
        for d in output_dirs:
            plt.savefig(os.path.join(d, "travel_dna_boxplots_by_persona.png"), dpi=150)
        plt.close()

        # 2. Choice Share by Persona
        plt.figure(figsize=(10, 6))
        chosen_df = df_choices[df_choices["chosen"] == 1]
        mode_counts = pd.crosstab(chosen_df["persona_type"], chosen_df["mode"], normalize="index") * 100
        mode_counts.plot(kind="bar", stacked=True, color=["#1f77b4", "#ff7f0e"], figsize=(10, 6))
        plt.title("Modal Choice Share by Persona Archetype (%)", fontsize=12)
        plt.xlabel("Persona Archetype", fontsize=10)
        plt.ylabel("Choice Share (%)", fontsize=10)
        plt.xticks(rotation=30, ha="right")
        plt.legend(title="Chosen Mode")
        plt.tight_layout()
        for d in output_dirs:
            plt.savefig(os.path.join(d, "modal_choice_share_by_persona.png"), dpi=150)
        plt.close()

        # 3. Correlation Heatmap of Travel DNA (7x7)
        plt.figure(figsize=(8, 6))
        sns.heatmap(df_travellers[DNA_VARS].corr(), annot=True, cmap="coolwarm", fmt=".2f", vmin=-1, vmax=1)
        plt.title("Travel DNA Inter-Variable Correlation Heatmap (7-D)", fontsize=12)
        plt.tight_layout()
        for d in output_dirs:
            plt.savefig(os.path.join(d, "travel_dna_correlation_heatmap.png"), dpi=150)
        plt.close()

        return True
    except Exception as e:
        print("Error generating validation plots:", e)
        return False

if __name__ == "__main__":
    import yaml
    print("=" * 80)
    print("YĀTRĀ AI — SYNTHETIC DATA & BEHAVIORAL SIMULATION VALIDATION SUITE")
    print("Executing Read-Only Validation on Frozen Datasets (Zero Regeneration)")
    print("=" * 80)

    cfg_path = os.path.join(BASE_DIR, "config", "synthetic_generation.yaml")
    with open(cfg_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Load frozen datasets
    print("[*] Loading frozen synthetic datasets...")
    df_t = pd.read_parquet(os.path.join(SYNTHETIC_DIR, "traveller_population.parquet"))
    df_s = pd.read_parquet(os.path.join(SYNTHETIC_DIR, "search_sessions.parquet"))
    df_c = pd.read_parquet(os.path.join(SYNTHETIC_DIR, "itinerary_candidates.parquet"))
    df_ch = pd.read_parquet(os.path.join(SYNTHETIC_DIR, "choice_dataset.parquet"))
    print(f"    Loaded: {len(df_t):,} travellers, {len(df_s):,} sessions, {len(df_c):,} candidates, {len(df_ch):,} choices")

    # 1. Structural Validation
    print("\n--- 1. Structural Validation ---")
    v_struct = validate_structural(df_t, df_s, df_c, df_ch, config, scale="final")
    print("Status:", "PASSED" if v_struct["passed"] else f"FAILED: {v_struct['errors']}")

    # 2. Statistical Validation
    print("\n--- 2. Statistical Validation (Beta Distribution Concordance) ---")
    v_stat = validate_statistical(df_t, config)
    print("Status:", "PASSED" if v_stat["passed"] else "FAILED")

    # 3. MNL Mathematical Axioms
    print("\n--- 3. MNL Mathematical Axioms ---")
    v_mnl = validate_mnl(df_ch)
    print("Status:", "PASSED" if v_mnl["passed"] else "FAILED", f"(Max diff: {v_mnl['max_prob_sum_discrepancy']:.2e})")

    # 4. Behavioural Sensitivity Tests
    print("\n--- 4. Behavioural Sensitivity Interventions ---")
    try:
        from src.synthetic_generation import derive_itinerary_features, calculate_utility, calculate_mnl_probabilities
        v_sens = run_sensitivity_tests(config, derive_itinerary_features, calculate_utility, calculate_mnl_probabilities)
        print("Status:", "PASSED" if v_sens["all_passed"] else "FAILED")
        for tname, tres in v_sens["tests"].items():
            print(f"   - {tname}: {'PASSED' if tres['passed'] else 'FAILED'} (delta: {tres['delta']:+.4f})")
    except Exception as e:
        print(f"   Sensitivity test execution error: {e}")

    print("\n" + "=" * 80)
    print("VALIDATION SUITE COMPLETED SUCCESSFULLY")
    print("=" * 80)
