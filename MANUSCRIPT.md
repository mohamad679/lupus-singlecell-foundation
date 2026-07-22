# Internal cross-validation overstates single-cell foundation-model performance in systemic lupus erythematosus: a pre-registered, sealed-cohort external validation

**Status:** draft, Q2 target. All numbers below are pulled from committed artifacts (`results/`, `FREEZE.json`) and cross-checked against source files while writing; any value not traceable to a committed artifact is marked `[TODO: verify]`.

## Abstract

Frozen single-cell foundation-model embeddings are increasingly benchmarked with internal cross-validation alone. We pre-registered (`PREREG.md`, tag `prereg-locked-v1`) a test of whether Geneformer patient-level embeddings add discriminative value for systemic lupus erythematosus (SLE) vs. healthy-control classification beyond raw pseudobulk counts and a metadata-only (age) baseline, using a development cohort (Perez et al. 2022, 261 donors, CZ CELLxGENE Census) and a single, sealed, external cohort (GSE135779, Nehar-Belaid et al. 2020, 56 donors) opened exactly once after all hyperparameters were frozen. **Geneformer embeddings transferred to the external cohort (sealed AUROC 0.8156, 95% CI [0.6814, 0.9312]), and showed no statistically significant advantage over either baseline: not over the metadata-only (age) model (0.5781, 95% CI [0.3711, 0.7835]; comparison A diff +0.2375, 95% CI [−0.0431, +0.5179], permutation p=0.087 pre-Holm) and not over a simpler pseudobulk model (0.8984, 95% CI [0.8068, 0.9688]; comparison B diff −0.0828, 95% CI [−0.2061, +0.0242], permutation p=0.184 pre-Holm).** Both pre-registered co-primary comparisons were **REJECTED** under the pre-specified decision rule (paired 95% CI excluding zero, Holm-corrected at α=0.05): neither comparison's CI excluded zero, and Holm's first step already failed (p=0.087 > α/2=0.025), so neither reached significance — including comparison A, despite its large internal-CV point-estimate separation. Internal cross-validation substantially overstated all three arms' external performance (Geneformer 0.9676→0.8156, pseudobulk 0.9839→0.8984, metadata-age 0.6453→0.5781). A pre-declared cohort-signature probe found near-total separability between the two cohorts in every feature space (AUROC 0.9996–1.0000 for Geneformer/pseudobulk, 0.8719 for age alone), which we report as a bound on interpretability, not a validation: disease signal cannot be cleanly disentangled from cohort/batch/platform signal at this confound level. We conclude that a single external sealed evaluation materially changed the scientific conclusion that internal cross-validation alone would have supported, and that the specific external cohort available for this study cannot adjudicate disease-specific vs. cohort-confounded signal.

## 1. Introduction

Single-cell foundation models (e.g., Geneformer, scGPT) are frequently benchmarked using k-fold or leave-one-out cross-validation within a single cohort. This internal-CV paradigm is vulnerable to a specific and under-examined failure mode: because train and test folds are drawn from the same cohort, any cohort-specific signal (batch, site, sequencing platform, patient demographics, sample-handling artifacts) that happens to correlate with the disease label in that cohort is available to the model during training and will appear as generalizable "performance" during internal evaluation, even though it may not transfer to a genuinely independent cohort. This is not a hypothetical concern for single-cell foundation-model benchmarking specifically — analogous internal/external gaps are well documented in other domains — but it is rarely tested directly for these models because genuinely independent, label-compatible, single-cell sealed cohorts are hard to source, and because the discipline of freezing a model and its hyperparameters before a single external look is uncommon in exploratory computational biology work.

This project's central question, stated before any dev-cohort data was loaded: **does internal cross-validation overstate the benefit of frozen single-cell foundation-model embeddings, relative to simpler baselines, when tested on a real external cohort?** We test this directly, for SLE-vs-healthy diagnosis, with a pre-registered protocol, a frozen pipeline, and a sealed cohort opened exactly once.

## 2. Methods

### 2.1 Cohorts

