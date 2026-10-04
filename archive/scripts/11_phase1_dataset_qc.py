#!/usr/bin/env python3
"""Run Phase 1 acquisition fallback, schema audit, QC, and visualization.

The public GEO record for GSE174188 currently has no supplementary h5ad.
When no user-supplied real h5ad is present, this script creates the required
500 x 200 acquisition fixture and a separate 500 x 2500 validation fixture.
The larger fixture is necessary to validate the independent 2,000-HVG
acceptance criterion without misrepresenting the dimensions of mini_test.h5ad.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from importlib.metadata import version
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache" / "matplotlib"))

import anndata as ad
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import scanpy as sc
import seaborn as sns
from scipy import sparse


RAW_DIR = ROOT / "data" / "raw"
REAL_DIR = RAW_DIR / "GSE174188"
MINI_PATH = RAW_DIR / "mini_test.h5ad"
VALIDATION_PATH = RAW_DIR / "mini_phase1_validation.h5ad"
PROCESSED_PATH = ROOT / "data" / "processed" / "lupus_qc_processed.h5ad"
RESULTS_DIR = ROOT / "results" / "phase1"
SCHEMA_PATH = RESULTS_DIR / "schema_map.json"
PATIENT_SUMMARY_PATH = RESULTS_DIR / "patient_summary.csv"
REPORT_PATH = RESULTS_DIR / "PHASE1_REPORT.md"
ACQUISITION_PATH = RESULTS_DIR / "acquisition_status.json"
INSTRUCTIONS_PATH = RAW_DIR / "DOWNLOAD_INSTRUCTIONS.md"

GEO_RECORD_URL = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE174188"
GEO_SUPPL_URL = (
    "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE174nnn/GSE174188/suppl/"
)
HCA_PROJECT_URL = (
    "https://explore.data.humancellatlas.org/projects/"
    "9fc0064b-84ce-40a5-a768-e6eb3d364ee0"
)
SCANPY_VERSION = version("scanpy")
ANNDATA_VERSION = version("anndata")

FIELD_ALIASES = {
    "patient_id": [
        "patient_id",
        "donor_id",
        "donor",
        "subject_id",
        "individual_id",
        "ind_cov",
        "participant_id",
        "orig.ident",
    ],
    "disease_group": [
        "disease_group",
        "group",
        "disease",
        "condition",
        "disease_label",
        "SLE_status",
        "status",
    ],
    "sledai_score": [
        "sledai_score",
        "SLEDAI",
        "SLEDAI_score",
        "sledai",
        "disease_activity_score",
    ],
    "cell_type": [
        "cell_type",
        "celltype",
        "cell_type_annotation",
        "celltype.l1",
        "annotation",
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        help="Explicit h5ad input. Otherwise prefer data/raw/GSE174188/*.h5ad.",
    )
    parser.add_argument(
        "--check-geo",
        action="store_true",
        help="Query the official GEO supplementary directory before fallback.",
    )
    parser.add_argument(
        "--force-synthetic",
        action="store_true",
        help="Use the synthetic validation fixture even if a real h5ad exists.",
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="Random seed for reproducibility."
    )
    return parser.parse_args()


def ensure_directories() -> None:
    for path in (RAW_DIR, REAL_DIR, PROCESSED_PATH.parent, RESULTS_DIR):
        path.mkdir(parents=True, exist_ok=True)


def write_download_instructions() -> None:
    text = f"""# GSE174188 download instructions

## Current source status

The official GEO record currently says that supplementary data files are not
provided, so there is no public GEO h5ad filename to place in a wget or curl
command. The record points to controlled access because of patient privacy.
The HCA project is public but currently lists FASTQ files, not a ready h5ad.

- GEO record: {GEO_RECORD_URL}
- GEO supplementary directory: {GEO_SUPPL_URL}
- HCA project: {HCA_PROJECT_URL}

Do not rename a different dataset to look like GSE174188. After a legitimate
h5ad export is obtained, place it under `data/raw/GSE174188/` and rerun the
pipeline. Raw source files are never overwritten by the pipeline.

## Exact GEO checks

