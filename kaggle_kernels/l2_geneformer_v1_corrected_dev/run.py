"""Versioned correction: V1 cell embeddings for all development donors.

This is a new analysis, never a recreation of the sealed first run. The
shared-gene input is primary; GENE_INPUT_MODE=native is a sensitivity run.

This configuration changes the historical tokenizer and extractor settings.
It pins a V1 source/checkpoint revision, uses V1 cell embeddings from the
penultimate layer, and verifies token/cell/donor integrity before pooling.

Processes donors in cell-count-balanced batches (not one giant in-memory
matrix, and not 261 separate tiny calls) so that:
- memory stays bounded (no attempt to materialize the full ~1B-nonzero
  sparse matrix at once),
- per-batch fixed overhead (tokenizer/model setup) is amortized across many
  cells rather than paid 261 times,
- real per-batch throughput can be logged at ~12.5% (1/8) intervals.

After each batch's per-cell embeddings are produced, they are immediately
mean-pooled to one vector per donor (PREREG's locked mean_pool_per_donor
convention) and the per-cell embeddings are discarded -- only the donor-level
mean vector is retained in memory.

Writes:
- /kaggle/working/l2_dev_geneformer_v1_<mode>_embeddings.parquet
- /kaggle/working/l2_dev_geneformer_v1_<mode>_run_summary.json (real wall-clock,
  per-batch throughput, integrity cross-check data)
"""

import json
import hashlib
import gc
import os
import shutil
import subprocess
import sys
import time
import traceback

DATASET_ID = "218acb0f-9f2f-4f76-b90b-15a4b7c7f629"
CENSUS_VERSION = "2025-11-08"
MODEL_SUBDIR = "Geneformer-V1-10M"
GENEFORMER_REVISION = "04c2b2e84da7c0f385c3f9ad8f3ec24bab6650e5"
GENE_INPUT_MODE = os.environ.get("GENE_INPUT_MODE", "shared")
BATCH_SIZE = int(os.environ.get("GENEFORMER_FORWARD_BATCH_SIZE", "32"))
SCRATCH = os.environ.get("GENEFORMER_SCRATCH_DIR", "/kaggle/temp")
CHECKPOINT_ROOT = os.environ.get(
    "GENEFORMER_CHECKPOINT_DIR",
    f"/kaggle/working/correction_checkpoints/dev_{GENE_INPUT_MODE}",
)
RESUME_ROOT = os.environ.get("GENEFORMER_RESUME_DIR", CHECKPOINT_ROOT)
INTERSECTION_PATH = os.environ.get("GENE_INTERSECTION_PATH", "/kaggle/input/lupus-correction/gene_space_intersection.txt")
INTERSECTION_SHA256 = "482f113c433ac76eb19940442e4f3b1a24ae73d387c4ec75ecb19b8116eea29b"
assert GENE_INPUT_MODE in {"shared", "native"}
assert BATCH_SIZE > 0
CALIBRATION_CELLS_PER_SEC = 135.16979626730776
N_BATCHES_TARGET = 8


def log(msg):
    print(f"[l2-geneformer-full] {msg}", flush=True)


def run(cmd):
    log(f"$ {cmd}")
    subprocess.run(cmd, shell=True, check=True)


if os.environ.get("GENEFORMER_SKIP_INSTALL") != "1":
    log("installing dependencies")
    run(f"{sys.executable} -m pip install -q cellxgene_census")
    run(f"{sys.executable} -m pip install -q git+https://huggingface.co/ctheodoris/Geneformer.git@{GENEFORMER_REVISION}")
    run(f"{sys.executable} -m pip install -q huggingface_hub anndata")
    run(f"{sys.executable} -m pip install -q 'transformers>=4.35,<4.50'")

import cellxgene_census  # noqa: E402
import tiledbsoma as soma  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from huggingface_hub import snapshot_download  # noqa: E402
from geneformer import TranscriptomeTokenizer, EmbExtractor  # noqa: E402
from datasets import load_from_disk  # noqa: E402


def shared_genes():
    if GENE_INPUT_MODE == "native":
        return None
    raw = open(INTERSECTION_PATH, "rb").read()
    if hashlib.sha256(raw).hexdigest() != INTERSECTION_SHA256:
        raise ValueError("shared-gene list checksum mismatch")
    genes = set(raw.decode().splitlines())
    if len(genes) != 30165:
        raise ValueError("shared-gene list is incomplete or contains duplicates")
    return genes


