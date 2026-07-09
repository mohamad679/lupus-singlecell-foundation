import csv
import json

import pandas as pd

from lupusfm.evaluation.stage7_metadata_baseline import (
    CLAIM_BOUNDARY,
    build_patient_metadata_feature_table,
    build_task_feature_manifest,
    run_metadata_baseline,
    run_task_loocv_baseline,
)


def synthetic_cell_metadata() -> pd.DataFrame:
    rows = []
    for patient_id, group, age, sex, counts in [
        ("FLARE001", "Flare", 42, "F", {"B": 6, "T": 2}),
        ("FLARE002", "Flare", 39, "F", {"B": 5, "T": 3}),
        ("MGD001", "Managed", 45, "M", {"B": 1, "T": 7}),
        ("MGD002", "Managed", 47, "M", {"B": 2, "T": 6}),
        ("HC001", "Healthy", 31, "Unknown", {"B": 1, "T": 7}),
        ("HC002", "Healthy", 29, "F", {"B": 2, "T": 6}),
    ]:
        for cell_type, count in counts.items():
            for cell_index in range(count):
                rows.append(
                    {
                        "patient_id": patient_id,
                        "disease_group": group,
                        "age": age,
                        "sex": sex,
                        "cell_type": cell_type,
                        "cell_id": f"{patient_id}_{cell_type}_{cell_index}",
                    }
                )
    return pd.DataFrame(rows)


def test_build_patient_metadata_feature_table_aggregates_patient_level_features():
    patient_table, availability = build_patient_metadata_feature_table(
        synthetic_cell_metadata()
    )

    assert list(patient_table["patient_id"]) == [
        "FLARE001",
        "FLARE002",
        "HC001",
        "HC002",
        "MGD001",
        "MGD002",
    ]
    assert availability.age_available is True
    assert availability.sex_available is True
    assert availability.cell_type_available is True

    flare001 = patient_table.set_index("patient_id").loc["FLARE001"]
    assert flare001["n_cells"] == 8
    assert flare001["cell_type_prop_b"] == 0.75
    assert flare001["cell_type_prop_t"] == 0.25


def test_loocv_predictions_hold_out_each_patient_once():
    patient_table, _availability = build_patient_metadata_feature_table(
        synthetic_cell_metadata()
    )
    manifest = build_task_feature_manifest(patient_table)
    task_table = manifest[manifest["task"] == "flare_vs_managed"].reset_index(drop=True)

    prediction_rows, metrics, _debug = run_task_loocv_baseline(
        task_table,
        task="flare_vs_managed",
        return_debug=True,
    )

    assert len(prediction_rows) == len(task_table)
    assert sorted(row["patient_id"] for row in prediction_rows) == sorted(
        task_table["patient_id"].tolist()
    )
    assert all(row["n_train"] == len(task_table) - 1 for row in prediction_rows)
    assert metrics["n_patients"] == len(task_table)


def test_preprocessing_is_fit_inside_each_train_fold_only():
    patient_table, _availability = build_patient_metadata_feature_table(
        synthetic_cell_metadata()
    )
    manifest = build_task_feature_manifest(patient_table)
    task_table = manifest[manifest["task"] == "flare_vs_healthy"].reset_index(drop=True)

    _rows, _metrics, debug_rows = run_task_loocv_baseline(
        task_table,
        task="flare_vs_healthy",
        return_debug=True,
    )

    held_out_unknown = next(row for row in debug_rows if row.test_patient_id == "HC001")
    assert "Unknown" not in held_out_unknown.one_hot_categories["sex"]

    held_out_flare = next(row for row in debug_rows if row.test_patient_id == "FLARE001")
    assert held_out_flare.numeric_imputer_statistics["age"] == 31.0


def test_geneformer_embedding_columns_are_rejected():
    patient_table, _availability = build_patient_metadata_feature_table(
        synthetic_cell_metadata()
    )
    patient_table["embedding_0"] = [0.1] * len(patient_table)

    try:
        build_task_feature_manifest(patient_table)
    except Exception as exc:  # pragma: no cover - exact type is the contract
        assert "Geneformer or expression features" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected metadata baseline to reject embedding columns.")


def test_missing_metadata_artifact_writes_todo_outputs(tmp_path):
    output_dir = tmp_path / "metadata_report"
    missing_path = tmp_path / "missing_metadata.h5ad"

    payload = run_metadata_baseline(
        metadata_artifact=missing_path,
        output_dir=output_dir,
    )

    assert payload["status"] == "blocked_missing_metadata_artifact"
    assert payload["geneformer_run"] is False
    assert payload["geneformer_embeddings_used"] is False

    feature_path = output_dir / "metadata_feature_manifest.csv"
    prediction_path = output_dir / "metadata_baseline_predictions.csv"
    metrics_path = output_dir / "metadata_baseline_metrics.csv"
    summary_path = output_dir / "run_summary.json"
    readme_path = output_dir / "README.md"

    assert feature_path.exists()
    assert prediction_path.exists()
    assert metrics_path.exists()
    assert summary_path.exists()
    assert readme_path.exists()

    with feature_path.open(newline="", encoding="utf-8") as handle:
        assert list(csv.DictReader(handle)) == []
    with prediction_path.open(newline="", encoding="utf-8") as handle:
        assert list(csv.DictReader(handle)) == []
    with metrics_path.open(newline="", encoding="utf-8") as handle:
        assert list(csv.DictReader(handle)) == []

    saved = json.loads(summary_path.read_text(encoding="utf-8"))
    assert saved["status"] == "blocked_missing_metadata_artifact"
    assert saved["clinical_diagnostic_claim"] is False

    report = readme_path.read_text(encoding="utf-8")
    assert "TODO" in report
    assert CLAIM_BOUNDARY in report