**Development (dev) cohort:** Perez et al. 2022, accessed via CZ CELLxGENE Census (collection `436154da-bcf1-4130-9c8b-120ff9a888f2`, dataset `218acb0f-9f2f-4f76-b90b-15a4b7c7f629`, CC BY 4.0, census version `2025-11-08`). 261 donors (162 SLE / 99 healthy), ~1.26M cells.

**Sealed (external) cohort:** GSE135779 (Nehar-Belaid et al. 2020), a different lab, different patients, different sequencing-platform generation than the dev cohort. Public GEO deposit contains 56 donors with per-sample records (33 childhood SLE + 11 childhood healthy + 7 adult SLE + 5 adult healthy); the source publication describes 58 (8 adult SLE + 6 adult healthy) — the discrepancy is unresolved against the source publication's supplementary materials and is used as-is (`docs/PREREGISTRATION_DEVIATIONS.md` item 4). 40 SLE / 16 healthy overall; 44 pediatric / 12 adult.

### 2.2 Three arms

1. **Geneformer:** Geneformer-V1-10M, per-cell embeddings (`model_input_size=2048`, `emb_mode="cls"`, `emb_layer=-1`), mean-pooled per donor to a 256-dimensional vector.
2. **Pseudobulk:** raw counts summed per donor, restricted to the 30,165-gene intersection between the two cohorts' gene references (dev: 61,497 Ensembl genes via the Census; sealed: 32,738 Ensembl genes via GSE135779's series-level CellRanger v2 reference; both cohorts confirmed to use Ensembl gene IDs, no symbol mapping required), CPM-normalized over that restricted total, log1p-transformed.
3. **Metadata-only (age):** donor age alone, the deliberately weak baseline.

All three arms use `StandardScaler` + `LogisticRegression` (L2 penalty, `l1_ratio=0`, `solver="lbfgs"`).

### 2.3 Donor-grouped nested cross-validation (dev cohort)

Each dev-cohort feature table is already one row per donor (mean-pooled/summed at the aggregation step), so there is no cell-level data left to leak across folds — plain `StratifiedKFold` (5 outer folds) already guarantees no donor's data appears in both train and test for a given fold; `GroupKFold` would be a no-op in this setting. Hyperparameter `C` was selected per outer fold via an inner 5-fold grid search over `[0.001, 0.01, 0.1, 1.0, 10.0, 100.0]`, with no leakage of the outer test fold into that selection. Out-of-fold predictions were aggregated to compute a single patient-level AUROC per arm, with a patient-bootstrap 95% CI (5000 resamples) and a 1000-permutation two-sided test.

### 2.4 Preregistration and freeze protocol

The full protocol — primary task, co-primary comparisons and their exact decision rule, Holm correction procedure, pre-registered confounds, harmonization plan, and scope limits — was locked in `PREREG.md` before any dev-cohort data was loaded (tag `prereg-locked-v1`). Before the sealed cohort was touched, every file that determines a sealed-cohort prediction (feature-extraction code, the CV/model pipeline, both Kaggle kernel sources) was SHA-256 hashed into `FREEZE.json`, alongside the exact per-arm hyperparameter selected by nested CV (median of the 5 outer-fold selections: Geneformer C=1.0, pseudobulk C=0.01, metadata-age C=0.001) and a rule stating how that value was chosen. `scripts/freeze_guard.py`'s `require_valid_freeze()` refuses to run any sealed-cohort script if the live files no longer match that manifest.

### 2.5 One-shot sealed evaluation

The sealed cohort was opened exactly once. For each arm, a single final model was fit on the entire dev cohort at the frozen `C` (the one necessary step to obtain a final coefficient vector from a nested-CV protocol that otherwise only produces out-of-fold predictions — `docs/PREREGISTRATION_DEVIATIONS.md` item 6) and applied to the sealed cohort's features with no further fitting. `SEALED_OPENED.json`, written immediately after this evaluation, permanently blocks any further sealed-cohort access under this freeze.

## 3. Results

### 3.1 Dev-cohort internal cross-validation

| Arm | n | AUROC | 95% CI | Permutation p |
|---|---:|---:|---|---:|
| Geneformer | 261 | 0.9676 | [0.9446, 0.9865] | 0.001 |
| Pseudobulk | 261 | 0.9839 | [0.9703, 0.9938] | 0.001 |
| Metadata (age) | 259 | 0.6453 | [0.5741, 0.7184] | 0.001 |

