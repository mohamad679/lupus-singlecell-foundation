# Stage 7D exclusion policy

## Primary inclusion set

Include only GSE135779 samples that satisfy all of the following:

1. group is SLE (`cSLE` or `aSLE`);
2. sample has an explicit numeric SLEDAI value;
3. expression data can be processed through the same frozen Geneformer embedding path used for Stage 6;
4. sample identity can be kept independent at the sample/donor level.

## Primary exclusion set

Exclude from the primary restricted proxy endpoint:

- all healthy controls (`cHD`, `aHD`);
- SLE samples with missing explicit numeric SLEDAI;
- samples that fail expression import, gene mapping, or embedding generation;
- duplicate or ambiguous samples that cannot be resolved to an independent donor/sample unit;
- any sample requiring label inference from free text only.

## Missing SLEDAI rule

Two child-SLE rows were reported as missing explicit SLEDAI while having low observed component totals. They must be excluded from the primary automated split unless a separate pre-registered inference rule is written before evaluation.

Default policy: exclude.

## Healthy control rule

Healthy controls are not part of the primary Stage 7D proxy endpoint. They may be used only for a separately reported sanity check, for example to inspect whether model scores are systematically shifted in non-SLE controls.

Do not combine healthy controls with low-activity SLE as the negative class for the primary proxy endpoint.

## Duplicate or repeated donor rule

If any sample IDs map to repeated donors, aggregate or deduplicate before scoring so that each donor contributes once to primary metrics. Never allow duplicate donor contributions to inflate external-transfer performance.
