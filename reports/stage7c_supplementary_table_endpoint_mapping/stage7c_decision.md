# Stage 7C endpoint-mapping decision

## Final decision

Strict external validation on `GSE135779` remains blocked.

## Reason

A Supplementary Tables XLSX link was identified from the Nature article, and the article clearly mentions disease-activity heterogeneity and SLEDAI-category analyses. However, the XLSX content was not parsed in this environment, and the author repository did not provide a confirmed donor-level endpoint mapping to the Stage 6 primary endpoint.

Therefore, this step cannot approve a direct mapping from `GSE135779` to:

- FLARE;
- managed SLE;
- active versus managed endpoint;
- treatment-controlled flare discrimination.

## What is allowed

The next step may manually download and inspect Supplementary Table 1. If it contains a disease-activity score or a categorical activity field, a new endpoint-mapping plan can be written.

Until then, GSE135779 can only be described as:

- the best public metadata candidate found so far;
- not yet endpoint-compatible with the Stage 6 primary task;
- possibly usable for limited SLE-versus-healthy transfer or biology replication.

## Paper-safe statement

GSE135779 was identified as a technically feasible independent single-cell lupus cohort, but strict external validation of the primary flare-versus-managed endpoint was not performed because the required endpoint mapping could not be verified from the acquired metadata in this pass.

## Paper-unsafe statement

Do not claim that the Stage 6 model has been externally validated on GSE135779.
