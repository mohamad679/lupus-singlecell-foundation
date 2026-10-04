import inspect

import pytest

import lupusfm.embeddings.config as config_module
from lupusfm.data.manifest import (
    DEFAULT_RANDOM_SEED,
    PRIMARY_CELLXGENE_CENSUS_VERSION,
    PRIMARY_CELLXGENE_DATASET_ID,
    IngestionManifest,
    ManifestOutputPaths,
    make_primary_cellxgene_ingestion_manifest,
)
from lupusfm.embeddings.config import (
    DEFAULT_BATCH_SIZE,
    DEFAULT_CELLS_PER_DONOR,
    DEFAULT_GENEFORMER_MODEL,
    DEFAULT_MAX_SEQUENCE_LENGTH,
    DEFAULT_PATIENT_AGGREGATION,
    EmbeddingConfigError,
    EmbeddingExtractionConfig,
    EmbeddingOutputPaths,
    embedding_config_to_dict,
    make_embedding_config_from_mapping,
    make_primary_cellxgene_embedding_config,
    validate_embedding_config,
    validate_embedding_config_against_manifest,
)


def valid_output_paths():
    return EmbeddingOutputPaths(
        root="artifacts/stage2/embeddings",
        config="artifacts/stage2/embeddings/embedding_config.json",
        provenance="artifacts/stage2/embeddings/embedding_provenance.json",
        embeddings="artifacts/stage2/embeddings/patient_embeddings",
        sampled_cell_ids="artifacts/stage2/embeddings/sampled_cell_ids.json",
    )


def valid_config():
    return EmbeddingExtractionConfig(
        dataset_id=PRIMARY_CELLXGENE_DATASET_ID,
        source="CELLxGENE Census",
        census_version=PRIMARY_CELLXGENE_CENSUS_VERSION,
        donor_column="donor_id",
        gene_symbol_column="gene_symbol",
        gene_id_policy="explicit_gene_symbol_to_ensembl_mapping",
        ingestion_manifest_path="artifacts/stage1/ingestion_manifest.json",
        model_name_or_path=DEFAULT_GENEFORMER_MODEL,
        model_revision="main",
        tokenizer_name_or_path="ctheodoris/Geneformer",
        vocabulary_source="ctheodoris/Geneformer/token_dictionary.pkl",
        cells_per_donor=300,
        max_sequence_length=1024,
        batch_size=16,
        random_seed=42,
        split_level="patient",
        patient_aggregation="mean_pool_per_donor",
        output_paths=valid_output_paths(),
        notes="test config",
    )


def test_validate_embedding_config_accepts_valid_config():
    config = validate_embedding_config(valid_config())

    assert config.dataset_id == PRIMARY_CELLXGENE_DATASET_ID
    assert config.census_version == PRIMARY_CELLXGENE_CENSUS_VERSION
    assert config.donor_column == "donor_id"
    assert config.gene_symbol_column == "gene_symbol"
    assert config.allow_downloads is False
    assert config.allow_anndata_loading is False
    assert config.allow_geneformer_execution is False
    assert config.allow_embedding_extraction is False
    assert config.allow_modeling is False
    assert config.allow_training is False
    assert config.allow_external_validation is False


@pytest.mark.parametrize(
    "field_name",
    [
        "source",
        "donor_column",
        "gene_symbol_column",
        "ingestion_manifest_path",
        "model_name_or_path",
        "model_revision",
        "tokenizer_name_or_path",
        "vocabulary_source",
    ],
)
def test_validate_embedding_config_rejects_empty_required_strings(field_name):
    values = valid_config().__dict__.copy()
    values[field_name] = "   "

    with pytest.raises(EmbeddingConfigError, match=field_name):
        validate_embedding_config(EmbeddingExtractionConfig(**values))


def test_validate_embedding_config_requires_primary_dataset_id():
    values = valid_config().__dict__.copy()
    values["dataset_id"] = "other-dataset"

    with pytest.raises(EmbeddingConfigError, match="dataset_id"):
        validate_embedding_config(EmbeddingExtractionConfig(**values))


def test_validate_embedding_config_requires_primary_census_version():
    values = valid_config().__dict__.copy()
    values["census_version"] = "2024-01-01"

    with pytest.raises(EmbeddingConfigError, match="census_version"):
        validate_embedding_config(EmbeddingExtractionConfig(**values))


