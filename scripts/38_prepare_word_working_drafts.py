"""Create clearly provisional Word drafts while corrected embeddings are pending.

Uses only the standard library and preserves every unchanged DOCX zip member.
Original submitted documents are never overwritten. Result-dependent final
editing must follow the corrected reanalysis, not this interim preparation.
"""

from __future__ import annotations

import argparse
import html
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

TITLE = "External transport of donor-level SLE classifiers: a preregistered comparison of Geneformer and pseudobulk across two cohorts"
NOTICE = ("WORKING CORRECTION DRAFT — NOT FOR SUBMISSION. The released Geneformer "
          "feature extraction and co-primary p-values require correction. All "
          "Geneformer-dependent estimates and figures below describe the historical "
          "release and remain provisional until the versioned rerun is complete.")
PARAGRAPH = re.compile(r"<w:p(?:\s[^>]*)?>.*?</w:p>", re.DOTALL)
NAMESPACE = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def text_of(paragraph):
    fragment = f'<root xmlns:w="{NAMESPACE["w"]}">{paragraph}</root>'
    element = ET.fromstring(fragment)
    return "".join(t.text or "" for t in element.findall(".//w:t", NAMESPACE))


def rewrite_paragraph(paragraph, new_text):
    properties = re.search(r"<w:pPr>.*?</w:pPr>", paragraph, re.DOTALL)
    style = properties.group(0) if properties else ""
    return f'<w:p>{style}<w:r><w:t xml:space="preserve">{html.escape(new_text)}</w:t></w:r></w:p>'


def transform(xml, replacements, *, notice=True):
    matches = list(PARAGRAPH.finditer(xml))
    paragraphs = [match.group(0) for match in matches]
    original = [text_of(p) for p in paragraphs]
    for prefix, replacement in replacements.items():
        found = [i for i, value in enumerate(original) if value.startswith(prefix)]
        if len(found) != 1:
            raise ValueError(f"expected one paragraph beginning {prefix!r}, found {len(found)}")
        paragraphs[found[0]] = rewrite_paragraph(paragraphs[found[0]], replacement)
    if notice:
        notice_xml = rewrite_paragraph('<w:p><w:pPr><w:pStyle w:val="BodyText"/></w:pPr></w:p>', NOTICE)
        paragraphs[0] += notice_xml
    pieces = []
    cursor = 0
    for match, replacement in zip(matches, paragraphs):
        pieces.extend((xml[cursor:match.start()], replacement))
        cursor = match.end()
    pieces.append(xml[cursor:])
    return "".join(pieces)