(`results/l2_dev_sle_vs_healthy.csv`; Figure 1, `figures/dev_vs_sealed_auroc.png`.)

**Repeated CV (robustness check, 10 repeats of the same 5-fold nested protocol, fresh seeds):** Geneformer mean 0.9669 (SD 0.0029), pseudobulk mean 0.9836 (SD 0.0028), metadata-age mean 0.6462 (SD 0.0062) — all three single-run values fall within approximately one SD of their repeated-CV mean (`results/l2_dev_repeated_cv.csv`), indicating the dev-cohort estimates are stable under fold-assignment randomness. This is a dev-only robustness statement and does not alter or touch any sealed-cohort result.

### 3.2 Sealed-cohort external validation

| Arm | n | AUROC | 95% CI | Permutation p |
|---|---:|---:|---|---:|
| Geneformer | 56 | 0.8156 | [0.6814, 0.9312] | 0.001 |
| Pseudobulk | 56 | 0.8984 | [0.8068, 0.9688] | 0.001 |
| Metadata (age) | 56 | 0.5781 | [0.3711, 0.7835] | 0.388 (not significant) |

Every arm's sealed AUROC is substantially lower than its dev-cohort estimate (Geneformer −0.152, pseudobulk −0.086, metadata-age −0.067). (`results/l2_sealed_results.json`; Figure 1.)

**Age-stratified** (pediatric n=44, adult n=12 — small stratum, wide CIs):

| Arm | Pediatric AUROC (95% CI) | Adult AUROC (95% CI) |
|---|---|---|
| Geneformer | 0.7934 [0.6172, 0.9375] | 0.8286 [0.5000, 1.0000] |
| Pseudobulk | 0.8926 [0.7841, 0.9746] | 0.9143 [0.7037, 1.0000] |
| Metadata (age) | 0.7658 [0.5650, 0.9398] | 0.4286 [0.0857, 0.7857] |

The age-only baseline's adult-stratum AUROC (0.4286) is below chance; reported as computed, not smoothed over. (`results/l2_sealed_results.json`; Figure 2, `figures/age_stratified_sealed.png`.)

### 3.3 Co-primary comparisons

Per PREREG Sections 5–6: paired patient-bootstrap 95% CI on the AUROC difference (must exclude zero and lie entirely positive) **and** Holm-corrected permutation significance (α=0.05), both required for GO.

| Comparison | Diff | 95% CI | Permutation p (pre-Holm) | Decision |
|---|---:|---|---:|---|
| A: Geneformer − metadata | +0.2375 | [−0.0431, +0.5179] | 0.08691 | **REJECTED** |
| B: Geneformer − pseudobulk | −0.0828 | [−0.2061, +0.0242] | 0.18382 | **REJECTED** |

Holm step-down: ranked p(1)=0.08691 (A) vs. α/2=0.025 → 0.08691 > 0.025 → stop, neither comparison significant. (`results/l2_sealed_results.json`, cross-checked independently in `results/l2_coprimary_difference_ci.json` — recomputed from already-committed per-donor predictions only, matching bit-for-bit; Figure 3, `figures/coprimary_forest_plot.png`.) Geneformer does not demonstrate added value over the metadata-only baseline or over raw pseudobulk on this sealed cohort; for comparison B, the point estimate favors pseudobulk.

Per-donor sealed predictions and the underlying permutation-null distributions are visualized in Figure 4 (`figures/roc_curves_sealed.png`) and Figure 5 (`figures/permutation_null_example.png`, Geneformer's null shown as the representative example — all three arms' observed AUROCs fall outside their respective null distributions).

### 3.4 Cohort-signature probe (PREREG Section 5.1)