def model_hashes(model_path):
    hashes = {}
    for root, _, files in os.walk(model_path):
        for name in sorted(files):
            path = os.path.join(root, name)
            digest = hashlib.sha256()
            with open(path, "rb") as stream:
                for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
                    digest.update(chunk)
            hashes[os.path.relpath(path, model_path)] = digest.hexdigest()
    if not hashes:
        raise ValueError("checkpoint download is empty")
    return hashes


def file_sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_batch_checkpoint(batch_idx, donors, expected_counts, config):
    stem = f"batch_{batch_idx:02d}"
    metadata_path = os.path.join(RESUME_ROOT, stem + ".json")
    parquet_path = os.path.join(RESUME_ROOT, stem + ".parquet")
    if not (os.path.isfile(metadata_path) and os.path.isfile(parquet_path)):
        return None
    with open(metadata_path) as stream:
        metadata = json.load(stream)
    if metadata.get("config") != config or metadata.get("donors") != sorted(donors):
        raise ValueError(f"incompatible batch checkpoint: {metadata_path}")
    if metadata.get("cell_counts") != expected_counts:
        raise ValueError(f"cell counts changed since checkpoint: {metadata_path}")
    if file_sha256(parquet_path) != metadata.get("parquet_sha256"):
        raise ValueError(f"corrupted batch checkpoint: {parquet_path}")
    frame = pd.read_parquet(parquet_path)
    if frame.index.name != "donor_id" or sorted(frame.index.tolist()) != sorted(donors):
        raise ValueError(f"donor IDs changed in checkpoint: {parquet_path}")
    if not all(str(column).startswith("gf_dim_") for column in frame.columns):
        raise ValueError(f"invalid checkpoint embedding columns: {parquet_path}")
    if frame.shape[1] == 0 or not np.isfinite(frame.to_numpy(dtype=float)).all():
        raise ValueError(f"invalid checkpoint embeddings: {parquet_path}")
    if os.path.abspath(RESUME_ROOT) != os.path.abspath(CHECKPOINT_ROOT):
        os.makedirs(CHECKPOINT_ROOT, exist_ok=True)
        shutil.copy2(parquet_path, os.path.join(CHECKPOINT_ROOT, stem + ".parquet"))
        shutil.copy2(metadata_path, os.path.join(CHECKPOINT_ROOT, stem + ".json"))
    return frame, metadata


def save_batch_checkpoint(batch_idx, donors, expected_counts, grouped, config, audit):
    os.makedirs(CHECKPOINT_ROOT, exist_ok=True)
    stem = f"batch_{batch_idx:02d}"
    parquet_path = os.path.join(CHECKPOINT_ROOT, stem + ".parquet")
    metadata_path = os.path.join(CHECKPOINT_ROOT, stem + ".json")
    frame = grouped.sort_index().copy()
    frame.index.name = "donor_id"
    frame.columns = [f"gf_dim_{i}" for i in range(frame.shape[1])]
    tmp_parquet = parquet_path + ".tmp"
    frame.to_parquet(tmp_parquet, compression="zstd")
    os.replace(tmp_parquet, parquet_path)
    metadata = {"config": config, "donors": sorted(donors),
                "cell_counts": expected_counts, "batch_audit": audit,
                "embedding_dim": frame.shape[1],
                "parquet_sha256": file_sha256(parquet_path)}
    tmp_metadata = metadata_path + ".tmp"
    with open(tmp_metadata, "w") as stream:
        json.dump(metadata, stream, indent=2, sort_keys=True)
    os.replace(tmp_metadata, metadata_path)
    return metadata


def validate_tokenizer(tk):
    expected = {"ENSG00000000003": 2, "ENSG00000000005": 3,
                "ENSG00000141510": 8088, "ENSG00000139618": 7809}
    if tk.model_version != "V1" or tk.special_token or tk.model_input_size != 2048:
        raise ValueError("Geneformer V1 tokenizer settings are invalid")
    if any(tk.gene_token_dict.get(gene) != token for gene, token in expected.items()):
        raise ValueError("Geneformer V1 vocabulary mapping mismatch")
    if "<cls>" in tk.gene_token_dict or "<eos>" in tk.gene_token_dict:
        raise ValueError("V1 vocabulary unexpectedly contains special tokens")


