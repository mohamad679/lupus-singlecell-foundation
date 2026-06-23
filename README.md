# Lupus Single-Cell Foundation

Phase 0 repository scaffold for a lupus single-cell feasibility project.

This repository currently contains only planning, state, metadata schema, and tests. It does not contain model code, downloaded datasets, or verified dataset accessions.

## Current Status

- Phase: 0, repository scaffold and master specification.
- Dataset downloads: not allowed.
- Model training: not allowed.
- First real scientific phase: dataset feasibility audit.
- Unknown information policy: mark as TODO.

## Required Gate Before Scientific Work

Phase 1 may begin only after human approval of the Phase 0 scaffold.

No dataset acquisition or model training is allowed until the dataset feasibility approval gate is passed. Model training also requires later modeling readiness approval.

## Repository Files

- `docs/00_master_spec.md`: project phases, gates, acceptance criteria, and judge rubrics.
- `docs/01_scientific_hypothesis.md`: draft hypothesis placeholder and required evidence.
- `state/project_state.yaml`: current project state and gate status.
- `state/backlog.yaml`: small, testable backlog items.
- `state/current_feature.md`: active feature scope and blocked work.
- `metadata/dataset_catalog.csv`: dataset feasibility catalog schema with TODO placeholders.
- `tests/test_metadata_schema.py`: schema tests for the dataset catalog.

## Verification

Run:

```bash
python -m pytest
```

The tests require no network access and do not download data.
