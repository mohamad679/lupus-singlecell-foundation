import csv
import json
import math

import pandas as pd

from lupusfm.evaluation.stage7_confounding_audit import (
    CLAIM_BOUNDARY,
    audit_cell_counts,
    audit_cell_type_composition,
    audit_source_batch_fields,
    build_patient_confounding_table,
    build_task_confounding_manifest,
    run_confounding_audit,
)


def synthetic_cell_metadata() -> pd.DataFrame:
    rows = []
    for patient_id, group, source, batch, counts in [
        ("FLARE001", "Flare", "site_a", "batch_1", {"B": 8, "T": 2}),
        ("FLARE002", "Flare", "site_a", "batch_1", {"B": 12, "T": 8}),
        ("MGD001", "Managed", "site_b", "batch_2", {"B": 1, "T": 4}),
        ("MGD002", "Managed", "site_b", "batch_2", {"B": 1, "T": 4}),
        ("HC001", "Healthy", "site_c", "batch_3", {"B": 2, "T": 8}),
        ("HC002", "Healthy", "site_c", "batch_3", {"B": 2, "T": 10}),
    ]:
        for cell_type, count in counts.items():
            for cell_index in range(count):
                rows.append(
                    {
                        "patient_id": patient_id,
                        "disease_group": group,
                        "cell_type": cell_type,
                        "source": source,
                        "batch": batch,
                        "cell_id": f"{patient_id}_{cell_type}_{cell_index}",
                    }
                )
    return pd.DataFrame(rows)


def test_synthetic_cell_metadata_builds_patient_level_confounding_manifest():
    build = build_patient_confounding_table(synthetic_cell_metadata())
    manifest = build_task_confounding_manifest(build.patient_table)

    assert list(build.patient_table["patient_id"]) == [
        "FLARE001",
        "FLARE002",
        "HC001",
        "HC002",
        "MGD001",
        "MGD002",
    ]
    assert build.availability.source_batch_fields_available is True
    assert set(build.source_columns) == {"source_field_source", "source_field_batch"}

    flare_row = build.patient_table.set_index("patient_id").loc["FLARE001"]
    assert flare_row["n_cells"] == 10
    assert math.isclose(flare_row["log1p_n_cells"], math.log1p(10))
    assert math.isclose(flare_row["cell_type_prop_b"], 0.8)
    assert math.isclose(flare_row["cell_type_prop_t"], 0.2)

    flare_vs_managed = manifest[manifest["task"] == "flare_vs_managed"].reset_index(drop=True)
    assert list(flare_vs_managed["label"]) == [1, 1, 0, 0]


def test_cell_count_audit_computes_class_summaries_and_smd():
    build = build_patient_confounding_table(synthetic_cell_metadata())
    manifest = build_task_confounding_manifest(build.patient_table)

    rows = audit_cell_counts(manifest)
    flare_vs_managed = next(row for row in rows if row["task"] == "flare_vs_managed")

    case_values = [math.log1p(10), math.log1p(20)]
    control_values = [math.log1p(5), math.log1p(5)]
    case_mean = sum(case_values) / 2
    control_mean = sum(control_values) / 2
    pooled_sd = math.sqrt(
        (((2 - 1) * ((case_values[0] - case_mean) ** 2 + (case_values[1] - case_mean) ** 2))
        + ((2 - 1) * 0.0))
        / (2 + 2 - 2)
    )
    expected_smd = (case_mean - control_mean) / pooled_sd

    assert flare_vs_managed["n_patients"] == 4
    assert flare_vs_managed["n_cases"] == 2
    assert flare_vs_managed["n_controls"] == 2
    assert math.isclose(flare_vs_managed["mean_n_cells_case"], 15.0)
    assert math.isclose(flare_vs_managed["mean_n_cells_control"], 5.0)
    assert math.isclose(flare_vs_managed["log1p_n_cells_smd"], expected_smd)
    assert flare_vs_managed["warning_flag"] == "strong"


