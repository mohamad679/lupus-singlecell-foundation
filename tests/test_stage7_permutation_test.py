import csv
import json

import numpy as np

from lupusfm.evaluation.stage7_permutation_test import (
    CLAIM_BOUNDARY,
    run_permutation_test,
    run_task_permutation_control,
    summarize_permutations,
)


def test_summarize_permutations_uses_conservative_one_sided_p_value():
    summary = summarize_permutations(
        task="flare_vs_managed",
        observed_auroc=0.8,
        permutation_aurocs=[0.1, 0.8, 0.9],
        n_permutations=3,
        seed=42,
    )

    assert summary["empirical_p_value"] == 3 / 4
    assert summary["n_valid_permutations"] == 3
    assert summary["claim_boundary"] == CLAIM_BOUNDARY


def test_task_permutation_control_shuffles_patient_labels_not_patient_identity():
    X = np.array(
        [
            [-3.0, -3.0],
            [-2.7, -2.5],
            [-2.4, -2.8],
            [2.4, 2.7],
            [2.8, 2.5],
            [3.0, 3.2],
        ]
    )
    y = np.array([0, 0, 0, 1, 1, 1])
    patient_ids = [f"P{i}" for i in range(6)]

    rows, summary = run_task_permutation_control(
        task="flare_vs_healthy",
        X=X,
        y=y,
        patient_ids=patient_ids,
        observed_auroc=1.0,
        n_permutations=3,
        seed=7,
        max_iter=200,
    )

    assert len(rows) == 3
    assert summary["n_valid_permutations"] == 3
    assert summary["observed_auroc_internal_loocv"] == 1.0
    assert all(row["label_shuffle_unit"] == "patient" for row in rows)
    assert all(row["patient_identity_preserved"] is True for row in rows)
    assert all(row["n_cases"] == 3 for row in rows)
    assert all(row["n_controls"] == 3 for row in rows)
    assert all(row["scaler_fit_scope"] == "train_fold_only" for row in rows)
    assert all(row["model_fit_scope"] == "train_fold_only" for row in rows)


def test_missing_embedding_artifact_writes_todo_outputs(tmp_path):
    output_dir = tmp_path / "permutation_report"
    missing_dir = tmp_path / "missing_embeddings"

    payload = run_permutation_test(
        emb_dir=missing_dir,
        output_dir=output_dir,
        n_permutations=2,
        seed=42,
    )

    assert payload["status"] == "blocked_missing_embedding_artifact"
    assert payload["external_validation_performed"] is False
    assert payload["clinical_validation_performed"] is False
    assert payload["clinical_diagnostic_claim"] is False

    permutation_path = output_dir / "permutation_results.csv"
    summary_path = output_dir / "permutation_summary.csv"
    json_path = output_dir / "run_summary.json"
    readme_path = output_dir / "README.md"

    assert permutation_path.exists()
    assert summary_path.exists()
    assert json_path.exists()
    assert readme_path.exists()

    with permutation_path.open(newline="", encoding="utf-8") as handle:
        assert list(csv.DictReader(handle)) == []
    with summary_path.open(newline="", encoding="utf-8") as handle:
        assert list(csv.DictReader(handle)) == []

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    assert saved["status"] == "blocked_missing_embedding_artifact"
    assert saved["geneformer_run"] is False
    assert saved["embeddings_reextracted"] is False

    report = readme_path.read_text(encoding="utf-8")
    assert "TODO" in report
    assert CLAIM_BOUNDARY in report
    assert "Internal negative-control only." in report
