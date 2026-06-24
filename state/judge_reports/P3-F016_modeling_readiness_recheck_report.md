# P3-F016 Modeling Readiness Re-check

## Executive Summary

The Scientific Judge re-checked modeling readiness after the P3-F015
metadata-only evidence review.

Decision: `not_ready`.

Recommendation: `more_metadata_inspection_required`.

No blocking readiness condition is resolved. P3-F015 verified useful
repository-level facts, including the GSE137029 sample-level `condition` field,
CELLxGENE `donor_id` field visibility, file manifests, and linked
GEO/HCA/CELLxGENE provenance. Those facts do not establish the complete
patient/donor-to-label relationships required for patient-level training.

`training_permission` remains `blocked`, `allow_modeling` remains false, no
dataset is selected, and no external-validation cohort is assigned.

## Evidence Reviewed

- `reports/tables/metadata_inspection_evidence_log.csv`
- `reports/tables/dataset_selection_verification.csv`
- `reports/tables/label_provenance_verification.csv`
- `reports/tables/patient_id_verification.csv`
- `reports/tables/modeling_readiness_checklist.csv`
- `state/modeling_readiness_gate.yaml`
- `state/training_permission_decision.yaml`
- `state/metadata_inspection_gate.yaml`
- `docs/10_dataset_selection_and_label_verification.md`
- `docs/11_patient_id_label_provenance_evidence_plan.md`
- `docs/12_controlled_metadata_inspection_plan.md`
- `state/judge_reports/P3-F015_dataset_label_evidence_review.md`

## Blockers Resolved

No training-blocking condition moved to passed.

Supporting facts clarified by P3-F015:

- GSE137029 exposes sample-level `condition` values in inspected GEO Samples.
- GSE137029 raw and processed resources have public manifests.
- CELLxGENE exposes a `donor_id` field and aggregate normal/SLE terms.
- Official sources establish linked provenance between GSE137029 and the
  CELLxGENE/HCA resource.

These facts narrow future evidence requirements but do not satisfy a complete
readiness condition.

## Blockers Remaining

- dataset selection;
- patient/donor-linked diagnosis and comparator provenance;
- stable patient/donor identifiers with sample and repeated-measure linkage;
- patient/donor-level split manifest;
- real leakage checks and exact cross-repository overlap resolution;
- approved training-cohort suitability;
- dataset-specific QC approval;
- populated and audited feature manifest.

## Dataset Selection Status

Status: pending and blocking.

GSE137029 remains a candidate for further verification, not a selected
training dataset. Patient/donor identifiers, complete sample linkage, class
counts, QC approval, and leakage-safe grouping remain unresolved.

CELLxGENE/HCA is not an independent second candidate for external validation.
Official metadata link it to GSE137029, while exact donor/sample/cell overlap
remains unresolved.

## Label Provenance Status

Status: pending and blocking.

GSE137029 has an explicit sample-level `condition` field in inspected GEO
records. Completeness across all records and linkage to stable patients or
donors are not verified.

CELLxGENE exposes aggregate normal and SLE vocabularies, but no donor-to-disease
mapping was exposed in the reviewed aggregate metadata.

Disease activity, flare modeling, and lupus nephritis remain blocked.

## Patient/Donor ID Status

Status: pending and blocking.

No explicit GSE137029 patient/donor field or complete sample-to-person mapping
was exposed.

CELLxGENE `donor_id` field visibility is verified, but sample relationships,
missingness, repeated samples, and donor-to-label linkage remain unresolved.

## Split Manifest Status

Status: pending and blocking.

The split manifest remains header-only. A split cannot be populated until
stable person identifiers, sample relationships, and labels are verified.
Cell-level splitting remains prohibited.

## Leakage Check Status

Status: pending and blocking.

Mock leakage utilities exist, but no real patient-level split exists.
Source-level linkage among GEO, HCA, and CELLxGENE is verified; exact
donor/sample/cell overlap is not.

## QC Approval Status

Status: pending and blocking.

Processing descriptions and asset manifests indicate that future QC may be
possible. They do not provide dataset-specific QC summaries, approved
thresholds, before/after counts, exclusions, or a named human approval.

## Feature Manifest Status

Status: pending and blocking.

Pseudobulk and cell-type feature manifests remain header-only. No approved
dataset, QC output, patient grouping, normalization policy, or real feature
record exists.

## External Validation Status

The external-validation planning framework remains passed as a documented,
nonblocking protocol condition.

The external-validation cohort assignment remains TODO. CELLxGENE/HCA is
linked to GSE137029 and cannot be assigned as independent validation without
record-level overlap evidence.

## Recommendation

Recommendation: `more_metadata_inspection_required`.

The next evidence must come from a metadata-only mapping asset or data
dictionary that explicitly exposes:

- stable patient/donor identifiers;
- complete sample-to-person relationships;
- person-to-diagnosis/comparator linkage;
- missingness, uniqueness, repeats, and class counts;
- exact cross-repository overlap.

If those relationships cannot be established without prohibited full-data
access or inference, a future judge should recommend a pivot to a dataset with
explicit patient-level metadata.

Real training cannot be considered now. Phase 4 is not started.

