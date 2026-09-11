"""
YĀTRĀ AI — Phase 3: Synthetic Traveller Behaviour & Travel DNA Generation Engine
Modular pipeline implementing:
- Persona Beta-distribution Travel DNA sampling
- Persistent traveller population generation
- Search session simulation across 30 metro corridors
- Authentic candidate itinerary retrieval from real canonical datasets
- Multi-attribute score derivation (Cost, Time, Transfer, Reliability, Comfort, Carbon, Departure Fit)
- Multinomial Logit (MNL) utility calculation and probabilistic choice sampling
- Automated comprehensive validation suite (Structural, Statistical, Behavioural Sensitivity, MNL, Reproducibility)
"""

import os
import sys
import yaml
import math
import hashlib
import numpy as np
import pandas as pd
from scipy.stats import beta as beta_dist

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "synthetic_generation.yaml")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
SYNTHETIC_DIR = os.path.join(BASE_DIR, "data", "synthetic")
DOCS_IMG_DIR = os.path.join(BASE_DIR, "docs", "images")

os.makedirs(SYNTHETIC_DIR, exist_ok=True)
os.makedirs(DOCS_IMG_DIR, exist_ok=True)

def load_config(config_path=CONFIG_PATH):
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# ==============================================================================
# 1. TRAVELLER POPULATION GENERATION
# ==============================================================================
def generate_travellers(config, scale="final", seed=None):
    """
    Generates the persistent traveller population.
    Each traveller receives 7 continuous Travel DNA variables sampled from persona Beta distributions.
    """
    if seed is None:
        seed = config["reproducibility"]["seed"]
    rng = np.random.default_rng(seed)
    
    dna_vars = [
        "cost_sensitivity",
        "time_sensitivity",
        "reliability_sensitivity",
        "comfort_preference",
        "transfer_tolerance",
        "departure_time_flexibility",
        "sustainability_preference"
    ]
    
    if scale == "pilot":
        target_counts = {p["name"]: config["population"]["pilot"]["travellers_per_persona"] for p in config["personas"]}
    else:
        # Final target persona mix:
        # 1. Cost-Sensitive Commuter: 25% = 1,250
        # 2. Time-Sensitive Professional: 20% = 1,000
        # 3. Occasional Leisure Traveler: 15% = 750
        # 4. Car-Dependent Suburban: 18% = 900
        # 5. Eco-Conscious Urbanite: 12% = 600
        # 6. Mobility-Constrained Traveler: 10% = 500
        target_counts = {
            "Cost-Sensitive Commuter": 1250,
            "Time-Sensitive Professional": 1000,
            "Occasional Leisure Traveler": 750,
            "Car-Dependent Suburban": 900,
            "Eco-Conscious Urbanite": 600,
            "Mobility-Constrained Traveler": 500
        }
    
    rows = []
    tid_counter = 1
    
    for persona_cfg in config["personas"]:
        persona_name = persona_cfg["name"]
        n_p = target_counts[persona_name]
        beta_params = persona_cfg["beta_params"]
        
        # Sample Beta variables for n_p
        persona_dna = {}
        for var in dna_vars:
            a, b = beta_params[var]
            samples = rng.beta(a, b, size=n_p)
            persona_dna[var] = np.clip(samples, 0.001, 0.999)
            
        for i in range(n_p):
            tid_str = f"T{tid_counter:06d}"
            row = {
                "traveller_id": tid_str,
                "persona_type": persona_name
            }
            for var in dna_vars:
                row[var] = round(float(persona_dna[var][i]), 4)
            rows.append(row)
            tid_counter += 1
            
    df_travellers = pd.DataFrame(rows)
    return df_travellers

