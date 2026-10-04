# Lupus paper scientific correction: implementation report

**Report date:** 30 September 2026  
**Repository:** [mohamad679/lupus-singlecell-foundation](https://github.com/mohamad679/lupus-singlecell-foundation)  
**Correction branch:** `scientific-correction-2026`  
**Review vehicle:** [open pull request #58](https://github.com/mohamad679/lupus-singlecell-foundation/pull/58)  
**Historical release preserved at:** `6158a8409064ae8c7a608126cc2d7a7e65b02506`

This report describes work performed under the five-phase correction plan, from the initial review through the corrected paper package. It distinguishes completed work from remaining scientific and submission tasks. The external GSE135779 cohort had already been examined, so all new analyses on it are **corrected reanalyses**, not independent confirmation.

## 1. Starting point and initial plan

The reviewed manuscript and supplement made Geneformer V1 performance and two Geneformer-superiority comparisons central to the paper. The review identified an unvalidated Geneformer V1 extraction path, an inference mismatch in the historical label-shuffle p values, differences in gene spaces between development and external analysis, and reporting gaps. The response was a focused, two-cohort validation paper, with the historical release retained and corrected outputs written separately. The agreed phases were: (1) preservation and traceability, (2) corrected V1 extraction, (3) repaired inference and essential analyses, (4) revised paper and figures, and (5) reproducibility and reporting checks. A new untouched cohort and broader encoder benchmark were explicitly deferred.

Work began by preserving commit `6158a840` and creating versioned correction code and documents on a separate branch. The first correction commit was `53fecda` (“Prepare versioned lupus scientific correction and provisional paper drafts”); subsequent commits document each repair and validated artifact. The original `FREEZE.json`, `SEALED_OPENED.json`, preregistration, historical `results/l2_*` files, and original Kaggle kernels were kept as historical records. Nine frozen file hashes were checked against the historical checkout. The [scientific correction ledger](https://github.com/mohamad679/lupus-singlecell-foundation/blob/scientific-correction-2026/docs/SCIENTIFIC_CORRECTION_2026-09.md) maps original claims to artifacts and states which original results could be reproduced, which were scientifically provisional, and what had to be regenerated.

## 2. Phase 1 — preserve and trace the original analysis

The historical Geneformer development AUROC was 0.9676 and external AUROC was 0.8156. Those values reproduce from released vectors, but that only verifies the saved vector-to-score calculation. The original development and external kernels selected a V1 checkpoint while requesting `emb_mode="cls"` and omitting explicit `model_version="V1"`; the original first-run checkpoint bytes, exact upstream package revision, and first-run probability vectors were not recovered. The released historical p values came from label permutations and test an above-chance null, not equality of paired AUROCs. They remain visible as historical results; they are not the corrected co-primary tests.

The pseudobulk comparison uses a 30,165-gene shared space for external scoring. The original development cross-validation used a different full-gene feature space; this was disclosed. The reported restriction effect and the restricted arm's above-chance p value were separated because they answer different questions. The public external deposit contains 56 usable samples, rather than the 58 described in older materials. Two development donors with ambiguous age are excluded only from the age-only arm. Other original protocol deviations remain documented in the [preregistration deviations record](https://github.com/mohamad679/lupus-singlecell-foundation/blob/scientific-correction-2026/docs/PREREGISTRATION_DEVIATIONS.md).

## 3. Phase 2 — correct V1 extraction and validate four Kaggle runs

New versioned development and external extraction runners were built; original runners were preserved. The corrected path pins Geneformer revision `04c2b2e84da7c0f385c3f9ad8f3ec24bab6650e5`, explicitly uses `model_version="V1"`, `model_input_size=2048`, `emb_mode="cell"`, and `emb_layer=-1`, and pools valid cell embeddings to 256-dimensional donor vectors. The **shared 30,165-gene input** is the main analysis; model-native input is a labeled sensitivity analysis. A synthetic eight-cell fixture checks tokenizer and extractor compatibility, selected gene-token mappings, special-token/length bounds, finite embeddings, and repeated tokenization after GPU extraction. Full runs check donor keys, exact cell accounting, finite vectors, hashes, and runtime provenance.

Four self-contained Kaggle notebooks were supplied in `kaggle_notebooks/`: `CBC_Kaggle_1_Development_Shared.ipynb`, `CBC_Kaggle_2_External_Shared.ipynb`, `CBC_Kaggle_3_Development_Native.ipynb`, and `CBC_Kaggle_4_External_Native.ipynb`. The notebooks stage checksum-verified code, install/verify pinned dependencies, run the fixture, process one cohort/mode, and export a share ZIP. Resumable batches have checksum-checked checkpoints. The complete execution instructions are in the [correction runbook](https://github.com/mohamad679/lupus-singlecell-foundation/blob/scientific-correction-2026/docs/CORRECTION_RUNBOOK.md).

The Kaggle implementation required several repairs before a valid full run:

1. Mixed in-process NumPy installation caused `_center` import errors, although a fresh Python process passed imports. Setup and jobs were changed to use and test a fresh process.
2. Three downloaded V1 dictionary files were Git LFS pointer text, producing `UnpicklingError: invalid load key, 'v'`. The notebooks now fetch exact dictionary bytes from the pinned revision, reject pointers, unpickle and validate them, and record hashes. Verified entry counts were 25,424 medians, 25,426 tokens, and 25,424 mappings.
3. `cellxgene_census` import exposed an `aiobotocore`/`botocore` incompatibility. Compatible `aiobotocore`, `boto3`, `botocore`, and `s3transfer` versions were pinned and the whole import path checked before the fixture.
4. The first real development/shared run finished a 158,835-cell batch, then Datasets/TBB failed after forking from a non-main thread. A resume patch initially rejected an unknown source hash as designed. The accepted source-hash list was corrected only after matching the staged source and checkpoint metadata. Tokenizer `nproc=1` still forked a worker, so the final runners use `nproc=None`; the fixture exercises the previous failure sequence. Existing checked checkpoints were reused only after source, mode, donor, cell-count, and parquet checks.

All four user-provided Kaggle share ZIPs were then ingested with `scripts/35_ingest_corrected_kaggle_zip.py`. The ingestion checks archive/member hashes, fixture success, cohort counts, unique donor/sample keys, finite 256-dimensional embeddings, and no missing rows. Development contained **261 donors and 1,263,676 cells**; external contained **56 samples and 363,083 cells**. Both modes matched the expected accounting. The original ZIPs remain outside Git in `correction_artifacts/`; validated parquet files, run summaries, and ingestion reports are versioned under `results/correction_2026-09/{shared,native}_features/`. The summaries record model/checkpoint hashes, Geneformer revision, parameters, and runtime package lists. **They do not contain V1 dictionary hashes.** Those three hashes were printed in the successful Kaggle setup output and are user-reported evidence, not independently archived records. The later revised notebooks export `setup_provenance.json` with dictionary, staged-source, checkpoint, runtime, and batch metadata; that revision was syntax-checked locally but has not been rerun on Kaggle. All four older ZIPs passed the new backwards-compatible ingest checks on 30 September.

## 4. Phase 3 — scoring, paired inference, and supporting analyses

`scripts/28_corrected_geneformer_scoring.py` reran donor-level development cross-validation and a final development fit from the corrected embeddings, then produced fixed external probabilities. It validates source hashes, checkpoint consistency, donor/label pairing, finite dimensions and probabilities, and expected input mode. `scripts/27_correction_analysis.py` applies paired DeLong equal-AUROC tests, 5,000 paired donor-bootstrap draws for difference intervals, and Holm adjustment across the two co-primary comparisons. The original superiority rule remains visible: both the corrected p value and the signed interval must support a positive Geneformer advantage.

| Corrected main result | Value | Source |
|---|---:|---|
| Geneformer V1 development AUROC | 0.9746 (95% CI 0.9548–0.9901) | `corrected_v1_descriptive.json` |
| Geneformer V1 external AUROC | 0.7344 (0.6017–0.8597) | `corrected_v1_descriptive.json` |
| Pseudobulk external AUROC | 0.8984 | `corrected_v1_shared_analysis.json` |
| Age-only external AUROC | 0.5781 | `corrected_v1_shared_analysis.json` |
| Geneformer minus age external AUROC | +0.1563 (paired CI −0.0859 to +0.4040); Holm p=0.2046 | `corrected_v1_shared_analysis.json` |
| Geneformer minus pseudobulk external AUROC | −0.1641 (paired CI −0.2916 to −0.0384); Holm p=0.0175 | `corrected_v1_shared_analysis.json` |

**Neither prespecified Geneformer-superiority criterion was met.** The second comparison provides evidence of a difference in the pseudobulk direction under the specified paired analysis; it does not prove general model inferiority across datasets or tasks. The external test comprises 40 cases and 16 controls. Confidence intervals condition on fixed predictions and do not include complete retraining or extraction uncertainty.

The model-native Geneformer sensitivity run gave external AUROC **0.7484**. Native minus shared was **+0.0141** (paired CI −0.0238 to +0.0597; paired DeLong p=0.4601). It is an exploratory analysis of the same examined external samples. `scripts/29_gene_input_sensitivity.py` verifies donor alignment and comparator identity before computing it.

The additional analyses include donor/cell accounting; the 30,165 shared genes and 490 development-zero genes expressed externally; AUROC by source-defined Children (44 samples) and Adult (12 samples) groups; average precision, Brier scores, a constant development-prevalence probability comparator, and diagnostic calibration. External Geneformer Brier score was 0.4713 versus 0.2128 for the constant comparator. The saved fitted models reproduced every saved Geneformer probability exactly; their original `decision_function` scores were attached to the prediction artifacts. Diagnostic calibration from those scores gives external shared-Geneformer intercept **2.091** (95% Wald CI 0.792–3.390) and slope **0.149** (0.027–0.271). Reconstructing logits from probabilities after clipping eight saturated values instead gives intercept 2.374 and slope 0.185, and is labeled as a separate convention. The corrected Geneformer cohort-origin probe gave AUROC **0.9999** (95% CI 0.9996–1.0000); it is a post-hoc diagnostic of cohort separability, not a disease-prediction result or proof of a particular causal batch effect. These outputs are in `corrected_v1_descriptive.json`, `corrected_v1_shared_cohort_probe.json`, `historical_gene_availability.json`, and the analysis files.

The later source-metadata review found aHD3/GSM4029942 recorded as age **50** in GEO, while an independent review reported age **43** in the study supplement. The supplement workbook and its hash were unavailable for independent verification, so 50 remains the preregistered-source primary value. The repository archives the dated GEO series/sample SOFT records and a 58-row source-to-GSM crosswalk identifying aHD2 and aSLE8 as absent from the 56-sample public deposit. Changing only aHD3 to 43 with the already fitted age model moves external age AUROC from 0.5781 to **0.5797**, and Geneformer-minus-age from +0.1563 to **+0.1547** (paired DeLong p **0.2082**; 95% paired CI −0.0862 to +0.4022). The superiority conclusion is unchanged. This is exploratory source sensitivity, not a replacement primary analysis or independent confirmation.

## 5. Phase 4 — paper and figure revision

Five revised Word documents were built in the paper workspace's `corrected_submission_2026-09/` directory: manuscript, supplement, title page, highlights, and cover letter. The manuscript now identifies the work as a corrected reanalysis; defines V1 cell-to-donor feature construction, shared and native gene inputs, cohort accounting, paired uncertainty and correction, calibration, and protocol boundaries; and replaces the original co-primary interpretation. The supplement records the claim-to-artifact map, source crosswalk, age sensitivity, calibration conventions, and reporting assessment. The title, highlights, and cover letter were aligned with the corrected message. The documents were rendered and visually checked page by page: the manuscript has **14 pages**, supplement **3 pages**, and each other document **1 page**. The cover letter is an author-review draft and does not assert that final author approval has occurred.

`scripts/32_corrected_figures.py` generated four publication-resolution TIFF figures, four vector PDF masters, and PNG inspection copies: overall corrected AUROCs, source age-group AUROCs, co-primary paired differences, and a cohort-origin probe. Figure 4's in-image legend defines the AUROC point, 95% donor-bootstrap interval whisker, and 0.5 chance line. Its Word caption also describes the intervals and interpretation.

The current downloadable package is `Lupus_Paper_Corrected_2026-09_v3.zip`. It contains the five Word documents, four corrected TIFFs, four vector PDF masters, this Markdown report, and a README. The earlier v1 and v2 ZIPs are superseded; v1 lacked Figure 4's in-image legend, and v2 predates the source-age and calibration corrections.

## 6. Phase 5 — reproducibility and reporting review

The correction branch contains versioned extraction, ingestion, scoring, analysis, figure, and document scripts; four Kaggle notebooks; pinned local scoring requirements and tested direct extraction dependencies; extracted run summaries with checkpoint and runtime provenance; per-donor probabilities and original decision scores; development out-of-fold predictions; fitted model artifacts; and an SHA-256 artifact manifest at `results/correction_2026-09/corrected_artifact_manifest.json`. The manifest checks corrected results, dated GEO source records, relevant code/notebooks, TIFF/PDF figures, five Word documents, and four original Kaggle ZIPs. The scoring path rejects mismatched input hashes, noncanonical V1 settings, missing or duplicate donor keys, inconsistent labels, invalid vectors or probabilities, and conflicting checkpoint provenance.

`scripts/37_reproduce_corrected_results.sh` now resolves packages online by default, writes to a new isolated directory, and supports explicit `--offline`; its comparator checks donor-aligned probabilities, decision scores, discrimination, and paired inference in both modes. An isolated offline run on 30 September completed with status **pass** and numerical tolerance 1e-12. This reproduces the validated feature-to-result path from archived donor vectors. A CPU CI workflow compiles the correction source and runs 17 focused tests. The full raw-cell extraction still requires Census/GEO access and a Kaggle GPU.

The [author correction audit](https://github.com/mohamad679/lupus-singlecell-foundation/blob/scientific-correction-2026/docs/correction_2026-09_audit.md) and dated [reporting and bias review](https://github.com/mohamad679/lupus-singlecell-foundation/blob/scientific-correction-2026/docs/REPORTING_AND_BIAS_REVIEW.md) use [TRIPOD+AI](https://www.bmj.com/content/385/bmj-2023-078378) and [PROBAST+AI](https://www.bmj.com/content/388/bmj-2024-082505) as frameworks. The reporting map links corrected manuscript locations to data sources, participants, labels, predictors, validation, uncertainty, calibration, code, and limitations, with explicit gaps. The author assessment finds high risk for a clinical-use claim and uncertain clinical applicability. A completed official item-by-item checklist and independent PROBAST+AI adjudication remain submission tasks. No clinical diagnostic use, prediction threshold, or decision-curve utility was established.

## 7. What is complete, and what remains

The agreed **focused two-cohort correction** is implemented: all four corrected feature runs were validated; predictions, paired inference, source-age sensitivity, essential descriptive analyses, five documents, and four figures with vector masters were generated; and reproducibility records were saved. PR #58 is the review vehicle for the correction branch. It is **open and unmerged**; the repository's `main` branch has not been changed by this correction. Its two CPU checks passed at commit `99323e3`. The v3 package is the current revised set for author review. Readable manuscript and supplement PDF drafts are also on the correction branch.

The paper is not a new confirmatory validation. The following are unresolved or outside the agreed scope: a fresh untouched external cohort; broader encoder comparison; cell-type-resolved validation; independent assessment of model-pretraining overlap; the official item-by-item reporting checklist and independent bias adjudication; harmonization of clinical outcome ascertainment and sparse external sex/ancestry metadata; and clinical utility. The public 56-versus-58 sample discrepancy and unverified study-supplement age entry remain documented. These limits should stay in the submitted paper. Final journal formatting, author verification of declarations, author sign-off, and merger of the open PR remain.

## 8. File map and verification pointers

| Purpose | Location |
|---|---|
| Historical release | Git commit `6158a840` and original `results/l2_*` |
| Correction ledger | `docs/SCIENTIFIC_CORRECTION_2026-09.md`, `docs/correction_2026-09_audit.md` |
| Four executable Kaggle notebooks | `kaggle_notebooks/CBC_Kaggle_{1..4}_*.ipynb` |
| Corrected extraction source | `kaggle_kernels/l2_geneformer_v1_corrected_dev/`, `kaggle_kernels/l2_geneformer_v1_corrected_external/` |
| Validated features and run summaries | `results/correction_2026-09/shared_features/`, `native_features/` |
| Predictions and statistics | `results/correction_2026-09/corrected_v1_*.json` |
| Analysis and figure source | `scripts/27_correction_analysis.py` through `scripts/32_corrected_figures.py` |
| Four corrected figures and vector masters | `figures/correction_2026-09/Figure_{1..4}_Corrected.{tiff,pdf}` |
| Five revised Word documents | Parent paper folder: `corrected_submission_2026-09/` |
| Readable manuscript and supplement drafts | `manuscript_drafts/correction_2026-09/` |
| GEO source crosswalk and age sensitivity | `external_source_to_gsm_crosswalk.csv`, `external_age_source_sensitivity.json`, `docs/source_records/` |
| Hash manifest | `results/correction_2026-09/corrected_artifact_manifest.json` |
| Reproduction instructions | `docs/CORRECTION_RUNBOOK.md` |

This is a work and provenance record. Source files and versioned result artifacts, rather than rounded numbers in this report, are authoritative for exact numerical reproduction.
