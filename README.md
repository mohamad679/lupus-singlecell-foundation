# Lupus Single-Cell Foundation

Phase 1 dataset feasibility audit scaffold for a lupus single-cell feasibility project.

This repository currently contains only planning, state, metadata schema, audit scaffolding, reports, and tests. It does not contain model code, downloaded datasets, or verified dataset accessions.

## Current Status

- Phase: 1, dataset feasibility audit.
- Current feature: P1-F001, Dataset Search Strategy.
- Dataset downloads: not allowed.
- Model training: not allowed.
- First real scientific phase: dataset feasibility audit.
- Unknown information policy: mark as TODO.

## Required Gate Before Data Acquisition

No dataset acquisition or model training is allowed until Human Gate 1, Dataset Feasibility Approved, is passed. Model training also requires later modeling readiness approval.

## Repository Files

- `docs/00_master_spec.md`: project phases, gates, acceptance criteria, and judge rubrics.
- `docs/01_scientific_hypothesis.md`: draft hypothesis placeholder and required evidence.
- `docs/02_dataset_feasibility_audit.md`: audit plan, criteria, workflow, and rejection rules.
- `configs/data_audit.yaml`: approved search terms, sources, required fields, scoring fields, and forbidden actions.
- `state/project_state.yaml`: current project state and gate status.
- `state/backlog.yaml`: small, testable backlog items.
- `state/current_feature.md`: active feature scope and blocked work.
- `metadata/dataset_catalog.csv`: dataset feasibility catalog schema with TODO placeholders.
- `scripts/00_audit_datasets.py`: safe local scaffold for validating metadata and writing feasibility tables.
- `reports/tables/dataset_feasibility_table.csv`: local feasibility table generated from existing catalog rows only.
- `tests/test_metadata_schema.py`: schema tests for the dataset catalog.
- `tests/test_data_audit_config.py`: config and source coverage tests.
- `tests/test_audit_script_no_invented_rows.py`: audit script safety tests.

## Verification

Run:

```bash
pytest -q
```

The tests require no network access and do not download data.
