# Lupus Single-Cell Foundation

Patient-level prediction foundations for lupus single-cell RNA sequencing.

## Current Phase 1 Runtime Status

The dataset loading and QC pipeline is implemented in
`scripts/11_phase1_dataset_qc.py`. The public GEO record for GSE174188
currently has no supplementary h5ad, so the checked-in workspace artifacts
are generated from explicitly labeled synthetic fixtures. They validate the
pipeline but are not evidence about the real Perez et al. cohort.

The required acquisition fixture is exactly 500 cells × 200 genes. A separate
500 cells × 2,500 genes fixture validates the independent requirement that the
processed object contain exactly 2,000 highly variable genes.

Run and verify:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements_phase1.txt
python scripts/11_phase1_dataset_qc.py --check-geo
python scripts/12_verify_phase1.py
```

To process an authorized or subsequently published real matrix:

```bash
python scripts/11_phase1_dataset_qc.py \
  --input data/raw/GSE174188/<source-file>.h5ad
```

See `data/raw/DOWNLOAD_INSTRUCTIONS.md` for source status and exact GEO
recheck commands. The completion report is at
`results/phase1/PHASE1_REPORT.md`.

## Historical Planning Scaffolds

The repository also retains earlier feasibility, gating, schema, and modeling
planning artifacts. Those documents predate this executable synthetic Phase 1
validation and should not be read as proof that the real GSE174188 matrix was
acquired or approved for modeling.

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

## Historical Test Suite

The original `pytest -q` suite validates the planning-only state. Several of
those tests deliberately fail when any h5ad, PNG, or local virtual environment
exists, so they conflict with the Phase 1 runtime deliverables above. Use
`scripts/12_verify_phase1.py` as the acceptance verifier for this pipeline.
