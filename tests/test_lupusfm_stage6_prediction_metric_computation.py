import pytest

from lupusfm.evaluation.stage6_controlled_baseline_execution import (
    DonorFeatureRecord,
    fit_controlled_centroid_baseline,
)
from lupusfm.evaluation.stage6_prediction_metric_computation import (
    DEFERRED_F007_ACTIONS,
    METRIC_NAMES,
    REQUIRED_F006_CONTRACTS,
    REQUIRED_UPSTREAM_GATES,
    BinaryMetricSummary,
    DonorPredictionRecord,
    Stage6PredictionMetricComputationError,
    Stage6PredictionMetricComputationGate,
    compute_binary_metrics,
    compute_stage6_prediction_metrics,
    predict_with_f005_centroid_baseline,
    prediction_metric_computation_result_to_dict,
    stage6_prediction_metric_computation_gate_from_mapping,
    stage6_prediction_metric_computation_gate_to_dict,
    stage6_prediction_metric_computation_summary,
    validate_stage6_prediction_metric_computation_gate,
)


def _records():
    return [
        DonorFeatureRecord("D001", "train", "flare", (1.0, 1.0)),
        DonorFeatureRecord("D002", "train", "managed", (5.0, 5.0)),
        DonorFeatureRecord("D003", "train", "flare", (1.5, 1.5)),
        DonorFeatureRecord("D004", "validation", "flare", (1.2, 1.2)),
        DonorFeatureRecord("D005", "test", "managed", (4.8, 4.8)),
        DonorFeatureRecord("D006", "holdout", "flare", (4.9, 4.9)),
    ]


def _model():
    return fit_controlled_centroid_baseline(_records()).fitted_model


def test_f006_gate_allows_prediction_and_metric_only_in_memory():
    gate = validate_stage6_prediction_metric_computation_gate(
        Stage6PredictionMetricComputationGate(notes="  prediction metric only  ")
    )

    assert gate.current_feature == "STAGE6-F006"
    assert gate.previous_feature == "STAGE6-F005"
    assert gate.previous_feature_status == "completed"
    assert gate.completed_stage6_features == (
        "STAGE6-F001",
        "STAGE6-F002",
        "STAGE6-F003",
        "STAGE6-F004",
        "STAGE6-F005",
    )
    assert gate.required_upstream_gates == REQUIRED_UPSTREAM_GATES
    assert gate.scope == (
        "in_memory_donor_level_prediction_metric_only_no_artifacts_claims"
    )
    assert gate.baseline_family == "nearest_centroid_baseline"
    assert gate.expected_record_level == "donor"
    assert gate.preprocessing_scope == "fold_local_only"
    assert gate.required_f006_contracts == REQUIRED_F006_CONTRACTS
    assert gate.deferred_f007_actions == DEFERRED_F007_ACTIONS
    assert gate.metric_names == METRIC_NAMES
    assert gate.next_feature == "STAGE6-F007"
    assert gate.closeout_feature == "STAGE6-F006-CLOSEOUT"
    assert gate.allow_prediction_generation is True
    assert gate.allow_metric_computation is True
    assert gate.allow_prediction_manifest_write is False
    assert gate.allow_metric_table_write is False
    assert gate.allow_model_refit is False
    assert gate.training_allowed is False
    assert gate.external_validation_allowed is False
    assert gate.performance_claims_added is False
    assert gate.notes == "prediction metric only"


def test_f006_from_mapping_normalizes_sequences():
    gate = stage6_prediction_metric_computation_gate_from_mapping(
        {
            "completed_stage6_features": list(REQUIRED_UPSTREAM_GATES),
            "required_upstream_gates": list(REQUIRED_UPSTREAM_GATES),
            "required_f006_contracts": list(REQUIRED_F006_CONTRACTS),
            "deferred_f007_actions": list(DEFERRED_F007_ACTIONS),
            "metric_names": list(METRIC_NAMES),
        }
    )

    assert gate.current_feature == "STAGE6-F006"
    assert gate.required_f006_contracts == REQUIRED_F006_CONTRACTS
    assert gate.deferred_f007_actions == DEFERRED_F007_ACTIONS
    assert gate.metric_names == METRIC_NAMES


@pytest.mark.parametrize(
    "flag_name",
    [
        "require_completed_stage6_f001",
        "require_completed_stage6_f002",
        "require_completed_stage6_f003",
        "require_completed_stage6_f004",
        "require_completed_stage6_f005",
        "require_f005_fitted_baseline",
        "require_in_memory_records_only",
        "require_non_train_predictions_only",
        "require_metric_scope_limited_to_in_memory_predictions",
        "require_no_file_or_artifact_outputs",
        "require_no_refit_or_training",
        "require_no_external_validation",
        "require_no_performance_claims",
        "allow_in_memory_prediction_generation",
        "allow_in_memory_metric_computation",
        "allow_prediction_generation",
        "allow_metric_computation",
    ],
)
def test_f006_requires_prediction_metric_permissions(flag_name):
    with pytest.raises(Stage6PredictionMetricComputationError, match="requires"):
        validate_stage6_prediction_metric_computation_gate(
            Stage6PredictionMetricComputationGate(**{flag_name: False})
        )


@pytest.mark.parametrize(
    "flag_name",
    [
        "allow_filesystem_artifact_access",
        "allow_real_artifact_loading",
        "allow_npy_payload_loading",
        "allow_embedding_vector_parsing_from_disk",
        "allow_split_execution_from_file",
        "allow_model_refit",
        "allow_training",
        "training_allowed",
        "allow_model_artifact_persistence",
        "allow_prediction_manifest_write",
        "allow_metric_table_write",
        "external_validation_allowed",
        "allow_external_validation",
        "performance_claims_allowed",
        "performance_claims_added",
    ],
)
def test_f006_keeps_file_refit_artifact_validation_and_claim_actions_disabled(
    flag_name,
):
    with pytest.raises(Stage6PredictionMetricComputationError):
        validate_stage6_prediction_metric_computation_gate(
            Stage6PredictionMetricComputationGate(**{flag_name: True})
        )