def validate_batch(dataset_path, embs, expected_counts, vocab_size):
    tokenized = load_from_disk(dataset_path)
    if len(tokenized) != sum(expected_counts.values()) or len(embs) != len(tokenized):
        raise ValueError("cells were lost during tokenization or embedding")
    lengths = [len(ids) for ids in tokenized["input_ids"]]
    if not lengths or min(lengths) < 1 or max(lengths) > 2048:
        raise ValueError("empty or overlong token sequence")
    if any(token < 0 or token >= vocab_size for ids in tokenized["input_ids"] for token in ids):
        raise ValueError("token outside V1 vocabulary")
    if embs["cell_id"].duplicated().any() or embs["cell_id"].isna().any():
        raise ValueError("missing or duplicate embedded cell ID")
    if set(embs["cell_id"]) != set(tokenized["cell_id"]):
        raise ValueError("embedded cell IDs differ from tokenized cells")
    counts = embs["donor_id"].value_counts().to_dict()
    if counts != expected_counts:
        raise ValueError(f"embedded donor counts differ: {counts}")
    values = embs.drop(columns=["cell_id", "donor_id"]).to_numpy(dtype=float)
    if values.shape[1] == 0 or not np.isfinite(values).all():
        raise ValueError("invalid cell embeddings")
    return {"tokenized": len(tokenized), "embedded": len(embs),
            "min_sequence_length": min(lengths), "max_sequence_length": max(lengths)}

SUMMARY = {"batches": [], "status": "in_progress"}
donor_embeddings: dict[str, np.ndarray] = {}
donor_cell_counts_observed: dict[str, int] = {}

