# Project Status — Lupus Single-Cell Foundation Model

## Current scientific objective

The project investigates whether frozen single-cell foundation-model representations can support patient-level discrimination of active SLE flare from managed SLE using peripheral blood single-cell RNA-seq data.

The current working framing is:

> Frozen Geneformer embeddings encode patient-level transcriptional structure sufficient to discriminate active SLE flare from managed SLE in a large PBMC single-cell cohort.

This project must not be framed as future flare prediction unless longitudinal pre-flare samples are added. The current task is active flare discrimination.

---

## Primary dataset

Primary cohort:

- Dataset: GSE174188 / Perez et al. lupus PBMC single-cell RNA-seq cohort
- Source used in exploratory work: CELLxGENE Census
- CELLxGENE dataset_id: `218acb0f-9f2f-4f76-b90b-15a4b7c7f629`
- Census version used in exploratory notebooks: `2025-11-08`
- Approximate exploratory cohort size:
  - 1,263,438 cells after initial loading/QC record
  - 261 donors/patients
  - 14 Flare
  - 149 Managed SLE
  - 98 Healthy

Working label rule from `donor_id`:

- `FLARE*` -> Flare
- `HC-*` or `IGTB*` -> Healthy
- numeric donor IDs -> Managed SLE

This label rule is currently exploratory and must be formalized, tested, and documented before publication claims.

---

## Current repository mismatch

The repository currently contains historical scaffold and synthetic Phase 1 validation artifacts.

Important mismatch:

- The checked-in Phase 1 report currently represents a synthetic validation fixture.
- The real GSE174188/CELLxGENE exploratory analysis was performed in Kaggle notebooks.
- The repository state files still contain old gate/blocker language that does not yet reflect the real exploratory Kaggle results.

Therefore, the immediate priority is repository reconciliation before additional modeling.

---

## Completed exploratory work outside the clean pipeline

### Phase 1 — exploratory dataset loading and QC

Exploratory Kaggle notebook:

- `notebooks/phase1_kaggle.ipynb`

Known outputs from exploratory run:

- `patient_summary.csv`
- `lupus_phase1_processed.h5ad` outside repo/Kaggle environment

Known issue to fix in production pipeline:

- mitochondrial QC must use validated gene symbols or correct feature metadata
- Census `var_names` / `feature_id` handling must be tested

---

### Phase 2 — exploratory Geneformer embedding extraction

Exploratory output:

- 261 per-patient `.npy` embedding files
- expected shape per patient: `(300, 1152)`
- dtype: `float32`

Geneformer details from exploratory run:

- Model: `ctheodoris/Geneformer`
- Architecture: BERT-style model
- Hidden size: 1152
- Vocab size must come from `model.config.vocab_size`
- Observed config vocab size: 20275
- Max sequence length used: 1024
- Cells per patient: 300
- Batch size: 16

Critical production requirements:

- create an embedding manifest
- record sampled cell IDs
- record random seed
- record model/config/vocabulary hashes
- test that token IDs are below model vocab size
- test that all embeddings are finite and match patient metadata

---

### Phase 3 — exploratory classification and validation

Exploratory task:

- Patient-level binary classification
- Mean pooling over per-cell Geneformer embeddings
- Logistic Regression classifier
- Leave-one-out cross-validation

Exploratory results:

| Task | AUROC | Sensitivity |
|---|---:|---:|
| Flare vs Healthy | ~0.993 | 12/14 |
| Flare vs Managed | ~0.996 | 14/14 |

Exploratory controls:

- permutation testing
- female-only control
- ancestry-stratified checks
- raw/pseudobulk baseline comparison

Known production fixes required:

- StandardScaler must be inside each cross-validation fold
- p-values must use a finite permutation correction, not be reported as 0.0000
- raw/pseudobulk baseline must be reproducible from script
- predictions and metrics must be saved as versioned artifacts
- confidence intervals must be added
- confounder controls must be formalized

---

## Main scientific risk

The main risk is not lack of signal. The main risk is overclaiming.

Geneformer appears to perform strongly, but the raw/pseudobulk baseline is also very strong. Therefore, the paper cannot rely only on a small AUROC improvement.

The final paper must answer:

1. Does frozen Geneformer provide incremental value beyond raw/pseudobulk expression?
2. Is the signal driven by within-cell-type transcriptional state, cell-type composition, or both?
3. Is performance robust to sex, ancestry, cell-count, and composition confounding?
4. Can the signal generalize under external or dataset-shift validation?

---

## Current target paper framing

Preferred framing:

> A reproducible benchmark of frozen single-cell foundation-model embeddings for patient-level SLE activity discrimination.

Avoid framing:

> A clinical future flare prediction model.

Avoid claiming:

> Fully zero-shot flare prediction.

Correct wording:

> Zero-shot Geneformer feature extraction with supervised patient-level linear evaluation.

---

## Immediate engineering plan

Stage 0: Repository reconciliation

- stop tracking system files
- add this project status file
- update README to distinguish historical synthetic artifacts from real exploratory Kaggle results
- update project state files so they no longer contradict the exploratory modeling work
- move notebooks into exploratory/final structure if needed

Stage 1: Convert notebooks into package-based scripts

- `src/lupusfm/data/`
- `src/lupusfm/qc/`
- `src/lupusfm/geneformer/`
- `src/lupusfm/eval/`
- `scripts/10_run_phase1_qc.py`
- `scripts/20_extract_geneformer_embeddings.py`
- `scripts/30_evaluate_geneformer.py`

Stage 2: Add tests and reproducibility artifacts

- label extraction tests
- QC tests
- embedding manifest tests
- split/leakage tests
- metric reproducibility tests

Stage 3: Add biological validation

- raw/pseudobulk baselines
- cell-type contribution
- composition controls
- external validation audit

---

## Current Stage 1 package progress

Completed on `main`:

- `src/lupusfm/data/labels.py`
- `tests/test_lupusfm_labels.py`
- `src/lupusfm/data/metadata.py`
- `tests/test_lupusfm_metadata.py`
- `src/lupusfm/qc/mitochondrial.py`
- `tests/test_lupusfm_mitochondrial.py`

In progress on `feat/stage1-cohort-summary`:

- `src/lupusfm/data/cohort.py`
- `tests/test_lupusfm_cohort.py`

Current targeted validation:

- `59 passed` for labels, metadata extraction, mitochondrial annotation, and cohort summary tests.

Important safety decisions now implemented:

- donor metadata must come from explicit `adata.obs` columns
- unknown donor-id patterns fail closed
- mitochondrial annotation requires an explicit gene-symbol column
- mitochondrial annotation refuses silent fallback to `adata.var_names`
- cohort summaries count donors and cells only; they do not filter, embed, or train

## Current next action

Finish the small Stage 1 cohort summary pull request, then continue with additional production-safe ingestion/QC utilities before any embedding extraction or modeling.
