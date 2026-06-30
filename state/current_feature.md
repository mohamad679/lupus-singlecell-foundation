# Current Feature

## STAGE1-F001 - Package skeleton and donor label extraction

Status: in progress
Branch: `feat/stage1-labels-package`

## Objective

Move the first production-safe logic out of exploratory notebooks and into a
tested Python package.

The current feature implements patient/donor-level clinical label extraction
for the primary CELLxGENE/Perez lupus cohort.

## Approved label rule

- `FLARE*` donor identifiers -> `Flare`
- `HC-*` donor identifiers -> `Healthy`
- `IGTB*` donor identifiers -> `Healthy`
- purely numeric donor identifiers -> `Managed`

Unknown donor-id patterns must fail closed with an explicit error. They must
not be silently assigned to any class.

## Completed in this branch

- Added `src/lupusfm/` package skeleton.
- Added `src/lupusfm/data/labels.py`.
- Added unit tests for donor-id normalization, clinical-status inference,
  unknown-pattern rejection, and order-preserving batch label creation.
- Added `pyproject.toml` for editable package installation.
- Updated `.gitignore` for Python packaging/build artifacts.
- Removed remaining tracked macOS `.DS_Store` metadata from Git.

## Validation

Current targeted test:

`python3 -m pytest tests/test_lupusfm_labels.py -q`

Expected result:

`19 passed`

## Not allowed in this feature

- No modeling or training.
- No new performance claims.
- No external validation.
- No large data downloads.
- No changes to exploratory notebook results.

## Next feature

Stage 1 should continue with production-safe metadata/QC utilities for the
primary AnnData/CELLxGENE ingestion path.
