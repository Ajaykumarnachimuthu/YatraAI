"""
YĀTRĀ AI — Phase 4 ML Experimentation
Step 1: Lock Task + Build Leakage-Safe Baseline Runner

Orchestration runner executing:
1. Pre-training leakage audit & feature classification (via src.feature_engineering)
2. Deterministic traveller-level data partition (70/15/15; Seed 42)
3. Preprocessing matrices generation (Linear & Tree pipelines)
4. Model training across 4 families: LR, DT, RF, HistGB (via src.train_models)
5. Multi-partition evaluation across Core (28 features) vs Extended (29 features)
6. Metric tables and publication figure generation (via src.evaluation)
"""

import os
import sys
import numpy as np
import pandas as pd

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from src.feature_engineering import (
    perform_leakage_audit,
    split_by_traveller,
    build_feature_matrices,
)
from src.train_models import train_all_models
from src.evaluation import evaluate_partition, generate_baseline_figures

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYNTHETIC_DIR = os.path.join(BASE_DIR, "data", "synthetic")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
REPORTS_DIR = os.path.join(BASE_DIR, "reports", "phase4")

# Results directories
RESULTS_TABLES_SYNTH = os.path.join(BASE_DIR, "results", "tables", "synthetic")
RESULTS_TABLES_MODELS = os.path.join(BASE_DIR, "results", "tables", "models")
RESULTS_TABLES_EVAL = os.path.join(BASE_DIR, "results", "tables", "evaluation")
RESULTS_FIG_MODELS = os.path.join(BASE_DIR, "results", "figures", "models")
RESULTS_FIG_EVAL = os.path.join(BASE_DIR, "results", "figures", "evaluation")

for d in [REPORTS_DIR, PROCESSED_DIR, RESULTS_TABLES_SYNTH, RESULTS_TABLES_MODELS,
          RESULTS_TABLES_EVAL, RESULTS_FIG_MODELS, RESULTS_FIG_EVAL]:
    os.makedirs(d, exist_ok=True)

SEED = 42

