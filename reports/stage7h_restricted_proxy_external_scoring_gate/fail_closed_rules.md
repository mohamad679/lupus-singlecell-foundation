# Stage 7H fail-closed rules

## Purpose

This file defines when Stage 7H must stop without scoring.

## Stop conditions

Stage 7H must stop if any of the following is true:

1. frozen PCA artifact is missing;
2. frozen classifier artifact is missing;
3. model manifest or hash record is missing;
4. external sample manifest is missing;
5. external embeddings are missing;
6. embedding QC summary is missing;
7. sample IDs cannot be aligned between manifest and embeddings;
8. external labels are used before scoring;
9. any code attempts to fit PCA or classifier on external data;
10. any threshold is selected using external labels.

## Reporting rule

If any stop condition is true, report:

`Stage 7H execution blocked: required frozen artifacts or external embeddings are missing.`

Do not produce performance metrics from incomplete inputs.

## Claim rule

Never upgrade a proxy result to strict clinical external validation. GSE135779 supports only restricted proxy transfer unless explicit flare and managed labels are later obtained.
