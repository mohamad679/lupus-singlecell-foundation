from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
CURRENT_FEATURE_PATH = REPO_ROOT / "state" / "current_feature.md"


def _block_between(text, start_marker, end_marker=None):
    start = text.index(start_marker)
    end = text.index(end_marker, start) if end_marker else len(text)
    return text[start:end]


def test_stage4_f005_closeout_marks_feature_complete_and_next_feature_ready():
    state = STATE_PATH.read_text()
    block = _block_between(
        state,
        "stage4_real_pre_modeling_audit_gate:",
        "stage4_final_closeout_and_modeling_handoff_decision:",
    )

    assert "status: stage4_complete" in state
    assert "current_phase: Stage 4" in state
    assert "current_feature: STAGE4-F006" in state
    assert "next_feature: STAGE4-F006" in state
    assert "next_feature_name: Stage 4 final closeout and modeling handoff decision" in state
    assert "status: completed" in block
    assert "branch: chore/stage4-f005-closeout" in block
    assert "current_feature: STAGE4-F005" in block
    assert "closeout_feature: STAGE4-F005-CLOSEOUT" in block
    assert "closeout_status: completed" in block
    assert "audit_outcome: review_required" in block


def test_stage4_f005_closeout_retains_pre_modeling_review_gates():
    state = STATE_PATH.read_text()
    block = _block_between(
        state,
        "stage4_real_pre_modeling_audit_gate:",
        "stage4_final_closeout_and_modeling_handoff_decision:",
    )

    assert "requires_human_review_before_modeling: true" in block
    assert "requires_explicit_modeling_permission: true" in block
    assert "requires_reproducibility_review: true" in block
    assert "requires_leakage_review: true" in block
    assert "requires_artifact_integrity_review: true" in block
    assert "requires_scope_review: true" in block
    assert "human review before modeling" in block
    assert "explicit modeling permission" in block
    assert "reproducibility review" in block
    assert "leakage review" in block
    assert "artifact integrity review" in block
    assert "scope review" in block


def test_stage4_f005_closeout_preserves_runtime_and_modeling_safety_locks():
    state = STATE_PATH.read_text()
    block = _block_between(
        state,
        "stage4_real_pre_modeling_audit_gate:",
        "stage4_final_closeout_and_modeling_handoff_decision:",
    )

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
    assert "modeling_allowed: false" in block
    assert "training_allowed: false" in block
    assert "external_validation_allowed: false" in block
    assert "performance_claims_allowed: false" in block



def test_stage4_f005_closeout_current_feature_document_has_advanced_to_f006():
    current_feature = CURRENT_FEATURE_PATH.read_text()

    assert "STAGE4-F006 - Stage 4 final closeout and modeling handoff decision" in current_feature
    assert "Status: completed" in current_feature
    assert "Stage 4 is complete." in current_feature
    assert "`separate_modeling_stage_required`" in current_feature
    assert "Stage 4 does not authorize modeling" in current_feature
    assert "No `.npy` embedding payload is loaded" in current_feature
    assert "No predictions are generated" in current_feature
    assert "No real metrics are computed" in current_feature
    assert "No performance claims are added" in current_feature
    assert "A separate modeling stage may be planned only after explicit approval." in current_feature