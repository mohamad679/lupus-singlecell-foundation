"""Run the Stage 7 metadata-only internal LOOCV control baseline."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from lupusfm.evaluation.stage7_metadata_baseline import (
    DEFAULT_METADATA_ARTIFACT,
    DEFAULT_OUTPUT_DIR,
    run_metadata_baseline,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the Stage 7 metadata-only internal confounding-control baseline "
            "without using Geneformer embeddings."
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
        help="Directory for manifest, predictions, metrics, summary, and README outputs.",
    )
    parser.add_argument("--c-value", type=float, default=0.1)
    parser.add_argument("--max-iter", type=int, default=1000)
    parser.add_argument("--random-state", type=int, default=42)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = run_metadata_baseline(
        metadata_artifact=args.metadata_artifact,
        output_dir=args.output_dir,
        c_value=args.c_value,
        max_iter=args.max_iter,
        random_state=args.random_state,
    )

    print("Stage 7 metadata-only baseline")
    print(f"status: {summary['status']}")
    print(f"metadata_artifact: {summary['metadata_artifact']}")
    print(f"metadata_feature_manifest: {summary['metadata_feature_manifest']}")
    print(f"metadata_baseline_predictions: {summary['metadata_baseline_predictions']}")
    print(f"metadata_baseline_metrics: {summary['metadata_baseline_metrics']}")
    print(f"report: {summary['report']}")
    if summary["status"] != "completed":
        print(f"blocker: {summary.get('blocker', '')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
