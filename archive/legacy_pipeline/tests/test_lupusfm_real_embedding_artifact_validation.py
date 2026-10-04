import hashlib

import pytest

from lupusfm.data.manifest import (
    PRIMARY_CELLXGENE_CENSUS_VERSION,
    PRIMARY_CELLXGENE_DATASET_ID,
)
from lupusfm.data.metadata import DEFAULT_DONOR_COLUMN
from lupusfm.embeddings.artifact_schema import DEFAULT_EMBEDDING_DIMENSION
from lupusfm.embeddings.real_artifact_validation import (
    STAGE4_CURRENT_FEATURE,
    RealEmbeddingArtifactManifest,
    RealEmbeddingArtifactValidationError,
    collect_artifact_filesystem_metadata,
    collect_embedding_directory_metadata,
    real_embedding_artifact_manifest_from_mapping,
    real_embedding_artifact_manifest_to_dict,
    validate_real_embedding_artifact_manifest,
)


def _valid_manifest(**overrides):
    values = {
        "local_artifact_path": "/tmp/lupusfm/local_embeddings.parquet",
        "dataset_id": PRIMARY_CELLXGENE_DATASET_ID,
        "census_version": PRIMARY_CELLXGENE_CENSUS_VERSION,
        "current_feature": STAGE4_CURRENT_FEATURE,
        "artifact_format": "parquet",
        "record_level": "cell",
        "split_level": "patient",
        "donor_id_column": DEFAULT_DONOR_COLUMN,
        "cell_id_column": "cell_id",
        "sampled_cell_id_column": None,
        "embedding_dimension": DEFAULT_EMBEDDING_DIMENSION,
        "declared_columns": ("donor_id", "cell_id", "embedding"),
        "notes": "  local manifest only  ",
    }
    values.update(overrides)
    return RealEmbeddingArtifactManifest(**values)


def test_real_embedding_artifact_manifest_accepts_safe_stage4_contract():
    manifest = _valid_manifest(
        size_bytes="314572800",
        sha256="a" * 64,
        hash_algorithm="sha256",
    )

    validated = validate_real_embedding_artifact_manifest(manifest)

    assert validated.current_feature == "STAGE4-F001"
    assert validated.dataset_id == PRIMARY_CELLXGENE_DATASET_ID
    assert validated.census_version == PRIMARY_CELLXGENE_CENSUS_VERSION
    assert validated.local_artifact_path == "/tmp/lupusfm/local_embeddings.parquet"
    assert validated.size_bytes == 314572800
    assert validated.sha256 == "a" * 64
    assert validated.hash_algorithm == "sha256"
    assert validated.artifact_commit_allowed is False
    assert validated.commit_real_artifact is False
    assert validated.allow_file_metadata_inspection is True
    assert validated.allow_header_inspection is False
    assert validated.allow_anndata_loading is False
    assert validated.allow_geneformer_execution is False
    assert validated.allow_tokenizer_execution is False
    assert validated.allow_embedding_extraction is False
    assert validated.allow_embedding_table_parsing is False
    assert validated.allow_model_fitting is False
    assert validated.allow_metric_computation is False
    assert validated.allow_modeling is False
    assert validated.allow_training is False
    assert validated.performance_claims_added is False
    assert validated.notes == "local manifest only"


def test_real_embedding_artifact_manifest_from_mapping_normalizes_values():
    manifest = real_embedding_artifact_manifest_from_mapping(
        {
            "local_artifact_path": " /tmp/lupusfm/artifact.npz ",
            "artifact_format": "npz",
            "record_level": "donor",
            "split_level": "donor",
            "cell_id_column": None,
            "declared_columns": [" donor_id ", " embedding "],
            "validation_status": "validated",
        }
    )

    assert manifest.local_artifact_path == "/tmp/lupusfm/artifact.npz"
    assert manifest.artifact_format == "npz"
    assert manifest.record_level == "donor"
    assert manifest.split_level == "donor"
    assert manifest.cell_id_column is None
    assert manifest.declared_columns == ("donor_id", "embedding")
    assert manifest.validation_status == "validated"


