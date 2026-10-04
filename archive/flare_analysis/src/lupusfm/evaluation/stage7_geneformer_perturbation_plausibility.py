"""Stage 7 scaffold for Geneformer-level perturbation plausibility analysis."""

from __future__ import annotations

import json
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any, Mapping, Sequence

from lupusfm.embeddings.extraction import GeneformerExtractionCallbacks
from lupusfm.evaluation.stage7_metadata_baseline import REPO_ROOT, TASKS, render_report_path, write_csv


DEFAULT_OUTPUT_DIR = REPO_ROOT / "reports" / "post_stage7_geneformer_perturbation_plausibility"
DEFAULT_MODE = "plan_only"
SYNTHETIC_DRY_RUN_MODE = "synthetic_dry_run"

CLAIM_BOUNDARY = (
    "Geneformer-level perturbation plausibility analysis is hypothesis-generating only. "
    "It does not constitute external validation, clinical validation, causal validation, "
    "or evidence of clinical diagnostic utility."
)
INTERPRETATION_BOUNDARY = (
    "Upstream perturbation before embedding extraction only; fixed-classifier score-shift "
    "analysis only; does not constitute causal validation, clinical validation, or "
    "external validation."
)
SCOPE = "stage7_geneformer_level_perturbation_plausibility_scaffold"
DOWNSTREAM_CLASSIFIER_POLICY = (
    "fixed downstream classifier only; no refit during perturbation score-shift analysis"
)
REAL_EXECUTION_BLOCKER = (
    "No safe upstream Geneformer perturbation API is implemented in this repository. "
    "Real Geneformer-level perturbation must run in a controlled cloud/GPU environment "
    "that perturbs raw or tokenized gene input before embedding extraction, recomputes "
    "embeddings, and then applies the fixed downstream classifier without refitting."
)

PLAN_FIELDNAMES = [
    "perturbation_id",
    "perturbation_unit_type",
    "perturbation_name",
    "perturbation_action",
    "target_genes",
    "input_stage",
    "requires_geneformer_rerun",
    "requires_gpu_or_cloud",
    "downstream_classifier_policy",
    "expected_output",
    "interpretation_boundary",
    "status",
]
SCORE_SHIFT_FIELDNAMES = [
    "perturbation_id",
    "task",
    "patient_id",
    "true_group",
    "baseline_score",
    "perturbed_score",
    "score_shift",
    "abs_score_shift",
    "direction",
    "classifier_policy",
    "embedding_policy",
    "interpretation_boundary",
    "execution_status",
]


@dataclass(frozen=True)
class PerturbationRuntimeAvailability:
    safe_upstream_api_available: bool
    callback_fields: tuple[str, ...]
    blocker: str


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _require_supported_mode(mode: str) -> str:
    normalized = str(mode).strip().lower().replace("-", "_")
    if normalized not in {DEFAULT_MODE, SYNTHETIC_DRY_RUN_MODE}:
        raise ValueError(f"Unsupported mode: {mode}")
    return normalized


def detect_perturbation_runtime_availability() -> PerturbationRuntimeAvailability:
    callback_fields = tuple(field.name for field in fields(GeneformerExtractionCallbacks))
    safe_upstream_api_available = any("perturb" in field_name for field_name in callback_fields)
    blocker = "" if safe_upstream_api_available else REAL_EXECUTION_BLOCKER
    return PerturbationRuntimeAvailability(
        safe_upstream_api_available=safe_upstream_api_available,
        callback_fields=callback_fields,
        blocker=blocker,
    )


