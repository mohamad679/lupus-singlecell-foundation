"""Run the Stage 7 internal confounding audit."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from lupusfm.evaluation.stage7_confounding_audit import (
    DEFAULT_METADATA_ARTIFACT,
    DEFAULT_OUTPUT_DIR,
    run_confounding_audit,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the Stage 7 internal confounding audit for batch/source, "
            "patient cell count, and cell-type composition without using "
            "Geneformer embeddings."
        )
    )
    parser.add_argument(
        "--metadata-artifact",
        type=Path,
        default=DEFAULT_METADATA_ARTIFACT,
        help="Local metadata artifact path. Supports .h5ad, .csv, and .parquet.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for audit CSV, summary JSON, and README outputs.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = run_confounding_audit(
        metadata_artifact=args.metadata_artifact,
        output_dir=args.output_dir,
    )

    print("Stage 7 confounding audit")
    print(f"status: {summary['status']}")
    print(f"metadata_artifact: {summary['metadata_artifact']}")
    print(f"patient_confounding_manifest: {summary['patient_confounding_manifest']}")
    print(f"cell_count_audit: {summary['cell_count_audit']}")
    print(f"cell_type_composition_audit: {summary['cell_type_composition_audit']}")
    print(f"source_batch_audit: {summary['source_batch_audit']}")
    print(f"confounding_audit_summary: {summary['confounding_audit_summary']}")
    print(f"report: {summary['report']}")
    if summary["status"] != "completed":
        print(f"blocker: {summary.get('blocker', '')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
