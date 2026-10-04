"""Run the Stage 7 patient-label permutation negative control."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from lupusfm.evaluation.stage7_permutation_test import (
    DEFAULT_OUTPUT_DIR,
    default_embedding_dir,
    run_permutation_test,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run an internal Stage 7 patient-level label permutation negative "
            "control without running Geneformer or re-extracting embeddings."
        )
    )
    parser.add_argument(
        "--emb-dir",
        type=Path,
        default=None,
        help=(
            "Directory containing existing patient embedding .npy files. "
            "Defaults to the recorded Stage 7 run-summary path when present."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for permutation CSV, JSON, and Markdown outputs.",
    )
    parser.add_argument("--n-permutations", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--c-value", type=float, default=0.1)
    parser.add_argument("--max-iter", type=int, default=1000)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    emb_dir = args.emb_dir or default_embedding_dir()
    summary = run_permutation_test(
        emb_dir=emb_dir,
        output_dir=args.output_dir,
        n_permutations=args.n_permutations,
        seed=args.seed,
        c_value=args.c_value,
        max_iter=args.max_iter,
    )

    print("Stage 7 permutation-label negative control")
    print(f"status: {summary['status']}")
    print(f"embedding_dir: {summary['embedding_dir']}")
    print(f"permutation_results: {summary['permutation_results']}")
    print(f"permutation_summary: {summary['permutation_summary']}")
    print(f"run_summary: {args.output_dir / 'run_summary.json'}")
    print(f"report: {summary['report']}")
    if summary["status"] != "completed":
        print(f"blocker: {summary.get('blocker', '')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
