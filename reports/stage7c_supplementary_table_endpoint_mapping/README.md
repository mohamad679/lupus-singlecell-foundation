# Stage 7C supplementary table parse and endpoint-mapping decision

This package records the completed Supplementary Table 1 parse for the GSE135779 source paper and the resulting endpoint-mapping decision for the Stage 6 primary task.

## Source paper

Nehar-Belaid et al., Nature Immunology 2020: `Mapping systemic lupus erythematosus heterogeneity at the single-cell level`.

The Nature article exposes a Supplementary Tables XLSX workbook covering Supplementary Tables 1 to 4. Deep Research retrieved and parsed that workbook, including Supplementary Table 1a, 1b, and 1c.

## Updated acquisition status

| Item | Status | Notes |
|---|---|---|
| Nature article located | pass | Article and DOI were identified. |
| Supplementary Tables XLSX located | pass | The article page lists the Supplementary Tables workbook. |
| Supplementary Table 1 parsed | pass | ST1a, ST1b, and ST1c were parsed into machine-readable tables. |
| Endpoint-relevant sheet found | pass | ST1b is the sample-level clinical information sheet. |
| SLEDAI total present | pass | ST1b contains sample-level SLEDAI for 39 samples. |
| SLEDAI component fields present | pass | ST1b contains weighted clinical/lab activity components such as arthritis, rash, proteinuria, hematuria, urinary casts, pyuria, dsDNA, low complement, fever, pleurisy, vasculitis, alopecia, and leukopenia. |
| Medications at screening present | pass | ST1b contains medication-at-screening variables including MMF, OS, MTX, and Plaquenil. |
| Renal/nephritis fields present | pass | ST1b contains nephritis indicators and nephrology class fields. |
| Explicit flare label present | fail | No explicit sample-level flare label was found. |
| Explicit managed/remission label present | fail | No explicit managed, stable, inactive, or remission label was found. |
| Strict Stage 6 endpoint mapping | fail | Cross-sectional SLEDAI does not equal clinician-adjudicated FLARE versus managed SLE. |
| Proxy endpoint mapping | pass_with_restrictions | A paper-aligned high-activity versus low-activity SLE proxy is defensible if clearly labeled as a proxy. |

## Updated decision

GSE135779 is now upgraded from a metadata-sparse candidate to a usable disease-activity proxy cohort.

However, strict external validation of the Stage 6 `FLARE` versus managed-SLE endpoint remains blocked because Supplementary Table 1 does not contain explicit flare, managed, remission, inactive, stable-disease, longitudinal visit-status, or treatment-controlled endpoint labels.

## Approved proxy endpoint

The strongest defensible proxy is:

- positive class: SLE samples with `SLEDAI > 4`;
- negative class: SLE samples with `SLEDAI <= 4`;
- framing: high-activity versus low-activity SLE transfer test;
- not allowed framing: strict FLARE versus managed-SLE external validation.

The parsed table reports 16 explicit high-activity SLE samples and 23 explicit low-activity SLE samples by numeric SLEDAI. Two additional child-SLE rows have missing explicit SLEDAI but low observed component totals; these should be excluded unless a pre-registered inference rule is added.

## Final Stage 7C conclusion

Proceed to a proxy external transfer design only. Do not claim strict external validation unless a separate clinical codebook or author-provided metadata supplies explicit flare and managed/remission status.
