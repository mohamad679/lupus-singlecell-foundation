# Scientific correction ledger and reproducibility audit

**Dated 30 September 2026.** This is a corrected reanalysis of the already
examined GSE135779 cohort. The historical release at commit `6158a840` and the
original preregistered decision rule remain preserved. Results below do not
constitute a new untouched confirmatory validation.

## Result status and claim trace

| Claim | Status | Source |
|---|---|---|
| Historical Geneformer 0.9676 development / 0.8156 external | Reproducible from released vectors, representation invalid for standard V1 claims | `results/l2_dev_sle_vs_healthy.csv`, `results/l2_sealed_results.json`, `results/correction_2026-09/historical_scores_analysis.json` |
| Historical co-primary label-permutation p values | Retained only as historical above-chance label-shuffle results; not equal-AUROC tests | `results/l2_coprimary_difference_ci.json`, `results/l2_sealed_results.json` |
| Corrected V1 shared-gene Geneformer development AUROC 0.9746 (95% CI 0.9548–0.9901), external 0.7344 (0.6017–0.8597) | Corrected main analysis | `results/correction_2026-09/corrected_v1_descriptive.json`, `corrected_v1_shared_predictions.json` |
| Corrected external pseudobulk 0.8984 and age 0.5781 | Reused regenerated historical comparator probabilities after exact donor-key and label checks; new descriptive CIs use the corrected report's bootstrap convention | `corrected_v1_shared_analysis.json`, `corrected_v1_descriptive.json` |
| Geneformer minus age +0.1563 (95% paired CI −0.0859 to +0.4040; Holm p 0.2046) | Corrected co-primary A; superiority criterion not met | `corrected_v1_shared_analysis.json:comparisons.geneformer_vs_age` |
| Geneformer minus pseudobulk −0.1641 (−0.2916 to −0.0384; Holm p 0.0175) | Corrected co-primary B; positive Geneformer-superiority criterion not met | `corrected_v1_shared_analysis.json:comparisons.geneformer_vs_pseudobulk` |
| Native-input Geneformer external 0.7484; native minus shared +0.0141 (−0.0238 to +0.0597; paired DeLong p 0.4601) | Exploratory sensitivity on the same donors | `corrected_v1_native_analysis.json`, `corrected_v1_gene_input_sensitivity.json` |
| 261 development donors / 1,263,676 cells and 56 external samples / 363,083 cells | Validated extraction accounting in both gene-input modes | `shared_features/*_run_summary.json`, `native_features/*_run_summary.json` and ingestion validations |
| 30,165 shared genes; 490 development-zero genes expressed externally | Descriptive gene availability, not a causal explanation | `historical_gene_availability.json` |
| Corrected Geneformer cohort-origin AUROC 0.9999 | Post-hoc feature-space diagnostic, not SLE prediction | `corrected_v1_shared_cohort_probe.json` |

The source-defined external `Children` category has 44 samples, including six
aged 18 and one aged 19. The `Adult` category has 12 samples. The paper uses
these source labels for stratified results rather than inventing a pediatric
cut-off. The adult stratum has only seven cases and five controls; 10 of 5000
bootstrap draws were single-class and discarded.

## Feature provenance

The four executed notebooks are in `kaggle_notebooks/CBC_Kaggle_{1..4}_*.ipynb`.
Each run output passed `scripts/35_ingest_corrected_kaggle_zip.py`: manifest and
member hashes, V1 fixture, finite 256-dimensional donor vectors, distinct donor
keys, expected donor and cell counts, and no missing donors. The development and
external V1 extraction summaries record the same pinned Geneformer revision,
checkpoint file SHA-256 hashes, dictionary identity, input mode, `emb_mode=cell`,
`emb_layer=-1`, `model_version=V1`, `model_input_size=2048`, and full runtime
package lists. ZIP originals are retained in the paper workspace outside Git.