def write_draft(source, target, replacements):
    with zipfile.ZipFile(source) as input_doc, zipfile.ZipFile(target, "w") as output_doc:
        for member in input_doc.infolist():
            data = input_doc.read(member.filename)
            if member.filename == "word/document.xml":
                revised = transform(data.decode("utf-8"), replacements)
                ET.fromstring(revised)
                data = revised.encode("utf-8")
            output_doc.writestr(member, data)
    with zipfile.ZipFile(target) as output_doc:
        if output_doc.testzip() is not None:
            raise ValueError(f"corrupt DOCX member in {target}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", type=Path, required=True)
    args = parser.parse_args()
    folder = args.folder
    edits = {
        "CBC_Manuscript_Research_Paper.docx": {
            "Internal cross-validation can overstate": TITLE,
            "Objective. Single-cell foundation models": (
                "Objective. We evaluate transport of donor-level SLE versus healthy-control classifiers "
                "from an adult development cohort to a predominantly pediatric external cohort. "
                "The released Geneformer analysis is under methodological correction."
            ),
            "Geneformer. Per-cell Geneformer-V1-10M embeddings": (
                "Geneformer (historical release). The published extraction scripts selected V1 weights "
                "but omitted model_version=V1 and requested CLS embeddings. This configuration does not "
                "establish a valid standard V1 representation. The corrected shared-gene primary analysis "
                "will use explicit V1 tokenization, cell embeddings from the penultimate layer, and "
                "donor mean pooling; model-native input will be a sensitivity analysis."
            ),
            "Not separately tallied in this study": "363,083 cells in the released external donor metadata, before corrected tokenization",
            "Results. In five-fold nested cross-validation": (
                "Results (historical release; corrected results pending). The released development and "
                "external Geneformer AUROCs were 0.9676 and 0.8156, respectively; pseudobulk external "
                "AUROC was 0.8984 and age external AUROC was 0.5781. These values reproduce from released "
                "features, but the Geneformer input semantics are unresolved. Released co-primary "
                "label-permutation p-values do not test equal correlated AUROCs. Corrected V1 "
                "representations and paired inference will replace these results before submission."
            ),
            "Conclusion. Geneformer did not demonstrate": (
                "Conclusion (provisional). The historical release did not establish a Geneformer "
                "advantage over either comparator. A scientific conclusion about corrected V1 features "
                "must wait for the versioned rerun. The small, demographically different external "
                "cohort limits generalization."
            ),
            "Success required both (i)": (
                "Historical co-primary rule. The preregistration required a positive paired donor-bootstrap "
                "95% CI and Holm-significant p-values. The released label-shuffle comparison tested label "
                "exchangeability, not equality of correlated AUROCs. The versioned correction will use "
                "paired DeLong inference, retain paired bootstrap intervals, and apply Holm correction."
            ),
            "Restricting development pseudobulk": (
                "Restricting development pseudobulk to the shared 30,165-gene space changed pooled "
                "development AUROC by +0.00125 (paired bootstrap 95% CI −0.00039 to +0.00321). "
                "Separately, the restricted arm discriminated above chance under a fixed-C label-permutation "
                "procedure (p = 0.000999); this p-value does not test the restriction effect."
            ),
            "Table 3. Co-primary comparisons": "Table 3. Historical co-primary comparisons from released scores; corrected V1 results pending.",
            "Permutation p (pre-Holm)": "Historical label-permutation p (pre-Holm; not a valid equal-AUROC test)",
            "Age-stratified external AUROCs are reported": (
                "Historical age-stratified external AUROCs are shown in Supplementary Table S2 and Figure 2; "
                "all Geneformer values and corresponding graphics await corrected extraction. The source-defined "
                "Children group has 44 donors, including some aged 18 or 19; the adult group has 12 "
                "donors (7 SLE, 5 healthy), so its AUROC is highly uncertain."
            ),
            "Neither comparison met the prespecified criterion": (
                "In the historical release, neither comparison met the preregistered rule. The "
                "label-shuffle p-values in Table 3 cannot be interpreted as valid tests of equal "
                "correlated AUROCs. An exploratory paired DeLong analysis of the same released "
                "scores gives two-sided p = 0.0921 for Geneformer versus age and p = 0.1590 "
                "for Geneformer versus pseudobulk; neither passes Holm correction. These analyses "
                "do not validate the Geneformer extraction."
            ),
            "In this preregistered external validation, frozen Geneformer": (
                "The released donor-level results are numerically reproducible from their feature "
                "matrices, but the advertised V1 representation remains unverified. The co-primary "
                "comparison and paper conclusions must be reassessed after corrected V1 extraction "
                "and paired inference. This already examined external cohort supports a corrected "
                "reanalysis, not a new untouched confirmatory test."
            ),
        },
        "CBC_Supplementary_Material.docx": {
            "Supplementary Table S1. Principal quantitative claim-to-artifact map":
                "Supplementary Table S1. Historical quantitative claim-to-artifact map; corrected analysis pending",
        },
        "CBC_Title_Page.docx": {"Internal cross-validation can overstate": TITLE},
        "CBC_Highlights.docx": {
            "Strong internal discrimination did not establish": "Historical within-cohort performance does not establish transport to a different cohort.",
            "Geneformer showed no statistically supported": "The Geneformer comparison is pending corrected V1 extraction and paired inference.",
            "All three model arms had lower": "Released external AUROC point estimates were lower for all three arms; corrected Geneformer values are pending.",
            "Transcriptomic feature spaces almost perfectly": "Cohort feature separability is a distribution diagnostic, not an estimate of causal batch effects.",
        },
        "CBC_Cover_Letter.docx": {
            "8 August 2026": "29 September 2026 — working correction draft; not for submission",
            "Please consider the manuscript entitled": (
                f"Submission request pending corrected reanalysis. Proposed manuscript title: “{TITLE}”."
            ),
            "Geneformer achieved high internal discrimination": (
                "The Geneformer extraction and paired inference are being corrected in a versioned "
                "reanalysis. This draft letter must be rewritten after the revised results and figures "
                "are complete."
            ),
        },
    }
    for filename, replacements in edits.items():
        source = folder / filename
        target = folder / filename.replace(".docx", "_Correction_Working_Draft.docx")
        write_draft(source, target, replacements)
        print(target)


if __name__ == "__main__":
    main()
