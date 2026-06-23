# Current Feature

Feature: P2-F001 - Phase 2 data pipeline scaffold.

Status: completed pending human review.

Builder scope:

- Create data-pipeline scaffold only.
- Define Phase 2 restrictions for future AnnData, metadata harmonization, QC, and patient-level split validation.
- Validate scaffold controls through local config and tests.

Approved-with-restrictions context:

- `GSE137029` is approved only as the primary candidate for Phase 2 pipeline development, not for modeling.
- `CELLxGENE/HCA 436154da-bcf1-4130-9c8b-120ff9a888f2 / 218acb0f-9f2f-4f76-b90b-15a4b7c7f629` is approved only for metadata harmonization design, not for modeling.
- `GSE174188` remains `needs_manual_verification` and is not part of Phase 2 processing.
- `GSE162577` remains `limited_candidate` and is not primary.
- `selected_datasets` remains `[]`.
- `external_validation_cohort` remains TODO.

Explicitly forbidden:

- Downloads.
- Modeling.
- Training.
- Model files.
- Cell-level splits.
- Dataset approval for modeling.
- Creating `selected_datasets`.
- Assigning `external_validation_cohort`.
- Full preprocessing.
- Creating AnnData objects in this feature.

Acceptance criteria:

- `docs/06_data_pipeline_plan.md` exists.
- `configs/data_pipeline.yaml` exists and blocks downloads/modeling.
- `scripts/08_phase2_pipeline_scaffold.py` exists and validates scaffold restrictions.
- `src/data`, `src/qc`, and `src/utils` package markers exist.
- Tests verify no downloads, no modeling, no cell-level splits, no selected datasets, and no external validation cohort assignment.
