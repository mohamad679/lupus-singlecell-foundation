import csv
import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = REPO_ROOT / "metadata" / "gene_identifier_policy.yaml"
REPORT_PATH = REPO_ROOT / "reports" / "tables" / "gene_mapping_report.csv"
MODULE_PATH = REPO_ROOT / "src" / "data" / "gene_identifier_policy.py"
STATE_PATH = REPO_ROOT / "state" / "project_state.yaml"

REQUIRED_REPORT_HEADERS = [
    "source_dataset",
    "gene_id",
    "gene_symbol",
    "ensembl_id",
    "mapping_status",
    "mapping_method",
    "duplicate_flag",
    "unmapped_flag",
    "foundation_vocab_match",
    "pathway_eligible",
    "notes",
    "audit_status",
]


def load_module():
    spec = importlib.util.spec_from_file_location("gene_identifier_policy", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def mock_gene_rows():
    return [
        {
            "gene_id": "ENSG000001",
            "gene_symbol": "GENE1",
            "ensembl_id": "ENSG000001",
            "feature_type": "Gene Expression",
            "genome": "GRCh38",
            "source_dataset": "GSE137029",
        },
        {
            "gene_id": "ENSG000002",
            "gene_symbol": "GENE2",
            "ensembl_id": "ENSG000002",
            "feature_type": "Gene Expression",
            "genome": "GRCh38",
            "source_dataset": "GSE137029",
        },
    ]


def test_gene_identifier_policy_yaml_exists():
    assert POLICY_PATH.exists()


def test_required_policy_rules_exist_and_are_strict():
    module = load_module()
    policy = module.load_gene_identifier_policy(POLICY_PATH)
    rules = policy["policy_rules"]

    assert rules["preserve_original_gene_ids"] is True
    assert rules["preserve_original_gene_symbols"] is True
    assert rules["require_unique_var_index"] is True
    assert rules["forbid_silent_gene_drop"] is True
    assert rules["forbid_silent_duplicate_collapse"] is True
    assert rules["require_mapping_report"] is True
    assert rules["require_unmapped_gene_report"] is True
    assert rules["require_duplicate_gene_report"] is True
    assert rules["allowed_unknown_value"] == "TODO"


def test_foundation_model_requirements_are_present():
    module = load_module()
    policy = module.load_gene_identifier_policy(POLICY_PATH)
    requirements = policy["foundation_model_requirements"]

    assert requirements["track_gene_vocabulary_overlap"] is True
    assert requirements["require_model_vocab_version"] is True
    assert requirements["require_unmatched_vocab_report"] is True


def test_pathway_requirements_are_present():
    module = load_module()
    policy = module.load_gene_identifier_policy(POLICY_PATH)
    requirements = policy["pathway_analysis_requirements"]

    assert requirements["require_valid_gene_symbols"] is True
    assert requirements["require_multiple_testing_correction_later"] is True
    assert requirements["forbid_pathway_claims_without_mapping"] is True


def test_gene_mapping_report_exists_with_required_headers_only():
    assert REPORT_PATH.exists()
    with REPORT_PATH.open(newline="") as handle:
        rows = list(csv.reader(handle))

    assert rows == [REQUIRED_REPORT_HEADERS]


def test_duplicate_gene_symbols_are_detected_on_mock_data():
    module = load_module()

    duplicates = module.detect_duplicate_gene_symbols(["GENE1", "GENE2", "GENE1"])

    assert duplicates == ["GENE1"]


def test_valid_mock_gene_table_passes():
    module = load_module()
    policy = module.load_gene_identifier_policy(POLICY_PATH)

    module.validate_gene_table_schema(mock_gene_rows(), policy)


def test_missing_required_gene_fields_fail():
    module = load_module()
    policy = module.load_gene_identifier_policy(POLICY_PATH)
    rows = mock_gene_rows()
    rows[0].pop("ensembl_id")
    rows[1].pop("ensembl_id")

    with pytest.raises(module.GeneIdentifierPolicyError, match="ensembl_id"):
        module.validate_gene_table_schema(rows, policy)


def test_mapping_status_summary_uses_mock_rows_only():
    module = load_module()
    rows = [
        {
            "mapping_status": "mapped",
            "duplicate_flag": "false",
            "unmapped_flag": "false",
            "foundation_vocab_match": "true",
            "pathway_eligible": "true",
        },
        {
            "mapping_status": "unmapped",
            "duplicate_flag": "true",
            "unmapped_flag": "true",
            "foundation_vocab_match": "false",
            "pathway_eligible": "false",
        },
    ]

    assert module.summarize_gene_mapping_status(rows) == {
        "total_rows": 2,
        "mapped_rows": 1,
        "unmapped_rows": 1,
        "duplicate_rows": 1,
        "foundation_vocab_matches": 1,
        "pathway_eligible_rows": 1,
    }


def test_no_download_or_modeling_flags_changed():
    state = STATE_PATH.read_text()

    assert "current_feature: P3-F007" in state
    assert "selected_datasets: []" in state
    assert "external_validation_cohort: TODO" in state
    assert "modeling_allowed: false" in state
    assert "allow_modeling: false" in state
    assert "dataset_download_allowed: false" in state
    assert "allow_downloads: false" in state


def test_gene_identifier_utility_does_not_import_processing_or_modeling_libraries():
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