The corrected scoring code rejects embedding hash mismatch, donor-key or label
misalignment, mismatched dimensions, non-finite vectors/probabilities, and
inconsistent checkpoint provenance. The direct native/shared comparison also
checks equality of baseline probabilities. Per-donor predicted probabilities
and development out-of-fold predictions are versioned with analysis JSON files.
The bootstrap intervals condition on these fixed predictions and do not include
the full variation from retraining or extraction.

## Reproduce the feature-to-result path

Use Python 3.11 with `requirements_correction_scoring.txt` (or `uv run
--no-project --with-requirements requirements_correction_scoring.txt`). From
repository root, execute in order:

1. Re-extract raw cells in Kaggle with the four checked-in notebooks, if raw
   Census/GEO access and GPU are available. Each notebook emits a share ZIP.
2. Validate each ZIP with `scripts/35_ingest_corrected_kaggle_zip.py --zip ZIP
   --job dev_shared|external_shared|dev_native|external_native --output-dir DIR`.
3. Run `scripts/28_corrected_geneformer_scoring.py` separately with matching
   `--dev-embeddings`, `--external-embeddings`, `--dev-summary`,
   `--external-summary`, and `--mode shared|native`, writing to a new output
   directory. Then run `scripts/27_correction_analysis.py` for each mode.
4. Run `scripts/29_gene_input_sensitivity.py` with the two prediction JSON
   files; `scripts/30_corrected_descriptive.py` and
   `scripts/31_corrected_cohort_probe.py` for descriptive results and the
   corrected diagnostic; `scripts/32_corrected_figures.py` for four figures.
5. Run `scripts/33_build_corrected_documents.py` with the five preserved Word
   working drafts in the parent paper directory, using a Python environment
   with `python-docx`. Inspect rendered DOCX pages before submission.

The versioned run summaries are the authoritative lock for Kaggle packages and
checkpoint/dictionary hashes. `requirements_correction_scoring.txt` locks the
local scientific scoring environment. Figures were generated with Matplotlib
3.11.2; the built-in document runtime supplied `python-docx` for Word editing.
`results/correction_2026-09/corrected_artifact_manifest.json` hashes the final
prediction, analysis, figure, and document artifacts.

## Reporting and bias audit

The [TRIPOD+AI statement](https://www.bmj.com/content/385/bmj-2023-078378)
provides reporting recommendations for development and evaluation of prediction
models. This revision identifies the study as a corrected reanalysis in the
title/abstract and Methods; describes data sources, eligibility, donor-level
outcome, predictors, missing age handling, fitting, internal and external
validation, calibration, participant counts, uncertainty, open code, and
limitations. A full independent item-by-item checklist remains a submission
task. Intended clinical use, prediction threshold, and decision-curve utility
were not specified or evaluated; the manuscript therefore makes no clinical
diagnostic claim. Calibration intervals are diagnostic Wald intervals on fixed
external scores. The original public dataset discrepancy (56 versus 58 records)
and unavailable external sex/ancestry data remain unresolved.

The [PROBAST+AI tool](https://www.bmj.com/content/388/bmj-2024-082505) informs
our author-conducted assessment. Participant applicability is limited by the
adult development versus source-Children-heavy external sample, platform and
protocol differences, and one small external cohort. Predictor measurement is
affected by reference-gene availability and previously invalid V1 extraction,
now corrected and versioned. The outcome uses public source SLE/control labels;
clinical ascertainment harmonization across cohorts is not independently
verified. Analysis concerns include corrected decisions after external outcomes
were examined, broad uncertainty for n=56, unknown foundation-model pretraining
overlap, and no third cohort. Overall risk of bias for a clinical-use claim is
high and clinical applicability is uncertain. This is an author assessment, not
an independent PROBAST+AI adjudication.

## Remaining scientific boundary

No new untouched external cohort, broader encoder benchmark, cell-type-resolved
validation, independent pretraining-overlap audit, or clinical utility analysis
was performed. The corrected conclusions are restricted to Geneformer V1-10M
cell embeddings pooled per donor, the recorded classifiers, and these cohorts.
