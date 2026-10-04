# P3-F017 Training Permission Re-evaluation

## Executive Summary

The Scientific Judge reviewed the P3-F016 Modeling Readiness Re-check and the
supporting P3-F015 metadata evidence.

Final decision:

- `training_permission`: `blocked`
- `allow_modeling`: false
- `decision`: `continue_metadata_inspection`
- `pivot_status`: `not_activated`
- `phase4_permission`: `blocked`

No dataset is selected and no external-validation cohort is assigned.

## Final Phase 3 Readiness Decision

The project is not ready for real training. No blocking readiness condition
passed during P3-F016. Repository-level metadata improved, but the project
still lacks the person-level relationships required for valid patient-level
prediction.

Phase 3 may continue only through controlled evidence work or dataset strategy
reassessment. Phase 4 is not permitted.

## Why Training Remains Blocked

### Dataset Selection

GSE137029 remains an unselected candidate. The current evidence does not
support a human-approved training role.

### Label Provenance

GEO sample-level `condition` values and CELLxGENE aggregate disease terms are
documented. Complete patient/donor-to-label linkage, missingness, definitions,
and class counts are not verified.

### Patient/Donor Mapping

No explicit GSE137029 patient/donor mapping is available in inspected metadata.
CELLxGENE exposes `donor_id`, but donor-to-sample and donor-to-diagnosis
relationships remain unresolved.

### Split Manifest

The split manifest is header-only. A patient/donor-level split cannot be
created without verified person identifiers and repeated-sample relationships.

### Leakage Checks

Mock checks exist, but no real split exists. Exact donor/sample/cell overlap
among GEO, HCA, and CELLxGENE remains unresolved.

### QC Approval

File manifests and processing descriptions are not dataset-specific QC
approval. Thresholds, before/after counts, exclusions, and named approval are
missing.

### Feature Manifest

Feature manifests remain header-only. No approved patient-level feature data
exist.

### External Validation

The evaluation framework is documented, but no cohort is assigned.
CELLxGENE/HCA is linked to GSE137029 and cannot be treated as independent.

## Evidence Still Required

- stable patient/donor identifiers;
- complete sample-to-person relationships;
- verified person-to-diagnosis/comparator linkage;
- missingness, uniqueness, repeated-sample, and class-count review;
- exact cross-repository overlap evidence;
- selected training cohort with explicit human approval;
- approved QC summaries and threshold decisions;
- populated patient/donor-level split manifest;
- passed real leakage checks;
- populated and audited feature manifest;
- independent external-validation cohort evidence.

## Allowed Next Work

- controlled metadata inspection;
- metadata evidence expansion;
- review of source-provided data dictionaries or mapping manifests;
- dataset strategy reassessment planning;
- future permission re-evaluation after new evidence.

Allowed work must remain metadata-only unless a separate human gate explicitly
changes access permissions.

## Forbidden Work

- full-data download;
- preprocessing or QC execution on real data;
- real split creation;
- feature extraction;
- model fitting, prediction, or evaluation;
- model artifact creation;
- dataset selection;
- external-validation assignment;
- Phase 4 start;
- metadata inference;
- pivot activation without a separate decision.

## Pivot Trigger Conditions

Pivot planning should be considered only if one or more of the following are
established after controlled evidence expansion:

- explicit patient/donor mappings cannot be obtained;
- patient/donor-to-label linkage remains unverifiable;
- leakage-safe patient-level splitting is impossible;
- required metadata can be accessed only through prohibited inference or
  inaccessible full-data inspection;
- no scientifically defensible training cohort can be selected.

These trigger conditions are documented, but pivot is not activated by this
feature.

## Recommendation

Continue controlled metadata inspection before any modeling.

If the required mappings remain unavailable after the next evidence expansion,
submit a separate dataset strategy decision or pivot gate. Training and Phase 4
remain blocked.

