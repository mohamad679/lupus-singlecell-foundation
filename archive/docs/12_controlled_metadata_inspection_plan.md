# Controlled Metadata Inspection Plan

Current feature: P3-F014 - Controlled metadata inspection plan.

## Purpose

This plan defines a controlled, auditable inspection of metadata pages, field
schemas, and file manifests needed to resolve modeling-readiness blockers for
GSE137029 and its linked CELLxGENE/HCA candidate.

The plan does not perform the inspection, download full data, select a dataset,
or authorize modeling. Every target remains `pending_inspection`.

## Inspection Scope

Allowed future work is limited to:

- reading public metadata pages and repository field descriptions;
- reading file names, formats, sizes, checksums, and access classifications;
- reading metadata-only run, sample, donor, and project manifests;
- recording exact field names, observed metadata values, definitions, and
  source URLs;
- recording repository and publication cross-references;
- writing evidence only to the controlled evidence log after inspection.

No inspected item can pass a readiness blocker without source-preserving
evidence and separate Scientific and Bioinformatics Judge review.

## Allowed Inspection Targets

- GSE137029 GEO Series and Sample metadata pages;
- GSE137029 supplementary file listing without retrieving file contents;
- GSE137029 SRA Study, Experiment, Sample, and Run metadata pages or
  metadata-only manifests;
- publication methods, tables, and supplements already linked by the audited
  candidate record;
- CELLxGENE collection metadata page;
- CELLxGENE dataset schema and metadata field descriptions;
- HCA project metadata page and metadata-only manifest descriptions;
- donor/sample metadata field lists without retrieving the expression matrix;
- GEO, HCA, and CELLxGENE identifiers needed for overlap reconciliation.

## Forbidden Targets

- FASTQ, BAM, CRAM, count matrices, H5AD, Seurat, loom, or other full data;
- full supplementary archives or expression objects;
- cell-by-gene matrices, embeddings, or processed expression layers;
- controlled-access individual-level data;
- commands that fetch, stream, mirror, or bulk-export dataset content;
- inferred identifiers, labels, mappings, or cohort independence;
- preprocessing, QC filtering, feature extraction, splitting, or modeling.

## GSE137029 Metadata/File-Manifest Inspection Plan

### GEO Metadata Page

Inspect Series and linked Sample metadata for:

- exact sample accessions and titles;
- characteristics fields;
- patient, donor, subject, or individual identifier fields;
- diagnosis and comparator fields;
- tissue, assay, batch, treatment, and timepoint fields;
- links to SRA, HCA, publications, and supplementary metadata.

Expected output: source-preserving field inventory and candidate evidence-log
entries. The page summary alone cannot verify patient-level linkage.

### Supplementary File List

Inspect listing metadata only:

- file name;
- file type and format;
- compressed and uncompressed size if displayed;
- checksum if displayed;
- whether the file appears to contain metadata, counts, or a processed object;
- access and license notes.

Do not retrieve any listed file. Expected output: a file-manifest feasibility
record identifying which future metadata asset would require a separate gate.

### SRA Metadata Page or Manifest

Inspect metadata-only Study, BioProject, BioSample, Experiment, and Run
relationships for:

- sample and run identifiers;
- library strategy, source, selection, and platform;
- run-to-sample relationships;
- public metadata attributes relevant to donor/sample linkage;
- record counts and cross-references.

Do not retrieve sequencing reads. Expected output: identifier-relationship
evidence or an explicit unresolved status.

### Publication Metadata

Inspect linked publication methods, tables, and supplements only for explicit:

- cohort definitions;
- case/control definitions;
- participant and sample counts;
- multiplexing and sample assignment methods;
- metadata field definitions;
- data availability and repository mapping statements.

Publication narrative cannot replace sample-level repository linkage.

## CELLxGENE/HCA Metadata/File-Manifest Inspection Plan

### CELLxGENE Collection Metadata Page

Inspect collection and dataset identifiers, publication linkage, organism,
tissue, assay, disease ontology summaries, asset types, and provenance links.
Do not download the H5AD asset.

