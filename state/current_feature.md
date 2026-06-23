# Current Feature

Feature: P2-F007 - Leakage prevention tests.

Status: completed pending human review.

Builder scope:

- Create leakage validation utilities and tests only.
- Validate mock row dictionaries for future patient-level single-cell prediction.
- Cover cell-level leakage, patient/donor/sample overlap, cohort contamination, batch leakage, label leakage, and duplicated cell/barcode leakage.

Explicitly forbidden:

- Downloads.
- Real preprocessing.
- Real train/test splits.
- Cell-level split assignments.
- Creating real AnnData outputs.
- Modeling.
- Training.
- Model files.
- Dataset approval.
- Creating `selected_datasets`.
- Assigning `external_validation_cohort`.

Leakage scaffold summary:

- Cell-level and barcode-level entity types are rejected.
- Patient, donor, and sample IDs cannot appear in more than one split.
- Duplicate cell IDs across splits are rejected.
- Batch-only split partitions are flagged.
- Labels perfectly tied to split partitions are flagged.
- Every mock row requires `audit_status`.

Acceptance criteria:

- `src/data/leakage_checks.py` exists.
- `tests/test_leakage_checks.py` exists and passes.
- No data is downloaded.
- No real split is created.
- No modeling code is created.
- `selected_datasets` remains `[]`.
- `external_validation_cohort` remains TODO.
