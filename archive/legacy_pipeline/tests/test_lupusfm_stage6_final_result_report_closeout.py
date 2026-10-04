import pytest

from lupusfm.evaluation.stage6_final_result_report_closeout import (
    REQUIRED_CLOSEOUT_SECTIONS,
    REQUIRED_FINAL_LIMITATIONS,
    REQUIRED_PRIOR_FEATURES,
    STAGE6_COMPLETED_FEATURES,
    Stage6FinalResultReportCloseout,
    Stage6FinalResultReportCloseoutError,
    stage6_final_result_report_closeout_from_mapping,
    stage6_final_result_report_closeout_summary,
    stage6_final_result_report_closeout_to_dict,
    validate_stage6_final_result_report_closeout,
)


def test_stage6_final_closeout_accepts_metadata_only_completion():
    closeout = validate_stage6_final_result_report_closeout(
        Stage6FinalResultReportCloseout(notes="  final closeout  ")
    )

    assert closeout.current_feature == "STAGE6-F007"
    assert closeout.closeout_feature == "STAGE6-F007-CLOSEOUT"
    assert closeout.closeout_status == "completed"
    assert closeout.closeout_decision == "stage6_final_result_report_closeout_completed"
    assert closeout.previous_feature == "STAGE6-F006"
    assert closeout.previous_feature_status == "completed"
    assert closeout.completed_stage6_features == STAGE6_COMPLETED_FEATURES
    assert closeout.required_prior_features == REQUIRED_PRIOR_FEATURES
    assert closeout.required_closeout_sections == REQUIRED_CLOSEOUT_SECTIONS
    assert closeout.required_final_limitations == REQUIRED_FINAL_LIMITATIONS
    assert closeout.final_stage_status == "completed"
    assert closeout.final_current_feature == "STAGE6-COMPLETE"
    assert closeout.scope == "stage6_final_report_closeout_no_real_performance_claims"
    assert closeout.record_level == "donor"
    assert closeout.execution_scope == "in_memory_only"
    assert closeout.stage7_policy == "no_stage7_required"
    assert closeout.allow_final_report_metadata is True
    assert closeout.allow_stage6_closeout is True
    assert closeout.require_no_stage7 is True
    assert closeout.allow_report_artifact_write is False
    assert closeout.performance_claims_added is False
    assert closeout.notes == "final closeout"


def test_stage6_final_closeout_from_mapping_normalizes_sequences():
    closeout = stage6_final_result_report_closeout_from_mapping(
        {
            "completed_stage6_features": list(STAGE6_COMPLETED_FEATURES),
            "required_prior_features": list(REQUIRED_PRIOR_FEATURES),
            "required_closeout_sections": list(REQUIRED_CLOSEOUT_SECTIONS),
            "required_final_limitations": list(REQUIRED_FINAL_LIMITATIONS),
        }
    )

    assert closeout.current_feature == "STAGE6-F007"
    assert closeout.completed_stage6_features == STAGE6_COMPLETED_FEATURES
    assert closeout.required_prior_features == REQUIRED_PRIOR_FEATURES
    assert closeout.required_closeout_sections == REQUIRED_CLOSEOUT_SECTIONS
    assert closeout.required_final_limitations == REQUIRED_FINAL_LIMITATIONS


@pytest.mark.parametrize(
    "field_name,value",
    [
        ("current_feature", "STAGE6-F006"),
        ("previous_feature", "STAGE6-F005"),
        ("final_current_feature", "STAGE7"),
        ("stage7_policy", "stage7_required"),
        ("scope", "performance_claim_report"),
    ],
)
def test_stage6_final_closeout_rejects_wrong_identity_or_scope(field_name, value):
    with pytest.raises(Stage6FinalResultReportCloseoutError):
        validate_stage6_final_result_report_closeout(
            Stage6FinalResultReportCloseout(**{field_name: value})
        )


@pytest.mark.parametrize(
    "flag_name",
    [
        "allow_final_report_metadata",
        "allow_stage6_closeout",
        "allow_next_research_handoff_summary",
        "require_all_stage6_features_completed",
        "require_metric_scope_documented",
        "require_limitations_documented",
        "require_no_stage7",
    ],
)
def test_stage6_final_closeout_requires_documentation_controls(flag_name):
    with pytest.raises(Stage6FinalResultReportCloseoutError, match="requires"):
        validate_stage6_final_result_report_closeout(
            Stage6FinalResultReportCloseout(**{flag_name: False})
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
        "allow_report_artifact_write",
        "external_validation_allowed",
        "allow_external_validation",
        "performance_claims_allowed",
        "performance_claims_added",
    ],
)
def test_stage6_final_closeout_keeps_runtime_artifact_validation_and_claims_disabled(
    flag_name,
):
    with pytest.raises(Stage6FinalResultReportCloseoutError):
        validate_stage6_final_result_report_closeout(
            Stage6FinalResultReportCloseout(**{flag_name: True})
        )


def test_stage6_final_closeout_to_dict_serializes_sequences():
    serialized = stage6_final_result_report_closeout_to_dict(
        Stage6FinalResultReportCloseout()
    )

    assert serialized["current_feature"] == "STAGE6-F007"
    assert serialized["final_current_feature"] == "STAGE6-COMPLETE"
    assert serialized["completed_stage6_features"] == list(STAGE6_COMPLETED_FEATURES)
    assert serialized["required_prior_features"] == list(REQUIRED_PRIOR_FEATURES)
    assert serialized["required_closeout_sections"] == list(REQUIRED_CLOSEOUT_SECTIONS)
    assert serialized["required_final_limitations"] == list(REQUIRED_FINAL_LIMITATIONS)
    assert serialized["performance_claims_added"] is False


def test_stage6_final_closeout_summary_has_no_performance_claims():
    summary = stage6_final_result_report_closeout_summary(
        Stage6FinalResultReportCloseout()
    )

    assert summary == {
        "current_stage": "Stage 6",
        "current_feature": "STAGE6-F007",
        "closeout_status": "completed",
        "closeout_decision": "stage6_final_result_report_closeout_completed",
        "final_current_feature": "STAGE6-COMPLETE",
        "final_stage_status": "completed",
        "scope": "stage6_final_report_closeout_no_real_performance_claims",
        "record_level": "donor",
        "execution_scope": "in_memory_only",
        "stage7_policy": "no_stage7_required",
        "prediction_metric_scope": "in_memory_donor_level_predictions_only",
        "performance_claim_policy": "no_real_cohort_performance_claim",
        "external_validation_policy": "not_performed",
        "performance_claims_added": False,
    }


def test_stage6_final_closeout_module_has_no_runtime_or_artifact_writes():
    import lupusfm.evaluation.stage6_final_result_report_closeout as module

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
