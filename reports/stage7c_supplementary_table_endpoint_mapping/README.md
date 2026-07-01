# Stage 7C supplementary table acquisition and endpoint-mapping decision

This package records the Stage 7C attempt to acquire and inspect the Supplementary Tables for the GSE135779 source paper and decide whether the cohort can support endpoint mapping for the Stage 6 primary task.

## Source paper

Nehar-Belaid et al., Nature Immunology 2020: `Mapping systemic lupus erythematosus heterogeneity at the single-cell level`.

The Nature article states that the study profiled childhood SLE patients with different degrees of disease activity and validated findings in an adult SLE cohort. The article page exposes a Supplementary Tables XLSX download covering Supplementary Tables 1 to 4.

## Acquisition status

| Item | Status | Notes |
|---|---|---|
| Nature article located | pass | Article and DOI were identified. |
| Supplementary Tables link located | pass | The Nature page lists `Supplementary Tables (download XLSX)` for Supplementary Tables 1 to 4. |
| XLSX parsed locally | blocked | The tool environment could not fetch/parse the static Springer XLSX payload. |
| Author GitHub repository located | pass | The Nature article links to the public analysis repository. |
| Public metadata CSV files identified | pass | The repository lists cSLE and caSLE metadata CSV files. |
| Direct repository search for SLEDAI | no_hit | A direct repository code search for `SLEDAI` returned no hits. |
| Endpoint mapping approved | no | No strict mapping to Stage 6 FLARE-vs-managed-SLE is approved in this step. |

## Decision

Do not use GSE135779 for strict external validation yet.

The article confirms disease-activity heterogeneity and SLEDAI-category analyses, but this Stage 7C pass did not obtain a machine-readable clinical table proving a donor-level mapping to the Stage 6 `FLARE` versus managed-SLE endpoint.

## Approved next actions

1. Manually download the Supplementary Tables XLSX from the Nature article.
2. Inspect Supplementary Table 1 columns for SLEDAI, disease activity, treatment, flare, remission, managed, or equivalent fields.
3. If an activity field is present, create a transparent endpoint-mapping plan before any model evaluation.
4. If no matching field is present, downgrade GSE135779 to limited transfer or biology-replication only.
