from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
CURRENT_FEATURE_PATH = REPO_ROOT / "state" / "current_feature.md"


def _block_between(text, start_marker, end_marker=None):
    start = text.index(start_marker)
    end = text.index(end_marker, start) if end_marker else len(text)
    return text[start:end]


def test_stage5_f004_closeout_marks_audit_complete_and_final_handoff_ready():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage5_pre_execution_audit_gate:")

    assert "status: stage5_complete" in state
    assert "current_phase: Stage 5" in state
    assert "current_phase_name: Stage 5 - Complete" in state
    assert "current_feature: STAGE5-COMPLETE" in state
    assert "modeling_readiness: blocked_pending_separate_modeling_execution_stage" in state
    assert "stage5_permission: stage5_complete_no_modeling_authorization" in state

    assert "status: completed" in block
    assert "branch: chore/stage5-f004-closeout" in block
    assert "current_feature: STAGE5-F004" in block
    assert "feature_name: Pre-execution audit gate" in block
    assert "closeout_feature: STAGE5-F004-CLOSEOUT" in block
    assert "closeout_status: completed" in block
    assert "next_feature: STAGE5-F005" in block
    assert "next_feature_name: Final Stage 5 modeling handoff decision" in block


def test_stage5_f004_closeout_preserves_audit_chain_and_policies():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage5_pre_execution_audit_gate:")

    assert "completed_stage5_features:" in block
    assert "STAGE5-F001" in block
    assert "STAGE5-F002" in block
    assert "STAGE5-F003" in block
    assert "previous_contract_feature: STAGE5-F003" in block
    assert "previous_contract_status: completed" in block
    assert "audit_record_level: donor" in block
    assert "split_policy: donor_level_only" in block
    assert "leakage_policy: cell_level_split_forbidden" in block
    assert "audit_scope_policy: audit_only_no_execution" in block
    assert "artifact_loading_policy: prohibited_until_explicit_gate" in block
    assert "input_materialization_policy: prohibited_until_explicit_gate" in block
    assert "label_creation_policy: prohibited_until_explicit_gate" in block
    assert "split_execution_policy: prohibited_until_explicit_gate" in block
    assert "aggregation_execution_policy: prohibited_until_explicit_gate" in block
    assert "modeling_execution_policy: prohibited_until_explicit_gate" in block
    assert "prediction_generation_policy: prohibited_until_explicit_gate" in block
    assert "metric_computation_policy: future_only_no_computation" in block
    assert "external_validation_policy: prohibited_until_explicit_gate" in block
    assert "performance_claim_policy: prohibited_until_explicit_gate" in block


def test_stage5_f004_closeout_keeps_required_reviews_and_handoff_gate():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage5_pre_execution_audit_gate:")

    assert "requires_explicit_modeling_approval: true" in block
    assert "requires_human_review_before_modeling: true" in block
    assert "requires_reproducibility_review: true" in block
    assert "requires_leakage_review: true" in block
    assert "requires_artifact_integrity_review: true" in block
    assert "requires_scope_review: true" in block
    assert "requires_donor_level_only: true" in block
    assert "forbids_cell_level_split: true" in block
    assert "requires_no_large_artifact_commit: true" in block
    assert "requires_protocol_before_execution: true" in block
    assert "requires_separate_execution_gate: true" in block
    assert "requires_final_stage5_handoff_decision: true" in block


def test_stage5_f004_closeout_preserves_runtime_modeling_metric_and_claim_locks():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage5_pre_execution_audit_gate:")

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
    assert "allow_global_preprocessing: false" in block
    assert "allow_scaler_outside_fold: false" in block
    assert "allow_model_fitting: false" in block
    assert "allow_prediction_generation: false" in block
    assert "allow_metric_computation: false" in block
    assert "allow_modeling: false" in block
    assert "modeling_authorization_granted: false" in block
    assert "modeling_allowed: false" in block
    assert "training_allowed: false" in block
    assert "external_validation_allowed: false" in block
    assert "performance_claims_allowed: false" in block
    assert "performance_claims_added: false" in block


def test_stage5_f004_closeout_current_feature_document_advances_to_f005():
    current_feature = CURRENT_FEATURE_PATH.read_text()

    assert "STAGE5-F005 - Final Stage 5 modeling handoff decision" in current_feature
    assert "Status: completed" in current_feature
    assert "Branch: `chore/stage5-final-closeout`" in current_feature
    assert "STAGE5-F004 - Pre-execution audit gate" in current_feature
    assert "Status: completed" in current_feature
    assert "Branch: `chore/stage5-f004-closeout`" in current_feature
    assert "Stage 5 has started, but modeling is still not authorized." in current_feature
    assert "No `.npy` embedding payload is loaded" in current_feature
    assert "No evaluation array is materialized" in current_feature
    assert "No models are fit" in current_feature
    assert "No predictions are generated" in current_feature
    assert "No real metrics are computed" in current_feature
    assert "No performance claims are added" in current_feature
