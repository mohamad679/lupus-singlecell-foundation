# Embedding generation plan

## Purpose

Define the future embedding-generation path for GSE135779 without running external scoring.

## Required inputs

- processed expression matrices;
- barcodes/sample identifiers;
- gene mapping manifest;
- sample manifest with inclusion and exclusion status;
- frozen Stage 6 preprocessing policy if available.

## Required process

1. Import each external expression matrix.
2. Validate gene and barcode dimensions.
3. Apply the approved gene mapping policy.
4. Apply the same cell selection or cell cap policy as Stage 6 where feasible.
5. Generate Geneformer embeddings per cell.
6. Aggregate cell embeddings to one vector per eligible sample.
7. Save per-sample embeddings with stable sample IDs.
8. Write an embedding QC summary before any scoring.

## Required output format

Future Stage 7H should consume either:

- one `.npy` file per included external sample; or
- one table/matrix with sample IDs aligned to rows.

Each output must record:

- sample ID;
- number of cells used;
- embedding dimension;
- aggregation policy;
- failed or excluded samples;
- hash of generated embedding file.

## Prohibited behavior

- Do not inspect score performance during embedding generation.
- Do not change cell filtering based on proxy labels.
- Do not combine healthy controls with low-activity SLE for the primary endpoint.
- Do not fit PCA or classifier during embedding generation.

## Status

Plan created. Real embeddings are not generated in Stage 7G.