```bash
mkdir -p data/raw/GSE174188
curl --fail --location --retry 3 \\
  '{GEO_SUPPL_URL}' \\
  --output data/raw/GSE174188/GEO_SUPPLEMENT_LISTING.html

wget --recursive --no-parent --no-host-directories --cut-dirs=4 \\
  --accept='*.h5ad,*.h5ad.gz' \\
  --directory-prefix=data/raw/GSE174188 \\
  '{GEO_SUPPL_URL}'
```

These commands currently return no h5ad because GEO publishes none for this
series. They are intentionally retained so the source can be rechecked if the
record changes.

## GEO metadata (not an expression matrix)

```bash
curl --fail --location --retry 3 \\
  'https://ftp.ncbi.nlm.nih.gov/geo/series/GSE174nnn/GSE174188/soft/GSE174188_family.soft.gz' \\
  --output data/raw/GSE174188/GSE174188_family.soft.gz
```

## After an authorized/public h5ad is obtained

```bash
source .venv/bin/activate
python scripts/11_phase1_dataset_qc.py \\
  --input data/raw/GSE174188/<authorized-file>.h5ad
python scripts/12_verify_phase1.py
```

The included `mini_test.h5ad` is a synthetic 500-cell, 200-gene acquisition
fallback only. `mini_phase1_validation.h5ad` has 2,500 genes and is used to
exercise the exact 2,000-HVG acceptance criterion.
"""
    INSTRUCTIONS_PATH.write_text(text)


def check_geo_supplementary() -> dict[str, Any]:
    status: dict[str, Any] = {
        "url": GEO_SUPPL_URL,
        "attempted": True,
        "h5ad_links": [],
    }
    try:
        response = requests.get(GEO_SUPPL_URL, timeout=30)
        status["http_status"] = response.status_code
        if response.status_code == 404:
            status["result"] = "no_supplement_directory"
            return status
        response.raise_for_status()
        links = re.findall(r'href=["\']([^"\']+\.h5ad(?:\.gz)?)["\']', response.text)
        status["h5ad_links"] = sorted(set(links))
        status["result"] = "h5ad_found" if links else "no_h5ad_published"
    except requests.RequestException as exc:
        status["result"] = "unavailable"
        status["error"] = f"{type(exc).__name__}: {exc}"
    return status


def create_synthetic_dataset(path: Path, n_genes: int, seed: int) -> None:
    if path.exists():
        existing = ad.read_h5ad(path, backed="r")
        expected = (500, n_genes)
        actual = tuple(existing.shape)
        if getattr(existing, "file", None) is not None:
            existing.file.close()
        if actual == expected:
            return
        raise ValueError(f"Existing {path} has shape {actual}, expected {expected}")

    rng = np.random.default_rng(seed)
    n_cells = 500
    n_mito = min(20 if n_genes == 200 else 50, n_genes // 4)
    matrix = np.zeros((n_cells, n_genes), dtype=np.int16)

    low_quality: set[int] = set()
    high_mito: set[int] = set()
    for patient_index in range(10):
        start = patient_index * 50
        bad_per_type = 3 if patient_index < 5 else 2
        low_quality.update(range(start, start + bad_per_type))
        high_mito.update(range(start + bad_per_type, start + 2 * bad_per_type))

    for cell_index in range(n_cells):
        if n_genes == 200:
            probability = 0.08 if cell_index in low_quality else 0.72
        else:
            probability = 0.03 if cell_index in low_quality else 0.14
        expressed = rng.random(n_genes) < probability
        matrix[cell_index, expressed] = (
            rng.poisson(1.5, int(expressed.sum())) + 1
        ).astype(np.int16)
        if cell_index in high_mito:
            matrix[cell_index, :n_mito] = (
                rng.poisson(24, n_mito) + 12
            ).astype(np.int16)

    groups = [
        "Flare",
        "Flare",
        "Flare",
        "Managed",
        "Managed",
        "Treated",
        "Treated",
        "Healthy",
        "Healthy",
        "Healthy",
    ]
    sledai_base = {"Flare": 14.0, "Managed": 6.0, "Treated": 3.0, "Healthy": 0.0}
    cell_types = np.array(
        ["B cell", "CD4 T cell", "CD8 T cell", "NK cell", "Classical monocyte"]
    )
    patient_numbers = np.arange(n_cells) // 50
    patient_ids = np.array([f"P{number + 1:03d}" for number in patient_numbers])
    disease_groups = np.array([groups[number] for number in patient_numbers])
    sledai = np.array(
        [sledai_base[group] + (number % 2) for group, number in zip(disease_groups, patient_numbers)]
    )

    obs = pd.DataFrame(
        {
            "donor_id": patient_ids,
            "disease_group": disease_groups,
            "SLEDAI": sledai,
            "cell_type": cell_types[np.arange(n_cells) % len(cell_types)],
            "synthetic_quality_class": np.select(
                [
                    np.isin(np.arange(n_cells), list(low_quality)),
                    np.isin(np.arange(n_cells), list(high_mito)),
                ],
                ["low_genes", "high_mito"],
                default="pass",
            ),
        },
        index=[f"CELL_{index:04d}" for index in range(n_cells)],
    )
    gene_names = [f"MT-SYN{index + 1:02d}" for index in range(n_mito)]
    gene_names.extend(
        f"GENE{index + 1:04d}" for index in range(n_genes - n_mito)
    )
    var = pd.DataFrame(
        {"gene_symbol": gene_names, "feature_type": "Gene Expression"},
        index=gene_names,
    )
    adata = ad.AnnData(X=sparse.csr_matrix(matrix), obs=obs, var=var)
    adata.uns.update(
        {
            "dataset_id": "synthetic_phase1_fixture",
            "source": "deterministic local generator",
            "synthetic": True,
            "seed": seed,
        }
    )
    adata.write_h5ad(path, compression="gzip")


def find_input(explicit: Path | None, force_synthetic: bool) -> tuple[Path, str]:
    if explicit is not None:
        path = explicit.expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(path)
        return path, "explicit h5ad"

    real_files = sorted(REAL_DIR.glob("*.h5ad"))
    if real_files and not force_synthetic:
        return real_files[0], "GSE174188 local h5ad"
    return VALIDATION_PATH, "synthetic validation fixture"


def closest_column(columns: Iterable[str], aliases: list[str]) -> str | None:
    columns = list(columns)
    exact = {str(column): str(column) for column in columns}
    folded = {str(column).casefold(): str(column) for column in columns}
    for alias in aliases:
        if alias in exact:
            return exact[alias]
        if alias.casefold() in folded:
            return folded[alias.casefold()]
    return None


def schema_audit(adata: ad.AnnData, input_path: Path) -> dict[str, Any]:
    mapping: dict[str, Any] = {}
    for canonical, aliases in FIELD_ALIASES.items():
        source = closest_column(adata.obs.columns, aliases)
        mapping[canonical] = {
            "source_column": source,
            "status": "confirmed" if source else "not_available",
            "aliases_checked": aliases,
        }

    patient_source = mapping["patient_id"]["source_column"]
    group_source = mapping["disease_group"]["source_column"]
    if patient_source is None:
        raise ValueError("No patient identifier column found in adata.obs")
    if group_source is None:
        raise ValueError("No disease/group column found in adata.obs")

    adata.obs["patient_id"] = adata.obs[patient_source].astype(str)
    adata.obs["disease_group"] = adata.obs[group_source].astype(str)
    sledai_source = mapping["sledai_score"]["source_column"]
    if sledai_source:
        adata.obs["sledai_score"] = pd.to_numeric(
            adata.obs[sledai_source], errors="coerce"
        )
    else:
        adata.obs["sledai_score"] = np.nan
    cell_type_source = mapping["cell_type"]["source_column"]
    if cell_type_source:
        adata.obs["cell_type"] = adata.obs[cell_type_source].astype(str)

    patient_counts = adata.obs["patient_id"].value_counts()
    group_counts = adata.obs["disease_group"].value_counts().sort_index()
    audit = {
        "input_path": str(input_path),
        "n_obs": int(adata.n_obs),
        "n_vars": int(adata.n_vars),
        "obs_columns": list(map(str, adata.obs.columns)),
        "obsm_keys": list(map(str, adata.obsm.keys())),
        "uns_keys": list(map(str, adata.uns.keys())),
        "canonical_fields": mapping,
        "patient_id_confirmed": bool(adata.obs["patient_id"].notna().all()),
        "unique_patients": int(adata.obs["patient_id"].nunique()),
        "cells_per_patient": {
            "min": int(patient_counts.min()),
            "max": int(patient_counts.max()),
            "mean": float(patient_counts.mean()),
        },
        "group_distribution_cells": {
            str(key): int(value) for key, value in group_counts.items()
        },
    }
    SCHEMA_PATH.write_text(json.dumps(audit, indent=2) + "\n")
    print(f"Schema: {adata.n_obs} cells x {adata.n_vars} genes")
    print(f"obs columns: {list(adata.obs.columns)}")
    print(f"obsm keys: {list(adata.obsm.keys())}")
    print(f"uns keys: {list(adata.uns.keys())}")
    print(
        "Cells/patient: "
        f"min={patient_counts.min()}, max={patient_counts.max()}, "
        f"mean={patient_counts.mean():.1f}"
    )
    print(f"Groups: {group_counts.to_dict()}")
    return audit


def save_qc_plots(adata: ad.AnnData) -> None:
    sns.set_theme(style="whitegrid")
    metrics = ["n_genes_by_counts", "total_counts", "pct_counts_mt"]
    labels = ["Genes per cell", "Total counts", "Mitochondrial counts (%)"]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    for axis, metric, label in zip(axes, metrics, labels):
        sns.violinplot(y=adata.obs[metric], ax=axis, color="#4C78A8", inner="quart")
        axis.set_ylabel(label)
        axis.set_xlabel("")
    fig.suptitle("Post-QC cell metrics")
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "qc_violin.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    scatter = axes[0].scatter(
        adata.obs["total_counts"],
        adata.obs["n_genes_by_counts"],
        c=adata.obs["pct_counts_mt"],
        s=12,
        alpha=0.7,
        cmap="viridis",
    )
    axes[0].set(xlabel="Total counts", ylabel="Genes per cell")
    fig.colorbar(scatter, ax=axes[0], label="Mitochondrial counts (%)")
    axes[1].scatter(
        adata.obs["total_counts"],
        adata.obs["pct_counts_mt"],
        s=12,
        alpha=0.7,
        color="#F58518",
    )
    axes[1].set(xlabel="Total counts", ylabel="Mitochondrial counts (%)")
    fig.suptitle("Post-QC count relationships")
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "qc_scatter.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def run_qc(adata: ad.AnnData) -> tuple[ad.AnnData, dict[str, int]]:
    before_cells, before_genes = adata.shape
    sc.pp.filter_cells(adata, min_genes=200)
    sc.pp.filter_cells(adata, max_genes=6000)
    sc.pp.filter_genes(adata, min_cells=3)
    adata.var["mt"] = adata.var_names.str.upper().str.startswith("MT-")
    sc.pp.calculate_qc_metrics(
        adata, qc_vars=["mt"], percent_top=None, log1p=False, inplace=True
    )
    adata = adata[adata.obs["pct_counts_mt"] < 20].copy()
    sc.pp.calculate_qc_metrics(
        adata, qc_vars=["mt"], percent_top=None, log1p=False, inplace=True
    )
    after_cells, after_genes = adata.shape
    if after_cells == 0 or after_genes == 0:
        raise ValueError("QC removed every cell or gene")
    save_qc_plots(adata)
    summary = {
        "cells_before": int(before_cells),
        "cells_after": int(after_cells),
        "genes_before": int(before_genes),
        "genes_after": int(after_genes),
    }
    print(f"Cells: {before_cells} -> {after_cells}")
    print(f"Genes: {before_genes} -> {after_genes}")
    return adata, summary


def normalize_and_select_hvg(adata: ad.AnnData) -> int:
    if adata.n_vars < 2000:
        raise ValueError(
            f"Exactly 2,000 HVGs requested, but input has only {adata.n_vars} genes"
        )
    adata.layers["counts"] = adata.X.copy()
    sc.pp.normalize_total(adata, target_sum=1e4)
    adata.layers["normalized"] = adata.X.copy()
    sc.pp.log1p(adata)
    adata.layers["log_normalized"] = adata.X.copy()
    sc.pp.highly_variable_genes(adata, n_top_genes=2000)
    hvg_count = int(adata.var["highly_variable"].sum())
    if hvg_count != 2000:
        raise AssertionError(f"Expected 2,000 HVGs, found {hvg_count}")
    return hvg_count


def patient_summary(adata: ad.AnnData) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for patient_id, frame in adata.obs.groupby("patient_id", observed=True):
        groups = sorted(frame["disease_group"].dropna().astype(str).unique())
        if len(groups) != 1:
            raise ValueError(f"Patient {patient_id} has conflicting groups: {groups}")
        scores = pd.to_numeric(frame["sledai_score"], errors="coerce").dropna()
        if "cell_type" in frame:
            types = sorted(frame["cell_type"].dropna().astype(str).unique())
            type_text = "|".join(types) if types else "unavailable"
        else:
            type_text = "unavailable"
        rows.append(
            {
                "patient_id": str(patient_id),
                "group": groups[0],
                "sledai_score": float(scores.median()) if not scores.empty else np.nan,
                "n_cells": int(len(frame)),
                "cell_types_present": type_text,
            }
        )
    summary = pd.DataFrame(rows).sort_values("patient_id").reset_index(drop=True)
    if len(summary) != adata.obs["patient_id"].nunique():
        raise AssertionError("Patient summary row count does not match unique patients")
    if summary["group"].nunique() < 2:
        raise AssertionError("Patient summary must contain at least two groups")
    summary.to_csv(PATIENT_SUMMARY_PATH, index=False)
    return summary


def plot_umap(adata: ad.AnnData, column: str, path: Path, title: str) -> None:
    fig, axis = plt.subplots(figsize=(8, 6))
    if column not in adata.obs:
        axis.text(0.5, 0.5, f"{column} unavailable", ha="center", va="center")
        axis.set_axis_off()
    else:
        coords = pd.DataFrame(
            adata.obsm["X_umap"], columns=["UMAP1", "UMAP2"], index=adata.obs_names
        )
        coords[column] = adata.obs[column].astype(str).to_numpy()
        sns.scatterplot(
            data=coords,
            x="UMAP1",
            y="UMAP2",
            hue=column,
            s=18,
            alpha=0.8,
            linewidth=0,
            ax=axis,
        )
        axis.legend(bbox_to_anchor=(1.02, 1), loc="upper left", borderaxespad=0)
    axis.set_title(title)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def run_umap(adata: ad.AnnData, seed: int) -> None:
    sc.pp.pca(adata, random_state=seed)
    sc.pp.neighbors(adata, random_state=seed)
    sc.tl.umap(adata, random_state=seed)
    plot_umap(
        adata,
        "disease_group",
        RESULTS_DIR / "umap_by_group.png",
        "UMAP by disease group",
    )
    plot_umap(
        adata,
        "cell_type",
        RESULTS_DIR / "umap_by_celltype.png",
        "UMAP by cell type",
    )


def completion_box(
    scanpy_version: str,
    source: str,
    schema: dict[str, Any],
    qc: dict[str, int],
    patients: pd.DataFrame,
) -> str:
    patient_dist = patients["group"].value_counts().sort_index().to_dict()
    dist_text = ", ".join(f"{key}={value}" for key, value in patient_dist.items())
    return "\n".join(
        [
            "╔══════════════════════════════════════╗",
            "║     PHASE 1 COMPLETION REPORT        ║",
            "╠══════════════════════════════════════╣",
            f"║ 1.1 Environment  ✅ scanpy={scanpy_version}     ║",
            f"║ 1.2 Dataset      ✅ {source}   ║",
            f"║ 1.3 Schema       ✅ {schema['n_obs']} cells,{schema['n_vars']} genes║",
            f"║ 1.4 QC           ✅ {qc['cells_before']}→{qc['cells_after']} cells   ║",
            "║ 1.5 Processing   ✅ 2000 HVGs      ║",
            f"║ 1.6 Patients     ✅ {len(patients)} patients, {dist_text}║",
            "║ 1.7 UMAP         ✅ plots saved    ║",
            "╠══════════════════════════════════════╣",
            "║ STATUS: PHASE 1 COMPLETE ✅          ║",
            "║ NEXT: Phase 2 — Geneformer Embedding ║",
            "╚══════════════════════════════════════╝",
        ]
    )


def write_report(
    box: str,
    input_path: Path,
    source: str,
    schema: dict[str, Any],
    qc: dict[str, int],
    patients: pd.DataFrame,
) -> None:
    group_distribution = patients["group"].value_counts().sort_index().to_dict()
    if source == "synthetic validation fixture":
        acquisition_note = """No real GSE174188 h5ad was present locally. GEO currently publishes no
