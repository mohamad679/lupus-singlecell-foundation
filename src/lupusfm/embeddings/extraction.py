"""Permission-gated Geneformer embedding extraction runner.

This module defines the Stage 2 extraction runner interface. It is intentionally
dependency-injected: the module avoids direct runtime-stack imports for Geneformer, tokenizer
runtimes, Scanpy, AnnData, CELLxGENE, or any deep-learning framework.

Runtime work is only possible when explicit execution permission and caller-
provided callbacks are supplied. The default path remains blocked.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass
from typing import Any

from lupusfm.data.ingestion_readiness import IngestionReadinessReport
from lupusfm.data.manifest import IngestionManifest
from lupusfm.embeddings.config import EmbeddingExtractionConfig
from lupusfm.embeddings.provenance import EmbeddingProvenanceManifest
from lupusfm.embeddings.readiness import (
    EmbeddingDryRunReadinessReport,
    require_embedding_dry_run_ready,
)


class GeneformerExtractionRunnerError(ValueError):
    """Raised when extraction runner execution is not explicitly permitted."""


@dataclass(frozen=True)
class GeneformerExtractionPermission:
    """Explicit runtime permission gate for a future extraction run."""

    approved_environment: str = ""
    approved_by: str = ""
    reason: str = ""
    allow_runtime_execution: bool = False
    allow_downloads: bool = False
    allow_anndata_loading: bool = False
    allow_tokenizer_execution: bool = False
    allow_geneformer_execution: bool = False
    allow_embedding_extraction: bool = False
    allow_artifact_write: bool = False
    allow_modeling: bool = False
    allow_training: bool = False
    allow_external_validation: bool = False
    allow_performance_claims: bool = False


@dataclass(frozen=True)
class GeneformerExtractionCallbacks:
    """Caller-provided runtime callbacks for extraction.

    The project package does not implement these callbacks in this feature.
    They must be supplied by a controlled runtime script or notebook after the
    dry-run readiness gate has passed.
    """

    load_anndata: Callable[[], Any]
    sample_cells: Callable[[Any, EmbeddingExtractionConfig], Any]
    tokenize_cells: Callable[[Any, EmbeddingExtractionConfig], Any]
    embed_tokens: Callable[[Any, EmbeddingExtractionConfig], Any]
    write_artifacts: Callable[
        [
            Any,
            EmbeddingExtractionConfig,
            EmbeddingProvenanceManifest,
        ],
        Mapping[str, Any],
    ]


@dataclass(frozen=True)
class GeneformerExtractionRunResult:
    """Result metadata returned by a permitted extraction runner call."""

    extraction_performed: bool
    dry_run_ready: bool
    approved_environment: str
    artifact_paths: Mapping[str, Any]
    callback_order: tuple[str, ...]
    notes: str = ""


def _clean_required_string(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise GeneformerExtractionRunnerError(f"{field_name} must not be empty.")
    return normalized


def _require_true(value: bool, field_name: str) -> None:
    if value is not True:
        raise GeneformerExtractionRunnerError(f"{field_name} must be explicitly true.")


def _require_false(value: bool, field_name: str) -> None:
    if value is not False:
        raise GeneformerExtractionRunnerError(f"{field_name} must remain false.")


def validate_geneformer_extraction_permission(
    permission: GeneformerExtractionPermission,
) -> GeneformerExtractionPermission:
    """Validate explicit permission for runtime extraction.

    Downloads, modeling, training, external validation, and performance claims
    remain prohibited even when extraction itself is explicitly approved.
    """

    approved_environment = _clean_required_string(
        permission.approved_environment,
        "approved_environment",
    )
    approved_by = _clean_required_string(permission.approved_by, "approved_by")
    reason = _clean_required_string(permission.reason, "reason")

    _require_true(permission.allow_runtime_execution, "allow_runtime_execution")
    _require_true(permission.allow_anndata_loading, "allow_anndata_loading")
    _require_true(permission.allow_tokenizer_execution, "allow_tokenizer_execution")
    _require_true(permission.allow_geneformer_execution, "allow_geneformer_execution")
    _require_true(permission.allow_embedding_extraction, "allow_embedding_extraction")
    _require_true(permission.allow_artifact_write, "allow_artifact_write")

    _require_false(permission.allow_downloads, "allow_downloads")
    _require_false(permission.allow_modeling, "allow_modeling")
    _require_false(permission.allow_training, "allow_training")
    _require_false(permission.allow_external_validation, "allow_external_validation")
    _require_false(permission.allow_performance_claims, "allow_performance_claims")

    return GeneformerExtractionPermission(
        approved_environment=approved_environment,
        approved_by=approved_by,
        reason=reason,
        allow_runtime_execution=True,
        allow_downloads=False,
        allow_anndata_loading=True,
        allow_tokenizer_execution=True,
        allow_geneformer_execution=True,
        allow_embedding_extraction=True,
        allow_artifact_write=True,
        allow_modeling=False,
        allow_training=False,
        allow_external_validation=False,
        allow_performance_claims=False,
    )


def require_geneformer_extraction_callbacks(
    callbacks: GeneformerExtractionCallbacks | None,
) -> GeneformerExtractionCallbacks:
    """Require caller-provided extraction callbacks."""

    if callbacks is None:
        raise GeneformerExtractionRunnerError(
            "Geneformer extraction callbacks must be provided explicitly."
        )

    for field_name, callback in callbacks.__dict__.items():
        if not callable(callback):
            raise GeneformerExtractionRunnerError(
                f"{field_name} must be a callable runtime callback."
            )

    return callbacks


def run_geneformer_embedding_extraction(
    *,
    manifest: IngestionManifest,
    readiness_report: IngestionReadinessReport,
    config: EmbeddingExtractionConfig,
    provenance: EmbeddingProvenanceManifest,
    permission: GeneformerExtractionPermission,
    callbacks: GeneformerExtractionCallbacks | None = None,
) -> GeneformerExtractionRunResult:
    """Run a permission-gated extraction workflow through injected callbacks.

    Execution order:

    1. require the Stage 2 dry-run readiness gate to pass
    2. require explicit runtime extraction permission
    3. require caller-provided callbacks
    4. call load/sample/tokenize/embed/write callbacks in order

    This function does not import or instantiate external runtime libraries.
    """

    dry_run_report: EmbeddingDryRunReadinessReport = require_embedding_dry_run_ready(
        manifest=manifest,
        readiness_report=readiness_report,
        config=config,
        provenance=provenance,
    )
    validated_permission = validate_geneformer_extraction_permission(permission)
    validated_callbacks = require_geneformer_extraction_callbacks(callbacks)

    callback_order: list[str] = []

    callback_order.append("load_anndata")
    adata = validated_callbacks.load_anndata()

    callback_order.append("sample_cells")
    sampled_cells = validated_callbacks.sample_cells(adata, config)

    callback_order.append("tokenize_cells")
    tokenized_cells = validated_callbacks.tokenize_cells(sampled_cells, config)

    callback_order.append("embed_tokens")
    embeddings = validated_callbacks.embed_tokens(tokenized_cells, config)

    callback_order.append("write_artifacts")
    artifact_paths = dict(
        validated_callbacks.write_artifacts(
            embeddings,
            config,
            provenance,
        )
    )

    return GeneformerExtractionRunResult(
        extraction_performed=True,
        dry_run_ready=dry_run_report.is_ready,
        approved_environment=validated_permission.approved_environment,
        artifact_paths=artifact_paths,
        callback_order=tuple(callback_order),
        notes=validated_permission.reason,
    )


def geneformer_extraction_run_result_to_dict(
    result: GeneformerExtractionRunResult,
) -> dict[str, Any]:
    """Serialize extraction-run result metadata to a plain dictionary."""

    serialized = asdict(result)
    serialized["artifact_paths"] = dict(result.artifact_paths)
    serialized["callback_order"] = list(result.callback_order)
    return serialized
