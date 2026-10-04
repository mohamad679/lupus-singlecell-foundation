"""L2 full-scale Geneformer embedding extraction: all 261 dev-cohort donors.

Same model/config as the validated calibration run (kernel
mohamadasgari/l2-calibration-census-geneformer-throughput, v5, confirmed on
Tesla T4 x2, 135.17 cells/sec on a real 10,171-cell/3-donor sample):
Geneformer-V1-10M, model_input_size=2048, emb_mode="cls", forward_batch_size=32,
emb_layer=-1, transformers pinned >=4.35,<4.50.

Processes donors in cell-count-balanced batches (not one giant in-memory
matrix, and not 261 separate tiny calls) so that:
- memory stays bounded (no attempt to materialize the full ~1B-nonzero
  sparse matrix at once),
- per-batch fixed overhead (tokenizer/model setup) is amortized across many
  cells rather than paid 261 times,
- real per-batch throughput can be logged at ~12.5% (1/8) intervals, so the
  135.17 cells/sec calibration number is checked against reality as the run
  progresses rather than trusted blindly (the pseudobulk full run's real
  throughput was 23x the small-batch calibration number -- this run reports
  its own real number rather than assuming a similar multiplier applies).

After each batch's per-cell embeddings are produced, they are immediately
mean-pooled to one vector per donor (PREREG's locked mean_pool_per_donor
convention) and the per-cell embeddings are discarded -- only the donor-level
mean vector is retained in memory.

Writes:
- /kaggle/working/l2_dev_geneformer_embeddings.parquet (donor x embedding_dim)
- /kaggle/working/l2_dev_geneformer_run_summary.json (real wall-clock,
  per-batch throughput, integrity cross-check data)
"""

import json
import os
import shutil
import subprocess
import sys
import time
import traceback

DATASET_ID = "218acb0f-9f2f-4f76-b90b-15a4b7c7f629"
CENSUS_VERSION = "2025-11-08"
MODEL_SUBDIR = "Geneformer-V1-10M"
CALIBRATION_CELLS_PER_SEC = 135.16979626730776
N_BATCHES_TARGET = 8


def log(msg):
    print(f"[l2-geneformer-full] {msg}", flush=True)


def run(cmd):
    log(f"$ {cmd}")
    subprocess.run(cmd, shell=True, check=True)


log("installing dependencies")
run(f"{sys.executable} -m pip install -q cellxgene_census")
run(f"{sys.executable} -m pip install -q git+https://huggingface.co/ctheodoris/Geneformer.git")
run(f"{sys.executable} -m pip install -q huggingface_hub anndata")
run(f"{sys.executable} -m pip install -q 'transformers>=4.35,<4.50'")

import cellxgene_census  # noqa: E402
import tiledbsoma as soma  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from huggingface_hub import snapshot_download  # noqa: E402
from geneformer import TranscriptomeTokenizer, EmbExtractor  # noqa: E402

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
    model_dir = snapshot_download(repo_id="ctheodoris/Geneformer", allow_patterns=[f"{MODEL_SUBDIR}/*"])
    model_path = f"{model_dir}/{MODEL_SUBDIR}"

    WORK = "/kaggle/working/gf_batches"
    os.makedirs(WORK, exist_ok=True)

    cumulative_cells = 0
    for batch_idx, batch_donors in enumerate(batches):
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
        for d, c in counts_this_batch.items():
            donor_cell_counts_observed[d] = donor_cell_counts_observed.get(d, 0) + int(c)

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
        )
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
            emb_mode="cls",
            max_ncells=None,
            emb_layer=-1,
            emb_label=["cell_id", "donor_id"],
            forward_batch_size=32,
            nproc=2,
        )
        embs = embex.extract_embs(
            model_directory=model_path,
            input_data_file=f"{batch_dir}/tokenized/batch.dataset",
            output_directory=f"{batch_dir}/emb",
            output_prefix="batch_embs",
        )

        # mean_pool_per_donor: real math, mean over each donor's cell embeddings
        emb_cols = [c for c in embs.columns if c not in ("cell_id", "donor_id")]
        grouped = embs.groupby("donor_id")[emb_cols].mean()
        for donor_id, row in grouped.iterrows():
            donor_embeddings[donor_id] = row.to_numpy(dtype=np.float64)

        batch_seconds = time.time() - t_batch_start
        cumulative_cells += n_cells_batch
        cumulative_seconds = time.time() - t_run_start
        batch_rate = n_cells_batch / batch_seconds
        running_rate = cumulative_cells / cumulative_seconds
        pct_done = 100.0 * cumulative_cells / total_cells_expected

        log(f"batch {batch_idx} done: {len(batch_donors)} donors, {n_cells_batch} cells, "
            f"{batch_seconds:.1f}s, batch_rate={batch_rate:.2f} cells/sec "
            f"(calibration was {CALIBRATION_CELLS_PER_SEC:.2f}, ratio={batch_rate/CALIBRATION_CELLS_PER_SEC:.2f}x)")
        log(f"  progress: {pct_done:.1f}% done ({cumulative_cells}/{total_cells_expected} cells), "
            f"running_rate={running_rate:.2f} cells/sec, "
            f"projected_total_seconds={total_cells_expected/running_rate:.0f} "
            f"({total_cells_expected/running_rate/3600:.2f}h)")

        SUMMARY["batches"].append({
            "batch_idx": batch_idx,
            "n_donors": len(batch_donors),
            "n_cells": int(n_cells_batch),
            "batch_seconds": batch_seconds,
            "batch_cells_per_sec": batch_rate,
            "cumulative_cells": cumulative_cells,
            "cumulative_seconds": cumulative_seconds,
            "running_cells_per_sec": running_rate,
        })

        # clean up this batch's temp files before starting the next
        shutil.rmtree(batch_dir, ignore_errors=True)

    t_run_end = time.time()
    total_seconds = t_run_end - t_run_start
    overall_rate = cumulative_cells / total_seconds

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

    SUMMARY.update({
        "status": "success",
        "n_donors_expected": len(all_donors),
        "n_donors_embedded": len(donor_embeddings),
        "total_cells_expected": total_cells_expected,
        "total_cells_processed": cumulative_cells,
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
        "model_input_size": 2048,
        "emb_mode": "cls",
        "aggregation": "mean_pool_per_donor",
    })

    emb_df = pd.DataFrame.from_dict(donor_embeddings, orient="index")
    emb_df.index.name = "donor_id"
    emb_df.columns = [f"gf_dim_{i}" for i in range(emb_df.shape[1])]
    emb_df = emb_df.sort_index()
    emb_df.to_parquet("/kaggle/working/l2_dev_geneformer_embeddings.parquet", compression="zstd")
    log(f"wrote embeddings parquet: shape={emb_df.shape}")

except Exception:
    log("FAILED:")
    traceback.print_exc()
    SUMMARY["status"] = "failed"
    SUMMARY["error"] = traceback.format_exc()

with open("/kaggle/working/l2_dev_geneformer_run_summary.json", "w") as f:
    json.dump(SUMMARY, f, indent=2, default=str)

log("=== FINAL SUMMARY (JSON, batches omitted for brevity) ===")
print(json.dumps({k: v for k, v in SUMMARY.items() if k not in ("batches", "donor_cell_counts_expected")},
                  indent=2, default=str), flush=True)
