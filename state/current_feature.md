# Current Feature

Feature: P1-F005 - Patient-level metadata audit schema.

Status: completed pending human review.

Allowed work:

- Define metadata requirements for patient-level prediction and leakage-free cohort splitting.
- Create patient metadata schema, audit table headers, and safe local validation scaffolding.
- Validate manually created audit rows without inventing labels, patient IDs, or dataset rows.

Blocked work:

- Dataset downloads.
- Dataset accession invention.
- Guessed patient labels.
- Invented patient IDs.
- Cell-level splitting.
- Model implementation.
- Model training.
- Internet queries from audit scripts.
- Scientific conclusions.
- Any Phase 2 work.

Acceptance criteria:

- `docs/02_dataset_feasibility_audit.md` exists.
- `metadata/patient_metadata_schema.yaml` exists.
- `reports/tables/patient_metadata_audit.csv` exists with headers only.
- `scripts/04_patient_metadata_audit.py` exists and does not query the internet.
- `reports/tables/` exists.
- Patient metadata schema and audit tests exist.
- `metadata/dataset_catalog.csv` is not populated with invented datasets.
- No patient metadata rows are invented.
- Human Gate 1, Dataset Feasibility Approved, remains PENDING.
