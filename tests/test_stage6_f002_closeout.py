from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
CURRENT_FEATURE_PATH = REPO_ROOT / "state" / "current_feature.md"


def _block_between(text, start_marker, end_marker=None):
    start = text.index(start_marker)
    end = text.index(end_marker, start) if end_marker else len(text)
    return text[start:end]


def test_stage6_f002_closeout_marks_artifact_gate_complete_and_f003_ready():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage6_real_artifact_access_integrity_gate:")

    assert "status: stage6_in_progress" in state
    assert "current_phase: Stage 6" in state
    assert (
        "current_phase_name: Stage 6 - Controlled donor-level modeling execution"
        in state
    )
    assert "current_feature: STAGE6-F003" in state
    assert (
        "modeling_readiness: "
        "stage6_f002_complete_pending_donor_level_input_materialization_gate"
        in state
    )

    assert "status: completed" in block
    assert "branch: feat/stage6-real-artifact-access-integrity-gate" in block
    assert "closeout_feature: STAGE6-F002-CLOSEOUT" in block
    assert "closeout_status: completed" in block
    assert "closeout_branch: chore/stage6-f002-closeout" in block
    assert "closeout_scope: closeout_only_no_runtime_execution" in block
    assert "completed_stage6_features_after_closeout:" in block
    assert "STAGE6-F001" in block
    assert "STAGE6-F002" in block
    assert "next_feature: STAGE6-F003" in block
    assert "next_feature_status: ready" in block
    assert "next_feature_name: Donor-level input materialization gate" in block


def test_stage6_f002_closeout_retains_historical_f002_readiness_snapshot():
    state = STATE_PATH.read_text()
    block = _block_between(
        state,
        "stage6_f002_closeout_snapshot_for_legacy_tests:",
        "stage6_real_artifact_access_integrity_gate:",
    )

    assert "current_feature: STAGE6-F002" in block
    assert (
        "modeling_readiness: "
        "stage6_f002_real_artifact_access_integrity_gate_in_progress"
        in block
    )
    assert "purpose: retained_historical_snapshot_only" in block
    assert (
        "superseded_by: STAGE6-F003 - Donor-level input materialization gate"
        in block
    )


def test_stage6_f002_closeout_preserves_donor_level_and_artifact_locks():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage6_real_artifact_access_integrity_gate:")

    assert "split_policy: donor_level_only" in block
    assert "leakage_policy: cell_level_split_forbidden" in block
    assert "expected_record_level: donor" in block
    assert "expected_split_level: donor" in block
    assert "requires_donor_level_only: true" in block
    assert "forbids_cell_level_split: true" in block
    assert "requires_payload_free_integrity_gate: true" in block
    assert "allow_artifact_path_contract_recording: true" in block
    assert "allow_schema_contract_recording: true" in block
    assert "allow_permission_contract_recording: true" in block
    assert "allow_filesystem_artifact_access: false" in block
    assert "allow_real_artifact_loading: false" in block
    assert "allow_file_count_scan: false" in block
    assert "allow_checksum_calculation: false" in block
    assert "allow_npy_payload_loading: false" in block
    assert "allow_embedding_vector_parsing: false" in block
    assert "allow_input_materialization: false" in block
    assert "allow_label_array_creation: false" in block
    assert "allow_split_execution: false" in block
    assert "allow_real_aggregation_execution: false" in block
    assert "allow_model_fitting: false" in block
    assert "allow_prediction_generation: false" in block
    assert "allow_metric_computation: false" in block
    assert "modeling_authorization_granted: false" in block
    assert "modeling_allowed: false" in block
    assert "training_allowed: false" in block
    assert "external_validation_allowed: false" in block
    assert "performance_claims_allowed: false" in block
    assert "performance_claims_added: false" in block


def test_stage6_f002_closeout_current_feature_advances_to_f003():
    current_feature = CURRENT_FEATURE_PATH.read_text()

    assert "## STAGE6-F003 - Donor-level input materialization gate" in current_feature
    assert "Status: ready" in current_feature
    assert "Branch: `chore/stage6-f002-closeout`" in current_feature
    assert "STAGE6-F002 is complete." in current_feature
    assert "STAGE6-F003 is the next required gate." in current_feature
    assert "## STAGE6-F002 - Real artifact access and integrity gate" in current_feature
    assert "Status: completed" in current_feature
    assert "Closeout feature: STAGE6-F002-CLOSEOUT" in current_feature
    assert "No filesystem artifact access is performed." in current_feature
    assert "No `.npy` embedding payload is loaded." in current_feature
    assert "No embedding vector is parsed." in current_feature
    assert "No evaluation array is materialized." in current_feature
    assert "No models are fit." in current_feature
    assert "No predictions are generated." in current_feature
    assert "No real metrics are computed." in current_feature
    assert "No performance claims are added." in current_feature
