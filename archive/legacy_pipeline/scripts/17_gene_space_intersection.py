"""Gene-space intersection: dev cohort (Perez 2022) x sealed cohort (GSE135779).

Real code, real math, per PREREG.md Section 8 ("Gene-space intersection:
features are restricted to the intersection of genes present and comparably
identified... in both the dev and sealed cohort's raw count matrices.").
Both cohorts use Ensembl gene IDs (verified during Phase 2 pre-flight, no
symbol-to-ID mapping needed), so the intersection is a plain set operation.

Inputs (both already-verified, real, no expression/cell data touched):
- results/l2_dev_pseudobulk_counts.parquet columns: dev's 61,497 Ensembl gene
  IDs, already committed.
- results/gse135779_genes_reference.tsv: GSE135779's series-level 10X
  CellRanger v2 gene reference (32,738 genes, Ensembl ID + symbol,
  fetched from the public GEO FTP during Phase 2 -- this is a gene
  reference/annotation file, not expression or cell-level data).

Run with --self-test to execute the unit tests (synthetic cases + the real
integration check against the committed artifacts, which pins the exact
verified overlap count from Phase 2: 30,165 genes) without writing output.
Run with no arguments to compute and write the real intersection artifact.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = REPO_ROOT / "results"

DEV_PSEUDOBULK_PATH = RESULTS_DIR / "l2_dev_pseudobulk_counts.parquet"
SEALED_GENES_PATH = RESULTS_DIR / "gse135779_genes_reference.tsv"
OUTPUT_PATH = RESULTS_DIR / "gene_space_intersection.txt"

# Pinned real result from Phase 2 pre-flight (2026-07-20), used as a
# regression oracle in the self-test -- if this ever changes, the input
# files changed and that is worth knowing, not silently accepting.
EXPECTED_OVERLAP_COUNT = 30165
EXPECTED_DEV_GENE_COUNT = 61497
EXPECTED_SEALED_GENE_COUNT = 32738


def compute_gene_intersection(genes_a, genes_b) -> list[str]:
    """Pure function: sorted list of gene IDs present in both inputs.

    No I/O, no assumptions about identifier system beyond "compare as
    strings" -- callers are responsible for ensuring both inputs use the
    same identifier system (verified separately: both cohorts use Ensembl
    IDs, checked during Phase 2 pre-flight).
    """
    return sorted(set(genes_a) & set(genes_b))


def load_dev_genes(path: Path = DEV_PSEUDOBULK_PATH) -> list[str]:
    # Read only the parquet schema (column names), not the row data -- no
    # need to materialize the 261x61,497 matrix just to get gene IDs.
    import pyarrow.parquet as pq

    schema = pq.read_schema(path)
    return [name for name in schema.names if name != "donor_id"]


def load_sealed_genes(path: Path = SEALED_GENES_PATH) -> list[str]:
    genes = []
    with open(path) as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if not parts or not parts[0]:
                continue
            genes.append(parts[0])
    return genes


def run_self_test() -> None:
    print("[self-test] synthetic cases...")

    # basic overlap
    result = compute_gene_intersection(["A", "B", "C"], ["B", "C", "D"])
    assert result == ["B", "C"], result

    # no overlap
    result = compute_gene_intersection(["A", "B"], ["C", "D"])
    assert result == [], result

    # full overlap (order-independent, sorted output)
    result = compute_gene_intersection(["Z", "A", "M"], ["M", "Z", "A"])
    assert result == ["A", "M", "Z"], result

    # duplicates in input do not duplicate output
    result = compute_gene_intersection(["A", "A", "B"], ["A", "B", "B"])
    assert result == ["A", "B"], result

    # empty input
    result = compute_gene_intersection([], ["A", "B"])
    assert result == [], result

    print("[self-test] synthetic cases PASSED")

    print("[self-test] real integration check against committed artifacts...")
    dev_genes = load_dev_genes()
    sealed_genes = load_sealed_genes()

    print(f"[self-test] dev genes: {len(dev_genes)} (expected {EXPECTED_DEV_GENE_COUNT})")
    assert len(dev_genes) == EXPECTED_DEV_GENE_COUNT, (
        f"dev gene count changed: {len(dev_genes)} != {EXPECTED_DEV_GENE_COUNT}. "
        "results/l2_dev_pseudobulk_counts.parquet may have been regenerated."
    )
    assert len(set(dev_genes)) == len(dev_genes), "dev gene list has duplicates"

    print(f"[self-test] sealed genes: {len(sealed_genes)} (expected {EXPECTED_SEALED_GENE_COUNT})")
    assert len(sealed_genes) == EXPECTED_SEALED_GENE_COUNT, (
        f"sealed gene count changed: {len(sealed_genes)} != {EXPECTED_SEALED_GENE_COUNT}. "
        "results/gse135779_genes_reference.tsv may have been regenerated."
    )

    overlap = compute_gene_intersection(dev_genes, sealed_genes)
    print(f"[self-test] overlap: {len(overlap)} (expected {EXPECTED_OVERLAP_COUNT})")
    assert len(overlap) == EXPECTED_OVERLAP_COUNT, (
        f"overlap count changed: {len(overlap)} != {EXPECTED_OVERLAP_COUNT}. "
        "This reproduces (or fails to reproduce) the real Phase 2 pre-flight "
        "finding -- investigate before trusting any downstream harmonization."
    )
    assert all(g.startswith("ENSG") for g in overlap[:100]), "overlap genes are not Ensembl IDs"

    print("[self-test] real integration check PASSED "
          f"({len(overlap)} genes, {len(overlap)/len(dev_genes)*100:.2f}% of dev, "
          f"{len(overlap)/len(sealed_genes)*100:.2f}% of sealed)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true",
                         help="Run unit tests only; do not write the output artifact.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    dev_genes = load_dev_genes()
    sealed_genes = load_sealed_genes()
    overlap = compute_gene_intersection(dev_genes, sealed_genes)

    OUTPUT_PATH.write_text("\n".join(overlap) + "\n")
    print(f"dev genes: {len(dev_genes)}, sealed genes: {len(sealed_genes)}, "
          f"overlap: {len(overlap)}")
    print(f"wrote {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
