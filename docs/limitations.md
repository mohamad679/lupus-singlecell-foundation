# Limitations and Next Steps

## Scope

This repository supports a pre-registered, frozen, one-look external
validation of frozen Geneformer donor-level embeddings against raw
pseudobulk counts and donor age alone, for discriminating SLE from
healthy control. Results below cover the development-cohort (Perez et
al. 2022) internal cross-validation and the sealed external cohort
(GSE135779, Nehar-Belaid et al. 2020) evaluation.

## Current limitations

### 1. Cohort-signature separability bounds interpretation

Development and sealed donors are separable at AUROC 0.9996 (Geneformer
feature space) and 1.0000 (pseudobulk feature space) — the same feature
spaces used for disease classification. We cannot exclude that some
fraction of each arm's sealed disease AUROC reflects cohort, batch, or
platform identity rather than SLE biology. This bound cannot be removed
by re-analyzing the same two cohorts; it would require a cohort-signature
mitigation method validated on its own held-out data, or a third
independent cohort with a different confound structure.

### 2. Small sealed cohort, smaller adult stratum

The sealed cohort is n=56 overall; the adult stratum is n=12 (7 SLE / 5
healthy). Adult-stratum confidence intervals are wide (several span most
of the unit interval), and 4 of 5000 bootstrap resamples were degenerate
in each arm at this stratum (0 in the pediatric stratum and overall). The
below-chance adult point estimate for the age arm (AUROC 0.4286) should
be read against this n=12, not as a robust finding.

### 3. Age, ancestry, and platform confounded with cohort

The development cohort is entirely adult; the sealed cohort is
pediatric-primary. This age-structure confound is pre-registered
(`PREREG.md` §7), not a post-hoc observation. Sex and ancestry cannot be
compared across cohorts, since neither appears in GSE135779's public
metadata. The platform difference between cohorts is documented only
qualitatively, from the two source publications; no structured,
comparable platform field exists in either cohort's committed metadata.
No analysis here adjusts for these confounds statistically; the
cohort-signature probe (Limitation 1) characterizes the resulting bound
but does not remove it.

### 4. Cell-type-resolved analysis deferred, not performed

GSE135779's public deposit carries no cell-type annotation, and the
Scanpy-ingest / k-NN label-transfer protocol specified in `PREREG.md` §8
was never implemented (`src/data/metadata_harmonization.py` remains an
unimplemented schema-validation stub;
`docs/PREREGISTRATION_DEVIATIONS.md` item 2). The co-primary comparisons
use only the donor-level mean-pooled arms (Geneformer, pseudobulk), which
require no cell-type labels, so this deferral does not affect them — but
the entire cell-type-resolved layer of the pre-registered plan, including
the cell-type-dependent portion of the cohort-signature analysis, is
undone.

### 5. Gene-space intersection and its downstream effects

The gene-space intersection between cohorts is 30,165 genes (49.05% of
the development reference's 61,497 genes; 92.14% of the sealed
reference's 32,738 genes), limited by GSE135779's older annotation,
recorded here as repository provenance rather than independently
re-verified from GEO. For sealed scoring, the pseudobulk arm was
restricted to this intersection by restricting the raw count matrix
before re-normalizing (one of two possible conventions;
`docs/PREREGISTRATION_DEVIATIONS.md` item 1). A dedicated post-hoc check
(item 10) established that this restriction is not itself responsible
for the pseudobulk optimism gap: repeating the development nested
cross-validation in the restricted gene space changed AUROC by only
+0.0012 (paired 95% CI −0.0004 to +0.0032; permutation test for this arm
still pending). That same check found the frozen pseudobulk
regularization strength (C=0.01, selected in the full gene space) would
have been C=0.1 had it been selected in the restricted space actually
used for sealed scoring (item 10) — retained rather than revised, since
altering it post-freeze would defeat the protocol.

### 6. Frozen pseudobulk hyperparameter is seed-fragile

Independent of the gene-space issue above, the frozen pseudobulk C=0.01
is reproduced in 0 of 10 reseeded repeats of the same selection procedure
(landing on C=0.1 or C=1.0 instead); the Geneformer (6/10) and age
(10/10) hyperparameters are comparatively more stable
(`docs/PREREGISTRATION_DEVIATIONS.md` item 9). No hyperparameter was
altered after the freeze in any arm.

### 7. Harmonization-sensitivity analysis not performed

Repeating the sealed evaluation under the alternative
coefficient-restriction convention (Limitation 5) was not performed, and
in our judgment could not be performed under this study's one-look
discipline without a fresh preregistration and a second sealed opening,
since `scripts/freeze_guard.py` blocks further sealed-cohort access under
the current freeze.

### 8. Unresolved sample-count discrepancy

The sealed cohort's public deposit carries per-sample records for 56
donors, against 58 described in the source publication; we could not
reconcile the two against the publication's supplementary materials
(`docs/PREREGISTRATION_DEVIATIONS.md` item 4). All sealed statistics in
this repository use the verified n=56.

## Clinical claim boundary

The repository does not support claims of:

- diagnostic readiness
- clinical deployment
- clinical decision support
- treatment recommendation
- generalization beyond the one sealed cohort evaluated here

## Embedding interpretation boundary

The Geneformer arm's downstream classifier operates on frozen
donor-level embeddings, not raw gene-level features. Logistic-regression
coefficients or embedding-dimension weights computed on that classifier
must not be interpreted as gene-level importance. Gene-level biological
plausibility would require upstream Geneformer-level analysis (e.g. in
silico gene or gene-program perturbation before embedding extraction,
followed by re-embedding and fixed-classifier re-scoring); no such
analysis has been performed here, and any future such analysis would
support mechanistic plausibility only, not external or clinical
validation.

## Next scientific steps

1. Land `docs/PREREGISTRATION_DEVIATIONS.md` items 9-10 and this
   document's rewrite on `main`.
2. Complete the manuscript's Step 4 end-to-end adversarial consistency
   pass.
3. If a follow-up study is pursued, identify a second independent sealed
   cohort under a fresh preregistration.

## Superseded: earlier flare-discrimination phase

An earlier phase of this repository evaluated frozen Geneformer
patient-level embeddings for active-SLE-flare discrimination (14
flare-positive patients, leave-one-patient-out cross-validation, no
external validation). `PREREG.md` §9 formally demotes this flare task to
a secondary, internal-only analysis, superseded by the SLE-vs-healthy
sealed-validation study described above. The flare task's own
limitations (small flare class, no external validation, cross-sectional
task definition, no baseline comparison performed) are retained here for
provenance only and are not part of this study's primary or co-primary
claims.