@pytest.mark.parametrize(
    ("field_name", "bad_value"),
    [
        ("cells_per_donor", 0),
        ("max_sequence_length", 0),
        ("batch_size", 0),
        ("random_seed", -1),
    ],
)
def test_validate_embedding_config_rejects_bad_counts_and_seed(field_name, bad_value):
    values = valid_config().__dict__.copy()
    values[field_name] = bad_value

    with pytest.raises(EmbeddingConfigError, match=field_name):
        validate_embedding_config(EmbeddingExtractionConfig(**values))


@pytest.mark.parametrize(
    "field_name",
    ["cells_per_donor", "max_sequence_length", "batch_size", "random_seed"],
)
def test_validate_embedding_config_rejects_bool_numeric_fields(field_name):
    values = valid_config().__dict__.copy()
    values[field_name] = True

    with pytest.raises(EmbeddingConfigError, match=field_name):
        validate_embedding_config(EmbeddingExtractionConfig(**values))


@pytest.mark.parametrize(
    "split_level",
    ["cell", "cell_level", "cell_level_split", "random_cell_split"],
)
def test_validate_embedding_config_rejects_cell_level_split(split_level):
    values = valid_config().__dict__.copy()
    values["split_level"] = split_level

    with pytest.raises(EmbeddingConfigError, match="split_level|cell-level"):
        validate_embedding_config(EmbeddingExtractionConfig(**values))


def test_validate_embedding_config_rejects_unknown_gene_id_policy():
    values = valid_config().__dict__.copy()
    values["gene_id_policy"] = "infer_from_var_names"

    with pytest.raises(EmbeddingConfigError, match="gene_id_policy"):
        validate_embedding_config(EmbeddingExtractionConfig(**values))


def test_validate_embedding_config_rejects_unknown_patient_aggregation():
    values = valid_config().__dict__.copy()
    values["patient_aggregation"] = "cell_level_predictions"

    with pytest.raises(EmbeddingConfigError, match="patient_aggregation"):
        validate_embedding_config(EmbeddingExtractionConfig(**values))


@pytest.mark.parametrize(
    "flag_name",
    [
        "allow_downloads",
        "allow_anndata_loading",
        "allow_geneformer_execution",
        "allow_embedding_extraction",
        "allow_modeling",
        "allow_training",
        "allow_external_validation",
    ],
)
def test_validate_embedding_config_keeps_execution_and_modeling_disabled(flag_name):
    values = valid_config().__dict__.copy()
    values[flag_name] = True

    with pytest.raises(EmbeddingConfigError, match="disabled"):
        validate_embedding_config(EmbeddingExtractionConfig(**values))


@pytest.mark.parametrize(
    ("path_field", "bad_path"),
    [
        ("config", "artifacts/stage2/model.pkl"),
        ("provenance", "artifacts/stage2/model.pt"),
        ("embeddings", "artifacts/stage2/model.joblib"),
        ("sampled_cell_ids", "artifacts/stage2/model.ckpt"),
    ],
)
def test_validate_embedding_config_rejects_model_artifact_output_suffixes(
    path_field,
    bad_path,
):
    values = valid_output_paths().__dict__.copy()
    values[path_field] = bad_path
    config_values = valid_config().__dict__.copy()
    config_values["output_paths"] = EmbeddingOutputPaths(**values)

    with pytest.raises(EmbeddingConfigError, match="model/training artifact-like"):
        validate_embedding_config(EmbeddingExtractionConfig(**config_values))


def test_make_primary_cellxgene_embedding_config_is_locked_and_metadata_only():
    config = make_primary_cellxgene_embedding_config()

    assert config.dataset_id == PRIMARY_CELLXGENE_DATASET_ID
    assert config.census_version == PRIMARY_CELLXGENE_CENSUS_VERSION
    assert config.model_name_or_path == DEFAULT_GENEFORMER_MODEL
    assert config.cells_per_donor == DEFAULT_CELLS_PER_DONOR
    assert config.max_sequence_length == DEFAULT_MAX_SEQUENCE_LENGTH
    assert config.batch_size == DEFAULT_BATCH_SIZE
    assert config.random_seed == DEFAULT_RANDOM_SEED
    assert config.patient_aggregation == DEFAULT_PATIENT_AGGREGATION
    assert config.allow_embedding_extraction is False


