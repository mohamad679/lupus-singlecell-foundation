# Corrected reporting and bias review — 30 September 2026

This author-prepared map uses [TRIPOD+AI](https://www.bmj.com/content/385/bmj-2023-078378) and [PROBAST+AI](https://www.bmj.com/content/388/bmj-2024-082505) as frameworks for the corrected two-cohort paper. It is a substantive reporting audit, not a completed official item-by-item checklist or independent bias adjudication. The external cohort was examined before the corrected analysis.

| Reporting area | Corrected manuscript or supplement location | Evidence and remaining gap |
|---|---|---|
| Title and abstract | Title; structured abstract | Names corrected V1 reanalysis, two cohorts, n, discrimination, paired comparisons, and limits. |
| Intended use and setting | Introduction; Discussion §5 | Donor-level SLE versus healthy-control research comparison. No clinical triage setting or intended decision threshold was defined. |
| Data sources and dates | Methods §3.1; Table 1; Data/code availability | Perez via Census version 2025-11-08; external GSE135779. Source GEO SOFT records are archived with hashes. |
| Eligibility and participant flow | Methods §3.1; Table 1; Supplement provenance | 261 development donors/1,263,676 cells and 56 external samples/363,083 cells. Public GEO has 56 accessions; aHD2 and aSLE8 are absent from the source-described 58 labels, with no verified reason. A full screening flow from all raw source records is unavailable. |
| Outcome and labels | Methods §3.1; Table 1; limitations | Source SLE/healthy labels and 40/16 external class counts. Cross-cohort ascertainment was not independently harmonized; healthy controls do not represent symptomatic differential diagnosis. |
| Predictors and processing | Methods §§3.2–3.4; Supplement provenance | Shared 30,165-gene input, native-input sensitivity, V1 checkpoint/revision, tokenization, cell embedding, donor mean pooling, scaling, and logistic regression. Historical dictionary hashes were printed but not in the original four ZIPs. |
| Missing data | Methods §3.1; Table 1; Results §4.5 | Development age valid for 259/261. External sex/ancestry unavailable in analyzed GEO metadata. GEO aHD3 age 50 retained for primary scoring; review-reported supplement age 43 evaluated only as sensitivity because the workbook was unavailable for independent verification. |
| Sample size | Methods and Results; Table 1 | Available-source sample, 16 external controls and 12 source Adult records; no prospective precision or power calculation. |
| Model specification | Methods §§3.2–3.5; repository fit reports | Scaler, L2 logistic regression, nested-CV selection, fixed external application, checkpoint and run summaries recorded. |
| Validation design and leakage | Methods §§3.3–3.7; deviations | Donor-level internal nested CV and fixed external cohort. Correction followed examination of external outcomes, so this is not untouched confirmatory validation. Historical freeze-guard omissions are disclosed. |
| Performance and uncertainty | Results §§4.1–4.4; Tables 2–3; Figures 1–4 | AUROC, donor-bootstrap CIs, paired DeLong/Holm, AP, Brier, and a constant-probability comparator. Fixed-prediction intervals omit complete extraction/retraining uncertainty. |
| Calibration | Results §4.2; Supplement provenance | Geneformer intercept/slope with Wald CIs use original saved decision scores. Clipped-probability reconstruction is reported separately; eight Geneformer and one pseudobulk probabilities were clipped under that convention. Calibration is diagnostic only. |
| Model availability and reproducibility | Data/code availability; Supplement Table S1; correction runbook | Code, validated features, predictions, analysis JSON, figures, source records, and hashes are versioned. Four original Kaggle ZIPs are retained outside Git. Revised setup-provenance notebooks have not been rerun on Kaggle. |
| Limitations and interpretation | Discussion §5.5; Conclusion | Narrow representation/cohort conclusion, unknown pretraining overlap, source demographic differences, no clinical utility or new untouched cohort. |
| Funding, interests, roles, AI assistance | Title page; declarations | Carried from author drafts; the author must verify these declarations and approve final revised wording before submission. |

## PROBAST+AI-informed appraisal

| Domain | Author assessment for this corrected analysis |
|---|---|
| Participants and applicability | **Major concern.** Development donors were adults and the external sample is mainly source-classified Children, with only 16 controls. Clinical target population and care setting were not defined. |
| Predictors | **Concern.** Geneformer extraction was repaired and versioned, but shared-gene restriction, platform differences, sparse external covariates, and unknown pretraining overlap limit transport interpretation. |
| Outcome | **Concern.** Public source SLE/healthy labels were used; cross-cohort clinical ascertainment and timing were not independently reconciled. |
| Analysis | **High risk for a clinical-use claim.** The correction was developed after external outcomes were seen. Paired inference is appropriate for the observed donors, but 56 samples, fixed-prediction intervals, and no untouched replication limit generalization. |
| Overall | The study supports a focused corrected comparison only. Clinical applicability is uncertain and no diagnosis or treatment decision claim is made. This judgment has not been independently adjudicated. |

Before journal submission, the author should complete the journal's official TRIPOD+AI checklist and obtain an independent PROBAST+AI assessment if one is required. Neither task changes the corrected numerical results reported here.