def test_real_embedding_artifact_manifest_accepts_npy_directory_contract():
    manifest = real_embedding_artifact_manifest_from_mapping(
        {
            "local_artifact_path": " /tmp/lupusfm/all_embeddings ",
            "artifact_format": "npy_directory",
            "artifact_layout": "directory",
            "directory_file_suffix": ".npy",
            "record_level": "donor",
            "split_level": "donor",
            "cell_id_column": None,
            "declared_columns": [" donor_id ", " embedding "],
            "expected_file_count": "261",
            "observed_file_count": "261",
            "total_size_bytes": "360839808",
            "min_file_size_bytes": "1382528",
            "max_file_size_bytes": "1382528",
            "all_files_same_size": "true",
            "validation_status": "validated",
        }
    )

    assert manifest.local_artifact_path == "/tmp/lupusfm/all_embeddings"
    assert manifest.artifact_format == "npy_directory"
    assert manifest.artifact_layout == "directory"
    assert manifest.directory_file_suffix == ".npy"
    assert manifest.record_level == "donor"
    assert manifest.split_level == "donor"
    assert manifest.expected_file_count == 261
    assert manifest.observed_file_count == 261
    assert manifest.total_size_bytes == 360839808
    assert manifest.min_file_size_bytes == 1382528
    assert manifest.max_file_size_bytes == 1382528
    assert manifest.all_files_same_size is True


def test_real_embedding_artifact_manifest_rejects_npy_directory_single_file_layout():
    with pytest.raises(
        RealEmbeddingArtifactValidationError,
        match="npy_directory artifacts must use directory layout",
    ):
        validate_real_embedding_artifact_manifest(
            _valid_manifest(
                artifact_format="npy_directory",
                artifact_layout="single_file",
                record_level="donor",
                split_level="donor",
                cell_id_column=None,
            )
        )


def test_real_embedding_artifact_manifest_rejects_npy_directory_cell_record_level():
    with pytest.raises(
        RealEmbeddingArtifactValidationError,
        match="donor-level files",
    ):
        validate_real_embedding_artifact_manifest(
            _valid_manifest(
                artifact_format="npy_directory",
                artifact_layout="directory",
                record_level="cell",
            )
        )


def test_real_embedding_artifact_manifest_requires_primary_dataset_contract():
    with pytest.raises(
        RealEmbeddingArtifactValidationError,
        match="approved primary CELLxGENE contract",
    ):
        validate_real_embedding_artifact_manifest(
            _valid_manifest(dataset_id="other-dataset")
        )


def test_real_embedding_artifact_manifest_rejects_cell_level_split():
    with pytest.raises(
        RealEmbeddingArtifactValidationError,
        match="split_level must be one of",
    ):
        validate_real_embedding_artifact_manifest(_valid_manifest(split_level="cell"))


def test_real_embedding_artifact_manifest_requires_cell_id_for_cell_records():
    with pytest.raises(
        RealEmbeddingArtifactValidationError,
        match="cell-level artifacts require",
    ):
        validate_real_embedding_artifact_manifest(
            _valid_manifest(cell_id_column=None, sampled_cell_id_column=None)
        )


def test_real_embedding_artifact_manifest_rejects_model_artifact_like_path():
    with pytest.raises(
        RealEmbeddingArtifactValidationError,
        match="model/training artifact-like",
    ):
        validate_real_embedding_artifact_manifest(
            _valid_manifest(local_artifact_path="/tmp/lupusfm/model.pt")
        )


def test_real_embedding_artifact_manifest_rejects_declared_split_prediction_metrics():
    with pytest.raises(
        RealEmbeddingArtifactValidationError,
        match="declared_columns must not include",
    ):
        validate_real_embedding_artifact_manifest(
            _valid_manifest(declared_columns=("donor_id", "embedding", "auroc"))
        )


def test_real_embedding_artifact_manifest_rejects_invalid_sha256():
    with pytest.raises(
        RealEmbeddingArtifactValidationError,
        match="64-character hexadecimal",
    ):
        validate_real_embedding_artifact_manifest(_valid_manifest(sha256="not-a-hash"))