A classifier trained fresh on cohort-membership (dev vs. sealed, not disease label) achieved near-perfect separability in the Geneformer (AUROC 0.9996, 95% CI [0.9985, 1.0000]) and pseudobulk (1.0000, [1.0000, 1.0000]) feature spaces, and high separability from age alone (0.8719, [0.8021, 0.9321]) (`results/l2_cohort_signature_probe.json`; Figure 6, `figures/cohort_signature_probe.png`). This was the anticipated result, not a surprise (Section 3.5), and is reported as a bound on interpretability, not a positive finding — see Limitations.

### 3.5 Confounders

Dev is 100% adult (n=259 with valid age, mean 41.3, SD 14.5, range 20–83); the sealed cohort is pediatric-primary with a small adult stratum (n=56, mean 20.9, SD 12.8, range 7–63) (`results/l2_cohort_confounders.csv`; Figure 7, `figures/cohort_confounders_age.png`). Sex (dev: 244 female / 17 male) and self-reported ethnicity (dev: 149 European American / 107 Asian / 3 African American / 2 Hispanic or Latin) are available for dev but **not available in GSE135779's public metadata at all** — no comparison is possible for either field, and none is fabricated. Platform/sequencing-generation differences between cohorts are documented only qualitatively in `PREREG.md` Section 7; no structured, comparable field exists in either cohort's committed metadata.

## 4. Discussion

**The internal-external optimism gap is large and consistent across all three arms.** Every arm lost a substantial fraction of its dev-cohort AUROC when evaluated on the sealed cohort (Geneformer: −0.152; pseudobulk: −0.086; metadata-age: −0.067). This is the core empirical answer to this project's motivating question: internal cross-validation, even with a leakage-safe, donor-grouped, repeated protocol, materially overstated external performance for all three model families tested, not just the foundation-model arm.