def test_f006_predicts_non_train_donors_only():
    predictions = predict_with_f005_centroid_baseline(_model(), _records())

    assert [record.donor_id for record in predictions] == ["D004", "D005", "D006"]
    assert [record.split for record in predictions] == [
        "validation",
        "test",
        "holdout",
    ]
    assert [record.predicted_label for record in predictions] == [
        "flare",
        "managed",
        "managed",
    ]
    assert all(record.prediction_unit == "donor" for record in predictions)
    assert all(0.0 <= record.positive_label_score <= 1.0 for record in predictions)


def test_f006_computes_binary_metrics_from_in_memory_predictions():
    metrics = compute_binary_metrics(
        [
            DonorPredictionRecord("D004", "validation", "flare", "flare", 0.8),
            DonorPredictionRecord("D005", "test", "managed", "managed", 0.2),
            DonorPredictionRecord("D006", "holdout", "flare", "managed", 0.3),
        ]
    )

    assert metrics == BinaryMetricSummary(
        positive_label="flare",
        n_predictions=3,
        true_positive=1,
        true_negative=1,
        false_positive=0,
        false_negative=1,
        accuracy=2 / 3,
        balanced_accuracy=0.75,
        sensitivity=0.5,
        specificity=1.0,
        precision=1.0,
        f1=2 / 3,
        brier_score=((0.8 - 1.0) ** 2 + (0.2 - 0.0) ** 2 + (0.3 - 1.0) ** 2)
        / 3,
        performance_claims_added=False,
    )


def test_f006_runs_prediction_and_metric_pipeline_without_artifacts_or_claims():
    result = compute_stage6_prediction_metrics(_model(), _records(), notes="  f006  ")

    assert result.current_feature == "STAGE6-F006"
    assert result.computation_status == "completed"
    assert result.model_family == "nearest_centroid_baseline"
    assert result.record_level == "donor"
    assert result.preprocessing_scope == "fold_local_only"
    assert result.positive_label == "flare"
    assert len(result.predictions) == 3
    assert result.metrics.n_predictions == 3
    assert result.metrics.true_positive == 1
    assert result.metrics.true_negative == 1
    assert result.metrics.false_negative == 1
    assert result.artifacts_written is False
    assert result.model_refit_performed is False
    assert result.external_validation_performed is False
    assert result.performance_claims_added is False
    assert result.notes == "f006"


def test_f006_rejects_non_binary_metrics_or_invalid_scores():
    with pytest.raises(Stage6PredictionMetricComputationError, match="two labels"):
        compute_binary_metrics(
            [
                DonorPredictionRecord("D1", "test", "flare", "flare", 0.7),
                DonorPredictionRecord("D2", "test", "managed", "managed", 0.2),
                DonorPredictionRecord("D3", "test", "healthy", "healthy", 0.1),
            ]
        )

    with pytest.raises(Stage6PredictionMetricComputationError, match=r"\[0, 1\]"):
        compute_binary_metrics(
            [
                DonorPredictionRecord("D1", "test", "flare", "flare", 1.2),
                DonorPredictionRecord("D2", "test", "managed", "managed", 0.2),
            ]
        )


def test_f006_serializes_gate_and_result_without_writing_files():
    gate_dict = stage6_prediction_metric_computation_gate_to_dict(
        Stage6PredictionMetricComputationGate()
    )
    assert gate_dict["current_feature"] == "STAGE6-F006"
    assert gate_dict["allow_prediction_generation"] is True
    assert gate_dict["allow_metric_computation"] is True
    assert gate_dict["allow_prediction_manifest_write"] is False
    assert gate_dict["allow_metric_table_write"] is False

    result_dict = prediction_metric_computation_result_to_dict(
        compute_stage6_prediction_metrics(_model(), _records())
    )
    assert result_dict["current_feature"] == "STAGE6-F006"
    assert len(result_dict["predictions"]) == 3
    assert result_dict["artifacts_written"] is False
    assert result_dict["performance_claims_added"] is False


def test_f006_summary_contains_metrics_but_no_claims():
    summary = stage6_prediction_metric_computation_summary(
        compute_stage6_prediction_metrics(_model(), _records())
    )

    assert summary["current_feature"] == "STAGE6-F006"
    assert summary["computation_status"] == "completed"
    assert summary["record_level"] == "donor"
    assert summary["n_predictions"] == 3
    assert set(summary["metrics"]) == set(METRIC_NAMES)
    assert summary["artifacts_written"] is False
    assert summary["model_refit_performed"] is False
    assert summary["external_validation_performed"] is False
    assert summary["performance_claims_added"] is False
    assert summary["next_feature"] == "STAGE6-F007"


def test_f006_module_has_no_file_loading_sklearn_numpy_or_artifact_writes():
    import lupusfm.evaluation.stage6_prediction_metric_computation as module

    source = module.__loader__.get_source(module.__name__).lower()
    forbidden_fragments = [
        "import sklearn",
        "from sklearn",
        "import pandas",
        "import numpy",
        "np.load",
        "read_h5ad",
        "read_parquet",
        "open(",
        ".write_text(",
        ".to_csv(",
        "joblib",
        "pickle",
    ]

    assert not any(fragment in source for fragment in forbidden_fragments)