def test_make_embedding_config_from_mapping_parses_and_validates_values():
    config = make_embedding_config_from_mapping(
        {
            "dataset_id": PRIMARY_CELLXGENE_DATASET_ID,
            "source": "CELLxGENE Census",
            "census_version": PRIMARY_CELLXGENE_CENSUS_VERSION,
            "donor_column": "donor_id",
            "gene_symbol_column": "gene_symbol",
            "gene_id_policy": "explicit_gene_symbol_to_ensembl_mapping",
            "ingestion_manifest_path": "artifacts/stage1/ingestion_manifest.json",
            "model_name_or_path": DEFAULT_GENEFORMER_MODEL,
            "model_revision": "main",
            "tokenizer_name_or_path": "ctheodoris/Geneformer",
            "vocabulary_source": "ctheodoris/Geneformer/token_dictionary.pkl",
            "cells_per_donor": "300",
            "max_sequence_length": "1024",
            "batch_size": "16",
            "random_seed": "42",
            "split_level": "patient",
            "patient_aggregation": "mean_pool_per_donor",
            "output_paths": {
                "root": "artifacts/stage2/embeddings",
                "config": "artifacts/stage2/embeddings/embedding_config.json",
                "provenance": "artifacts/stage2/embeddings/embedding_provenance.json",
                "embeddings": "artifacts/stage2/embeddings/patient_embeddings",
                "sampled_cell_ids": (
                    "artifacts/stage2/embeddings/sampled_cell_ids.json"
                ),
            },
            "allow_downloads": "false",
            "allow_anndata_loading": "false",
            "allow_geneformer_execution": "false",
            "allow_embedding_extraction": "false",
            "allow_modeling": "false",
            "allow_training": "false",
            "allow_external_validation": "false",
        }
    )

    assert config.cells_per_donor == 300
    assert config.max_sequence_length == 1024
    assert config.batch_size == 16
    assert config.random_seed == 42


def test_make_embedding_config_from_mapping_requires_output_paths_mapping():
    with pytest.raises(EmbeddingConfigError, match="output_paths"):
        make_embedding_config_from_mapping({"output_paths": None})


def test_embedding_config_to_dict_serializes_validated_config():
    serialized = embedding_config_to_dict(valid_config())

    assert serialized["dataset_id"] == PRIMARY_CELLXGENE_DATASET_ID
    assert serialized["output_paths"]["config"].endswith("embedding_config.json")
    assert serialized["allow_geneformer_execution"] is False


def test_validate_embedding_config_against_manifest_accepts_matching_manifest():
    validate_embedding_config_against_manifest(
        make_primary_cellxgene_embedding_config(),
        make_primary_cellxgene_ingestion_manifest(),
    )


def test_validate_embedding_config_against_manifest_rejects_mismatch():
    config_values = make_primary_cellxgene_embedding_config().__dict__.copy()
    config_values["random_seed"] = 7
    config = EmbeddingExtractionConfig(**config_values)

    with pytest.raises(EmbeddingConfigError, match="random_seed"):
        validate_embedding_config_against_manifest(
            config,
            make_primary_cellxgene_ingestion_manifest(),
        )


def test_validate_embedding_config_against_manifest_rejects_invalid_manifest():
    manifest = IngestionManifest(
        dataset_id=PRIMARY_CELLXGENE_DATASET_ID,
        source="CELLxGENE Census",
        census_version=PRIMARY_CELLXGENE_CENSUS_VERSION,
        donor_column="donor_id",
        gene_symbol_column="gene_symbol",
        split_column="split_group",
        expected_total_donors=261,
        expected_total_cells=1_263_438,
        random_seed=42,
        output_paths=ManifestOutputPaths(
            root="artifacts/stage1",
            manifest="artifacts/stage1/ingestion_manifest.json",
            readiness_report="artifacts/stage1/ingestion_readiness.json",
            cohort_summary="artifacts/stage1/cohort_summary.json",
        ),
        allow_embedding_extraction=True,
    )

    with pytest.raises(EmbeddingConfigError):
        validate_embedding_config_against_manifest(valid_config(), manifest)


def test_config_module_does_not_import_runtime_embedding_stack():
    source = inspect.getsource(config_module)

    assert "import geneformer" not in source.lower()
    assert "from geneformer" not in source.lower()
    assert "import scanpy" not in source.lower()
    assert "import anndata" not in source.lower()
