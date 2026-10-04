# Changelog

## 2.0.0 — Corrected publication package

- Corrected Geneformer V1 extraction/scoring provenance.
- Reported corrected shared-gene external AUROC 0.7344, with pseudobulk 0.8984 and age-only 0.5781.
- Replaced the historical equal-AUROC comparison procedure with paired DeLong inference plus Holm adjustment, retaining paired donor-bootstrap intervals.
- Added shared-gene primary and model-native sensitivity analyses.
- Added fresh-checkout CPU reproduction checks and publication-focused CI.
- Reorganized the repository into reviewer-facing code, results, figures, notebooks, documentation, and a separate historical archive.
- Removed large historical pseudobulk parquet matrices from the active branch without rewriting their historical release snapshot.

## 1.0.0 — Historical archival release

Original archived analysis and manuscript-support snapshot. Retained for provenance; superseded for the corrected Geneformer-dependent results by v2.0.0.