# ==============================================================================
# 2. SEARCH SESSIONS GENERATION
# ==============================================================================
def generate_sessions(travellers_df, config, scale="final", seed=None):
    """
    Generates search sessions for each traveller.
    Travel DNA remains strictly persistent per traveller across all sessions.
    """
    if seed is None:
        seed = config["reproducibility"]["seed"] + 101
    rng = np.random.default_rng(seed)
    
    sess_cfg = config["session_space"]
    cities = sess_cfg["metro_cities"]
    dep_windows = sess_cfg["departure_windows"]
    lead_min = sess_cfg["lead_days_min"]
    lead_max = sess_cfg["lead_days_max"]
    base_date = pd.to_datetime(sess_cfg["base_search_date"])
    
    if scale == "pilot":
        sessions_per_traveller = config["population"]["pilot"]["sessions_per_traveller"]
    else:
        sessions_per_traveller = config["population"]["final_target"]["sessions_per_traveller"]
    
    # 30 directed corridors
    corridors = [(c1, c2) for c1 in cities for c2 in cities if c1 != c2]
    
    persona_map = {p["name"]: p for p in config["personas"]}
    
    session_rows = []
    sess_counter = 1
    
    for _, trav in travellers_df.iterrows():
        tid = trav["traveller_id"]
        persona_name = trav["persona_type"]
        p_cfg = persona_map[persona_name]
        
        # Distributions for purpose and party size
        purposes = list(p_cfg["purpose_distribution"].keys())
        p_weights = list(p_cfg["purpose_distribution"].values())
        
        party_sizes = [int(k) for k in p_cfg["party_size_distribution"].keys()]
        ps_weights = list(p_cfg["party_size_distribution"].values())
        
        for s_idx in range(sessions_per_traveller):
            sess_id = f"S{sess_counter:07d}"
            
            # Sample corridor uniformly
            c_idx = rng.integers(0, len(corridors))
            orig, dest = corridors[c_idx]
            
            # Lead days and dates
            lead_days = int(rng.integers(lead_min, lead_max + 1))
            search_date = base_date + pd.Timedelta(days=int(rng.integers(0, 30)))
            travel_date = search_date + pd.Timedelta(days=lead_days)
            
            dep_win = str(rng.choice(dep_windows))
            purpose = str(rng.choice(purposes, p=p_weights))
            party_sz = int(rng.choice(party_sizes, p=ps_weights))
            
            session_rows.append({
                "session_id": sess_id,
                "traveller_id": tid,
                "origin_city": orig,
                "destination_city": dest,
                "search_date": search_date.strftime("%Y-%m-%d"),
                "travel_date": travel_date.strftime("%Y-%m-%d"),
                "lead_days": lead_days,
                "departure_window": dep_win,
                "trip_purpose": purpose,
                "party_size": party_sz
            })
            sess_counter += 1
            
    df_sessions = pd.DataFrame(session_rows)
    return df_sessions

