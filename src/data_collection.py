"""
YĀTRĀ AI — Multimodal Transit Data Source Registry & Provenance Auditor
Authoritative module for tracking public transit data origins, license attribution,
file integrity checksums, and schema registrations.
"""

import os
import sys
import json
import hashlib
import pandas as pd

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METADATA_PATH = os.path.join(BASE_DIR, "data", "external", "sources_metadata.json")

def load_sources_metadata(metadata_path=METADATA_PATH):
    """Loads canonical source metadata and provenance catalog."""
    if not os.path.exists(metadata_path):
        raise FileNotFoundError(f"Source metadata file not found at: {metadata_path}")
    with open(metadata_path, "r", encoding="utf-8") as f:
        return json.load(f)

def compute_sha256(filepath):
    """Computes standard SHA-256 hash of a local file in read-only binary chunks."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()

def verify_source_integrity(metadata_path=METADATA_PATH):
    """
    Validates local raw datasets against documented file sizes and SHA-256 checksums.
    Returns a structured verification report.
    """
    catalog = load_sources_metadata(metadata_path)
    report = []
    
    for src in catalog.get("sources", []):
        src_id = src["id"]
        rel_path = src.get("local_path") or src.get("local_path_manifest")
        abs_path = os.path.join(BASE_DIR, rel_path)
        
        file_exists = os.path.exists(abs_path)
        actual_size = os.path.getsize(abs_path) if file_exists else None
        expected_size = src.get("size_bytes")
        
        expected_sha = src.get("sha256") or src.get("sha256_manifest")
        actual_sha = compute_sha256(abs_path) if file_exists else None
        
        hash_match = (actual_sha == expected_sha) if (actual_sha and expected_sha) else False
        size_match = (actual_size == expected_size) if (actual_size and expected_size) else True
        
        report.append({
            "source_id": src_id,
            "dataset_name": src["dataset_name"],
            "local_path": rel_path,
            "exists": file_exists,
            "size_bytes": actual_size,
            "expected_size_bytes": expected_size,
            "size_match": size_match,
            "sha256": actual_sha,
            "expected_sha256": expected_sha,
            "hash_match": hash_match,
            "status": "VERIFIED" if (file_exists and hash_match and size_match) else "ANOMALY"
        })
        
    return pd.DataFrame(report)

def get_raw_inventory():
    """Returns file count and total storage footprint of data/raw directory."""
    raw_dir = os.path.join(BASE_DIR, "data", "raw")
    inventory = []
    for root, _, files in os.walk(raw_dir):
        for f in files:
            p = os.path.join(root, f)
            rel_p = os.path.relpath(p, BASE_DIR).replace("\\", "/")
            inventory.append({
                "file_path": rel_p,
                "size_bytes": os.path.getsize(p)
            })
    return pd.DataFrame(inventory)

def display_provenance_summary():
    """Prints a formatted console summary of data provenance and integrity."""
    print("=" * 80)
    print("YATRA AI -- DATA PROVENANCE & INTEGRITY AUDIT")
    print("=" * 80)
    df_verify = verify_source_integrity()
    all_passed = (df_verify["status"] == "VERIFIED").all()
    
    for idx, row in df_verify.iterrows():
        print(f"[{row['status']}] {row['dataset_name']}")
        print(f"  Path: {row['local_path']}")
        print(f"  Size: {row['size_bytes']:,} bytes (Matches expected: {row['size_match']})")
        print(f"  SHA-256: {row['sha256']}")
        print(f"  Hash Verified: {row['hash_match']}")
        print("-" * 80)
        
    print(f"\nOverall Raw Source Verification: {'ALL SOURCES VERIFIED' if all_passed else 'ATTENTION REQUIRED'}")
    return all_passed

if __name__ == "__main__":
    success = display_provenance_summary()
    sys.exit(0 if success else 1)
