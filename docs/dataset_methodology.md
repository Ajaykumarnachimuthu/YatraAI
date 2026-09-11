# YĀTRĀ AI — Dataset Acquisition & Engineering Methodology

## 1. Principles of Data Strategy

Project Yātrā AI employs a **Hybrid Real-Data Strategy** for India:
1. **Real/Public Data Primacy**: Real-world transit topology, timetables, delays, and fares form the non-negotiable core.
2. **Official Government Alignment**: Open Government Data (OGD data.gov.in, IMD, Ministry of Railways) is prioritized as the ground truth.
3. **Reproducible Provenance**: Every dataset must have verifiable origin, explicit licensing (e.g. MIT, GODL, CC0), and cryptographic SHA-256 validation.
4. **Non-Destructive Ingestion**: Downloaded files must remain completely untouched in `data/raw/`. No in-place editing or ad-hoc transformations are permitted on raw assets.
5. **Decoupled Architecture**: Raw provider structures are translated into canonical Yātrā schemas (`TransitStationNode`, `TransitScheduleSegment`, etc.) via adapters in `src/`, preventing vendor lock-in.
6. **Synthetic Data Boundaries**: Synthetic data is strictly restricted to traveller preference simulations where privacy constraints preclude real user profiling. No synthetic operational data (stations, tracks, timetables) is permitted.

---

## 2. Directory Hierarchy

```
YatraAI/
├── data/
│   ├── raw/                  # Untouched original downloads
│   │   ├── railways/         # Station coordinates & train schedules (JSON)
│   │   ├── delays/           # Historical train delays & punctuality (CSV)
│   │   ├── flights/          # Domestic flight itineraries & prices (CSV)
│   │   └── environmental/    # Subdivisional rainfall & climate (CSV)
│   ├── external/             # Machine-readable metadata & schema mapping
│   ├── processed/            # Canonical normalized datasets (Phase 2)
│   └── synthetic/            # Simulated traveler preference personas (Phase 3)
├── docs/
│   ├── data_sources.md       # Detailed technical catalog of all datasets
│   ├── dataset_methodology.md# Architectural principles & standards
│   └── phase1_report.md      # Phase 1 evaluation & component mapping report
```

---

## 3. Data Governance & Licensing Matrix

| Dataset Category | Source Entity | Applicable License | Usage Permissibility |
| :--- | :--- | :--- | :--- |
| **Railways Station Master** | CRIS / Open Contributor | MIT License | Commercial & Non-Commercial with attribution |
| **Railways Timetable Master** | Indian Railways Timetable | MIT License | Open Access / Research & Analytics |
| **Train Delay Statistics** | NTES / Academic DA323 | Open Academic / Public Log | Research, benchmarking & predictive modeling |
| **Domestic Flights Pricing** | EaseMyTrip / Public Domain | CC0 / Public Domain | Open Data Analytics & ML Modeling |
| **Historical Rainfall** | India Meteorological Dept | Government Open Data License (GODL) | Worldwide, royalty-free public use |
