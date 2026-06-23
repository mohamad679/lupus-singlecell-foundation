# Current Feature

Feature: P1-F001 - Dataset Search Strategy.

Status: in progress.

Allowed work:

- Plan a rigorous public dataset feasibility audit for SLE, lupus, and lupus nephritis single-cell transcriptomics.
- Define search terms, sources to audit, metadata requirements, eligibility criteria, and rejection rules.
- Build safe audit scaffolding that reads existing metadata and writes planning reports.
- Validate that dataset catalog rows and accessions are not invented.

Blocked work:

- Dataset downloads.
- Dataset accession invention.
- Model implementation.
- Model training.
- Internet queries from audit scripts.
- Scientific conclusions.
- Any Phase 2 work.

Acceptance criteria:

- `docs/02_dataset_feasibility_audit.md` exists.
- `configs/data_audit.yaml` exists.
- `scripts/00_audit_datasets.py` exists and does not query the internet.
- `reports/tables/` exists.
- Config and audit safety tests exist.
- `metadata/dataset_catalog.csv` is not populated with invented datasets.
- Human Gate 1, Dataset Feasibility Approved, remains PENDING.
