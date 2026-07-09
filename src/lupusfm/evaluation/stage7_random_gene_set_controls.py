"""Stage 7 random gene-set control scaffold for Geneformer perturbation planning."""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any, Mapping, Sequence

from lupusfm.evaluation.stage7_geneformer_perturbation_plausibility import (
    REAL_EXECUTION_BLOCKER,
    detect_perturbation_runtime_availability,
)
from lupusfm.evaluation.stage7_metadata_baseline import REPO_ROOT, TASKS, render_report_path, write_csv


DEFAULT_OUTPUT_DIR = REPO_ROOT / "reports" / "post_stage7_random_gene_set_controls"
DEFAULT_MODE = "plan_only"
SYNTHETIC_DRY_RUN_MODE = "synthetic_dry_run"
DEFAULT_RANDOM_CONTROL_COUNT = 100
DEFAULT_RANDOM_SEED = 42
DEFAULT_SYNTHETIC_RANDOM_CONTROL_COUNT = 2

CLAIM_BOUNDARY = (
    "Random gene-set controls for Geneformer-level perturbation are hypothesis-generating "
    "controls only. They do not constitute causal validation, external validation, clinical "
    "validation, or evidence of clinical diagnostic utility."
)
INTERPRETATION_BOUNDARY = (
    "Size-matched random gene-set controls are a hypothesis-generating control for future "
    "fixed-classifier score-shift analysis only; they are an empirical null comparison, "
    "require upstream Geneformer-level perturbation, and are not biological validation."
)
DOWNSTREAM_CLASSIFIER_POLICY = "fixed downstream classifier only; no refit"
GENE_UNIVERSE_POLICY = "TODO_define_geneformer_token_gene_universe"
MATCHING_POLICY = "size_matched_only_pending_gene_universe"
SCOPE = "stage7_random_gene_set_controls_scaffold"
GENE_UNIVERSE_BLOCKER = (
    "TODO: define the Geneformer token gene universe and any token-availability filters before "
    "sampling real size-matched random gene-set controls."
)
CONTROL_BLOCKER = (
    f"{GENE_UNIVERSE_BLOCKER} {REAL_EXECUTION_BLOCKER}"
)

CONTROL_PLAN_FIELDNAMES = [
    "control_plan_id",
    "target_perturbation_id",
    "target_gene_set_name",
    "target_gene_count",
    "random_control_count",
    "random_seed",
    "matching_policy",
    "gene_universe_policy",
    "exclude_target_genes",
    "requires_geneformer_rerun",
    "requires_gpu_or_cloud",
    "downstream_classifier_policy",
    "expected_output",
    "interpretation_boundary",
    "status",
]
RANDOM_CONTROL_SCHEMA_FIELDNAMES = [
    "control_plan_id",
    "random_control_id",
    "target_perturbation_id",
    "target_gene_set_name",
    "random_gene_set_name",
    "target_gene_count",
    "random_gene_count",
    "random_seed",
    "sampled_genes",
    "matching_policy",
    "gene_universe_policy",
    "synthetic_output",
    "execution_status",
    "interpretation_boundary",
]
SUMMARY_SCHEMA_FIELDNAMES = [
    "target_perturbation_id",
    "task",
    "target_gene_set_name",
    "target_score_shift_mean",
    "random_score_shift_mean",
    "random_score_shift_sd",
    "empirical_p_value",
    "n_random_controls",
    "classifier_policy",
    "embedding_policy",
    "interpretation_boundary",
    "execution_status",
]

TARGET_GENE_SETS: tuple[dict[str, Any], ...] = (
    {
        "control_plan_id": "rgsc_plan_001",
        "target_perturbation_id": "gp_gene_mask_placeholder",
        "target_gene_set_name": "placeholder_mask_target_genes",
        "target_genes": ("TOY_GENE_001", "TOY_GENE_002", "TOY_GENE_003"),
    },
    {
        "control_plan_id": "rgsc_plan_002",
        "target_perturbation_id": "gp_gene_set_downweight_placeholder",
        "target_gene_set_name": "placeholder_downweight_target_genes",
        "target_genes": ("TOY_GENE_011", "TOY_GENE_012", "TOY_GENE_013", "TOY_GENE_014"),
    },
    {
        "control_plan_id": "rgsc_plan_003",
        "target_perturbation_id": "gp_gene_program_rank_placeholder",
        "target_gene_set_name": "placeholder_rank_target_genes",
        "target_genes": (
            "TOY_GENE_021",
            "TOY_GENE_022",
            "TOY_GENE_023",
            "TOY_GENE_024",
            "TOY_GENE_025",
        ),
    },
)
SYNTHETIC_GENE_UNIVERSE = tuple(f"TOY_GENE_{index:03d}" for index in range(1, 41))


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _require_supported_mode(mode: str) -> str:
    normalized = str(mode).strip().lower().replace("-", "_")
    if normalized not in {DEFAULT_MODE, SYNTHETIC_DRY_RUN_MODE}:
        raise ValueError(f"Unsupported mode: {mode}")
    return normalized


