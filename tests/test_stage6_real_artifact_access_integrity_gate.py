from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"
CURRENT_FEATURE_PATH = REPO_ROOT / "state" / "current_feature.md"


def _block_between(text, start_marker, end_marker=None):
    start = text.index(start_marker)
    end = text.index(end_marker, start) if end_marker else len(text)
    return text[start:end]


def test_stage6_f002_records_artifact_access_integrity_gate_metadata():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage6_real_artifact_access_integrity_gate:")

    assert "status: stage6_in_progress" in state
    assert "current_phase: Stage 6" in state
    assert "current_feature: STAGE6-F002" in state
    assert (
        "modeling_readiness: "
        "stage6_f002_real_artifact_access_integrity_gate_in_progress"
        in state
    )
    assert "status: in_progress" in block
    assert "branch: feat/stage6-real-artifact-access-integrity-gate" in block
    assert "current_feature: STAGE6-F002" in block
    assert "feature_name: Real artifact access and integrity gate" in block
    assert "previous_feature: STAGE6-F001" in block
    assert "previous_feature_status: completed" in block
    assert "completed_stage6_features:" in block
    assert "STAGE6-F001" in block
    assert "gate_decision: metadata_access_integrity_gate_opened" in block
    assert "access_scope: path_schema_permission_contract_only" in block
    assert "integrity_scope: metadata_integrity_contract_only" in block
    assert "next_feature: STAGE6-F003" in block
    assert "next_feature_name: Donor-level input materialization gate" in block


def test_stage6_f002_records_expected_artifact_contract_without_payload_access():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage6_real_artifact_access_integrity_gate:")

    assert "artifact_family: geneformer_donor_embeddings" in block
    assert "expected_artifact_format: npy_directory" in block
    assert "expected_artifact_layout: one_file_per_donor_embedding" in block
    assert "expected_record_level: donor" in block
    assert "expected_split_level: donor" in block
    assert (
        "expected_artifact_location_policy: "
        "external_local_or_remote_path_not_committed"
        in block
    )
    assert "required_integrity_contracts:" in block
    assert "path_schema_contract" in block
    assert "permission_contract" in block
    assert "record_level_contract" in block
    assert "artifact_format_contract" in block
    assert "no_large_artifact_commit_contract" in block
    assert "deferred_real_artifact_checks:" in block
    assert "filesystem_existence_check" in block
    assert "file_count_scan" in block
    assert "checksum_calculation" in block
    assert "npy_payload_loading" in block
    assert "embedding_vector_parsing" in block


def test_stage6_f002_preserves_donor_level_and_runtime_locks():
    state = STATE_PATH.read_text()
    block = _block_between(state, "stage6_real_artifact_access_integrity_gate:")

    assert "split_policy: donor_level_only" in block
    assert "leakage_policy: cell_level_split_forbidden" in block
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


def test_stage6_f002_current_feature_document_records_metadata_gate_scope():
    current_feature = CURRENT_FEATURE_PATH.read_text()

    assert "## STAGE6-F002 - Real artifact access and integrity gate" in current_feature
    assert "Status: in_progress" in current_feature
    assert "Branch: `feat/stage6-real-artifact-access-integrity-gate`" in current_feature
    assert "path/schema/permission/integrity contracts only" in current_feature
    assert "STAGE6-F003 - Donor-level input materialization gate" in current_feature
    assert "No filesystem artifact access is performed." in current_feature
    assert "No `.npy` embedding payload is loaded." in current_feature
    assert "No embedding vector is parsed." in current_feature
    assert "No evaluation array is materialized." in current_feature
    assert "No labels are created from real data." in current_feature
    assert "No models are fit." in current_feature
    assert "No predictions are generated." in current_feature
    assert "No real metrics are computed." in current_feature
    assert "No performance claims are added." in current_feature
