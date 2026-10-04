from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
CURRENT_FEATURE_PATH = REPO_ROOT / "state" / "current_feature.md"


def _block_between(text, start_marker, end_marker=None):
    start = text.index(start_marker)
    end = text.index(end_marker, start) if end_marker else len(text)
    return text[start:end]


def test_stage6_f001_records_active_stage6_execution_authorization():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage6_modeling_execution_authorization:")

    assert "status: stage6_in_progress" in state
    assert "current_phase: Stage 6" in state
    assert "current_phase_name: Stage 6 - Controlled donor-level modeling execution" in state
    assert "current_feature: STAGE6-F001" in state
    assert "status: in_progress" in block
    assert "branch: feat/stage6-controlled-donor-level-modeling-execution" in block
    assert "current_feature: STAGE6-F001" in block
    assert "feature_name: Modeling execution authorization" in block
    assert "authorization_decision: stage6_controlled_execution_path_authorized" in block
    assert "modeling_authorization_status: stage6_opened_no_runtime_execution" in block
    assert "stage6_execution_policy: controlled_donor_level_execution_in_stage6" in block
    assert "additional_execution_stage_policy: no_additional_execution_stage_required" in block
    assert "first_runtime_execution_feature: STAGE6-F005" in block
    assert "next_feature: STAGE6-F002" in block
    assert "next_feature_name: Real artifact access and integrity gate" in block


def test_stage6_f001_records_stage5_handoff_as_completed_upstream():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage6_modeling_execution_authorization:")

    assert "upstream_stage5_status: completed" in block
    assert "upstream_handoff_decision: separate_modeling_execution_stage_required" in block
    assert "previous_stage5_feature: STAGE5-F005" in block
    assert "previous_stage5_closeout_status: completed" in block
    assert "completed_stage5_features:" in block
    assert "STAGE5-F001" in block
    assert "STAGE5-F002" in block
    assert "STAGE5-F003" in block
    assert "STAGE5-F004" in block
    assert "STAGE5-F005" in block


def test_stage6_f001_removes_need_for_stage7_and_keeps_execution_inside_stage6():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage6_modeling_execution_authorization:")

    assert "requires_no_additional_execution_stage: true" in block
    assert "permits_stage6_controlled_execution_path: true" in block
    assert "stage7_required: false" in block
    assert "separate_stage7_required: false" in block
    assert "remaining_stage6_features:" in block
    assert "STAGE6-F002" in block
    assert "STAGE6-F003" in block
    assert "STAGE6-F004" in block
    assert "STAGE6-F005" in block
    assert "STAGE6-F006" in block
    assert "STAGE6-F007" in block


def test_stage6_f001_preserves_donor_level_leakage_and_runtime_locks():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage6_modeling_execution_authorization:")

    assert "handoff_record_level: donor" in block
    assert "split_policy: donor_level_only" in block
    assert "leakage_policy: cell_level_split_forbidden" in block
    assert "requires_donor_level_only: true" in block
    assert "forbids_cell_level_split: true" in block
    assert "allow_real_artifact_loading: false" in block
    assert "allow_npy_payload_loading: false" in block
    assert "allow_embedding_vector_parsing: false" in block
    assert "allow_input_materialization: false" in block
    assert "allow_label_array_creation: false" in block
    assert "allow_split_execution: false" in block
    assert "allow_real_aggregation_execution: false" in block
    assert "allow_anndata_loading: false" in block
    assert "allow_geneformer_execution: false" in block
    assert "allow_tokenizer_execution: false" in block
    assert "allow_embedding_extraction: false" in block
    assert "allow_feature_extraction: false" in block
    assert "allow_model_fitting: false" in block
    assert "allow_prediction_generation: false" in block
    assert "allow_metric_computation: false" in block
    assert "modeling_authorization_granted: false" in block
    assert "modeling_allowed: false" in block
    assert "training_allowed: false" in block
    assert "external_validation_allowed: false" in block
    assert "performance_claims_allowed: false" in block
    assert "performance_claims_added: false" in block


def test_stage6_f001_current_feature_document_starts_stage6_without_runtime_execution():
    current_feature = CURRENT_FEATURE_PATH.read_text()

    assert "## Stage 6 active" in current_feature
    assert "Stage 6 - Controlled donor-level modeling execution" in current_feature
    assert "STAGE6-F001 - Modeling execution authorization" in current_feature
    assert "Branch: `feat/stage6-controlled-donor-level-modeling-execution`" in current_feature
    assert "No Stage 7 is required for execution." in current_feature
    assert "Real execution must proceed inside Stage 6 after explicit feature gates." in current_feature
    assert "STAGE6-F005 - Controlled baseline execution" in current_feature
    assert "No `.npy` embedding payload is loaded." in current_feature
    assert "No evaluation array is materialized." in current_feature
    assert "No models are fit." in current_feature
    assert "No predictions are generated." in current_feature
    assert "No real metrics are computed." in current_feature
    assert "No performance claims are added." in current_feature
    assert "Stage 5 - Modeling stage approval and execution planning" in current_feature
    assert "STAGE5-F005 - Final Stage 5 modeling handoff decision" in current_feature
