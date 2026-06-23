# Current Feature

Feature: P2-F006 - Patient-level split protocol.

Status: completed pending human review.

Builder scope:

- Define split policy and validation scaffold only.
- Create local split config, a header-only split manifest, mock-safe validation utilities, documentation, and tests.
- Enforce patient-level, donor-level, and cohort-level split units only.

Explicitly forbidden:

- Cell-level splits.
- Barcode-level splits.
- Downloads.
- Preprocessing real data.
- Creating real AnnData outputs.
- Modeling.
- Training.
- Model files.
- Dataset approval.
- Creating real train/test assignments.
- Creating `selected_datasets`.
- Assigning `external_validation_cohort`.

Split scaffold summary:

- Allowed split units are `patient_id`, `donor_id`, and `cohort_id`.
- Forbidden split units are `cell_id` and `barcode`.
- Cell-level splitting is disabled.
- Future external validation requires cohort holdout.
- Mock split manifests must include `audit_status`.
- Train/test entity overlap is rejected.

Acceptance criteria:

- `configs/splitting.yaml` exists.
- `reports/tables/split_manifest.csv` exists with headers only.
- `src/data/split_policy.py` exists.
- `tests/test_patient_split_policy.py` exists and passes.
- No data is downloaded.
- No real split is created.
- No modeling code is created.
- `selected_datasets` remains `[]`.
- `external_validation_cohort` remains TODO.