@pytest.mark.parametrize(
    "flag_name",
    [
        "artifact_commit_allowed",
        "commit_real_artifact",
        "contains_model_artifact",
        "contains_training_artifact",
        "contains_split_columns",
        "contains_predictions",
        "contains_performance_metrics",
        "allow_header_inspection",
        "allow_anndata_loading",
        "allow_geneformer_execution",
        "allow_tokenizer_execution",
        "allow_embedding_extraction",
        "allow_embedding_table_parsing",
        "allow_aggregation",
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
def test_real_embedding_artifact_manifest_keeps_forbidden_flags_disabled(flag_name):
    with pytest.raises(RealEmbeddingArtifactValidationError):
        validate_real_embedding_artifact_manifest(_valid_manifest(**{flag_name: True}))


def test_real_embedding_artifact_manifest_to_dict_validates_before_serializing():
    serialized = real_embedding_artifact_manifest_to_dict(_valid_manifest())

    assert serialized["current_feature"] == "STAGE4-F001"
    assert serialized["artifact_commit_allowed"] is False
    assert serialized["allow_modeling"] is False
    assert serialized["performance_claims_added"] is False


def test_collect_artifact_filesystem_metadata_checks_file_size_and_checksum(tmp_path):
    artifact = tmp_path / "local_embeddings.parquet"
    payload = b"safe filesystem metadata only"
    artifact.write_bytes(payload)

    metadata = collect_artifact_filesystem_metadata(
        str(artifact),
        compute_sha256=True,
    )

    assert metadata.local_artifact_path == str(artifact)
    assert metadata.exists is True
    assert metadata.is_file is True
    assert metadata.is_dir is False
    assert metadata.size_bytes == len(payload)
    assert metadata.sha256 == hashlib.sha256(payload).hexdigest()
    assert metadata.hash_algorithm == "sha256"


def test_collect_artifact_filesystem_metadata_reports_missing_path(tmp_path):
    artifact = tmp_path / "missing_embeddings.parquet"

    metadata = collect_artifact_filesystem_metadata(str(artifact))

    assert metadata.exists is False
    assert metadata.is_file is False
    assert metadata.is_dir is False
    assert metadata.size_bytes is None
    assert metadata.sha256 is None


def test_collect_artifact_filesystem_metadata_rejects_checksum_for_missing_path(tmp_path):
    artifact = tmp_path / "missing_embeddings.parquet"

    with pytest.raises(
        RealEmbeddingArtifactValidationError,
        match="existing regular file",
    ):
        collect_artifact_filesystem_metadata(str(artifact), compute_sha256=True)


def test_collect_embedding_directory_metadata_counts_npy_files_without_loading(tmp_path):
    directory = tmp_path / "all_embeddings"
    directory.mkdir()

    payload = b"metadata only"
    for name in ["FLARE001.npy", "HC-002.npy", "IGTB1290.npy", "1004.npy"]:
        (directory / name).write_bytes(payload)
    (directory / "README.txt").write_text("not an embedding")

    metadata = collect_embedding_directory_metadata(str(directory))

    assert metadata.local_artifact_path == str(directory)
    assert metadata.exists is True
    assert metadata.is_dir is True
    assert metadata.file_suffix == ".npy"
    assert metadata.total_top_level_files == 5
    assert metadata.embedding_files == 4
    assert metadata.non_embedding_files == 1
    assert metadata.total_embedding_size_bytes == len(payload) * 4
    assert metadata.min_embedding_file_size_bytes == len(payload)
    assert metadata.max_embedding_file_size_bytes == len(payload)
    assert metadata.all_embedding_files_same_size is True
    assert dict(metadata.filename_category_counts) == {
        "flare_like": 1,
        "healthy_hc_like": 1,
        "healthy_igtb_like": 1,
        "managed_sle_numeric_like": 1,
    }


def test_collect_embedding_directory_metadata_reports_missing_directory(tmp_path):
    directory = tmp_path / "missing_embeddings"

    metadata = collect_embedding_directory_metadata(str(directory))

    assert metadata.exists is False
    assert metadata.is_dir is False
    assert metadata.embedding_files == 0
    assert metadata.total_embedding_size_bytes == 0


def test_collect_embedding_directory_metadata_rejects_regular_file(tmp_path):
    artifact = tmp_path / "artifact.npy"
    artifact.write_bytes(b"metadata only")

    with pytest.raises(
        RealEmbeddingArtifactValidationError,
        match="existing directory",
    ):
        collect_embedding_directory_metadata(str(artifact))


def test_real_artifact_validation_module_has_no_modeling_or_loading_imports():
    import lupusfm.embeddings.real_artifact_validation as validation_module

    source = validation_module.__loader__.get_source(
        validation_module.__name__,
    ).lower()
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
