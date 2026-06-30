import pytest

from lupusfm.data.manifest import (
    PRIMARY_CELLXGENE_CENSUS_VERSION,
    PRIMARY_CELLXGENE_DATASET_ID,
)
from lupusfm.data.metadata import DEFAULT_DONOR_COLUMN
from lupusfm.embeddings.artifact_schema import (
    DEFAULT_EMBEDDING_DIMENSION,
    EmbeddingArtifactPaths,
    EmbeddingArtifactSchema,
    EmbeddingArtifactSchemaError,
    embedding_artifact_schema_from_mapping,
    embedding_artifact_schema_to_dict,
    validate_embedding_artifact_schema,
)


def _valid_paths(**overrides):
    values = {
        "artifact": "outputs/stage3/embeddings.parquet",
        "metadata": "outputs/stage3/embeddings.metadata.json",
        "extraction_config": "outputs/stage2/embedding_config.json",
        "provenance": "outputs/stage2/embedding_provenance.json",
    }
    values.update(overrides)
    return EmbeddingArtifactPaths(**values)


def _valid_schema(**overrides):
    values = {
        "dataset_id": PRIMARY_CELLXGENE_DATASET_ID,
        "source": "CELLxGENE Census",
        "census_version": PRIMARY_CELLXGENE_CENSUS_VERSION,
        "donor_id_column": DEFAULT_DONOR_COLUMN,
        "cell_id_column": "cell_id",
        "sampled_cell_id_column": None,
        "embedding_column": "embedding",
        "embedding_dimension": DEFAULT_EMBEDDING_DIMENSION,
        "embedding_source": "frozen_geneformer_feature_extractor",
        "artifact_format": "parquet",
        "record_level": "cell",
        "split_level": "patient",
        "model_provenance_reference": "outputs/stage2/embedding_provenance.json",
        "extraction_config_reference": "outputs/stage2/embedding_config.json",
        "paths": _valid_paths(),
    }
    values.update(overrides)
    return EmbeddingArtifactSchema(**values)


def test_embedding_artifact_schema_accepts_metadata_only_contract():
    schema = _valid_schema(
        cell_id_column=" cell_id ",
        sampled_cell_id_column=" sampled_cell_id ",
        embedding_dimension="1152",
        notes="  metadata only  ",
    )

    validated = validate_embedding_artifact_schema(schema)

    assert validated.dataset_id == PRIMARY_CELLXGENE_DATASET_ID
    assert validated.cell_id_column == "cell_id"
    assert validated.sampled_cell_id_column == "sampled_cell_id"
    assert validated.embedding_dimension == 1152
    assert validated.split_level == "patient"
    assert validated.allow_modeling is False
    assert validated.allow_training is False
    assert validated.performance_claims_added is False
    assert validated.notes == "metadata only"


def test_embedding_artifact_schema_requires_primary_dataset_contract():
    schema = _valid_schema(dataset_id="other-dataset")

    with pytest.raises(
        EmbeddingArtifactSchemaError,
        match="approved primary CELLxGENE contract",
    ):
        validate_embedding_artifact_schema(schema)


def test_embedding_artifact_schema_requires_primary_census_version():
    schema = _valid_schema(census_version="2020-01-01")

    with pytest.raises(
        EmbeddingArtifactSchemaError,
        match="approved primary CELLxGENE contract",
    ):
        validate_embedding_artifact_schema(schema)


def test_embedding_artifact_schema_requires_cell_or_sampled_cell_identifier():
    schema = _valid_schema(cell_id_column=" ", sampled_cell_id_column=None)

    with pytest.raises(
        EmbeddingArtifactSchemaError,
        match="At least one of cell_id_column or sampled_cell_id_column",
    ):
        validate_embedding_artifact_schema(schema)


def test_embedding_artifact_schema_rejects_cell_level_split():
    schema = _valid_schema(split_level="cell")

    with pytest.raises(
        EmbeddingArtifactSchemaError,
        match="split_level must be one of",
    ):
        validate_embedding_artifact_schema(schema)


def test_embedding_artifact_schema_rejects_unknown_artifact_format():
    schema = _valid_schema(artifact_format="pickle")

    with pytest.raises(
        EmbeddingArtifactSchemaError,
        match="artifact_format must be one of",
    ):
        validate_embedding_artifact_schema(schema)


def test_embedding_artifact_schema_rejects_non_positive_embedding_dimension():
    schema = _valid_schema(embedding_dimension=0)

    with pytest.raises(
        EmbeddingArtifactSchemaError,
        match="embedding_dimension must be positive",
    ):
        validate_embedding_artifact_schema(schema)


def test_embedding_artifact_schema_rejects_model_artifact_like_paths():
    schema = _valid_schema(paths=_valid_paths(artifact="outputs/embeddings.pt"))

    with pytest.raises(
        EmbeddingArtifactSchemaError,
        match="model/training artifact-like output",
    ):
        validate_embedding_artifact_schema(schema)


@pytest.mark.parametrize(
    "flag_name",
    [
        "contains_model_artifact",
        "contains_training_artifact",
        "allow_modeling",
        "allow_training",
        "allow_external_validation",
        "performance_claims_added",
    ],
)
def test_embedding_artifact_schema_keeps_forbidden_flags_disabled(flag_name):
    schema = _valid_schema(**{flag_name: True})

    with pytest.raises(EmbeddingArtifactSchemaError):
        validate_embedding_artifact_schema(schema)


def test_embedding_artifact_schema_from_mapping_normalizes_nested_paths():
    schema = embedding_artifact_schema_from_mapping(
        {
            "dataset_id": PRIMARY_CELLXGENE_DATASET_ID,
            "source": "CELLxGENE Census",
            "census_version": PRIMARY_CELLXGENE_CENSUS_VERSION,
            "donor_id_column": DEFAULT_DONOR_COLUMN,
            "cell_id_column": None,
            "sampled_cell_id_column": " sampled_cell_id ",
            "embedding_column": " embedding ",
            "embedding_dimension": "1152",
            "embedding_source": " frozen_geneformer_feature_extractor ",
            "artifact_format": "parquet",
            "record_level": "cell",
            "split_level": "donor",
            "model_provenance_reference": " outputs/stage2/provenance.json ",
            "extraction_config_reference": " outputs/stage2/config.json ",
            "paths": {
                "artifact": " outputs/stage3/embeddings.parquet ",
                "metadata": " outputs/stage3/embeddings.metadata.json ",
                "extraction_config": " outputs/stage2/config.json ",
                "provenance": " outputs/stage2/provenance.json ",
            },
        }
    )

    assert schema.sampled_cell_id_column == "sampled_cell_id"
    assert schema.embedding_column == "embedding"
    assert schema.embedding_dimension == 1152
    assert schema.split_level == "donor"
    assert schema.paths.artifact == "outputs/stage3/embeddings.parquet"


def test_embedding_artifact_schema_to_dict_validates_before_serializing():
    serialized = embedding_artifact_schema_to_dict(_valid_schema())

    assert serialized["dataset_id"] == PRIMARY_CELLXGENE_DATASET_ID
    assert serialized["paths"]["artifact"] == "outputs/stage3/embeddings.parquet"
