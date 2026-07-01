# Stage 7B GSE135779 metadata feasibility audit

This package records the metadata feasibility audit for `GSE135779`, the priority external-cohort candidate selected in Stage 7.

## Audit decision

`GSE135779` is technically usable as an independent public single-cell PBMC cohort, but it is not yet approved for strict external validation of the Stage 6 endpoint.

The reason is endpoint mismatch: the accessible GEO metadata confirms sample-level SLE versus healthy donor labels, age, and age group, but it does not expose a direct flare versus managed-SLE endpoint or disease-activity operating label in the sample records inspected here.

## Feasibility status

| Gate | Status | Decision |
|---|---|---|
| Public independent cohort | pass | GSE135779 is public and independent from the Stage 6 primary artifact. |
| Processed matrix availability | pass | GEO provides processed Matrix Market count matrices and barcodes plus a shared genes file. |
| Donor/sample identifiers | pass | Sample titles encode donor-like IDs such as cSLE1, cHD1, aSLE5, and bracketed JB identifiers. |
| Basic clinical group labels | pass | GEO sample pages expose SLE/HD group labels and age group fields. |
| Flare versus managed endpoint | fail | No direct flare/managed-SLE label was found in the accessible GEO sample metadata. |
| Disease activity score mapping | unresolved | GEO notes that clinical information is in supplementary table 1, but this audit did not confirm an activity-based threshold field from accessible GEO sample pages. |
| Strict external validation readiness | fail | Strict validation remains blocked pending supplementary clinical table inspection and label mapping. |
| Limited transfer test readiness | conditional | A limited SLE-versus-healthy or source-distinct biology replication test is feasible if clearly framed. |

## Decision

Do not run a paper-claimed strict external validation yet.

Proceed only to a metadata-table acquisition step. If supplementary clinical table 1 contains disease-activity fields or scores that can be mapped transparently, then a follow-up Stage 7C can define an external endpoint. Otherwise, GSE135779 should be used only as a limited transfer or biology-replication cohort, not as matched external validation for the Stage 6 primary task.
