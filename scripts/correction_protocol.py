"""Canonical protocol checks for corrected Geneformer V1 feature artifacts.

The 2026-09 Kaggle archives did not export dictionary hashes. Their known
checkpoint hashes and fixture are validated; dictionary identity remains a
documented archival limitation until a new setup-provenance file is available.
"""

from __future__ import annotations

import hashlib

REVISION = "04c2b2e84da7c0f385c3f9ad8f3ec24bab6650e5"
SHARED_GENE_SHA256 = "482f113c433ac76eb19940442e4f3b1a24ae73d387c4ec75ecb19b8116eea29b"
CHECKPOINT_SHA256_BY_FILE = {
    "config.json": "9cf69ca3bdb0215c4188b54c451b6f02adfe68b8f66011a57d0f32845133fd4b",
    "model.safetensors": "a5e33a757431643b3697de7ef6127950cdc49e06e58d4266b3a3ab191b683f14",
    "pytorch_model.bin": "8d860e2125884475dd42bc2cd9a0e60c60808a7351241e08f2154931ffc142da",
    "training_args.bin": "f0ec3459454205174c9d2e4d6c6930f6b0fbf3364fc03a6f4d99c4d3add2012b",
}
# These are the verified dictionary hashes printed by the successful Kaggle
# setup cell, not values recovered from the four historical share archives.
EXPECTED_DICTIONARY_SHA256_BY_FILE = {
    "gene_median_dictionary_gc30M.pkl": "b3b589bb5ec75040d05fc44dd6bf0184cf87f3c362cf158d196a6ed3b7fe5f39",
    "token_dictionary_gc30M.pkl": "ab9dc40973fa5224d77b793e2fd114cacf3d08423ed9c4c49caf0ba9c7f218f1",
    "ensembl_mapping_dict_gc30M.pkl": "eac0fb0b3007267871b6305ac0003ceba19d4f28d85686cb9067ecf142787869",
}
COHORTS = {
    "dev": {"n": 261, "cells": 1263676, "n_field": "n_donors_embedded"},
    "external": {"n": 56, "cells": 363083, "n_field": "n_samples_embedded"},
}


def validate_summary(summary: dict, mode: str, cohort: str | None = None) -> None:
    """Reject wrong V1 settings even when both cohort summaries agree."""
    if mode not in {"shared", "native"}:
        raise ValueError("unknown gene input mode")
    expected = {
        "status": "success", "gene_input_mode": mode,
        "geneformer_revision": REVISION, "model": "Geneformer-V1-10M",
        "model_version": "V1", "model_input_size": 2048,
        "emb_mode": "cell", "emb_layer": -1,
        "aggregation": "mean_pool_per_donor", "tokenizer_num_proc": None,
        "embedding_dim": 256,
        "intersection_sha256": SHARED_GENE_SHA256 if mode == "shared" else None,
        "checkpoint_sha256_by_file": CHECKPOINT_SHA256_BY_FILE,
    }
    for field, value in expected.items():
        if summary.get(field) != value:
            raise ValueError(f"Geneformer protocol differs at {field}")
    digest = summary.get("embedding_sha256")
    if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        raise ValueError("embedding SHA-256 absent or invalid")
    if cohort is not None:
        if cohort not in COHORTS:
            raise ValueError("unknown cohort")
        spec = COHORTS[cohort]
        if (summary.get(spec["n_field"]) != spec["n"] or
                summary.get("total_cells_expected") != spec["cells"] or
                summary.get("total_cells_processed") != spec["cells"]):
            raise ValueError("cohort donor or cell accounting differs")


def validate_setup_provenance(record: dict, summary: dict) -> None:
    """Validate the machine-readable record exported by newer notebooks."""
    if record.get("geneformer_revision") != REVISION:
        raise ValueError("setup Geneformer revision differs")
    if record.get("dictionary_sha256_by_file") != EXPECTED_DICTIONARY_SHA256_BY_FILE:
        raise ValueError("setup V1 dictionary hashes differ")
    if record.get("checkpoint_sha256_by_file") != summary["checkpoint_sha256_by_file"]:
        raise ValueError("setup checkpoint hashes differ")
    hashes = record.get("staged_source_sha256_by_file")
    if not isinstance(hashes, dict) or not {"corrected_run.py", "v1_fixture.py", "gene_space_intersection.txt"} <= hashes.keys():
        raise ValueError("setup staged source hashes are incomplete")
    if hashes["gene_space_intersection.txt"] != SHARED_GENE_SHA256:
        raise ValueError("setup shared gene digest differs")
    freeze = summary.get("runtime_pip_freeze")
    if (not isinstance(freeze, list) or
            record.get("runtime_pip_freeze_sha256") != hashlib.sha256("\n".join(freeze).encode()).hexdigest()):
        raise ValueError("setup runtime package digest differs")
    batches = record.get("batch_checkpoint_metadata_by_file")
    if not isinstance(batches, dict) or len(batches) != len(summary.get("batches", [])):
        raise ValueError("batch checkpoint metadata incomplete")
    for batch in summary["batches"]:
        item = batches.get(f"batch_{batch['batch_idx']:02d}.json")
        if not isinstance(item, dict) or not isinstance(item.get("metadata"), dict):
            raise ValueError("batch checkpoint metadata missing")
        metadata = item["metadata"]
        if metadata.get("parquet_sha256") != batch["checkpoint_sha256"]:
            raise ValueError("batch checkpoint parquet digest differs")
        if metadata.get("config", {}).get("checkpoint_sha256_by_file") != CHECKPOINT_SHA256_BY_FILE:
            raise ValueError("batch checkpoint model digest differs")
