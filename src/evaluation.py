"""
YĀTRĀ AI — Model Evaluation & Decision-Threshold Optimization Suite
Authoritative module for:
- Computing classification metrics: Accuracy, Precision, Recall, F1, ROC-AUC
- Constructing detailed confusion matrices across data partitions
- Rigorous decision-threshold tuning strictly on validation partitions
- Generating publication-quality diagnostic figures
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_EVAL_DIR = os.path.join(BASE_DIR, "results", "figures", "evaluation")
RESULTS_MODELS_FIG_DIR = os.path.join(BASE_DIR, "results", "figures", "models")
REPORTS_PHASE4_DIR = os.path.join(BASE_DIR, "reports", "phase4")

os.makedirs(RESULTS_EVAL_DIR, exist_ok=True)
os.makedirs(RESULTS_MODELS_FIG_DIR, exist_ok=True)
os.makedirs(REPORTS_PHASE4_DIR, exist_ok=True)

# ==============================================================================
# 1. PARTITION EVALUATION
# ==============================================================================

def evaluate_partition(model, X, y, partition_name="test", threshold=0.50):
    """
    Evaluates a trained model on a given data matrix and target vector.
    Returns metrics dictionary and raw confusion matrix.
    """
    if hasattr(model, "predict_proba"):
        y_prob = model.predict_proba(X)[:, 1]
    else:
        y_prob = model.decision_function(X)

    y_pred = (y_prob >= threshold).astype(int)

    acc = float(accuracy_score(y, y_pred))
    prec = float(precision_score(y, y_pred, zero_division=0))
    rec = float(recall_score(y, y_pred, zero_division=0))
    f1 = float(f1_score(y, y_pred, zero_division=0))
    auc = float(roc_auc_score(y, y_prob))
    cm = confusion_matrix(y, y_pred)

    tn, fp, fn, tp = cm.ravel()

    return {
        f"{partition_name}_accuracy": round(acc, 4),
        f"{partition_name}_precision": round(prec, 4),
        f"{partition_name}_recall": round(rec, 4),
        f"{partition_name}_f1": round(f1, 4),
        f"{partition_name}_roc_auc": round(auc, 4),
        f"{partition_name}_cm": cm,
        f"{partition_name}_tp": int(tp),
        f"{partition_name}_fp": int(fp),
        f"{partition_name}_fn": int(fn),
        f"{partition_name}_tn": int(tn),
    }

# ==============================================================================
# 2. VALIDATION DECISION-THRESHOLD OPTIMIZATION
# ==============================================================================

def sweep_decision_thresholds(
    model,
    X_val,
    y_val,
    model_identifier,
    model_name,
    feature_config="core",
    thresholds=None,
):
    """
    Sweeps decision thresholds exclusively on the validation set.
    """
    if thresholds is None:
        thresholds = [0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60]

    if hasattr(model, "predict_proba"):
        y_prob_val = model.predict_proba(X_val)[:, 1]
    else:
        y_prob_val = model.decision_function(X_val)

    val_auc = float(roc_auc_score(y_val, y_prob_val))
    records = []

    for t in thresholds:
        y_pred = (y_prob_val >= t).astype(int)
        cm = confusion_matrix(y_val, y_pred)
        tn, fp, fn, tp = cm.ravel()

        records.append({
            "model_identifier": model_identifier,
            "model_name": model_name,
            "feature_config": feature_config,
            "threshold": round(float(t), 2),
            "val_accuracy": round(float(accuracy_score(y_val, y_pred)), 4),
            "val_precision": round(float(precision_score(y_val, y_pred, zero_division=0)), 4),
            "val_recall": round(float(recall_score(y_val, y_pred, zero_division=0)), 4),
            "val_f1": round(float(f1_score(y_val, y_pred, zero_division=0)), 4),
            "val_roc_auc": round(val_auc, 4),
            "val_tp": int(tp),
            "val_fp": int(fp),
            "val_fn": int(fn),
            "val_tn": int(tn),
        })

    return pd.DataFrame(records)

def select_optimal_threshold(df_thresholds, model_id, metric="val_f1"):
    """
    Selects optimal threshold maximizing validation metric.
    Tie-breaking: prefers higher threshold for greater precision.
    """
    subset = df_thresholds[df_thresholds["model_identifier"] == model_id].copy()
    max_val = subset[metric].max()
    candidates = subset[subset[metric] == max_val]
    best_row = candidates.sort_values("threshold", ascending=False).iloc[0]
    return float(best_row["threshold"]), best_row

# ==============================================================================
# 3. VISUALIZATION FUNCTIONS
# ==============================================================================

def generate_baseline_figures(df_metrics, trained_models, output_dirs=None):
    """
    Renders baseline comparison charts:
    1. model_comparison_plot.png
    2. train_vs_val_test_comparison.png
    3. feature_importance_plot.png
    4. confusion_matrices_plot.png
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    if output_dirs is None:
        output_dirs = [REPORTS_PHASE4_DIR, RESULTS_MODELS_FIG_DIR, RESULTS_EVAL_DIR]

    for d in output_dirs:
        os.makedirs(d, exist_ok=True)

    # 1. Model Comparison Plot
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    metrics_to_plot = ["test_accuracy", "test_precision", "test_recall", "test_f1", "test_roc_auc"]
    metric_labels = ["Accuracy", "Precision", "Recall", "F1 Score", "ROC-AUC"]

    df_core = df_metrics[df_metrics["feature_config"] == "Core (Model A)"]
    df_core_melt = df_core.melt(id_vars=["model_family"], value_vars=metrics_to_plot, var_name="metric", value_name="score")
    df_core_melt["metric_label"] = df_core_melt["metric"].map(dict(zip(metrics_to_plot, metric_labels)))

    sns.barplot(data=df_core_melt, x="model_family", y="score", hue="metric_label", palette="tab10", ax=axes[0])
    axes[0].set_title("Test Set Evaluation Metrics: Core Features (Model A)", fontsize=12, fontweight="bold")
    axes[0].set_ylabel("Metric Score", fontsize=11)
    axes[0].set_xlabel("Model Family", fontsize=11)
    axes[0].set_ylim(0, 1.0)
    axes[0].legend(loc="upper right", fontsize=9)

    df_ext = df_metrics[df_metrics["feature_config"] == "Extended (Model B)"]
    df_ext_melt = df_ext.melt(id_vars=["model_family"], value_vars=metrics_to_plot, var_name="metric", value_name="score")
    df_ext_melt["metric_label"] = df_ext_melt["metric"].map(dict(zip(metrics_to_plot, metric_labels)))

    sns.barplot(data=df_ext_melt, x="model_family", y="score", hue="metric_label", palette="tab10", ax=axes[1])
    axes[1].set_title("Test Set Evaluation Metrics: Extended Features (Model B)", fontsize=12, fontweight="bold")
    axes[1].set_ylabel("Metric Score", fontsize=11)
    axes[1].set_xlabel("Model Family", fontsize=11)
    axes[1].set_ylim(0, 1.0)
    axes[1].legend(loc="upper right", fontsize=9)

    plt.tight_layout()
    for d in [REPORTS_PHASE4_DIR, RESULTS_MODELS_FIG_DIR]:
        plt.savefig(os.path.join(d, "model_comparison_plot.png"), dpi=150)
    plt.close()

    # 2. Overfitting Check: Train vs Val vs Test ROC-AUC
    plt.figure(figsize=(10, 5))
    df_overfit = df_metrics[df_metrics["feature_config"] == "Core (Model A)"].copy()
    overfit_vars = ["train_roc_auc", "val_roc_auc", "test_roc_auc"]
    df_overfit_melt = df_overfit.melt(id_vars=["model_family"], value_vars=overfit_vars, var_name="partition", value_name="roc_auc")
    df_overfit_melt["partition"] = df_overfit_melt["partition"].map({"train_roc_auc": "Train", "val_roc_auc": "Validation", "test_roc_auc": "Test"})

    sns.barplot(data=df_overfit_melt, x="model_family", y="roc_auc", hue="partition", palette="magma")
    plt.title("Overfitting Diagnostic: Train vs. Validation vs. Test (Core Model A)", fontsize=12, fontweight="bold")
    plt.ylabel("ROC-AUC Score", fontsize=11)
    plt.xlabel("Model Family", fontsize=11)
    plt.ylim(0.5, 1.0)
    for p in plt.gca().patches:
        h = p.get_height()
        if h > 0:
            plt.gca().annotate(f"{h:.3f}", (p.get_x() + p.get_width() / 2.0, h), ha="center", va="bottom", fontsize=8, xytext=(0, 2), textcoords="offset points")
    plt.tight_layout()
    for d in [REPORTS_PHASE4_DIR, RESULTS_MODELS_FIG_DIR]:
        plt.savefig(os.path.join(d, "train_vs_val_test_comparison.png"), dpi=150)
    plt.close()

    # 3. Feature Importance Plot
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    if "LR_Core (Model A)" in trained_models:
        lr_model, lr_feats = trained_models["LR_Core (Model A)"]
        lr_coefs = lr_model.coef_[0]
        df_lr_imp = pd.DataFrame({"feature": lr_feats, "coefficient": lr_coefs})
        df_lr_imp["abs_coef"] = df_lr_imp["coefficient"].abs()
        top_lr = df_lr_imp.sort_values("abs_coef", ascending=False).head(15)
        sns.barplot(data=top_lr, x="coefficient", y="feature", hue="feature", ax=axes[0], palette=["#d62728" if c < 0 else "#1f77b4" for c in top_lr["coefficient"]], legend=False)
        axes[0].set_title("Logistic Regression: Top 15 Standardized Coefficients (Core)", fontsize=11, fontweight="bold")
        axes[0].set_xlabel("Coefficient Magnitude (Blue: +, Red: -)", fontsize=10)
        axes[0].set_ylabel("")

    if "RF_Core (Model A)" in trained_models:
        rf_model, rf_feats = trained_models["RF_Core (Model A)"]
        rf_imps = rf_model.feature_importances_
        df_rf_imp = pd.DataFrame({"feature": rf_feats, "importance": rf_imps})
        top_rf = df_rf_imp.sort_values("importance", ascending=False).head(15)
        sns.barplot(data=top_rf, x="importance", y="feature", hue="feature", ax=axes[1], palette="viridis", legend=False)
        axes[1].set_title("Random Forest: Top 15 Gini Feature Importances (Core)", fontsize=11, fontweight="bold")
        axes[1].set_xlabel("Relative Importance", fontsize=10)
        axes[1].set_ylabel("")

    plt.tight_layout()
    for d in [REPORTS_PHASE4_DIR, RESULTS_MODELS_FIG_DIR]:
        plt.savefig(os.path.join(d, "feature_importance_plot.png"), dpi=150)
    plt.close()

    # 4. Confusion Matrices Plot
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    core_models = ["LR_Core (Model A)", "DT_Core (Model A)", "RF_Core (Model A)", "GB_Core (Model A)"]
    ext_models = ["LR_Extended (Model B)", "DT_Extended (Model B)", "RF_Extended (Model B)", "GB_Extended (Model B)"]

    for idx, mid in enumerate(core_models):
        fam = mid[:2].upper()
        sub = df_metrics[df_metrics["model_identifier"].str.upper() == f"{fam}_CORE"]
        row_data = sub.iloc[0]
        cm = row_data["test_cm"]
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False, ax=axes[0, idx], xticklabels=["Not Chosen", "Chosen"], yticklabels=["Not Chosen", "Chosen"])
        axes[0, idx].set_title(f"Test CM: {mid.split(' (')[0]} (Core)", fontsize=10, fontweight="bold")
        axes[0, idx].set_ylabel("True Label")
        axes[0, idx].set_xlabel("Predicted Label")

    for idx, mid in enumerate(ext_models):
        fam = mid[:2].upper()
        sub = df_metrics[df_metrics["model_identifier"].str.upper() == f"{fam}_EXTE"]
        row_data = sub.iloc[0]
        cm = row_data["test_cm"]
        sns.heatmap(cm, annot=True, fmt="d", cmap="Greens", cbar=False, ax=axes[1, idx], xticklabels=["Not Chosen", "Chosen"], yticklabels=["Not Chosen", "Chosen"])
        axes[1, idx].set_title(f"Test CM: {mid.split(' (')[0]} (Ext)", fontsize=10, fontweight="bold")
        axes[1, idx].set_ylabel("True Label")
        axes[1, idx].set_xlabel("Predicted Label")

    plt.tight_layout()
    for d in [REPORTS_PHASE4_DIR, RESULTS_EVAL_DIR]:
        plt.savefig(os.path.join(d, "confusion_matrices_plot.png"), dpi=150)
    plt.close()

