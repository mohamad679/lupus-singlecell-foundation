"""L2 dev-cohort pipeline: census-streamed metadata + donor-level pseudobulk.

Real code, per PREREG.md's locked conventions (Sections 2, 3, 7). This is not
a fake-data contract — every function here performs real math on real data
pulled from the CZ CELLxGENE Census. It does not touch GSE135779 (sealed
cohort) and does not implement Geneformer inference.

Two entry points, deliberately separated by cost:

- `fetch_donor_metadata()` / `--metadata-only`: obs-only census query. Cheap
  (single query, seconds). Safe to run locally. This is how the 162 SLE / 99
  healthy donor count is confirmed against PREREG (no expression data
  touched).

- `compute_donor_pseudobulk()` / `--donor <id>` or `--all`: streams raw X
  counts per donor from census and does real CPM-normalize + log1p
  aggregation (PREREG Section 3, arm 2). A single-donor timing probe (donor
  HC-546, 4,102 cells) measured ~327s end-to-end from a residential network
  connection to census's S3-backed store. Naively extrapolated across 261
  donors and ~1.26M cells, sequential per-donor fetches at that rate would
  take on the order of a day — this is why `--all` is intended to run on
  Kaggle (better network path to the census bucket, and should be
  re-benchmarked there before committing to a full run), not locally. Do not
  invoke `--all` locally.

Known data-quality note (real, verified): donors "1130" and "1772" have two
distinct `development_stage` values across their cells (27/29-year-old-stage
and 20/21-year-old-stage respectively) instead of one. This looks like a
birthday-crossing artifact in the source annotation. Per human decision
(2026-07-19, see PREREG.md amendment log), these two donors are flagged
`age_flag=age_ambiguous`, `metadata_arm_eligible=False`, and excluded from
the metadata-only arm (n=259 for that arm) rather than resolved by taking a
minimum or average. They remain in the full 261-donor set for the other two
arms (Geneformer, pseudobulk), which don't depend on age.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "results"

CENSUS_VERSION = "2025-11-08"
DATASET_ID = "218acb0f-9f2f-4f76-b90b-15a4b7c7f629"  # Perez et al. 2022, PREREG Section 2
COLLECTION_ID = "436154da-bcf1-4130-9c8b-120ff9a888f2"

_AGE_RE = re.compile(r"^(\d+)-year-old stage$")


class L2PipelineError(RuntimeError):
    """Raised when a real data-integrity assumption fails."""


def parse_development_stage_age(value: str) -> int | None:
    """Parse a HsapDv-style label ('34-year-old stage') to an integer age.

    Returns None for anything that doesn't match the expected pattern
    (e.g. non-adult HsapDv terms) rather than guessing.
    """

    match = _AGE_RE.match(value)
    if match is None:
        return None
    return int(match.group(1))


def fetch_donor_metadata() -> list[dict]:
    """Real, donor-level metadata for the Perez 2022 dev cohort via census.

    Queries obs columns only (disease, sex, self_reported_ethnicity,
    development_stage) for the fixed DATASET_ID. Does not touch X. One donor
    row per output record, deduplicated from cell-level obs rows after
    confirming each field is donor-invariant (raises otherwise, rather than
    silently picking one value).
    """

    import cellxgene_census

    census = cellxgene_census.open_soma(census_version=CENSUS_VERSION)
    try:
        obs_df = cellxgene_census.get_obs(
            census,
            "homo_sapiens",
            value_filter=f"dataset_id == '{DATASET_ID}'",
            column_names=[
                "donor_id",
                "disease",
                "sex",
                "self_reported_ethnicity",
                "development_stage",
            ],
        )
    finally:
        census.close()

    for col in ("disease", "sex", "self_reported_ethnicity"):
        n_multi = int(obs_df.groupby("donor_id")[col].nunique().gt(1).sum())
        if n_multi:
            raise L2PipelineError(
                f"{col} is not donor-invariant for {n_multi} donors; "
                "aggregation assumption violated, aborting rather than guessing."
            )

    records: list[dict] = []
    for donor_id, group in obs_df.groupby("donor_id", observed=True):
        stages = sorted(group["development_stage"].unique().tolist())
        ages = [a for a in (parse_development_stage_age(s) for s in stages) if a is not None]
        age_flag = "ok"
        metadata_arm_eligible = True
        age = None
        if len(stages) > 1:
            # Decision (2026-07-19, human): do not resolve by taking the
            # minimum. Flag as ambiguous and exclude this donor from the
            # metadata-only arm rather than guess which age is correct.
            age_flag = "age_ambiguous"
            metadata_arm_eligible = False
        elif ages:
            age = ages[0]
        records.append(
            {
                "donor_id": donor_id,
                "disease": group["disease"].iloc[0],
                "sle_label": 1 if group["disease"].iloc[0] == "systemic lupus erythematosus" else 0,
                "sex": group["sex"].iloc[0],
                "self_reported_ethnicity": group["self_reported_ethnicity"].iloc[0],
                "age": age,
                "age_flag": age_flag,
                "metadata_arm_eligible": metadata_arm_eligible,
                "development_stage_raw": ";".join(stages),
                "n_cells": int(len(group)),
            }
        )
    records.sort(key=lambda r: r["donor_id"])
    return records


def compute_donor_pseudobulk_from_counts(
    donor_gene_sums: dict[str, "np.ndarray"],
) -> dict[str, "np.ndarray"]:
    """Real CPM-normalize + log1p aggregation (PREREG Section 3, arm 2).

    Input: donor_id -> raw per-gene count sum across that donor's cells
    (already summed; summing is the aggregation step, done by the caller
    while streaming so the full cell-by-gene matrix is never materialized at
    once). Output: donor_id -> CPM-normalized, log1p-transformed vector.

    Pure math, no census/network dependency, so it is unit-testable without
    touching the network.
    """

    import numpy as np

    out: dict[str, "np.ndarray"] = {}
    for donor_id, gene_sum in donor_gene_sums.items():
        total = gene_sum.sum()
        if total <= 0:
            raise L2PipelineError(f"donor {donor_id} has zero total counts; cannot CPM-normalize.")
        cpm = gene_sum / total * 1_000_000.0
        out[donor_id] = np.log1p(cpm)
    return out


def stream_donor_pseudobulk(donor_ids: list[str] | None = None) -> dict[str, "np.ndarray"]:
    """Stream raw X counts from census for the given donors (or all 261) and
    sum per gene per donor, then CPM+log1p normalize.

    Uses a single chunked axis_query per donor group rather than materializing
    a dense matrix, so memory stays bounded regardless of cell count. This is
    the function `--all` calls; it is expected to be slow from a non-Kaggle
    network path (see module docstring) and is not invoked by default.
    """

    import numpy as np
    import tiledbsoma as soma
    import cellxgene_census

    census = cellxgene_census.open_soma(census_version=CENSUS_VERSION)
    try:
        exp = census["census_data"]["homo_sapiens"]
        value_filter = f"dataset_id == '{DATASET_ID}'"
        if donor_ids:
            id_list = ",".join(f"'{d}'" for d in donor_ids)
            value_filter += f" and donor_id in [{id_list}]"

        with exp.axis_query(
            measurement_name="RNA",
            obs_query=soma.AxisQuery(value_filter=value_filter),
        ) as query:
            n_genes = query.n_vars
            var_joinids = np.asarray(query.var_joinids())  # PyArrow Int64Array, not numpy
            # Dense lookup array: var soma_joinid -> dense gene column index.
            # Vectorized (np.add.at below), not a per-entry Python dict lookup.
            var_col_of_joinid = np.full(int(var_joinids.max()) + 1, -1, dtype=np.int64)
            var_col_of_joinid[var_joinids] = np.arange(len(var_joinids))

            obs_table = query.obs(column_names=["soma_joinid", "donor_id"]).concat().to_pandas()
            donor_ids_sorted = sorted(obs_table["donor_id"].unique().tolist())
            donor_row_of_id = {d: i for i, d in enumerate(donor_ids_sorted)}
            obs_joinids = obs_table["soma_joinid"].to_numpy()
            donor_row_of_joinid = np.full(int(obs_joinids.max()) + 1, -1, dtype=np.int64)
            donor_row_of_joinid[obs_joinids] = obs_table["donor_id"].map(donor_row_of_id).to_numpy()

            gene_sums = np.zeros((len(donor_ids_sorted), n_genes), dtype=np.float64)
            for x_tbl in query.X("raw").tables():
                soma_dim_0 = x_tbl["soma_dim_0"].to_numpy()
                soma_dim_1 = x_tbl["soma_dim_1"].to_numpy()
                values = x_tbl["soma_data"].to_numpy()
                donor_rows = donor_row_of_joinid[soma_dim_0]
                gene_cols = var_col_of_joinid[soma_dim_1]
                np.add.at(gene_sums, (donor_rows, gene_cols), values)

            donor_gene_sums = {d: gene_sums[i] for i, d in enumerate(donor_ids_sorted)}
    finally:
        census.close()

    return compute_donor_pseudobulk_from_counts(donor_gene_sums)


def write_metadata_csv(records: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "donor_id",
        "disease",
        "sle_label",
        "sex",
        "self_reported_ethnicity",
        "age",
        "age_flag",
        "metadata_arm_eligible",
        "development_stage_raw",
        "n_cells",
    ]
    with output_path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--metadata-only",
        action="store_true",
        help="Fetch donor-level metadata only (obs query, cheap, local-safe).",
    )
    parser.add_argument(
        "--donor",
        type=str,
        default=None,
        help="Run pseudobulk aggregation for a single donor id (smoke test).",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run pseudobulk aggregation for all 261 donors. SLOW from a "
        "non-Kaggle network path (see module docstring); intended for "
        "Kaggle execution, not local use.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
    )
    args = parser.parse_args(argv)

    if args.metadata_only:
        records = fetch_donor_metadata()
        n_sle = sum(r["sle_label"] for r in records)
        n_healthy = len(records) - n_sle
        n_metadata_arm = sum(r["metadata_arm_eligible"] for r in records)
        n_excluded = len(records) - n_metadata_arm
        print(f"donors: {len(records)}  SLE: {n_sle}  healthy: {n_healthy}")
        print(f"metadata-only arm eligible: {n_metadata_arm}  excluded (age_ambiguous): {n_excluded}")
        write_metadata_csv(records, args.output_dir / "l2_dev_donor_metadata.csv")
        return 0

    if args.donor:
        result = stream_donor_pseudobulk([args.donor])
        vec = result[args.donor]
        print(f"donor {args.donor}: pseudobulk vector shape={vec.shape} "
              f"mean={vec.mean():.4f} nonzero={(vec > 0).sum()}")
        return 0

    if args.all:
        print(
            "Refusing to run --all locally by default. This is intended for "
            "Kaggle execution per PREREG/L2 plan. Pass --i-know-this-is-slow "
            "to override.",
            file=sys.stderr,
        )
        if "--i-know-this-is-slow" not in (argv or sys.argv[1:]):
            return 1
        result = stream_donor_pseudobulk(None)
        print(f"computed pseudobulk for {len(result)} donors")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
