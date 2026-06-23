# Current Feature

Feature: P2-F008 - Cohort manifest design.

Status: completed pending human review.

Builder scope:

- Define cohort manifest schema and validation only.
- Create an empty manifest table, mock-safe validation utilities, documentation, and tests.
- Track candidate datasets, cohorts, samples, batches, tissues, assay types, access restrictions, and intended roles.

Explicitly forbidden:

- Downloads.
- Preprocessing.
- Creating real AnnData outputs.
- Modeling.
- Training.
- Model files.
- Cohort approval.
- Official training cohort assignment.
- Official external validation cohort assignment.
- Moving datasets into `selected_datasets`.
- Assigning `external_validation_cohort`.

Manifest scaffold summary:

- `intended_role` is planning metadata only.
- `approved_role` must be `TODO` or `none` unless `human_gate_approved` is explicitly true in a mock validation row.
- Every row requires `provenance_url` and `audit_status`.
- The manifest CSV is headers-only and contains no approved rows.

Acceptance criteria:

- `metadata/cohort_manifest_schema.yaml` exists.
- `metadata/cohort_manifest.csv` exists with headers only.
- `src/data/cohort_manifest.py` exists.
- `tests/test_cohort_manifest_schema.py` and `tests/test_cohort_manifest_validation.py` exist and pass.
- No data is downloaded.
- No cohort is approved.
- `selected_datasets` remains `[]`.
- `external_validation_cohort` remains TODO.
