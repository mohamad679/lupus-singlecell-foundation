# Current Feature

Feature: P1-F011 - Scientific Judge review of dataset feasibility.

Status: completed pending human review.

Allowed work:

- Review existing candidate audit artifacts.
- Classify candidate scientific status without approval.
- Identify patient-level, label, leakage, cohort-shift, disease-activity, lupus nephritis, and data-access blockers.
- Keep all candidates as `candidate_pending_audit`.

Scientific Judge decision:

- `GSE162577`: `limited_candidate`.
- `GSE137029`: `continue_audit`.
- `GSE174188`: `needs_manual_verification`.
- `436154da-bcf1-4130-9c8b-120ff9a888f2::218acb0f-9f2f-4f76-b90b-15a4b7c7f629`: `continue_audit`.

Blocking findings:

- No candidate has completed patient-level metadata verification.
- Label availability is not sufficient for training, external validation, disease-activity prediction, or lupus nephritis prediction.
- External validation roles are unresolved because GEO, HCA, and CELLxGENE overlap must be reconciled.
- Leakage risk remains high until patient, donor, sample, batch, and cohort identifiers are verified.
- Human Gate 1 remains PENDING.

Blocked work:

- Dataset downloads.
- Dataset approval.
- Human Gate 1 closure.
- Moving datasets into `selected_datasets`.
- Moving datasets into `metadata/dataset_catalog.csv` as selected or approved.
- Model implementation.
- Model training.
- Guessing patient IDs, labels, activity scores, treatment metadata, or batch metadata.
- Any Phase 2 work.

Acceptance criteria:

- `state/judge_reports/P1-F011_scientific_judge_report.md` exists.
- `reports/tables/scientific_judge_dataset_review.csv` exists.
- One scientific review row exists per known candidate.
- No candidate is marked approved.
- Human Gate 1 remains PENDING.
- `selected_datasets` remains `[]`.
- `external_validation_cohort` remains TODO.