supplementary h5ad for this accession. The HCA project is public but lists
FASTQ source files rather than a ready h5ad. Therefore all computational
success criteria were executed against the explicitly labeled synthetic
validation fixture; scientific conclusions about GSE174188 require rerunning
this same pipeline on an authorized or public real matrix."""
    else:
        acquisition_note = f"""This run used `{input_path}`. Confirm its source provenance and access
terms before using the processed object for scientific conclusions."""
    report = f"""# Phase 1 Completion Report

```text
{box}
```

## Execution evidence

- Runtime: Scanpy {SCANPY_VERSION}; AnnData {ANNDATA_VERSION}
- Input: `{input_path.relative_to(ROOT) if input_path.is_relative_to(ROOT) else input_path}`
- Source class: {source}
- Loaded shape: {schema['n_obs']:,} cells × {schema['n_vars']:,} genes
- Patient identifier source: `{schema['canonical_fields']['patient_id']['source_column']}`
- Unique patients: {schema['unique_patients']}
- QC cells: {qc['cells_before']:,} → {qc['cells_after']:,}
- QC genes: {qc['genes_before']:,} → {qc['genes_after']:,}
- Highly variable genes: 2,000
- Patient group distribution: {group_distribution}
- Processed AnnData: `data/processed/lupus_qc_processed.h5ad`

