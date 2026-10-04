"""Run the Stage 7 Geneformer-level perturbation plausibility scaffold."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from lupusfm.evaluation.stage7_geneformer_perturbation_plausibility import (
    DEFAULT_MODE,
    DEFAULT_OUTPUT_DIR,
    SYNTHETIC_DRY_RUN_MODE,
    run_geneformer_perturbation_plausibility,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a safe Stage 7 Geneformer-level perturbation plausibility scaffold. "
            "Default mode is plan-only and does not execute Geneformer or recompute embeddings."
        )
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for perturbation plan, score-shift schema, summary JSON, and README.",
    )
    parser.add_argument(
        "--mode",
        choices=[DEFAULT_MODE, SYNTHETIC_DRY_RUN_MODE],
        default=DEFAULT_MODE,
        help="`plan_only` is safe default; `synthetic_dry_run` writes synthetic non-biological rows.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = run_geneformer_perturbation_plausibility(
        output_dir=args.output_dir,
        mode=args.mode,
    )

    print("Stage 7 Geneformer-level perturbation plausibility scaffold")
    print(f"status: {summary['status']}")
    print(f"mode: {summary['mode']}")
    print(f"perturbation_plan: {summary['output_paths']['perturbation_plan']}")
    print(
        "perturbation_score_shift_schema: "
        f"{summary['output_paths']['perturbation_score_shift_schema']}"
    )
    print(f"run_summary: {summary['output_paths']['run_summary']}")
    print(f"report: {summary['output_paths']['readme']}")
    print(f"real_geneformer_perturbation_run: {summary['real_geneformer_perturbation_run']}")
    print(f"real_embeddings_recomputed: {summary['real_embeddings_recomputed']}")
    print(f"downstream_classifier_fixed: {summary['downstream_classifier_fixed']}")
    if summary.get("blocker"):
        print(f"blocker: {summary['blocker']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
