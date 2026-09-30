"""Build the author-review package without modifying the paper sources."""

from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT.parent
WORD = PAPER / "corrected_submission_2026-09"
OUT = PAPER / "Lupus_Paper_Corrected_2026-09_v3.zip"


def main() -> None:
    files: dict[str, Path] = {}
    for path in sorted(WORD.glob("*Corrected_2026-09.docx")):
        files[f"Word/{path.name}"] = path
    for ext in ("tiff", "pdf"):
        for path in sorted((ROOT / "figures/correction_2026-09").glob(f"*.{ext}")):
            files[f"Figures/{path.name}"] = path
    for path in sorted((ROOT / "manuscript_drafts/correction_2026-09").glob("*.pdf")):
        files[f"Readable_drafts/{path.name}"] = path
    for path in sorted((ROOT / "kaggle_notebooks").glob("CBC_Kaggle_*.ipynb")):
        files[f"Kaggle_notebooks_future_runs/{path.name}"] = path
    names = (
        "corrected_v1_shared_analysis.json",
        "corrected_v1_native_analysis.json",
        "corrected_v1_descriptive.json",
        "corrected_v1_gene_input_sensitivity.json",
        "external_age_source_sensitivity.json",
        "external_source_to_gsm_crosswalk.csv",
        "corrected_artifact_manifest.json",
    )
    for name in names:
        files[f"Results/{name}"] = ROOT / "results/correction_2026-09" / name
    files["Report/Lupus_Correction_Implementation_Report_2026-09-30.md"] = PAPER / "Lupus_Correction_Implementation_Report_2026-09-30.md"
    files["Report/REPORTING_AND_BIAS_REVIEW.md"] = ROOT / "docs/REPORTING_AND_BIAS_REVIEW.md"
    files["Report/CORRECTION_RUNBOOK.md"] = ROOT / "docs/CORRECTION_RUNBOOK.md"
    if len(list(WORD.glob("*Corrected_2026-09.docx"))) != 5:
        raise ValueError("expected five Word documents")
    for name, path in files.items():
        if not path.is_file():
            raise FileNotFoundError(f"{name}: {path}")
    readme = (
        "Lupus paper scientific correction — author-review package v3 (30 September 2026)\n\n"
        "The corrected shared-gene Geneformer external AUROC is 0.7344; the "
        "prespecified superiority criteria were not met. This is corrected "
        "reanalysis of a previously examined external cohort.\n\n"
        "Word/ contains five editable drafts. Readable_drafts/ contains the "
        "manuscript and supplement PDFs. Figures/ contains four TIFFs and "
        "four vector PDF masters, including Figure 4's in-image legend. "
        "Results/ contains key machine-readable results and the source-age "
        "sensitivity. Report/ gives the full chronology, reporting audit, and "
        "runbook. Kaggle_notebooks_future_runs/ contains a later provenance "
        "revision that has been syntax-checked locally but has not been rerun "
        "on Kaggle. The four completed original Kaggle ZIPs are held separately.\n\n"
        "The study supplement workbook was unavailable for independent age-43 "
        "verification. GEO age 50 remains the primary value. The author must "
        "review the scientific wording and declarations before journal submission.\n"
    ).encode()
    checksums = []
    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        archive.writestr("README.txt", readme)
        checksums.append(f"{hashlib.sha256(readme).hexdigest()}  README.txt")
        for name, path in sorted(files.items()):
            data = path.read_bytes()
            archive.writestr(name, data)
            checksums.append(f"{hashlib.sha256(data).hexdigest()}  {name}")
        archive.writestr("SHA256SUMS.txt", "\n".join(checksums) + "\n")
    with zipfile.ZipFile(OUT) as archive:
        for line in archive.read("SHA256SUMS.txt").decode().splitlines():
            digest, name = line.split("  ", 1)
            if hashlib.sha256(archive.read(name)).hexdigest() != digest:
                raise ValueError(f"package checksum mismatch: {name}")
    print(f"{OUT} ({OUT.stat().st_size} bytes; {len(files)} files plus README and checksums)")


if __name__ == "__main__":
    main()
