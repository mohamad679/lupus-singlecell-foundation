# Computational methods

This file is a compact code-to-method map for reviewers. The manuscript remains the authoritative scientific description.

## 1. Corrected Geneformer scoring

`scripts/02_score_corrected_models.py` validates the pinned Geneformer V1 extraction summaries and feature checksums, aligns development/external donors, reruns the originally recorded nested-CV regularization-selection rule on corrected development embeddings, fits the final donor-level logistic model, and scores the previously examined external cohort.

Primary representation: corrected V1 shared-gene input. Sensitivity representation: corrected V1 model-native input.

## 2. Statistical analysis

`scripts/01_statistical_analysis.py` computes fixed-prediction probability metrics and paired model comparisons. Pairwise AUROC comparisons use paired DeLong inference; paired donor bootstrap intervals are retained; multiplicity is handled with Holm adjustment.

## 3. Gene-input sensitivity

`scripts/03_gene_input_sensitivity.py` compares shared-gene and model-native Geneformer representations on exactly aligned external donors. This is exploratory sensitivity analysis on the same already examined cohort.

## 4. Descriptive uncertainty

`scripts/04_descriptive_statistics.py` computes 5,000-draw donor bootstrap AUROC intervals for overall and source-defined age strata using fixed predictions.

## 5. Cohort-membership diagnostic

`scripts/05_cohort_probe.py` quantifies development-versus-external separability in the corrected shared-gene representation. It is a post-hoc distribution-shift diagnostic and does not predict SLE labels.

## 6. Figures

`scripts/06_generate_figures.py` regenerates the four publication figures from the committed corrected results.

## 7. Independent reproduction check

`scripts/07_compare_reproduction.py` verifies a fresh CPU rerun against the published corrected package. Cross-platform LBFGS/BLAS differences are handled with explicit numeric tolerances while requiring unchanged reported discrimination and paired inference.

## Extraction environment

The four notebooks in `notebooks/extraction/` document the GPU extraction path and pin the Geneformer source revision. CPU reproduction of the reported corrected scoring results does not require rerunning the full cell-level GPU extraction.
