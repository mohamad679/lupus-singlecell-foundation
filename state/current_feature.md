# Current Feature

Feature: P1-F007 - External validation candidate criteria.

Status: completed pending human review.

Allowed work:

- Define criteria for deciding whether a candidate dataset can serve as an external validation cohort.
- Create external validation criteria, candidate table headers, and safe local validation scaffolding.
- Validate manually created external validation rows without approving a cohort or creating dataset rows.

Blocked work:

- Dataset downloads.
- Dataset accession invention.
- Guessed patient labels.
- Invented labels.
- Inferred disease activity labels.
- Invented patient IDs.
- Invented cohort labels.
- Cell-level splitting.
- Cell-level train/test split.
- Model implementation.
- Model training.
- Approving a cohort without audit.
- Clinical overclaiming.
- Internet queries from audit scripts.
- Scientific conclusions.
- Any Phase 2 work.

Acceptance criteria:

- `docs/02_dataset_feasibility_audit.md` exists.
- `metadata/external_validation_criteria.yaml` exists.
- `reports/tables/external_validation_candidates.csv` exists with headers only.
- `scripts/06_external_validation_audit.py` exists and does not query the internet.
- `reports/tables/` exists.
- External validation criteria and audit tests exist.
- `metadata/dataset_catalog.csv` is not populated with invented datasets.
- No external validation cohort is approved.
- No external validation candidate rows are invented.
- Human Gate 1, Dataset Feasibility Approved, remains PENDING.
