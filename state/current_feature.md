# Current Feature

Feature: P1-F010 - Manual metadata audit of candidate datasets.

Status: completed pending human review.

Allowed work:

- Audit existing candidate rows using public metadata only.
- Record exact source URLs and explicitly verified metadata.
- Mark unknown or unresolved fields as `TODO` or `unclear`.
- Add candidate-only audit summaries.
- Keep all candidates as `candidate_pending_audit`.

Completed candidate-only audit:

- `reports/tables/geo_candidate_datasets.csv` updated with explicit GEO/dbGaP metadata and unresolved fields.
- `reports/tables/cellxgene_candidate_datasets.csv` updated with explicit CELLxGENE/HCA metadata and unresolved fields.
- `reports/tables/manual_metadata_audit_summary.csv` created with one pending row per known candidate.
- `reports/tables/dataset_eligibility_scores.csv` contains unresolved preliminary rows only; no score or eligibility category is assigned.
- `reports/final_dataset_feasibility_report.md` includes a manual metadata audit summary.

Blocked work:

- Dataset downloads.
- Dataset accession invention.
- Invented metadata.
- Guessed patient IDs.
- Guessed labels.
- Inferred disease activity labels.
- Invented treatment metadata.
- Invented batch metadata.
- Cell-level splitting.
- Cell-level train/test split.
- Model implementation.
- Model training.
- Moving datasets into `metadata/dataset_catalog.csv` as selected or approved.
- Approving datasets.
- Approving an external validation cohort.
- Changing Human Gate 1.
- Any Phase 2 work.

Scientific Judge note:

- Candidates are real public metadata candidates but are not approved datasets.
- Manual metadata audit was completed as candidate-only.
- No datasets were approved.
- Patient-level usability remains unresolved.
- Label availability remains unresolved.
- External validation role remains unresolved.
- Unresolved patient-level and label fields remain blockers for Human Gate 1.

Acceptance criteria:

- `reports/tables/manual_metadata_audit_summary.csv` exists.
- One manual audit summary row exists per known candidate.
- Candidate rows remain `candidate_pending_audit`.
- No dataset is approved.
- No full data are downloaded.
- No model code is created.
- Human Gate 1, Dataset Feasibility Approved, remains PENDING.
