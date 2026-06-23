# Current Feature

Feature: P1-F003 - CELLxGENE feasibility query plan.

Status: completed pending human review.

Allowed work:

- Plan a rigorous CELLxGENE metadata-only feasibility workflow for SLE, lupus, and lupus nephritis single-cell transcriptomics.
- Define CELLxGENE query terms, metadata extraction fields, disease ontology checks, verification rules, and rejection rules.
- Build safe local scaffolding that validates schema and candidate CSV headers.
- Validate that candidate rows cannot be added without collection ID, dataset ID, and audit status.

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
- `metadata/cellxgene_candidate_schema.yaml` exists.
- `reports/tables/cellxgene_candidate_datasets.csv` exists with headers only.
- `scripts/02_cellxgene_metadata_plan.py` exists and does not query the internet.
- `reports/tables/` exists.
- CELLxGENE schema and metadata plan tests exist.
- `metadata/dataset_catalog.csv` is not populated with invented datasets.
- Human Gate 1, Dataset Feasibility Approved, remains PENDING.
