"""Reconcile GEO accessions and run the one-record external age sensitivity.

The paper supplement's age 43 for aHD3 is review-reported because the original
XLSX could not be archived here. GEO's age 50 and the 56 sample IDs are checked
against dated primary-source SOFT downloads stored under docs/source_records.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

from correction_stats import holm_adjust, paired_bootstrap_ci, paired_delong

ROOT = Path(__file__).resolve().parents[1]
GEO_SERIES_URL = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE135779&targ=self&form=text&view=full"
GEO_SAMPLE_URL = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM4029942&targ=self&form=text&view=full"
SOURCE_SUPPLEMENT_URL = "https://pmc.ncbi.nlm.nih.gov/articles/instance/7442743/bin/NIHMS1605899-supplement-1.xlsx"
CHANGED_GSM = "GSM4029942"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def geo_field(text: str, name: str) -> list[str]:
    return re.findall(rf"^!{re.escape(name)} = (.*)$", text, flags=re.MULTILINE)


def run(root: Path) -> dict:
    source_dir = root / "docs/source_records"
    series_file = source_dir / "GSE135779_series_SOFT_2026-09-30.txt"
    sample_file = source_dir / "GSM4029942_sample_SOFT_2026-09-30.txt"
    series_text = series_file.read_text()
    sample_text = sample_file.read_text()
    geo_ids = geo_field(series_text, "Series_sample_id")
    if len(geo_ids) != 56 or len(set(geo_ids)) != 56:
        raise ValueError("GEO series does not contain 56 unique sample IDs")
    sample_age = [v for v in geo_field(sample_text, "Sample_characteristics_ch1") if v.startswith("age: ")]
    if geo_field(sample_text, "Sample_geo_accession") != [CHANGED_GSM] or sample_age != ["age: 50"]:
        raise ValueError("GEO aHD3 accession or age differs from primary-source record")

    results = root / "results"
    corr = results / "correction_2026-09"
    external = pd.read_csv(results / "l2_sealed_donor_metadata.csv", dtype={"gsm_id": str})
    development = pd.read_csv(results / "l2_dev_donor_metadata.csv", dtype={"donor_id": str})
    if len(external) != 56 or set(external.gsm_id) != set(geo_ids):
        raise ValueError("repository metadata does not match GEO series sample IDs")
    labels = external.title.str.extract(r"^((?:cSLE|cHD|aSLE|aHD)\d+) \[([A-Z0-9]+)\]$")
    if labels.isna().any().any() or labels[0].duplicated().any():
        raise ValueError("source sample labels are absent or duplicated")
    if external.loc[external.gsm_id == CHANGED_GSM, "age"].tolist() != [50]:
        raise ValueError("repository aHD3 age differs from GEO age 50")

    crosswalk = external[["gsm_id", "title", "age", "age_group", "group", "n_cells"]].copy()
    crosswalk.rename(columns={"age": "geo_age_years", "age_group": "geo_age_group",
                              "group": "geo_group", "n_cells": "analyzed_cells"}, inplace=True)
    crosswalk.insert(2, "source_sample_label", labels[0])
    crosswalk.insert(3, "source_subject_id", labels[1])
    crosswalk["supplement_age_years_review_reported"] = pd.NA
    crosswalk.loc[crosswalk.gsm_id == CHANGED_GSM, "supplement_age_years_review_reported"] = 43
    crosswalk["source_priority"] = "GEO SOFT age retained for primary analysis"
    crosswalk["reconciliation_status"] = "GEO sample present; source supplement not independently archived"
    crosswalk.loc[crosswalk.gsm_id == CHANGED_GSM, "reconciliation_status"] = (
        "GEO 50 verified; supplement 43 review-reported; conflicting source ages"
    )
    described = {f"cSLE{i}" for i in range(1, 34)} | {f"cHD{i}" for i in range(1, 12)} | {f"aSLE{i}" for i in range(1, 9)} | {f"aHD{i}" for i in range(1, 7)}
    missing = sorted(described - set(labels[0]))
    if missing != ["aHD2", "aSLE8"]:
        raise ValueError(f"unexpected missing source sample labels: {missing}")
    for label in missing:
        crosswalk.loc[len(crosswalk)] = {
            "gsm_id": "", "title": "", "source_sample_label": label,
            "source_subject_id": "", "geo_age_years": pd.NA,
            "geo_age_group": "", "geo_group": "", "analyzed_cells": pd.NA,
            "supplement_age_years_review_reported": pd.NA,
            "source_priority": "not analyzed", "reconciliation_status":
            "described in source cohort; absent from 56 GEO series samples",
        }
    crosswalk_path = corr / "external_source_to_gsm_crosswalk.csv"
    crosswalk.to_csv(crosswalk_path, index=False)

    eligible = development.loc[development.metadata_arm_eligible]
    scaler = StandardScaler().fit(eligible[["age"]].to_numpy(dtype=float))
    model = LogisticRegression(C=0.001, l1_ratio=0, max_iter=2000, solver="lbfgs")
    model.fit(scaler.transform(eligible[["age"]].to_numpy(dtype=float)),
              eligible.sle_label.to_numpy(dtype=int))
    X = external[["age"]].to_numpy(dtype=float)
    original = model.predict_proba(scaler.transform(X))[:, 1]
    predictions = json.loads((corr / "corrected_v1_shared_predictions.json").read_text())
    age_row = predictions["metadata_only_age"]
    if age_row["donor_ids"] != external.gsm_id.tolist():
        raise ValueError("age predictions and metadata keys are misaligned")
    if not np.allclose(original, age_row["proba"], rtol=0, atol=1e-12):
        raise ValueError("refitted historical age model does not reproduce primary scores")
    X_alt = X.copy()
    changed_idx = external.index[external.gsm_id == CHANGED_GSM].tolist()
    if len(changed_idx) != 1:
        raise ValueError("aHD3 sample must occur exactly once")
    X_alt[changed_idx[0], 0] = 43
    alternate = model.predict_proba(scaler.transform(X_alt))[:, 1]
    if np.count_nonzero(original != alternate) != 1:
        raise ValueError("age sensitivity changed more than one probability")
    y = external.sle_label.to_numpy(dtype=int)
    gf = np.asarray(predictions["geneformer"]["proba"], dtype=float)
    adult = external.age_group.to_numpy() == "Adult"
    comparison = {**paired_delong(y, gf, alternate), **paired_bootstrap_ci(y, gf, alternate)}
    pb_p = paired_delong(y, gf, predictions["pseudobulk"]["proba"])["p_two_sided"]
    comparison["holm_adjusted_p"] = holm_adjust({"age": comparison["p_two_sided"], "pseudobulk": pb_p})["age"]
    comparison["superiority_rule_met"] = comparison["ci95"][0] > 0 and comparison["holm_adjusted_p"] <= 0.05
    output = {
        "status": "exploratory source-age sensitivity; primary GEO age 50 retained",
        "source_priority_rule": "Use public GEO SOFT age for all primary age-model predictions; vary only the conflict in a labeled sensitivity.",
        "source_records": {
            "GSE135779": {"url": GEO_SERIES_URL, "local_path": str(series_file.relative_to(root)), "sha256": digest(series_file), "field": "Series_sample_id", "n_samples": 56},
            CHANGED_GSM: {"url": GEO_SAMPLE_URL, "local_path": str(sample_file.relative_to(root)), "sha256": digest(sample_file), "fields": ["Sample_geo_accession", "Sample_characteristics_ch1: age"], "geo_age_years": 50},
            "publication_supplement": {"url": SOURCE_SUPPLEMENT_URL, "sha256": None,
                                       "status": "original XLSX unavailable; age 43 and sample-name reconciliation taken from supplied independent review"},
        },
        "crosswalk": str(crosswalk_path.relative_to(root)),
        "source_labels_absent_from_public_geo_deposit": missing,
        "absence_reason": "unresolved",
        "supplement_ST4": "Publication describes per-individual cluster/subcluster cell counts; exact barcode-level labels for analyzed raw matrices not established.",
        "age_conflict": {"gsm_id": CHANGED_GSM, "sample_label": "aHD3", "source_subject_id": "JB19003",
                         "geo_age_years": 50, "supplement_age_years_review_reported": 43,
                         "analyzed_cells": int(external.loc[changed_idx[0], "n_cells"]),
                         "primary_age_model_probability": float(original[changed_idx[0]]),
                         "sensitivity_age_model_probability": float(alternate[changed_idx[0]])},
        "primary_age_auroc": float(roc_auc_score(y, original)),
        "sensitivity_age_auroc": float(roc_auc_score(y, alternate)),
        "primary_adult_age_auroc": float(roc_auc_score(y[adult], original[adult])),
        "sensitivity_adult_age_auroc": float(roc_auc_score(y[adult], alternate[adult])),
        "shared_geneformer_minus_sensitivity_age": comparison,
        "primary_predictions_sha256": digest(corr / "corrected_v1_shared_predictions.json"),
    }
    out = corr / "external_age_source_sensitivity.json"
    out.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()
    print(json.dumps(run(args.repo_root), indent=2, allow_nan=False))
