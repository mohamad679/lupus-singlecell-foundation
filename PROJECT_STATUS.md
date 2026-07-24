# Project Status

Current claim boundary: donor-level 5-fold nested cross-validation on a
development cohort, plus one pre-registered, sealed, one-look external
validation. No clinical claim. External validation is complete for one
independent cohort (not "not complete" — see below); a second external
cohort has not been evaluated.

## Current repository status

The repository implements a preregistered, frozen, sealed-cohort external
validation of whether frozen Geneformer donor-level embeddings
discriminate systemic lupus erythematosus (SLE) from healthy control
beyond raw pseudobulk counts and donor age alone.

Current completed state:

- `PREREG.md` (tag `prereg-locked-v1`) fixes the primary task, three model
  arms, two co-primary comparisons, decision rule, Holm procedure, and
  pre-declared confounds, committed before any development data were
  loaded.
- Development-cohort (Perez et al. 2022, via CZ CELLxGENE Census; 261
  donors, 162 SLE / 99 healthy) donor-level 5-fold nested cross-validation
  completed for all three arms (Geneformer, pseudobulk, metadata-age).
- `FREEZE.json` SHA-256-hashes every file determining a sealed-cohort
  prediction, together with each arm's frozen hyperparameter, at commit
  `44d6f567670829527a6efa39c2d968c20e8d5515`.
- The sealed external cohort (GSE135779, Nehar-Belaid et al. 2020; 56
  donors with public per-sample records, 40 SLE / 16 healthy) was opened
  exactly once (`SEALED_OPENED.json`, 2026-07-21T06:50:41Z) and scored
  under the frozen protocol.
- Both pre-specified co-primary comparisons (Geneformer vs. metadata-age;
  Geneformer vs. pseudobulk) were REJECTED under the pre-specified rule
  (paired donor-bootstrap 95% CI plus Holm-corrected permutation
  significance) — Geneformer showed no statistically significant
  external advantage over either baseline.
- A cohort-signature probe (post-hoc; pre-declared in `PREREG.md` §5.1
  but deferred at freeze time — see
  `docs/PREREGISTRATION_DEVIATIONS.md` items 2 and 7) found development
  and sealed donors separable at AUROC 0.9996-1.0000 in both
  transcriptomic feature spaces, bounding how much of any sealed result
  can be attributed to disease biology rather than cohort identity.
- A dev-only sensitivity check (`docs/PREREGISTRATION_DEVIATIONS.md`
  item 10) confirmed the pseudobulk optimism gap is not an artifact of
  the gene-space restriction used for sealed scoring.
- Manuscript drafting in progress, targeting BMC Bioinformatics (all six
  sections drafted and under review as of this status).

## Current authoritative implementation

- Development-cohort CV: `scripts/15_l2_dev_cv_pseudobulk_metadata.py`,
  `kaggle_kernels/l2_geneformer_full/`
- Freeze manifest and guard: `FREEZE.json`, `scripts/freeze_guard.py`
- Sealed-cohort scoring: outputs recorded in `results/l2_sealed_results.json`,
  `SEALED_OPENED.json`
- Co-primary comparison and Holm correction:
  `results/l2_coprimary_difference_ci.json`

## Current claim boundary

The repository supports the following conservative statement:

> Under a pre-registered, frozen, one-look external-validation protocol,
> frozen Geneformer donor-level embeddings showed no statistically
> significant advantage over either a raw-pseudobulk or a donor-age-only
> baseline in discriminating SLE from healthy control on one independent,
> sealed single-cell cohort (n=56). The optimism gap between internal
> cross-validation and external performance was present in all three
> arms, including the two that use no foundation model.

The repository does not support claims of:

- clinical deployment
- diagnostic readiness
- treatment recommendation
- generalization beyond the one sealed cohort evaluated here
- generalized clinical decision support

## Validation status

- Development-cohort donor-level nested CV: complete, all three arms
- Sealed external validation: complete for one independent cohort
  (GSE135779); a second independent cohort has not been evaluated and
  would require a fresh preregistration under this study's one-look
  discipline
- Clinical validation: not attempted; out of scope
- Prospective validation: not attempted; out of scope

## Next scientific work

1. Land the two outstanding preregistration-deviations updates
   (`docs/PREREGISTRATION_DEVIATIONS.md` items 9 and 10) and this
   document's rewrite on `main` before manuscript submission.
2. Complete the Step 4 end-to-end adversarial pass over the assembled
   manuscript (cross-section numeric consistency, residual-flag sweep).
3. Prepare the cover letter and submit to BMC Bioinformatics; prepare a
   condensed (~200-word) abstract if a Scientific Reports submission is
   pursued instead or afterward.
4. Longer-term: identify a second independent sealed cohort if a
   follow-up study is pursued; this would require a new preregistration,
   since the current freeze and one-look discipline are specific to
   GSE135779.

## Documentation

- `README.md`
- `PREREG.md`, `FREEZE.json`, `SEALED_OPENED.json`
- `docs/PREREGISTRATION_DEVIATIONS.md`
- `docs/limitations.md`
- `MANUSCRIPT.md`

## Interpretation boundary

Downstream logistic-regression coefficients or embedding-dimension
weights are not gene-level importance measures: the classifier operates
on donor-level Geneformer-derived embeddings (or, for the pseudobulk arm,
on gene-level counts, but without a validated attribution method) rather
than on a representation designed for per-gene interpretation.

## Gene masking boundary

Gene masking is not valid on the downstream logistic-regression
classifier for the Geneformer arm. Gene or gene-program perturbation
must occur upstream, before Geneformer embedding extraction, followed by
re-embedding and fixed-classifier re-scoring. No such analysis has been
performed in this study.

## Superseded: earlier flare-discrimination phase

An earlier phase of this repository (Stage 7, prior to the current
preregistered SLE-vs-healthy design) evaluated frozen Geneformer
patient-level embeddings for active-SLE-flare discrimination using
leave-one-patient-out cross-validation on 14 flare-positive patients, with
no external validation. `PREREG.md` §9 formally demotes this flare task
to a secondary, internal-only analysis; it is not part of this study's
primary or co-primary claims and is retained here only for provenance.
The claim boundary, validation status, and next-steps sections above
describe the current, primary SLE-vs-healthy study and supersede any
flare-task statement made under the earlier phase.
