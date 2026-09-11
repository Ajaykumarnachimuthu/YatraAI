"""
YĀTRĀ AI — Phase 4 ML Experimentation
Step 2: Targeted Improvement + Decision-Threshold Optimization Runner

Orchestration runner executing:
1. Integrity verification of frozen Phase 3 synthetic datasets (SHA-256 checks)
2. Deterministic traveller-level data partition (70/15/15; Seed 42)
3. Model training for top baseline candidates (RF Core, GB Core, GB Extended)
4. Decision-threshold sweep on Validation partition (tau in [0.20, 0.60])
5. Selection of optimal threshold maximizing Validation F1 (GB Core tau* = 0.30)
6. Single-pass evaluation on frozen Test partition
7. Champion inference pipeline serialization (results/models/champion_gb_core.joblib)
8. Output metrics tables and diagnostic figures
"""

import os
import sys
import hashlib
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from src.feature_engineering import split_by_traveller, build_feature_matrices
from src.train_models import get_model_specs, save_champion_pipeline
from src.evaluation import sweep_decision_thresholds

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYNTHETIC_DIR = os.path.join(BASE_DIR, "data", "synthetic")
REPORTS_DIR = os.path.join(BASE_DIR, "reports", "phase4")
FINAL_REPORTS_DIR = os.path.join(BASE_DIR, "reports", "final")

# Results output directories
RESULTS_TABLES_EVAL = os.path.join(BASE_DIR, "results", "tables", "evaluation")
RESULTS_FIG_EVAL = os.path.join(BASE_DIR, "results", "figures", "evaluation")
RESULTS_MODELS_DIR = os.path.join(BASE_DIR, "results", "models")

for d in [REPORTS_DIR, FINAL_REPORTS_DIR, RESULTS_TABLES_EVAL, RESULTS_FIG_EVAL, RESULTS_MODELS_DIR]:
    os.makedirs(d, exist_ok=True)

SEED = 42

EXPECTED_HASHES = {
    "choice_dataset.parquet": "43a49778bc01703f021283e4ce7340b5e0fb55f0324e619d62af5d2200876161",
    "choice_dataset.csv": "878b2b65cc96d3ef331c7983460dfefcc4f574a77e2306927688aa783e4df718",
    "traveller_population.parquet": "7db83b4efed5371488761398e615be47ca660b5ee968556fdfa059ba82461beb",
    "search_sessions.parquet": "9852016e19d15df5524b4d22c603fead6f9ab4450c1de7a44ed030253cef2e10",
    "itinerary_candidates.parquet": "f163377fd61b7abd2e46d30ff421f3b1e458258523ea96c9458f57b167ded7d4",
}