# ==============================================================================
# 3. REAL ITINERARY CANDIDATE RETRIEVAL
# ==============================================================================
def preindex_real_data(processed_dir=PROCESSED_DIR):
    """
    Loads and indexes canonical flights and trains for fast corridor retrieval.
    """
    flights_path = os.path.join(processed_dir, "canonical_flights.parquet")
    trains_srv_path = os.path.join(processed_dir, "canonical_train_services.parquet")
    trains_routes_path = os.path.join(processed_dir, "canonical_train_routes.parquet")
    stations_path = os.path.join(processed_dir, "canonical_stations.parquet")
    delays_path = os.path.join(processed_dir, "canonical_train_delays.parquet")
    
    df_fl = pd.read_parquet(flights_path)
    df_ts = pd.read_parquet(trains_srv_path)
    df_tr = pd.read_parquet(trains_routes_path)
    df_st = pd.read_parquet(stations_path)
    df_dl = pd.read_parquet(delays_path)
    
    # Station delay index (canonical_station_code -> mean delay stats)
    station_delays = df_dl.groupby("canonical_station_code").agg({
        "p_on_time": "mean",
        "p_slight_delay": "mean",
        "p_severe_delay": "mean",
        "p_cancelled": "mean",
        "mean_delay_minutes": "mean"
    }).to_dict("index")
    
    # Pre-index train routes between metro clusters
    metro_stns = df_st[df_st["metro_cluster"] != "OTHER"][["station_code", "metro_cluster"]]
    r_metro = df_tr.merge(metro_stns, on="station_code", how="inner")
    
    # Find direct train legs between metro clusters
    pairs = r_metro.merge(r_metro, on="train_number", suffixes=("_src", "_dst"))
    pairs = pairs[pairs["sequence_dst"] > pairs["sequence_src"]]
    pairs = pairs[pairs["metro_cluster_src"] != pairs["metro_cluster_dst"]]
    
    # Join train services
    pairs = pairs.merge(df_ts[["train_number", "train_name", "train_type"]], on="train_number", how="left")
    
    # Calculate travel duration in hours
    def calc_train_dur(row):
        dep_min = row["departure_minutes_from_midnight_src"]
        arr_min = row["arrival_minutes_from_midnight_dst"]
        day_diff = row["journey_day_dst"] - row["journey_day_src"]
        if pd.isna(dep_min) or pd.isna(arr_min):
            return 18.0 # Default fallback
        tot_min = (day_diff * 1440) + arr_min - dep_min
        if tot_min <= 0:
            tot_min += 1440
        return max(1.0, round(tot_min / 60.0, 2))
        
    pairs["duration_hours"] = pairs.apply(calc_train_dur, axis=1)
    
    # Leg distance
    def calc_train_dist(row):
        cum_dst = row["cumulative_haversine_km_dst"]
        cum_src = row["cumulative_haversine_km_src"]
        if not pd.isna(cum_dst) and not pd.isna(cum_src) and (cum_dst > cum_src):
            return round(cum_dst - cum_src, 1)
        return round(row.get("segment_haversine_km_dst", 800.0), 1)
        
    pairs["distance_km"] = pairs.apply(calc_train_dist, axis=1)
    
    # Map departure window
    def map_train_dep_window(dep_min):
        if pd.isna(dep_min):
            return "Morning"
        hr = dep_min / 60.0
        if 4.0 <= hr < 8.0:
            return "Early Morning"
        elif 8.0 <= hr < 12.0:
            return "Morning"
        elif 12.0 <= hr < 16.0:
            return "Afternoon"
        elif 16.0 <= hr < 20.0:
            return "Evening"
        else:
            return "Night"
            
    pairs["departure_window"] = pairs["departure_minutes_from_midnight_src"].apply(map_train_dep_window)
    
    # Clean up train options table
    train_options = pairs[[
        "train_number", "train_name", "train_type",
        "metro_cluster_src", "metro_cluster_dst",
        "station_code_src", "station_code_dst",
        "departure_window", "duration_hours", "distance_km"
    ]].drop_duplicates(subset=["train_number", "metro_cluster_src", "metro_cluster_dst"]).reset_index(drop=True)
    
    # Pre-index flight pools for fast corridor/window lookup
    fl_pools = {}
    for (src, dst, win), group in df_fl.groupby(["source_city", "destination_city", "departure_time_window"]):
        fl_pools[(src, dst, win)] = group
    for (src, dst), group in df_fl.groupby(["source_city", "destination_city"]):
        fl_pools[(src, dst, "ALL")] = group
        
    # Pre-index train pools for fast corridor/window lookup
    tr_pools = {}
    for (src, dst, win), group in train_options.groupby(["metro_cluster_src", "metro_cluster_dst", "departure_window"]):
        tr_pools[(src, dst, win)] = group
    for (src, dst), group in train_options.groupby(["metro_cluster_src", "metro_cluster_dst"]):
        tr_pools[(src, dst, "ALL")] = group
        
    return {
        "flights": df_fl,
        "train_options": train_options,
        "station_delays": station_delays,
        "fl_pools": fl_pools,
        "tr_pools": tr_pools
    }