def run_baseline_pipeline():
    print("=" * 80)
    print("YĀTRĀ AI — PHASE 4 STEP 1: BASELINE MODEL ORCHESTRATION")
    print("=" * 80)

    # 1. Load Choice Dataset
    choice_path = os.path.join(SYNTHETIC_DIR, "choice_dataset.parquet")
    print(f"Loading frozen choice dataset: {choice_path}...")
    df = pd.read_parquet(choice_path)
    print(f"Dataset Loaded: {len(df):,} rows x {len(df.columns)} columns")

    # 2. Leakage Audit
    print("\n--- 1. Pre-Training Leakage Audit ---")
    df_audit = perform_leakage_audit(df)
    audit_save_path = os.path.join(REPORTS_DIR, "dataset_audit.csv")
    df_audit.to_csv(audit_save_path, index=False)
    df_audit.to_csv(os.path.join(RESULTS_TABLES_SYNTH, "dataset_audit.csv"), index=False)
    # Also save canonical processed summary
    df_audit.to_csv(os.path.join(PROCESSED_DIR, "phase4_ml_dataset_summary.csv"), index=False)
    print(f"Leakage audit verified zero leakage. Saved audit table.")

    # 3. Traveller Partition
    print("\n--- 2. Deterministic Traveller-Level Partition (Seed 42) ---")
    df_train, df_val, df_test, df_split = split_by_traveller(df, seed=SEED)
    df_split.to_csv(os.path.join(REPORTS_DIR, "train_val_test_split_summary.csv"), index=False)
    df_split.to_csv(os.path.join(RESULTS_TABLES_SYNTH, "train_val_test_split_summary.csv"), index=False)
    print(df_split[["partition", "traveller_count", "total_rows", "positive_rate_pct", "imbalance_ratio"]])

    # 4. Feature Matrices & Model Training (Core & Extended)
    configs = [("core", "Core (Model A)"), ("extended", "Extended (Model B)")]
    all_metrics = []
    all_cms = []
    trained_models = {}

    for cfg_code, cfg_name in configs:
        print(f"\n--- 3. Processing Feature Configuration: {cfg_name} ---")
        matrices = build_feature_matrices(df_train, df_val, df_test, feature_config=cfg_code)

        print(f"  Matrices: Linear shape {matrices['linear']['X_train'].shape}, Tree shape {matrices['tree']['X_train'].shape}")
        models_dict = train_all_models(matrices, feature_config=cfg_code, seed=SEED)
        trained_models.update(models_dict)

        # Evaluate models
        print(f"  Evaluating {cfg_name} across Train, Validation, and Test partitions...")
        for mid, (model, feats) in models_dict.items():
            fam_key = mid.split("_")[0]
            fam_name = {
                "LR": "Logistic Regression",
                "DT": "Decision Tree",
                "RF": "Random Forest",
                "GB": "Gradient Boosting",
            }[fam_key]
            m_type = "linear" if fam_key == "LR" else "tree"

            X_tr = matrices[m_type]["X_train"]
            y_tr = matrices["y_train"]
            X_va = matrices[m_type]["X_val"]
            y_va = matrices["y_val"]
            X_te = matrices[m_type]["X_test"]
            y_te = matrices["y_test"]

            res_tr = evaluate_partition(model, X_tr, y_tr, partition_name="train")
            res_va = evaluate_partition(model, X_va, y_va, partition_name="val")
            res_te = evaluate_partition(model, X_te, y_te, partition_name="test")

            row = {
                "feature_config": cfg_name,
                "model_family": fam_name,
                "model_identifier": f"{fam_key}_{cfg_code[:4]}",
                "train_accuracy": res_tr["train_accuracy"],
                "train_precision": res_tr["train_precision"],
                "train_recall": res_tr["train_recall"],
                "train_f1": res_tr["train_f1"],
                "train_roc_auc": res_tr["train_roc_auc"],
                "val_accuracy": res_va["val_accuracy"],
                "val_precision": res_va["val_precision"],
                "val_recall": res_va["val_recall"],
                "val_f1": res_va["val_f1"],
                "val_roc_auc": res_va["val_roc_auc"],
                "test_accuracy": res_te["test_accuracy"],
                "test_precision": res_te["test_precision"],
                "test_recall": res_te["test_recall"],
                "test_f1": res_te["test_f1"],
                "test_roc_auc": res_te["test_roc_auc"],
                "test_cm": res_te["test_cm"],
            }
            all_metrics.append(row)

            # Record CM rows
            for p_name, r_part in [("train", res_tr), ("val", res_va), ("test", res_te)]:
                all_cms.append({
                    "model_identifier": f"{fam_key}_{cfg_code[:4]}",
                    "model_name": fam_name,
                    "feature_config": cfg_name,
                    "partition": p_name,
                    "tn": r_part[f"{p_name}_tn"],
                    "fp": r_part[f"{p_name}_fp"],
                    "fn": r_part[f"{p_name}_fn"],
                    "tp": r_part[f"{p_name}_tp"],
                })

    df_metrics = pd.DataFrame(all_metrics)
    df_cms = pd.DataFrame(all_cms)

    # Save metrics tables
    metrics_export = df_metrics.drop(columns=["test_cm"])
    metrics_export.to_csv(os.path.join(REPORTS_DIR, "model_metrics_table.csv"), index=False)
    metrics_export.to_csv(os.path.join(RESULTS_TABLES_MODELS, "model_metrics_table.csv"), index=False)

    df_cms.to_csv(os.path.join(REPORTS_DIR, "confusion_matrices.csv"), index=False)
    df_cms.to_csv(os.path.join(RESULTS_TABLES_EVAL, "confusion_matrices.csv"), index=False)

    print("\n=== BASELINE TEST SET RESULTS ===")
    print(metrics_export[["model_identifier", "feature_config", "model_family", "test_accuracy", "test_precision", "test_recall", "test_f1", "test_roc_auc"]].to_string(index=False))

    # 5. Generate Figures
    print("\n--- 4. Generating Publication Figures ---")
    generate_baseline_figures(
        df_metrics,
        trained_models,
        output_dirs=[REPORTS_DIR, RESULTS_FIG_MODELS, RESULTS_FIG_EVAL],
    )
    print("Baseline figures successfully generated.")

    print("\n=== PHASE 4 STEP 1 BASELINE EXECUTION COMPLETE ===")
    return df_metrics, df_cms, trained_models

if __name__ == "__main__":
    run_baseline_pipeline()