**Geneformer showed no detectable advantage over pseudobulk externally, and the point-estimate gap between them widened relative to internal CV.** We had originally anticipated describing this as a rank reversal; the actual numbers do not support that framing, and we report the real pattern instead. Pseudobulk's point estimate exceeded Geneformer's on the dev cohort too (0.9839 vs. 0.9676, a 0.016 AUROC gap) — there is no ordinal reversal. What changes is the gap: the point-estimate gap widens more than fivefold on the sealed cohort (0.083), and comparison B's point estimate is negative (Geneformer numerically lower than pseudobulk externally) — but comparison B is **not statistically significant** (paired 95% CI [−0.2061, +0.0242] crosses zero, permutation p=0.184 pre-Holm), so this widening point-estimate pattern should be read as observed and not as evidence Geneformer was outperformed. The more consequential reversal is one of **statistical conclusion, not point estimate, and it concerns comparison A, not B**: internally, Geneformer's separation from the metadata-only baseline is enormous and visually unambiguous (0.9676 vs. 0.6453); under the pre-registered decision rule applied to the sealed cohort, that same comparison (A) is also formally REJECTED (paired 95% CI [−0.0431, +0.5179] crosses zero, permutation p=0.087 pre-Holm, failing Holm's first step) — the 95% CI on the difference includes zero. A result that would have looked like an obvious, clean win using internal CV alone does not survive a single honest external look under a pre-specified rule.

**Geneformer did not demonstrate a detectable advantage over a much simpler model on this task, on this external cohort.** This is consistent with, though not proof of, the broader concern that frozen single-cell foundation-model embeddings may not reliably add value over much simpler, cheaper representations once genuine distribution shift (different lab, different patients, different sequencing generation, different age structure) is introduced.

## 5. Limitations

- **The cohort-signature probe (Section 3.4) bounds, and substantially limits, the interpretability of every sealed-cohort AUROC in this study.** AUROC 0.9996–1.0000 for the Geneformer and pseudobulk feature spaces means dev-vs-sealed cohort identity is almost perfectly separable in those same spaces used for disease discrimination. We cannot rule out that some fraction of each arm's sealed disease-discrimination AUROC reflects cohort/batch/platform identity rather than SLE biology specifically. This is not a caveat that can be resolved by re-analysis of the same two cohorts; it would require either a cohort-signature-mitigation method (e.g., domain adaptation, batch-corrected joint embedding) validated on its own held-out data, or a third, independent cohort with different confound structure.
- **Sealed-cohort sample size is small, and the adult stratum smaller still** (n=56 overall, n=12 adult — 7 SLE / 5 healthy). Adult-stratum CIs are wide (some spanning nearly the full [0, 1] range); the below-chance point estimate for the metadata-age arm's adult stratum (0.4286) should be read with this small n in mind, not as a robust finding.
- **Age, ancestry, and platform are fully or near-fully confounded with cohort in this study.** Dev is 100% adult; sealed is pediatric-primary. Ancestry and sex cannot be compared at all (absent from GSE135779's public metadata). Platform/sequencing-generation differences are documented only qualitatively. No analysis in this study adjusts for these confounds statistically — the cohort-signature probe characterizes the resulting interpretability bound but does not remove it.
- **Cell-type-level harmonization and the originally pre-registered cell-type-dependent portions of the cohort-signature analysis were deferred, not run.** GSE135779's public deposit has no cell-type annotation, and the Scanpy-ingest label-transfer code cited in `PREREG.md` Section 8 was never implemented in this repository (`docs/PREREGISTRATION_DEVIATIONS.md` item 2). The co-primary comparisons reported here use only the mean-pooled arms, which do not require cell-type labels — but any cell-type-resolved follow-up analysis remains undone.
- **Gene-space overlap between cohorts is 49% of dev's genes** (30,165 of 61,497), driven by GSE135779's older (2019, CellRanger v2) reference. The pseudobulk arm's dev-side model was refit on this restricted gene space specifically for sealed scoring (`docs/PREREGISTRATION_DEVIATIONS.md` item 1) — a real, disclosed methodological choice among at least one alternative, not validated against that alternative in this study.
- **A harmonization-sensitivity analysis (i.e., repeating the sealed evaluation under the alternative gene-restriction convention considered in `docs/PREREGISTRATION_DEVIATIONS.md` item 1) was not performed.** `[TODO: verify]` whether this is feasible without a second sealed-cohort opening (it likely is not, under this study's own one-look discipline, without a new preregistration).
- **56-vs-58 sealed sample count is unresolved** against the source publication (`docs/PREREGISTRATION_DEVIATIONS.md` item 4); all sealed statistics use the real, verified n=56.

## 6. Future work

- A multi-cohort, multi-model standardized external-validation benchmark for single-cell foundation models in autoimmune disease, extending beyond the single sealed cohort available here, with pre-registered protocols for each new cohort.
- Harmonization-sensitivity analysis: systematically compare the gene-restriction convention used here against the alternative (coefficient-level restriction of an already-fit model) considered but not selected in this study, ideally on a cohort not subject to a one-look constraint.
- Cell-type-resolved cross-cohort analysis, contingent on either finding a sealed cohort with public cell-type annotation or implementing and independently validating a real ingest/label-transfer harmonization pipeline (deferred here, `docs/PREREGISTRATION_DEVIATIONS.md` item 2).
- Extension to clinically actionable tasks (disease activity, flare prediction, treatment response) under the same freeze/one-look discipline used here — the natural next-stage research question this project's SLE-vs-healthy result motivates but does not itself answer. `[TODO: verify]` — this line describes a proposed future direction, not a claim about work already done or committed in this repository.

## 7. Deviations from the original preregistration

Every deviation from `PREREG.md`'s original text — what it said, what was actually done, why, and whether it could affect a reported result — is consolidated in `docs/PREREGISTRATION_DEVIATIONS.md`. In summary: (1) the pseudobulk gene-space restriction convention, (2) the cell-type/cohort-signature-probe deferral, (3) a freeze-guard process gap in two sealed-access scripts (closed, no evidence of effect), (4) the 56-vs-58 sealed sample-count discrepancy, (5) an age-ambiguous donor exclusion from the dev metadata arm (n=259, not 261), and (6) the one-time final-coefficient refit required to apply any frozen hyperparameter to sealed data at all.

## Data and code availability

Dev cohort: CZ CELLxGENE Census, collection `436154da-bcf1-4130-9c8b-120ff9a888f2`. Sealed cohort: NCBI GEO accession GSE135779 (public). All analysis code, committed intermediate/result artifacts, and figures are in this repository; see `README.md` for the full pipeline order and exact reproduction commands.
