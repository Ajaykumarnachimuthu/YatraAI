# YĀTRĀ AI — Phase 4 Requirement Specification & Prompt Archive

## 1. Phase Objective
Design, train, evaluate, and optimize supervised machine learning models to solve Yātrā AI's itinerary choice prediction problem. Formulate binary classification predicting whether a candidate alternative is selected by a traveller (`chosen` $\in \{0, 1\}$). Enforce strict group-level traveller splitting to prevent identity leakage, compare linear and non-linear model families across Core and Extended feature sets, conduct rigorous evaluation under severe class imbalance, optimize decision thresholds for operational utility, and package the champion model.

---

## 2. Core Directives & Constraints
1. **Target Definition**:
   - Supervised binary target: `chosen` (1 = chosen alternative, 0 = not chosen).
   - Class imbalance: ~71.14% negative (98,603 rows) vs. ~28.86% positive (40,000 rows).
2. **Deterministic Group-Level Partitioning**:
   - Split strictly by `traveller_id`: 70% Train (3,500 travellers), 15% Validation (750 travellers), 15% Test (750 travellers).
   - Random seed strictly fixed at $42$. No session or traveller overlap across splits.
3. **Leakage Elimination**:
   - Strictly exclude post-choice indicators (`chosen`, `choice_probability`, `utility`, `rank`, `traveller_id`, `session_id`, `itinerary_id`).
   - Fit all preprocessors (scalers, encoders, imputers) exclusively on the training partition.
4. **Model Families Evaluated**:
   - Regularized Logistic Regression (L2, C=1.0)
   - Regularized Decision Tree (max_depth=6, min_samples_leaf=20)
   - Random Forest Classifier (100 estimators, max_depth=10, min_samples_leaf=10)
   - Histogram-based Gradient Boosting (100 max_iter, max_depth=6, lr=0.1)
5. **Feature Set Configurations**:
   - Core Features (28 features): 21 numeric features (Travel DNA + normalized candidate scores) + 7 categorical features.
   - Extended Features (29 features): Core features + unscaled candidate cost.
6. **Threshold Optimization**:
   - Tune classification threshold $\tau$ exclusively on the validation set across $\tau \in [0.20, 0.60]$ with step $0.01$.
   - Multi-criteria policy: $\max_\tau F_1(\tau)$ subject to $\text{Recall} \ge 0.50$ and $\text{Precision} \ge 0.35$.
   - Evaluate tuned threshold strictly once on the frozen test set.

---

## 3. Required Mathematical Formulations
* **Classification Accuracy**:
  $$\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}$$
* **Precision**:
  $$\text{Precision} = \frac{TP}{TP + FP}$$
* **Recall**:
  $$\text{Recall} = \frac{TP}{TP + FN}$$
* **F1-Score**:
  $$F_1 = \frac{2 \cdot \text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$
* **Threshold Optimization Objective**:
  $$\tau^* = \arg\max_{\tau \in [0.20, 0.60]} F_1(\tau) \quad \text{s.t.} \quad \text{Recall}(\tau) \ge 0.50, \; \text{Precision}(\tau) \ge 0.35$$
* **ROC-AUC**:
  Area under the Receiver Operating Characteristic curve.

---

## 4. Required Deliverables
1. **Model Training & Evaluation Scripts**: Clean, modular execution in `src/phase4_baseline.py` and `src/phase4_step2.py`.
2. **Machine-Readable Tables** in `results/tables/`:
   - `model_metrics_table.csv`: Baseline Train/Val/Test metrics across all models.
   - `confusion_matrices.csv`: TN, FP, FN, TP breakdowns.
   - `threshold_analysis.csv`: Detailed 41-step validation threshold sweep.
   - `final_model_comparison.csv`: Default ($\tau=0.50$) vs. Tuned ($\tau^*=0.30$) test performance.
   - `feature_importance_summary.csv`: Feature rankings for tree-based models.
3. **Publication-Quality Figures** in `results/figures/`:
   - Model comparison bar chart, train vs. val/test generalization plot, feature importance plot, confusion matrices grid, threshold sweep trade-off curve, final confusion matrix.
4. **Serialized Champion Model**: Self-contained inference engine in `results/models/champion_gb_core.joblib`.
5. **Phase 4 Evidence Reports**: Comprehensive documentation of baseline results, leakage audits, and threshold optimization.
