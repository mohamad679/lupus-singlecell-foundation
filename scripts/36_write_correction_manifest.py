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
        "external_age_source_sensitivity.json", "external_source_to_gsm_crosswalk.csv",
    ]
    feature_files = []
    for mode in ("shared", "native"):
        folder = CORR / f"{mode}_features"
        feature_files.extend(sorted(folder.glob("*.parquet")))
        feature_files.extend(sorted(folder.glob("*run_summary.json")))
        feature_files.extend(sorted(folder.glob("*ingestion_validation.json")))
    result_files = [CORR / name for name in result_names] + feature_files
    figure_dir = ROOT / "figures/correction_2026-09"
    figures = sorted(figure_dir.glob("*.tiff")) + sorted(figure_dir.glob("*.pdf"))
    documents = sorted(OUT.glob("*Corrected_2026-09.docx"))
    if len(figures) != 8 or len(documents) != 5:
        raise ValueError("expected four TIFF/PDF figure pairs and five final Word documents")
    source_records = sorted((ROOT / "docs/source_records").glob("*.txt"))
    if len(source_records) != 2:
        raise ValueError("expected dated GEO series and sample records")
    code_files = [
        ROOT / "scripts/correction_protocol.py",
        ROOT / "scripts/28_corrected_geneformer_scoring.py",
        ROOT / "scripts/27_correction_analysis.py",
        ROOT / "scripts/32_corrected_figures.py",
        ROOT / "scripts/33_build_corrected_documents.py",
        ROOT / "scripts/35_ingest_corrected_kaggle_zip.py",
        ROOT / "scripts/36_write_correction_manifest.py",
        ROOT / "scripts/37_reproduce_corrected_results.sh",
        ROOT / "scripts/39_external_metadata_reconciliation.py",
        ROOT / "scripts/40_compare_corrected_results.py",
        ROOT / "scripts/41_package_submission.py",
        ROOT / "requirements_correction_scoring.txt",
        ROOT / "requirements_correction_kaggle_extraction.txt",
    ] + sorted((ROOT / "kaggle_notebooks").glob("CBC_Kaggle_*.ipynb"))
    manuscript_drafts = sorted((ROOT / "manuscript_drafts/correction_2026-09").glob("*.pdf"))
    if len(manuscript_drafts) != 2:
        raise ValueError("expected manuscript and supplement PDF drafts")
    source_zip_names = ["dev_shared", "external_shared", "dev_native", "external_native"]
    zips = [PAPER / "correction_artifacts" / name / f"lupus_correction_{name}_share.zip"
            for name in source_zip_names]
    manifest = {
        "date": str(date.today()),
        "status": "corrected reanalysis on previously examined external cohort",
        "historical_release_commit": "6158a840",
        "repository_results": [record(p, ROOT) for p in result_files],
        "repository_figures": [record(p, ROOT) for p in figures],
        "repository_source_records": [record(p, ROOT) for p in source_records],
        "repository_code_at_manifest_date": [record(p, ROOT) for p in code_files],
        "repository_manuscript_drafts": [record(p, ROOT) for p in manuscript_drafts],
        "repository_report": record(ROOT / "docs/correction_2026-09_implementation_report.md", ROOT),
        "repository_reporting_audit": record(ROOT / "docs/REPORTING_AND_BIAS_REVIEW.md", ROOT),
        "paper_documents": [record(p, PAPER) for p in documents],
        "original_kaggle_zips_outside_git": [record(p, PAPER) for p in zips],
    }
    path = CORR / "corrected_artifact_manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(path)


if __name__ == "__main__":
    main()
