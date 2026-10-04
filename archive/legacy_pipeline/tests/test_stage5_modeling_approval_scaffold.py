from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
CURRENT_FEATURE_PATH = REPO_ROOT / "state" / "current_feature.md"


def _block_between(text, start_marker, end_marker=None):
    start = text.index(start_marker)
    end = text.index(end_marker, start) if end_marker else len(text)
    return text[start:end]


def test_stage5_f001_records_stage5_history_without_modeling_authorization():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage5_modeling_approval_scaffold:")

    assert "status: stage5_complete" in state
    assert "current_phase: Stage 5" in state
    assert "current_phase_name: Stage 5 - Complete" in state
    assert "current_feature: STAGE5-COMPLETE" in state
    assert "modeling_readiness: blocked_pending_separate_modeling_execution_stage" in state
    assert "status: completed" in block
    assert "branch: chore/stage5-f001-closeout" in block
    assert "current_feature: STAGE5-F001" in block
    assert "feature_name: Modeling approval scaffold" in block
    assert "closeout_feature: STAGE5-F001-CLOSEOUT" in block
    assert "closeout_status: completed" in block
    assert "next_feature: STAGE5-F002" in block
    assert "next_feature_name: Modeling execution protocol scaffold" in block
    assert "modeling_authorization_status: not_granted" in block
    assert "approval_status: pending" in block


def test_stage5_f001_records_stage4_handoff_as_required_upstream():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage5_modeling_approval_scaffold:")

    assert "upstream_stage4_status: completed" in block
    assert "upstream_handoff_decision: separate_modeling_stage_required" in block
    assert "completed_stage4_features:" in block
    assert "STAGE4-F001" in block
    assert "STAGE4-F002" in block
    assert "STAGE4-F003" in block
    assert "STAGE4-F004" in block
    assert "STAGE4-F005" in block
    assert "STAGE4-F006" in block


def test_stage5_f001_requires_approval_protocol_and_donor_level_controls():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage5_modeling_approval_scaffold:")

    assert "requires_explicit_modeling_approval: true" in block
    assert "requires_human_review_before_modeling: true" in block
    assert "requires_reproducibility_review: true" in block
    assert "requires_leakage_review: true" in block
    assert "requires_artifact_integrity_review: true" in block
    assert "requires_scope_review: true" in block
    assert "requires_protocol_before_execution: true" in block
    assert "requires_donor_level_only: true" in block
    assert "forbids_cell_level_split: true" in block
    assert "requires_no_large_artifact_commit: true" in block


def test_stage5_f001_preserves_runtime_modeling_metric_and_claim_locks():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage5_modeling_approval_scaffold:")

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


def test_stage5_f001_current_feature_document_advances_after_closeout():
    current_feature = CURRENT_FEATURE_PATH.read_text()

    assert "STAGE5-F002 - Modeling execution protocol scaffold" in current_feature
    assert "Status: completed" in current_feature
    assert "Branch: `chore/stage5-final-closeout`" in current_feature
    assert "Stage 5 - Modeling stage approval and execution planning" in current_feature
    assert "Stage 5 has started, but modeling is still not authorized." in current_feature
    assert "STAGE5-F001 - Modeling approval scaffold" in current_feature
    assert "Status: completed" in current_feature
    assert "Branch: `chore/stage5-f001-closeout`" in current_feature
    assert "No `.npy` embedding payload is loaded" in current_feature
    assert "No evaluation array is materialized" in current_feature
    assert "No models are fit" in current_feature
    assert "No predictions are generated" in current_feature
    assert "No real metrics are computed" in current_feature
    assert "No performance claims are added" in current_feature
