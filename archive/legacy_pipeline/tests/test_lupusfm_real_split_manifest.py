import pytest

from lupusfm.evaluation.real_split_manifest import (
    STAGE4_CURRENT_FEATURE,
    RealDonorSplitRecord,
    RealLeakageSafeSplitManifest,
    RealSplitManifestValidationError,
    real_leakage_safe_split_manifest_from_mapping,
    real_leakage_safe_split_manifest_to_dict,
    split_manifest_summary,
    validate_real_leakage_safe_split_manifest,
)


def _records():
    return (
        RealDonorSplitRecord("FLARE001", "train", "flare_like"),
        RealDonorSplitRecord("HC-002", "validation", "healthy_hc_like"),
        RealDonorSplitRecord("12345", "test", "managed_sle_numeric_like"),
    )


def _manifest(**overrides):
    values = {
        "records": _records(),
        "current_feature": STAGE4_CURRENT_FEATURE,
        "manifest_status": "pending",
        "split_level": "donor",
        "expected_donor_count": 3,
        "notes": "  split manifest only  ",
    }
    values.update(overrides)
    return RealLeakageSafeSplitManifest(**values)


def test_real_split_manifest_accepts_donor_level_records():
    validated = validate_real_leakage_safe_split_manifest(_manifest())

    assert validated.current_feature == "STAGE4-F003"
    assert validated.manifest_status == "pending"
    assert validated.split_level == "donor"
    assert validated.expected_donor_count == 3
    assert [record.donor_id for record in validated.records] == [
        "FLARE001",
        "HC-002",
        "12345",
    ]
    assert [record.split for record in validated.records] == [
        "train",
        "validation",
        "test",
    ]
    assert validated.allow_cell_level_splits is False
    assert validated.allow_duplicate_donors_across_splits is False
    assert validated.allow_npy_payload_loading is False
    assert validated.allow_embedding_vector_parsing is False
    assert validated.allow_real_aggregation_execution is False
    assert validated.allow_model_fitting is False
    assert validated.allow_metric_computation is False
    assert validated.allow_modeling is False
    assert validated.performance_claims_added is False
    assert validated.notes == "split manifest only"


def test_real_split_manifest_from_mapping_normalizes_records_and_metadata():
    manifest = real_leakage_safe_split_manifest_from_mapping(
        {
            "records": [
                {"donor_id": " FLARE001 ", "split": "train", "label_group": "flare_like"},
                {
                    "donor_id": " HC-002 ",
                    "split": "validation",
                    "label_group": "healthy_hc_like",
                },
                {
                    "donor_id": " 12345 ",
                    "split": "test",
                    "label_group": "managed_sle_numeric_like",
                },
            ],
            "manifest_status": "validated",
            "expected_donor_count": "3",
            "notes": "  normalized  ",
        }
    )

    assert manifest.current_feature == "STAGE4-F003"
    assert manifest.manifest_status == "validated"
    assert manifest.expected_donor_count == 3
    assert manifest.records[0].donor_id == "FLARE001"
    assert manifest.notes == "normalized"


def test_real_split_manifest_treats_patient_split_level_as_donor_level():
    validated = validate_real_leakage_safe_split_manifest(
        _manifest(split_level="patient")
    )

    assert validated.split_level == "donor"


def test_real_split_manifest_rejects_wrong_current_feature():
    with pytest.raises(RealSplitManifestValidationError, match="current_feature"):
        validate_real_leakage_safe_split_manifest(
            _manifest(current_feature="STAGE4-F002")
        )


def test_real_split_manifest_rejects_cell_level_splits():
    with pytest.raises(RealSplitManifestValidationError, match="split_level"):
        validate_real_leakage_safe_split_manifest(_manifest(split_level="cell"))


def test_real_split_manifest_rejects_cell_level_column_names():
    with pytest.raises(RealSplitManifestValidationError, match="cell-level"):
        validate_real_leakage_safe_split_manifest(_manifest(donor_id_column="cell_id"))


def test_real_split_manifest_rejects_duplicate_donor_ids():
    with pytest.raises(RealSplitManifestValidationError, match="donor_id values"):
        validate_real_leakage_safe_split_manifest(
            _manifest(
                records=(
                    RealDonorSplitRecord("d1", "train", "flare_like"),
                    RealDonorSplitRecord("d1", "validation", "healthy_hc_like"),
                    RealDonorSplitRecord("d2", "test", "managed_sle_numeric_like"),
                ),
                expected_donor_count=3,
            )
        )


