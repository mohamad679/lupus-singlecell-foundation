# Final handoff decision

## Final Stage 7 decision

Stage 7 is closed as a complete design and readiness package.

## Scientific handoff

GSE135779 remains the selected external cohort candidate only for a restricted proxy transfer task.

Approved endpoint:

- positive proxy: SLEDAI > 4;
- negative proxy: SLEDAI <= 4.

Blocked endpoint:

- strict FLARE versus managed SLE external validation.

## Implementation handoff

External scoring must remain paused until the following real artifacts exist:

- frozen Stage 6 PCA object;
- frozen Stage 6 classifier object;
- model artifact manifest;
- GSE135779 sample manifest;
- external sample embeddings;
- embedding QC summary;
- no-fit scoring procedure.

## Open blocker

Issue #57 remains open and should stay open until frozen artifacts and scoring scaffold are implemented outside the design-only Stage 7 package.

## Next allowed directions

Allowed:

1. pause here and keep Stage 7 as the final external-cohort readiness package;
2. start a new implementation stage for local artifact export and data generation;
3. use Stage 7 outputs in a manuscript as evidence that strict external validation was not available but a proxy transfer path was designed.

Not allowed:

1. claim external validation for FLARE versus managed SLE;
2. run scoring without frozen model artifacts;
3. tune thresholds or model parameters using external labels.
