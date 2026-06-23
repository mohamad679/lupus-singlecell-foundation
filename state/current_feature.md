# Current Feature

Feature: P1-F006 - Label availability audit schema.

Status: completed pending human review.

Allowed work:

- Define label availability requirements for patient-level prediction task feasibility.
- Create label dictionary, label availability schema, audit table headers, and safe local validation scaffolding.
- Validate manually created label audit rows without inventing labels, inferring disease activity, or creating dataset rows.

Blocked work:

- Dataset downloads.
- Dataset accession invention.
- Guessed patient labels.
- Invented labels.
- Inferred disease activity labels.
- Invented patient IDs.
- Cell-level splitting.
- Model implementation.
- Model training.
- Clinical overclaiming.
- Internet queries from audit scripts.
- Scientific conclusions.
- Any Phase 2 work.

Acceptance criteria:

- `docs/02_dataset_feasibility_audit.md` exists.
- `metadata/label_dictionary.yaml` exists.
- `metadata/label_availability_schema.yaml` exists.
- `reports/tables/label_availability_audit.csv` exists with headers only.
- `scripts/05_label_availability_audit.py` exists and does not query the internet.
- `reports/tables/` exists.
- Label dictionary, schema, and audit tests exist.
- `metadata/dataset_catalog.csv` is not populated with invented datasets.
- No label rows are invented.
- Human Gate 1, Dataset Feasibility Approved, remains PENDING.
