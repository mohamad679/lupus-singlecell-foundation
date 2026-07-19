"""L2 calibration kernel: census X-streaming benchmark + Geneformer throughput.

Scope, deliberately bounded per human instruction (2026-07-19):
  - Part A: benchmark cellxgene_census X-streaming, per-donor loop vs one
    batched/chunked query, on a small donor subset (not the full 261).
  - Part B: run real Geneformer embedding extraction on a real 2,000-5,000
    cell sample (2-3 donors), measure wall-clock cells/sec.
  - Does NOT run the full 261-donor pseudobulk extraction.
  - Does NOT run full-cohort (1.26M cell) Geneformer embedding.
  - Does NOT touch GSE135779 (sealed cohort) in any way.

Prints clearly-labeled results for both parts so they can be read off the
Kaggle kernel log and reported back verbatim, not re-derived or rounded.
"""

import json
import subprocess
import sys
import time
import traceback

DATASET_ID = "218acb0f-9f2f-4f76-b90b-15a4b7c7f629"  # Perez et al. 2022
CENSUS_VERSION = "2025-11-08"

RESULTS = {}


def log(msg):
    print(f"[l2-calib] {msg}", flush=True)


def run(cmd):
    log(f"$ {cmd}")
    subprocess.run(cmd, shell=True, check=True)


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
log("installing cellxgene_census")
run(f"{sys.executable} -m pip install -q cellxgene_census")

import cellxgene_census  # noqa: E402
import tiledbsoma as soma  # noqa: E402
import numpy as np  # noqa: E402

# ---------------------------------------------------------------------------
# Part A: X-streaming benchmark, per-donor loop vs one batched query
# ---------------------------------------------------------------------------
log("=== PART A: census X-streaming benchmark ===")

# Already produced real results in kernel version 1 (per-donor 64.4 cells/sec,
# batched 278.5 cells/sec on the same 5-donor/17,986-cell set). Skipping the
# re-run on this version to save GPU quota; Part B (which failed in v1) is
# the only thing this version needs to re-verify.
SKIP_PART_A = True

# Small, fixed donor subset for a fair, cheap comparison. Chosen arbitrarily
# from the dev-cohort donor_id list (not cherry-picked for size).
BENCHMARK_DONORS = ["HC-546", "HC-540", "HC-520", "HC-519", "HC-501"]


def run_part_a():
    census = cellxgene_census.open_soma(census_version=CENSUS_VERSION)
    exp = census["census_data"]["homo_sapiens"]

    # --- per-donor loop: one axis_query per donor ---
    t0 = time.time()
    per_donor_cells = 0
    for donor in BENCHMARK_DONORS:
        with exp.axis_query(
            measurement_name="RNA",
            obs_query=soma.AxisQuery(
                value_filter=f"dataset_id == '{DATASET_ID}' and donor_id == '{donor}'"
            ),
        ) as q:
            for tbl in q.X("raw").tables():
                pass
            per_donor_cells += q.n_obs
    per_donor_seconds = time.time() - t0
    log(f"per-donor loop: {len(BENCHMARK_DONORS)} donors, {per_donor_cells} cells, "
        f"{per_donor_seconds:.2f}s, {per_donor_cells / per_donor_seconds:.3f} cells/sec")
    RESULTS["per_donor_loop"] = {
        "donors": BENCHMARK_DONORS,
        "n_cells": per_donor_cells,
        "seconds": per_donor_seconds,
        "cells_per_sec": per_donor_cells / per_donor_seconds,
    }

    # --- one batched query across the same donors ---
    donor_list = ",".join(f"'{d}'" for d in BENCHMARK_DONORS)
    t0 = time.time()
    with exp.axis_query(
        measurement_name="RNA",
        obs_query=soma.AxisQuery(
            value_filter=f"dataset_id == '{DATASET_ID}' and donor_id in [{donor_list}]"
        ),
    ) as q:
        batched_cells = q.n_obs
        for tbl in q.X("raw").tables():
            pass
    batched_seconds = time.time() - t0
    log(f"batched query: {len(BENCHMARK_DONORS)} donors, {batched_cells} cells, "
        f"{batched_seconds:.2f}s, {batched_cells / batched_seconds:.3f} cells/sec")
    RESULTS["batched_query"] = {
        "donors": BENCHMARK_DONORS,
        "n_cells": batched_cells,
        "seconds": batched_seconds,
        "cells_per_sec": batched_cells / batched_seconds,
    }

    census.close()


if SKIP_PART_A:
    log("SKIP_PART_A=True; reusing kernel-v1 results, see report.")
    RESULTS["per_donor_loop"] = {
        "donors": BENCHMARK_DONORS, "n_cells": 17986,
        "seconds": 279.2034342288971, "cells_per_sec": 64.41897840430818,
        "source": "kernel_v1_rerun_skipped",
    }
    RESULTS["batched_query"] = {
        "donors": BENCHMARK_DONORS, "n_cells": 17986,
        "seconds": 64.57118272781372, "cells_per_sec": 278.54530829667794,
        "source": "kernel_v1_rerun_skipped",
    }
else:
    try:
        run_part_a()
    except Exception:
        log("PART A FAILED:")
        traceback.print_exc()
        RESULTS["part_a_error"] = traceback.format_exc()

# ---------------------------------------------------------------------------
# Part B: Geneformer calibration on a real 2,000-5,000 cell sample
# ---------------------------------------------------------------------------
log("=== PART B: Geneformer calibration ===")

