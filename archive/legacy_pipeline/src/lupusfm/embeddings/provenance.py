"""Stage 2 embedding provenance manifest contract.

This module records metadata-only provenance for a future Geneformer embedding
extraction run. It does not load model runtimes, load AnnData files, download
data, tokenize cells, extract embeddings, train models, evaluate performance, or
write artifacts.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any, Mapping

from lupusfm.data.manifest import (
    PRIMARY_CELLXGENE_CENSUS_VERSION,
    PRIMARY_CELLXGENE_DATASET_ID,
)
from lupusfm.embeddings.config import (
    EmbeddingConfigError,
    EmbeddingExtractionConfig,
    validate_embedding_config,
)


SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
ALLOWED_HASH_STATUSES = ("pending_runtime_resolution", "recorded")


class EmbeddingProvenanceError(ValueError):
    """Raised when embedding provenance violates the Stage 2 contract."""


@dataclass(frozen=True)
class ProvenanceHash:
    """Provenance hash record for a model, tokenizer, vocabulary, or config."""

    name: str
    source: str
    status: str = "pending_runtime_resolution"
    sha256: str | None = None


@dataclass(frozen=True)
class EmbeddingProvenanceManifest:
    """Metadata-only provenance manifest for future embedding extraction."""

    dataset_id: str
    source: str
    census_version: str
    donor_column: str
    gene_symbol_column: str
    gene_id_policy: str
    model_name_or_path: str
    model_revision: str
    model_config_hash: ProvenanceHash
    tokenizer_name_or_path: str
    tokenizer_hash: ProvenanceHash
    vocabulary_source: str
    vocabulary_hash: ProvenanceHash
    embedding_config_hash: ProvenanceHash
    cells_per_donor: int
    max_sequence_length: int
    batch_size: int
    random_seed: int
    split_level: str
    patient_aggregation: str
    output_root: str
    config_path: str
    provenance_path: str
    embeddings_path: str
    sampled_cell_ids_path: str
    extraction_performed: bool = False
    allow_downloads: bool = False
    allow_anndata_loading: bool = False
    allow_geneformer_execution: bool = False
    allow_tokenizer_execution: bool = False
    allow_embedding_extraction: bool = False
    allow_modeling: bool = False
    allow_training: bool = False
    allow_external_validation: bool = False
    performance_claims_added: bool = False
    notes: str = ""


def _clean_required_string(value: object, field_name: str) -> str:
    """Return a non-empty normalized string or raise."""

    normalized = str(value).strip()
    if not normalized:
        raise EmbeddingProvenanceError(f"{field_name} must not be empty.")
    return normalized


def _require_non_negative_int(value: object, field_name: str) -> int:
    """Return a non-negative integer or raise."""

    if isinstance(value, bool):
        raise EmbeddingProvenanceError(f"{field_name} must be an integer, not bool.")

    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise EmbeddingProvenanceError(f"{field_name} must be an integer.") from exc

    if parsed < 0:
        raise EmbeddingProvenanceError(f"{field_name} must be non-negative.")

    return parsed


def _require_positive_int(value: object, field_name: str) -> int:
    """Return a positive integer or raise."""

    parsed = _require_non_negative_int(value, field_name)
    if parsed <= 0:
        raise EmbeddingProvenanceError(f"{field_name} must be positive.")
    return parsed


def _as_bool(value: object) -> bool:
    """Parse common bool-like values."""

    if isinstance(value, bool):
        return value

    return str(value).strip().lower() in {"1", "true", "yes"}


def _normalize_sha256(value: object, field_name: str) -> str:
    """Return a normalized sha256 hex digest or raise."""

    normalized = str(value).strip().lower()
    if not SHA256_PATTERN.fullmatch(normalized):
        raise EmbeddingProvenanceError(
            f"{field_name} must be a 64-character lowercase sha256 hex digest."
        )
    return normalized


def validate_provenance_hash(record: ProvenanceHash) -> ProvenanceHash:
    """Validate one provenance hash record."""

    name = _clean_required_string(record.name, "hash.name")
    source = _clean_required_string(record.source, "hash.source")
    status = _clean_required_string(record.status, "hash.status")

    if status not in ALLOWED_HASH_STATUSES:
        allowed = ", ".join(ALLOWED_HASH_STATUSES)
        raise EmbeddingProvenanceError(
            f"hash.status must be one of: {allowed}; got {status!r}."
        )

    if status == "recorded":
        if record.sha256 is None:
            raise EmbeddingProvenanceError(
                "hash.sha256 is required when hash.status is recorded."
            )
        sha256 = _normalize_sha256(record.sha256, "hash.sha256")
    else:
        if record.sha256 not in (None, ""):
            raise EmbeddingProvenanceError(
                "hash.sha256 must be empty while hash.status is pending."
            )
        sha256 = None

    return ProvenanceHash(
        name=name,
        source=source,
        status=status,
        sha256=sha256,
    )


def validate_embedding_provenance_manifest(
    manifest: EmbeddingProvenanceManifest,
) -> EmbeddingProvenanceManifest:
    """Validate metadata-only Stage 2 embedding provenance."""

    dataset_id = _clean_required_string(manifest.dataset_id, "dataset_id")
    census_version = _clean_required_string(manifest.census_version, "census_version")

    if dataset_id != PRIMARY_CELLXGENE_DATASET_ID:
        raise EmbeddingProvenanceError(
            "dataset_id must match the approved primary CELLxGENE contract."
        )
    if census_version != PRIMARY_CELLXGENE_CENSUS_VERSION:
        raise EmbeddingProvenanceError(
            "census_version must match the approved primary CELLxGENE contract."
        )

    if manifest.extraction_performed:
        raise EmbeddingProvenanceError(
            "Stage 2 provenance contract must not mark extraction as performed."
        )
    if manifest.allow_downloads:
        raise EmbeddingProvenanceError("Stage 2 provenance must keep downloads disabled.")
    if manifest.allow_anndata_loading:
        raise EmbeddingProvenanceError(
            "Stage 2 provenance must keep AnnData loading disabled."
        )
    if manifest.allow_geneformer_execution:
        raise EmbeddingProvenanceError(
            "Stage 2 provenance must keep Geneformer execution disabled."
        )
    if manifest.allow_tokenizer_execution:
        raise EmbeddingProvenanceError(
            "Stage 2 provenance must keep tokenizer execution disabled."
        )
    if manifest.allow_embedding_extraction:
        raise EmbeddingProvenanceError(
            "Stage 2 provenance must keep embedding extraction disabled."
        )
    if manifest.allow_modeling:
        raise EmbeddingProvenanceError("Stage 2 provenance must keep modeling disabled.")
    if manifest.allow_training:
        raise EmbeddingProvenanceError("Stage 2 provenance must keep training disabled.")
    if manifest.allow_external_validation:
        raise EmbeddingProvenanceError(
            "Stage 2 provenance must keep external validation disabled."
        )
    if manifest.performance_claims_added:
        raise EmbeddingProvenanceError(
            "Stage 2 provenance must not add performance claims."
        )

    return EmbeddingProvenanceManifest(
        dataset_id=dataset_id,
        source=_clean_required_string(manifest.source, "source"),
        census_version=census_version,
        donor_column=_clean_required_string(manifest.donor_column, "donor_column"),
        gene_symbol_column=_clean_required_string(
            manifest.gene_symbol_column,
            "gene_symbol_column",
        ),
        gene_id_policy=_clean_required_string(manifest.gene_id_policy, "gene_id_policy"),
        model_name_or_path=_clean_required_string(
            manifest.model_name_or_path,
            "model_name_or_path",
        ),
        model_revision=_clean_required_string(
            manifest.model_revision,
            "model_revision",
        ),
        model_config_hash=validate_provenance_hash(manifest.model_config_hash),
        tokenizer_name_or_path=_clean_required_string(
            manifest.tokenizer_name_or_path,
            "tokenizer_name_or_path",
        ),
        tokenizer_hash=validate_provenance_hash(manifest.tokenizer_hash),
        vocabulary_source=_clean_required_string(
            manifest.vocabulary_source,
            "vocabulary_source",
        ),
        vocabulary_hash=validate_provenance_hash(manifest.vocabulary_hash),
        embedding_config_hash=validate_provenance_hash(
            manifest.embedding_config_hash,
        ),
        cells_per_donor=_require_positive_int(
            manifest.cells_per_donor,
            "cells_per_donor",
        ),
        max_sequence_length=_require_positive_int(
            manifest.max_sequence_length,
            "max_sequence_length",
        ),
        batch_size=_require_positive_int(manifest.batch_size, "batch_size"),
        random_seed=_require_non_negative_int(manifest.random_seed, "random_seed"),
        split_level=_clean_required_string(manifest.split_level, "split_level"),
        patient_aggregation=_clean_required_string(
            manifest.patient_aggregation,
            "patient_aggregation",
        ),
        output_root=_clean_required_string(manifest.output_root, "output_root"),
        config_path=_clean_required_string(manifest.config_path, "config_path"),
        provenance_path=_clean_required_string(
            manifest.provenance_path,
            "provenance_path",
        ),
        embeddings_path=_clean_required_string(
            manifest.embeddings_path,
            "embeddings_path",
        ),
        sampled_cell_ids_path=_clean_required_string(
            manifest.sampled_cell_ids_path,
            "sampled_cell_ids_path",
        ),
        extraction_performed=False,
        allow_downloads=False,
        allow_anndata_loading=False,
        allow_geneformer_execution=False,
        allow_tokenizer_execution=False,
        allow_embedding_extraction=False,
        allow_modeling=False,
        allow_training=False,
        allow_external_validation=False,
        performance_claims_added=False,
        notes=str(manifest.notes),
    )


def make_embedding_provenance_from_config(
    config: EmbeddingExtractionConfig,
) -> EmbeddingProvenanceManifest:
    """Create pending-runtime provenance from a validated embedding config."""

    validated = validate_embedding_config(config)

    return validate_embedding_provenance_manifest(
        EmbeddingProvenanceManifest(
            dataset_id=validated.dataset_id,
            source=validated.source,
            census_version=validated.census_version,
            donor_column=validated.donor_column,
            gene_symbol_column=validated.gene_symbol_column,
            gene_id_policy=validated.gene_id_policy,
            model_name_or_path=validated.model_name_or_path,
            model_revision=validated.model_revision,
            model_config_hash=ProvenanceHash(
                name="model_config",
                source=validated.model_name_or_path,
            ),
            tokenizer_name_or_path=validated.tokenizer_name_or_path,
            tokenizer_hash=ProvenanceHash(
                name="tokenizer",
                source=validated.tokenizer_name_or_path,
            ),
            vocabulary_source=validated.vocabulary_source,
            vocabulary_hash=ProvenanceHash(
                name="vocabulary",
                source=validated.vocabulary_source,
            ),
            embedding_config_hash=ProvenanceHash(
                name="embedding_config",
                source=validated.output_paths.config,
            ),
            cells_per_donor=validated.cells_per_donor,
            max_sequence_length=validated.max_sequence_length,
            batch_size=validated.batch_size,
            random_seed=validated.random_seed,
            split_level=validated.split_level,
            patient_aggregation=validated.patient_aggregation,
            output_root=validated.output_paths.root,
            config_path=validated.output_paths.config,
            provenance_path=validated.output_paths.provenance,
            embeddings_path=validated.output_paths.embeddings,
            sampled_cell_ids_path=validated.output_paths.sampled_cell_ids,
            notes="Pending runtime hash resolution; no extraction performed.",
        )
    )


def validate_embedding_provenance_against_config(
    provenance: EmbeddingProvenanceManifest,
    config: EmbeddingExtractionConfig,
) -> None:
    """Validate provenance consistency against an embedding config object."""

    validated_provenance = validate_embedding_provenance_manifest(provenance)
    validated_config = validate_embedding_config(config)

    comparisons = {
        "dataset_id": (validated_provenance.dataset_id, validated_config.dataset_id),
        "census_version": (
            validated_provenance.census_version,
            validated_config.census_version,
        ),
        "donor_column": (
            validated_provenance.donor_column,
            validated_config.donor_column,
        ),
        "gene_symbol_column": (
            validated_provenance.gene_symbol_column,
            validated_config.gene_symbol_column,
        ),
        "gene_id_policy": (
            validated_provenance.gene_id_policy,
            validated_config.gene_id_policy,
        ),
        "model_name_or_path": (
            validated_provenance.model_name_or_path,
            validated_config.model_name_or_path,
        ),
        "model_revision": (
            validated_provenance.model_revision,
            validated_config.model_revision,
        ),
        "tokenizer_name_or_path": (
            validated_provenance.tokenizer_name_or_path,
            validated_config.tokenizer_name_or_path,
        ),
        "vocabulary_source": (
            validated_provenance.vocabulary_source,
            validated_config.vocabulary_source,
        ),
        "cells_per_donor": (
            validated_provenance.cells_per_donor,
            validated_config.cells_per_donor,
        ),
        "max_sequence_length": (
            validated_provenance.max_sequence_length,
            validated_config.max_sequence_length,
        ),
        "batch_size": (validated_provenance.batch_size, validated_config.batch_size),
        "random_seed": (
            validated_provenance.random_seed,
            validated_config.random_seed,
        ),
        "split_level": (validated_provenance.split_level, validated_config.split_level),
        "patient_aggregation": (
            validated_provenance.patient_aggregation,
            validated_config.patient_aggregation,
        ),
        "output_root": (
            validated_provenance.output_root,
            validated_config.output_paths.root,
        ),
        "config_path": (
            validated_provenance.config_path,
            validated_config.output_paths.config,
        ),
        "provenance_path": (
            validated_provenance.provenance_path,
            validated_config.output_paths.provenance,
        ),
        "embeddings_path": (
            validated_provenance.embeddings_path,
            validated_config.output_paths.embeddings,
        ),
        "sampled_cell_ids_path": (
            validated_provenance.sampled_cell_ids_path,
            validated_config.output_paths.sampled_cell_ids,
        ),
    }

    mismatches = tuple(
        field_name
        for field_name, (provenance_value, config_value) in comparisons.items()
        if provenance_value != config_value
    )
    if mismatches:
        mismatch_text = ", ".join(mismatches)
        raise EmbeddingProvenanceError(
            f"Embedding provenance does not match config: {mismatch_text}."
        )


def make_embedding_provenance_from_mapping(
    row: Mapping[str, Any],
) -> EmbeddingProvenanceManifest:
    """Create and validate provenance from mapping-like metadata."""

    def hash_record(name: str) -> ProvenanceHash:
        raw = row.get(name)
        if not isinstance(raw, Mapping):
            raise EmbeddingProvenanceError(f"{name} must be a mapping.")
        return ProvenanceHash(
            name=raw.get("name", ""),
            source=raw.get("source", ""),
            status=raw.get("status", "pending_runtime_resolution"),
            sha256=raw.get("sha256"),
        )

    manifest = EmbeddingProvenanceManifest(
        dataset_id=row.get("dataset_id", ""),
        source=row.get("source", ""),
        census_version=row.get("census_version", ""),
        donor_column=row.get("donor_column", ""),
        gene_symbol_column=row.get("gene_symbol_column", ""),
        gene_id_policy=row.get("gene_id_policy", ""),
        model_name_or_path=row.get("model_name_or_path", ""),
        model_revision=row.get("model_revision", ""),
        model_config_hash=hash_record("model_config_hash"),
        tokenizer_name_or_path=row.get("tokenizer_name_or_path", ""),
        tokenizer_hash=hash_record("tokenizer_hash"),
        vocabulary_source=row.get("vocabulary_source", ""),
        vocabulary_hash=hash_record("vocabulary_hash"),
        embedding_config_hash=hash_record("embedding_config_hash"),
        cells_per_donor=row.get("cells_per_donor", 0),
        max_sequence_length=row.get("max_sequence_length", 0),
        batch_size=row.get("batch_size", 0),
        random_seed=row.get("random_seed", 0),
        split_level=row.get("split_level", ""),
        patient_aggregation=row.get("patient_aggregation", ""),
        output_root=row.get("output_root", ""),
        config_path=row.get("config_path", ""),
        provenance_path=row.get("provenance_path", ""),
        embeddings_path=row.get("embeddings_path", ""),
        sampled_cell_ids_path=row.get("sampled_cell_ids_path", ""),
        extraction_performed=_as_bool(row.get("extraction_performed", False)),
        allow_downloads=_as_bool(row.get("allow_downloads", False)),
        allow_anndata_loading=_as_bool(row.get("allow_anndata_loading", False)),
        allow_geneformer_execution=_as_bool(
            row.get("allow_geneformer_execution", False)
        ),
        allow_tokenizer_execution=_as_bool(
            row.get("allow_tokenizer_execution", False)
        ),
        allow_embedding_extraction=_as_bool(
            row.get("allow_embedding_extraction", False)
        ),
        allow_modeling=_as_bool(row.get("allow_modeling", False)),
        allow_training=_as_bool(row.get("allow_training", False)),
        allow_external_validation=_as_bool(
            row.get("allow_external_validation", False)
        ),
        performance_claims_added=_as_bool(
            row.get("performance_claims_added", False)
        ),
        notes=row.get("notes", ""),
    )

    return validate_embedding_provenance_manifest(manifest)


def embedding_provenance_to_dict(
    manifest: EmbeddingProvenanceManifest,
) -> dict[str, Any]:
    """Serialize a validated provenance manifest to a plain dictionary."""

    return asdict(validate_embedding_provenance_manifest(manifest))
