# Current Feature

Feature: P1-F009 - Real GEO / HCA / CELLxGENE candidate discovery, metadata-only.

Status: completed pending human review.

Allowed work:

- Add real candidate lupus single-cell datasets to candidate audit tables using verified public metadata only.
- Record source URLs and mark all candidates as `candidate_pending_audit`.
- Use `TODO` or `unclear` for metadata that is not explicit in public source metadata.
- Update the feasibility report with a TODO candidate summary.

Blocked work:

- Dataset downloads.
- Dataset accession invention.
- Invented metadata.
- Guessed patient labels.
- Guessed metadata.
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

Scientific Judge repair note:

- Candidates are real public metadata candidates but are not approved datasets.
- Patient-level usability is unresolved.
- Label availability is unresolved.
- External validation role is unresolved.
- Training and external validation suitability require manual audit evidence and Human Gate 1 approval.

Acceptance criteria:

- `docs/02_dataset_feasibility_audit.md` exists.
- `reports/final_dataset_feasibility_report.md` exists.
- `reports/tables/rejected_dataset_log.csv` exists with headers only.
- `scripts/07_generate_dataset_feasibility_report.py` exists and does not query the internet.
- `reports/tables/` exists.
- Dataset feasibility report template, rejected log, and generator tests exist.
- `metadata/dataset_catalog.csv` is not populated with invented datasets.
- No dataset is approved.
- Candidate rows are marked `candidate_pending_audit`.
- Human Gate 1, Dataset Feasibility Approved, remains PENDING.
