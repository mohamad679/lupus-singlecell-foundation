# No-fit external scoring scaffold

## Purpose

This scaffold defines how a future scoring step must use frozen Stage 6 objects.

## Required inputs

- frozen artifact bundle from Stage 6;
- external sample embedding matrix;
- sample manifest with proxy labels and exclusions.

## Required scoring behavior

1. Load frozen PCA object.
2. Load frozen classifier object.
3. Load external sample embeddings.
4. Apply PCA transform only.
5. Generate continuous scores.
6. Apply frozen threshold only if a threshold manifest exists.
7. Report metrics only on included primary proxy samples.

## Prohibited behavior

- fitting PCA on external data;
- fitting classifier on external data;
- selecting threshold on external data;
- changing exclusions after predictions are inspected.

## Status

Scaffold created. Real scoring remains blocked until the frozen artifact bundle and external embeddings exist.
