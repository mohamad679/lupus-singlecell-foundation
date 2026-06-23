# Lupus Single-Cell Foundation Master Spec

## Scope

This repository is in Phase 0: repository scaffold and master specification only.

The project will eventually evaluate whether public single-cell lupus datasets can support a reproducible scientific workflow. No modeling, model training, dataset downloads, accession claims, or biological conclusions are allowed in Phase 0.

Unknown information must be recorded as `TODO` rather than inferred.

## Non-Goals For Phase 0

- Do not implement modeling.
- Do not train, fine-tune, benchmark, or evaluate models.
- Do not download datasets.
- Do not invent dataset accessions, cohort sizes, assay details, labels, or disease phenotypes.
- Do not proceed beyond Phase 0.

## Phase Plan

### Phase 0: Repository Scaffold And Master Spec

Purpose: establish project controls, documentation, state tracking, metadata schema, and testable acceptance criteria.

Allowed work:

- Create required repository files.
- Define project phases, gates, rubrics, and backlog.
- Define dataset catalog schema with TODO placeholders.
- Add schema tests for metadata files.

Exit criteria:

- Required files exist.
- Metadata schema test passes.
- Backlog contains small, testable items.
- Human gates and judge rubrics are documented.
- No dataset accessions are invented.
- No model code or dataset download logic exists.

Human gate: Phase 0 scaffold review.

Gate owner: TODO.

Gate decision required before Phase 1: approved / changes requested / rejected.

### Phase 1: Dataset Feasibility Audit

This must be the first real scientific phase.

Purpose: determine whether candidate datasets are findable, legally usable, scientifically relevant, technically accessible, and sufficiently annotated for downstream work.

Allowed work after Phase 0 approval:

- Search authoritative dataset sources.
- Record candidate datasets in `metadata/dataset_catalog.csv`.
- Verify access terms, organisms, tissue/cell source, assay type, disease labels, controls, sample counts, patient metadata, batch variables, and raw/processed availability.
- Document unresolved metadata gaps as TODO.

Forbidden work:

- No model training.
- No dataset download unless explicitly approved by the dataset feasibility gate.
- No claims that a dataset is suitable until evidence is recorded.

Exit criteria:

- Each candidate dataset has verifiable source metadata.
- Required catalog fields are populated or marked TODO.
- Feasibility risks are documented.
- Human feasibility gate approves whether any dataset may be acquired.

Human gate: Dataset feasibility approval.

Gate owner: TODO.

Gate decision required before Phase 2: approved dataset list / no feasible datasets / changes requested.

### Phase 2: Data Acquisition And Provenance

May begin only after dataset feasibility approval.

Purpose: acquire approved datasets in a reproducible, provenance-preserving way.

Human gate: data acquisition approval.

Gate owner: TODO.

### Phase 3: Bioinformatics Quality Control

May begin only after approved data acquisition.

Purpose: inspect data quality, metadata consistency, cell and gene filtering assumptions, batch structure, and annotation reliability.

Human gate: QC approval.

Gate owner: TODO.

### Phase 4: Baseline Analysis

May begin only after QC approval.

Purpose: perform descriptive, non-modeling analyses that validate whether the data support the scientific hypothesis.

Human gate: baseline analysis approval.

Gate owner: TODO.

### Phase 5: Modeling Readiness Review

No model training before this phase is explicitly approved.

Purpose: decide whether modeling is scientifically justified, technically feasible, and reproducible.

Human gate: modeling readiness approval.

Gate owner: TODO.

## Global Acceptance Criteria

- Phase 0 contains scaffold and specification only.
- Dataset feasibility audit is the first real scientific phase.
- Model training is blocked until dataset feasibility, acquisition, QC, baseline analysis, and modeling readiness gates are approved.
- Every backlog item has a small scope and testable acceptance criteria.
- Unknown scientific or dataset information is marked TODO.
- Metadata schema is enforced by tests.
- Human gates are documented before work that changes scientific claims or data state.

## Human Gates

| Gate | Blocks | Required Evidence | Decision Values | Owner |
| --- | --- | --- | --- | --- |
| Phase 0 scaffold review | Phase 1 start | Required files, schema test, backlog, rubrics | approved / changes requested / rejected | TODO |
| Dataset feasibility approval | Data acquisition and all modeling | Candidate dataset evidence and feasibility notes | approved dataset list / no feasible datasets / changes requested | TODO |
| Data acquisition approval | QC | Provenance plan and approved dataset list | approved / changes requested / rejected | TODO |
| QC approval | Baseline analysis | QC report and metadata consistency notes | approved / changes requested / rejected | TODO |
| Baseline analysis approval | Modeling readiness review | Descriptive analysis report | approved / changes requested / rejected | TODO |
| Modeling readiness approval | Any model training | Scientific justification, leakage controls, evaluation plan | approved / changes requested / rejected | TODO |

## Judge Rubrics

### Engineering Judge

Pass criteria:

- Repository files are organized and named consistently.
- Tests are deterministic and runnable without network access.
- Work is phase-gated and state is explicit.
- Backlog items are small, independently reviewable, and testable.
- No modeling or dataset download code appears in Phase 0.

Fail criteria:

- Hidden network dependency.
- Ambiguous acceptance criteria.
- Untracked phase transition.
- Model or dataset acquisition implementation added prematurely.

### Scientific Judge

Pass criteria:

- Hypothesis is stated as a testable scientific question.
- Unknowns are marked TODO.
- Dataset feasibility is treated as prerequisite evidence.
- Claims are separated from assumptions.
- Human review gates protect against unsupported conclusions.

Fail criteria:

- Invented dataset facts.
- Claims about lupus biology unsupported by recorded evidence.
- Modeling proposed before dataset suitability is established.

### Bioinformatics Judge

Pass criteria:

- Dataset catalog captures organism, tissue, assay, sample, disease, control, metadata, and availability fields.
- Feasibility audit requires raw and processed data availability checks.
- Batch, donor, disease activity, treatment, and annotation risks are tracked.
- QC is blocked until approved data acquisition.

Fail criteria:

- Missing provenance fields.
- No way to distinguish TODO from verified metadata.
- Downstream analysis planned before data structure is known.

### Reproducibility Judge

Pass criteria:

- Repository state files identify current phase and gates.
- Metadata schema is versioned by tests.
- Network and external data actions are deferred until approval.
- Acceptance criteria can be verified from repository contents.
- TODO markers are explicit and searchable.

Fail criteria:

- Unrecorded manual decisions.
- Non-deterministic tests.
- Dataset or model state exists without provenance.

## Phase 0 Completion Checklist

- [x] `docs/00_master_spec.md` created.
- [x] `docs/01_scientific_hypothesis.md` created.
- [x] `state/project_state.yaml` created.
- [x] `state/backlog.yaml` created.
- [x] `state/current_feature.md` created.
- [x] `metadata/dataset_catalog.csv` created.
- [x] `tests/test_metadata_schema.py` created.
- [x] `README.md` created.
- [x] Metadata schema test passes.
- [ ] Human Phase 0 scaffold review is requested.
