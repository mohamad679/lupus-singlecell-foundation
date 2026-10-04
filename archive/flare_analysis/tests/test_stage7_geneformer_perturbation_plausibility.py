import csv
import json

from lupusfm.evaluation.stage7_geneformer_perturbation_plausibility import (
    CLAIM_BOUNDARY,
    DEFAULT_MODE,
    PLAN_FIELDNAMES,
    REAL_EXECUTION_BLOCKER,
    SCORE_SHIFT_FIELDNAMES,
    SYNTHETIC_DRY_RUN_MODE,
    run_geneformer_perturbation_plausibility,
)


def test_default_plan_only_run_writes_expected_output_files(tmp_path):
    output_dir = tmp_path / "plausibility_report"

    summary = run_geneformer_perturbation_plausibility(output_dir=output_dir)

    assert summary["mode"] == DEFAULT_MODE
    assert summary["synthetic_output"] is False
    assert (output_dir / "perturbation_plan.csv").exists()
    assert (output_dir / "perturbation_score_shift_schema.csv").exists()
    assert (output_dir / "run_summary.json").exists()
    assert (output_dir / "README.md").exists()


def test_perturbation_plan_rows_require_geneformer_rerun_and_cloud_gpu(tmp_path):
    output_dir = tmp_path / "plausibility_report"
    run_geneformer_perturbation_plausibility(output_dir=output_dir)

    with (output_dir / "perturbation_plan.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert rows
    assert list(rows[0]) == PLAN_FIELDNAMES
    assert all(row["requires_geneformer_rerun"] == "True" for row in rows)
    assert all(row["requires_gpu_or_cloud"] == "True" for row in rows)
    assert all(
        row["input_stage"] == "upstream perturbation before embedding extraction" for row in rows
    )


def test_score_shift_schema_contains_expected_columns_and_boundary(tmp_path):
    output_dir = tmp_path / "plausibility_report"
    run_geneformer_perturbation_plausibility(output_dir=output_dir)

    with (output_dir / "perturbation_score_shift_schema.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == SCORE_SHIFT_FIELDNAMES
        rows = list(reader)

    assert rows == []
    assert "baseline_score" in SCORE_SHIFT_FIELDNAMES
    assert "perturbed_score" in SCORE_SHIFT_FIELDNAMES
    assert "score_shift" in SCORE_SHIFT_FIELDNAMES
    assert "interpretation_boundary" in SCORE_SHIFT_FIELDNAMES


def test_synthetic_dry_run_is_clearly_marked_synthetic(tmp_path):
    output_dir = tmp_path / "synthetic_report"

    summary = run_geneformer_perturbation_plausibility(
        output_dir=output_dir,
        mode=SYNTHETIC_DRY_RUN_MODE,
    )

    assert summary["synthetic_output"] is True
    assert summary["real_geneformer_perturbation_run"] is False

    with (output_dir / "perturbation_score_shift_schema.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))

    assert rows
    assert all("SYNTHETIC ONLY." in row["interpretation_boundary"] for row in rows)
    assert all(
        row["execution_status"] == "synthetic_dry_run_only_not_biological_result"
        for row in rows
    )


def test_summary_sets_required_false_claim_flags(tmp_path):
    output_dir = tmp_path / "plausibility_report"
    run_geneformer_perturbation_plausibility(output_dir=output_dir)

    saved = json.loads((output_dir / "run_summary.json").read_text(encoding="utf-8"))

    assert saved["real_geneformer_perturbation_run"] is False
    assert saved["real_embeddings_recomputed"] is False
    assert saved["downstream_classifier_fixed"] is True
    assert saved["external_validation_performed"] is False
    assert saved["clinical_validation_performed"] is False
    assert saved["clinical_diagnostic_claim"] is False
    assert saved["causal_claim"] is False
    assert saved["gene_level_claim"] is False
    assert saved["claim_boundary"] == CLAIM_BOUNDARY
    assert saved["blocker"] == REAL_EXECUTION_BLOCKER


def test_forbidden_phrases_are_not_present_in_readme_or_summary(tmp_path):
    output_dir = tmp_path / "plausibility_report"
    run_geneformer_perturbation_plausibility(output_dir=output_dir)

    readme = (output_dir / "README.md").read_text(encoding="utf-8").lower()
    summary = (output_dir / "run_summary.json").read_text(encoding="utf-8").lower()
    combined = "\n".join([readme, summary])

    for phrase in (
        "causal gene importance",
        "clinically validated",
        "diagnostic gene signature",
        "validated mechanism",
    ):
        assert phrase not in combined