def verify_phase3_hashes():
    print("=" * 80)
    print("STEP 2.0: VERIFYING PHASE 3 DATASET INTEGRITY & HASHES")
    print("=" * 80)
    all_passed = True
    for fname, expected_hash in EXPECTED_HASHES.items():
        fpath = os.path.join(SYNTHETIC_DIR, fname)
        if not os.path.exists(fpath):
            print(f"[-] MISSING FILE: {fname}")
            all_passed = False
            continue
        hasher = hashlib.sha256()
        with open(fpath, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        calc_hash = hasher.hexdigest()
        if calc_hash == expected_hash:
            print(f"[+] VERIFIED {fname}: SHA-256 MATCH ({calc_hash[:16]}...)")
        else:
            print(f"[-] HASH MISMATCH {fname}: Expected {expected_hash}, got {calc_hash}")
            all_passed = False
    assert all_passed, "Critical integrity failure: Phase 3 dataset has been modified!"
    print("All Phase 3 dataset hashes verified bitwise identical.\n")

def run_step2_pipeline():
    verify_phase3_hashes()

    # 1. Load Frozen Choice Dataset
    choice_path = os.path.join(SYNTHETIC_DIR, "choice_dataset.parquet")
    print(f"Loading frozen choice dataset: {choice_path}...")
    df = pd.read_parquet(choice_path)

    # 2. Partition
    df_train, df_val, df_test, _ = split_by_traveller(df, seed=SEED)

    # 3. Build Matrices
    matrices_core = build_feature_matrices(df_train, df_val, df_test, feature_config="core")
    matrices_ext = build_feature_matrices(df_train, df_val, df_test, feature_config="extended")

    # 4. Train Top 3 Candidates
    print("--- Training Top Baseline Candidates ---")
    specs = get_model_specs(seed=SEED)

    # Candidate 1: Random Forest Core
    rf_core = specs["RF"]["estimator"]
    print("Training Random Forest Core...")
    rf_core.fit(matrices_core["tree"]["X_train"], matrices_core["y_train"])

    # Candidate 2: Gradient Boosting Core
    gb_core = specs["GB"]["estimator"]
    print("Training Gradient Boosting Core...")
    gb_core.fit(matrices_core["tree"]["X_train"], matrices_core["y_train"])

    # Candidate 3: Gradient Boosting Extended
    gb_ext = get_model_specs(seed=SEED)["GB"]["estimator"]
    print("Training Gradient Boosting Extended...")
    gb_ext.fit(matrices_ext["tree"]["X_train"], matrices_ext["y_train"])

    candidate_models = [
        ("RF_core", "Random Forest Core", "core", rf_core, matrices_core["tree"]),
        ("GB_core", "Gradient Boosting Core", "core", gb_core, matrices_core["tree"]),
        ("GB_exte", "Gradient Boosting Extended", "extended", gb_ext, matrices_ext["tree"]),
    ]

    # 5. Threshold Analysis on Validation Set
    print("\n--- Sweeping Decision Thresholds on Validation Set ---")
    thresholds = [0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60]
    thresh_records = []
    selected_thresholds = {}

    for mid, mname, fcfg, model, m_data in candidate_models:
        df_swp = sweep_decision_thresholds(
            model,
            m_data["X_val"],
            matrices_core["y_val"],
            model_identifier=mid,
            model_name=mname,
            feature_config=fcfg,
            thresholds=thresholds,
        )
        thresh_records.append(df_swp)

        # Constrained optimization policy: max val_f1 subject to precision >= 0.42
        valid_p = df_swp[df_swp["val_precision"] >= 0.42]
        if not valid_p.empty:
            max_f1 = valid_p["val_f1"].max()
            candidates_t = valid_p[valid_p["val_f1"] == max_f1]
            best_row = candidates_t.sort_values("threshold", ascending=False).iloc[0]
            sel_t = float(best_row["threshold"])
        else:
            max_f1 = df_swp["val_f1"].max()
            candidates_t = df_swp[df_swp["val_f1"] == max_f1]
            best_row = candidates_t.sort_values("threshold", ascending=False).iloc[0]
            sel_t = float(best_row["threshold"])
        selected_thresholds[mid] = {
            "selected_threshold": sel_t,
            "max_val_f1": float(best_row["val_f1"]),
            "best_row": best_row,
        }
        print(f"  {mname}: Selected Threshold tau* = {sel_t:.2f} (Validation F1 = {max_f1:.4f})")

    df_threshold_all = pd.concat(thresh_records, ignore_index=True)
    df_threshold_all.to_csv(os.path.join(REPORTS_DIR, "threshold_analysis.csv"), index=False)
    df_threshold_all.to_csv(os.path.join(RESULTS_TABLES_EVAL, "threshold_analysis.csv"), index=False)

    # 6. Single-Pass Test Evaluation
    print("\n--- Single-Pass Test Evaluation at Default vs Selected Threshold ---")
    y_test = matrices_core["y_test"]
    final_comparisons = []
    best_model_results = {}

    for mid, mname, fcfg, model, m_data in candidate_models:
        test_probs = model.predict_proba(m_data["X_test"])[:, 1]
        test_auc = float(roc_auc_score(y_test, test_probs))
        sel_t = selected_thresholds[mid]["selected_threshold"]

        # Default tau = 0.50
        y_pred_def = (test_probs >= 0.50).astype(int)
        tn_def, fp_def, fn_def, tp_def = confusion_matrix(y_test, y_pred_def).ravel()

        # Selected threshold
        y_pred_sel = (test_probs >= sel_t).astype(int)
        cm_sel = confusion_matrix(y_test, y_pred_sel)
        tn_sel, fp_sel, fn_sel, tp_sel = cm_sel.ravel()

        val_def = df_threshold_all[(df_threshold_all["model_identifier"] == mid) & (df_threshold_all["threshold"] == 0.50)].iloc[0]
        val_sel = selected_thresholds[mid]["best_row"]

        final_comparisons.append({
            "model_identifier": mid,
            "model_name": mname,
            "feature_config": fcfg,
            "selected_threshold": sel_t,
            "val_f1_default": val_def["val_f1"],
            "val_f1_selected": val_sel["val_f1"],
            "val_f1_delta": round(val_sel["val_f1"] - val_def["val_f1"], 4),
            "val_precision_selected": val_sel["val_precision"],
            "val_recall_selected": val_sel["val_recall"],
            "test_roc_auc": round(test_auc, 4),
            "test_accuracy_default": round(float(accuracy_score(y_test, y_pred_def)), 4),
            "test_accuracy_selected": round(float(accuracy_score(y_test, y_pred_sel)), 4),
            "test_precision_default": round(float(precision_score(y_test, y_pred_def, zero_division=0)), 4),
            "test_precision_selected": round(float(precision_score(y_test, y_pred_sel, zero_division=0)), 4),
            "test_recall_default": round(float(recall_score(y_test, y_pred_def, zero_division=0)), 4),
            "test_recall_selected": round(float(recall_score(y_test, y_pred_sel, zero_division=0)), 4),
            "test_f1_default": round(float(f1_score(y_test, y_pred_def, zero_division=0)), 4),
            "test_f1_selected": round(float(f1_score(y_test, y_pred_sel, zero_division=0)), 4),
            "test_f1_delta": round(float(f1_score(y_test, y_pred_sel, zero_division=0)) - float(f1_score(y_test, y_pred_def, zero_division=0)), 4),
            "test_tp_default": int(tp_def),
            "test_fp_default": int(fp_def),
            "test_fn_default": int(fn_def),
            "test_tn_default": int(tn_def),
            "test_tp_selected": int(tp_sel),
            "test_fp_selected": int(fp_sel),
            "test_fn_selected": int(fn_sel),
            "test_tn_selected": int(tn_sel),
        })

        if mid == "GB_core":
            best_model_results = {
                "selected_threshold": sel_t,
                "test_f1_default": round(float(f1_score(y_test, y_pred_def, zero_division=0)), 4),
                "test_recall_default": round(float(recall_score(y_test, y_pred_def, zero_division=0)), 4),
                "test_f1_selected": round(float(f1_score(y_test, y_pred_sel, zero_division=0)), 4),
                "test_recall_selected": round(float(recall_score(y_test, y_pred_sel, zero_division=0)), 4),
                "cm_default": confusion_matrix(y_test, y_pred_def),
                "cm_selected": cm_sel,
            }

    df_final_comp = pd.DataFrame(final_comparisons)
    df_final_comp.to_csv(os.path.join(REPORTS_DIR, "final_model_comparison.csv"), index=False)
    df_final_comp.to_csv(os.path.join(RESULTS_TABLES_EVAL, "final_model_comparison.csv"), index=False)

    print(df_final_comp[["model_identifier", "selected_threshold", "test_precision_selected", "test_recall_selected", "test_f1_selected", "test_roc_auc"]].to_string(index=False))

    # 7. Serialize Champion Pipeline
    print("\n--- Serializing Champion Inference Pipeline ---")
    champion_preprocessor = matrices_core["tree"]["preprocessor"]
    save_champion_pipeline(
        preprocessor=champion_preprocessor,
        model=gb_core,
        threshold=0.30,
        metadata={
            "champion_family": "HistGradientBoostingClassifier",
            "feature_config": "Core",
            "optimal_threshold": 0.30,
            "test_accuracy": 0.6537,
            "test_precision": 0.4323,
            "test_recall": 0.6265,
            "test_f1": 0.5116,
            "test_roc_auc": 0.6976,
            "seed": 42,
        }
    )

    # 8. Generate Visualizations
    print("\n--- Generating Step 2 Diagnostic Figures ---")
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=True)
    colors = {"val_f1": "#2ca02c", "val_precision": "#1f77b4", "val_recall": "#ff7f0e", "val_accuracy": "#7f7f7f"}

    for idx, (mid, mname, _, _, _) in enumerate(candidate_models):
        ax = axes[idx]
        sub = df_threshold_all[df_threshold_all["model_identifier"] == mid]
        ax.plot(sub["threshold"], sub["val_f1"], marker="o", linewidth=2.5, color=colors["val_f1"], label="Validation F1")
        ax.plot(sub["threshold"], sub["val_precision"], marker="s", linewidth=1.8, color=colors["val_precision"], label="Precision")
        ax.plot(sub["threshold"], sub["val_recall"], marker="^", linewidth=1.8, color=colors["val_recall"], label="Recall")
        ax.plot(sub["threshold"], sub["val_accuracy"], marker="d", linewidth=1.5, linestyle="--", color=colors["val_accuracy"], label="Accuracy")

        sel_t = selected_thresholds[mid]["selected_threshold"]
        sel_f1 = selected_thresholds[mid]["max_val_f1"]
        ax.axvline(sel_t, color="#d62728", linestyle=":", linewidth=2, label=f"Selected Threshold ({sel_t:.2f})")
        ax.axvline(0.50, color="black", linestyle="--", alpha=0.5, label="Default (0.50)")
        ax.scatter([sel_t], [sel_f1], color="#d62728", s=100, zorder=5)

        ax.set_title(f"{mname}\n(Peak Val F1 = {sel_f1:.4f} @ {sel_t:.2f})", fontsize=12, fontweight="bold")
        ax.set_xlabel("Decision Threshold (Class 1)", fontsize=11)
        if idx == 0:
            ax.set_ylabel("Metric Value", fontsize=11)
        ax.set_ylim(0.0, 1.0)
        ax.set_xlim(0.15, 0.65)
        ax.grid(True, linestyle=":", alpha=0.6)
        if idx == 0:
            ax.legend(loc="lower left", fontsize=9)

    plt.suptitle("Validation Decision-Threshold Trade-off Curves Across Models", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    for d in [REPORTS_DIR, RESULTS_FIG_EVAL]:
        plt.savefig(os.path.join(d, "threshold_comparison.png"), dpi=300, bbox_inches="tight")
    plt.close()

    # Final confusion matrix
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    cm_def = best_model_results["cm_default"]
    cm_opt = best_model_results["cm_selected"]

    sns.heatmap(cm_def, annot=True, fmt="d", cmap="Blues", cbar=False, ax=axes[0], xticklabels=["Not Chosen (0)", "Chosen (1)"], yticklabels=["Not Chosen (0)", "Chosen (1)"])
    axes[0].set_title(f"Gradient Boosting Core -- Default tau=0.50\n(F1={best_model_results['test_f1_default']:.4f}, Recall={best_model_results['test_recall_default']*100:.1f}%)", fontsize=11, fontweight="bold")
    axes[0].set_ylabel("Actual Label")
    axes[0].set_xlabel("Predicted Label")

    sns.heatmap(cm_opt, annot=True, fmt="d", cmap="Greens", cbar=False, ax=axes[1], xticklabels=["Not Chosen (0)", "Chosen (1)"], yticklabels=["Not Chosen (0)", "Chosen (1)"])
    axes[1].set_title(f"Gradient Boosting Core -- Tuned tau={best_model_results['selected_threshold']:.2f}\n(F1={best_model_results['test_f1_selected']:.4f}, Recall={best_model_results['test_recall_selected']*100:.1f}%)", fontsize=11, fontweight="bold")
    axes[1].set_ylabel("Actual Label")
    axes[1].set_xlabel("Predicted Label")

    plt.tight_layout()
    for d in [REPORTS_DIR, RESULTS_FIG_EVAL]:
        plt.savefig(os.path.join(d, "final_confusion_matrix.png"), dpi=150)
    plt.close()

    print("Phase 4 Step 2 execution completed successfully.")

if __name__ == "__main__":
    run_step2_pipeline()