def retrieve_real_candidates(session, indexed_data, config, seed=None):
    """
    Retrieves 2 to 5 genuine alternatives for a search session from real flights and train options.
    Preserves raw source attributes and source traceability.
    """
    if seed is not None:
        rng = np.random.default_rng(seed)
    else:
        rng = np.random.default_rng()
        
    orig = session["origin_city"]
    dest = session["destination_city"]
    pref_win = session["departure_window"]
    
    station_delays = indexed_data["station_delays"]
    fare_cfg = config["itinerary_attributes"]["rail_fares_irctc_telescopic"]
    fl_pools = indexed_data.get("fl_pools")
    tr_pools = indexed_data.get("tr_pools")
    
    # 1. Filter Flights on Corridor
    if fl_pools is not None:
        fl_win = fl_pools.get((orig, dest, pref_win))
        if fl_win is None or len(fl_win) < 2:
            fl_win = fl_pools.get((orig, dest, "ALL"))
        if fl_win is None:
            fl_win = pd.DataFrame()
        fl_pool = fl_pools.get((orig, dest, "ALL"), pd.DataFrame())
    else:
        df_fl = indexed_data["flights"]
        fl_pool = df_fl[(df_fl["source_city"] == orig) & (df_fl["destination_city"] == dest)]
        fl_win = fl_pool[fl_pool["departure_time_window"] == pref_win]
        if len(fl_win) < 2:
            fl_win = fl_pool
        
    # 2. Filter Trains on Corridor
    if tr_pools is not None:
        tr_win = tr_pools.get((orig, dest, pref_win))
        if tr_win is None or len(tr_win) < 1:
            tr_win = tr_pools.get((orig, dest, "ALL"))
        if tr_win is None:
            tr_win = pd.DataFrame()
    else:
        df_tr = indexed_data["train_options"]
        tr_pool = df_tr[(df_tr["metro_cluster_src"] == orig) & (df_tr["metro_cluster_dst"] == dest)]
        tr_win = tr_pool[tr_pool["departure_window"] == pref_win]
        if len(tr_win) < 1:
            tr_win = tr_pool
        
    candidates = []
    
    # Sample 1-3 Flights (if available)
    if len(fl_win) > 0:
        n_fl = min(len(fl_win), int(rng.integers(1, 4)))
        sampled_fl_indices = rng.choice(fl_win.index, size=n_fl, replace=False)
        for fidx in sampled_fl_indices:
            fl_row = fl_win.loc[fidx]
            dist_km = fl_row["direct_flight_distance_km"]
            if pd.isna(dist_km) or dist_km <= 0:
                dist_km = 1000.0
            candidates.append({
                "mode": "Flight",
                "airline_or_train": fl_row["airline"],
                "service_identifier": fl_row["flight_number"],
                "cabin_class_or_tier": fl_row["cabin_class"],
                "departure_window": fl_row["departure_time_window"],
                "raw_cost": float(fl_row["price_inr"]),
                "raw_duration": float(fl_row["duration_hours"]),
                "raw_distance": float(dist_km),
                "transfer_count": int(fl_row["stops"]),
                "p_on_time": 0.88, # Documented neutral baseline for domestic flights
                "p_slight_delay": 0.08,
                "p_severe_delay": 0.03,
                "p_cancelled": 0.01,
                "is_empirical_delay": False,
                "source_dataset": "canonical_flights.parquet",
                "source_record_id": f"flight_{fl_row['flight_number']}_{fidx}"
            })
            
    # Sample 1-2 Trains (if available)
    if len(tr_win) > 0:
        n_tr = min(len(tr_win), int(rng.integers(1, 3)))
        sampled_tr_indices = rng.choice(tr_win.index, size=n_tr, replace=False)
        for tidx in sampled_tr_indices:
            tr_row = tr_win.loc[tidx]
            dist_km = float(tr_row["distance_km"])
            ttype = tr_row["train_type"]
            is_premium = ttype in ["Raj", "Tejas", "Drnt", "Shtb"]
            
            # Sample class tier: Sleeper, 3AC, 2AC, or 1AC
            tier_choice = rng.choice(["3AC", "Sleeper", "2AC"], p=[0.55, 0.25, 0.20])
            if tier_choice == "Sleeper":
                cost = fare_cfg["base_sleeper_per_km"] * dist_km
                tier_label = "Standard Sleeper"
            elif tier_choice == "3AC":
                cost = fare_cfg["base_3ac_per_km"] * dist_km + fare_cfg["superfast_surcharge"]
                tier_label = "3-Tier AC"
            else:
                cost = fare_cfg["base_2ac_per_km"] * dist_km + fare_cfg["superfast_surcharge"] * 1.5
                tier_label = "2-Tier AC"
                
            if is_premium:
                cost *= fare_cfg["rajdhani_surcharge_multiplier"]
                tier_label = f"Premium {tier_label}"
                
            # Lookup empirical station delay
            stn_dst = tr_row["station_code_dst"]
            del_info = station_delays.get(stn_dst, {})
            p_ontime = del_info.get("p_on_time", 0.65)
            p_slight = del_info.get("p_slight_delay", 0.22)
            p_severe = del_info.get("p_severe_delay", 0.10)
            p_cancel = del_info.get("p_cancelled", 0.03)
            
            candidates.append({
                "mode": "Rail",
                "airline_or_train": ttype,
                "service_identifier": tr_row["train_number"],
                "cabin_class_or_tier": tier_label,
                "departure_window": tr_row["departure_window"],
                "raw_cost": round(float(cost), 2),
                "raw_duration": float(tr_row["duration_hours"]),
                "raw_distance": float(dist_km),
                "transfer_count": 0, # direct corridor train
                "p_on_time": round(float(p_ontime), 4),
                "p_slight_delay": round(float(p_slight), 4),
                "p_severe_delay": round(float(p_severe), 4),
                "p_cancelled": round(float(p_cancel), 4),
                "is_empirical_delay": True,
                "source_dataset": "canonical_train_routes.parquet",
                "source_record_id": f"train_{tr_row['train_number']}_{tr_row['station_code_src']}_{stn_dst}"
            })
            
    # Guarantee between 2 and 5 candidates
    if len(candidates) < 2 and len(fl_pool) > 1:
        # Pad with another flight from pool
        extra_fl = fl_pool.sample(min(2, len(fl_pool)), random_state=rng.integers(0, 10000))
        for fidx, fl_row in extra_fl.iterrows():
            if len(candidates) >= 2:
                break
            candidates.append({
                "mode": "Flight",
                "airline_or_train": fl_row["airline"],
                "service_identifier": fl_row["flight_number"],
                "cabin_class_or_tier": fl_row["cabin_class"],
                "departure_window": fl_row["departure_time_window"],
                "raw_cost": float(fl_row["price_inr"]),
                "raw_duration": float(fl_row["duration_hours"]),
                "raw_distance": float(fl_row["direct_flight_distance_km"]),
                "transfer_count": int(fl_row["stops"]),
                "p_on_time": 0.88,
                "p_slight_delay": 0.08,
                "p_severe_delay": 0.03,
                "p_cancelled": 0.01,
                "is_empirical_delay": False,
                "source_dataset": "canonical_flights.parquet",
                "source_record_id": f"flight_{fl_row['flight_number']}_{fidx}"
            })
            
    # Limit max candidates to 5
    if len(candidates) > 5:
        candidates = candidates[:5]
        
    return candidates

