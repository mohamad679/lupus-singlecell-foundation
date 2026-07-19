"""L2 full-scale pseudobulk extraction: all 261 dev-cohort donors.

CPU-only (no GPU/Geneformer code in this kernel, per explicit instruction).
Real math, same vectorized aggregation as scripts/14_l2_census_pipeline.py's
stream_donor_pseudobulk() (mirrored here since Kaggle kernels don't have
repo access): sum raw counts per donor per gene -> CPM-normalize -> log1p,
per PREREG.md Section 3, arm 2. Uses one batched axis_query across all 261
donors (not a per-donor loop), per the confirmed-faster pattern from the
prior calibration session.

Writes:
- /kaggle/working/l2_dev_pseudobulk_counts.csv (donor x gene, CPM+log1p)
- /kaggle/working/l2_dev_pseudobulk_run_summary.json (timing, integrity checks)
"""

import json
import subprocess
import sys
import time
import traceback

DATASET_ID = "218acb0f-9f2f-4f76-b90b-15a4b7c7f629"  # Perez et al. 2022
CENSUS_VERSION = "2025-11-08"


def log(msg):
    print(f"[l2-pseudobulk] {msg}", flush=True)


def run(cmd):
    log(f"$ {cmd}")
    subprocess.run(cmd, shell=True, check=True)


log("installing cellxgene_census")
run(f"{sys.executable} -m pip install -q cellxgene_census")

import cellxgene_census  # noqa: E402
import tiledbsoma as soma  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SUMMARY = {}

try:
    t_start = time.time()
    census = cellxgene_census.open_soma(census_version=CENSUS_VERSION)
    exp = census["census_data"]["homo_sapiens"]
    value_filter = f"dataset_id == '{DATASET_ID}'"

    with exp.axis_query(
        measurement_name="RNA",
        obs_query=soma.AxisQuery(value_filter=value_filter),
    ) as query:
        n_genes = query.n_vars
        n_obs_total = query.n_obs
        log(f"query scope: {n_obs_total} cells x {n_genes} genes (all donors, one batched query)")

        var_joinids = np.asarray(query.var_joinids())  # PyArrow Int64Array, not numpy
        var_col_of_joinid = np.full(int(var_joinids.max()) + 1, -1, dtype=np.int64)
        var_col_of_joinid[var_joinids] = np.arange(len(var_joinids))

        # gene column names for the output CSV header, in the same dense order
        var_table = query.var(column_names=["soma_joinid", "feature_id"]).concat().to_pandas()
        joinid_to_feature_id = dict(zip(var_table["soma_joinid"], var_table["feature_id"]))
        gene_names = [joinid_to_feature_id[j] for j in var_joinids]

        obs_table = query.obs(column_names=["soma_joinid", "donor_id"]).concat().to_pandas()
        donor_ids_sorted = sorted(obs_table["donor_id"].unique().tolist())
        donor_row_of_id = {d: i for i, d in enumerate(donor_ids_sorted)}
        obs_joinids = obs_table["soma_joinid"].to_numpy()
        donor_row_of_joinid = np.full(int(obs_joinids.max()) + 1, -1, dtype=np.int64)
        donor_row_of_joinid[obs_joinids] = obs_table["donor_id"].map(donor_row_of_id).to_numpy()

        # real per-donor cell counts from this query, for an integrity check
        # against results/l2_dev_donor_metadata.csv produced in the prior
        # metadata-only session.
        real_cell_counts = obs_table["donor_id"].value_counts().to_dict()

        log(f"donors in query: {len(donor_ids_sorted)}")

        gene_sums = np.zeros((len(donor_ids_sorted), n_genes), dtype=np.float64)
        n_chunks = 0
        n_nonzero_processed = 0
        t_stream_start = time.time()
        for x_tbl in query.X("raw").tables():
            soma_dim_0 = x_tbl["soma_dim_0"].to_numpy()
            soma_dim_1 = x_tbl["soma_dim_1"].to_numpy()
            values = x_tbl["soma_data"].to_numpy()
            donor_rows = donor_row_of_joinid[soma_dim_0]
            gene_cols = var_col_of_joinid[soma_dim_1]
            np.add.at(gene_sums, (donor_rows, gene_cols), values)
            n_chunks += 1
            n_nonzero_processed += len(values)
            if n_chunks % 20 == 0:
                elapsed = time.time() - t_stream_start
                log(f"chunk {n_chunks}: {n_nonzero_processed} nonzero entries processed, "
                    f"{elapsed:.1f}s elapsed")

        t_stream_end = time.time()

    census.close()
    t_end = time.time()

    stream_seconds = t_stream_end - t_stream_start
    total_seconds = t_end - t_start
    cells_per_sec = n_obs_total / stream_seconds if stream_seconds > 0 else None

    log(f"streaming+aggregation: {stream_seconds:.1f}s for {n_obs_total} cells "
        f"({cells_per_sec:.2f} cells/sec)")
    log(f"total wall clock (incl. setup): {total_seconds:.1f}s")

    SUMMARY["n_donors"] = len(donor_ids_sorted)
    SUMMARY["n_cells_total"] = int(n_obs_total)
    SUMMARY["n_genes"] = int(n_genes)
    SUMMARY["n_chunks"] = n_chunks
    SUMMARY["n_nonzero_entries"] = int(n_nonzero_processed)
    SUMMARY["stream_seconds"] = stream_seconds
    SUMMARY["total_seconds"] = total_seconds
    SUMMARY["cells_per_sec"] = cells_per_sec
    SUMMARY["calibration_batched_cells_per_sec"] = 278.54530829667794
    SUMMARY["throughput_ratio_vs_calibration"] = (
        cells_per_sec / 278.54530829667794 if cells_per_sec else None
    )
    SUMMARY["real_cell_counts_per_donor"] = real_cell_counts

    # CPM-normalize + log1p, per PREREG Section 3 arm 2 (real math, unit-tested
    # separately in scripts/14_l2_census_pipeline.py::compute_donor_pseudobulk_from_counts)
    totals = gene_sums.sum(axis=1, keepdims=True)
    zero_total_donors = [donor_ids_sorted[i] for i in np.where(totals.ravel() <= 0)[0]]
    if zero_total_donors:
        raise RuntimeError(f"donors with zero total counts, cannot CPM-normalize: {zero_total_donors}")
    cpm = gene_sums / totals * 1_000_000.0
    log1p_cpm = np.log1p(cpm)

    df = pd.DataFrame(log1p_cpm, index=donor_ids_sorted, columns=gene_names)
    df.index.name = "donor_id"
    out_path = "/kaggle/working/l2_dev_pseudobulk_counts.csv"
    df.to_csv(out_path)
    log(f"wrote {out_path}: shape={df.shape}")
    SUMMARY["output_shape"] = list(df.shape)
    SUMMARY["status"] = "success"

except Exception:
    log("FAILED:")
    traceback.print_exc()
    SUMMARY["status"] = "failed"
    SUMMARY["error"] = traceback.format_exc()

with open("/kaggle/working/l2_dev_pseudobulk_run_summary.json", "w") as f:
    json.dump(SUMMARY, f, indent=2, default=str)

log("=== FINAL SUMMARY (JSON) ===")
print(json.dumps({k: v for k, v in SUMMARY.items() if k != "real_cell_counts_per_donor"},
                  indent=2, default=str), flush=True)
