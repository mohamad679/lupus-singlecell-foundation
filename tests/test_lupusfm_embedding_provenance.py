import inspect

import pytest

import lupusfm.embeddings.provenance as provenance_module
from lupusfm.data.manifest import (
    PRIMARY_CELLXGENE_CENSUS_VERSION,
    PRIMARY_CELLXGENE_DATASET_ID,
)
from lupusfm.embeddings.config import make_primary_cellxgene_embedding_config
from lupusfm.embeddings.provenance import (
    EmbeddingProvenanceError,
    EmbeddingProvenanceManifest,
    ProvenanceHash,
    embedding_provenance_to_dict,
    make_embedding_provenance_from_config,
    make_embedding_provenance_from_mapping,
    validate_embedding_provenance_against_config,
    validate_embedding_provenance_manifest,
    validate_provenance_hash,
)


VALID_SHA256 = "a" * 64


def valid_hash(name="model_config", source="ctheodoris/Geneformer"):
    return ProvenanceHash(name=name, source=source)


def recorded_hash(name="model_config", source="ctheodoris/Geneformer"):
    return ProvenanceHash(
        name=name,
        source=source,
        status="recorded",
        sha256=VALID_SHA256,
    )


def valid_provenance():
    config = make_primary_cellxgene_embedding_config()
    return make_embedding_provenance_from_config(config)


def test_validate_provenance_hash_accepts_pending_hash_record():
    record = validate_provenance_hash(valid_hash())

    assert record.status == "pending_runtime_resolution"
    assert record.sha256 is None


def test_validate_provenance_hash_accepts_recorded_sha256():
    record = validate_provenance_hash(recorded_hash())

    assert record.status == "recorded"
    assert record.sha256 == VALID_SHA256


def test_validate_provenance_hash_rejects_missing_recorded_sha256():
    with pytest.raises(EmbeddingProvenanceError, match="sha256"):
        validate_provenance_hash(
            ProvenanceHash(
                name="model_config",
                source="ctheodoris/Geneformer",
                status="recorded",
                sha256=None,
            )
        )


def test_validate_provenance_hash_rejects_bad_recorded_sha256():
    with pytest.raises(EmbeddingProvenanceError, match="sha256"):
        validate_provenance_hash(
            ProvenanceHash(
                name="model_config",
                source="ctheodoris/Geneformer",
                status="recorded",
                sha256="not-a-hash",
            )
        )


def test_validate_provenance_hash_rejects_pending_hash_value():
    with pytest.raises(EmbeddingProvenanceError, match="pending"):
        validate_provenance_hash(
            ProvenanceHash(
                name="model_config",
                source="ctheodoris/Geneformer",
                status="pending_runtime_resolution",
                sha256=VALID_SHA256,
            )
        )


def test_make_embedding_provenance_from_config_records_pending_runtime_sources():
    provenance = valid_provenance()

    assert provenance.dataset_id == PRIMARY_CELLXGENE_DATASET_ID
    assert provenance.census_version == PRIMARY_CELLXGENE_CENSUS_VERSION
    assert provenance.model_config_hash.status == "pending_runtime_resolution"
    assert provenance.tokenizer_hash.status == "pending_runtime_resolution"
    assert provenance.vocabulary_hash.status == "pending_runtime_resolution"
    assert provenance.embedding_config_hash.status == "pending_runtime_resolution"
    assert provenance.extraction_performed is False


def test_validate_embedding_provenance_manifest_accepts_valid_provenance():
    provenance = validate_embedding_provenance_manifest(valid_provenance())

    assert provenance.allow_downloads is False
    assert provenance.allow_anndata_loading is False
    assert provenance.allow_geneformer_execution is False
    assert provenance.allow_tokenizer_execution is False
    assert provenance.allow_embedding_extraction is False
    assert provenance.allow_modeling is False
    assert provenance.allow_training is False
    assert provenance.allow_external_validation is False
    assert provenance.performance_claims_added is False


@pytest.mark.parametrize(
    ("field_name", "bad_value"),
    [
        ("dataset_id", "other-dataset"),
        ("census_version", "2024-01-01"),
    ],
)
def test_validate_embedding_provenance_requires_primary_contract(field_name, bad_value):
    values = valid_provenance().__dict__.copy()
    values[field_name] = bad_value

    with pytest.raises(EmbeddingProvenanceError, match=field_name):
        validate_embedding_provenance_manifest(
            EmbeddingProvenanceManifest(**values)
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "source",
        "donor_column",
        "gene_symbol_column",
        "gene_id_policy",
        "model_name_or_path",
        "model_revision",
        "tokenizer_name_or_path",
        "vocabulary_source",
        "split_level",
        "patient_aggregation",
        "output_root",
        "config_path",
        "provenance_path",
        "embeddings_path",
        "sampled_cell_ids_path",
    ],
)
def test_validate_embedding_provenance_rejects_empty_required_strings(field_name):
    values = valid_provenance().__dict__.copy()
    values[field_name] = "   "

    with pytest.raises(EmbeddingProvenanceError, match=field_name):
        validate_embedding_provenance_manifest(
            EmbeddingProvenanceManifest(**values)
        )


@pytest.mark.parametrize(
    ("field_name", "bad_value"),
    [
        ("cells_per_donor", 0),
        ("max_sequence_length", 0),
        ("batch_size", 0),
        ("random_seed", -1),
    ],
)
def test_validate_embedding_provenance_rejects_bad_counts_and_seed(
    field_name,
    bad_value,
):
    values = valid_provenance().__dict__.copy()
    values[field_name] = bad_value

    with pytest.raises(EmbeddingProvenanceError, match=field_name):
        validate_embedding_provenance_manifest(
            EmbeddingProvenanceManifest(**values)
        )


