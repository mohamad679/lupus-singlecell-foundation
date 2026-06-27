# GSE174188 download instructions

## Current source status

The official GEO record currently says that supplementary data files are not
provided, so there is no public GEO h5ad filename to place in a wget or curl
command. The record points to controlled access because of patient privacy.
The HCA project is public but currently lists FASTQ files, not a ready h5ad.

- GEO record: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE174188
- GEO supplementary directory: https://ftp.ncbi.nlm.nih.gov/geo/series/GSE174nnn/GSE174188/suppl/
- HCA project: https://explore.data.humancellatlas.org/projects/9fc0064b-84ce-40a5-a768-e6eb3d364ee0

Do not rename a different dataset to look like GSE174188. After a legitimate
h5ad export is obtained, place it under `data/raw/GSE174188/` and rerun the
pipeline. Raw source files are never overwritten by the pipeline.

## Exact GEO checks

```bash
mkdir -p data/raw/GSE174188
curl --fail --location --retry 3 \
  'https://ftp.ncbi.nlm.nih.gov/geo/series/GSE174nnn/GSE174188/suppl/' \
  --output data/raw/GSE174188/GEO_SUPPLEMENT_LISTING.html

wget --recursive --no-parent --no-host-directories --cut-dirs=4 \
  --accept='*.h5ad,*.h5ad.gz' \
  --directory-prefix=data/raw/GSE174188 \
  'https://ftp.ncbi.nlm.nih.gov/geo/series/GSE174nnn/GSE174188/suppl/'
```

These commands currently return no h5ad because GEO publishes none for this
series. They are intentionally retained so the source can be rechecked if the
record changes.

## GEO metadata (not an expression matrix)

```bash
curl --fail --location --retry 3 \
  'https://ftp.ncbi.nlm.nih.gov/geo/series/GSE174nnn/GSE174188/soft/GSE174188_family.soft.gz' \
  --output data/raw/GSE174188/GSE174188_family.soft.gz
```

## After an authorized/public h5ad is obtained

```bash
source .venv/bin/activate
python scripts/11_phase1_dataset_qc.py \
  --input data/raw/GSE174188/<authorized-file>.h5ad
python scripts/12_verify_phase1.py
```

The included `mini_test.h5ad` is a synthetic 500-cell, 200-gene acquisition
fallback only. `mini_phase1_validation.h5ad` has 2,500 genes and is used to
exercise the exact 2,000-HVG acceptance criterion.
