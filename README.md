# Lupus Single-Cell Foundation Model — corrected reanalysis

Donor-level SLE-versus-healthy benchmarking of corrected Geneformer V1 embeddings against pseudobulk and age baselines across the previously examined development/external cohorts.

## Current corrected result

| Arm | External AUROC |
|---|---:|
| Geneformer V1, shared-gene input | **0.7344** |
| Pseudobulk | **0.8984** |
| Age only | **0.5781** |

**Claim boundary:** this is a corrected reanalysis on an already examined external cohort, not a new untouched confirmatory validation. No clinical-use, diagnostic-readiness, treatment, or deployment claim is made.

The historical release is preserved at commit `6158a8409064ae8c7a608126cc2d7a7e65b02506`; it is not modified by this cleanup.

## Reproduce the corrected result

```bash
git clone https://github.com/mohamad679/lupus-singlecell-foundation.git
cd lupus-singlecell-foundation
bash scripts/37_reproduce_corrected_results.sh
```

The script creates an isolated `reproductions/correction-*` directory and checks donor-aligned probabilities, decision scores, AUROCs, and paired inference against the committed corrected artifacts.

## Data archive

The three large historical pseudobulk parquet files were removed from `main` without rewriting Git history and remain preserved in the `v2-corrected` GitHub release snapshot: https://github.com/mohamad679/lupus-singlecell-foundation/releases/tag/v2-corrected

Zenodo v2 DOI: pending minting/ingestion. The version-specific DOI will replace this line once Zenodo publishes the new version.

## Repository map

- `scripts/` — active corrected scoring, analysis, reproduction, reporting, and packaging code.
- `results/correction_2026-09/` — corrected donor features, predictions, analyses, and manifests.
- `kaggle_notebooks/` — self-contained corrected extraction notebooks.
- `docs/` — active correction, reproducibility, reporting, and limitations documentation.
- `figures/correction_2026-09/` — corrected figures.
- `manuscript_drafts/correction_2026-09/` — corrected manuscript/supplement drafts.
- `archive/` — legacy state, reports, Kaggle kernels, early docs/scripts, Stage-7 flare analysis, and the historical manuscript.
- `PREREG.md`, `FREEZE.json`, `SEALED_OPENED.json` — historical governance artifacts retained for traceability.

See `PROJECT_STATUS.md` and `docs/correction_2026-09_audit.md` for the scientific correction boundary and provenance.
