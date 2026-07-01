# Stage 7B decision

## Final decision

`GSE135779` remains the best public candidate identified so far, but it is not approved for strict external validation of the Stage 6 `FLARE` versus managed-SLE endpoint.

## Why it is not approved yet

The accessible GEO series and sample pages support these labels:

- SLE versus healthy donor;
- child versus adult age group;
- sample-level age;
- sample identifiers such as cSLE, cHD, aSLE, and aHD.

The accessible GEO sample pages inspected in this audit do not expose:

- active flare label;
- managed-SLE label;
- explicit disease activity score or threshold;
- treatment-controlled activity endpoint matching Stage 6.

## Allowed next use

The cohort may be used only after one of the following decisions is made:

1. If supplementary clinical table 1 contains a defensible disease-activity field, define a Stage 7C endpoint-mapping plan.
2. If no disease-activity mapping exists, use GSE135779 only as a limited transfer or biology-replication cohort.
3. If metadata cannot be obtained or mapped, reject it as an external validation cohort for the primary task.

## Paper-safe language

A safe statement is:

Public independent single-cell lupus cohorts were reviewed. GSE135779 was identified as the most feasible public candidate, but strict matched external validation of the primary flare-versus-managed endpoint remains blocked pending clinical metadata and endpoint-mapping verification.

## Paper-unsafe language

Do not write:

The Stage 6 model was externally validated on GSE135779.

That claim is not supported by this audit.
