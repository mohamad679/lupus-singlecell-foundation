# Stage 7 external cohort scouting

This package records the first external-cohort scouting pass after the Stage 6 real-artifact internal evaluation.

## Goal

Identify whether a public independent single-cell lupus cohort can support an external transfer evaluation for the Stage 6 donor-level embedding signal.

## Decision

No strict one-to-one external validation cohort was confirmed in this pass.

The best next candidate is `GSE135779`, because it is an independent PBMC single-cell lupus cohort with substantially more donors than the other public candidates reviewed here. It still requires metadata inspection and label mapping before any model can be tested.

## Priority order

1. `GSE135779` — proceed to metadata feasibility audit.
2. `GSE162577` — too small for validation; possible smoke test only.
3. `GSE142016` — too small and not a suitable donor-level validation cohort.
4. `GSE142637` — perturbation/stimulation design, not a clinical donor validation cohort.

## Stage 7 scope

This is a scouting and feasibility decision package only. It does not download data, extract Geneformer embeddings, train a model, or perform external validation.

## Next gate

Before any external test:

- inspect supplementary clinical metadata for the chosen cohort;
- define a paper-defensible mapping between external labels and the Stage 6 binary task;
- confirm donor/sample identifiers and independence from the primary cohort;
- build or document the Geneformer input path;
- freeze the Stage 6 trained/calibrated model before testing on the external cohort.
