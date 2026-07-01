# Stage 7 candidate decision

## Decision

`GSE135779` is the first candidate for the next metadata audit.

This file records a feasibility decision only. No external test was run in this step.

## Why this candidate

- It is independent from the Stage 6 primary artifact.
- It has a larger donor count than the other public candidates reviewed here.
- GEO reports about 276k PBMCs from 33 childhood lupus donors and 11 matched controls, plus an adult cohort with 8 lupus donors and 6 matched controls.
- Processed matrix files are available as supplementary files.

## Main risk

The endpoint used in Stage 6 may not exactly match labels in public external cohorts. Therefore the next step must inspect the candidate metadata before any external test is attempted.

## Other candidates

- `GSE162577`: too small for donor-level validation.
- `GSE142016`: only three scRNA-seq samples.
- `GSE142637`: stimulation design, not a donor-level validation cohort.

## Required next gate

1. Inspect the `GSE135779` supplementary metadata.
2. Confirm donor and sample identifiers.
3. Check whether disease activity fields or clinical scores are available.
4. Define a defensible label mapping if possible.
5. Decide whether this cohort supports validation, a limited transfer test, biology-only replication, or rejection.