## Acquisition limitation

{acquisition_note}
"""
    REPORT_PATH.write_text(report)


def main() -> None:
    args = parse_args()
    ensure_directories()
    write_download_instructions()
    create_synthetic_dataset(MINI_PATH, n_genes=200, seed=args.seed)
    create_synthetic_dataset(VALIDATION_PATH, n_genes=2500, seed=args.seed + 1)

    geo_status = (
        check_geo_supplementary()
        if args.check_geo
        else {"url": GEO_SUPPL_URL, "attempted": False, "result": "not_requested"}
    )
    real_files = sorted(str(path) for path in REAL_DIR.glob("*.h5ad"))
    geo_status["local_real_h5ad_files"] = real_files
    geo_status["fallback_mini"] = str(MINI_PATH)
    geo_status["validation_fixture"] = str(VALIDATION_PATH)
    ACQUISITION_PATH.write_text(json.dumps(geo_status, indent=2) + "\n")

    input_path, source = find_input(args.input, args.force_synthetic)
    print(f"Loading {input_path}")
    adata = ad.read_h5ad(input_path)
    schema = schema_audit(adata, input_path)
    adata, qc = run_qc(adata)
    hvg_count = normalize_and_select_hvg(adata)
    print(f"Highly variable genes: {hvg_count}")
    patients = patient_summary(adata)
    run_umap(adata, args.seed)
    adata.uns["phase1_qc"] = qc
    adata.uns["phase1_input"] = str(input_path)
    adata.uns["phase1_source_class"] = source
    adata.write_h5ad(PROCESSED_PATH, compression="gzip")

    input_size_kib = input_path.stat().st_size / 1024
    source_display = f"{source}, {input_size_kib:.0f} KiB"
    box = completion_box(SCANPY_VERSION, source_display, schema, qc, patients)
    write_report(box, input_path, source, schema, qc, patients)
    print(box)


if __name__ == "__main__":
    main()
