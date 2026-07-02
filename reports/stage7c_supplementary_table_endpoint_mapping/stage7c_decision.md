# Stage 7C endpoint-mapping decision

## Final decision

`GSE135779` is now approved for a restricted proxy external transfer test, but it is still not approved for strict external validation of the Stage 6 `FLARE` versus managed-SLE endpoint.

## What changed

Supplementary Table 1 was successfully parsed after the initial acquisition attempt. The parsed ST1b clinical sheet contains sample-level disease-activity information that was not visible in the public GEO sample pages.

Confirmed endpoint-relevant fields include:

- sample-level `SLEDAI` total score;
- weighted SLEDAI-style components, including arthritis, rash, renal urine findings, dsDNA, low complement, fever, pleurisy, vasculitis, alopecia, and leukopenia;
- derived activity domain flags including `MSK`, `KIDNEY`, and `SERUM`;
- medications at screening, including MMF, OS, MTX, and Plaquenil;
- nephritis indicators and nephrology class fields;
- laboratory fields including complement and anti-dsDNA measurements.

## Approved mapping

A paper-aligned proxy endpoint is defensible:

| Proxy class | Definition | Interpretation |
|---|---|---|
| Positive | SLE sample with `SLEDAI > 4` | high-activity SLE |
| Negative | SLE sample with `SLEDAI <= 4` | low-activity SLE |

The explicit numeric SLEDAI values yield 16 high-activity samples and 23 low-activity samples. Two additional child-SLE rows have missing explicit SLEDAI but low observed component totals; exclude them unless an inference rule is pre-registered.

## Why strict validation remains blocked

The parsed table still does not contain explicit sample-level labels for:

- clinician-adjudicated flare;
- managed SLE;
- stable disease;
- remission;
- inactive disease;
- longitudinal visit status;
- treatment-controlled endpoint status;
- recent treatment change or flare timing.

Therefore, `SLEDAI > 4` versus `SLEDAI <= 4` is an activity proxy, not the same endpoint as Stage 6 `FLARE` versus managed SLE.

## Allowed paper language

Safe:

GSE135779 was used for a restricted proxy external transfer analysis of high-activity versus low-activity SLE using a paper-aligned SLEDAI threshold.

Unsafe:

The Stage 6 model was externally validated on GSE135779 for FLARE versus managed SLE.

## Next implementation step

Proceed to Stage 7D only if the project accepts a proxy endpoint. Stage 7D should freeze the Stage 6 model and evaluate it against the `SLEDAI > 4` versus `SLEDAI <= 4` donor/sample labels as a restricted transfer test, not as strict clinical validation.