@pytest.mark.parametrize(
    "field_name",
    ["cells_per_donor", "max_sequence_length", "batch_size", "random_seed"],
)
def test_validate_embedding_provenance_rejects_bool_numeric_fields(field_name):
    values = valid_provenance().__dict__.copy()
    values[field_name] = True

    with pytest.raises(EmbeddingProvenanceError, match=field_name):
        validate_embedding_provenance_manifest(
            EmbeddingProvenanceManifest(**values)
        )


@pytest.mark.parametrize(
    "flag_name",
    [
        "extraction_performed",
        "allow_downloads",
        "allow_anndata_loading",
        "allow_geneformer_execution",
        "allow_tokenizer_execution",
        "allow_embedding_extraction",
        "allow_modeling",
        "allow_training",
        "allow_external_validation",
        "performance_claims_added",
    ],
)
def test_validate_embedding_provenance_keeps_runtime_and_claims_disabled(flag_name):
    values = valid_provenance().__dict__.copy()
    values[flag_name] = True

    with pytest.raises(EmbeddingProvenanceError):
        validate_embedding_provenance_manifest(
            EmbeddingProvenanceManifest(**values)
        )


def test_validate_embedding_provenance_against_config_accepts_matching_config():
    config = make_primary_cellxgene_embedding_config()
    provenance = make_embedding_provenance_from_config(config)

    validate_embedding_provenance_against_config(provenance, config)


def test_validate_embedding_provenance_against_config_rejects_mismatch():
    config = make_primary_cellxgene_embedding_config()
    values = make_embedding_provenance_from_config(config).__dict__.copy()
    values["random_seed"] = 7

    with pytest.raises(EmbeddingProvenanceError, match="random_seed"):
        validate_embedding_provenance_against_config(
            EmbeddingProvenanceManifest(**values),
            config,
        )


def test_make_embedding_provenance_from_mapping_parses_and_validates_values():
    provenance = make_embedding_provenance_from_mapping(
        {
            "dataset_id": PRIMARY_CELLXGENE_DATASET_ID,
            "source": "CELLxGENE Census",
            "census_version": PRIMARY_CELLXGENE_CENSUS_VERSION,
            "donor_column": "donor_id",
            "gene_symbol_column": "gene_symbol",
            "gene_id_policy": "explicit_gene_symbol_to_ensembl_mapping",
            "model_name_or_path": "ctheodoris/Geneformer",
            "model_revision": "main",
            "model_config_hash": {
                "name": "model_config",
                "source": "ctheodoris/Geneformer",
                "status": "recorded",
                "sha256": VALID_SHA256,
            },
            "tokenizer_name_or_path": "ctheodoris/Geneformer",
            "tokenizer_hash": {
                "name": "tokenizer",
                "source": "ctheodoris/Geneformer",
                "status": "pending_runtime_resolution",
            },
            "vocabulary_source": "ctheodoris/Geneformer/token_dictionary.pkl",
            "vocabulary_hash": {
                "name": "vocabulary",
                "source": "ctheodoris/Geneformer/token_dictionary.pkl",
                "status": "pending_runtime_resolution",
            },
            "embedding_config_hash": {
                "name": "embedding_config",
                "source": "artifacts/stage2/embeddings/embedding_config.json",
                "status": "pending_runtime_resolution",
            },
            "cells_per_donor": "300",
            "max_sequence_length": "1024",
            "batch_size": "16",
            "random_seed": "42",
            "split_level": "patient",
            "patient_aggregation": "mean_pool_per_donor",
            "output_root": "artifacts/stage2/embeddings",
            "config_path": "artifacts/stage2/embeddings/embedding_config.json",
            "provenance_path": (
                "artifacts/stage2/embeddings/embedding_provenance.json"
            ),
            "embeddings_path": "artifacts/stage2/embeddings/patient_embeddings",
            "sampled_cell_ids_path": (
                "artifacts/stage2/embeddings/sampled_cell_ids.json"
            ),
            "allow_downloads": "false",
            "allow_anndata_loading": "false",
            "allow_geneformer_execution": "false",
            "allow_tokenizer_execution": "false",
            "allow_embedding_extraction": "false",
            "allow_modeling": "false",
            "allow_training": "false",
            "allow_external_validation": "false",
            "performance_claims_added": "false",
        }
    )

    assert provenance.cells_per_donor == 300
    assert provenance.max_sequence_length == 1024
    assert provenance.batch_size == 16
    assert provenance.random_seed == 42
    assert provenance.model_config_hash.status == "recorded"


def test_make_embedding_provenance_from_mapping_requires_hash_mappings():
    with pytest.raises(EmbeddingProvenanceError, match="model_config_hash"):
        make_embedding_provenance_from_mapping({"model_config_hash": None})


def test_embedding_provenance_to_dict_serializes_validated_provenance():
    serialized = embedding_provenance_to_dict(valid_provenance())

    assert serialized["dataset_id"] == PRIMARY_CELLXGENE_DATASET_ID
    assert serialized["model_config_hash"]["status"] == "pending_runtime_resolution"
    assert serialized["allow_geneformer_execution"] is False


def test_provenance_module_does_not_load_runtime_stack():
    source = inspect.getsource(provenance_module)

    assert "import geneformer" not in source.lower()
    assert "from geneformer" not in source.lower()
    assert "import scanpy" not in source.lower()
    assert "import anndata" not in source.lower()
