from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
CURRENT_FEATURE_PATH = REPO_ROOT / "state" / "current_feature.md"


def _block_between(text, start_marker, end_marker=None):
    start = text.index(start_marker)
    end = text.index(end_marker, start) if end_marker else len(text)
    return text[start:end]


def test_stage4_f005_is_current_project_feature():
    state = STATE_PATH.read_text()

    assert "status: stage4_f005_in_progress" in state
    assert "current_phase: Stage 4" in state
    assert "current_feature: STAGE4-F005" in state
    assert "stage4_real_pre_modeling_audit_gate:" in state
    assert "next_feature: STAGE4-F006" in state
    assert "next_feature_name: Stage 4 final closeout and modeling handoff decision" in state


def test_stage4_f005_records_pre_modeling_audit_scope_and_upstream_gates():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage4_real_pre_modeling_audit_gate:")

    assert "status: in_progress" in block
    assert "branch: feat/stage4-real-pre-modeling-audit-gate" in block
    assert "current_feature: STAGE4-F005" in block
    assert "STAGE4-F001" in block
    assert "STAGE4-F002" in block
    assert "STAGE4-F003" in block
    assert "STAGE4-F004" in block
    assert "artifact_validation_status: completed" in block
    assert "aggregation_plan_status: completed" in block
    assert "split_manifest_validation_status: completed" in block
    assert "evaluation_input_readiness_status: completed" in block
    assert "audit_outcome: review_required" in block


def test_stage4_f005_preserves_review_gates_and_safety_locks():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage4_real_pre_modeling_audit_gate:")

    assert "requires_human_review_before_modeling: true" in block
    assert "requires_explicit_modeling_permission: true" in block
    assert "requires_reproducibility_review: true" in block
    assert "requires_leakage_review: true" in block
    assert "requires_artifact_integrity_review: true" in block
    assert "requires_scope_review: true" in block
    assert "allow_npy_payload_loading: false" in block
    assert "allow_input_materialization: false" in block
    assert "allow_split_execution: false" in block
    assert "allow_model_fitting: false" in block
    assert "allow_prediction_generation: false" in block
    assert "allow_metric_computation: false" in block
    assert "modeling_allowed: false" in block
    assert "training_allowed: false" in block
    assert "external_validation_allowed: false" in block
    assert "performance_claims_allowed: false" in block
    assert "fit models" in block
    assert "compute metrics" in block
    assert "add performance claims" in block


def test_stage4_f005_current_feature_document_describes_safe_scope():
    current_feature = CURRENT_FEATURE_PATH.read_text()

    assert "STAGE4-F005 - Real pre-modeling audit gate" in current_feature
    assert "Status: in_progress" in current_feature
    assert "pre-modeling audit gate" in current_feature
    assert "No `.npy` embedding payload is loaded" in current_feature
    assert "No predictions are generated" in current_feature
    assert "No real metrics are computed" in current_feature
    assert "No performance claims are added" in current_feature
    assert "STAGE4-F006 - Stage 4 final closeout and modeling handoff decision" in current_feature
