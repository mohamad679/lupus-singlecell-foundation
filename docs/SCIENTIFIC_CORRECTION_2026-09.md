# Scientific correction ledger — 29 September 2026

## Release boundary

The historical release is Git commit `6158a8409064ae8c7a608126cc2d7a7e65b02506`.
Its `FREEZE.json`, `SEALED_OPENED.json`, `results/l2_*` artifacts, original
Kaggle kernels, and preregistration remain unchanged in this correction branch.
All nine `FREEZE.json` file hashes match this copied historical checkout.
The original co-primary decision is retained as a historical outcome. New
work writes to `results/correction_2026-09/` and uses new extraction scripts.

The external cohort has already been examined. Every corrected result on
GSE135779 must be described as a **corrected reanalysis**, regardless of the
direction of its result. It is not a fresh confirmatory validation.

## Claim-to-artifact ledger

| Manuscript claim | Historical source | Current evidential status | Correction action |
|---|---|---|---|
| Development Geneformer AUROC 0.9676; external 0.8156 | `results/l2_dev_sle_vs_healthy.csv`; `results/l2_sealed_results.json` | Reproduces from released features, but advertised V1 extraction is not validated | Regenerate both cohorts with explicit V1 tokenizer and cell embeddings; rerun nested development CV and external scoring |
| Pseudobulk development 0.9839; external 0.8984 | Same artifacts; restricted development matrix in `results/l2_dev_pseudobulk_counts_restricted.parquet` | Historical values reproduce; development full-gene and deployment shared-gene feature spaces differ | State the feature spaces; keep external baseline fixed in the corrected comparison |
| Age development 0.6453; external 0.5781 | Same artifacts | Historical values reproduce | Keep fixed prediction comparator and state its limited confounding interpretation |
| Co-primary Geneformer minus age and pseudobulk | `results/l2_coprimary_difference_ci.json` and `results/l2_sealed_results.json` | Original label-shuffle p values test a stronger null than equal AUROC | Retain as historical; use paired DeLong plus paired bootstrap and Holm on corrected scores |
| Gene restriction changed pseudobulk AUROC by +0.00125 | `results/l2_dev_pseudobulk_restricted_cv.json` | Paired CI crosses zero; `p=0.000999` tests above-chance performance of the restricted arm | Report effect and above-chance test in separate sentences |
| External cohort counts and age strata | `results/l2_sealed_donor_metadata.csv`; external extraction summary | 56 donors, 40 cases, 16 controls; 44 source-defined Children and 12 adults; released metadata sum to 363,083 cells | Add accounting table and pre/post-tokenization counts after correction run |
| Calibration and probability quality | `results/l2_sealed_predictions_regenerated.json` | Conditional on released fitted scores, not original first-run probability identity | Report average precision, Brier, constant comparator, and diagnostic calibration with limitations |
| Cohort separability | `results/l2_cohort_signature_probe.json` | Distribution difference diagnostic; cannot quantify causal batch contribution | Investigate gene availability and use restrained interpretation |

`results/correction_2026-09/historical_scores_analysis.json` is a
read-only reanalysis of the **released** prediction vectors. Its DeLong and
calibration numbers must not be presented as validation of the defective
Geneformer recipe or as the final corrected comparison.

## Historical provenance recovered and outstanding

- The old development and external kernels selected `Geneformer-V1-10M`, set
  `model_input_size=2048`, requested `emb_mode="cls"`, and omitted
  `model_version="V1"` in both tokenizer and extractor. Their upstream Git
  install and model snapshot had no immutable revision.
- The correction scripts pin upstream Geneformer source and model snapshot to
  revision `04c2b2e84da7c0f385c3f9ad8f3ec24bab6650e5`. They validate four
  known V1 gene-to-token mappings, token bounds, sequence lengths, and exact
  donor/cell preservation. Runtime summaries will record checkpoint hashes
  and the installed package list.
- The exact original Kaggle package revision, checkpoint bytes, and first-run
  probability vectors have not been recovered. Released regenerated
  probabilities reproduce AUROCs but do not prove byte-identical first-run
  probabilities.
- Raw Census/GEO inputs and GPU embeddings are absent from this checkout.
  Consequently, no corrected Geneformer AUROC, co-primary decision, figure,
  or submission-ready manuscript can yet be claimed.
- The first Kaggle synthetic V1 fixture attempt stopped before tokenization:
  Geneformer import reached `boto3`, which expected an API absent from the
  installed `botocore`. No cohort extraction ran. The Kaggle setup now pins a
  mutually compatible `boto3`/`botocore`/`s3transfer` set. A later import in
  the already-running notebook kernel failed with NumPy's `_center` error,
  while a fresh process successfully imported NumPy 2.5.3, SciPy 1.16.3,
  Geneformer, boto3 1.40.46, and botocore 1.40.46. The notebook setup now
  tests imports in a fresh process, matching the fixture and cohort execution.
  The corrected setup still requires a successful Kaggle fixture run.
