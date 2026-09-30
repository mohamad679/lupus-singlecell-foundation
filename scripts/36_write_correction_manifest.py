"""Hash the finalized correction artifacts without hashing this manifest itself."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORR = ROOT / "results/correction_2026-09"
PAPER = ROOT.parent
OUT = PAPER / "corrected_submission_2026-09"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def record(path: Path, relative_to: Path):
    if not path.is_file():
        raise FileNotFoundError(path)
    return {"path": str(path.relative_to(relative_to)), "bytes": path.stat().st_size,
            "sha256": digest(path)}


def main():
    result_names = [
        "corrected_v1_shared_predictions.json", "corrected_v1_native_predictions.json",
        "corrected_v1_shared_development_oof_predictions.json",
        "corrected_v1_native_development_oof_predictions.json",
        "corrected_v1_shared_analysis.json", "corrected_v1_native_analysis.json",
        "corrected_v1_gene_input_sensitivity.json", "corrected_v1_descriptive.json",
        "corrected_v1_shared_cohort_probe.json", "corrected_v1_shared_fit_report.json",
        "corrected_v1_native_fit_report.json", "corrected_v1_shared_fit.joblib",
        "corrected_v1_native_fit.joblib",
    ]
    feature_files = []
    for mode in ("shared", "native"):
        folder = CORR / f"{mode}_features"
        feature_files.extend(sorted(folder.glob("*.parquet")))
        feature_files.extend(sorted(folder.glob("*run_summary.json")))
        feature_files.extend(sorted(folder.glob("*ingestion_validation.json")))
    result_files = [CORR / name for name in result_names] + feature_files
    figures = sorted((ROOT / "figures/correction_2026-09").glob("*.tiff"))
    documents = sorted(OUT.glob("*Corrected_2026-09.docx"))
    if len(figures) != 4 or len(documents) != 5:
        raise ValueError("expected four final figures and five final Word documents")
    source_zip_names = ["dev_shared", "external_shared", "dev_native", "external_native"]
    zips = [PAPER / "correction_artifacts" / name / f"lupus_correction_{name}_share.zip"
            for name in source_zip_names]
    manifest = {
        "date": str(date.today()),
        "status": "corrected reanalysis on previously examined external cohort",
        "historical_release_commit": "6158a840",
        "repository_results": [record(p, ROOT) for p in result_files],
        "repository_figures": [record(p, ROOT) for p in figures],
        "paper_documents": [record(p, PAPER) for p in documents],
        "original_kaggle_zips_outside_git": [record(p, PAPER) for p in zips],
    }
    path = CORR / "corrected_artifact_manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(path)


if __name__ == "__main__":
    main()
