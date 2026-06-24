# P3-F015 Dataset/Label Evidence Review

## Decision Summary

Metadata-only review was completed for GSE137029 and the linked
CELLxGENE/HCA candidate. Eighteen evidence items were recorded from public GEO,
SRA, NCBI publication metadata, the official CELLxGENE collection API, and the
HCA project overview.

The review verifies several repository-level fields and manifests, but it does
not resolve the patient-level linkage required for modeling.

Decision:

- GSE137029 cannot be selected for training.
- CELLxGENE/HCA cannot be assigned as external validation.
- `modeling_readiness` remains `not_ready`.
- `training_permission` remains `blocked`.
- No dataset is selected.

## Evidence Reviewed

### GSE137029

Sources:

- https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE137029
- https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM4065951
- https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM4065963
- https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM4065975
- https://www.ncbi.nlm.nih.gov/sra?term=SRP220690
- https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=33127880&retmode=json

Reviewed:

- GEO Series design and reported case/control counts;
- representative GEO Sample characteristics;
- GSM, BioSample, SRA experiment, and run relationships;
- supplementary file names, types, and displayed sizes;
- raw and processed availability statements;
- CellRanger and Demuxlet processing descriptions;
- linked publication metadata.

### CELLxGENE/HCA

Sources:

- https://api.cellxgene.cziscience.com/curation/v1/collections/436154da-bcf1-4130-9c8b-120ff9a888f2
- https://cellxgene.cziscience.com/collections/436154da-bcf1-4130-9c8b-120ff9a888f2
- https://explore.data.humancellatlas.org/projects/9fc0064b-84ce-40a5-a768-e6eb3d364ee0

Reviewed:

- collection and dataset identifiers;
- donor field visibility;
- aggregate disease ontology terms;
- tissue, assay, cell count, and donor count;
- raw-count and H5AD asset indicators;
- HCA project accessions and file count;
- GEO, HCA, and CELLxGENE source cross-references.

No H5AD, FASTQ, SRA, matrix, or supplementary data file was downloaded.

## Verified Items

### GSE137029

- Human PBMC single-cell case-control study context.
- GEO reports 134 SLE cases and 58 healthy controls.
- GEO Sample field `condition` is explicit in inspected records.
- Inspected values include `SLE`, `healthy`, and `SLE flare`.
- GSM-to-BioSample-to-SRA experiment relations exist.
- SRP220690 exposes 66 public records.
- Raw data availability in SRA and processed matrices on the GEO Series.
- Processed matrix, barcode, and gene file manifest.
- CellRanger, Demuxlet, aggregation, and doublet-removal descriptions.

### CELLxGENE/HCA

- Authoritative collection and dataset identifiers.
- `donor_id` field/list is exposed by the official CELLxGENE API.
- Aggregate disease terms include `normal` and
  `systemic lupus erythematosus`.
- HCA reports 261 donors, blood/PBMC, 10x 3' v2, and 800 FASTQ files.
- CELLxGENE reports 1,263,676 cells, `raw.X`, and an H5AD asset.
- Official CELLxGENE metadata links GSE137029 as raw-data provenance.
- HCA lists GSE137029 and GSE174188 and links the CELLxGENE collection.

## Unresolved Blockers

### GSE137029

- No explicit patient or donor identifier field was exposed on inspected pages.
- GSM, BioSample, and SRA identifiers do not establish a patient identifier.
- No complete sample-to-patient map was exposed.
- Patient-level label linkage and class counts cannot be verified.
- Identifier uniqueness, missingness, repeats, and longitudinal structure are
  unresolved.
- QC summary tables, thresholds, before/after counts, and human QC approval are
  unavailable.
- Leakage-safe split feasibility is not established.

### CELLxGENE/HCA

- The aggregate API does not expose an explicit sample identifier or
  donor-to-sample map.
- Donor and disease vocabularies are exposed separately; donor-to-disease
  linkage is not exposed.
- Comparator class counts after donor linkage are unavailable.
- Activity and lupus nephritis labels are not exposed.
- Exact donor/sample/cell overlap with GSE137029 is unresolved.
- QC and feature-manifest readiness cannot be established from aggregate
  metadata.

## GSE137029 Selection Decision

GSE137029 remains the strongest candidate for further verification but cannot
be selected.

The sample-level diagnosis field is useful evidence, but the absence of an
explicit patient/donor field and complete patient-label linkage blocks
patient-level splitting, leakage checks, feature aggregation, and training.

## CELLxGENE/HCA External Validation Decision

CELLxGENE/HCA cannot serve as external validation.

Official metadata directly link the collection and HCA project to GSE137029.
This resolves the independence assumption negatively: the resource must be
treated as linked provenance unless record-level evidence demonstrates a
non-overlapping subset. Exact overlap remains unresolved, so no external role
can be assigned.

## Recommendation

Continue verification, not modeling.

The next permissible work is a separately approved inspection of a
metadata-only data dictionary or mapping asset that can expose:

- stable patient/donor identifiers;
- complete sample-to-person relationships;
- donor/sample-to-diagnosis linkage;
- missingness, repeats, and class counts;
- exact cross-repository overlap.

If those metadata cannot be obtained without prohibited full-data access,
GSE137029 should be rejected for patient-level training under the current
task. Training remains blocked.