def test_cell_type_composition_audit_computes_mean_proportion_differences():
    build = build_patient_confounding_table(synthetic_cell_metadata())
    manifest = build_task_confounding_manifest(build.patient_table)

    rows = audit_cell_type_composition(manifest, cell_type_columns=build.cell_type_columns)
    flare_b = next(
        row
        for row in rows
        if row["task"] == "flare_vs_managed" and row["cell_type_feature"] == "cell_type_prop_b"
    )

    assert math.isclose(flare_b["mean_prop_case"], 0.7)
    assert math.isclose(flare_b["mean_prop_control"], 0.2)
    assert math.isclose(flare_b["abs_mean_prop_diff"], 0.5)
    assert flare_b["warning_flag"] == "strong"


def test_source_batch_audit_detects_category_imbalance_conservatively():
    build = build_patient_confounding_table(synthetic_cell_metadata())
    manifest = build_task_confounding_manifest(build.patient_table)

    rows = audit_source_batch_fields(manifest, source_columns=build.source_columns)
    site_a = next(
        row
        for row in rows
        if row["task"] == "flare_vs_managed"
        and row["source_column"] == "source_field_source"
        and row["category"] == "site_a"
    )

    assert site_a["n_patients"] == 2
    assert site_a["n_cases"] == 2
    assert site_a["n_controls"] == 0
    assert site_a["present_in_only_one_class"] is True
    assert site_a["warning_flag"] == "strong"


def test_missing_metadata_artifact_writes_todo_outputs(tmp_path):
    output_dir = tmp_path / "confounding_report"
    missing_path = tmp_path / "missing_metadata.h5ad"

    payload = run_confounding_audit(
        metadata_artifact=missing_path,
        output_dir=output_dir,
    )

    assert payload["status"] == "blocked_missing_metadata_artifact"
    assert payload["real_audit_metrics_generated"] is False

    manifest_path = output_dir / "patient_confounding_manifest.csv"
    cell_count_path = output_dir / "cell_count_audit.csv"
    cell_type_path = output_dir / "cell_type_composition_audit.csv"
    source_path = output_dir / "source_batch_audit.csv"
    summary_csv_path = output_dir / "confounding_audit_summary.csv"
    summary_json_path = output_dir / "run_summary.json"
    readme_path = output_dir / "README.md"

    for path in (
        manifest_path,
        cell_count_path,
        cell_type_path,
        source_path,
        summary_csv_path,
        summary_json_path,
        readme_path,
    ):
        assert path.exists()

    with manifest_path.open(newline="", encoding="utf-8") as handle:
        assert list(csv.DictReader(handle)) == []
    with cell_count_path.open(newline="", encoding="utf-8") as handle:
        assert list(csv.DictReader(handle)) == []
    with cell_type_path.open(newline="", encoding="utf-8") as handle:
        assert list(csv.DictReader(handle)) == []
    with source_path.open(newline="", encoding="utf-8") as handle:
        assert list(csv.DictReader(handle)) == []
    with summary_csv_path.open(newline="", encoding="utf-8") as handle:
        assert list(csv.DictReader(handle)) == []

    saved = json.loads(summary_json_path.read_text(encoding="utf-8"))
    assert saved["status"] == "blocked_missing_metadata_artifact"
    assert saved["clinical_diagnostic_claim"] is False

    report = readme_path.read_text(encoding="utf-8")
    assert "TODO" in report
    assert CLAIM_BOUNDARY in report


def test_disallowed_embedding_columns_are_rejected():
    frame = synthetic_cell_metadata()
    frame["embedding_0"] = [0.1] * len(frame)

    try:
        build_patient_confounding_table(frame)
    except Exception as exc:  # pragma: no cover - exact type is the contract
        assert "Geneformer or expression features" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected confounding audit to reject embedding columns.")
