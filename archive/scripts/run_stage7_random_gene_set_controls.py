"""Run the Stage 7 random gene-set control scaffold."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from lupusfm.evaluation.stage7_random_gene_set_controls import (
    DEFAULT_MODE,
    DEFAULT_OUTPUT_DIR,
    SYNTHETIC_DRY_RUN_MODE,
    run_random_gene_set_controls,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a safe Stage 7 random gene-set control scaffold for future "
            "Geneformer-level perturbation analysis."
        )
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for plan, schema, summary JSON, and README outputs.",
    )
    parser.add_argument(
        "--mode",
        choices=[DEFAULT_MODE, SYNTHETIC_DRY_RUN_MODE],
        default=DEFAULT_MODE,
        help="`plan_only` is safe default; `synthetic_dry_run` writes synthetic toy rows only.",
    )
    parser.add_argument(
        "--synthetic-random-control-count",
        type=int,
        default=2,
        help="Number of toy random controls per target during synthetic dry-run mode.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = run_random_gene_set_controls(
        output_dir=args.output_dir,
        mode=args.mode,
        synthetic_random_control_count=args.synthetic_random_control_count,
    )

    print("Stage 7 random gene-set control scaffold")
    print(f"status: {summary['status']}")
    print(f"mode: {summary['mode']}")
    print(
        "random_gene_set_control_plan: "
        f"{summary['output_paths']['random_gene_set_control_plan']}"
    )
    print(
        "random_gene_set_control_schema: "
        f"{summary['output_paths']['random_gene_set_control_schema']}"
    )
    print(
        "random_gene_set_control_summary_schema: "
        f"{summary['output_paths']['random_gene_set_control_summary_schema']}"
    )
    print(f"run_summary: {summary['output_paths']['run_summary']}")
    print(f"report: {summary['output_paths']['readme']}")
    print(f"real_geneformer_perturbation_run: {summary['real_geneformer_perturbation_run']}")
    print(f"real_embeddings_recomputed: {summary['real_embeddings_recomputed']}")
    print(f"downstream_classifier_fixed: {summary['downstream_classifier_fixed']}")
    print(f"random_controls_are_real: {summary['random_controls_are_real']}")
    if summary.get("blocker"):
        print(f"blocker: {summary['blocker']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
