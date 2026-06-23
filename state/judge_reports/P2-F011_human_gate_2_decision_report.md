# P2-F011 Human Gate 2 Decision Report

## Decision Summary

Human Gate 2 is `approved_with_restrictions`. The project may prepare a Phase 3
baseline design for **SLE diagnosis / case-control prediction only**.

This is a task-scope decision, not dataset approval or modeling authorization.
`selected_datasets` remains empty, `external_validation_cohort` remains TODO,
and `allow_modeling` remains false.

## Approved Scope

- Create a future baseline modeling scaffold for SLE versus healthy
  case-control prediction.
- Specify patient- or donor-level feature and evaluation designs.
- Preserve label provenance, leakage prevention, and preliminary-result
  requirements in future Phase 3 plans.

No training, preprocessing, data acquisition, or model implementation is
approved by this gate.

## Rejected or Blocked Scopes

- Disease activity prediction: blocked because patient-level activity labels,
  score definitions, and timepoints are not verified.
- Flare prediction: blocked because longitudinal flare outcomes, temporal
  ordering, and forecast horizons are not verified.
- Lupus nephritis prediction: blocked because nephritis labels, comparator
  definitions, compatible cohorts, and access requirements are unresolved.
- Foundation models: not approved.
- Deep patient-level multiple-instance learning: not approved.
- Uncertainty modeling: not approved as an implementation task.
- Dashboard development: not approved.

## Risks

- Patient-level diagnosis and control label provenance remains incomplete.
- Candidate GEO and CELLxGENE/HCA resources may overlap.
- Batch, treatment, and cohort metadata remain unresolved.
- No independent external validation cohort has been justified.
- Dataset labels are not sufficiently verified for non-preliminary claims.
- Case-control performance could reflect cohort or technical confounding.

## Restrictions

- Training cannot begin until a later baseline feature explicitly authorizes
  it; this feature does not.
- Cell-level splitting is forbidden.
- Patient- or donor-level splitting is mandatory.
- External validation remains TODO.
- Label provenance must be checked before results are reported.
- Any future baseline result must be labeled preliminary until dataset labels
  are verified.
- Datasets are not fully approved for modeling and must not be added to
  `selected_datasets` by this decision.

## Next Phase Readiness

Phase 2 is complete under restricted Human Gate 2 approval. Phase 3 exists only
as a backlog scaffold. The next permissible feature is P3-F001, baseline
modeling scaffold, and it must remain design-only unless a later explicit
feature changes modeling authorization.

No Phase 3 implementation is created by P2-F011.
