import pytest

from lupusfm.evaluation.stage6_controlled_baseline_execution import (
    DEFERRED_F006_ACTIONS,
    REQUIRED_EXECUTION_CONTRACTS,
    REQUIRED_UPSTREAM_GATES,
    DonorFeatureRecord,
    Stage6ControlledBaselineExecutionError,
    Stage6ControlledBaselineExecutionGate,
    controlled_baseline_execution_result_to_dict,
    fit_controlled_centroid_baseline,
    normalize_donor_feature_records,
    stage6_controlled_baseline_execution_gate_from_mapping,
    stage6_controlled_baseline_execution_gate_to_dict,
    stage6_controlled_baseline_execution_summary,
    validate_stage6_controlled_baseline_execution_gate,
)


def _records():
    return [
        DonorFeatureRecord("D001", "train", "flare", (1.0, 2.0, 3.0)),
        DonorFeatureRecord("D002", "train", "managed", (3.0, 4.0, 5.0)),
        DonorFeatureRecord("D003", "train", "flare", (2.0, 3.0, 4.0)),
        DonorFeatureRecord("D004", "validation", "managed", (4.0, 5.0, 6.0)),
        DonorFeatureRecord("D005", "test", "flare", (5.0, 6.0, 7.0)),
    ]


def test_f005_gate_allows_controlled_fit_only():
    gate = validate_stage6_controlled_baseline_execution_gate(
        Stage6ControlledBaselineExecutionGate(notes="  fit only  ")
    )

    assert gate.current_feature == "STAGE6-F005"
    assert gate.previous_feature == "STAGE6-F004"
    assert gate.previous_feature_status == "completed"
    assert gate.completed_stage6_features == (
        "STAGE6-F001",
        "STAGE6-F002",
        "STAGE6-F003",
        "STAGE6-F004",
    )
    assert gate.required_upstream_gates == REQUIRED_UPSTREAM_GATES
    assert gate.scope == (
        "in_memory_donor_level_baseline_fit_only_no_predictions_metrics"
    )
    assert gate.baseline_family == "nearest_centroid_baseline"
    assert gate.expected_record_level == "donor"
    assert gate.preprocessing_scope == "fold_local_only"
    assert gate.required_execution_contracts == REQUIRED_EXECUTION_CONTRACTS
    assert gate.deferred_f006_actions == DEFERRED_F006_ACTIONS
    assert gate.next_feature == "STAGE6-F006"
    assert gate.closeout_feature == "STAGE6-F005-CLOSEOUT"
    assert gate.allow_in_memory_donor_records is True
    assert gate.allow_controlled_baseline_fitting is True
    assert gate.allow_model_fitting is True
    assert gate.modeling_authorization_granted is True
    assert gate.modeling_allowed is True
    assert gate.allow_prediction_generation is False
    assert gate.allow_metric_computation is False
    assert gate.training_allowed is False
    assert gate.external_validation_allowed is False
    assert gate.performance_claims_added is False
    assert gate.notes == "fit only"


def test_f005_from_mapping_normalizes_sequence_fields():
    gate = stage6_controlled_baseline_execution_gate_from_mapping(
        {
            "completed_stage6_features": list(REQUIRED_UPSTREAM_GATES),
            "required_upstream_gates": list(REQUIRED_UPSTREAM_GATES),
            "required_execution_contracts": list(REQUIRED_EXECUTION_CONTRACTS),
            "deferred_f006_actions": list(DEFERRED_F006_ACTIONS),
        }
    )

    assert gate.current_feature == "STAGE6-F005"
    assert gate.required_upstream_gates == REQUIRED_UPSTREAM_GATES
    assert gate.required_execution_contracts == REQUIRED_EXECUTION_CONTRACTS
    assert gate.deferred_f006_actions == DEFERRED_F006_ACTIONS


@pytest.mark.parametrize(
    "flag_name",
    [
        "require_completed_stage6_f001",
        "require_completed_stage6_f002",
        "require_completed_stage6_f003",
        "require_completed_stage6_f004",
        "require_donor_level_records",
        "require_unique_donor_ids",
        "require_train_only_fit",
        "require_holdout_predictions_deferred",
        "require_metric_computation_deferred",
        "require_no_cell_level_split",
        "require_no_global_preprocessing",
        "require_no_model_artifact_persistence",
        "allow_in_memory_donor_records",
        "allow_controlled_baseline_fitting",
        "allow_model_fitting",
        "modeling_authorization_granted",
        "modeling_allowed",
    ],
)
def test_f005_requires_controlled_fit_permissions(flag_name):
    with pytest.raises(Stage6ControlledBaselineExecutionError, match="requires"):
        validate_stage6_controlled_baseline_execution_gate(
            Stage6ControlledBaselineExecutionGate(**{flag_name: False})
        )


@pytest.mark.parametrize(
    "flag_name",
    [
        "allow_filesystem_artifact_access",
        "allow_real_artifact_loading",
        "allow_npy_payload_loading",
        "allow_embedding_vector_parsing_from_disk",
        "allow_input_file_materialization",
        "allow_label_file_materialization",
        "allow_split_execution_from_file",
        "allow_global_preprocessing",
        "allow_scaler_outside_fold",
        "allow_model_artifact_persistence",
        "allow_prediction_generation",
        "allow_metric_computation",
        "allow_training_beyond_controlled_baseline_fit",
        "training_allowed",
        "external_validation_allowed",
        "performance_claims_allowed",
        "performance_claims_added",
    ],
)
def test_f005_keeps_file_prediction_metric_and_claim_actions_disabled(flag_name):
    with pytest.raises(Stage6ControlledBaselineExecutionError):
        validate_stage6_controlled_baseline_execution_gate(
            Stage6ControlledBaselineExecutionGate(**{flag_name: True})
        )