def build_random_gene_set_control_plan() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for spec in TARGET_GENE_SETS:
        rows.append(
            {
                "control_plan_id": spec["control_plan_id"],
                "target_perturbation_id": spec["target_perturbation_id"],
                "target_gene_set_name": spec["target_gene_set_name"],
                "target_gene_count": len(spec["target_genes"]),
                "random_control_count": DEFAULT_RANDOM_CONTROL_COUNT,
                "random_seed": DEFAULT_RANDOM_SEED,
                "matching_policy": MATCHING_POLICY,
                "gene_universe_policy": GENE_UNIVERSE_POLICY,
                "exclude_target_genes": True,
                "requires_geneformer_rerun": True,
                "requires_gpu_or_cloud": True,
                "downstream_classifier_policy": DOWNSTREAM_CLASSIFIER_POLICY,
                "expected_output": (
                    "future fixed-classifier score-shift analysis against an empirical null "
                    "comparison after upstream Geneformer-level perturbation"
                ),
                "interpretation_boundary": INTERPRETATION_BOUNDARY,
                "status": "planned_blocked_pending_gene_universe_and_upstream_api",
            }
        )
    return rows


def sample_synthetic_random_gene_sets(
    *,
    plan_rows: Sequence[Mapping[str, Any]],
    gene_universe: Sequence[str] = SYNTHETIC_GENE_UNIVERSE,
    synthetic_random_control_count: int = DEFAULT_SYNTHETIC_RANDOM_CONTROL_COUNT,
) -> list[dict[str, Any]]:
    if synthetic_random_control_count < 1:
        raise ValueError("synthetic_random_control_count must be at least 1.")

    target_lookup = {
        str(spec["control_plan_id"]): tuple(str(gene) for gene in spec["target_genes"])
        for spec in TARGET_GENE_SETS
    }
    universe = tuple(sorted({str(gene) for gene in gene_universe}))
    rows: list[dict[str, Any]] = []

    for plan_index, plan_row in enumerate(plan_rows):
        control_plan_id = str(plan_row["control_plan_id"])
        target_genes = target_lookup[control_plan_id]
        target_gene_set = set(target_genes)
        target_gene_count = int(plan_row["target_gene_count"])
        exclude_target_genes = str(plan_row["exclude_target_genes"]).lower() == "true"

        available_genes = tuple(
            gene for gene in universe if (gene not in target_gene_set or not exclude_target_genes)
        )
        if len(available_genes) < target_gene_count:
            raise ValueError(
                f"Toy universe is too small for {control_plan_id}: "
                f"need {target_gene_count}, found {len(available_genes)}."
            )

        base_seed = int(plan_row["random_seed"]) + (plan_index * 1000)
        for control_index in range(1, synthetic_random_control_count + 1):
            rng = random.Random(base_seed + control_index)
            sampled_genes = tuple(sorted(rng.sample(list(available_genes), target_gene_count)))
            rows.append(
                {
                    "control_plan_id": control_plan_id,
                    "random_control_id": f"{control_plan_id}_synthetic_{control_index:03d}",
                    "target_perturbation_id": plan_row["target_perturbation_id"],
                    "target_gene_set_name": plan_row["target_gene_set_name"],
                    "random_gene_set_name": f"synthetic_random_control_{control_index:03d}",
                    "target_gene_count": target_gene_count,
                    "random_gene_count": len(sampled_genes),
                    "random_seed": base_seed + control_index,
                    "sampled_genes": "|".join(sampled_genes),
                    "matching_policy": "size_matched_only_toy_gene_universe",
                    "gene_universe_policy": "synthetic_toy_gene_universe",
                    "synthetic_output": True,
                    "execution_status": "synthetic_dry_run_only_not_biological_result",
                    "interpretation_boundary": f"SYNTHETIC ONLY. {INTERPRETATION_BOUNDARY}",
                }
            )

    return rows


