# P3-F011 Training Permission Decision Report

## Decision Summary

**Training permission: blocked**

**Modeling readiness: not_ready**

Real model training is not allowed. `allow_modeling`, `modeling_allowed`, and
`training_allowed` remain false. `selected_datasets` remains empty.
`external_validation_cohort` remains TODO. Phase 4 is not started.

Reason: unresolved modeling readiness blockers.

## Why Training Is Blocked

The baseline scaffold is scientifically adequate as a design framework, but
none of the eight execution-critical verification requirements is complete:

1. **Dataset selection:** no dataset is assigned for training.
2. **Label provenance:** patient-level SLE and healthy-control labels, values,
   definitions, linkage, and source provenance are unverified.
3. **Patient/donor IDs:** stable identifiers and repeated-sample relationships
   are unresolved.
4. **Split manifest readiness:** the split manifest contains headers only.
5. **Leakage check readiness:** mock utilities exist, but no real approved split
   has passed overlap and confounding checks.
6. **Training cohort suitability:** no cohort role, patient count, class
   balance, access package, or dimensionality review is approved.
7. **QC approval:** no real dataset-specific QC thresholds, reports, exclusion
   log, or human approval exists.
8. **Feature manifest readiness:** feature manifests contain headers only, and
   normalization, gene-filtering, annotation, and transformation policies are
   incomplete.

Passing scaffold tests does not establish that real data satisfy these
requirements.

## What Is Allowed Next

- Continue metadata-only and evidence-only verification.
- Inspect authoritative public metadata manually without downloading full data.
- Resolve discrepancies in patient, donor, sample, label, cohort, and access
  metadata.
- Update verification evidence only after named human review.
- Request a future training-permission re-review after every blocking condition
  has auditable evidence.

Recommendation: **continue verification, not modeling**.

## What Remains Forbidden

- Dataset downloads or preprocessing.
- Real QC, feature extraction, or split generation without separate approval.
- Logistic regression, random forest, XGBoost, or any classifier fitting.
- Predictions, metrics, calibration values, or reliability plots.
- Model, preprocessing, feature, prediction, or figure artifacts.
- Dataset or training-cohort selection without explicit human approval.
- External validation cohort assignment.
- Phase 4.
- Foundation models, DeepSets, MIL, or other deep learning.
- Uncertainty, abstention, selective prediction, or clinical utility claims.

## Exact Conditions Required to Unblock Training

Training may be reconsidered only when all conditions below are met:

- `dataset_selection` is verified with authoritative IDs, access, scope,
  overlap review, and explicit human assignment.
- `label_provenance` is verified at patient or linked-sample level.
- `patient_or_donor_id_availability` is verified, including repeated samples
  and cross-source overlap.
- `split_manifest_readiness` is verified with a populated patient-, donor-, or
  cohort-level manifest.
- `leakage_check_readiness` is verified with passed real overlap, duplicate,
  cohort, batch, and label checks.
- `training_cohort_suitability` is verified using patient counts, class balance,
  tissue, assay, treatment, batch, access, and dimensionality evidence.
- `qc_approval` is verified with dataset-specific reports, threshold rationale,
  before/after counts, exclusions, and a named approver.
- `feature_manifest_readiness` is verified with populated audited manifests and
  finalized transformation policies.
- Every blocking Modeling Readiness Gate row is marked passed through an
  evidence review.
- A new explicit human Training Permission Decision authorizes the restricted
  baseline scope.

Foundation models and uncertainty modeling require separate future gates even
if baseline training is later approved.

## Recommendation

Continue verification, not modeling. Phase 3 planning and readiness review are
complete with training denied. The project must remain in the blocked state
until new evidence justifies a fresh decision.
