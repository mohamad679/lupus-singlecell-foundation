"""Stage 3 embedding artifact schema contract.

This module validates metadata-only contracts for future Geneformer embedding
artifacts. It does not load artifact files, load AnnData files, execute
Geneformer, execute tokenizers, aggregate embeddings, train models, evaluate
models, perform external validation, or add performance claims.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Any

from lupusfm.data.anndata_schema import DEFAULT_FORBIDDEN_SPLIT_VALUES
from lupusfm.data.manifest import (
    FORBIDDEN_OUTPUT_SUFFIXES,
    PRIMARY_CELLXGENE_CENSUS_VERSION,
    PRIMARY_CELLXGENE_DATASET_ID,
)
from lupusfm.data.metadata import DEFAULT_DONOR_COLUMN


ALLOWED_EMBEDDING_ARTIFACT_FORMATS = (
    "parquet",
    "npz",
    "zarr",
    "csv_metadata_plus_numpy",
)

ALLOWED_EMBEDDING_RECORD_LEVELS = ("cell", "donor")

DEFAULT_ARTIFACT_SPLIT_LEVEL = "patient"
ALLOWED_ARTIFACT_SPLIT_LEVELS = ("patient", "donor")

DEFAULT_EMBEDDING_COLUMN = "embedding"
DEFAULT_EMBEDDING_DIMENSION = 1152
DEFAULT_EMBEDDING_SOURCE = "frozen_geneformer_feature_extractor"


class EmbeddingArtifactSchemaError(ValueError):
    """Raised when a Stage 3 embedding artifact schema violates the contract."""


@dataclass(frozen=True)
class EmbeddingArtifactPaths:
    """Declared future artifact paths without touching the filesystem."""

    artifact: str
    metadata: str
    extraction_config: str
    provenance: str


@dataclass(frozen=True)
class EmbeddingArtifactSchema:
    """Metadata-only contract for future embedding artifacts."""

    dataset_id: str
    source: str
    census_version: str
    donor_id_column: str
    cell_id_column: str | None
    sampled_cell_id_column: str | None
    embedding_column: str
    embedding_dimension: int
    embedding_source: str
    artifact_format: str
    record_level: str
    split_level: str
    model_provenance_reference: str
    extraction_config_reference: str
    paths: EmbeddingArtifactPaths
    contains_model_artifact: bool = False
    contains_training_artifact: bool = False
    allow_modeling: bool = False
    allow_training: bool = False
    allow_external_validation: bool = False
    performance_claims_added: bool = False
    notes: str = ""


def _clean_required_string(value: object, field_name: str) -> str:
    """Return a non-empty normalized string or raise."""

    normalized = str(value).strip()
    if not normalized:
        raise EmbeddingArtifactSchemaError(f"{field_name} must not be empty.")
    return normalized


def _clean_optional_string(value: object, field_name: str) -> str | None:
    """Return a normalized optional string."""

    if value is None:
        return None

    normalized = str(value).strip()
    if not normalized:
        return None

    return normalized


def _require_positive_int(value: object, field_name: str) -> int:
    """Return a positive integer or raise."""

    if isinstance(value, bool):
        raise EmbeddingArtifactSchemaError(f"{field_name} must be an integer, not bool.")

    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise EmbeddingArtifactSchemaError(
            f"{field_name} must be an integer."
        ) from exc

    if parsed <= 0:
        raise EmbeddingArtifactSchemaError(f"{field_name} must be positive.")

    return parsed


def _as_bool(value: object) -> bool:
    """Parse common bool-like values."""

    if isinstance(value, bool):
        return value

    return str(value).strip().lower() in {"1", "true", "yes"}


def _validate_choice(value: object, allowed: tuple[str, ...], field_name: str) -> str:
    """Validate a normalized string against an allowed set."""

    normalized = _clean_required_string(value, field_name)
    if normalized not in allowed:
        allowed_text = ", ".join(allowed)
        raise EmbeddingArtifactSchemaError(
            f"{field_name} must be one of: {allowed_text}; got {normalized!r}."
        )

    return normalized


def _validate_declared_path(path: object, field_name: str) -> str:
    """Validate a declared metadata/artifact path without filesystem access."""

    normalized = _clean_required_string(path, field_name)
    lowered = normalized.lower()

    if lowered.endswith(FORBIDDEN_OUTPUT_SUFFIXES):
        raise EmbeddingArtifactSchemaError(
            f"{field_name} points to a model/training artifact-like output: "
            f"{normalized!r}."
        )

    return normalized


def validate_embedding_artifact_paths(
    paths: EmbeddingArtifactPaths,
) -> EmbeddingArtifactPaths:
    """Validate declared future embedding artifact paths."""

    return EmbeddingArtifactPaths(
        artifact=_validate_declared_path(paths.artifact, "paths.artifact"),
        metadata=_validate_declared_path(paths.metadata, "paths.metadata"),
        extraction_config=_validate_declared_path(
            paths.extraction_config,
            "paths.extraction_config",
        ),
        provenance=_validate_declared_path(paths.provenance, "paths.provenance"),
    )


def validate_embedding_artifact_schema(
    schema: EmbeddingArtifactSchema,
) -> EmbeddingArtifactSchema:
    """Validate a Stage 3 embedding artifact schema and return a normalized copy."""

    dataset_id = _clean_required_string(schema.dataset_id, "dataset_id")
    census_version = _clean_required_string(schema.census_version, "census_version")

    if dataset_id != PRIMARY_CELLXGENE_DATASET_ID:
        raise EmbeddingArtifactSchemaError(
            "dataset_id must match the approved primary CELLxGENE contract."
        )
    if census_version != PRIMARY_CELLXGENE_CENSUS_VERSION:
        raise EmbeddingArtifactSchemaError(
            "census_version must match the approved primary CELLxGENE contract."
        )

    artifact_format = _validate_choice(
        schema.artifact_format,
        ALLOWED_EMBEDDING_ARTIFACT_FORMATS,
        "artifact_format",
    )
    record_level = _validate_choice(
        schema.record_level,
        ALLOWED_EMBEDDING_RECORD_LEVELS,
        "record_level",
    )
    split_level = _validate_choice(
        schema.split_level,
        ALLOWED_ARTIFACT_SPLIT_LEVELS,
        "split_level",
    )

    forbidden_split_levels = {str(value) for value in DEFAULT_FORBIDDEN_SPLIT_VALUES}
    if split_level in forbidden_split_levels:
        raise EmbeddingArtifactSchemaError(
            "cell-level split assignments are not allowed."
        )

    cell_id_column = _clean_optional_string(schema.cell_id_column, "cell_id_column")
    sampled_cell_id_column = _clean_optional_string(
        schema.sampled_cell_id_column,
        "sampled_cell_id_column",
    )
    if cell_id_column is None and sampled_cell_id_column is None:
        raise EmbeddingArtifactSchemaError(
            "At least one of cell_id_column or sampled_cell_id_column is required."
        )

    if _as_bool(schema.contains_model_artifact):
        raise EmbeddingArtifactSchemaError(
            "Embedding artifact schema must not contain model artifacts."
        )
    if _as_bool(schema.contains_training_artifact):
        raise EmbeddingArtifactSchemaError(
            "Embedding artifact schema must not contain training artifacts."
        )
    if _as_bool(schema.allow_modeling):
        raise EmbeddingArtifactSchemaError(
            "Stage 3 artifact schema must keep modeling disabled."
        )
    if _as_bool(schema.allow_training):
        raise EmbeddingArtifactSchemaError(
            "Stage 3 artifact schema must keep training disabled."
        )
    if _as_bool(schema.allow_external_validation):
        raise EmbeddingArtifactSchemaError(
            "Stage 3 artifact schema must keep external validation disabled."
        )
    if _as_bool(schema.performance_claims_added):
        raise EmbeddingArtifactSchemaError(
            "Stage 3 artifact schema must not add performance claims."
        )

    return EmbeddingArtifactSchema(
        dataset_id=dataset_id,
        source=_clean_required_string(schema.source, "source"),
        census_version=census_version,
        donor_id_column=_clean_required_string(
            schema.donor_id_column,
            "donor_id_column",
        ),
        cell_id_column=cell_id_column,
        sampled_cell_id_column=sampled_cell_id_column,
        embedding_column=_clean_required_string(
            schema.embedding_column,
            "embedding_column",
        ),
        embedding_dimension=_require_positive_int(
            schema.embedding_dimension,
            "embedding_dimension",
        ),
        embedding_source=_clean_required_string(
            schema.embedding_source,
            "embedding_source",
        ),
        artifact_format=artifact_format,
        record_level=record_level,
        split_level=split_level,
        model_provenance_reference=_validate_declared_path(
            schema.model_provenance_reference,
            "model_provenance_reference",
        ),
        extraction_config_reference=_validate_declared_path(
            schema.extraction_config_reference,
            "extraction_config_reference",
        ),
        paths=validate_embedding_artifact_paths(schema.paths),
        contains_model_artifact=False,
        contains_training_artifact=False,
        allow_modeling=False,
        allow_training=False,
        allow_external_validation=False,
        performance_claims_added=False,
        notes=str(schema.notes).strip(),
    )


def embedding_artifact_schema_from_mapping(
    data: Mapping[str, Any],
) -> EmbeddingArtifactSchema:
    """Build and validate an artifact schema from a mapping."""

    paths_data = data.get("paths")
    if not isinstance(paths_data, Mapping):
        raise EmbeddingArtifactSchemaError("paths must be a mapping.")

    return validate_embedding_artifact_schema(
        EmbeddingArtifactSchema(
            dataset_id=data.get("dataset_id", ""),
            source=data.get("source", ""),
            census_version=data.get("census_version", ""),
            donor_id_column=data.get("donor_id_column", DEFAULT_DONOR_COLUMN),
            cell_id_column=data.get("cell_id_column"),
            sampled_cell_id_column=data.get("sampled_cell_id_column"),
            embedding_column=data.get("embedding_column", DEFAULT_EMBEDDING_COLUMN),
            embedding_dimension=data.get(
                "embedding_dimension",
                DEFAULT_EMBEDDING_DIMENSION,
            ),
            embedding_source=data.get(
                "embedding_source",
                DEFAULT_EMBEDDING_SOURCE,
            ),
            artifact_format=data.get("artifact_format", "parquet"),
            record_level=data.get("record_level", "cell"),
            split_level=data.get("split_level", DEFAULT_ARTIFACT_SPLIT_LEVEL),
            model_provenance_reference=data.get("model_provenance_reference", ""),
            extraction_config_reference=data.get("extraction_config_reference", ""),
            paths=EmbeddingArtifactPaths(
                artifact=paths_data.get("artifact", ""),
                metadata=paths_data.get("metadata", ""),
                extraction_config=paths_data.get("extraction_config", ""),
                provenance=paths_data.get("provenance", ""),
            ),
            contains_model_artifact=data.get("contains_model_artifact", False),
            contains_training_artifact=data.get("contains_training_artifact", False),
            allow_modeling=data.get("allow_modeling", False),
            allow_training=data.get("allow_training", False),
            allow_external_validation=data.get("allow_external_validation", False),
            performance_claims_added=data.get("performance_claims_added", False),
            notes=data.get("notes", ""),
        )
    )


def embedding_artifact_schema_to_dict(
    schema: EmbeddingArtifactSchema,
) -> dict[str, Any]:
    """Serialize a validated artifact schema to plain dictionaries."""

    return asdict(validate_embedding_artifact_schema(schema))
