# Stage 7 external validation decision

## Decision

`GSE135779` is selected as the first external-cohort candidate for a metadata feasibility audit.

This is not yet approval to run external validation. It is approval to inspect the candidate cohort metadata and decide whether a defensible binary label mapping can be made.

## Why GSE135779 is prioritized

- It is independent from the Stage 6 primary donor embedding archive.
- It contains a substantially larger donor count than the other public single-cell lupus candidates reviewed here.
- GEO reports about 276k PBMCs from 33 childhood lupus donors and 11 matched controls, plus an independent adult cohort with 8 adult lupus donors and 6 matched controls.
- Processed matrix files are listed as supplementary files, which makes a feasibility audit practical without requiring protected raw data access.

## Main risk

The Stage 6 primary task is active flare versus managed lupus. Public external cohorts often use different clinical labels, such as lupus versus healthy, adult versus childhood disease, new-onset disease, treatment status, or activity score. Therefore, the next gate must determine whether an activity-based proxy can be mapped without overclaiming.

## Rejected for primary external validation in this pass

### GSE162577

Too small for donor-level validation: two lupus donors and one healthy donor.

### GSE142016

Only three scRNA-seq samples and not a matched donor-level external validation cohort for the Stage 6 primary task.

### GSE142637

Perturbation/stimulation design rather than clinical donor-level validation.

## Required next gate

1. Fetch and inspect the GSE135779 supplementary metadata.
2. Confirm donor identifiers and sample-to-donor mapping.
3. Check whether disease activity labels or clinical scores are present.
4. Define candidate label mapping, if defensible.
5. Decide between:
   - strict external validation,
   - limited external transfer test,
   - biology-only replication,
   - reject as validation cohort.

## Paper language if no strict mapping exists

If GSE135779 cannot support the same binary endpoint, the paper should state that independent public single-cell cohorts were reviewed, but no matched external flare-versus-managed validation cohort with compatible labels was available in this pass.
