# Current Feature

## STAGE3-PLANNING - Patient-level embedding aggregation and leakage-safe evaluation design

Status: planning pending
Branch: `chore/finalize-stage2-state`

## Objective

Prepare the repository state for Stage 3 after Stage 2 closeout was merged.

This cleanup does not add runtime code, download data, load AnnData files,
execute Geneformer, execute tokenizers, extract embeddings, train models,
perform external validation, commit artifacts, or add performance claims.

## Completed prerequisite

Stage 2 is complete:

- `STAGE2-F001 - Reproducible Geneformer embedding extraction plan`
- `STAGE2-F002 - Embedding config contract`
- `STAGE2-F003 - Embedding provenance manifest`
- `STAGE2-F004 - Dry-run extraction readiness`
- `STAGE2-F005 - Actual Geneformer extraction runner`
- `STAGE2-CLOSEOUT - Stage 2 closeout gate`

## Next scientific stage

`STAGE3 - Patient-level embedding aggregation and leakage-safe evaluation design`

Stage 3 must remain conservative and patient-level only. It must not claim
future flare prediction, clinical utility, external validation, or model
performance. It should first define embedding artifact contracts, aggregation,
split policy, baseline controls, anti-leakage checks, and evaluation contracts
before any modeling is considered.

## Countdown

Stage 3 step: planning
Remaining before Stage 3 implementation: open Stage 3 feature branch after this cleanup PR is merged
