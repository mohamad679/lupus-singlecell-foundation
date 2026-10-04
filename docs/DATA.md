# Data and cohorts

## Study cohorts

| Cohort | Role in v2.0.0 | Donors | Cases / controls | Public source | Raw data redistributed here? |
|---|---|---:|---:|---|---|
| Perez et al. lupus PBMC cohort | Development | 261 | 162 / 99 | CZ CELLxGENE Census, dataset `218acb0f-9f2f-4f76-b90b-15a4b7c7f629` | No |
| GSE135779 | Previously examined external cohort used for corrected reanalysis | 56 | 40 / 16 | NCBI GEO, accession `GSE135779` | No |

The unit of analysis is the donor/sample, not the individual cell. The external cohort is not treated as newly untouched after the historical release; v2.0.0 is explicitly a corrected reanalysis.

## Inputs retained in Git

`results/reference/` contains only compact donor metadata and the historical donor-level comparator predictions required to reproduce the corrected scoring analysis. Corrected Geneformer feature artifacts used by the CPU reproduction are in `results/published/{shared_features,native_features}/`.

Large historical pseudobulk parquet matrices were removed from the active branch without rewriting Git history. They remain available in the historical release snapshot and are intended for the archival Zenodo record.

## Gene space

The corrected primary Geneformer analysis uses the validated shared-gene input representation. A model-native representation is retained as a sensitivity analysis. The exact feature/run provenance is recorded in `results/published/corrected_artifact_manifest.json` and the corresponding run-summary JSON files.

## External age groups

Source-defined external age categories are retained as provided. The `Children` category includes some participants aged 18–19; age-stratified results are therefore descriptive and should not be interpreted as a clean pediatric/adult causal contrast.

## Licensing

Repository code is MIT licensed. Third-party datasets retain their original source terms; the repository does not relicense or redistribute raw third-party expression data.
