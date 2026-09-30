"""Build the five corrected Word documents from the preserved working drafts.

Run with the bundled document Python environment, which provides python-docx.
All numerical replacements are checked against versioned result JSON files.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from docx import Document
from docx.shared import Pt

ROOT = Path(__file__).resolve().parents[1]
CORR = ROOT / "results/correction_2026-09"


def load(name):
    return json.loads((CORR / name).read_text())


def para(doc, prefix, value):
    matches = [p for p in doc.paragraphs if p.text.startswith(prefix)]
    if len(matches) != 1:
        raise ValueError(f"expected one paragraph for {prefix!r}; found {len(matches)}")
    matches[0].text = value


def drop(doc, prefix):
    matches = [p for p in doc.paragraphs if p.text.startswith(prefix)]
    if len(matches) != 1:
        raise ValueError(f"expected one paragraph for {prefix!r}; found {len(matches)}")
    element = matches[0]._element
    element.getparent().remove(element)


def cell(table, row, col, text):
    table.cell(row, col).text = str(text)


def fmt_ci(row, digits=4):
    return f"{row['auroc']:.{digits}f} ({row['ci95'][0]:.{digits}f}–{row['ci95'][1]:.{digits}f})"


def finalize(doc, target):
    for table in doc.tables:
        for row in table.rows:
            for c in row.cells:
                for p in c.paragraphs:
                    for run in p.runs:
                        if run.font.size is None or run.font.size.pt > 9:
                            run.font.size = Pt(8)
    doc.save(target)


def manuscript(source, target, d, shared, native, sensitivity, probe):
    doc = Document(source)
    para(doc, "External transport of donor-level SLE classifiers:",
         "External transport of donor-level SLE classifiers across two cohorts: corrected Geneformer V1 and pseudobulk analysis")
    drop(doc, "WORKING CORRECTION DRAFT")
    para(doc, "Objective. We evaluate", "Objective. We evaluated donor-level SLE versus healthy-control discrimination after development in an adult cohort and application to an external cohort with mostly source-classified Children samples. This report is a versioned correction of the Geneformer V1 analysis.")
    para(doc, "Methods. Development used", "Methods. We analyzed 261 development donors (162 SLE, 99 healthy; 1,263,676 cells) and 56 external samples (40 SLE, 16 healthy; 363,083 cells). Corrected V1 cell embeddings used explicit V1 tokenization, shared-gene input, penultimate-layer cell extraction, and donor mean pooling. We repeated nested donor cross-validation and full-development fitting. External AUROCs were compared by paired DeLong tests with Holm correction and paired donor-bootstrap intervals.")
    para(doc, "Results (historical release", "Results. Corrected shared-gene Geneformer AUROC was 0.9746 in development nested cross-validation and 0.7344 (95% donor-bootstrap CI 0.6017–0.8597) externally. External pseudobulk and age AUROCs were 0.8984 and 0.5781. Geneformer minus age was +0.1563 (95% CI −0.0859 to +0.4040; Holm p = 0.2046); Geneformer minus pseudobulk was −0.1641 (95% CI −0.2916 to −0.0384; Holm p = 0.0175). Neither prespecified Geneformer-superiority criterion was met. Native-input sensitivity yielded Geneformer AUROC 0.7484.")
    para(doc, "Conclusion (provisional)", "Conclusion. In this previously examined, distribution-shifted external cohort, corrected V1 features did not meet either prespecified Geneformer-superiority criterion. The findings are specific to this task, model version, feature construction, and two cohorts; they do not establish clinical diagnostic performance or general model inferiority.")
    para(doc, "We studied this transport question", "We studied donor-level SLE discrimination in the adult Perez et al. development cohort [7] and GSE135779 from Nehar-Belaid et al. [8]. The task, three arms, two co-primary comparisons, Holm procedure, and decision rule were preregistered before development data were loaded. The historical external evaluation was later found to use an unsupported Geneformer V1 extraction configuration and an invalid equal-AUROC test. This paper reports a versioned correction with the originally specified shared-gene input as the main analysis, model-native input as sensitivity, and explicit paired inference. Because the external cohort had already been examined, the correction is a reanalysis rather than a new untouched confirmatory validation.")
    para(doc, "The development cohort was obtained", "The development cohort was obtained from Perez et al. [7] through the CZ CELLxGENE Census [18] (collection 436154da-bcf1-4130-9c8b-120ff9a888f2, dataset 218acb0f-9f2f-4f76-b90b-15a4b7c7f629, CC BY 4.0; census version 2025-11-08). It comprised 261 adult donors (162 SLE, 99 healthy), aged 20–83 years, and 1,263,676 cells contributing to the corrected embeddings.")
    para(doc, "The external cohort was GSE135779", "The external cohort was GSE135779 from Nehar-Belaid et al. [8]. The public deposit contained 56 samples: 33 SLE and 11 healthy in the source Children category, and 7 SLE and 5 healthy in Adult. Seven Children samples were aged 18 or 19, so source category names are retained without imposing a new pediatric age cut-off. The source publication describes 58 donors, a discrepancy not reconciled from the public records (deviations item 4). The 56 analyzed samples were 40 SLE and 16 healthy, aged 7–63 years. Cohorts differed in sequencing platform generation or protocol and age distribution; external sex and ancestry fields were unavailable [19].")
    para(doc, "Geneformer (historical release)", "Geneformer V1 correction. The historical extraction selected V1 weights but omitted model_version=V1 and requested CLS embeddings, so those vectors are retained only as historical artifacts. The corrected extraction pinned Geneformer revision 04c2b2e84da7c0f385c3f9ad8f3ec24bab6650e5 and the V1-10M checkpoint/dictionaries by SHA-256, set model_version=V1, emb_mode=cell, emb_layer=−1, and model_input_size=2048, and averaged finite 256-dimensional cell embeddings by donor. The main input used the 30,165-gene reference intersection; unrestricted model-native input was an exploratory sensitivity analysis. An eight-cell fixture checked dictionary loading, token IDs, special tokens, and output shape before extraction; versioned summaries record checkpoint hashes, cell accounting, runtime packages, and embedding hashes.")
    para(doc, "Pooled outer-fold predictions", "Pooled outer-fold donor predictions yielded internal AUROC. For the corrected Geneformer reanalysis, 5000 percentile bootstrap resamples of fixed donor predictions provided descriptive AUROC intervals. Baseline intervals and above-chance permutation p-values remain the historical released estimates where explicitly identified; they are not used to test equality of correlated AUROCs. Single-class bootstrap resamples were discarded.")
    para(doc, "Permutation implementation differed", "Historical above-chance permutation procedures differed by arm: pseudobulk held C = 0.01 fixed while Geneformer and age repeated hyperparameter selection. These released p-values are preserved as historical results and do not provide paired comparisons. The corrected co-primary inference uses paired DeLong tests and paired donor-bootstrap intervals on aligned external donor predictions. With 1000 historical permutations, the smallest reported p-value was 1/1001 [26–29].")
    para(doc, "The final frozen C was", "The historical frozen C was the median of five outer-fold selections: Geneformer 1.0 ([1, 1, 10, 10, 1]), pseudobulk 0.01 ([0.01, 0.1, 0.1, 0.01, 0.01]), and age 0.001 ([0.001]×5). Corrected shared-gene Geneformer development refitting selected [1, 10, 100, 10, 1] and median C = 10; native-input sensitivity selected [1, 10, 100, 100, 1] and median C = 10. The correction did not overwrite frozen or original release artifacts.")
    para(doc, "After development and freeze", "For the corrected main Geneformer analysis, a scaler and L2 logistic regression were fitted on all 261 corrected development donor vectors using median nested-CV C = 10, then applied unchanged to the 56 corrected external vectors. Pseudobulk and age comparator probabilities were deterministically regenerated from the historical frozen analysis and checked for exact donor-key/label alignment. Development AUROC comes from pooled outer-fold predictions; external AUROC comes from a single full-development fit, so their difference is descriptive rather than a causal estimate of cohort shift.")
    para(doc, "The automated freeze guard was", "The historical freeze guard was not called by every initial Phase 3 script: sealed pseudobulk processing and final scoring lacked require_valid_freeze() until later guard calls were added (deviations item 3). SEALED_OPENED.json records the initial external opening at 2026-07-21T06:50:41.257496+00:00. Historical external Geneformer scoring used frozen C = 1; the corrected V1 analysis reran development selection and used C = 10. Neither frozen historical artifacts nor the already-examined external sample status were changed by the correction.")
    para(doc, "Historical co-primary rule", "The preregistered Geneformer-superiority rule required a paired donor-bootstrap 95% AUROC-difference interval wholly above zero and Holm-significant evidence for each comparison. The historical label-shuffle p-values tested above-chance label exchangeability, not equality of two correlated AUROCs. The correction therefore uses two-sided paired DeLong p-values for Geneformer versus age and Geneformer versus pseudobulk, applies Holm adjustment across these two tests, and retains 5000 paired donor-bootstrap intervals. A positive difference and both statistical conditions are required for superiority; analyses on the previously examined external cohort are labeled corrected reanalysis.")
    para(doc, "The co-primary comparisons were independently", "The versioned correction regenerated V1 development and external vectors using validated Kaggle outputs, repeated development nested CV, and rescored the already examined external cohort. The secondary analyses are age-stratified AUROC, average precision, Brier score, logistic recalibration, a development-prevalence constant-probability comparator, model-native input sensitivity, and an updated corrected-feature cohort-membership probe. These diagnostics do not create a new confirmatory cohort.")
    para(doc, "All three external AUROC point estimates", "The corrected Geneformer development-to-external point estimate changed by −0.2402 AUROC (0.9746 to 0.7344). The like-for-like restricted pseudobulk and age changes were −0.0867 and −0.0672. These descriptive gaps compare nested-CV protocol estimates with full-development model applications and cannot isolate a cohort effect. Figure 1 shows the point estimates and their separate donor-bootstrap intervals.")
    para(doc, "Restricting development pseudobulk", "Restricting development pseudobulk to the shared 30,165-gene space changed pooled development AUROC by +0.00125 (paired bootstrap 95% CI −0.00039 to +0.00321). Its fixed-C label-permutation p = 0.000999 tests above-chance discrimination in the restricted space; it does not test the restriction effect. Of 4015 genes absent across development donors, 490 were expressed in the external cohort; this descriptive availability check is not a causal explanation of the performance pattern.")
    para(doc, "Historical age-stratified external", "In the source-defined Children group (n = 44; 33 SLE, 11 healthy), corrected shared-gene Geneformer AUROC was 0.7052 (95% CI 0.5452–0.8533); in the Adult group (n = 12; 7 SLE, 5 healthy), it was 0.8857 (0.6250–1.0000). The source Children category includes some donors aged 18 or 19. These exploratory stratum estimates are imprecise, especially for adults (Figure 2; Supplementary Table S2).")
    para(doc, "Post-hoc external AUPRC", "External average precision/Brier score was 0.899/0.471 for corrected shared-gene Geneformer, 0.962/0.149 for pseudobulk, and 0.744/0.216 for age. A constant probability equal to development SLE prevalence (162/261) had Brier score 0.213 externally. Diagnostic recalibration slopes were 0.185, 0.545, and −5.414, respectively; the age estimate was unstable because its predictions spanned a narrow range. The corrected Geneformer probabilities were poorly calibrated and were not recalibrated before evaluation.")
    para(doc, "Table 3. Historical", "Table 3. Corrected co-primary paired external comparisons (n = 56).")
    para(doc, "Provenance terminology note", "The repository preserves the original preregistration, historical release, and released decision label. The revised manuscript uses “Not met” for a failed Geneformer-superiority criterion. Corrected result files are in results/correction_2026-09; the prior external cohort had already been examined.")
    para(doc, "In the historical release", "Geneformer exceeded age by 0.1563 AUROC, but its paired CI included zero and Holm-adjusted p = 0.2046. Geneformer was 0.1641 AUROC below pseudobulk; the paired interval lay below zero and Holm-adjusted p = 0.0175. Neither contrast satisfies a positive Geneformer-superiority rule. The negative pseudobulk contrast is a result for this representation and cohort, not proof of broad model inferiority (Figure 3).")
    para(doc, "The post-hoc cohort-signature probe distinguished", "A post-hoc cohort-membership classifier using corrected shared-gene Geneformer vectors distinguished development from external donors with AUROC 0.9999 (95% CI 0.9996–1.0000). The preserved pseudobulk and age probes were 1.0000 (1.0000–1.0000) and 0.8719 (0.8021–0.9321), respectively. These are cohort-origin diagnostics, not SLE prediction or estimates of a causal batch contribution (Figure 4).")
    para(doc, "Valid development age was available", "Valid development age was available for 259 donors (mean 41.3, SD 14.5; range 20–83), all adults. External samples had mean age 20.9 (SD 12.8; range 7–63), with 44 source Children and 12 source Adult records. Development metadata recorded 244 female/17 male donors and ancestry as 149 European American, 107 Asian, 3 African American, and 2 Hispanic or Latin. Corresponding external sex and ancestry fields were unavailable. Source studies document different sequencing generations or protocols, but chemistry was not a harmonized structured field; these factors cannot be disentangled in this design.")
    para(doc, "Strong within-cohort performance", "Corrected Geneformer V1 yielded strong development discrimination (AUROC 0.9746) but did not meet either prespecified external superiority criterion. Its external AUROC was 0.7344 versus 0.8984 for pseudobulk and 0.5781 for age. The paired evidence supports a lower AUROC than pseudobulk for this specific corrected representation in this cohort; it does not establish general inferiority of Geneformer or clinical utility of any arm.")
    para(doc, "The internal-to-external AUROC point estimates", "The development-to-external AUROC point estimates differed by −0.240 for corrected Geneformer, −0.087 for restricted pseudobulk, and −0.067 for age. These comparisons are descriptive and combine changes in population, technical acquisition, and fitting procedure; they were not tested as causal cohort-shift effects.")
    para(doc, "Cohort origin was almost perfectly", "Cohort origin remained almost perfectly distinguishable using corrected Geneformer and pseudobulk features, while age alone was also informative for cohort membership. The diagnostic reveals strong cohort-associated structure but cannot identify its biological or technical source. The external cohort was mostly source-classified Children, while all development donors were adults; sex and ancestry metadata were unavailable externally. This limits attribution of the SLE-discrimination estimates.")
    para(doc, "External validation used one small cohort", "The external comparison has only 56 samples, including a 12-person source Adult subgroup, and the public deposit has 56 rather than the 58 donor records described in the publication. Its external outcomes had already been examined when the corrected feature extraction and inference were performed. Thus, this is a transparent corrected reanalysis, not an untouched confirmatory validation, and uncertainty intervals do not absorb all feature-selection or model-selection uncertainty.")
    para(doc, "Cohort membership was strongly", "Cohort membership was strongly separable, but age structure, sequencing differences, unavailable external sex/ancestry, and possible pretraining overlap are entangled. The corrected −0.240, −0.087, and −0.067 development-to-external AUROC differences are descriptive and lack direct CIs for the gaps. This two-cohort design does not show that internal cross-validation is generally biased.")
    para(doc, "Preregistered cell-type harmonization", "Preregistered cell-type harmonization and cell-type-resolved analyses were not performed because public external cell-type annotations and the planned label-transfer implementation were unavailable (deviations item 2). Prespecified age-stratified permutation p-values and stratified co-primary tests were not produced; revised age-stratified AUROCs are descriptive. Historical arm-level permutation procedures also differed in hyperparameter retuning.")
    para(doc, "Pseudobulk external scoring", "Pseudobulk external scoring required the 30,165-gene intersection. The restricted-space development AUROC effect was small (+0.00125), but its above-chance permutation p-value is not an effect test. Model-native Geneformer input was an exploratory sensitivity analysis: external AUROC 0.7484 versus 0.7344 for shared-gene input (paired difference +0.0141, 95% CI −0.0238 to +0.0597; two-sided paired DeLong p = 0.4601). Neither native-input co-primary Geneformer-superiority criterion was met.")
    para(doc, "The sealing mechanism provided", "The original sealing mechanism supplied precommitment and file-integrity checks but did not technically block every historical external-path script. The correction preserved original artifacts and preregistered rules, recorded a new V1 checkpoint/runtime/feature provenance chain, and reanalyzed the already examined external data. Findings apply to frozen V1-10M cell embeddings, donor mean pooling, and L2 logistic regression. Other encoder versions, fine-tuning, cell-type strategies, cohorts, and possible Geneformer pretraining overlap were not assessed.")
    para(doc, "The released donor-level results", "The corrected shared-gene V1 analysis yielded external AUROC 0.7344 and did not meet either prespecified Geneformer-superiority criterion under paired DeLong/Holm inference and paired donor-bootstrap intervals. The native-input sensitivity was similar. This corrected reanalysis does not constitute a new untouched validation on the previously examined external cohort.")
    para(doc, "These findings do not establish", "The result does not establish that Geneformer is generally inferior, that pseudobulk is always preferable, or that any model is suitable for clinical diagnosis. It shows that one corrected frozen representation did not provide the prespecified added value in a small, distribution-shifted external cohort. Independent replication in another cohort is required for broader claims.")
    para(doc, "Data and code availability", "Data and code availability. Development data are available through the CZ CELLxGENE Census (collection 436154da-bcf1-4130-9c8b-120ff9a888f2; census version 2025-11-08), and external data through GEO GSE135779. Original preregistration and release commit 6158a840 remain preserved. Corrected extraction, validation, donor predictions, paired analyses, figures, dependency locks, and artifact hashes are versioned at https://github.com/mohamad679/lupus-singlecell-foundation on the scientific-correction-2026 branch. Supplementary Table S1 maps each main numerical claim to its source artifact.")
    para(doc, "Figure 1. Development-cohort", "Figure 1. Corrected shared-gene main analysis: development nested-CV and external fixed-model AUROCs for Geneformer V1, restricted pseudobulk, and age. Points are estimates and whiskers are separate 95% donor-bootstrap intervals; connecting lines are descriptive, not intervals for an internal-to-external effect. Geneformer development n = 261 and external n = 56; age development n = 259.")
    para(doc, "Figure 2. External-cohort", "Figure 2. Corrected external donor-level AUROC by source-defined Children (n = 44) and Adult (n = 12) categories. Whiskers are 95% donor-bootstrap intervals. The Adult subgroup has 7 SLE and 5 healthy samples; some donors aged 18–19 are in the source Children category.")
    para(doc, "Figure 3. Co-primary", "Figure 3. Corrected co-primary external comparisons. Points are paired Geneformer-minus-comparator AUROC differences and whiskers are 95% paired donor-bootstrap intervals. Displayed p-values are two-sided paired DeLong tests adjusted by Holm across the two comparisons. “Rule not met” denotes failure of the prespecified positive Geneformer-superiority conditions.")
    para(doc, "Figure 4. Cohort-signature", "Figure 4. Post-hoc cohort-membership diagnostic using corrected shared-gene Geneformer vectors and preserved pseudobulk/age feature probes. The target is development versus external cohort origin, not SLE. The diagnostic quantifies feature-space separability without identifying a cause of disease-classification performance.")
    t1, t2, t3 = doc.tables[:3]
    cell(t1, 7, 1, "1,263,676 cells contributing to corrected embeddings")
    cell(t1, 7, 2, "363,083 cells contributing to corrected embeddings")
    cell(t1, 4, 2, "7–63 y (mean 20.9, SD 12.8); 44 source Children (including seven aged 18–19) / 12 Adult")
    cell(t2, 0, 3, "Historical above-chance p")
    cell(t2, 0, 6, "Historical above-chance p")
    cell(t2, 1, 0, "Geneformer V1, shared genes")
    cell(t2, 1, 2, fmt_ci(d["modes"]["shared"]["development_geneformer"]))
    cell(t2, 1, 3, "—")
    cell(t2, 1, 5, fmt_ci(d["modes"]["shared"]["external"]["geneformer"]["overall"]))
    cell(t2, 1, 6, "—")
    cell(t2, 3, 5, fmt_ci(d["modes"]["shared"]["external"]["pseudobulk"]["overall"]))
    cell(t2, 4, 5, fmt_ci(d["modes"]["shared"]["external"]["metadata_only_age"]["overall"]))
    cell(t3, 0, 2, "95% paired donor-bootstrap CI")
    cell(t3, 0, 3, "Paired DeLong p / Holm p")
    cell(t3, 1, 1, "+0.1563")
    cell(t3, 1, 2, "−0.0859 to +0.4040")
    cell(t3, 1, 3, "0.2046 / 0.2046")
    cell(t3, 2, 1, "−0.1641")
    cell(t3, 2, 2, "−0.2916 to −0.0384")
    cell(t3, 2, 3, "0.0088 / 0.0175")
    for i in (1, 2):
        cell(t3, i, 4, "Not met")
    finalize(doc, target)


def supplement(source, target, d, shared, native, sensitivity, probe):
    doc = Document(source)
    drop(doc, "WORKING CORRECTION DRAFT")
    para(doc, "Supplementary Table S1. Historical", "Supplementary Table S1. Corrected quantitative claim-to-artifact map")
    t1, t2 = doc.tables[:2]
    updates = {
        1: ("Corrected development Geneformer AUROC and interval", "results/correction_2026-09/corrected_v1_descriptive.json", "modes.shared.development_geneformer"),
        4: ("Corrected Geneformer C selections and final C", "results/correction_2026-09/corrected_v1_shared_fit_report.json", "development_selected_c_per_outer_fold; final_c_median"),
        5: ("Historical Geneformer frozen C, retained", "FREEZE.json", "hyperparameters.geneformer.C_per_outer_fold; C_frozen"),
        8: ("Corrected external AUROC, AP, Brier, calibration", "results/correction_2026-09/corrected_v1_shared_analysis.json", "metrics.<arm>; also corrected_v1_descriptive.json for AUROC CIs"),
        9: ("Corrected paired AUROC differences, intervals, DeLong/Holm", "results/correction_2026-09/corrected_v1_shared_analysis.json", "comparisons.geneformer_vs_age; geneformer_vs_pseudobulk"),
        10: ("Historical decision terminology", "results/l2_sealed_results.json", "REJECTED in original release; Not met in revised manuscript"),
        11: ("Corrected Geneformer cohort-membership probe", "results/correction_2026-09/corrected_v1_shared_cohort_probe.json", "cohort_membership_auroc; ci95"),
    }
    for row, values in updates.items():
        for col, value in enumerate(values):
            cell(t1, row, col, value)
    for values in [
        ("Corrected external age strata", "results/correction_2026-09/corrected_v1_descriptive.json", "modes.shared.external.<arm>.Children/Adult"),
        ("V1 extraction and donor/cell accounting", "results/correction_2026-09/shared_features/", "two *_run_summary.json and ingestion_validation.json files"),
        ("Model-native Geneformer sensitivity", "results/correction_2026-09/corrected_v1_native_analysis.json", "metrics.geneformer; comparisons"),
        ("Native minus shared input paired effect", "results/correction_2026-09/corrected_v1_gene_input_sensitivity.json", "native_minus_shared"),
        ("Gene availability diagnostic", "results/correction_2026-09/historical_gene_availability.json", "shared_genes; development_zero_but_external_expressed_genes"),
    ]:
        row = t1.add_row()
        for c, value in enumerate(values):
            row.cells[c].text = value
    para(doc, "Terminology note.", "All corrected values are from versioned artifacts under results/correction_2026-09. The original release and preregistration remain visible. The repository's historical decision token REJECTED is rendered as “Not met” for the prespecified Geneformer-superiority criterion. This correction used the previously examined external cohort.")
    [p for p in doc.paragraphs if p.text.startswith("All corrected values are")][0].paragraph_format.keep_together = True
    cell(t2, 0, 1, "Source Children (n = 44)")
    cell(t2, 0, 2, "Source Adult (n = 12)")
    for row, arm in enumerate(("geneformer", "pseudobulk", "metadata_only_age"), start=1):
        cell(t2, row, 1, fmt_ci(d["modes"]["shared"]["external"][arm]["Children"]))
        cell(t2, row, 2, fmt_ci(d["modes"]["shared"]["external"][arm]["Adult"]))
    para(doc, "Values are AUROC", "Values are AUROC (95% percentile donor-bootstrap CI), based on 5000 draws of fixed predictions. The source Adult stratum had 7 SLE and 5 healthy samples; 10 of 5000 bootstrap draws were single-class and discarded. The source Children group includes some donors aged 18 or 19. Prespecified stratum-specific permutation and co-primary tests were not completed and are reported as protocol deviations.")
    p = doc.add_paragraph()
    p.add_run("Supplementary provenance and sensitivity").bold = True
    doc.add_paragraph("Shared-gene main analysis: 261 development donors and 1,263,676 cells; 56 external samples and 363,083 cells; 256-dimensional finite donor vectors. The same pinned Geneformer V1 revision, checkpoint/dictionary hashes, V1 settings, eight-cell technical fixture, and 30,165-gene intersection were verified in both cohorts. The run summaries and ingestion validations contain the exact SHA-256 hashes and runtime package inventories. The original uploaded ZIPs were retained outside the repository.")
    doc.add_paragraph("Model-native input was a labeled exploratory sensitivity, not a replacement primary analysis. Development Geneformer AUROC was 0.9754 (95% CI 0.9573–0.9898); external AUROC was 0.7484 (0.6122–0.8699). Native minus shared external AUROC was +0.0141 (paired 95% CI −0.0238 to +0.0597; two-sided paired DeLong p = 0.4601). Native Geneformer minus age was +0.1703 (Holm p = 0.1595); native Geneformer minus pseudobulk was −0.1500 (Holm p = 0.0181). Neither native comparison met a positive Geneformer-superiority rule.")
    doc.add_paragraph("Calibration is diagnostic and did not alter predictions. External Brier scores were 0.4713 for corrected shared-gene Geneformer, 0.1489 for pseudobulk, 0.2156 for age, and 0.2128 for a constant probability fixed at development SLE prevalence (162/261). Estimated recalibration slopes were 0.1845, 0.5453, and −5.4144, respectively; the age slope is unstable. These analyses are exploratory on the previously examined cohort.")
    p = doc.add_paragraph()
    p.add_run("Supplementary reporting and bias assessment").bold = True
    doc.add_paragraph("TRIPOD+AI reporting items were mapped to the revised title/abstract, source and eligibility, donor-level outcome and predictors, missing age handling, model fitting and validation, participant accounting, discrimination, calibration, open code, and limitations. The repository audit records each location and remaining gap. A PROBAST+AI-informed appraisal flags high risk of bias or major applicability concern for clinical prediction because the external sample is small and demographically different, correction followed examination of the external outcomes, pretraining overlap is unknown, and clinical-use thresholds and utility were not evaluated. This is an author-conducted assessment, not an independent adjudication.")
    finalize(doc, target)


def simple(source, target, replacements, *, remove_notice=True):
    doc = Document(source)
    if remove_notice:
        drop(doc, "WORKING CORRECTION DRAFT")
    for old, new in replacements:
        para(doc, old, new)
    finalize(doc, target)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--documents-dir", type=Path, default=ROOT.parent)
    parser.add_argument("--out-dir", type=Path, default=ROOT.parent / "corrected_submission_2026-09")
    args = parser.parse_args()
    args.out_dir.mkdir(exist_ok=True)
    d = load("corrected_v1_descriptive.json")
    shared = load("corrected_v1_shared_analysis.json")
    native = load("corrected_v1_native_analysis.json")
    sensitivity = load("corrected_v1_gene_input_sensitivity.json")
    probe = load("corrected_v1_shared_cohort_probe.json")
    if abs(shared["metrics"]["geneformer"]["auroc"]-.734375) > 1e-10 or abs(native["metrics"]["geneformer"]["auroc"]-.7484375) > 1e-10:
        raise ValueError("source analysis differs from manuscript constants")
    pairs = [("CBC_Manuscript_Research_Paper", manuscript),
             ("CBC_Supplementary_Material", supplement)]
    for stem, fn in pairs:
        fn(args.documents_dir / f"{stem}_Correction_Working_Draft.docx",
           args.out_dir / f"{stem}_Corrected_2026-09.docx", d, shared, native, sensitivity, probe)
    title = "External transport of donor-level SLE classifiers across two cohorts: corrected Geneformer V1 and pseudobulk analysis"
    simple(args.documents_dir / "CBC_Title_Page_Correction_Working_Draft.docx",
           args.out_dir / "CBC_Title_Page_Corrected_2026-09.docx",
           [("External transport of donor-level", title),
            ("Zenodo software snapshot v1.0.0", "Zenodo historical software snapshot v1.0.0: DOI 10.5281/zenodo.21841692; corrected analysis: scientific-correction-2026 branch of the public repository")])
    simple(args.documents_dir / "CBC_Highlights_Correction_Working_Draft.docx",
           args.out_dir / "CBC_Highlights_Corrected_2026-09.docx",
           [("Historical within-cohort", "Corrected V1 Geneformer AUROC was 0.9746 internally and 0.7344 externally."),
            ("The Geneformer comparison", "Neither prespecified Geneformer-superiority comparison met its criterion."),
            ("Released external AUROC", "Pseudobulk external AUROC was 0.8984; age AUROC was 0.5781."),
            ("Cohort feature separability", "This is a corrected reanalysis of a previously examined external cohort.")])
    simple(args.documents_dir / "CBC_Cover_Letter_Correction_Working_Draft.docx",
           args.out_dir / "CBC_Cover_Letter_Corrected_2026-09.docx",
           [("29 September 2026", "30 September 2026"),
            ("Submission request pending", f"Please consider our manuscript, “{title}”, as a Research Paper."),
            ("The Geneformer extraction", "The initial release used unsupported Geneformer V1 extraction settings and an invalid equal-AUROC comparison. We preserve that release and report a versioned correction: explicit V1 tokenization and cell embeddings, paired DeLong/Holm inference, and a model-native sensitivity analysis. In the 56 previously examined external samples, corrected shared-gene Geneformer AUROC was 0.7344 versus 0.8984 for pseudobulk and 0.5781 for age; neither prespecified Geneformer-superiority criterion was met. We clearly identify this as corrected reanalysis rather than a new untouched validation."),
            ("The manuscript is original", "The manuscript is original, has not been published previously, and is not under consideration by another journal. The author has approved the submitted version and declares no competing interests. The analyses use previously published, de-identified public datasets. The manuscript identifies the public code repository and distinguishes its historical Zenodo software snapshot from the corrected branch. Generative-AI assistance is disclosed in the manuscript; the author takes responsibility for the content.")])
    print(args.out_dir)


if __name__ == "__main__":
    main()
