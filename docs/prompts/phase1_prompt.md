# YĀTRĀ AI — Phase 1 Requirement Specification & Prompt Archive

## 1. Phase Objective
Establish the real, public, and open government data foundation for Yātrā AI—an AI-driven multimodal travel recommendation and journey orchestration engine for India. Formulate the transportation domain context, discover candidate datasets across open repositories, evaluate data provenance and licensing, and store unadulterated raw assets in the repository.

---

## 2. Core Directives & Constraints
1. **Zero Synthetic Data**: Absolutely no synthetic traveller profiles, synthetic search sessions, or simulated choices may be generated during Phase 1.
2. **Zero Machine Learning**: No machine learning models, baselines, or predictive classifiers may be trained prematurely.
3. **No Mock APIs or Fake Downloaders**: Only genuinely accessible public data sources may be used.
4. **Provider Independence**: Datasets must be catalogued with schema mappings so the system does not depend on proprietary third-party APIs.
5. **Raw Data Immutability**: All downloaded assets must be preserved in `data/raw/` in their original format without manual editing.

---

## 3. Required Input Sources & Discovery Scope
Investigate official Indian transit, aviation, geographic, and climatological datasets across:
* Official open government portals: `data.gov.in`, CRIS, NTES, India Meteorological Department (IMD).
* Vetted open-source repositories: DataMeet Indian Railways, Academic GitHub repositories.
* Aviation pricing archives: EaseMyTrip domestic route aggregations.

---

## 4. Required Deliverables
1. **Candidate Datasets Evaluated**: Document all investigated candidates, distinguishing between selected (KEEP), deferred, and rejected sources with clear technical rationale.
2. **Source Registry & Metadata**: Maintain `data/external/sources_metadata.json` capturing title, publisher, license, access URL, date accessed, file format, and byte size.
3. **Cryptographic Integrity Baseline**: Compute and record baseline SHA-256 hashes for all acquired raw files.
4. **Schema & Architectural Mapping**: Map raw datasets to planned Yātrā AI functional components (Topology Graph, Delay Predictor, Cross-Modal Comparator).
5. **Phase 1 Technical Report**: Deliver a comprehensive markdown report summarizing source selection, provenance, and data limitations.

---

## 5. Required Validation Checks
* File existence and non-zero byte size verification.
* Cryptographic SHA-256 checksum verification against external registry.
* Confirmation of open academic or public licensing (MIT, CC0, GODL-India).
* Domain relevance: Verified coverage across Indian rail networks, domestic aviation corridors, station coordinates, and monsoon precipitation.
