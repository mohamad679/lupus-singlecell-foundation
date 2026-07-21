"""Sealed-cohort (GSE135779) pseudobulk: real per-sample raw counts,
restricted to the frozen 30,165-gene intersection, CPM-normalized over that
restricted total, log1p. Per PREREG Section 8 (restriction happens on raw
count matrices, before normalization) and the human decision locking this
convention on 2026-07-21, before any sealed data was touched.

Real code, real math, local. Reads the 56 already-downloaded GSE135779
samples (data/raw/GSE135779/extracted/*.mtx.gz + *_barcodes.tsv.gz), which
are real per-cell raw count matrices from the public GEO deposit -- this IS
the sealed-cohort opening, run exactly once per PREREG/FREEZE.

Output: one row per sample (56 rows), columns = the 30,165 shared genes,
in the same column order as results/gene_space_intersection.txt.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.io

sys.path.insert(0, str(Path(__file__).resolve().parent))
from freeze_guard import require_valid_freeze  # noqa: E402

require_valid_freeze()

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "raw" / "GSE135779" / "extracted"
RESULTS_DIR = REPO_ROOT / "results"

GENE_REF_PATH = RESULTS_DIR / "gse135779_genes_reference.tsv"
INTERSECTION_PATH = RESULTS_DIR / "gene_space_intersection.txt"
SAMPLE_META_PATH = REPO_ROOT / "data" / "raw" / "GSE135779" / "sample_metadata.csv"


def load_sealed_gene_order() -> list[str]:
    """Ensembl IDs in the exact row order of every sample's matrix.mtx
    (all 56 samples share the one series-level gene reference)."""
    genes = []
    with open(GENE_REF_PATH) as f:
        for line in f:
            genes.append(line.rstrip("\n").split("\t")[0])
    return genes


def load_intersection_genes() -> list[str]:
    with open(INTERSECTION_PATH) as f:
        return [line.strip() for line in f if line.strip()]


def find_sample_files() -> dict[str, tuple[Path, Path]]:
    """gsm_id -> (matrix_path, barcodes_path), discovered from real files on disk."""
    out = {}
    for matrix_path in sorted(RAW_DIR.glob("*_matrix.mtx.gz")):
        gsm_id = matrix_path.name.split("_")[0]
        barcodes_candidates = list(RAW_DIR.glob(f"{gsm_id}_*_barcodes.tsv.gz"))
        if len(barcodes_candidates) != 1:
            raise RuntimeError(f"expected exactly 1 barcodes file for {gsm_id}, found {barcodes_candidates}")
        out[gsm_id] = (matrix_path, barcodes_candidates[0])
    return out


def compute_sample_pseudobulk(matrix_path: Path, intersection_mask: np.ndarray) -> tuple[np.ndarray, int, float]:
    """Real math: sum raw counts per gene across all cells in this sample,
    restrict to the intersection genes, CPM-normalize over the restricted
    total, log1p. Returns (log1p_cpm_restricted, n_cells, restricted_total_counts).
    """
    mat = scipy.io.mmread(matrix_path).tocsr()  # genes x cells, sparse
    n_genes, n_cells = mat.shape
    gene_sums_full = np.asarray(mat.sum(axis=1)).ravel()  # (n_genes,)
    if len(intersection_mask) != n_genes:
        raise RuntimeError(
            f"gene reference length {len(intersection_mask)} != matrix gene rows {n_genes}"
        )
    restricted = gene_sums_full[intersection_mask]
    restricted_total = float(restricted.sum())
    if restricted_total <= 0:
        raise RuntimeError(f"{matrix_path}: zero total counts in the 30,165-gene intersection")
    cpm = restricted / restricted_total * 1_000_000.0
    log1p_cpm = np.log1p(cpm)
    return log1p_cpm, n_cells, restricted_total


def main() -> None:
    sealed_gene_order = load_sealed_gene_order()
    intersection_genes = set(load_intersection_genes())
    intersection_mask = np.array([g in intersection_genes for g in sealed_gene_order])
    n_kept = int(intersection_mask.sum())
    print(f"sealed gene reference: {len(sealed_gene_order)} genes, "
          f"{n_kept} in the frozen 30,165-gene intersection "
          f"(expected 30165, since GSE135779's own reference is a subset check)")
    assert n_kept == 30165, f"expected 30165 genes to match, got {n_kept}"

    # column order for the output = intersection order restricted to genes
    # actually present in the sealed reference, in the sealed reference's
    # own row order (deterministic, not re-sorted, so it matches the mask
    # indexing used per-sample above)
    kept_gene_ids = [g for g in sealed_gene_order if g in intersection_genes]

    sample_files = find_sample_files()
    print(f"found {len(sample_files)} samples with matched matrix+barcodes files on disk")
    assert len(sample_files) == 56, f"expected 56 samples, found {len(sample_files)}"

    meta = {}
    with open(SAMPLE_META_PATH) as f:
        for row in csv.DictReader(f):
            meta[row["gsm_id"]] = row

    records = []
    pseudobulk_rows = {}
    for gsm_id, (matrix_path, barcodes_path) in sample_files.items():
        log1p_cpm, n_cells, restricted_total = compute_sample_pseudobulk(matrix_path, intersection_mask)
        m = meta[gsm_id]
        pseudobulk_rows[gsm_id] = log1p_cpm
        records.append({
            "gsm_id": gsm_id,
            "title": m["title"],
            "age": int(m["age"]),
            "age_group": m["age_group"],
            "group": m["group"],
            "sle_label": 1 if m["group"] == "SLE" else 0,
            "n_cells": n_cells,
            "restricted_total_counts": restricted_total,
        })
        print(f"  {gsm_id} ({m['title']}): {n_cells} cells, "
              f"restricted total counts={restricted_total:.0f}")

    df = pd.DataFrame(pseudobulk_rows).T
    df.columns = kept_gene_ids
    df.index.name = "gsm_id"
    df = df.sort_index()
    out_path = RESULTS_DIR / "l2_sealed_pseudobulk_counts.parquet"
    df.to_parquet(out_path, compression="zstd")
    print(f"\nwrote {out_path}: shape={df.shape}")

    meta_df = pd.DataFrame(records).sort_values("gsm_id")
    meta_out_path = RESULTS_DIR / "l2_sealed_donor_metadata.csv"
    meta_df.to_csv(meta_out_path, index=False)
    print(f"wrote {meta_out_path}: {len(meta_df)} rows")

    print()
    print("=== label counts ===")
    print(meta_df["sle_label"].value_counts().to_dict())
    print("=== age group counts ===")
    print(meta_df["age_group"].value_counts().to_dict())


if __name__ == "__main__":
    main()