- The next fixture attempt reached `TranscriptomeTokenizer` but stopped when
  the V1 gene median pickle was a Git LFS pointer (`invalid load key, 'v'`).
  This arose because the code checkout deliberately skipped LFS smudge to
  avoid downloading all model weights. The Kaggle setup now fetches the three
  V1 dictionaries from the pinned Hugging Face revision, rejects pointer
  content, validates each nonempty pickle, and records SHA-256 hashes. The
  fixture has not yet passed on Kaggle.
- The Kaggle dictionary repair reported `V1_DICTIONARIES_OK` with 25,424
  median entries (SHA-256 `b3b589bb5ec75040d05fc44dd6bf0184cf87f3c362cf158d196a6ed3b7fe5f39`),
  25,426 token entries (`ab9dc40973fa5224d77b793e2fd114cacf3d08423ed9c4c49caf0ba9c7f218f1`),
  and 25,424 mapping entries (`eac0fb0b3007267871b6305ac0003ceba19d4f28d85686cb9067ecf142787869`).
  These hashes are user-reported Kaggle output from the pinned-revision repair
  cell; the technical embedding fixture is still pending.
- The user then attempted Kaggle Cell 4. Before cohort access, importing
  `cellxgene_census` through `s3fs`/`aiobotocore` failed because the earlier
  `botocore==1.40.46` repair lacks `EC` in `botocore.compat`. No cohort cells
  were processed by that attempt. The revised setup pins `aiobotocore==2.26.0`
  with `boto3==1.41.5`, `botocore==1.41.5`, and `s3transfer==0.15.0`, and
  checks the complete Census/Geneformer import path in a fresh process.
  Local isolated import checks passed for the AWS quartet; Kaggle validation
  and the fixture summary are awaited.
- A subsequent development/shared run reached the real data. Batch 0 finished
  for 33 donors and 158,835 cells in 1,767.3 seconds (89.87 cells/s); the
  runner writes a hash-checked batch checkpoint before its completion log.
  Batch 1 stopped while Geneformer called `datasets.map` with two processes:
  Numba reported a TBB fork from a non-main thread and a map subprocess died.
  This is a runtime multiprocessing failure, not a completed cohort result.
  The revised development and external runners use one process for tokenizer
  and extractor mapping, clear scratch for an uncheckpointed retry, and allow
  the original batch-0 checkpoint only if the prior script hash and all other
  config, donor, cell-count, and parquet integrity checks pass. The original
  checkpoint metadata is preserved. The restart and full run remain pending.
- The first in-session resume patch correctly refused an unrecognized staged
  runner hash and changed nothing. The first Kaggle notebook release had a
  second known runner SHA-256 (`be18c4d09531f211b5729fbd1380d76165f12ab02fd243af3e861688d4be509c`);
  its only difference from the later hash was an install block skipped by
  Cell 4. The revised patch accepts exactly these two historical hashes,
  checks the checkpoint's source hash against the staged source, and produces
  one exact versioned single-process runner.
- A local historical accounting run found 261 development donors and
  1,263,676 cells, plus 56 external donors and 363,083 cells. Among 30,165
  shared genes, 4,015 are zero throughout development; 490 of these are
  expressed in at least one external donor. This is a post-hoc measurement
  diagnostic, not an estimate of a biological or batch-effect contribution.

## Protocol decisions

The corrected main analysis restricts raw gene input to the recorded 30,165
shared Ensembl IDs **before** computing per-cell `n_counts`; this is a
post-hoc protocol correction on an already examined external cohort. The
model-native full-gene input is a separately labeled sensitivity analysis.
Both use V1 cell embeddings and mean pooling per donor. Geneformer `emb_layer=-1`
is the penultimate layer in the pinned upstream implementation.

## Remaining gates

1. Recover historical Kaggle logs if available; record what can and cannot
   be established about the original environment.
2. Stage the checksum-verified embedded shared-gene file. Run the synthetic
   V1 tokenizer/extractor fixture and inspect the first real-cell batch's
   checkpoint, token, cell, and donor checks.
3. Run corrected development and external extraction in both `shared` and
   `native` modes; save parquet files and summaries under a versioned release.
4. Use `scripts/28_corrected_geneformer_scoring.py`, then
   `scripts/27_correction_analysis.py` on its prediction JSON. Rebuild all
   result-dependent text and figures only after these outputs pass review.
5. Archive fitted models, prediction vectors, runtime logs, hashes, figure
   sources, and a final claim-to-artifact map in the versioned release.

## Reporting checks for manuscript revision

- Define pseudobulk restricted-gene CPM and cell-then-donor mean pooling;
  distinguish frozen encoder features from a zero-shot classifier.
- State that the development-to-external difference is descriptive transport
  performance, not estimated internal CV bias for its own population.
- Report external prevalence beside average precision, a development-
  prevalence constant Brier comparator, and diagnostic calibration with
  uncertainty. Do not evaluate recalibration on its own fit data.
- Distinguish the source-defined `Children` group from age below 18, retain
  the adult subgroup denominators, and avoid diagnostic deployment claims.
- Use TRIPOD+AI for reporting completeness and PROBAST+AI for a documented
  risk-of-bias assessment; neither constitutes a certificate of validity.