def build_perturbation_plan() -> list[dict[str, Any]]:
    base = {
        "input_stage": "upstream perturbation before embedding extraction",
        "requires_geneformer_rerun": True,
        "requires_gpu_or_cloud": True,
        "downstream_classifier_policy": DOWNSTREAM_CLASSIFIER_POLICY,
        "expected_output": "patient-level fixed-classifier score-shift analysis",
        "interpretation_boundary": INTERPRETATION_BOUNDARY,
    }
    return [
        {
            **base,
            "perturbation_id": "gp_gene_mask_placeholder",
            "perturbation_unit_type": "gene",
            "perturbation_name": "candidate_gene_placeholder",
            "perturbation_action": "mask",
            "target_genes": "TODO_define_candidate_gene",
            "status": "planned_blocked_pending_upstream_api",
        },
        {
            **base,
            "perturbation_id": "gp_gene_set_downweight_placeholder",
            "perturbation_unit_type": "gene_set",
            "perturbation_name": "candidate_gene_set_placeholder",
            "perturbation_action": "downweight",
            "target_genes": "TODO_define_gene_set_members",
            "status": "planned_blocked_pending_upstream_api",
        },
        {
            **base,
            "perturbation_id": "gp_gene_program_rank_placeholder",
            "perturbation_unit_type": "gene_program",
            "perturbation_name": "candidate_gene_program_placeholder",
            "perturbation_action": "remove_from_token_rank",
            "target_genes": "TODO_define_gene_program_members",
            "status": "planned_blocked_pending_upstream_api",
        },
        {
            **base,
            "perturbation_id": "gp_neutral_token_placeholder",
            "perturbation_unit_type": "gene",
            "perturbation_name": "neutral_token_placeholder_only",
            "perturbation_action": "replace_with_neutral_token",
            "target_genes": "TODO_define_placeholder_only",
            "status": "placeholder_only_no_repo_implementation",
        },
    ]


def build_score_shift_schema_rows(mode: str) -> list[dict[str, Any]]:
    if mode != SYNTHETIC_DRY_RUN_MODE:
        return []

    rows: list[dict[str, Any]] = []
    synthetic_rows = [
        ("gp_gene_mask_placeholder", "flare_vs_managed", "SYN001", "Flare", 0.82, 0.71),
        ("gp_gene_mask_placeholder", "flare_vs_managed", "SYN002", "Managed", 0.21, 0.27),
        ("gp_gene_set_downweight_placeholder", "flare_vs_healthy", "SYN003", "Flare", 0.88, 0.79),
        ("gp_gene_program_rank_placeholder", "flare_vs_healthy", "SYN004", "Healthy", 0.09, 0.15),
    ]
    for perturbation_id, task, patient_id, true_group, baseline, perturbed in synthetic_rows:
        shift = round(perturbed - baseline, 6)
        rows.append(
            {
                "perturbation_id": perturbation_id,
                "task": task,
                "patient_id": patient_id,
                "true_group": true_group,
                "baseline_score": baseline,
                "perturbed_score": perturbed,
                "score_shift": shift,
                "abs_score_shift": round(abs(shift), 6),
                "direction": "increase" if shift > 0 else "decrease" if shift < 0 else "no_change",
                "classifier_policy": DOWNSTREAM_CLASSIFIER_POLICY,
                "embedding_policy": (
                    "synthetic dry-run only; placeholder for recompute_embeddings_after_upstream_perturbation"
                ),
                "interpretation_boundary": (
                    f"SYNTHETIC ONLY. {INTERPRETATION_BOUNDARY}"
                ),
                "execution_status": "synthetic_dry_run_only_not_biological_result",
            }
        )
    return rows