# ==============================================================================
# 4. DERIVE ITINERARY ATTRIBUTES & UTILITY
# ==============================================================================
from src.feature_engineering import compute_candidate_scores

def derive_itinerary_features(candidates, session, traveller, config):
    """
    Computes choice-set relative quality scores by delegating to authoritative
    feature_engineering module: cost_score, time_score, transfer_score,
    reliability_score, comfort_score, carbon_estimate, carbon_score, and departure_fit.
    """
    return compute_candidate_scores(candidates, session, traveller, config)

        
    return candidates

def calculate_utility(candidates, traveller, config):
    """
    Computes deterministic utility V_nj for traveller n and each alternative j.
    Weights are derived strictly from the traveller's persistent Travel DNA.
    """
    # Raw Travel DNA dimensions
    w_c = traveller["cost_sensitivity"]
    w_t = traveller["time_sensitivity"]
    w_r = traveller["reliability_sensitivity"]
    w_comf = traveller["comfort_preference"]
    w_trans = 1.0 - traveller["transfer_tolerance"] # Transfer avoidance strength
    w_dep = 1.0 - 0.50 * traveller["departure_time_flexibility"] # Departure fit sensitivity
    w_sust = traveller["sustainability_preference"]
    
    total_w = w_c + w_t + w_r + w_comf + w_trans + w_dep + w_sust
    if total_w <= 0:
        total_w = 1.0
        
    # Normalized weights
    wc = w_c / total_w
    wt = w_t / total_w
    wr = w_r / total_w
    wcomf = w_comf / total_w
    wtrans = w_trans / total_w
    wdep = w_dep / total_w
    wsust = w_sust / total_w
    
    asc_mode = config["utility_model"]["asc_mode"]
    
    for c in candidates:
        asc = asc_mode.get(c["mode"].lower(), 0.0)
        v = (
            wc * c["cost_score"] +
            wt * c["time_score"] +
            wr * c["reliability_score"] +
            wcomf * c["comfort_score"] +
            wtrans * c["transfer_score"] +
            wdep * c["departure_fit"] +
            wsust * c["carbon_score"] +
            asc
        )
        c["utility"] = round(float(v), 5)
        
    return candidates

