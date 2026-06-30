# Current Feature

Feature: STAGE0-F001 - Repository reconciliation for real exploratory Kaggle/CELLxGENE results.

Status: in progress.

## Purpose

The repository is being reconciled from a historical planning/synthetic-fixture scaffold into a real, reproducible computational biology project based on exploratory Kaggle/CELLxGENE work.

The immediate goal is not to run new modeling. The immediate goal is to make the repository accurately describe the current state of the project before converting notebooks into tested scripts.

## Current scientific objective

The active scientific objective is patient-level discrimination of active SLE flare from managed SLE using frozen single-cell foundation-model embeddings.

This is currently framed as active flare discrimination, not future flare prediction.

## Current evidence status

Exploratory work has already produced:

- real CELLxGENE Census loading of the Perez et al. lupus PBMC cohort
- exploratory donor-level label extraction
- per-patient Geneformer embeddings
- preliminary patient-level Logistic Regression evaluation
- preliminary permutation and confounder checks

These results are promising but remain exploratory until regenerated from clean scripts with saved predictions, metrics, manifests, and tests.

## Current production status

Production-grade modeling and publication claims remain blocked until the following are completed:

- repository documentation and state reconciliation
- package-based Phase 1/2/3 scripts
- label extraction tests
- QC tests
- embedding manifest and integrity tests
- leakage-safe evaluation scripts
- reproducible raw/pseudobulk baselines
- cell-type contribution analysis
- external validation audit

## Current branch goal

The current branch should only reconcile documentation and project state.

Allowed work on this branch:

- remove system files from Git tracking
- add PROJECT_STATUS.md
- update README.md
- update state files to reflect exploratory results and production blockers

Not allowed on this branch:

- new modeling
- new external validation
- large data downloads
- rewriting notebooks into scripts
- changing scientific results

## Next feature after this branch

After this reconciliation branch is complete, the next feature should create the package skeleton and begin converting Phase 1 label/QC logic into tested Python modules.