try:
    t_run_start = time.time()

    # --- fetch full donor list + real cell counts (cheap, obs-only) ---
    census = cellxgene_census.open_soma(census_version=CENSUS_VERSION)
    obs_df = cellxgene_census.get_obs(
        census, "homo_sapiens",
        value_filter=f"dataset_id == '{DATASET_ID}'",
        column_names=["donor_id"],
    )
    census.close()
    # Root-cause fix (not just a downstream filter): donor_id is a pandas
    # Categorical whose dtype carries the full census-wide category list
    # (confirmed: 11,633 categories at the dtype level, only 261 actually
    # observed in this dataset -- same bug class as the pseudobulk run's
    # earlier finding). remove_unused_categories() drops the ~11,372
    # zero-count categories from OTHER census datasets at the column level,
    # before donor_id is used for anything -- so every downstream use
    # (value_counts, batch assignment, the IN-list built for streaming
    # queries) operates on a clean 261-category column instead of relying on
    # a value>0 filter applied after the fact.
    obs_df["donor_id"] = obs_df["donor_id"].cat.remove_unused_categories()
    assert len(obs_df["donor_id"].cat.categories) == obs_df["donor_id"].nunique(), (
        "donor_id still has unused categories after remove_unused_categories(); "
        "the Categorical-artifact bug is not actually fixed."
    )
    donor_cell_counts_full = obs_df["donor_id"].value_counts().to_dict()
    all_donors = sorted(donor_cell_counts_full.keys())
    total_cells_expected = int(obs_df.shape[0])
    input_genes = shared_genes()
    log(f"donors: {len(all_donors)}, total cells: {total_cells_expected}")

    # --- greedy balanced batching by cell count ---
    target_per_batch = total_cells_expected / N_BATCHES_TARGET
    donors_by_count_desc = sorted(all_donors, key=lambda d: -donor_cell_counts_full[d])
    batches: list[list[str]] = [[] for _ in range(N_BATCHES_TARGET)]
    batch_loads = [0] * N_BATCHES_TARGET
    for d in donors_by_count_desc:
        i = batch_loads.index(min(batch_loads))
        batches[i].append(d)
        batch_loads[i] += donor_cell_counts_full[d]
    batches = [b for b in batches if b]  # drop any empty batch
    for i, b in enumerate(batches):
        log(f"batch {i}: {len(b)} donors, {sum(donor_cell_counts_full[d] for d in b)} cells")

    # --- model download (once) ---
    log(f"downloading {MODEL_SUBDIR} pretrained model")
    model_dir = snapshot_download(repo_id="ctheodoris/Geneformer", revision=GENEFORMER_REVISION,
                                  allow_patterns=[f"{MODEL_SUBDIR}/*"])
    model_path = f"{model_dir}/{MODEL_SUBDIR}"
    checkpoint_hashes = model_hashes(model_path)

    WORK = f"{SCRATCH}/gf_batches_{GENE_INPUT_MODE}"
    os.makedirs(WORK, exist_ok=True)
    checkpoint_config = {
        "cohort": "development", "dataset_id": DATASET_ID,
        "census_version": CENSUS_VERSION, "gene_input_mode": GENE_INPUT_MODE,
        "intersection_sha256": INTERSECTION_SHA256 if input_genes is not None else None,
        "geneformer_revision": GENEFORMER_REVISION,
        "extraction_script_sha256": file_sha256(__file__),
        "checkpoint_sha256_by_file": checkpoint_hashes,
        "model_version": "V1", "emb_mode": "cell", "emb_layer": -1,
        "aggregation": "mean_pool_per_donor",
    }

    cumulative_cells = 0
    resumed_cells = 0
    for batch_idx, batch_donors in enumerate(batches):
        expected_counts = {d: int(donor_cell_counts_full[d]) for d in batch_donors}
        prior = load_batch_checkpoint(batch_idx, batch_donors, expected_counts,
                                      checkpoint_config)
        if prior is not None:
            frame, metadata = prior
            for donor_id, row in frame.iterrows():
                donor_embeddings[donor_id] = row.to_numpy(dtype=np.float64)
                donor_cell_counts_observed[donor_id] = expected_counts[donor_id]
            batch_cells = sum(expected_counts.values())
            cumulative_cells += batch_cells
            resumed_cells += batch_cells
            SUMMARY["batches"].append({"batch_idx": batch_idx, "resumed": True,
                                       "n_donors": len(batch_donors), "n_cells": batch_cells,
                                       "checkpoint_sha256": metadata["parquet_sha256"],
                                       **metadata["batch_audit"]})
            log(f"batch {batch_idx}: restored {batch_cells} cells from verified checkpoint")
            continue
        t_batch_start = time.time()
        batch_dir = f"{WORK}/batch_{batch_idx}"
        os.makedirs(f"{batch_dir}/input", exist_ok=True)
        os.makedirs(f"{batch_dir}/tokenized", exist_ok=True)
        os.makedirs(f"{batch_dir}/emb", exist_ok=True)

        census = cellxgene_census.open_soma(census_version=CENSUS_VERSION)
        exp = census["census_data"]["homo_sapiens"]
        donor_list_str = ",".join(f"'{d}'" for d in batch_donors)
        with exp.axis_query(
            measurement_name="RNA",
            obs_query=soma.AxisQuery(
                value_filter=f"dataset_id == '{DATASET_ID}' and donor_id in [{donor_list_str}]"
            ),
        ) as q:
            adata = q.to_anndata(X_name="raw")
        census.close()

        n_cells_batch = adata.n_obs
        # Same root-cause fix as above: adata.obs["donor_id"] inherits the
        # full census-wide Categorical dtype from the source query, so it
        # needs the same remove_unused_categories() treatment before
        # value_counts(), not just a >0 filter on the result.
        if hasattr(adata.obs["donor_id"], "cat"):
            adata.obs["donor_id"] = adata.obs["donor_id"].cat.remove_unused_categories()
        counts_this_batch = adata.obs["donor_id"].value_counts().to_dict()
        if set(counts_this_batch) != set(batch_donors):
            raise ValueError("batch donor IDs do not match requested donors")
        if {d: int(c) for d, c in counts_this_batch.items()} != expected_counts:
            raise ValueError("development batch cell counts changed before embedding")
        for d, c in counts_this_batch.items():
            donor_cell_counts_observed[d] = donor_cell_counts_observed.get(d, 0) + int(c)

        if input_genes is not None:
            feature_ids = adata.var["feature_id"].astype(str)
            if set(feature_ids) & input_genes != input_genes:
                raise ValueError("development matrix lacks shared genes")
            adata = adata[:, feature_ids.isin(input_genes)].copy()
        adata.var["ensembl_id"] = adata.var["feature_id"].values
        adata.obs["n_counts"] = np.asarray(adata.X.sum(axis=1)).ravel()
        adata.obs["cell_id"] = [f"b{batch_idx}_{i}" for i in range(adata.n_obs)]
        # donor_id already present in adata.obs from census

        adata.write_h5ad(f"{batch_dir}/input/batch.h5ad")
        del adata

        tk = TranscriptomeTokenizer(
            custom_attr_name_dict={"cell_id": "cell_id", "donor_id": "donor_id"},
            nproc=2,
            model_input_size=2048,
            model_version="V1",
        )
        validate_tokenizer(tk)
        tk.tokenize_data(
            data_directory=f"{batch_dir}/input",
            output_directory=f"{batch_dir}/tokenized",
            output_prefix="batch",
            file_format="h5ad",
        )

        # emb_label is required to get cell_id/donor_id attached to the output
        # embeddings dataframe. Without it, extract_embs() returns a bare
        # embedding-dims-only dataframe with no way to map rows back to
        # donors -- confirmed by inspecting the v5 calibration output, which
        # was run without emb_label and produced exactly that. label_cell_embs
        # (geneformer's emb_extractor.py) pulls these labels directly from
        # the same (internally length-sorted) dataset object used to compute
        # embeddings, so this is safe regardless of any internal reordering.
        embex = EmbExtractor(
            model_type="Pretrained",
            emb_mode="cell",
            model_version="V1",
            max_ncells=None,
            emb_layer=-1,
            emb_label=["cell_id", "donor_id"],
            forward_batch_size=BATCH_SIZE,
            nproc=2,
        )
        embs = embex.extract_embs(
            model_directory=model_path,
            input_data_file=f"{batch_dir}/tokenized/batch.dataset",
            output_directory=f"{batch_dir}/emb",
            output_prefix="batch_embs",
        )
        batch_audit = validate_batch(f"{batch_dir}/tokenized/batch.dataset", embs,
                                     {d: int(c) for d, c in counts_this_batch.items()},
                                     len(tk.gene_token_dict))

        # mean_pool_per_donor: real math, mean over each donor's cell embeddings
        emb_cols = [c for c in embs.columns if c not in ("cell_id", "donor_id")]
        grouped = embs.groupby("donor_id")[emb_cols].mean()
        for donor_id, row in grouped.iterrows():
            donor_embeddings[donor_id] = row.to_numpy(dtype=np.float64)
        checkpoint = save_batch_checkpoint(batch_idx, batch_donors, expected_counts,
                                           grouped, checkpoint_config, batch_audit)

        batch_seconds = time.time() - t_batch_start
        cumulative_cells += n_cells_batch
        cumulative_seconds = time.time() - t_run_start
        batch_rate = n_cells_batch / batch_seconds
        running_rate = (cumulative_cells - resumed_cells) / cumulative_seconds
        pct_done = 100.0 * cumulative_cells / total_cells_expected

        log(f"batch {batch_idx} done: {len(batch_donors)} donors, {n_cells_batch} cells, "
            f"{batch_seconds:.1f}s, batch_rate={batch_rate:.2f} cells/sec "
            f"(calibration was {CALIBRATION_CELLS_PER_SEC:.2f}, ratio={batch_rate/CALIBRATION_CELLS_PER_SEC:.2f}x)")
        log(f"  progress: {pct_done:.1f}% done ({cumulative_cells}/{total_cells_expected} cells), "
            f"running_rate={running_rate:.2f} cells/sec, "
            f"projected_remaining_seconds={(total_cells_expected-cumulative_cells)/running_rate:.0f} "
            f"({(total_cells_expected-cumulative_cells)/running_rate/3600:.2f}h)")

        SUMMARY["batches"].append({
            "batch_idx": batch_idx,
            "n_donors": len(batch_donors),
            "n_cells": int(n_cells_batch),
            "batch_seconds": batch_seconds,
            "batch_cells_per_sec": batch_rate,
            "cumulative_cells": cumulative_cells,
            "cumulative_seconds": cumulative_seconds,
            "running_cells_per_sec": running_rate,
            "checkpoint_sha256": checkpoint["parquet_sha256"],
            "resumed": False,
            **batch_audit,
        })

        # clean up this batch's temp files before starting the next
        shutil.rmtree(batch_dir, ignore_errors=True)
        del embs, grouped, tk, embex
        gc.collect()

    t_run_end = time.time()
    total_seconds = t_run_end - t_run_start
    overall_rate = (cumulative_cells - resumed_cells) / total_seconds

    log(f"ALL BATCHES DONE: {len(donor_embeddings)} donors, {cumulative_cells} cells, "
        f"{total_seconds:.1f}s, overall_rate={overall_rate:.2f} cells/sec "
        f"(calibration was {CALIBRATION_CELLS_PER_SEC:.2f}, ratio={overall_rate/CALIBRATION_CELLS_PER_SEC:.2f}x)")

    # --- integrity cross-check ---
    missing_donors = set(all_donors) - set(donor_embeddings.keys())
    extra_donors = set(donor_embeddings.keys()) - set(all_donors)
    cell_count_mismatches = {
        d: {"expected": donor_cell_counts_full[d], "observed": donor_cell_counts_observed.get(d, 0)}
        for d in all_donors
        if donor_cell_counts_full[d] != donor_cell_counts_observed.get(d, 0)
    }
    if missing_donors or extra_donors or cell_count_mismatches or cumulative_cells != total_cells_expected:
        raise ValueError("development donor/cell integrity check failed")

    SUMMARY.update({
        "status": "success",
        "n_donors_expected": len(all_donors),
        "n_donors_embedded": len(donor_embeddings),
        "total_cells_expected": total_cells_expected,
        "total_cells_processed": cumulative_cells,
        "cells_restored_from_checkpoints": resumed_cells,
        "new_cells_processed": cumulative_cells - resumed_cells,
        "total_seconds": total_seconds,
        "overall_cells_per_sec": overall_rate,
        "calibration_cells_per_sec": CALIBRATION_CELLS_PER_SEC,
        "throughput_ratio_vs_calibration": overall_rate / CALIBRATION_CELLS_PER_SEC,
        "missing_donors": sorted(missing_donors),
        "extra_donors": sorted(extra_donors),
        "cell_count_mismatches": cell_count_mismatches,
        "donor_cell_counts_expected": donor_cell_counts_full,
        "embedding_dim": int(next(iter(donor_embeddings.values())).shape[0]) if donor_embeddings else None,
        "model": MODEL_SUBDIR,
        "geneformer_revision": GENEFORMER_REVISION,
        "checkpoint_sha256_by_file": checkpoint_hashes,
        "runtime_pip_freeze": subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True).splitlines(),
        "gene_input_mode": GENE_INPUT_MODE,
        "intersection_sha256": INTERSECTION_SHA256 if input_genes is not None else None,
        "model_input_size": 2048,
        "emb_mode": "cell",
        "model_version": "V1",
        "emb_layer": -1,
        "forward_batch_size": BATCH_SIZE,
        "aggregation": "mean_pool_per_donor",
    })

    emb_df = pd.DataFrame.from_dict(donor_embeddings, orient="index")
    emb_df.index.name = "donor_id"
    emb_df.columns = [f"gf_dim_{i}" for i in range(emb_df.shape[1])]
    emb_df = emb_df.sort_index()
    embedding_path = f"/kaggle/working/l2_dev_geneformer_v1_{GENE_INPUT_MODE}_embeddings.parquet"
    emb_df.to_parquet(embedding_path, compression="zstd")
    SUMMARY["embedding_sha256"] = file_sha256(embedding_path)
    log(f"wrote embeddings parquet: shape={emb_df.shape}")

except Exception:
    log("FAILED:")
    traceback.print_exc()
    SUMMARY["status"] = "failed"
    SUMMARY["error"] = traceback.format_exc()

with open(f"/kaggle/working/l2_dev_geneformer_v1_{GENE_INPUT_MODE}_run_summary.json", "w") as f:
    json.dump(SUMMARY, f, indent=2, default=str)

log("=== FINAL SUMMARY (JSON, batches omitted for brevity) ===")
print(json.dumps({k: v for k, v in SUMMARY.items() if k not in ("batches", "donor_cell_counts_expected")},
                  indent=2, default=str), flush=True)
if SUMMARY["status"] != "success":
    raise SystemExit(1)
