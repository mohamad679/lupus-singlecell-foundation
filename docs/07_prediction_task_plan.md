# Prediction Task Plan

Current feature: P2-F010 - Human Gate 2 preparation: labels and prediction task.

This document prepares a scientific decision for Human Gate 2. It does not select
a primary task, approve a dataset for modeling, or establish an external
validation cohort. All task conclusions are provisional until patient-level
labels and their provenance are verified.

## Decision Rules

- A task is `feasible` only when patient identifiers, target labels, comparator
  definitions, label provenance, and leakage-safe evaluation are supported.
- A task is `partially_feasible` when the scientific task is plausible and some
  required metadata appear to exist, but critical evidence remains unresolved.
- A task is `blocked` when required labels or patient-level evidence are not
  explicitly available in the current audit.
- Labels must come from source metadata or a linked publication. They must not
  be inferred from study titles, tissue, cell type, accession, or cohort name.
- Cross-cohort feasibility requires compatible label definitions and evidence
  that patients, samples, and cells do not overlap across cohorts.
- No task is approved by this plan.

## SLE vs Healthy Diagnosis

**Scientific motivation:** Evaluate whether patient-level single-cell profiles
can distinguish source-defined SLE cases from source-defined healthy controls.
This is the most direct candidate task and may establish whether a reproducible
case-control signal exists before considering more specific clinical outcomes.

**Required labels:** Explicit patient- or donor-level SLE diagnosis and healthy
control status, stable patient/donor identifiers, sample identifiers, cohort
identifiers, and source-supported comparator definitions.

**Label provenance requirements:** Exact source field names, observed values,
patient/sample linkage, and supporting repository or publication evidence must
be recorded. Study-level SLE wording is insufficient.

**Expected cohorts:** GSE137029 and the linked CELLxGENE/HCA resource are
continued-audit candidates only. Their overlap must be resolved before they can
be treated as separate cohorts.

**Patient-level requirement:** All cells and repeated samples from one patient
or donor must remain in one split. Patient/donor identifiers must be verified
before task approval.

**Cross-cohort feasibility:** Potentially possible, but currently unresolved
because label compatibility and GEO/HCA/CELLxGENE cohort overlap are not yet
verified.

**Uncertainty risks:** Cohort shift, assay and preprocessing differences,
medication confounding, disease severity imbalance, and uncertain comparator
composition could produce overconfident predictions.

**Biological interpretation opportunities:** Patient-level cell-state and
pathway comparisons may be possible after gene mapping, cell-type provenance,
and confounding controls are verified.

**Blockers:** Patient-level label mapping, exact control definitions, cohort
deduplication, batch metadata, treatment metadata, and external cohort
independence.

**Current status:** `partially_feasible`

## Disease Activity Prediction

**Scientific motivation:** Predict clinically meaningful SLE activity at the
patient level and assess whether molecular states track active versus inactive
disease or a validated activity score.

**Required labels:** Explicit activity state or score, score name, measurement
timepoint, patient/donor and sample linkage, and a documented threshold or
category definition.

**Label provenance requirements:** The source must explicitly provide the
activity field and definition, such as a named SLEDAI measure. Activity must not
be inferred from treatment, tissue, diagnosis, or publication narrative.

**Expected cohorts:** TODO pending source-level label inspection. No current
candidate is assigned to this task.

**Patient-level requirement:** Activity must be linked to a patient sample at a
defined timepoint. Repeated samples must remain grouped by patient in future
evaluation.

**Cross-cohort feasibility:** Blocked until compatible activity instruments,
timing, thresholds, and patient-level mappings are demonstrated across
independent cohorts.

**Uncertainty risks:** Score-definition mismatch, temporal mismatch, treatment
effects, class imbalance, and cohort-specific clinical practice may cause
severe calibration failure.

**Biological interpretation opportunities:** Activity-associated cell states
and pathways could be studied only after temporal provenance and treatment
confounding are resolved.

**Blockers:** No explicitly verified patient-level activity labels, score
definitions, timepoints, or compatible external cohort.

**Current status:** `blocked`

## Flare Prediction

**Scientific motivation:** Identify molecular states associated with a
source-defined flare outcome. A true prediction task would require information
available before the future flare window.

**Required labels:** Explicit flare/non-flare or flare/remission labels, event
definition, assessment date, prediction index date, forecast horizon, and
longitudinal patient identifiers.

**Label provenance requirements:** Flare labels and temporal definitions must
be directly documented in metadata or the linked publication. Disease activity
or treatment escalation cannot be substituted for flare status.

**Expected cohorts:** TODO. No audited candidate currently demonstrates the
required longitudinal outcome structure.

**Patient-level requirement:** Longitudinal observations must be grouped by
patient, and features used for prediction must precede the labeled outcome.

**Cross-cohort feasibility:** Blocked because no compatible longitudinal flare
definition or independent validation cohort is verified.

**Uncertainty risks:** Temporal leakage, variable flare definitions, sparse
events, treatment changes, informative sampling, and censoring create high
uncertainty.

**Biological interpretation opportunities:** Pre-flare cell states might be
interpretable only with adequate event counts, temporal ordering, and
confounder documentation.

**Blockers:** Flare labels, longitudinal timepoints, forecast horizon, event
counts, and external validation evidence are absent or unclear.

**Current status:** `blocked`

## Lupus Nephritis Prediction

**Scientific motivation:** Evaluate patient-level renal involvement, such as
lupus nephritis versus non-nephritis SLE, using explicitly defined clinical
labels and biologically relevant tissue context.

**Required labels:** Explicit lupus nephritis status, non-nephritis SLE or other
defined comparator, patient/donor identifiers, tissue, sampling timepoint, and
histologic class only when directly reported.

**Label provenance requirements:** Nephritis status and histologic class must
come from source clinical metadata or a linked publication. Kidney tissue alone
does not establish a lupus nephritis label.

**Expected cohorts:** TODO pending manual verification of renal labels,
comparators, access conditions, and patient-level metadata. GSE174188 remains
outside Phase 2 processing.

**Patient-level requirement:** Renal labels must be linked to individual
patients and samples. Kidney compartments or cell types cannot replace a
patient-level outcome.

**Cross-cohort feasibility:** Blocked until compatible nephritis definitions,
tissues, assays, comparators, and independent patient cohorts are verified.

**Uncertainty risks:** Tissue mismatch, histologic heterogeneity, class
imbalance, treatment effects, access restrictions, and differing case
definitions may impair calibration and transportability.

**Biological interpretation opportunities:** Renal cell-state, compartment,
and pathway analysis may become possible after tissue, annotation, gene
identifier, and clinical-label provenance are verified.

**Blockers:** Patient-level nephritis labels, comparator definition, histologic
metadata, compatible cohorts, data access, and external validation evidence.

**Current status:** `blocked`

## Human Gate 2 Requirements

Human Gate 2 remains pending until a reviewer can verify:

- patient/donor identifiers and patient-level target labels
- exact label provenance and allowed values
- leakage-safe patient or cohort split feasibility
- independent cross-cohort and external validation feasibility
- biological interpretation prerequisites
- calibration and uncertainty evaluation feasibility

`primary_task` remains TODO. `selected_datasets` remains empty, and
`external_validation_cohort` remains TODO. Phase 3 must not start.