def calculate_mnl_probabilities(candidates, temperature=1.0):
    """
    Computes Multinomial Logit probabilities using numerically stable softmax:
    P_nj = exp((V_nj - max_V) / T) / sum_k exp((V_nk - max_V) / T)
    """
    v_vals = np.array([c["utility"] for c in candidates], dtype=np.float64)
    # Scale by scaling factor / temperature
    v_scaled = v_vals * 4.0 # Scale to realistic choice sharpness
    v_max = np.max(v_scaled)
    exp_v = np.exp(v_scaled - v_max)
    denom = np.sum(exp_v)
    probs = exp_v / denom
    
    # Clip and renormalize to avoid float underflow
    probs = np.clip(probs, 1e-6, 1.0)
    probs = probs / np.sum(probs)
    
    for idx, c in enumerate(candidates):
        c["choice_probability"] = float(probs[idx])
        
    return candidates

def sample_choices(candidates, rng):
    """
    Probabilistically samples exactly one chosen alternative per session using MNL probabilities.
    Assigns ranks based on descending utility / probability.
    """
    probs = [c["choice_probability"] for c in candidates]
    probs = np.array(probs, dtype=np.float64)
    probs = probs / np.sum(probs)
    
    chosen_idx = rng.choice(len(candidates), p=probs)
    
    # Sort candidates by utility descending to determine rank
    sorted_order = np.argsort([-c["utility"] for c in candidates])
    ranks = np.empty_like(sorted_order)
    ranks[sorted_order] = np.arange(1, len(candidates) + 1)
    
    for idx, c in enumerate(candidates):
        c["chosen"] = 1 if (idx == chosen_idx) else 0
        c["rank"] = int(ranks[idx])
        
    return candidates

