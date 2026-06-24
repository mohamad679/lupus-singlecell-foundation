# P3-F018 Metadata Inspection Evidence Expansion

## Executive Summary

The Planner, Scientific Judge, and Bioinformatics Judge completed one final
metadata-only expansion for GSE137029 and the linked CELLxGENE/HCA resource.

The expansion resolved donor-label and sample-donor mapping for the
CELLxGENE/HCA candidate. It did not resolve GSE137029 patient-level mapping or
cross-repository overlap.

Decision:

- GSE137029 cannot be selected for patient-level training.
- CELLxGENE/HCA cannot be assigned as external validation.
- CELLxGENE/HCA has stronger patient-level metadata feasibility than previously
  documented, but it is not selected automatically.
- Further inspection of the same aggregate public metadata is unlikely to
  resolve GSE137029.
- The P3-F019 dataset strategy/pivot gate should be prepared, but pivot is not
  activated.

`modeling_readiness` remains `not_ready`, `training_permission` remains
`blocked`, and `allow_modeling` remains false.

## Evidence Expanded

### GSE137029 GEO MINiML

The complete GEO MINiML family metadata archive was inspected without
retrieving sequencing reads or expression matrices.

Verified:

- all 66 GEO Samples contain the same four characteristics fields:
  `cell type`, `condition`, `sample type`, and `chip antibody`;
- all 66 Samples have a `condition` value;
- condition counts are 42 `SLE`, 12 `SLE flare`, and 12 `healthy`.

Not found:

- patient ID;
- donor ID;
- subject ID;
- individual ID;
- a sample-to-person mapping.

The 66 GEO Samples are pooled sequencing records and cannot be treated as the
192 reported individuals.

Source:

- https://ftp.ncbi.nlm.nih.gov/geo/series/GSE137nnn/GSE137029/miniml/GSE137029_family.xml.tgz

### CELLxGENE/HCA Linked UCSC Metadata

The linked UCSC Cell Browser dataset manifest and three compressed metadata
vectors were inspected:

- `donor_id`;
- `sample_uuid`;
- `disease`.

No expression matrix, H5AD, coordinate file, or full metadata table was
downloaded.

Verified:

- 1,263,676 cell records;
- 261 donor IDs;
- 274 sample UUIDs;
- 162 donors linked only to systemic lupus erythematosus;
- 99 donors linked only to normal;
- zero donors linked to multiple disease values;
- zero samples linked to multiple donors;
- zero samples linked to multiple disease values;
- 250 donors with one sample;
- 9 donors with two samples;
- 2 donors with three samples.

This resolves donor-to-disease and sample-to-donor consistency for the
CELLxGENE/HCA candidate metadata.

Sources:

- https://cells.ucsc.edu/lupus-pbmc/dataset.json
- https://cells.ucsc.edu/lupus-pbmc/metaFields/donor_id.bin.gz
- https://cells.ucsc.edu/lupus-pbmc/metaFields/sample_uuid.bin.gz
- https://cells.ucsc.edu/lupus-pbmc/metaFields/disease.bin.gz

### Portal Provenance and Additional Metadata Availability

The linked UCSC description identifies its GEO Series as GSE174188 and links
the HCA project. It does not provide a record-level crosswalk to GSE137029.

The linked Zenodo record exposes analysis code files but no dedicated
patient/donor metadata mapping file in its public manifest. Code files were not
downloaded.

Sources:

- https://cells.ucsc.edu/lupus-pbmc/desc.json
- https://zenodo.org/api/records/4724043

## Still Unresolved Blockers

### GSE137029

- patient/donor identifiers;
- sample-to-person mapping;
- patient-level diagnosis labels;
- patient-level class counts;
- repeated-patient relationships;
- leakage-safe patient-level splitting;
- training-cohort suitability.

### Cross-cohort and External Validation

- exact GSE137029-to-CELLxGENE/HCA donor overlap;
- exact sample or cell overlap;
- evidence that CELLxGENE/HCA is independent of a potential GSE137029 training
  cohort;
- an independently assignable external-validation cohort.

### Project-wide

- dataset selection;
- QC approval;
- populated split manifest;
- real leakage checks;
- populated feature manifest;
- explicit training permission.

## Can GSE137029 Be Selected?

No.

The final public GEO metadata inventory confirms complete sample-level
condition labels but no patient/donor mapping. Without an explicit external
mapping asset, GSE137029 cannot support leakage-safe patient-level training.

## Can CELLxGENE/HCA Be Used Externally?

No.

Its internal donor, sample, and disease mappings are now explicitly supported.
However, the linked portal represents GSE174188/HCA data, and exact overlap
with GSE137029 remains unresolved. It cannot be declared independent external
validation.

## Is More Inspection Useful?

Repeated inspection of the same GEO, CELLxGENE aggregate API, HCA overview,
UCSC manifest, and Zenodo manifest is unlikely to resolve the remaining
GSE137029 person mapping or cross-repository overlap.

Additional inspection is useful only if a new authoritative metadata mapping
asset or data dictionary is identified. It must explicitly link people,
samples, labels, and accessions.

## Should the Pivot Gate Be Prepared?

Yes.

P3-F019 should evaluate at least these options:

- retain GSE137029 only if a new authoritative patient mapping appears;
- consider CELLxGENE/HCA as a potential primary cohort under a new explicit
  selection and access gate, not as external validation;
- identify a different training or external-validation dataset with explicit
  patient-level mappings;
- reject the current case-control modeling path if no defensible cohort pair
  can be established.

This report prepares the strategy question. It does not activate a pivot.

## Recommendation

Prepare P3-F019 Dataset Strategy Decision / Pivot Gate.

Keep training blocked, Phase 4 blocked, selected datasets empty, and external
validation TODO until a separate human strategy decision is made.

