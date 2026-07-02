# Frozen model transfer protocol

## Core rule

GSE135779 labels must never influence model fitting, dimensionality reduction, threshold choice, feature selection, or hyperparameter choice.

The Stage 7D analysis is a frozen external transfer test, not model development.

## Required frozen components

Before scoring GSE135779, freeze and record:

1. Geneformer model/version and tokenization strategy;
2. gene identifier mapping policy;
3. cell-level QC and cell sampling/capping policy;
4. per-sample embedding aggregation policy;
5. internal PCA or dimensionality-reduction object;
6. internal classifier object;
7. internal decision threshold, if thresholded metrics are reported;
8. random seeds for cell selection and bootstrap confidence intervals.

## Primary embedding and aggregation design

The Stage 6 primary model used donor/sample mean embeddings with PCA(20) and a balanced logistic regression classifier. Stage 7D should preserve that structure as closely as possible:

1. generate Geneformer embeddings for each eligible GSE135779 sample;
2. cap or sample cells using the same fixed policy used for the Stage 6 artifact where feasible;
3. aggregate cell embeddings to one sample-level vector using the frozen primary aggregation policy, preferably mean embedding;
4. transform external sample vectors with the internally fitted PCA transform only;
5. score transformed vectors with the internally fitted classifier only.

## Prohibited operations

The following are prohibited before primary reporting:

- fitting PCA on GSE135779;
- training or fine-tuning a classifier on GSE135779 labels;
- choosing thresholds on GSE135779 labels;
- selecting the best cell type, feature subset, or preprocessing option based on GSE135779 performance;
- dropping difficult samples after inspecting predictions;
- reporting proxy results as strict FLARE-versus-managed external validation.

## Allowed sensitivity analyses

Allowed only after the primary frozen analysis is defined:

- compare mean versus median/trimmed-mean aggregation if all are pre-registered;
- child-only analysis if sample size permits;
- adult-only descriptive scoring, likely underpowered;
- excluding nephritis-heavy samples as a sensitivity check if pre-specified;
- optional healthy-control score distribution sanity check, reported separately from the primary proxy endpoint.
