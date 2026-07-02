# Stage 7G GSE135779 external data and embedding scaffold

This package defines the external data and embedding preparation scaffold for a future restricted proxy transfer run on GSE135779.

## Scope

Stage 7G is scaffold-only.

It does not download data, generate embeddings, or run external scoring. It defines what must be prepared before Stage 7H can score GSE135779.

## Required input families

A future implementation must prepare these input families:

1. GSE135779 processed expression matrices;
2. matching barcodes and sample identifiers;
3. shared gene table or gene identifiers;
4. parsed Supplementary Table 1b clinical metadata;
5. Stage 7F frozen Stage 6 artifact bundle.

## Required output families

Stage 7G must ultimately produce:

1. external data acquisition manifest;
2. GSE135779 sample manifest with proxy labels and exclusions;
3. gene mapping manifest;
4. embedding generation manifest;
5. external sample embedding matrix or per-sample embedding files;
6. embedding quality-control summary.

## Proxy endpoint carried forward

The only approved primary endpoint remains:

| Class | Definition |
|---|---|
| Positive proxy | SLE sample with `SLEDAI > 4` |
| Negative proxy | SLE sample with `SLEDAI <= 4` |

Healthy controls and samples without explicit numeric SLEDAI are excluded from the primary proxy endpoint.

## Stage 7G decision

Proceed only to data and embedding preparation. Do not score the external cohort in this stage.