def write_readme(
    path: Path,
    *,
    mode: str,
    output_dir: Path,
    runtime: PerturbationRuntimeAvailability,
    blocker: str,
    synthetic_rows_written: int,
) -> None:
    lines = [
        "# Stage 7 Geneformer-level perturbation plausibility scaffold",
        "",
        CLAIM_BOUNDARY,
        "",
        "This scaffold is for biological plausibility assessment only.",
        "This is not downstream LR/SHAP gene interpretation.",
        "Do not interpret downstream logistic regression coefficients as gene importance.",
        "Do not use SHAP on downstream embedding dimensions as gene-level interpretation.",
        "Perturbation must happen upstream before embedding extraction.",
        (
            "Correct execution path: raw/tokenized gene input -> gene/gene-program perturbation "
            "-> recompute Geneformer embeddings -> apply fixed downstream classifier -> compare "
            "prediction-score shifts."
        ),
        "Do not perform gene masking on the fixed patient-level embedding table.",
        "The downstream classifier must remain fixed.",
        "Score shifts are plausibility signals only.",
        "Real execution requires a Geneformer-capable environment and recomputation of embeddings.",
        "Synthetic dry-run outputs, if any, are not biological results.",
        "Geneformer-level perturbation does not constitute causal validation.",
        "Geneformer-level perturbation does not constitute clinical validation.",
        "Geneformer-level perturbation does not constitute external validation.",
        "",
        f"- Status: {mode}",
        f"- Output directory: `{render_report_path(output_dir)}`",
        f"- Upstream perturbation API available in repo: {str(runtime.safe_upstream_api_available).lower()}",
        f"- Extraction callback fields inspected: {', '.join(runtime.callback_fields)}",
        "- Downstream classifier policy: fixed downstream classifier only",
        "- Real Geneformer perturbation run: false",
        "- Real embeddings recomputed: false",
        f"- Synthetic score-shift rows written: {synthetic_rows_written}",
        "",
        "## TODO / Blocker",
        "",
        blocker,
        "",
        "## Output Notes",
        "",
        "- `perturbation_plan.csv` is a planning artifact only.",
        "- `perturbation_score_shift_schema.csv` is an empty schema in plan-only mode.",
        "- `perturbation_score_shift_schema.csv` contains synthetic placeholder rows in synthetic dry-run mode.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_geneformer_perturbation_plausibility(
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    mode: str = DEFAULT_MODE,
) -> dict[str, Any]:
    selected_mode = _require_supported_mode(mode)
    runtime = detect_perturbation_runtime_availability()
    blocker = runtime.blocker or REAL_EXECUTION_BLOCKER

    plan_rows = build_perturbation_plan()
    score_rows = build_score_shift_schema_rows(selected_mode)

    plan_path = output_dir / "perturbation_plan.csv"
    score_shift_path = output_dir / "perturbation_score_shift_schema.csv"
    summary_path = output_dir / "run_summary.json"
    readme_path = output_dir / "README.md"

    write_csv(plan_path, plan_rows, PLAN_FIELDNAMES)
    write_csv(score_shift_path, score_rows, SCORE_SHIFT_FIELDNAMES)
    write_readme(
        readme_path,
        mode=selected_mode,
        output_dir=output_dir,
        runtime=runtime,
        blocker=blocker,
        synthetic_rows_written=len(score_rows),
    )

    summary = {
        "status": (
            "completed_synthetic_dry_run"
            if selected_mode == SYNTHETIC_DRY_RUN_MODE
            else "plan_only_blocked_pending_cloud_geneformer_perturbation_api"
        ),
        "scope": SCOPE,
        "mode": selected_mode,
        "synthetic_output": selected_mode == SYNTHETIC_DRY_RUN_MODE,
        "tasks": [task["task"] for task in TASKS],
        "real_geneformer_perturbation_run": False,
        "real_embeddings_recomputed": False,
        "downstream_classifier_fixed": True,
        "external_validation_performed": False,
        "clinical_validation_performed": False,
        "clinical_diagnostic_claim": False,
        "causal_claim": False,
        "gene_level_claim": False,
        "perturbation_api_available": runtime.safe_upstream_api_available,
        "requires_gpu_or_cloud": True,
        "blocker": blocker,
        "claim_boundary": CLAIM_BOUNDARY,
        "output_paths": {
            "perturbation_plan": render_report_path(plan_path),
            "perturbation_score_shift_schema": render_report_path(score_shift_path),
            "run_summary": render_report_path(summary_path),
            "readme": render_report_path(readme_path),
        },
        "perturbation_plan_rows": len(plan_rows),
        "score_shift_rows": len(score_rows),
    }
    _write_json(summary_path, summary)
    return summary
