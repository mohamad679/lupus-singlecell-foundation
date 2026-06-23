# Current Feature

Feature: P1-F013 - Repair Loop for judge blockers.

Status: completed pending human review.

Allowed work:

- Convert Scientific Judge and Bioinformatics Judge blockers into repair tasks.
- Track required evidence, allowed resolution actions, forbidden actions, and human gate requirements.
- Keep every repair unresolved or pending manual review.

Repair loop created:

- `state/repair_queue.yaml` contains structured repair items.
- `reports/tables/judge_repair_queue.csv` contains tabular repair rows for auditing.
- `reports/final_dataset_feasibility_report.md` includes a Judge Repair Queue section.

Blocking findings:

- No blocker has been resolved yet.
- Patient IDs, label provenance, activity labels, treatment metadata, batch metadata, cell-type labels, gene identifiers, raw/processed availability, controlled-access constraints, cohort overlap, and external validation roles remain unresolved.
- Human Gate 1 remains PENDING.
- No dataset is approved or selected.

Next planned feature:

- Final decision table after repair queue review.

Blocked work:

- Dataset downloads.
- Dataset approval.
- Human Gate 1 closure.
- Moving datasets into `selected_datasets`.
- Moving datasets into `metadata/dataset_catalog.csv` as selected or approved.
- Inferring missing metadata.
- Marking repair rows resolved without source evidence and human review.
- Model implementation.
- Model training.
- Any Phase 2 work.

Acceptance criteria:

- `state/repair_queue.yaml` exists.
- `reports/tables/judge_repair_queue.csv` exists.
- Repair rows exist.
- No repair is marked resolved.
- Every repair has required evidence and forbidden actions.
- Human Gate 1 remains PENDING.
- `selected_datasets` remains `[]`.
- `external_validation_cohort` remains TODO.
- `project.blocked` is true.
