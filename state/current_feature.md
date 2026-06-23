# Current Feature

Feature: P1-F004 - Dataset eligibility scoring schema.

Status: completed pending human review.

Allowed work:

- Define a scoring framework for evaluating SLE, lupus, and lupus nephritis single-cell dataset eligibility.
- Create scoring schema, score output headers, and safe local validation scaffolding.
- Validate candidate tables without inventing candidates or assigning eligibility to unaudited rows.

Blocked work:

- Dataset downloads.
- Dataset accession invention.
- Guessed patient labels.
- Model implementation.
- Model training.
- Internet queries from audit scripts.
- Scientific conclusions.
- Any Phase 2 work.

Acceptance criteria:

- `docs/02_dataset_feasibility_audit.md` exists.
- `configs/data_audit.yaml` exists.
- `metadata/dataset_eligibility_scoring.yaml` exists.
- `reports/tables/dataset_eligibility_scores.csv` exists with headers only.
- `scripts/03_score_dataset_eligibility.py` exists and does not query the internet.
- `reports/tables/` exists.
- Dataset eligibility scoring tests exist.
- `metadata/dataset_catalog.csv` is not populated with invented datasets.
- No unaudited candidates are scored as eligible.
- Human Gate 1, Dataset Feasibility Approved, remains PENDING.
