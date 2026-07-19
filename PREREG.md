# Preregistration: External-Cohort Benchmark of Single-Cell Foundation-Model Embeddings in SLE

Status: LOCKED at time of writing. No data loaded, no models run, no compute performed under this document.

This document preregisters a confirmatory study testing whether frozen single-cell
foundation-model (Geneformer) embeddings provide patient-level discriminative value
for SLE vs. healthy control beyond a metadata-only baseline and raw pseudobulk counts,
under an external, independently sourced cohort. It supersedes the internal-only
flare-discrimination results in `reports/stage7_kaggle_result_reconciliation/` as the
project's primary analysis; those results become secondary, internal-only, tiny-n
analyses (see "Secondary / internal-only analyses" below).

Any deviation from this document after data are loaded must be recorded in an
amendment section at the bottom of this file, dated, with a stated reason. No
retroactive edits to the sections above the amendment log are permitted once the dev
cohort has been loaded.

## 1. Primary task

**SLE vs. healthy control, patient/donor-level, cross-sectional.**

- Unit of analysis: one prediction per patient/donor.
- Positive class: systemic lupus erythematosus (any disease-metadata-confirmed SLE
  donor in the respective cohort). Negative class: healthy control.
- This is a diagnosis-discrimination task, not activity, flare, nephritis, or outcome
  prediction. No claim beyond SLE-vs-healthy discrimination is in scope for the
  primary analysis.

## 2. Cohorts

**Development cohort (dev, public):** Perez et al. 2022 lupus PBMC scRNA-seq, accessed
via CELLxGENE collection `436154da-bcf1-4130-9c8b-120ff9a888f2`, dataset id
`218acb0f-9f2f-4f76-b90b-15a4b7c7f629` (verified via the CELLxGENE curation API on
2026-07-19), CC BY 4.0. 261 donors (162 SLE / 99 healthy), ~1.26M cells — donor count
and SLE/healthy split independently confirmed by categorizing the live `donor_id`
array against the README naming heuristic (`FLARE*`=flare, `HC-*`/`IGTB*`/
`ICC_control`=healthy, numeric=managed SLE): 14+148=162 SLE, 48+50+1=99 healthy.
The H5AD asset URL is reissued on each dataset revision (this dataset's
`revised_at` is 2026-06-11) — resolve the current asset URL from the dataset id via
the curation API at load time rather than hardcoding a URL in this document.

**Sealed external cohort (public, independent):** Nehar-Belaid et al. 2020,
GSE135779 (SLE + healthy PBMC; different lab, different patients, different
sequencing platform/generation than the dev cohort). The series-level summary
states 33 cSLE + 11 cHD + 8 aSLE + 6 aHD (58 donors), but the public GEO SOFT family
file (verified 2026-07-19) contains individual sample records for only **56**
donors: 33 cSLE + 11 cHD + 7 aSLE + 5 aHD — two adult samples named in the design
text have no public per-sample GEO record. This discrepancy is unresolved and must
be checked against the source publication (patient counts table) before the sealed
cohort is opened; until resolved, the sealed-cohort adult stratum should be treated
as 7 aSLE / 5 aHD (the only donors with verifiable public sample-level records), not
8/6.

Per-donor metadata field availability (verified 2026-07-19, no expression data
accessed): the dev cohort's CELLxGENE `obs` schema carries donor-level `sex`
(female/male), `self_reported_ethnicity` (African American / Asian / European
American / Hispanic or Latin), and `development_stage` (exact integer age, 20-83,
all adult). GSE135779's public per-GSM `Sample_characteristics_ch1` fields are
limited to `age` (integer), `age group` (Children/Adult), and `groups` (SLE/HD) —
**no sex or ancestry/race field is present anywhere in GSE135779's public GEO
metadata**; the series notes "Clinical information to be found in supplementary
table 1," which has not been fetched or verified under this document. This directly
constrains the metadata-only arm (Section 3) and the ancestry confound (Section 7).

All model development, feature engineering, hyperparameter selection, and
threshold/decision-rule finalization occur on the dev cohort only. The sealed cohort
is opened exactly once, after this document is frozen and after dev-cohort work is
complete, following the same freeze/one-look discipline used in the project's prior
work (`reports/stage7_kaggle_result_reconciliation/`).