def write_random_gene_set_control_outputs(
    *,
    output_dir: Path,
    plan_rows: Sequence[Mapping[str, Any]],
    random_control_rows: Sequence[Mapping[str, Any]],
    summary_rows: Sequence[Mapping[str, Any]],
    mode: str,
    blocker: str,
) -> dict[str, str]:
    plan_path = output_dir / "random_gene_set_control_plan.csv"
    schema_path = output_dir / "random_gene_set_control_schema.csv"
    summary_schema_path = output_dir / "random_gene_set_control_summary_schema.csv"
    run_summary_path = output_dir / "run_summary.json"
    readme_path = output_dir / "README.md"

    write_csv(plan_path, plan_rows, CONTROL_PLAN_FIELDNAMES)
    write_csv(schema_path, random_control_rows, RANDOM_CONTROL_SCHEMA_FIELDNAMES)
    write_csv(summary_schema_path, summary_rows, SUMMARY_SCHEMA_FIELDNAMES)

    runtime = detect_perturbation_runtime_availability()
    readme_lines = [
        "# Stage 7 random gene-set controls",
        "",
        CLAIM_BOUNDARY,
        "",
        "This scaffold prepares size-matched random gene-set controls for a future empirical null comparison.",
        "It is a hypothesis-generating control only.",
        "Upstream Geneformer-level perturbation required before any score-shift analysis.",
        "The downstream classifier must remain fixed; no refit is allowed.",
        "Do not perturb fixed patient-level embeddings.",
        "Do not interpret downstream LR coefficients as gene importance.",
        "Do not use SHAP on embedding dimensions as gene-level interpretation.",
        "Synthetic dry-run rows, if present, are synthetic output only and not biological results.",
        "No causal validation, clinical validation, or external validation is performed here.",
        "",
        f"- Status: {mode}",
        f"- Output directory: `{render_report_path(output_dir)}`",
        f"- Upstream perturbation API available in repo: {str(runtime.safe_upstream_api_available).lower()}",
        f"- Extraction callback fields inspected: {', '.join(runtime.callback_fields)}",
        "- Real Geneformer perturbation run: false",
        "- Real embeddings recomputed: false",
        "- Downstream classifier fixed: true",
        f"- Synthetic random control rows written: {len(random_control_rows)}",
        "",
        "## TODO / Blocker",
        "",
        blocker,
        "",
        "## Output Notes",
        "",
        "- `random_gene_set_control_plan.csv` is a planning artifact only.",
        "- `random_gene_set_control_schema.csv` is header-only in plan-only mode.",
        "- `random_gene_set_control_schema.csv` contains toy deterministic controls in synthetic dry-run mode.",
        "- `random_gene_set_control_summary_schema.csv` is a schema only; no real score-shift metrics are written.",
    ]
    readme_path.parent.mkdir(parents=True, exist_ok=True)
    readme_path.write_text("\n".join(readme_lines) + "\n", encoding="utf-8")

    return {
        "random_gene_set_control_plan": render_report_path(plan_path),
        "random_gene_set_control_schema": render_report_path(schema_path),
        "random_gene_set_control_summary_schema": render_report_path(summary_schema_path),
        "run_summary": render_report_path(run_summary_path),
        "readme": render_report_path(readme_path),
    }


def run_random_gene_set_controls(
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    mode: str = DEFAULT_MODE,
    synthetic_random_control_count: int = DEFAULT_SYNTHETIC_RANDOM_CONTROL_COUNT,
) -> dict[str, Any]:
    selected_mode = _require_supported_mode(mode)
    plan_rows = build_random_gene_set_control_plan()
    random_control_rows = (
        sample_synthetic_random_gene_sets(
            plan_rows=plan_rows,
            synthetic_random_control_count=synthetic_random_control_count,
        )
        if selected_mode == SYNTHETIC_DRY_RUN_MODE
        else []
    )
    summary_rows: list[dict[str, Any]] = []
    output_paths = write_random_gene_set_control_outputs(
        output_dir=output_dir,
        plan_rows=plan_rows,
        random_control_rows=random_control_rows,
        summary_rows=summary_rows,
        mode=selected_mode,
        blocker=CONTROL_BLOCKER,
    )

    summary = {
        "status": (
            "completed_synthetic_dry_run"
            if selected_mode == SYNTHETIC_DRY_RUN_MODE
            else "plan_only_blocked_pending_gene_universe_and_upstream_api"
        ),
        "scope": SCOPE,
        "mode": selected_mode,
        "synthetic_output": selected_mode == SYNTHETIC_DRY_RUN_MODE,
        "tasks": [task["task"] for task in TASKS],
        "real_geneformer_perturbation_run": False,
        "real_embeddings_recomputed": False,
        "downstream_classifier_fixed": True,
        "causal_claim": False,
        "clinical_validation_performed": False,
        "external_validation_performed": False,
        "clinical_diagnostic_claim": False,
        "requires_geneformer_rerun": True,
        "requires_gpu_or_cloud": True,
        "random_controls_are_real": False,
        "gene_universe_defined": False,
        "blocker": CONTROL_BLOCKER,
        "claim_boundary": CLAIM_BOUNDARY,
        "output_paths": output_paths,
        "control_plan_rows": len(plan_rows),
        "random_control_schema_rows": len(random_control_rows),
        "summary_schema_rows": len(summary_rows),
    }
    _write_json(output_dir / "run_summary.json", summary)
    return summary
