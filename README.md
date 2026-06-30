# Lupus Single-Cell Foundation Model

Patient-level benchmarking of frozen single-cell foundation-model embeddings for active systemic lupus erythematosus (SLE) flare discrimination from peripheral blood single-cell RNA-seq.

## Scientific objective

This project investigates whether frozen single-cell foundation-model representations, especially Geneformer embeddings, can support patient-level discrimination of active SLE flare from managed SLE.

The current working claim is intentionally conservative:

> Frozen Geneformer embeddings encode patient-level transcriptional structure sufficient to discriminate active SLE flare from managed SLE in a large PBMC single-cell cohort.

This project should not currently be described as future flare prediction. The available primary analysis is cross-sectional active flare discrimination, not longitudinal pre-flare forecasting.

## Current status

This repository is being reconciled from an exploratory Kaggle/notebook project into a reproducible, testable, publication-grade computational biology pipeline.

Current exploratory evidence exists for:

- CELLxGENE Census loading of the Perez et al. lupus PBMC cohort
- patient-level label extraction from donor_id
- per-patient Geneformer embedding extraction
- patient-level logistic-regression evaluation
- preliminary permutation and confounder controls

However, the project is not yet publication-ready because the exploratory notebooks must be converted into scripts, tests, manifests, and reproducible result artifacts.

For the detailed current state, see:

- PROJECT_STATUS.md

## Primary dataset

Primary exploratory cohort:

- Dataset: GSE174188 / Perez et al. lupus PBMC single-cell RNA-seq cohort
- Source used in exploratory work: CELLxGENE Census
- CELLxGENE dataset_id: 218acb0f-9f2f-4f76-b90b-15a4b7c7f629
- Census version used in exploratory notebooks: 2025-11-08

Exploratory donor grouping rule:

- FLARE* -> Flare
- HC-* or IGTB* -> Healthy
- numeric donor IDs -> Managed SLE

This label rule must be formalized and tested before final publication claims.

## Important repository note

Earlier versions of this repository contained historical planning scaffolds and synthetic Phase 1 validation artifacts. Those files are retained for provenance, but they should not be interpreted as the final scientific pipeline.

The checked-in historical Phase 1 synthetic report validates local pipeline mechanics only. It is not evidence about the real Perez et al. cohort.

The active engineering priority is to reconcile the repository with the real exploratory Kaggle/CELLxGENE work and then convert the notebooks into a clean package-based workflow.

## Exploratory results summary

Preliminary patient-level Geneformer mean-pooling results from exploratory notebooks:

| Task | AUROC | Sensitivity |
|---|---:|---:|
| Flare vs Healthy | ~0.993 | 12/14 |
| Flare vs Managed | ~0.996 | 14/14 |

These values are exploratory. Final reported values must be regenerated from clean scripts with saved predictions, confidence intervals, leakage checks, and versioned metrics.

## Main scientific risk

The key risk is overclaiming.

The preliminary Geneformer performance is strong, but raw/pseudobulk expression baselines are also strong. Therefore, the final paper must answer whether frozen foundation-model embeddings provide meaningful incremental value beyond simpler baselines.

The final analysis must address:

1. Geneformer vs raw/pseudobulk/PCA baselines
2. donor-level leakage prevention
3. sex and ancestry controls
4. cell-count and cell-type-composition confounding
5. cell-type contribution analysis
6. external validation or dataset-shift robustness

## Planned production pipeline

Target structure:

    src/lupusfm/
      data/
      qc/
      geneformer/
      eval/
      reporting/

    scripts/
      10_run_phase1_qc.py
      20_extract_geneformer_embeddings.py
      30_evaluate_geneformer.py
      31_evaluate_raw_baseline.py
      40_celltype_contribution.py
      50_external_validation_audit.py

    configs/
      phase1_census.yaml
      phase2_geneformer.yaml
      phase3_eval.yaml

    tests/
      test_labels.py
      test_qc.py
      test_embeddings.py
      test_splits.py
      test_metrics.py

## Immediate roadmap

### Stage 0 — Repository reconciliation

- remove system files from Git tracking
- document current real project status
- update README and state files
- separate historical synthetic artifacts from active exploratory results

### Stage 1 — Package-based Phase 1 pipeline

- build CELLxGENE Census loader
- formalize donor label extraction
- fix and test mitochondrial QC
- generate reproducible patient summary

### Stage 2 — Geneformer embedding pipeline

- convert notebook extraction into scripts
- create embedding manifest
- record sampled cell IDs and random seed
- test vocabulary bounds and embedding integrity

### Stage 3 — Evaluation pipeline

- rebuild LOOCV evaluation with leakage-safe preprocessing
- save predictions and metrics
- add AUPRC, bootstrap confidence intervals, and corrected permutation p-values

### Stage 4 — Baselines and biological interpretation

- raw/pseudobulk baseline
- PCA baseline
- cell-type contribution analysis
- composition controls

### Stage 5 — External validation gate

- audit GSE137029 or alternative cohorts
- verify patient/sample mapping
- check donor overlap and label provenance
- run external or dataset-shift validation only after passing the audit

## Reproducibility status

Current reproducibility level:

- exploratory notebooks: available
- clean scripts: in progress
- tests: in progress
- embedding manifest: pending
- external validation: pending

## Development workflow

Work should happen on feature branches, not directly on main.

Each branch should make a small, reviewable change:

1. documentation/state reconciliation
2. package structure
3. Phase 1 pipeline
4. Phase 2 embedding pipeline
5. Phase 3 evaluation pipeline
6. baselines and biological validation
7. external validation audit
