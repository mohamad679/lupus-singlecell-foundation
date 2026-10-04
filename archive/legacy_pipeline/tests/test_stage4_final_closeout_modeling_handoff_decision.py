from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
CURRENT_FEATURE_PATH = REPO_ROOT / "state" / "current_feature.md"


def _block_between(text, start_marker, end_marker=None):
    start = text.index(start_marker)
    end = text.index(end_marker, start) if end_marker else len(text)
    return text[start:end]


def test_stage4_f006_marks_stage4_complete_without_modeling_authorization():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage4_final_closeout_and_modeling_handoff_decision:")

    assert "status: stage4_complete" in state
    assert "current_phase: Stage 4" in state
    assert "current_feature: STAGE4-F006" in state
    assert "modeling_readiness: blocked_pending_separate_modeling_stage_approval" in state
    assert "status: completed" in block
    assert "branch: feat/stage4-final-closeout-modeling-handoff-decision" in block
    assert "current_feature: STAGE4-F006" in block
    assert "stage4_closeout_status: completed" in block
    assert "decision_status: completed" in block
    assert "handoff_decision: separate_modeling_stage_required" in block
    assert "modeling_handoff_scope: planning_only_no_modeling_authorization" in block


def test_stage4_f006_records_all_completed_stage4_features():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage4_final_closeout_and_modeling_handoff_decision:")

    assert "STAGE4-F001" in block
    assert "STAGE4-F002" in block
    assert "STAGE4-F003" in block
    assert "STAGE4-F004" in block
    assert "STAGE4-F005" in block
    assert "artifact_validation_status: completed" in block
    assert "aggregation_plan_status: completed" in block
    assert "split_manifest_validation_status: completed" in block
    assert "evaluation_input_readiness_status: completed" in block
    assert "pre_modeling_audit_status: completed" in block


def test_stage4_f006_requires_separate_modeling_stage_and_reviews():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage4_final_closeout_and_modeling_handoff_decision:")

    assert "requires_separate_modeling_stage: true" in block
    assert "requires_new_branch_for_modeling: true" in block
    assert "requires_explicit_modeling_approval: true" in block
    assert "requires_human_review_before_modeling: true" in block
    assert "requires_reproducibility_review: true" in block
    assert "requires_leakage_review: true" in block
    assert "requires_artifact_integrity_review: true" in block
    assert "requires_scope_review: true" in block


def test_stage4_f006_preserves_runtime_and_modeling_safety_locks():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage4_final_closeout_and_modeling_handoff_decision:")

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


def test_stage4_f006_current_feature_document_records_final_handoff_decision():
    current_feature = CURRENT_FEATURE_PATH.read_text()

    assert "STAGE4-F006 - Stage 4 final closeout and modeling handoff decision" in current_feature
    assert "Status: completed" in current_feature
    assert "Stage 4 is complete." in current_feature
    assert "`separate_modeling_stage_required`" in current_feature
    assert "Stage 4 does not authorize modeling" in current_feature
    assert "No `.npy` embedding payload is loaded" in current_feature
    assert "No evaluation array is materialized" in current_feature
    assert "No predictions are generated" in current_feature
    assert "No real metrics are computed" in current_feature
    assert "No training is performed" in current_feature
    assert "No performance claims are added" in current_feature
    assert "A separate modeling stage may be planned only after explicit approval." in current_feature
