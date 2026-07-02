# Next implementation plan

## Recommended next stage

The next stage should not be external scoring yet.

Recommended next stage:

`Stage 7F — frozen Stage 6 model artifact export and external scoring scaffold`

## Goal of Stage 7F

Prepare everything needed to execute Stage 7D safely without using GSE135779 labels for model development.

## Stage 7F deliverables

### 1. Frozen Stage 6 artifact export

Export and hash:

- fitted PCA(20);
- fitted balanced logistic regression;
- frozen threshold policy;
- preprocessing/aggregation manifest;
- software environment manifest.

### 2. GSE135779 sample manifest

Build from parsed Supplementary Table 1b:

- sample ID;
- group;
- SLEDAI;
- high/low activity proxy label;
- inclusion flag;
- exclusion reason.

### 3. External data import scaffold

Prepare code or documentation to acquire processed matrices from GSE135779 and convert them into the same embedding input format.

### 4. No-fit scoring scaffold

Create a script that can score external embeddings using only frozen Stage 6 objects.

The script must fail closed if frozen artifacts are missing.

### 5. Dry-run checks

Before real external scoring, add tests that verify:

- external labels are not used before scoring;
- PCA is never fit on external data;
- classifier is never fit on external data;
- threshold is not selected on external data;
- excluded samples remain excluded.

## Stage 7F exit criteria

Stage 7F is complete only when the repository contains all required artifacts or scripts needed to run the restricted proxy external transfer analysis reproducibly.

Only then may the project proceed to actual external scoring.
