"""Compare corrected V1 native and shared-gene external predictions by donor."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from correction_stats import paired_bootstrap_ci, paired_delong, probability_metrics


ARMS = ("geneformer", "pseudobulk", "metadata_only_age")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare(shared: dict, native: dict) -> dict:
    for mode, predictions in (("shared", shared), ("native", native)):
        base = predictions["geneformer"]
        for arm in ARMS:
            row = predictions[arm]
            if (row["donor_ids"] != base["donor_ids"] or row["y"] != base["y"]
                    or len(row["proba"]) != len(base["donor_ids"])):
                raise ValueError(f"{mode}/{arm}: donor keys, labels, or scores are misaligned")
    for arm in ARMS:
        a, b = shared[arm], native[arm]
        if a["donor_ids"] != b["donor_ids"] or a["y"] != b["y"]:
            raise ValueError(f"{arm}: donor keys or labels differ between modes")
        if len(a["donor_ids"]) != len(set(a["donor_ids"])):
            raise ValueError(f"{arm}: duplicate donor keys")
        if arm != "geneformer" and a["proba"] != b["proba"]:
            raise ValueError(f"{arm}: comparator probabilities differ between modes")
    shared_gf, native_gf = shared["geneformer"], native["geneformer"]
    y = shared_gf["y"]
    if len(y) != 56 or sum(y) != 40:
        raise ValueError("external cohort labels or sample count differ")
    prevalence = 162 / 261
    shared_metrics = probability_metrics(y, shared_gf["proba"],
                                         development_prevalence=prevalence)
    native_metrics = probability_metrics(y, native_gf["proba"],
                                         development_prevalence=prevalence)
    return {
        "analysis": "exploratory model-native input sensitivity on previously examined external cohort",
        "n_samples": len(y), "n_case": sum(y), "n_control": len(y) - sum(y),
        "shared_geneformer": shared_metrics,
        "native_geneformer": native_metrics,
        "native_minus_shared": {
            **paired_delong(y, native_gf["proba"], shared_gf["proba"]),
            **paired_bootstrap_ci(y, native_gf["proba"], shared_gf["proba"]),
        },
        "interpretation_limit": (
            "Exploratory paired comparison of two corrected representations on the same "
            "previously examined external samples; no new confirmatory cohort."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shared-predictions", type=Path, required=True)
    parser.add_argument("--native-predictions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.resolve() in {args.shared_predictions.resolve(),
                                 args.native_predictions.resolve()}:
        raise ValueError("output cannot overwrite input predictions")
    shared = json.loads(args.shared_predictions.read_text())
    native = json.loads(args.native_predictions.read_text())
    result = compare(shared, native)
    result["shared_predictions_sha256"] = sha256(args.shared_predictions)
    result["native_predictions_sha256"] = sha256(args.native_predictions)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(args.output)


if __name__ == "__main__":
    main()
