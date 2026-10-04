# Project Status — corrected release preparation

## Current result

The authoritative corrected shared-gene external AUROCs are Geneformer V1 **0.7344**, pseudobulk **0.8984**, and age-only **0.5781**. Neither prespecified Geneformer-superiority criterion was met.

## Claim boundary

This repository now describes the external analysis as a **corrected reanalysis on an already examined cohort**. It is not a new untouched confirmatory validation. No clinical-use, diagnostic-readiness, treatment, or deployment claim is supported.

The historical release commit `6158a8409064ae8c7a608126cc2d7a7e65b02506` remains unchanged.

## Repository cleanup

Legacy material has been moved under `archive/`: `state/`, `reports/`, `kaggle_kernels/`, numbered early docs (00–12), scripts 00–13, `run_stage7_*`, Stage-7/flare evaluation code and tests, and the historical `MANUSCRIPT.md`.

Duplicate script numbers were removed while preserving the active corrected sequence. The former secondary scripts are now:
- `38_prepare_word_working_drafts.py`
- `42_historical_accounting.py`
- `43_v1_gpu_fixture.py`
- `44_build_colab_notebook.py`
- `45_build_kaggle_notebooks.py`

## Reproducibility

The release gate runs `scripts/37_reproduce_corrected_results.sh` from a fresh GitHub Actions checkout using Python 3.11 dependencies resolved through `uv`. A release is created only after that reproduction passes.

## Large data / Zenodo

The three large historical pseudobulk parquet files total about 164 MB:
- `results/l2_dev_pseudobulk_counts.parquet`
- `results/l2_dev_pseudobulk_counts_restricted.parquet`
- `results/l2_sealed_pseudobulk_counts.parquet`

They remain in the `v2-corrected` release snapshot so Zenodo can archive them, then they are removed from `main` without rewriting Git history. The new version-specific Zenodo DOI is recorded here, in `README.md`, and in `CITATION.cff` after ingestion completes.