def test_real_split_manifest_rejects_missing_required_split():
    with pytest.raises(RealSplitManifestValidationError, match="required splits"):
        validate_real_leakage_safe_split_manifest(
            _manifest(
                records=(
                    RealDonorSplitRecord("d1", "train", "flare_like"),
                    RealDonorSplitRecord("d2", "validation", "healthy_hc_like"),
                ),
                expected_donor_count=2,
            )
        )


def test_real_split_manifest_rejects_expected_count_mismatch():
    with pytest.raises(RealSplitManifestValidationError, match="expected_donor_count"):
        validate_real_leakage_safe_split_manifest(_manifest(expected_donor_count=4))


@pytest.mark.parametrize(
    "bad_record",
    [
        {"donor_id": "", "split": "train", "label_group": "flare_like"},
        {"donor_id": "d1", "split": "bad_split", "label_group": "flare_like"},
        {"donor_id": "d1", "split": "train", "label_group": "bad_label"},
    ],
)
def test_real_split_manifest_rejects_invalid_records(bad_record):
    with pytest.raises(RealSplitManifestValidationError):
        real_leakage_safe_split_manifest_from_mapping(
            {
                "records": [
                    bad_record,
                    {"donor_id": "d2", "split": "validation", "label_group": "healthy_hc_like"},
                    {
                        "donor_id": "d3",
                        "split": "test",
                        "label_group": "managed_sle_numeric_like",
                    },
                ],
                "expected_donor_count": 3,
            }
        )


@pytest.mark.parametrize(
    "flag_name",
    [
        "allow_cell_level_splits",
        "allow_duplicate_donors_across_splits",
        "allow_real_artifact_loading",
        "allow_npy_payload_loading",
        "allow_embedding_vector_parsing",
        "allow_real_aggregation_execution",
        "allow_anndata_loading",
        "allow_geneformer_execution",
        "allow_tokenizer_execution",
        "allow_embedding_extraction",
        "allow_feature_extraction",
        "allow_global_preprocessing",
        "allow_scaler_outside_fold",
        "allow_model_fitting",
        "allow_metric_computation",
        "allow_modeling",
        "allow_training",
        "allow_external_validation",
        "performance_claims_added",
    ],
)
def test_real_split_manifest_keeps_forbidden_flags_disabled(flag_name):
    with pytest.raises(RealSplitManifestValidationError):
        validate_real_leakage_safe_split_manifest(_manifest(**{flag_name: True}))


def test_split_manifest_summary_counts_splits_and_labels_without_metrics():
    summary = split_manifest_summary(_manifest())

    assert summary == {
        "current_feature": "STAGE4-F003",
        "manifest_status": "pending",
        "split_level": "donor",
        "n_donors": 3,
        "split_counts": {"test": 1, "train": 1, "validation": 1},
        "label_group_counts": {
            "flare_like": 1,
            "healthy_hc_like": 1,
            "managed_sle_numeric_like": 1,
        },
        "allow_modeling": False,
        "allow_metric_computation": False,
        "performance_claims_added": False,
    }


def test_real_split_manifest_to_dict_validates_before_serializing():
    serialized = real_leakage_safe_split_manifest_to_dict(_manifest())

    assert serialized["current_feature"] == "STAGE4-F003"
    assert serialized["records"][0]["donor_id"] == "FLARE001"
    assert serialized["allow_npy_payload_loading"] is False
    assert serialized["allow_modeling"] is False
    assert serialized["performance_claims_added"] is False


def test_real_split_manifest_module_has_no_runtime_or_modeling_imports():
    import lupusfm.evaluation.real_split_manifest as split_module

    source = split_module.__loader__.get_source(split_module.__name__).lower()
    forbidden_fragments = [
        "import sklearn",
        "from sklearn",
        "import pandas",
        "import numpy",
        "import scanpy",
        "import anndata",
        "import torch",
        "import tensorflow",
        "import geneformer",
        "from geneformer",
        "read_h5ad",
        "read_parquet",
        "np.load",
        ".fit(",
        ".predict(",
    ]

    assert not any(fragment in source for fragment in forbidden_fragments)
