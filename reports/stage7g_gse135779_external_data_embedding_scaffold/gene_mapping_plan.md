# Gene mapping plan

## Purpose

The external expression matrices must be mapped into the same gene/token space expected by the frozen Geneformer embedding path.

## Required checks

Before embedding generation, record:

1. source gene identifier type;
2. number of genes in the external matrix;
3. number of genes mappable to the Geneformer vocabulary;
4. number of unmapped genes;
5. duplicate gene handling policy;
6. mitochondrial/ribosomal gene policy if any filtering is applied;
7. final tokenized gene count per sample.

## Mapping rules

- Use the same gene identifier policy as the Stage 6 embedding artifact where feasible.
- Do not choose a mapping strategy based on external proxy-label performance.
- Keep all unmapped and duplicated genes documented.
- Do not fit or tune any model component during gene mapping.

## Required output

Write a future `gene_mapping_manifest.json` containing:

- input gene table path;
- Geneformer vocabulary version;
- source identifier type;
- mapped gene count;
- unmapped gene count;
- duplicate handling rule;
- mapping date;
- software versions.

## Status

Plan created. Real gene mapping is pending external data acquisition.
