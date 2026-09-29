"""Validate and preserve one corrected Kaggle Geneformer result package.

Usage: uv run --no-project --with pandas --with pyarrow python \
  scripts/35_ingest_corrected_kaggle_zip.py --zip ARCHIVE --job dev_shared \
  --output-dir OUTPUT
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import zipfile
from pathlib import Path


REVISION = "04c2b2e84da7c0f385c3f9ad8f3ec24bab6650e5"
SHARED_GENE_SHA256 = "482f113c433ac76eb19940442e4f3b1a24ae73d387c4ec75ecb19b8116eea29b"
COHORTS = {
    "dev": {"prefix": "l2_dev", "n": 261, "cells": 1263676,
            "index": "donor_id", "n_field": "n_donors_embedded",
            "batch_n_field": "n_donors",
            "counts_field": "donor_cell_counts_expected", "missing": "missing_donors",
            "extra": "extra_donors"},
    "external": {"prefix": "l2_sealed", "n": 56, "cells": 363083,
                 "index": "gsm_id", "n_field": "n_samples_embedded",
                 "batch_n_field": "n_samples",
                 "counts_field": "sample_cell_counts_expected", "missing": "missing_samples",
                 "extra": "extra_samples"},
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_archive(path: Path, job: str) -> tuple[dict, dict[str, bytes]]:
    import numpy as np
    import pandas as pd

    cohort, mode = job.split("_", 1)
    require(cohort in COHORTS and mode in {"shared", "native"}, "unknown job")
    expected = COHORTS[cohort]
    stem = f"{expected['prefix']}_geneformer_v1_{mode}"
    embedding_name = f"{stem}_embeddings.parquet"
    summary_name = f"{stem}_run_summary.json"
    manifest_name = f"{job}_share_manifest.json"
    names = {embedding_name, summary_name, "fixture_summary.json", manifest_name}

    with zipfile.ZipFile(path) as archive:
        entries = archive.namelist()
        require(len(entries) == len(names) and set(entries) == names,
                "unexpected, missing, or duplicate ZIP members")
        require(all("/" not in name and "\\" not in name for name in entries),
                "ZIP member path is not a basename")
        require(archive.testzip() is None, "ZIP CRC check failed")
        payload = {name: archive.read(name) for name in names}

    manifest = json.loads(payload[manifest_name])
    require(manifest.get("job") == job and manifest.get("geneformer_revision") == REVISION,
            "manifest job or model revision differs")
    actual_hashes = {name: sha256(payload[name]) for name in names if name != manifest_name}
    require(manifest.get("files_sha256") == actual_hashes, "manifest member hashes differ")

    fixture = json.loads(payload["fixture_summary.json"])
    require(fixture.get("status") == "pass" and fixture.get("n_cells") == 8 and
            fixture.get("embedding_dim") == 256 and
            fixture.get("geneformer_revision") == REVISION and
            fixture.get("replay_after_embedding_passed") is True and
            fixture.get("tokenizer_num_proc") is None,
            "updated eight-cell fixture did not pass")

    summary = json.loads(payload[summary_name])
    require(summary.get("status") == "success" and summary.get("gene_input_mode") == mode,
            "run status or gene mode differs")
    require(summary.get("geneformer_revision") == REVISION and
            summary.get("model_version") == "V1" and
            summary.get("model_input_size") == 2048 and
            summary.get("emb_mode") == "cell" and
            summary.get("emb_layer") == -1 and
            summary.get("aggregation") == "mean_pool_per_donor" and
            summary.get("tokenizer_num_proc") is None,
            "Geneformer protocol differs")
    require(summary.get("intersection_sha256") ==
            (SHARED_GENE_SHA256 if mode == "shared" else None),
            "shared-gene protocol differs")
    require(summary.get(expected["n_field"]) == expected["n"] and
            summary.get("total_cells_expected") == expected["cells"] and
            summary.get("total_cells_processed") == expected["cells"],
            "cohort donor or cell counts differ")
    require(not summary.get(expected["missing"]) and not summary.get(expected["extra"]) and
            not summary.get("cell_count_mismatches"), "run summary reports missing or mismatched cells")
    require(summary.get("embedding_sha256") == actual_hashes[embedding_name],
            "embedding digest differs from run summary")

    counts = summary.get(expected["counts_field"])
    require(isinstance(counts, dict) and len(counts) == expected["n"] and
            all(isinstance(value, int) and value > 0 for value in counts.values()) and
            sum(counts.values()) == expected["cells"],
            "per-donor cell accounting differs")
    batches = summary.get("batches")
    require(isinstance(batches, list) and len(batches) > 0 and
            [batch.get("batch_idx") for batch in batches] == list(range(len(batches))) and
            sum(batch.get(expected["batch_n_field"], 0) for batch in batches) == expected["n"] and
            sum(batch.get("n_cells", 0) for batch in batches) == expected["cells"] and
            all(batch.get("tokenized") == batch.get("embedded") == batch.get("n_cells")
                for batch in batches), "batch tokenization or embedding counts differ")

    frame = pd.read_parquet(io.BytesIO(payload[embedding_name]))
    require(summary.get("embedding_dim") == 256 and
            frame.shape == (expected["n"], 256) and
            frame.index.name == expected["index"] and frame.index.is_unique and
            set(map(str, frame.index)) == set(counts),
            "embedding table donor keys, shape, or index differ")
    require(list(frame.columns) == [f"gf_dim_{i}" for i in range(frame.shape[1])],
            "embedding dimension columns differ")
    values = frame.to_numpy(dtype=float)
    require(np.isfinite(values).all() and (values.std(axis=0) > 0).all(),
            "embedding table contains nonfinite or constant dimensions")
    require(not frame.duplicated().any(), "embedding table contains duplicate vectors")
    norms = np.linalg.norm(values, axis=1)
    require(np.isfinite(norms).all() and (norms > 0).all(), "invalid embedding norms")

    report = {
        "status": "validated", "job": job,
        "source_zip_sha256": sha256(path.read_bytes()),
        "member_sha256": actual_hashes,
        "manifest_sha256": sha256(payload[manifest_name]),
        "n_donors_or_samples": expected["n"],
        "n_cells": expected["cells"],
        "embedding_shape": list(frame.shape),
        "embedding_index": frame.index.name,
        "embedding_norm_min": float(norms.min()),
        "embedding_norm_max": float(norms.max()),
        "batches": len(batches),
        "cells_restored_from_checkpoints": summary.get("cells_restored_from_checkpoints"),
        "model_revision": REVISION,
        "shared_gene_sha256": summary.get("intersection_sha256"),
    }
    require(all(math.isfinite(report[key]) for key in
                ("embedding_norm_min", "embedding_norm_max")), "invalid report statistic")
    return report, payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip", type=Path, required=True)
    parser.add_argument("--job", choices=[f"{cohort}_{mode}" for cohort in COHORTS
                                          for mode in ("shared", "native")], required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    report, payload = validate_archive(args.zip, args.job)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    targets = {args.zip.name: args.zip.read_bytes(), **payload}
    for name, data in targets.items():
        target = args.output_dir / name
        if target.exists():
            require(target.read_bytes() == data, f"existing artifact differs: {target}")
        else:
            target.write_bytes(data)
    (args.output_dir / "ingestion_validation.json").write_text(
        json.dumps(report, indent=2, allow_nan=False) + "\n",
    )
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
