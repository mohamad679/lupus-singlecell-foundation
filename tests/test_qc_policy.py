import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs" / "qc.yaml"
MODULE_PATH = REPO_ROOT / "src" / "qc" / "qc_policy.py"


def load_module():
    spec = importlib.util.spec_from_file_location("qc_policy", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def valid_threshold_row():
    return {
        "dataset_id": "GSE137029",
        "metric": "pct_counts_mt",
        "threshold_value": "TODO",
        "threshold_direction": "TODO",
        "threshold_source": "manual_audit_required",
        "rationale": "TODO",
        "applied": "false",
        "approved_by": "",
        "notes": "mock row only",
        "audit_status": "pending_manual_review",
    }


def test_validate_qc_config_accepts_scaffold_config():
    module = load_module()
    config = module.load_qc_config(CONFIG_PATH)

    module.validate_qc_config(config)


def test_validate_qc_summary_headers_accepts_required_headers():
    module = load_module()

    module.validate_qc_summary_headers(module.QC_SUMMARY_HEADERS)


def test_mock_valid_qc_summary_passes():
    module = load_module()
    row = {
        "dataset_id": "GSE137029",
        "sample_id": "TODO",
        "patient_id": "TODO",
        "n_cells": "TODO",
        "median_genes_per_cell": "TODO",
        "median_counts_per_cell": "TODO",
        "median_pct_mt": "TODO",
        "doublet_rate": "TODO",
        "disease_label": "TODO",
        "batch_id": "TODO",
        "qc_status": "pending_manual_review",
        "notes": "mock row only",
        "audit_status": "pending_manual_review",
    }

    module.validate_qc_summary_headers(list(row.keys()))


def test_validate_qc_summary_headers_rejects_missing_headers():
    module = load_module()
    headers = [header for header in module.QC_SUMMARY_HEADERS if header != "audit_status"]

    with pytest.raises(module.QCPolicyError, match="audit_status"):
        module.validate_qc_summary_headers(headers)


def test_mock_valid_threshold_decision_row_passes():
    module = load_module()

    module.validate_threshold_decision_rows([valid_threshold_row()])


def test_applied_threshold_requires_approved_by():
    module = load_module()
    row = valid_threshold_row()
    row["applied"] = "true"
    row["approved_by"] = ""

    with pytest.raises(module.QCPolicyError, match="approved_by"):
        module.validate_threshold_decision_rows([row])


def test_guessed_threshold_source_is_rejected():
    module = load_module()
    row = valid_threshold_row()
    row["threshold_source"] = "guessed"

    with pytest.raises(module.QCPolicyError, match="guessed"):
        module.validate_threshold_decision_rows([row])


def test_audit_status_is_required_for_threshold_rows():
    module = load_module()
    row = valid_threshold_row()
    row["audit_status"] = ""

    with pytest.raises(module.QCPolicyError, match="audit_status"):
        module.validate_threshold_decision_rows([row])


def test_qc_utility_does_not_import_processing_or_modeling_libraries():
    source = MODULE_PATH.read_text().lower()
    forbidden_fragments = [
        "import scanpy",
        "import anndata",
        "from scanpy",
        "from anndata",
        "sklearn",
        "torch",
        "tensorflow",
        "xgboost",
        "lightgbm",
        "requests",
        "urllib",
        "socket",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in source
