import os
import json
import math
import pandas as pd
import numpy as np

import sys

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)

def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance between two points in km."""
    if any(pd.isna([lat1, lon1, lat2, lon2])):
        return 0.0
    R = 6371.0 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2.0)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def time_str_to_minutes(t_str):
    if pd.isna(t_str) or not isinstance(t_str, str):
        return None
    parts = t_str.strip().split(':')
    if len(parts) >= 2:
        try:
            return int(parts[0]) * 60 + int(parts[1])
        except ValueError:
            return None
    return None

# =====================================================================
# 1. CLEAN STATIONS
# =====================================================================
def process_stations():
    print("Processing stations...")
    path = os.path.join(RAW_DIR, "railways", "stations.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    rows = []
    for s in data:
        coords = s.get("coordinates", {})
        lon = coords.get("longitude") if isinstance(coords, dict) else None
        lat = coords.get("latitude") if isinstance(coords, dict) else None
        
        # Check valid India bounding box (approx 6-38 N, 68-98 E)
        is_valid_coord = (
            lat is not None and lon is not None and
            not (lat == 0.0 and lon == 0.0) and
            (6.0 <= lat <= 38.0) and (68.0 <= lon <= 98.0)
        )
        
        # Check dummy/test codes
        code = str(s.get("code", "")).strip().upper()
        is_dummy = code.startswith("XX-") or code.startswith("YY-") or not code
        
        zone = str(s.get("zone", "")).strip()
        if not zone or zone == "?":
            zone = "UNKNOWN"
            
        state = str(s.get("state", "")).strip()
        if not state:
            state = "UNKNOWN"
            
        rows.append({
            "station_code": code,
            "station_name": str(s.get("name", "")).strip(),
            "state": state,
            "railway_zone": zone,
            "address": str(s.get("address", "")).strip(),
            "latitude": round(lat, 6) if lat is not None else np.nan,
            "longitude": round(lon, 6) if lon is not None else np.nan,
            "is_valid_coordinate": is_valid_coord,
            "is_test_dummy_record": is_dummy
        })
        
    df = pd.DataFrame(rows)
    # Deduplicate on station_code if any
    df = df.drop_duplicates(subset=["station_code"]).reset_index(drop=True)
    
    # Identify Metro Hub association
    metro_keywords = {
        "Delhi": ["DELHI", "NDLS", "ANVT", "DLI", "NZM", "SARAI ROHILLA"],
        "Mumbai": ["MUMBAI", "CSTM", "BCT", "BDTS", "LTT", "DADAR", "KURLA", "BORIVALI"],
        "Bangalore": ["BANGALORE", "BENGALURU", "SBC", "YPR", "SMVB", "YESVANTPUR"],
        "Kolkata": ["KOLKATA", "CALCUTTA", "HWH", "HOWRAH", "SDAH", "SEALDAH", "KOAA", "SHM"],
        "Hyderabad": ["HYDERABAD", "SECUNDERABAD", "SC", "HYB", "KACHEGUDA", "KCG"],
        "Chennai": ["CHENNAI", "MADRAS", "MAS", "MS", "TBM", "PERAMBUR"]
    }
    
    def assign_metro_cluster(row):
        txt = f"{row['station_code']} {row['station_name']} {row['address']}".upper()
        for city, kw_list in metro_keywords.items():
            for kw in kw_list:
                if kw in txt:
                    return city
        return "OTHER"
        
    df["metro_cluster"] = df.apply(assign_metro_cluster, axis=1)
    
    csv_out = os.path.join(PROCESSED_DIR, "canonical_stations.csv")
    parquet_out = os.path.join(PROCESSED_DIR, "canonical_stations.parquet")
    df.to_csv(csv_out, index=False)
    df.to_parquet(parquet_out, index=False)
    print(f"Stations saved: {len(df)} records (Valid coords: {df['is_valid_coordinate'].sum()}, Metro stations: {(df['metro_cluster'] != 'OTHER').sum()})")
    return df

# =====================================================================
# 2. CLEAN TRAIN ROUTES & SCHEDULES
# =====================================================================
def process_train_routes(df_stations):
    print("Processing train routes & schedules...")
    coord_lookup = df_stations.set_index("station_code")[["latitude", "longitude", "state", "railway_zone"]].to_dict("index")
    
    path = os.path.join(RAW_DIR, "railways", "trains.json")
    with open(path, "r", encoding="utf-8") as f:
        trains_data = json.load(f)
        
    route_rows = []
    service_rows = []
    
    for t in trains_data:
        tnum = str(t.get("trainNumber", "")).strip().zfill(5)
        tname = str(t.get("trainName", "")).strip()
        ttype = str(t.get("type", "Exp")).strip()
        src_code = str(t.get("source", {}).get("code", "")).strip().upper()
        dst_code = str(t.get("destination", {}).get("code", "")).strip().upper()
        overall_dist = t.get("overallDistanceKm", 0.0)
        running_days = t.get("runningDays", {})
        running_days_str = ",".join([k for k, v in running_days.items() if v])
        
        service_rows.append({
            "train_number": tnum,
            "train_name": tname,
            "train_type": ttype,
            "source_code": src_code,
            "dest_code": dst_code,
            "running_days": running_days_str,
            "total_route_distance_km": overall_dist,
            "total_halts": len(t.get("completeOrderedRoute", []))
        })
        
        route = t.get("completeOrderedRoute", [])
        prev_lat, prev_lon = None, None
        cum_dist = 0.0
        
        for idx, stop in enumerate(route):
            stn_code = str(stop.get("stationCode", "")).strip().upper()
            stn_name = str(stop.get("stationName", "")).strip()
            arr_time = stop.get("arrivalTime")
            dep_time = stop.get("departureTime")
            seq = stop.get("sequence", idx + 1)
            j_day = stop.get("journeyDay", 1)
            
            # lookup coords
            stn_info = coord_lookup.get(stn_code, {})
            lat = stn_info.get("latitude", np.nan)
            lon = stn_info.get("longitude", np.nan)
            
            arr_min = time_str_to_minutes(arr_time)
            dep_min = time_str_to_minutes(dep_time)
            
            # calculate halt duration in minutes
            halt_duration = None
            if arr_min is not None and dep_min is not None:
                if dep_min >= arr_min:
                    halt_duration = dep_min - arr_min
                else:
                    # crossing midnight
                    halt_duration = (dep_min + 1440) - arr_min
            
            # step distance
            if prev_lat is not None and not pd.isna(lat) and not pd.isna(lon):
                step_dist = haversine(prev_lat, prev_lon, lat, lon)
            else:
                step_dist = 0.0
                
            cum_dist += step_dist
            prev_lat, prev_lon = lat, lon
            
            route_rows.append({
                "train_number": tnum,
                "sequence": seq,
                "station_code": stn_code,
                "station_name": stn_name,
                "arrival_time": arr_time,
                "departure_time": dep_time,
                "arrival_minutes_from_midnight": arr_min,
                "departure_minutes_from_midnight": dep_min,
                "halt_duration_minutes": halt_duration,
                "journey_day": j_day,
                "segment_haversine_km": round(step_dist, 2),
                "cumulative_haversine_km": round(cum_dist, 2),
                "is_origin": (idx == 0),
                "is_destination": (idx == len(route) - 1)
            })
            
    df_services = pd.DataFrame(service_rows)
    df_routes = pd.DataFrame(route_rows)
    
    # Save train services master
    df_services.to_csv(os.path.join(PROCESSED_DIR, "canonical_train_services.csv"), index=False)
    df_services.to_parquet(os.path.join(PROCESSED_DIR, "canonical_train_services.parquet"), index=False)
    
    # Save route stops
    df_routes.to_csv(os.path.join(PROCESSED_DIR, "canonical_train_routes.csv"), index=False)
    df_routes.to_parquet(os.path.join(PROCESSED_DIR, "canonical_train_routes.parquet"), index=False)
    
    print(f"Train services saved: {len(df_services)}, Route halts saved: {len(df_routes)}")
    return df_services, df_routes

# =====================================================================
# 3. CLEAN TRAIN DELAYS & PUNCTUALITY
# =====================================================================
def process_train_delays():
    print("Processing train delay logs...")
    # Station alias mapping for renamed/new stations
    alias_map = {
        "PRYJ": "ALD",  # Prayagraj Jn (formerly Allahabad)
        "DDU": "MGS",   # Pt DD Upadhyaya (formerly Mughalsarai)
        "SMVB": "SBC",  # Sir M Visvesvaraya Terminal (Bangalore hub)
        "PCOI": "COI",  # Prayagraj Chheoki
        "NBJU": "BJU",  # New Barauni / Barauni Jn
        "NKMG": "KXJ"   # New Karimganj / Karimganj
    }
    
    routes_dir = os.path.join(RAW_DIR, "delays", "train_routes")
    dfs = []
    for f in os.listdir(routes_dir):
        if f.endswith(".csv"):
            tnum = f.replace(".csv", "").zfill(5)
            df = pd.read_csv(os.path.join(routes_dir, f))
            df["train_number"] = tnum
            dfs.append(df)
            
    df_delays = pd.concat(dfs, ignore_index=True)
    
    # Standardize column names
    df_delays.rename(columns={
        "Station": "station_code_raw",
        "Station_Name": "station_name",
        "Average_Delay(min)": "mean_delay_minutes",
        "Right Time (0-15 min's)": "pct_right_time_0_15m",
        "Slight Delay (15-60 min's)": "pct_slight_delay_15_60m",
        "Significant Delay (>1 Hour)": "pct_severe_delay_over_60m",
        "Cancelled/Unknown": "pct_cancelled_unknown"
    }, inplace=True)
    
    df_delays["station_code_raw"] = df_delays["station_code_raw"].str.strip().str.upper()
    df_delays["canonical_station_code"] = df_delays["station_code_raw"].apply(lambda s: alias_map.get(s, s))
    
    # Derived probability features (0.0 to 1.0)
    df_delays["p_on_time"] = round(df_delays["pct_right_time_0_15m"] / 100.0, 4)
    df_delays["p_slight_delay"] = round(df_delays["pct_slight_delay_15_60m"] / 100.0, 4)
    df_delays["p_severe_delay"] = round(df_delays["pct_severe_delay_over_60m"] / 100.0, 4)
    df_delays["p_cancelled"] = round(df_delays["pct_cancelled_unknown"] / 100.0, 4)
    
    # Operational Delay Risk Categories
    def assign_delay_risk_class(row):
        # Multiclass target formulation
        if row["p_cancelled"] >= 0.20:
            return "CANCEL_DISRUPTED"
        elif row["mean_delay_minutes"] <= 15 and row["p_on_time"] >= 0.70:
            return "ON_TIME_RELIABLE"
        elif row["mean_delay_minutes"] <= 45:
            return "MODERATE_DELAY"
        else:
            return "SEVERE_DELAY"
            
    df_delays["delay_risk_category"] = df_delays.apply(assign_delay_risk_class, axis=1)
    
    # Binary transfer risk target (High Risk: delay > 45m or severe delay prob > 25%)
    df_delays["is_high_transfer_risk"] = (
        (df_delays["mean_delay_minutes"] > 45) | (df_delays["p_severe_delay"] > 0.25) | (df_delays["p_cancelled"] > 0.10)
    ).astype(int)
    
    csv_out = os.path.join(PROCESSED_DIR, "canonical_train_delays.csv")
    parquet_out = os.path.join(PROCESSED_DIR, "canonical_train_delays.parquet")
    df_delays.to_csv(csv_out, index=False)
    df_delays.to_parquet(parquet_out, index=False)
    print(f"Train delays saved: {len(df_delays)} station delay observations across {df_delays['train_number'].nunique()} trains")
    return df_delays

# =====================================================================
# 4. CLEAN FLIGHTS
# =====================================================================
def process_flights():
    print("Processing flights dataset...")
    path = os.path.join(RAW_DIR, "flights", "Clean_flight_data_Vivek.csv")
    df = pd.read_csv(path)
    
    # Deduplicate identical rows
    init_len = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    print(f"Deduplicated flights: {init_len} -> {len(df)} (removed {init_len - len(df)} duplicates)")
    
    df.rename(columns={
        "flight": "flight_number",
        "departure_time": "departure_time_window",
        "arrival_time": "arrival_time_window",
        "class": "cabin_class",
        "duration": "duration_hours",
        "price": "price_inr"
    }, inplace=True)
    
    # Add corridor pair
    df["corridor"] = df["source_city"] + "-" + df["destination_city"]
    
    # Derive price per flight hour
    df["price_per_duration_hour"] = round(df["price_inr"] / df["duration_hours"], 2)
    
    # Speed proxy (km/h) assuming approximate great-circle distances between metro airports
    metro_coords = {
        "Delhi": (28.5562, 77.1000),
        "Mumbai": (19.0896, 72.8656),
        "Bangalore": (13.1986, 77.7066),
        "Kolkata": (22.6547, 88.4467),
        "Hyderabad": (17.2403, 78.4294),
        "Chennai": (12.9941, 80.1709)
    }
    
    def get_corridor_dist(row):
        c1 = metro_coords.get(row["source_city"])
        c2 = metro_coords.get(row["destination_city"])
        if c1 and c2:
            return round(haversine(c1[0], c1[1], c2[0], c2[1]), 1)
        return np.nan
        
    df["direct_flight_distance_km"] = df.apply(get_corridor_dist, axis=1)
    
    csv_out = os.path.join(PROCESSED_DIR, "canonical_flights.csv")
    parquet_out = os.path.join(PROCESSED_DIR, "canonical_flights.parquet")
    df.to_csv(csv_out, index=False)
    df.to_parquet(parquet_out, index=False)
    print(f"Flights saved: {len(df)} records across {df['corridor'].nunique()} corridors")
    return df

# =====================================================================
# 5. CLEAN RAINFALL & ENVIRONMENTAL DATA
# =====================================================================
def process_rainfall():
    print("Processing rainfall dataset...")
    path = os.path.join(RAW_DIR, "environmental", "rainfall_india_1901-2015.csv")
    df = pd.read_csv(path)
    
    months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    
    # Impute missing values with subdivisional median across years
    for m in months + ["ANNUAL"]:
        df[m] = df.groupby("SUBDIVISION")[m].transform(lambda grp: grp.fillna(grp.median()))
        
    # Recalculate ANNUAL if discrepancy exists
    df["ANNUAL_COMPUTED"] = df[months].sum(axis=1)
    df["monsoon_jjas_rainfall_mm"] = df[["JUN", "JUL", "AUG", "SEP"]].sum(axis=1)
    df["monsoon_intensity_ratio"] = round(df["monsoon_jjas_rainfall_mm"] / df["ANNUAL_COMPUTED"], 4)
    
    # Standardize column naming
    df.rename(columns={
        "SUBDIVISION": "subdivision",
        "YEAR": "year",
        "ANNUAL": "annual_rainfall_mm"
    }, inplace=True)
    
    # Calculate 30-year climatological normal baseline (1986-2015) per subdivision
    df_recent = df[df["year"] >= 1986]
    normals = df_recent.groupby("subdivision").agg({
        "annual_rainfall_mm": "mean",
        "monsoon_jjas_rainfall_mm": "mean",
        "monsoon_intensity_ratio": "mean"
    }).reset_index()
    normals.columns = [
        "subdivision",
        "baseline_normal_annual_rainfall_mm",
        "baseline_normal_monsoon_rainfall_mm",
        "baseline_monsoon_intensity_ratio"
    ]
    
    df = df.merge(normals, on="subdivision", how="left")
    
    csv_out = os.path.join(PROCESSED_DIR, "canonical_subdivision_rainfall.csv")
    parquet_out = os.path.join(PROCESSED_DIR, "canonical_subdivision_rainfall.parquet")
    df.to_csv(csv_out, index=False)
    df.to_parquet(parquet_out, index=False)
    print(f"Rainfall saved: {len(df)} records (1901-2015, {df['subdivision'].nunique()} subdivisions)")
    return df

# =====================================================================
# 6. BUILD CORRIDOR MULTIMODAL BENCHMARK (METRO PAIRS)
# =====================================================================
def build_corridor_multimodal(df_flights, df_train_services, df_routes, df_stations):
    print("Building corridor multimodal comparison...")
    # Map major railway stations to city names
    city_primary_stations = {
        "Delhi": ["NDLS", "DLI", "NZM", "ANVT"],
        "Mumbai": ["MMCT", "BCT", "CSMT", "BDTS", "LTT"],
        "Bangalore": ["SBC", "YPR", "SMVB"],
        "Kolkata": ["HWH", "SDAH", "KOAA"],
        "Hyderabad": ["SC", "HYB", "KCG"],
        "Chennai": ["MAS", "MS"]
    }
    
    metro_cities = list(city_primary_stations.keys())
    corridor_rows = []
    
    for c_src in metro_cities:
        for c_dst in metro_cities:
            if c_src == c_dst:
                continue
            corr_id = f"{c_src}-{c_dst}"
            
            # Flight summary
            fl_subset = df_flights[(df_flights["source_city"] == c_src) & (df_flights["destination_city"] == c_dst)]
            fl_econ = fl_subset[fl_subset["cabin_class"] == "Economy"]
            
            fl_avail = len(fl_subset) > 0
            fl_count = len(fl_subset)
            fl_min_dur = fl_subset["duration_hours"].min() if fl_avail else np.nan
            fl_med_dur = fl_subset["duration_hours"].median() if fl_avail else np.nan
            fl_econ_min_fare = fl_econ["price_inr"].min() if len(fl_econ) > 0 else np.nan
            fl_econ_med_fare = fl_econ["price_inr"].median() if len(fl_econ) > 0 else np.nan
            fl_nonstop_count = len(fl_subset[fl_subset["stops"] == 0]) if fl_avail else 0
            
            # Train summary: find trains starting at any src station and ending at any dst station
            src_stns = city_primary_stations[c_src]
            dst_stns = city_primary_stations[c_dst]
            
            train_subset = df_train_services[
                (df_train_services["source_code"].isin(src_stns)) &
                (df_train_services["dest_code"].isin(dst_stns))
            ]
            
            train_avail = len(train_subset) > 0
            train_count = len(train_subset)
            train_min_dist = train_subset["total_route_distance_km"].min() if train_avail else np.nan
            train_med_dist = train_subset["total_route_distance_km"].median() if train_avail else np.nan
            train_types = ",".join(train_subset["train_type"].unique()) if train_avail else ""
            
            corridor_rows.append({
                "corridor": corr_id,
                "origin_city": c_src,
                "destination_city": c_dst,
                "has_direct_flight": fl_avail,
                "flight_options_count": fl_count,
                "flight_nonstop_count": fl_nonstop_count,
                "flight_min_duration_hours": fl_min_dur,
                "flight_median_duration_hours": fl_med_dur,
                "flight_econ_min_fare_inr": fl_econ_min_fare,
                "flight_econ_median_fare_inr": fl_econ_med_fare,
                "has_direct_train": train_avail,
                "direct_train_services_count": train_count,
                "train_types_available": train_types,
                "train_min_distance_km": train_min_dist,
                "train_median_distance_km": train_med_dist
            })
            
    df_corridor = pd.DataFrame(corridor_rows)
    csv_out = os.path.join(PROCESSED_DIR, "canonical_corridor_multimodal.csv")
    parquet_out = os.path.join(PROCESSED_DIR, "canonical_corridor_multimodal.parquet")
    df_corridor.to_csv(csv_out, index=False)
    df_corridor.to_parquet(parquet_out, index=False)
    print(f"Corridor multimodal dataset saved: {len(df_corridor)} city pairs")
    return df_corridor

if __name__ == "__main__":
    print("=== STARTING YATRA AI CANONICAL NORMALIZATION PIPELINE ===")
    df_stns = process_stations()
    df_srv, df_routes = process_train_routes(df_stns)
    df_delays = process_train_delays()
    df_flights = process_flights()
    df_rainfall = process_rainfall()
    df_corridor = build_corridor_multimodal(df_flights, df_srv, df_routes, df_stns)
    print("=== PIPELINE EXECUTION COMPLETED SUCCESSFULLY ===")
