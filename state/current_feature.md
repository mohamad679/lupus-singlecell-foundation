# Current Feature

Feature: P1-F012 - Bioinformatics Judge review of metadata validity.

Status: completed pending human review.

Allowed work:

- Review current candidate metadata for bioinformatics readiness.
- Classify assay, tissue, raw count, processed object, cell-type annotation, gene identifier, pathway, and harmonization feasibility.
- Keep all candidates as `candidate_pending_audit`.

Bioinformatics Judge decision:

- `GSE162577`: `limited_candidate`.
- `GSE137029`: `continue_audit`.
- `GSE174188`: `needs_manual_verification`.
- `436154da-bcf1-4130-9c8b-120ff9a888f2::218acb0f-9f2f-4f76-b90b-15a4b7c7f629`: `continue_audit`.

Blocking findings:

- No dataset is approved.
- Human Gate 1 remains PENDING.
- GEO cell-type annotation status is not audited.
- Gene identifier feasibility and pathway analysis feasibility require approved metadata or file inspection.
- Donor/sample metadata, batch metadata, treatment metadata, and label provenance remain unresolved.
- GEO, HCA, and CELLxGENE overlap must be resolved before cross-cohort harmonization.

Blocked work:

- Dataset downloads.
- Dataset approval.
- Human Gate 1 closure.
- Moving datasets into `selected_datasets`.
- Moving datasets into `metadata/dataset_catalog.csv` as selected or approved.
- Inferring metadata.
- Assuming raw counts, processed objects, or cell-type labels beyond explicit public metadata.
- Model implementation.
- Model training.
- Any Phase 2 work.

Acceptance criteria:

- `state/judge_reports/P1-F012_bioinformatics_judge_report.md` exists.
- `reports/tables/bioinformatics_judge_review.csv` exists.
- One bioinformatics review row exists per known candidate.
- No candidate is marked approved.
- Human Gate 1 remains PENDING.
- `selected_datasets` remains `[]`.
- `external_validation_cohort` remains TODO.
