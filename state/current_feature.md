# Current Feature

Feature: P1-F008 - Dataset feasibility report template.

Status: completed pending human review.

Allowed work:

- Define a manuscript-grade reporting framework for Phase 1 dataset feasibility review.
- Create report template, rejected dataset log headers, and safe local report generation scaffolding.
- Read local audit tables without approving datasets or changing Human Gate 1.

Blocked work:

- Dataset downloads.
- Dataset accession invention.
- Invented metadata.
- Guessed patient labels.
- Invented labels.
- Inferred disease activity labels.
- Invented patient IDs.
- Invented cohort labels.
- Cell-level splitting.
- Cell-level train/test split.
- Model implementation.
- Model training.
- Approving datasets.
- Approving a cohort without audit.
- Changing Human Gate 1.
- Clinical overclaiming.
- Internet queries from audit scripts.
- Scientific conclusions.
- Any Phase 2 work.

Acceptance criteria:

- `docs/02_dataset_feasibility_audit.md` exists.
- `reports/final_dataset_feasibility_report.md` exists.
- `reports/tables/rejected_dataset_log.csv` exists with headers only.
- `scripts/07_generate_dataset_feasibility_report.py` exists and does not query the internet.
- `reports/tables/` exists.
- Dataset feasibility report template, rejected log, and generator tests exist.
- `metadata/dataset_catalog.csv` is not populated with invented datasets.
- No dataset is approved.
- No dataset rows are invented.
- Human Gate 1, Dataset Feasibility Approved, remains PENDING.
