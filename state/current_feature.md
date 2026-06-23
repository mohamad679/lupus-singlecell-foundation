# Current Feature

Feature: P1-F002 - GEO / NCBI metadata audit plan.

Status: completed pending human review.

Allowed work:

- Plan a rigorous metadata-only GEO / NCBI audit workflow for SLE, lupus, and lupus nephritis single-cell transcriptomics.
- Define GEO / NCBI search terms, metadata extraction fields, verification rules, and rejection rules.
- Build safe local scaffolding that validates schema and candidate CSV headers.
- Validate that candidate rows cannot be added without explicit accession and audit status.

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
- `metadata/geo_candidate_schema.yaml` exists.
- `reports/tables/geo_candidate_datasets.csv` exists with headers only.
- `scripts/01_geo_metadata_search_plan.py` exists and does not query the internet.
- `reports/tables/` exists.
- GEO schema and metadata search plan tests exist.
- `metadata/dataset_catalog.csv` is not populated with invented datasets.
- Human Gate 1, Dataset Feasibility Approved, remains PENDING.