def generate_step2_figures(df_thresholds, best_model_results, output_dirs=None):
    """
    Renders threshold comparison and final confusion matrix:
    1. threshold_comparison.png
    2. final_confusion_matrix.png
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    if output_dirs is None:
        output_dirs = [REPORTS_PHASE4_DIR, RESULTS_EVAL_DIR]

    for d in output_dirs:
        os.makedirs(d, exist_ok=True)

    # 1. Threshold comparison
    plt.figure(figsize=(15, 5))
    models_to_plot = ["RF_core", "GB_core", "GB_exte"]
    titles = ["Random Forest Core", "Gradient Boosting Core", "Gradient Boosting Extended"]

    for idx, (mid, title) in enumerate(zip(models_to_plot, titles)):
        plt.subplot(1, 3, idx + 1)
        sub = df_thresholds[df_thresholds["model_identifier"] == mid]
        plt.plot(sub["threshold"], sub["val_f1"], "o-", label="F1 Score", color="#1f77b4", linewidth=2)
        plt.plot(sub["threshold"], sub["val_precision"], "s--", label="Precision", color="#2ca02c")
        plt.plot(sub["threshold"], sub["val_recall"], "^--", label="Recall", color="#d62728")
        plt.plot(sub["threshold"], sub["val_accuracy"], "d:", label="Accuracy", color="#7f7f7f")

        best_t = sub.loc[sub["val_f1"].idxmax(), "threshold"]
        best_f1 = sub["val_f1"].max()
        plt.axvline(best_t, color="black", linestyle="--", alpha=0.7, label=f"Best tau={best_t:.2f} (F1={best_f1:.4f})")

        plt.title(title, fontsize=11, fontweight="bold")
        plt.xlabel("Decision Threshold (tau)")
        plt.ylabel("Score")
        plt.ylim(0, 1.0)
        plt.grid(True, linestyle="--", alpha=0.5)
        if idx == 0:
            plt.legend(loc="lower left", fontsize=8)

    plt.tight_layout()
    for d in output_dirs:
        plt.savefig(os.path.join(d, "threshold_comparison.png"), dpi=150)
    plt.close()

    # 2. Final Confusion Matrix (Default vs Tuned)
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
    for d in output_dirs:
        plt.savefig(os.path.join(d, "final_confusion_matrix.png"), dpi=150)
    plt.close()