### 2.1 Independence verification (pre-freeze)

Before the sealed cohort is opened for evaluation, independence from the dev cohort
will be verified using public metadata only:

- Compare GEO/CELLxGENE-published donor identifiers, and where available
  demographic/clinical descriptors (age, sex, ancestry, recruitment site), between
  the Perez 2022 dev cohort and GSE135779 to confirm no donor or sample overlap.
- Confirm the two cohorts derive from distinct publications, distinct recruitment
  cohorts, and distinct sequencing generations, per their respective source papers
  and GEO/CELLxGENE records.
- Record the result of this check (pass/fail, with the specific metadata fields
  compared) in the sealed-cohort evaluation report before any sealed-cohort
  prediction is generated. If overlap is found, the sealed cohort is disqualified as
  an independent external cohort and this document must be amended before proceeding.

## 3. Model arms

Three arms, all fit using train-fold data only (dev-cohort cross-validation) and then
frozen for the single sealed-cohort application:

1. **Geneformer embeddings arm**: mean-pooled per-cell Geneformer embeddings,
   aggregated to one vector per patient/donor (mean over that donor's cells), fed to
   a downstream classifier.
2. **Raw pseudobulk arm**: per donor, raw counts are summed across that donor's
   cells, CPM-normalized (counts per million within the summed donor profile), then
   log1p-transformed. This CPM+log1p pseudobulk vector is the feature input to the
   same downstream classifier family. Locked 2026-07-19.
3. **Metadata-only arm**: only non-transcriptomic metadata fields confirmed present
   and comparably coded in **both** dev and sealed cohorts (Section 2). As verified
   2026-07-19, this is currently **age only** — sex and ancestry are present in the
   dev cohort's CELLxGENE `obs` schema but absent from GSE135779's public GEO
   metadata, so they cannot be used in the metadata-only arm as it stands. If
   sex/ancestry are later confirmed at donor level from the source publication's
   supplementary table (a separate metadata-only verification step, not yet done),
   this arm's feature set may be amended and the amendment logged. No
   gene-expression-derived feature enters this arm.

Constraints applying to all three arms:
- Patient-grouped cross-validation splits on the dev cohort (no donor's cells appear
  in both train and validation folds).
- Any scaling, normalization, dimensionality reduction, or classifier fitting is
  performed within the train fold only and applied to the held-out fold/sealed
  cohort without refitting on held-out data.
- Aggregation to one prediction per patient happens before AUROC is computed (no
  cell-level AUROC).

## 4. Primary metric and statistics

- **Primary metric:** patient-level AUROC.
- **Uncertainty:** patient-bootstrap 95% CI (resample patients with replacement,
  recompute AUROC, over the bootstrap distribution).
- **Null test:** permutation test on patient-level labels, 1000 permutations,
  two-sided.
- These are computed separately for each arm, on the dev cohort (internal CV) and
  on the sealed cohort (single external application).

## 5. Co-primary confirmatory comparisons

Both comparisons below are confirmatory (not exploratory) and are evaluated on the
**sealed external cohort**. Both use a one-sided directional hypothesis (Geneformer
expected superior) with a pre-specified decision rule.

### Comparison A: Geneformer vs. metadata-only

- H_A: AUROC(Geneformer) − AUROC(metadata-only) > 0 on the sealed cohort.
- Decision rule: reject the null (conclude Geneformer adds value over metadata) only
  if the patient-bootstrap 95% CI of the paired difference
  [AUROC(Geneformer) − AUROC(metadata-only)] excludes 0 **and** lies entirely above
  0, after Holm correction (Section 6).
- If the CI includes 0, or excludes 0 on the negative side, the null is not rejected
  and the working conclusion is that Geneformer embeddings do not demonstrate
  external added value over metadata alone.

### Comparison B: Geneformer vs. raw pseudobulk

- H_B: AUROC(Geneformer) − AUROC(pseudobulk) > 0 on the sealed cohort.
- Decision rule: identical structure to Comparison A — reject the null only if the
  patient-bootstrap 95% CI of the paired difference excludes 0 and lies entirely
  above 0, after Holm correction (Section 6).

### 5.1 Pre-specified secondary confirmatory analysis: cohort-signature probe

- Question: can a classifier distinguish dev-cohort donors from sealed-cohort donors
  using the same feature arms (Geneformer / pseudobulk / metadata)? This is the SLE
  analogue of a site-signature probe and is used to characterize the degree to which
  cohort/batch/platform identity is separable in each feature space — a high cohort-
  signature AUROC in the Geneformer or pseudobulk arm is evidence that apparent
  disease-discrimination performance may be confounded by cohort identity rather
  than SLE biology.
- Metric: patient-level AUROC of cohort-membership (dev vs. sealed) classification,
  computed per arm, with the same patient-bootstrap 95% CI and permutation test as
  Section 4.
- This analysis is confirmatory (pre-declared here) but not part of the co-primary
  family; it is not Holm-corrected alongside Comparisons A/B. It is reported
  alongside them as an interpretive check.

## 6. Multiple-comparisons correction

The confirmatory family for Holm correction consists of exactly the two co-primary
comparisons: Comparison A and Comparison B (Section 5). The correction is applied to
the two two-sided p-values obtained from the permutation test of the paired AUROC
differences (Geneformer − metadata; Geneformer − pseudobulk), each permuting
patient-level labels 1000 times.

Holm step-down procedure (to be executed, not merely cited). α = 0.05, locked
2026-07-19:
1. Rank the two p-values ascending: p(1) ≤ p(2).
2. Compare p(1) to α/2 (α = 0.05). If p(1) > α/2, stop — neither comparison is
   significant.
3. If p(1) ≤ α/2, comparison (1) is significant. Compare p(2) to α/1. If p(2) ≤ α,
   comparison (2) is also significant; otherwise only comparison (1) is significant.

The realized p-values, the ranking, and the step-by-step threshold comparisons must
be reported numerically in the results report — a citation to "Holm correction" with
no computed thresholds does not satisfy this preregistration.

## 7. Pre-registered confounds

The following confounds are pre-declared as of interest and will be reported
regardless of primary outcome:

- **Age structure**: dev cohort (Perez 2022) is 100% adult (20-83); sealed cohort
  (Nehar-Belaid 2020, GSE135779) is mixed pediatric/adult (as verified 2026-07-19:
  44 pediatric donors [33 cSLE + 11 cHD] and either 12 or 14 adult donors depending
  on resolution of the sample-count discrepancy in Section 2). Locked decision
  (2026-07-19): the sealed cohort's adult stratum is **not pooled blindly** into the
  overall sealed-cohort AUROC. Age group (pediatric/adult, from GSE135779's `age
  group` field) is treated as a pre-declared stratification covariate — sealed-
  cohort AUROC, bootstrap CI, and permutation p-values for the primary task and both
  co-primary comparisons (Section 5) are reported both overall and stratified by age
  group, and any adult-vs-pediatric AUROC gap is reported descriptively alongside
  the primary result. This is consistent with age structure already being a
  pre-declared confound rather than a nuisance to average away.
- **Ancestry**: reported ancestry/genetic-ancestry composition, to the extent coded
  comparably in both cohorts' public metadata. As verified 2026-07-19, GSE135779 has
  no public ancestry/race field (Section 2), so this confound is currently
  assessable for the dev cohort only and cannot be compared dev-vs-sealed unless a
  sealed-cohort ancestry field is later sourced and this document is amended.
- **Platform/batch**: the two cohorts were generated on different sequencing
  platform generations/protocols per their source publications; this is treated as
  an uncontrolled batch effect between dev and sealed, not a within-cohort batch to
  be corrected away.

These confounds are reported as descriptive comparisons (dev vs. sealed composition)
and are not adjusted for in the primary AUROC estimates — adjustment is out of scope
for this preregistration and is not required for the primary/co-primary conclusions.
The cohort-signature probe (Section 5.1) is the primary confirmatory device for
assessing whether these confounds are separable in feature space.

## 8. Harmonization plan

- **Reference/ingest protocol**: dev cohort (Perez 2022) serves as the reference.
  Sealed-cohort (GSE135779) cells are projected into the reference embedding space
  and cell-type labels are transferred via Scanpy `ingest` and k-NN label transfer,
  following the precedent described in the harmonization protocol cited in project
  context (bioRxiv 10.64898/2026.04.28.721379v1).
- **Gene-space intersection**: features are restricted to the intersection of genes
  present and comparably identified (matching gene symbol/Ensembl ID convention)
  in both the dev and sealed cohort's raw count matrices. No imputation of missing
  genes is performed.
- **Genes absent in one cohort**: dropped from all three model arms uniformly — the
  Geneformer, pseudobulk, and any gene-derived preprocessing use only the intersected
  gene set, so no arm receives a systematic feature-availability advantage.
- **Cell types absent in one cohort**: retained in the source cohort's per-donor
  aggregation (mean-pooling / pseudobulk summation is computed over whatever cells
  a donor has); no cell type is excluded from a donor's aggregate solely because it
  is rare or absent in the other cohort. Any donor-level exclusion for near-zero
  cell count in a given aggregation is a data-quality decision, not a modeling
  decision, and will be reported explicitly with counts if applied.

## 9. Secondary / internal-only analyses

The following are retained from prior work as secondary, **non-externally-validated**
analyses. They are not part of the confirmatory family and carry no Holm correction:

- **flare_vs_managed** (internal patient-level LOOCV, dev-cohort-only exploratory
  data; prior result AUROC 0.9962 on 163 patients, 14 flare cases).
- **flare_vs_healthy** (internal patient-level LOOCV, dev-cohort-only exploratory
  data; prior result AUROC 0.9927 on 112 patients, 14 flare cases).

Both are explicitly labeled: internal-only, no external cohort applied, tiny active-
flare class (n=14), and not eligible for any external-generalization or clinical
claim. These numbers are carried forward as already-committed prior results
(`reports/stage7_kaggle_result_reconciliation/stage7_metric_results.csv`) and are not
re-run under this preregistration.

## 10. Scope limits

This preregistration and the study it governs do **not** support, and no report
produced under it may claim:

- clinical deployment readiness,
- diagnostic use or diagnostic-grade performance claims,
- disease-activity or flare-activity prediction (primary task is diagnosis only),
- lupus nephritis prediction,
- prospective/longitudinal forecasting of any kind,
- generalization beyond the two named public cohorts.

## 11. What is NOT done under this document

No cell or donor data have been loaded. No embeddings have been computed. No
classifier has been fit. No AUROC, CI, or p-value referenced above is a result —
all numeric outcomes stated as "prior result" in Section 9 are carried forward
verbatim from `reports/stage7_kaggle_result_reconciliation/stage7_metric_results.csv`
and are not new computations. This document is a plan only.

## Amendment log

**2026-07-19 — L1 metadata-only inspection.** No cell/donor data loaded, no models
run. Performed before any dev-cohort loading, so this updates Sections 2, 3, 6, and
7 in place rather than appending a post-freeze deviation. Changes:
- Locked pseudobulk arm definition to CPM-normalization + log1p (Section 3).
- Confirmed Holm α = 0.05 (Section 6).
- Restricted the metadata-only arm to age-only, since GSE135779's public GEO
  metadata has no sex or ancestry field (Sections 2, 3).
- Locked sealed-cohort age-group (pediatric/adult) as a pre-declared stratification
  covariate rather than pooling the adult stratum in blindly (Section 7).
- Recorded a verified CELLxGENE dataset id/asset-URL correction and an unresolved
  GSE135779 sample-count discrepancy (56 public per-sample GEO records vs. 58
  claimed in the series summary) (Section 2).

**L1 status: NOT locked.** Two open items block calling metadata inspection clean:
(1) sex/ancestry are unverified for the sealed cohort pending a supplementary-table
check against the source publication; (2) the GSE135779 58-vs-56 sample count
discrepancy is unresolved. L2 (donor-grouped dev-cohort run) does not begin until
these are resolved or explicitly accepted as-is.
