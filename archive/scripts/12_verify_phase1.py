#!/usr/bin/env python3
"""Strictly verify every Phase 1 acceptance artifact."""

from __future__ import annotations

import json
import os
from importlib.metadata import version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache" / "matplotlib"))

import anndata as ad
import pandas as pd
import scanpy as sc


RESULTS = ROOT / "results" / "phase1"
PROCESSED = ROOT / "data" / "processed" / "lupus_qc_processed.h5ad"


def require_nonempty(path: Path, minimum_bytes: int = 1) -> None:
    if not path.is_file() or path.stat().st_size < minimum_bytes:
        raise AssertionError(f"Missing or empty artifact: {path}")


def main() -> None:
    import_checks = {
        "scanpy": version("scanpy"),
        "anndata": version("anndata"),
    }
    mini = ad.read_h5ad(ROOT / "data" / "raw" / "mini_test.h5ad", backed="r")
    assert tuple(mini.shape) == (500, 200), mini.shape
    mini.file.close()
    require_nonempty(ROOT / "data" / "raw" / "DOWNLOAD_INSTRUCTIONS.md", 500)

    schema = json.loads((RESULTS / "schema_map.json").read_text())
    assert schema["patient_id_confirmed"] is True
    assert schema["canonical_fields"]["patient_id"]["source_column"]
    assert schema["unique_patients"] > 0

    for name in (
        "qc_violin.png",
        "qc_scatter.png",
        "umap_by_group.png",
        "umap_by_celltype.png",
    ):
        require_nonempty(RESULTS / name, 1_000)

    processed = ad.read_h5ad(PROCESSED)
    assert int(processed.var["highly_variable"].sum()) == 2000
    assert processed.n_obs < schema["n_obs"]
    assert processed.n_vars <= schema["n_vars"]
    assert {"counts", "normalized", "log_normalized"}.issubset(processed.layers.keys())
    assert "X_umap" in processed.obsm

    patients = pd.read_csv(RESULTS / "patient_summary.csv")
    assert list(patients.columns) == [
        "patient_id",
        "group",
        "sledai_score",
        "n_cells",
        "cell_types_present",
    ]
    assert len(patients) == processed.obs["patient_id"].nunique()
    assert patients["patient_id"].is_unique
    assert patients["group"].nunique() >= 2
    assert patients["n_cells"].sum() == processed.n_obs

    report_path = RESULTS / "PHASE1_REPORT.md"
    require_nonempty(report_path, 1_000)
    report = report_path.read_text()
    assert "STATUS: PHASE 1 COMPLETE ✅" in report
    assert "NEXT: Phase 2 — Geneformer Embedding" in report

    verification = {
        "status": "pass",
        "imports": import_checks,
        "mini_shape": [500, 200],
        "processed_shape": list(processed.shape),
        "highly_variable_genes": 2000,
        "patients": len(patients),
        "groups": sorted(patients["group"].unique().tolist()),
        "artifacts_verified": 10,
    }
    (RESULTS / "verification.json").write_text(json.dumps(verification, indent=2) + "\n")
    print(json.dumps(verification, indent=2))


if __name__ == "__main__":
    main()
