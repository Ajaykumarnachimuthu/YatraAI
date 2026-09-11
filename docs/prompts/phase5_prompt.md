# YĀTRĀ AI — Phase 5 Requirement Specification & Prompt Archive

## 1. Phase Objective
Consolidate the multi-modal transportation data foundation, behavioural simulation engine, and optimized machine learning choice model into an integrated, reproducible, publication-ready travel intelligence system. Document end-to-end system architecture, verify offline reproducibility, validate the standalone inference pipeline, evaluate scientific limitations and operational boundaries, generate an executive slide presentation, and prepare a comprehensive defense package for viva examination.

---

## 2. Core Directives & Constraints
1. **No New ML Models**: The experimental phase is complete and frozen. Use the validated champion model (`HistGradientBoostingClassifier`, Core 28 features, $\tau^* = 0.30$).
2. **Honest Scientific Boundary**: Explicitly declare that traveller choices are synthetic behavioural ground truth generated under RUM/MNL. Do not claim observed real-world user tracking.
3. **Reproducibility Audit**: Every result, metric, table, and figure must be generated strictly from real code and frozen datasets without manual intervention.
4. **End-to-End Inference Verification**: Test the serialized `champion_gb_core.joblib` pipeline with dynamic inputs to verify production readiness.
5. **No Academic Structure**: Maintain software engineering repository architecture (`src/`, `data/`, `notebooks/`, `results/`, `docs/`, `reports/`).

---

## 3. Required Deliverables
1. **Executive Summary & Comprehensive Final Report**:
   - `reports/final/executive_summary.md`
   - `reports/final/final_report.md`
   - `reports/final/final_comprehensive_report.md` (synthesizing all 5 phases)
2. **Viva Defense Package**:
   - `reports/final/viva_questions_and_answers.md`: 25 in-depth technical questions and defensible answers spanning transport theory, RUM/MNL math, ML bias-variance trade-offs, and production engineering.
3. **Limitations & Future Work**:
   - `reports/final/limitations_and_future_work.md`: Critical appraisal of pricing heuristics, weather integration, static timetables, and roadmap for real-time NTES API integration.
4. **Executive PowerPoint Presentation**:
   - `reports/final/Yatra_AI_Final_Presentation.pptx`: 12-slide professional presentation with embedded high-resolution figures, architecture diagrams, and speaker notes.
   - Verified automated generator script: `src/generate_presentation.py`.
5. **Consolidated Tables & Verification Matrix**:
   - Implementation coverage audit, reproducibility matrix, and final performance metrics table in `results/tables/`.
