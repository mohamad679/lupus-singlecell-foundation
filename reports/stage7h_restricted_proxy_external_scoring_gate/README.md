# Stage 7H restricted proxy external scoring design and execution gate

This package defines the scoring design and execution gate for a future restricted proxy external transfer analysis on GSE135779.

## Scope

Stage 7H is an execution gate.

It does not run external scoring unless all required frozen model artifacts and external embeddings are already present. Based on Stage 7F and Stage 7G, those real artifacts are still pending, so Stage 7H blocks execution.

## Approved endpoint

The only approved endpoint remains:

| Class | Definition |
|---|---|
| Positive proxy | SLE sample with `SLEDAI > 4` |
| Negative proxy | SLE sample with `SLEDAI <= 4` |

This is restricted proxy transfer, not strict external validation of the Stage 6 FLARE-versus-managed-SLE endpoint.

## Required before scoring

Scoring may run only when all of the following exist:

1. frozen Stage 6 PCA object;
2. frozen Stage 6 classifier object;
3. frozen threshold policy or threshold-disabled policy;
4. GSE135779 sample manifest;
5. external sample embeddings;
6. embedding QC summary;
7. no-fit scoring script or equivalent reproducible scoring procedure.

## Current gate decision

Execution status: `blocked_missing_real_artifacts`.

Do not score GSE135779 yet.