# ==============================================================================
# 5. FULL PIPELINE EXECUTION
# ==============================================================================
def run_generation(scale="final", config=None, seed=None):
    """
    Executes dataset generation (pilot or final target) and produces long-format choice records.
    """
    if config is None:
        config = load_config()
    if seed is None:
        seed = config["reproducibility"]["seed"]
        
    n_trav = 5000 if scale == "final" else 600
    n_sess = 40000 if scale == "final" else 2400
    sess_per_trav = 8 if scale == "final" else 4
    
    print(f"--- Generating {n_trav} Travellers ({scale.upper()} Scale, Seed: {seed}) ---")
    df_travellers = generate_travellers(config, scale=scale, seed=seed)
    
    print(f"--- Generating {n_sess} Search Sessions ({sess_per_trav} per traveller) ---")
    df_sessions = generate_sessions(df_travellers, config, scale=scale, seed=seed + 101)
    
    print("--- Pre-indexing Real Flights and Train Options ---")
    indexed_data = preindex_real_data()
    
    print("--- Generating Alternatives, Utilities & MNL Choices ---")
    trav_dict = df_travellers.set_index("traveller_id").to_dict("index")
    
    candidate_records = []
    choice_records = []
    
    rng_choice = np.random.default_rng(seed + 202)
    sess_records = df_sessions.to_dict("records")
    
    for s_idx, sess in enumerate(sess_records):
        tid = sess["traveller_id"]
        trav = trav_dict[tid]
        sess_id = sess["session_id"]
        
        # Sessional seed for deterministic candidate retrieval
        s_seed = seed + 1000 + s_idx
        cand_list = retrieve_real_candidates(sess, indexed_data, config, seed=s_seed)
        cand_list = derive_itinerary_features(cand_list, sess, trav, config)
        cand_list = calculate_utility(cand_list, trav, config)
        cand_list = calculate_mnl_probabilities(cand_list)
        cand_list = sample_choices(cand_list, rng_choice)
        
        for alt_idx, c in enumerate(cand_list):
            alt_id = f"{sess_id}_A{alt_idx+1}"
            
            # Record for candidate table
            c_rec = {
                "session_id": sess_id,
                "alternative_id": alt_id,
                "mode": c["mode"],
                "carrier": c["airline_or_train"],
                "service_identifier": c["service_identifier"],
                "service_tier": c["cabin_class_or_tier"],
                "departure_window": c["departure_window"],
                "raw_cost": c["raw_cost"],
                "raw_duration": c["raw_duration"],
                "raw_distance": c["raw_distance"],
                "transfer_count": c["transfer_count"],
                "carbon_estimate_kg": c["carbon_estimate"],
                "p_on_time": c["p_on_time"],
                "p_severe_delay": c["p_severe_delay"],
                "p_cancelled": c["p_cancelled"],
                "source_dataset": c["source_dataset"],
                "source_record_id": c["source_record_id"]
            }
            candidate_records.append(c_rec)
            
            # Long format choice record with full Travel DNA context
            choice_rec = {
                "traveller_id": tid,
                "session_id": sess_id,
                "alternative_id": alt_id,
                "persona_type": trav["persona_type"],
                "cost_sensitivity": trav["cost_sensitivity"],
                "time_sensitivity": trav["time_sensitivity"],
                "reliability_sensitivity": trav["reliability_sensitivity"],
                "comfort_preference": trav["comfort_preference"],
                "transfer_tolerance": trav["transfer_tolerance"],
                "departure_time_flexibility": trav["departure_time_flexibility"],
                "sustainability_preference": trav["sustainability_preference"],
                "mode": c["mode"],
                "carrier": c["airline_or_train"],
                "service_identifier": c["service_identifier"],
                "service_tier": c["cabin_class_or_tier"],
                "origin_city": sess["origin_city"],
                "destination_city": sess["destination_city"],
                "departure_window": sess["departure_window"],
                "trip_purpose": sess["trip_purpose"],
                "party_size": sess["party_size"],
                "lead_days": sess["lead_days"],
                "chosen": c["chosen"],
                "rank": c["rank"],
                "choice_probability": c["choice_probability"],
                "utility": c["utility"],
                "raw_cost": c["raw_cost"],
                "raw_duration": c["raw_duration"],
                "raw_distance": c["raw_distance"],
                "cost_score": c["cost_score"],
                "time_score": c["time_score"],
                "reliability_score": c["reliability_score"],
                "comfort_score": c["comfort_score"],
                "transfer_count": c["transfer_count"],
                "transfer_score": c["transfer_score"],
                "carbon_estimate_kg": c["carbon_estimate"],
                "carbon_score": c["carbon_score"],
                "departure_fit": c["departure_fit"],
                "source_dataset": c["source_dataset"],
                "source_record_id": c["source_record_id"]
            }
            choice_records.append(choice_rec)
            
    df_candidates = pd.DataFrame(candidate_records)
    df_choices = pd.DataFrame(choice_records)
    
    # Save filenames
    if scale == "pilot":
        suffix = "_pilot"
    else:
        suffix = ""
        
    df_travellers.to_csv(os.path.join(SYNTHETIC_DIR, f"traveller_population{suffix}.csv"), index=False)
    df_travellers.to_parquet(os.path.join(SYNTHETIC_DIR, f"traveller_population{suffix}.parquet"), index=False)
    
    df_sessions.to_csv(os.path.join(SYNTHETIC_DIR, f"search_sessions{suffix}.csv"), index=False)
    df_sessions.to_parquet(os.path.join(SYNTHETIC_DIR, f"search_sessions{suffix}.parquet"), index=False)
    
    df_candidates.to_csv(os.path.join(SYNTHETIC_DIR, f"itinerary_candidates{suffix}.csv"), index=False)
    df_candidates.to_parquet(os.path.join(SYNTHETIC_DIR, f"itinerary_candidates{suffix}.parquet"), index=False)
    
    df_choices.to_csv(os.path.join(SYNTHETIC_DIR, f"choice_dataset{suffix}.csv"), index=False)
    df_choices.to_parquet(os.path.join(SYNTHETIC_DIR, f"choice_dataset{suffix}.parquet"), index=False)
    
    print(f"Datasets saved in {SYNTHETIC_DIR} (suffix: '{suffix}')")
    print(f"Travellers: {len(df_travellers)}, Sessions: {len(df_sessions)}, Candidates: {len(df_candidates)}, Choice rows: {len(df_choices)}")
    
    return df_travellers, df_sessions, df_candidates, df_choices

def run_pilot_generation(config=None, seed=None):
    return run_generation(scale="pilot", config=config, seed=seed)

# ==============================================================================
# 6. AUTOMATED VALIDATION SUITE (DELEGATED TO src.validation)
# ==============================================================================
from src.validation import (
    validate_structural,
    validate_statistical,
    validate_mnl,
    run_sensitivity_tests as run_sens_suite,
    generate_validation_plots,
)

def run_sensitivity_tests(config):
    """Delegates behavioural sensitivity tests to authoritative validation module."""
    return run_sens_suite(
        config,
        derive_itinerary_features,
        calculate_utility,
        calculate_mnl_probabilities,
    )

