# AGENTS.md — Lupus Single-Cell Foundation Model

## Project mission

This repository is being converted from exploratory Kaggle notebooks into a reproducible, tested, publication-grade computational biology pipeline.

The scientific goal is patient-level discrimination of active systemic lupus erythematosus (SLE) flare from managed SLE using peripheral blood single-cell RNA-seq data and frozen single-cell foundation-model embeddings.

The current preferred framing is:

Frozen Geneformer embeddings encode patient-level transcriptional structure sufficient to discriminate active SLE flare from managed SLE in a large PBMC single-cell cohort.

Do not frame the project as future flare prediction unless longitudinal pre-flare samples are added.

## Current status

The repository is in Stage 0: repository reconciliation.

Exploratory work has been completed outside the clean production pipeline:

- CELLxGENE Census loading of the GSE174188 / Perez et al. lupus PBMC cohort
- donor-level label extraction
- per-patient Geneformer embedding extraction
- preliminary patient-level Logistic Regression evaluation
- preliminary permutation and confounder checks

These results are promising but remain exploratory until regenerated from clean scripts with tests, manifests, saved predictions, and versioned metrics.

## Non-negotiable scientific rules

1. Do not claim future flare prediction.
   The current analysis is cross-sectional active flare discrimination.

2. Do not claim fully zero-shot clinical prediction.
   Correct wording: zero-shot Geneformer feature extraction with supervised patient-level linear evaluation.

3. Do not use cell-level train/test splits.
   All modeling and validation must be donor/patient-level.

4. Do not report p-value as 0.0000.
   Use finite permutation correction, for example (k + 1) / (n + 1), and report p < 0.001 when appropriate.

5. Do not fit preprocessing outside cross-validation folds.
   Scaling, PCA, feature selection, and thresholds must be learned inside training folds only.

6. Do not overstate Geneformer improvement.
   Raw/pseudobulk baselines are strong and must be reported honestly.

7. Do not treat GSE137029 as external validation until patient/sample mapping, label provenance, and donor overlap are audited.

8. Do not commit large raw data, h5ad files, model weights, or embedding arrays unless explicitly approved.
   Use manifests, checksums, and documented external storage instead.

## Current primary dataset

Primary exploratory cohort:

- Accession: GSE174188
- Source used in exploratory work: CELLxGENE Census
- CELLxGENE dataset_id: 218acb0f-9f2f-4f76-b90b-15a4b7c7f629
- Census version used in exploratory notebooks: 2025-11-08

Working donor_id label rule:

- FLARE* -> Flare
- HC-* or IGTB* -> Healthy
- numeric donor IDs -> Managed SLE

This rule must be formalized in code and covered by tests.

## Required production pipeline design

Target package layout:

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

## Engineering rules

1. Work on feature branches only.
   Do not work directly on main.

2. Keep changes small and reviewable.
   Each commit should have one purpose.

3. Prefer scripts and modules over notebooks.
   Notebooks are allowed for exploration, not as the final reproducible pipeline.

4. Every production result must have a saved artifact.
   Metrics should be saved as JSON/CSV.
   Predictions should be saved as CSV.
   Model comparisons should be saved as tables.
   Figures should be generated from saved result files.

5. Every important data transformation must be testable.
   Label extraction, QC, embedding integrity, patient splits, and metrics must have tests.

6. Avoid hard-coded Kaggle or local machine paths in production code.
   Use config files and command-line arguments.

7. Do not silently overwrite existing result files.
   Either version outputs or require explicit overwrite flags.

8. Do not add generated caches or system files to Git.
   Keep .DS_Store, .venv, __pycache__, and cache folders ignored.

## Immediate allowed work for Stage 0

Allowed:

- update documentation
- update project state files
- add AGENTS.md
- clarify roadmap and scientific framing
- remove irrelevant system files from Git tracking

Not allowed in Stage 0:

- new modeling
- new external validation
- large data downloads
- converting all notebooks into scripts
- changing reported scientific results

## Next stage after Stage 0

Stage 1 should create the package skeleton and convert Phase 1 label/QC logic into tested Python modules.

The first production tests should cover:

- FLARE001 -> Flare
- HC-546 -> Healthy
- IGTB670 -> Healthy
- 1132 -> Managed
- patient summary row count equals unique donor_id count
- mitochondrial QC uses validated gene metadata
- no patient appears in multiple labels

## Final publication direction

The paper should be framed as a reproducible benchmark of frozen single-cell foundation-model embeddings for patient-level SLE activity discrimination.

The paper should not be framed as a ready clinical predictor unless external validation, calibration, and clinical decision analysis are added.
