# Claim guardrails

## Allowed claims

Allowed wording:

- `Restricted proxy external transfer analysis`;
- `high-activity versus low-activity SLE`;
- `SLEDAI-thresholded proxy endpoint`;
- `paper-aligned SLEDAI > 4 versus SLEDAI <= 4 activity split`;
- `not a strict external validation of the primary FLARE-versus-managed endpoint`.

Example safe statement:

`We evaluated frozen Stage 6-derived scores on GSE135779 as a restricted proxy external transfer test, using SLEDAI > 4 versus SLEDAI <= 4 to distinguish high-activity from low-activity SLE.`

## Prohibited claims

Do not write:

- `external validation of FLARE versus managed SLE`;
- `flare prediction validated on GSE135779`;
- `managed SLE label was externally validated`;
- `clinical flare model generalizes to GSE135779`;
- `SLEDAI <= 4 equals managed SLE`.

## Required caveat

Any Stage 7D result must include this caveat:

`GSE135779 does not provide explicit sample-level flare or managed/remission labels in the parsed Supplementary Table 1 metadata; therefore, this analysis is restricted to a SLEDAI-based high-activity versus low-activity proxy endpoint.`

## Interpretation rule

A positive Stage 7D result would support transfer of Stage 6-derived embedding scores to a related SLE disease-activity proxy. It would not prove validation of the original FLARE-versus-managed SLE endpoint.

A negative Stage 7D result would not invalidate the Stage 6 internal result because the endpoint is related but non-identical and the external cohort differs in age group, cohort design, processing, and metadata semantics.
