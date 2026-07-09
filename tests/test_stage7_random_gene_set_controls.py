import csv
import json

from lupusfm.evaluation.stage7_random_gene_set_controls import (
    CLAIM_BOUNDARY,
    CONTROL_PLAN_FIELDNAMES,
    RANDOM_CONTROL_SCHEMA_FIELDNAMES,
    SUMMARY_SCHEMA_FIELDNAMES,
    SYNTHETIC_GENE_UNIVERSE,
    SYNTHETIC_DRY_RUN_MODE,
    build_random_gene_set_control_plan,
    run_random_gene_set_controls,
    sample_synthetic_random_gene_sets,
)


def test_default_plan_only_run_writes_expected_output_files(tmp_path):
    output_dir = tmp_path / "random_control_report"

    summary = run_random_gene_set_controls(output_dir=output_dir)

    assert summary["mode"] == "plan_only"
    assert summary["synthetic_output"] is False
    assert (output_dir / "random_gene_set_control_plan.csv").exists()
    assert (output_dir / "random_gene_set_control_schema.csv").exists()
    assert (output_dir / "random_gene_set_control_summary_schema.csv").exists()
    assert (output_dir / "run_summary.json").exists()
    assert (output_dir / "README.md").exists()


def test_plan_rows_require_geneformer_rerun_and_cloud_gpu(tmp_path):
    output_dir = tmp_path / "random_control_report"
    run_random_gene_set_controls(output_dir=output_dir)

    with (output_dir / "random_gene_set_control_plan.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))

    assert rows
    assert list(rows[0]) == CONTROL_PLAN_FIELDNAMES
    assert all(row["requires_geneformer_rerun"] == "True" for row in rows)
    assert all(row["requires_gpu_or_cloud"] == "True" for row in rows)
    assert all(
        row["status"] == "planned_blocked_pending_gene_universe_and_upstream_api" for row in rows
    )


def test_plan_rows_use_deterministic_seed_and_random_control_count(tmp_path):
    output_dir = tmp_path / "random_control_report"
    run_random_gene_set_controls(output_dir=output_dir)

    with (output_dir / "random_gene_set_control_plan.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))

    assert all(row["random_seed"] == "42" for row in rows)
    assert all(row["random_control_count"] == "100" for row in rows)
    assert all(row["exclude_target_genes"] == "True" for row in rows)


def test_schema_contains_expected_columns_and_boundary(tmp_path):
    output_dir = tmp_path / "random_control_report"
    run_random_gene_set_controls(output_dir=output_dir)

    with (output_dir / "random_gene_set_control_schema.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == RANDOM_CONTROL_SCHEMA_FIELDNAMES
        rows = list(reader)

    with (output_dir / "random_gene_set_control_summary_schema.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        summary_reader = csv.DictReader(handle)
        assert summary_reader.fieldnames == SUMMARY_SCHEMA_FIELDNAMES
        summary_rows = list(summary_reader)

    assert rows == []
    assert summary_rows == []
    assert "sampled_genes" in RANDOM_CONTROL_SCHEMA_FIELDNAMES
    assert "synthetic_output" in RANDOM_CONTROL_SCHEMA_FIELDNAMES
    assert "interpretation_boundary" in RANDOM_CONTROL_SCHEMA_FIELDNAMES


def test_synthetic_dry_run_samples_deterministic_size_matched_random_gene_sets():
    plan_rows = build_random_gene_set_control_plan()

    first = sample_synthetic_random_gene_sets(
        plan_rows=plan_rows,
        gene_universe=SYNTHETIC_GENE_UNIVERSE,
        synthetic_random_control_count=2,
    )
    second = sample_synthetic_random_gene_sets(
        plan_rows=plan_rows,
        gene_universe=SYNTHETIC_GENE_UNIVERSE,
        synthetic_random_control_count=2,
    )

    assert first == second
    assert len(first) == 6
    assert all(row["synthetic_output"] is True for row in first)
    assert all(
        len(row["sampled_genes"].split("|")) == int(row["target_gene_count"]) for row in first
    )
    assert all(
        row["execution_status"] == "synthetic_dry_run_only_not_biological_result"
        for row in first
    )


def test_synthetic_dry_run_excludes_target_genes_when_requested():
    plan_rows = build_random_gene_set_control_plan()
    rows = sample_synthetic_random_gene_sets(
        plan_rows=plan_rows,
        gene_universe=SYNTHETIC_GENE_UNIVERSE,
        synthetic_random_control_count=2,
    )

    target_lookup = {
        row["control_plan_id"]: {
            "placeholder_mask_target_genes": {"TOY_GENE_001", "TOY_GENE_002", "TOY_GENE_003"},
            "placeholder_downweight_target_genes": {
                "TOY_GENE_011",
                "TOY_GENE_012",
                "TOY_GENE_013",
                "TOY_GENE_014",
            },
            "placeholder_rank_target_genes": {
                "TOY_GENE_021",
                "TOY_GENE_022",
                "TOY_GENE_023",
                "TOY_GENE_024",
                "TOY_GENE_025",
            },
        }[row["target_gene_set_name"]]
        for row in plan_rows
    }

    for row in rows:
        sampled = set(row["sampled_genes"].split("|"))
        assert sampled.isdisjoint(target_lookup[row["control_plan_id"]])


def test_summary_sets_required_false_claim_flags(tmp_path):
    output_dir = tmp_path / "random_control_report"
    run_random_gene_set_controls(output_dir=output_dir)

    saved = json.loads((output_dir / "run_summary.json").read_text(encoding="utf-8"))

    assert saved["real_geneformer_perturbation_run"] is False
    assert saved["real_embeddings_recomputed"] is False
    assert saved["downstream_classifier_fixed"] is True
    assert saved["causal_claim"] is False
    assert saved["clinical_validation_performed"] is False
    assert saved["external_validation_performed"] is False
    assert saved["clinical_diagnostic_claim"] is False
    assert saved["claim_boundary"] == CLAIM_BOUNDARY


def test_forbidden_phrases_are_not_present_in_readme_or_summary(tmp_path):
    output_dir = tmp_path / "random_control_report"
    run_random_gene_set_controls(output_dir=output_dir, mode=SYNTHETIC_DRY_RUN_MODE)

    readme = (output_dir / "README.md").read_text(encoding="utf-8").lower()
    summary = (output_dir / "run_summary.json").read_text(encoding="utf-8").lower()
    combined = "\n".join([readme, summary])

    for phrase in (
        "validated gene program",
        "causal gene-set importance",
        "clinically validated",
        "diagnostic gene signature",
        "confirmed biomarker",
        "proves mechanism",
    ):
        assert phrase not in combined
