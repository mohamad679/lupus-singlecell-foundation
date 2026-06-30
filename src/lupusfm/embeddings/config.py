"""Stage 2 embedding extraction configuration contract.

This module validates metadata-only configuration for a future Geneformer
embedding extraction feature. It does not load the Geneformer runtime, load
AnnData files, download data, tokenize cells, extract embeddings, train models,
or evaluate performance.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Any

from lupusfm.data.anndata_schema import DEFAULT_FORBIDDEN_SPLIT_VALUES
from lupusfm.data.anndata_schema import DEFAULT_GENE_SYMBOL_COLUMN
from lupusfm.data.manifest import (
    DEFAULT_RANDOM_SEED,
    FORBIDDEN_OUTPUT_SUFFIXES,
    PRIMARY_CELLXGENE_CENSUS_VERSION,
    PRIMARY_CELLXGENE_DATASET_ID,
    IngestionManifest,
    IngestionManifestError,
    validate_ingestion_manifest,
)
from lupusfm.data.metadata import DEFAULT_DONOR_COLUMN


DEFAULT_GENE_ID_POLICY = "explicit_gene_symbol_to_ensembl_mapping"
ALLOWED_GENE_ID_POLICIES = (
    "explicit_gene_symbol_column",
    "explicit_ensembl_id_column",
    "explicit_gene_symbol_to_ensembl_mapping",
)

DEFAULT_PATIENT_AGGREGATION = "mean_pool_per_donor"
ALLOWED_PATIENT_AGGREGATIONS = (DEFAULT_PATIENT_AGGREGATION,)

DEFAULT_SPLIT_LEVEL = "patient"
ALLOWED_SPLIT_LEVELS = ("patient", "donor", "none")

DEFAULT_GENEFORMER_MODEL = "ctheodoris/Geneformer"
DEFAULT_GENEFORMER_REVISION = "main"
DEFAULT_TOKENIZER_SOURCE = "ctheodoris/Geneformer"
DEFAULT_VOCABULARY_SOURCE = "ctheodoris/Geneformer/token_dictionary.pkl"

DEFAULT_CELLS_PER_DONOR = 300
DEFAULT_MAX_SEQUENCE_LENGTH = 1024
DEFAULT_BATCH_SIZE = 16


class EmbeddingConfigError(ValueError):
    """Raised when a Stage 2 embedding config violates the contract."""


@dataclass(frozen=True)
class EmbeddingOutputPaths:
    """Declared metadata/output locations for future embedding extraction."""

    root: str
    config: str
    provenance: str
    embeddings: str
    sampled_cell_ids: str


@dataclass(frozen=True)
class EmbeddingExtractionConfig:
    """Metadata-only contract for future Geneformer embedding extraction."""

    dataset_id: str
    source: str
    census_version: str
    donor_column: str
    gene_symbol_column: str
    gene_id_policy: str
    ingestion_manifest_path: str
    model_name_or_path: str
    model_revision: str
    tokenizer_name_or_path: str
    vocabulary_source: str
    cells_per_donor: int
    max_sequence_length: int
    batch_size: int
    random_seed: int
    split_level: str
    patient_aggregation: str
    output_paths: EmbeddingOutputPaths
    allow_downloads: bool = False
    allow_anndata_loading: bool = False
    allow_geneformer_execution: bool = False
    allow_embedding_extraction: bool = False
    allow_modeling: bool = False
    allow_training: bool = False
    allow_external_validation: bool = False
    notes: str = ""


def _clean_required_string(value: object, field_name: str) -> str:
    """Return a non-empty normalized string or raise."""

    normalized = str(value).strip()
    if not normalized:
        raise EmbeddingConfigError(f"{field_name} must not be empty.")
    return normalized


def _require_non_negative_int(value: object, field_name: str) -> int:
    """Return a non-negative integer or raise."""

    if isinstance(value, bool):
        raise EmbeddingConfigError(f"{field_name} must be an integer, not bool.")

    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise EmbeddingConfigError(f"{field_name} must be an integer.") from exc

    if parsed < 0:
        raise EmbeddingConfigError(f"{field_name} must be non-negative.")

    return parsed


def _require_positive_int(value: object, field_name: str) -> int:
    """Return a positive integer or raise."""

    parsed = _require_non_negative_int(value, field_name)
    if parsed <= 0:
        raise EmbeddingConfigError(f"{field_name} must be positive.")
    return parsed


def _as_bool(value: object) -> bool:
    """Parse common bool-like values."""

    if isinstance(value, bool):
        return value

    return str(value).strip().lower() in {"1", "true", "yes"}


def _validate_choice(value: str, allowed: tuple[str, ...], field_name: str) -> str:
    """Validate a normalized string against an allowed set."""

    normalized = _clean_required_string(value, field_name)
    if normalized not in allowed:
        allowed_text = ", ".join(allowed)
        raise EmbeddingConfigError(
            f"{field_name} must be one of: {allowed_text}; got {normalized!r}."
        )
    return normalized


def _validate_output_path(path: str, field_name: str) -> str:
    """Validate one declared Stage 2 metadata or embedding output path."""

    normalized = _clean_required_string(path, field_name)
    lowered = normalized.lower()

    if lowered.endswith(FORBIDDEN_OUTPUT_SUFFIXES):
        raise EmbeddingConfigError(
            f"{field_name} points to a model/training artifact-like output: "
            f"{normalized!r}."
        )

    return normalized


def validate_embedding_output_paths(
    output_paths: EmbeddingOutputPaths,
) -> EmbeddingOutputPaths:
    """Validate declared Stage 2 output paths without touching the filesystem."""

    return EmbeddingOutputPaths(
        root=_validate_output_path(output_paths.root, "output_paths.root"),
        config=_validate_output_path(output_paths.config, "output_paths.config"),
        provenance=_validate_output_path(
            output_paths.provenance,
            "output_paths.provenance",
        ),
        embeddings=_validate_output_path(
            output_paths.embeddings,
            "output_paths.embeddings",
        ),
        sampled_cell_ids=_validate_output_path(
            output_paths.sampled_cell_ids,
            "output_paths.sampled_cell_ids",
        ),
    )


def validate_embedding_config(
    config: EmbeddingExtractionConfig,
) -> EmbeddingExtractionConfig:
    """Validate a Stage 2 embedding configuration and return a normalized copy."""

    dataset_id = _clean_required_string(config.dataset_id, "dataset_id")
    census_version = _clean_required_string(config.census_version, "census_version")

    if dataset_id != PRIMARY_CELLXGENE_DATASET_ID:
        raise EmbeddingConfigError(
            "dataset_id must match the approved primary CELLxGENE contract."
        )
    if census_version != PRIMARY_CELLXGENE_CENSUS_VERSION:
        raise EmbeddingConfigError(
            "census_version must match the approved primary CELLxGENE contract."
        )

    split_level = _validate_choice(
        str(config.split_level),
        ALLOWED_SPLIT_LEVELS,
        "split_level",
    )
    forbidden_split_levels = {str(value) for value in DEFAULT_FORBIDDEN_SPLIT_VALUES}
    if split_level in forbidden_split_levels:
        raise EmbeddingConfigError("cell-level split assignments are not allowed.")

    if config.allow_downloads:
        raise EmbeddingConfigError("Stage 2 config must keep downloads disabled.")
    if config.allow_anndata_loading:
        raise EmbeddingConfigError("Stage 2 config must keep AnnData loading disabled.")
    if config.allow_geneformer_execution:
        raise EmbeddingConfigError(
            "Stage 2 config must keep Geneformer execution disabled."
        )
    if config.allow_embedding_extraction:
        raise EmbeddingConfigError(
            "Stage 2 config must keep embedding extraction disabled."
        )
    if config.allow_modeling:
        raise EmbeddingConfigError("Stage 2 config must keep modeling disabled.")
    if config.allow_training:
        raise EmbeddingConfigError("Stage 2 config must keep training disabled.")
    if config.allow_external_validation:
        raise EmbeddingConfigError(
            "Stage 2 config must keep external validation disabled."
        )

    return EmbeddingExtractionConfig(
        dataset_id=dataset_id,
        source=_clean_required_string(config.source, "source"),
        census_version=census_version,
        donor_column=_clean_required_string(config.donor_column, "donor_column"),
        gene_symbol_column=_clean_required_string(
            config.gene_symbol_column,
            "gene_symbol_column",
        ),
        gene_id_policy=_validate_choice(
            str(config.gene_id_policy),
            ALLOWED_GENE_ID_POLICIES,
            "gene_id_policy",
        ),
        ingestion_manifest_path=_validate_output_path(
            config.ingestion_manifest_path,
            "ingestion_manifest_path",
        ),
        model_name_or_path=_clean_required_string(
            config.model_name_or_path,
            "model_name_or_path",
        ),
        model_revision=_clean_required_string(config.model_revision, "model_revision"),
        tokenizer_name_or_path=_clean_required_string(
            config.tokenizer_name_or_path,
            "tokenizer_name_or_path",
        ),
        vocabulary_source=_clean_required_string(
            config.vocabulary_source,
            "vocabulary_source",
        ),
        cells_per_donor=_require_positive_int(
            config.cells_per_donor,
            "cells_per_donor",
        ),
        max_sequence_length=_require_positive_int(
            config.max_sequence_length,
            "max_sequence_length",
        ),
        batch_size=_require_positive_int(config.batch_size, "batch_size"),
        random_seed=_require_non_negative_int(config.random_seed, "random_seed"),
        split_level=split_level,
        patient_aggregation=_validate_choice(
            str(config.patient_aggregation),
            ALLOWED_PATIENT_AGGREGATIONS,
            "patient_aggregation",
        ),
        output_paths=validate_embedding_output_paths(config.output_paths),
        allow_downloads=False,
        allow_anndata_loading=False,
        allow_geneformer_execution=False,
        allow_embedding_extraction=False,
        allow_modeling=False,
        allow_training=False,
        allow_external_validation=False,
        notes=str(config.notes),
    )


def validate_embedding_config_against_manifest(
    config: EmbeddingExtractionConfig,
    manifest: IngestionManifest,
) -> None:
    """Validate config consistency against a Stage 1 ingestion manifest object."""

    validated_config = validate_embedding_config(config)
    try:
        validated_manifest = validate_ingestion_manifest(manifest)
    except IngestionManifestError as exc:
        raise EmbeddingConfigError(
            "Ingestion manifest does not satisfy the Stage 1 contract."
        ) from exc

    comparisons = {
        "dataset_id": (validated_config.dataset_id, validated_manifest.dataset_id),
        "census_version": (
            validated_config.census_version,
            validated_manifest.census_version,
        ),
        "donor_column": (
            validated_config.donor_column,
            validated_manifest.donor_column,
        ),
        "gene_symbol_column": (
            validated_config.gene_symbol_column,
            validated_manifest.gene_symbol_column,
        ),
        "random_seed": (validated_config.random_seed, validated_manifest.random_seed),
    }

    mismatches = tuple(
        field_name
        for field_name, (config_value, manifest_value) in comparisons.items()
        if config_value != manifest_value
    )
    if mismatches:
        mismatch_text = ", ".join(mismatches)
        raise EmbeddingConfigError(
            f"Embedding config does not match ingestion manifest: {mismatch_text}."
        )


def make_embedding_config_from_mapping(
    row: Mapping[str, Any],
) -> EmbeddingExtractionConfig:
    """Create and validate an embedding config from mapping-like metadata."""

    output_paths_raw = row.get("output_paths")
    if not isinstance(output_paths_raw, Mapping):
        raise EmbeddingConfigError("output_paths must be a mapping.")

    output_paths = EmbeddingOutputPaths(
        root=output_paths_raw.get("root", ""),
        config=output_paths_raw.get("config", ""),
        provenance=output_paths_raw.get("provenance", ""),
        embeddings=output_paths_raw.get("embeddings", ""),
        sampled_cell_ids=output_paths_raw.get("sampled_cell_ids", ""),
    )

    config = EmbeddingExtractionConfig(
        dataset_id=row.get("dataset_id", ""),
        source=row.get("source", ""),
        census_version=row.get("census_version", ""),
        donor_column=row.get("donor_column", DEFAULT_DONOR_COLUMN),
        gene_symbol_column=row.get("gene_symbol_column", DEFAULT_GENE_SYMBOL_COLUMN),
        gene_id_policy=row.get("gene_id_policy", DEFAULT_GENE_ID_POLICY),
        ingestion_manifest_path=row.get("ingestion_manifest_path", ""),
        model_name_or_path=row.get("model_name_or_path", DEFAULT_GENEFORMER_MODEL),
        model_revision=row.get("model_revision", DEFAULT_GENEFORMER_REVISION),
        tokenizer_name_or_path=row.get(
            "tokenizer_name_or_path",
            DEFAULT_TOKENIZER_SOURCE,
        ),
        vocabulary_source=row.get("vocabulary_source", DEFAULT_VOCABULARY_SOURCE),
        cells_per_donor=row.get("cells_per_donor", DEFAULT_CELLS_PER_DONOR),
        max_sequence_length=row.get(
            "max_sequence_length",
            DEFAULT_MAX_SEQUENCE_LENGTH,
        ),
        batch_size=row.get("batch_size", DEFAULT_BATCH_SIZE),
        random_seed=row.get("random_seed", DEFAULT_RANDOM_SEED),
        split_level=row.get("split_level", DEFAULT_SPLIT_LEVEL),
        patient_aggregation=row.get(
            "patient_aggregation",
            DEFAULT_PATIENT_AGGREGATION,
        ),
        output_paths=output_paths,
        allow_downloads=_as_bool(row.get("allow_downloads", False)),
        allow_anndata_loading=_as_bool(row.get("allow_anndata_loading", False)),
        allow_geneformer_execution=_as_bool(
            row.get("allow_geneformer_execution", False)
        ),
        allow_embedding_extraction=_as_bool(
            row.get("allow_embedding_extraction", False)
        ),
        allow_modeling=_as_bool(row.get("allow_modeling", False)),
        allow_training=_as_bool(row.get("allow_training", False)),
        allow_external_validation=_as_bool(
            row.get("allow_external_validation", False)
        ),
        notes=row.get("notes", ""),
    )

    return validate_embedding_config(config)


def make_primary_cellxgene_embedding_config(
    output_root: str = "artifacts/stage2/embeddings",
    ingestion_manifest_path: str = "artifacts/stage1/ingestion_manifest.json",
) -> EmbeddingExtractionConfig:
    """Create the locked primary CELLxGENE Stage 2 embedding config contract."""

    return validate_embedding_config(
        EmbeddingExtractionConfig(
            dataset_id=PRIMARY_CELLXGENE_DATASET_ID,
            source="CELLxGENE Census",
            census_version=PRIMARY_CELLXGENE_CENSUS_VERSION,
            donor_column=DEFAULT_DONOR_COLUMN,
            gene_symbol_column=DEFAULT_GENE_SYMBOL_COLUMN,
            gene_id_policy=DEFAULT_GENE_ID_POLICY,
            ingestion_manifest_path=ingestion_manifest_path,
            model_name_or_path=DEFAULT_GENEFORMER_MODEL,
            model_revision=DEFAULT_GENEFORMER_REVISION,
            tokenizer_name_or_path=DEFAULT_TOKENIZER_SOURCE,
            vocabulary_source=DEFAULT_VOCABULARY_SOURCE,
            cells_per_donor=DEFAULT_CELLS_PER_DONOR,
            max_sequence_length=DEFAULT_MAX_SEQUENCE_LENGTH,
            batch_size=DEFAULT_BATCH_SIZE,
            random_seed=DEFAULT_RANDOM_SEED,
            split_level=DEFAULT_SPLIT_LEVEL,
            patient_aggregation=DEFAULT_PATIENT_AGGREGATION,
            output_paths=EmbeddingOutputPaths(
                root=output_root,
                config=f"{output_root}/embedding_config.json",
                provenance=f"{output_root}/embedding_provenance.json",
                embeddings=f"{output_root}/patient_embeddings",
                sampled_cell_ids=f"{output_root}/sampled_cell_ids.json",
            ),
            notes="Primary CELLxGENE/Perez lupus Geneformer embedding config.",
        )
    )


def embedding_config_to_dict(config: EmbeddingExtractionConfig) -> dict[str, Any]:
    """Serialize a validated embedding config to a plain dictionary."""

    return asdict(validate_embedding_config(config))