### CELLxGENE Dataset Metadata Fields

Inspect schema-documented fields and metadata summaries for:

- donor identifier;
- sample, specimen, library, or observation identifier;
- disease and ontology fields;
- cell-type fields;
- batch, assay, tissue, and source fields;
- field completeness summaries if publicly displayed;
- raw-count and processed-object indicators without retrieving matrices.

### HCA Project Metadata Page

Inspect project, donor, specimen, library, file-format, and repository
cross-reference descriptions. Record whether the HCA project explicitly links
GSE137029 or other candidate accessions.

### Donor/Sample Metadata Field List

Inspect only field names, definitions, allowed values, and publicly displayed
summary counts. Do not retrieve a cell-level metadata table or expression
object under this plan.

## Patient/Donor ID Checks

- record exact original field names and source;
- distinguish patient, donor, sample, specimen, library, and cell levels;
- identify whether stable grouping is explicitly supported;
- record missingness and uniqueness only when publicly summarized;
- identify repeated or longitudinal relationships only when explicit;
- prohibit IDs inferred from filenames, barcodes, row order, or combined fields.

## Sample-to-Patient Linkage Checks

- identify explicit parent-child relationships among donor, sample, library,
  experiment, and run records;
- record one-to-many or many-to-one relationships;
- identify repeated samples and multiplexed libraries;
- record unresolved relationships as `TODO` or `unclear`;
- do not construct a mapping from naming patterns.

## Disease Label Provenance Checks

- record exact diagnosis and comparator field names;
- record observed values and ontology identifiers when public;
- record field definitions and data level;
- determine whether labels are linked to donor/sample records;
- distinguish healthy controls from other comparators;
- keep activity, flare, nephritis, and treatment labels separate and blocked.

## Cohort Overlap Checks

- compare accessions, project IDs, collection IDs, dataset IDs, publications,
  and repository cross-references;
- compare donor/sample identifiers only when explicitly available;
- compare reported cohort, sample, and cell counts as supporting, not decisive,
  evidence;
- determine whether CELLxGENE/HCA is a representation of GSE137029;
- prohibit external-validation assignment until independence is verified.

## Raw/Processed Object Checks

Metadata inspection may record:

- file or asset name;
- format;
- size;
- checksum;
- access status;
- raw-count indicator;
- processed-object indicator;
- whether metadata appears separable from expression data.

It may not retrieve or open full expression objects.

## QC Feasibility Checks

Record whether future approved files appear capable of supporting:

- sample- and patient-level cell counts;
- count-depth and detected-gene summaries;
- mitochondrial and ribosomal metrics;
- doublet and ambient-RNA review;
- batch-aware and disease-group-aware summaries;
- before/after exclusion logs.

QC is not approved merely because relevant fields or assets exist.

## Split Manifest Feasibility Checks

Record whether metadata explicitly supports:

- stable patient or donor grouping;
- sample-to-person linkage;
- repeated-sample grouping;
- disease-label linkage;
- cohort and batch fields;
- cross-repository overlap review;
- patient-, donor-, or cohort-level split assignment.

No split manifest may be populated under this feature.

## Evidence Required to Unblock Training

- verified patient/donor identifiers and relationships;
- verified patient-level diagnosis and comparator provenance;
- verified split-manifest feasibility;
- verified cohort independence or documented overlap with a safe role decision;
- verified QC feasibility and later QC approval;
- verified feature-manifest feasibility;
- explicit dataset selection by a human gate;
- passed Modeling Readiness Gate and a new training permission decision.

## Evidence Required to Reject Training

Training must be rejected if inspection shows:

- no stable patient/donor grouping;
- no explicit case/control linkage;
- labels available only at cell level;
- irreconcilable sample or cohort overlap;
- metadata missingness that prevents leakage-safe splitting;
- inaccessible metadata required for the task;
- incompatible assay, tissue, or comparator definition;
- no defensible QC or patient-level feature path;
- unverifiable or contradictory provenance.

`allow_modeling` remains false, `training_permission` remains `blocked`,
`selected_datasets` remains empty, and Phase 4 is not started.