try:
    log("installing geneformer + huggingface_hub")
    run(f"{sys.executable} -m pip install -q git+https://huggingface.co/ctheodoris/Geneformer.git")
    run(f"{sys.executable} -m pip install -q huggingface_hub anndata")
    # Kaggle's preinstalled transformers is incompatible with Geneformer's
    # eager import of SpecialTokensMixin (v1 run, 2026-07-19, failed with
    # ImportError). Pin to a known-compatible range and retry.
    run(f"{sys.executable} -m pip install -q 'transformers>=4.35,<4.50'")

    import anndata as ad  # noqa: E402
    import pandas as pd  # noqa: E402
    from huggingface_hub import snapshot_download  # noqa: E402
    from geneformer import TranscriptomeTokenizer, EmbExtractor  # noqa: E402

    # --- pull a real ~2,000-5,000 cell sample via census (2-3 donors) ---
    CALIB_DONORS = ["HC-546", "HC-540", "HC-520"]
    census = cellxgene_census.open_soma(census_version=CENSUS_VERSION)
    exp = census["census_data"]["homo_sapiens"]
    donor_list = ",".join(f"'{d}'" for d in CALIB_DONORS)
    with exp.axis_query(
        measurement_name="RNA",
        obs_query=soma.AxisQuery(
            value_filter=f"dataset_id == '{DATASET_ID}' and donor_id in [{donor_list}]"
        ),
    ) as q:
        adata = q.to_anndata(X_name="raw")
    census.close()

    log(f"calibration sample: {adata.n_obs} cells x {adata.n_vars} genes from donors {CALIB_DONORS}")
    RESULTS["geneformer_sample_n_cells"] = int(adata.n_obs)

    # Geneformer's tokenizer expects var['ensembl_id'] and obs['n_counts'].
    adata.var["ensembl_id"] = adata.var["feature_id"].values
    adata.obs["n_counts"] = np.asarray(adata.X.sum(axis=1)).ravel()
    adata.obs["cell_id"] = adata.obs.index.astype(str)

    import os
    os.makedirs("/kaggle/working/calib_input", exist_ok=True)
    os.makedirs("/kaggle/working/calib_tokenized", exist_ok=True)
    os.makedirs("/kaggle/working/calib_emb", exist_ok=True)
    adata.write_h5ad("/kaggle/working/calib_input/calib_sample.h5ad")

    # v2 run (2026-07-19) found the repo restructured: 'gf-6L-30M-i2048'
    # no longer exists. Verified via the HF Hub API that the current repo
    # top-level dirs are Geneformer-V1-10M, Geneformer-V2-104M,
    # Geneformer-V2-104M_CLcancer, Geneformer-V2-316M. Using the smallest
    # (V1-10M) for calibration speed.
    MODEL_SUBDIR = "Geneformer-V1-10M"
    log(f"downloading {MODEL_SUBDIR} pretrained model")
    model_dir = snapshot_download(
        repo_id="ctheodoris/Geneformer",
        allow_patterns=[f"{MODEL_SUBDIR}/*"],
    )
    model_path = f"{model_dir}/{MODEL_SUBDIR}"
    log(f"model_path={model_path}")

    t0 = time.time()
    # v3 run (2026-07-19) failed with a RuntimeError: some cells tokenized to
    # 2,951 tokens, exceeding Geneformer-V1-10M's 2,048-token position-
    # embedding limit. model_input_size truncates each cell's rank-ordered
    # token sequence to the model's supported max.
    tk = TranscriptomeTokenizer(
        custom_attr_name_dict={"cell_id": "cell_id"},
        nproc=2,
        model_input_size=2048,
    )
    tk.tokenize_data(
        data_directory="/kaggle/working/calib_input",
        output_directory="/kaggle/working/calib_tokenized",
        output_prefix="calib",
        file_format="h5ad",
    )
    tokenize_seconds = time.time() - t0
    log(f"tokenization: {tokenize_seconds:.2f}s")

    t0 = time.time()
    embex = EmbExtractor(
        model_type="Pretrained",
        emb_mode="cls",
        max_ncells=None,
        emb_layer=-1,
        forward_batch_size=32,
        nproc=2,
    )
    embs = embex.extract_embs(
        model_directory=model_path,
        input_data_file="/kaggle/working/calib_tokenized/calib.dataset",
        output_directory="/kaggle/working/calib_emb",
        output_prefix="calib_embs",
    )
    embed_seconds = time.time() - t0
    n_embedded = len(embs)
    cells_per_sec = n_embedded / embed_seconds

    log(f"embedding extraction: {n_embedded} cells, {embed_seconds:.2f}s, "
        f"{cells_per_sec:.3f} cells/sec")

    RESULTS["geneformer_embed_seconds"] = embed_seconds
    RESULTS["geneformer_n_cells_embedded"] = n_embedded
    RESULTS["geneformer_cells_per_sec"] = cells_per_sec
    RESULTS["geneformer_tokenize_seconds"] = tokenize_seconds

    full_cohort_cells = 1_263_676
    RESULTS["geneformer_full_cohort_eta_hours"] = (
        full_cohort_cells / cells_per_sec / 3600.0 if cells_per_sec > 0 else None
    )

except Exception:
    log("PART B FAILED:")
    traceback.print_exc()
    RESULTS["part_b_error"] = traceback.format_exc()

# ---------------------------------------------------------------------------
log("=== FINAL RESULTS (JSON) ===")
print(json.dumps(RESULTS, indent=2, default=str), flush=True)