def run_reproducibility_test(config, scale="final", pregenerated=None):
    """
    Runs generation twice with SEED = 42 and confirms bitwise identical outputs.
    """
    seed = config["reproducibility"]["seed"]
    if pregenerated is not None:
        t1, s1, c1, ch1 = pregenerated
    else:
        t1, s1, c1, ch1 = run_generation(scale=scale, config=config, seed=seed)
    t2, s2, c2, ch2 = run_generation(scale=scale, config=config, seed=seed)
    
    h_t1 = hashlib.sha256(t1.to_csv(index=False).encode()).hexdigest()
    h_t2 = hashlib.sha256(t2.to_csv(index=False).encode()).hexdigest()
    
    h_ch1 = hashlib.sha256(ch1.to_csv(index=False).encode()).hexdigest()
    h_ch2 = hashlib.sha256(ch2.to_csv(index=False).encode()).hexdigest()
    
    is_identical = (h_t1 == h_t2) and (h_ch1 == h_ch2)
    return {
        "reproducible": is_identical,
        "travellers_hash": h_t1,
        "choice_dataset_hash": h_ch1,
    }

def compute_artifact_hashes(scale="final"):
    suffix = "_pilot" if scale == "pilot" else ""
    files = [
        f"traveller_population{suffix}.parquet",
        f"traveller_population{suffix}.csv",
        f"search_sessions{suffix}.parquet",
        f"search_sessions{suffix}.csv",
        f"itinerary_candidates{suffix}.parquet",
        f"itinerary_candidates{suffix}.csv",
        f"choice_dataset{suffix}.parquet",
        f"choice_dataset{suffix}.csv",
    ]
    hashes = {}
    for fname in files:
        fpath = os.path.join(SYNTHETIC_DIR, fname)
        if os.path.exists(fpath):
            with open(fpath, "rb") as f:
                hashes[fname] = hashlib.sha256(f.read()).hexdigest()
    return hashes


# ==============================================================================
# 7. MAIN RUNNER
# ==============================================================================
if __name__ == "__main__":
    config = load_config()
    print("=== STARTING YATRA AI PHASE 3 FINAL-SCALE GENERATION ===")
    print("Target: 5,000 Travellers x 8 Sessions = 40,000 Search Sessions")
    df_t, df_s, df_c, df_ch = run_generation(scale="final", config=config)
    
    print("\n=== RUNNING AUTOMATED VALIDATION SUITE (FINAL SCALE) ===")
    v_struct = validate_structural(df_t, df_s, df_c, df_ch, config, scale="final")
    print("1. Structural Validation:", "PASSED" if v_struct["passed"] else f"FAILED ({v_struct['errors']})")
    
    v_stat = validate_statistical(df_t, config)
    print("2. Statistical Validation:", "PASSED" if v_stat["passed"] else "FAILED")
    
    v_mnl = validate_mnl(df_ch)
    print("3. MNL Mathematical Axioms:", "PASSED" if v_mnl["passed"] else "FAILED", f"(Max diff: {v_mnl['max_prob_sum_discrepancy']:.2e})")
    
    v_sens = run_sensitivity_tests(config)
    print("4. Behavioural Sensitivity Tests:", "PASSED" if v_sens["all_passed"] else "FAILED")
    for tname, tres in v_sens["tests"].items():
        print(f"   - {tname}: {'PASSED' if tres['passed'] else 'FAILED'} (delta: {tres['delta']:+.4f})")
        
    print("\n--- Generating Statistical Validation Plots ---")
    generate_validation_plots(df_t, df_ch)
    
    print("\n=== RUNNING REPRODUCIBILITY BITWISE CHECK ===")
    v_repro = run_reproducibility_test(config, scale="final", pregenerated=(df_t, df_s, df_c, df_ch))
    print("5. Reproducibility Test:", "PASSED" if v_repro["reproducible"] else "FAILED")
    print("   Travellers Hash:", v_repro["travellers_hash"])
    print("   Choice Dataset Hash:", v_repro["choice_dataset_hash"])
    
    print("\n=== FINAL ARTIFACT SHA-256 HASHES ===")
    hashes = compute_artifact_hashes(scale="final")
    for fname, fhash in hashes.items():
        print(f"   {fname}: {fhash}")
    
    print("\n=== PHASE 3 FINAL-SCALE COMPLETE ===")