def test_f005_normalizes_donor_records_without_file_access():
    normalized = normalize_donor_feature_records(
        [
            {
                "donor_id": " D001 ",
                "split": "train",
                "label": "flare",
                "features": [1, 2, 3],
            },
            {
                "donor_id": "D002",
                "split": "train",
                "label": "managed",
                "features": [3, 4, 5],
            },
            {
                "donor_id": "D003",
                "split": "validation",
                "label": "managed",
                "features": [5, 6, 7],
            },
        ]
    )

    assert normalized[0] == DonorFeatureRecord(
        donor_id="D001",
        split="train",
        label="flare",
        features=(1.0, 2.0, 3.0),
    )


def test_f005_rejects_duplicate_donors_mismatched_features_or_missing_holdout():
    with pytest.raises(Stage6ControlledBaselineExecutionError, match="unique"):
        normalize_donor_feature_records(
            [
                DonorFeatureRecord("D001", "train", "flare", (1.0, 2.0)),
                DonorFeatureRecord("D001", "train", "managed", (2.0, 3.0)),
                DonorFeatureRecord("D003", "test", "flare", (3.0, 4.0)),
            ]
        )

    with pytest.raises(Stage6ControlledBaselineExecutionError, match="same length"):
        normalize_donor_feature_records(
            [
                DonorFeatureRecord("D001", "train", "flare", (1.0, 2.0)),
                DonorFeatureRecord("D002", "train", "managed", (2.0, 3.0, 4.0)),
                DonorFeatureRecord("D003", "test", "flare", (3.0, 4.0)),
            ]
        )

    with pytest.raises(Stage6ControlledBaselineExecutionError, match="non-train"):
        normalize_donor_feature_records(
            [
                DonorFeatureRecord("D001", "train", "flare", (1.0, 2.0)),
                DonorFeatureRecord("D002", "train", "managed", (2.0, 3.0)),
                DonorFeatureRecord("D003", "train", "flare", (3.0, 4.0)),
            ]
        )


def test_f005_fits_centroids_from_train_records_only_without_predictions_or_metrics():
    result = fit_controlled_centroid_baseline(_records(), notes="  fixture fit  ")

    assert result.current_feature == "STAGE6-F005"
    assert result.execution_status == "completed"
    assert result.model_family == "nearest_centroid_baseline"
    assert result.record_level == "donor"
    assert result.preprocessing_scope == "fold_local_only"
    assert result.n_records == 5
    assert result.n_train_records == 3
    assert result.n_deferred_prediction_records == 2
    assert result.predictions_generated is False
    assert result.metrics_computed is False
    assert result.performance_claims_added is False
    assert result.notes == "fixture fit"

    fitted = result.fitted_model
    assert fitted.labels == ("flare", "managed")
    assert fitted.train_donor_ids == ("D001", "D002", "D003")
    assert fitted.class_counts == {"flare": 2, "managed": 1}
    assert fitted.centroids_by_label == {
        "flare": (1.5, 2.5, 3.5),
        "managed": (3.0, 4.0, 5.0),
    }
    assert fitted.predictions_generated is False
    assert fitted.metrics_computed is False
    assert fitted.performance_claims_added is False


def test_f005_serializes_gate_and_result_without_prediction_or_metric_values():
    gate_dict = stage6_controlled_baseline_execution_gate_to_dict(
        Stage6ControlledBaselineExecutionGate()
    )
    assert gate_dict["current_feature"] == "STAGE6-F005"
    assert gate_dict["allow_model_fitting"] is True
    assert gate_dict["allow_prediction_generation"] is False
    assert gate_dict["allow_metric_computation"] is False
    assert gate_dict["performance_claims_added"] is False

    result_dict = controlled_baseline_execution_result_to_dict(
        fit_controlled_centroid_baseline(_records())
    )
    assert result_dict["current_feature"] == "STAGE6-F005"
    assert result_dict["fitted_model"]["centroids_by_label"] == {
        "flare": [1.5, 2.5, 3.5],
        "managed": [3.0, 4.0, 5.0],
    }
    assert result_dict["predictions_generated"] is False
    assert result_dict["metrics_computed"] is False


def test_f005_summary_reports_fit_counts_not_performance():
    summary = stage6_controlled_baseline_execution_summary(
        fit_controlled_centroid_baseline(_records())
    )

    assert summary == {
        "current_feature": "STAGE6-F005",
        "execution_status": "completed",
        "model_family": "nearest_centroid_baseline",
        "record_level": "donor",
        "preprocessing_scope": "fold_local_only",
        "n_records": 5,
        "n_train_records": 3,
        "n_deferred_prediction_records": 2,
        "labels": ("flare", "managed"),
        "predictions_generated": False,
        "metrics_computed": False,
        "performance_claims_added": False,
        "next_feature": "STAGE6-F006",
    }


def test_f005_module_has_no_file_loading_sklearn_numpy_metric_or_artifact_writes():
    import lupusfm.evaluation.stage6_controlled_baseline_execution as module

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
        ".fit(",
        ".predict(",
        "roc_auc",
        "accuracy_score",
        "classification_report",
        "joblib",
        "pickle",
    ]

    assert not any(fragment in source for fragment in forbidden_fragments)
