# Current Feature

Feature: P2-F009 - Candidate dataset access plan.

Status: completed pending human review.

Builder scope:

- Data access planning only.
- Create access metadata, a two-row access-plan table, a local validator script, documentation, and tests.
- Keep GSE137029 and CELLxGENE/HCA as planning candidates only.

Explicitly forbidden:

- Actual downloads.
- Network fetch commands.
- Preprocessing.
- Creating AnnData objects.
- Modeling.
- Training.
- Model files.
- Dataset approval.
- External validation assignment.
- Creating `selected_datasets`.
- Assigning `external_validation_cohort`.

Access scaffold summary:

- `approved_for_download` is false for every candidate.
- `approved_for_modeling` is false for every candidate.
- Future acquisition requires file-list, metadata, access, storage, checksum, and human-gate checks.
- Audit status is `pending_human_download_gate`.

Acceptance criteria:

- `metadata/dataset_access_plan.yaml` exists.
- `reports/tables/dataset_access_plan.csv` exists with exactly two candidate rows.
- `scripts/09_validate_dataset_access_plan.py` exists and validates gates locally.
- `tests/test_dataset_access_plan.py` exists and passes.
- No data is downloaded.
- `approved_for_download` remains false.
- `approved_for_modeling` remains false.
- `selected_datasets` remains `[]`.
- `external_validation_cohort` remains TODO.
