"""Dry-run readiness checks for future Stage 2 embedding extraction.

These helpers combine existing metadata-only contracts before any runtime
embedding extraction is allowed. They do not load model runtimes, load AnnData
files, download data, tokenize cells, extract embeddings, train models, evaluate
performance, or write artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from lupusfm.data.ingestion_readiness import IngestionReadinessReport
from lupusfm.data.manifest import (
    IngestionManifest,
    IngestionManifestError,
    validate_manifest_against_readiness_report,
)
from lupusfm.embeddings.config import (
    EmbeddingConfigError,
    EmbeddingExtractionConfig,
    validate_embedding_config,
    validate_embedding_config_against_manifest,
)
from lupusfm.embeddings.provenance import (
    EmbeddingProvenanceError,
    EmbeddingProvenanceManifest,
    validate_embedding_provenance_against_config,
    validate_embedding_provenance_manifest,
)


@dataclass(frozen=True)
class EmbeddingDryRunCheck:
    """One dry-run readiness check result."""

    name: str
    passed: bool
    message: str


@dataclass(frozen=True)
class EmbeddingDryRunReadinessReport:
    """Combined dry-run readiness report for future embedding extraction."""

    checks: tuple[EmbeddingDryRunCheck, ...]

    @property
    def is_ready(self) -> bool:
        """Return True only when every dry-run check passed."""

        return all(check.passed for check in self.checks)

    @property
    def failed_checks(self) -> tuple[EmbeddingDryRunCheck, ...]:
        """Return failed dry-run checks preserving execution order."""

        return tuple(check for check in self.checks if not check.passed)


class EmbeddingDryRunReadinessError(ValueError):
    """Raised when dry-run readiness is required but not satisfied."""


def _passed(name: str, message: str) -> EmbeddingDryRunCheck:
    return EmbeddingDryRunCheck(name=name, passed=True, message=message)


def _failed(name: str, error: Exception | str) -> EmbeddingDryRunCheck:
    if isinstance(error, Exception):
        message = f"{type(error).__name__}: {error}"
    else:
        message = error
    return EmbeddingDryRunCheck(name=name, passed=False, message=message)


def _unique_output_paths(config: EmbeddingExtractionConfig) -> None:
    """Ensure metadata/output paths are explicit and non-overlapping."""

    validated = validate_embedding_config(config)
    paths = {
        "config": validated.output_paths.config,
        "provenance": validated.output_paths.provenance,
        "embeddings": validated.output_paths.embeddings,
        "sampled_cell_ids": validated.output_paths.sampled_cell_ids,
    }

    seen: dict[str, str] = {}
    duplicates: list[str] = []
    for name, path in paths.items():
        previous = seen.get(path)
        if previous is not None:
            duplicates.append(f"{previous}={name}={path}")
        seen[path] = name

    if duplicates:
        duplicate_text = ", ".join(duplicates)
        raise EmbeddingDryRunReadinessError(
            f"embedding output paths must be distinct: {duplicate_text}."
        )


def build_embedding_dry_run_readiness_report(
    *,
    manifest: IngestionManifest,
    readiness_report: IngestionReadinessReport,
    config: EmbeddingExtractionConfig,
    provenance: EmbeddingProvenanceManifest,
) -> EmbeddingDryRunReadinessReport:
    """Build a dry-run readiness report without performing extraction.

    The report checks that:

    - Stage 1 ingestion manifest and readiness report agree
    - embedding config satisfies the Stage 2 contract
    - embedding config agrees with the Stage 1 manifest
    - embedding provenance satisfies the Stage 2 provenance contract
    - embedding provenance agrees with the embedding config
    - declared output paths are distinct

    This function intentionally collects failures instead of starting downstream
    runtime work.
    """

    checks: list[EmbeddingDryRunCheck] = []

    try:
        validate_manifest_against_readiness_report(manifest, readiness_report)
        checks.append(
            _passed(
                "manifest_readiness",
                "ingestion manifest matches readiness report",
            )
        )
    except IngestionManifestError as exc:
        checks.append(_failed("manifest_readiness", exc))

    try:
        validate_embedding_config(config)
        checks.append(_passed("embedding_config", "embedding config contract passed"))
    except EmbeddingConfigError as exc:
        checks.append(_failed("embedding_config", exc))

    try:
        validate_embedding_config_against_manifest(config, manifest)
        checks.append(
            _passed(
                "config_manifest_consistency",
                "embedding config matches ingestion manifest",
            )
        )
    except EmbeddingConfigError as exc:
        checks.append(_failed("config_manifest_consistency", exc))

    try:
        validate_embedding_provenance_manifest(provenance)
        checks.append(
            _passed(
                "embedding_provenance",
                "embedding provenance contract passed",
            )
        )
    except EmbeddingProvenanceError as exc:
        checks.append(_failed("embedding_provenance", exc))

    try:
        validate_embedding_provenance_against_config(provenance, config)
        checks.append(
            _passed(
                "provenance_config_consistency",
                "embedding provenance matches embedding config",
            )
        )
    except (EmbeddingProvenanceError, EmbeddingConfigError) as exc:
        checks.append(_failed("provenance_config_consistency", exc))

    try:
        _unique_output_paths(config)
        checks.append(_passed("output_paths", "embedding output paths are distinct"))
    except (EmbeddingDryRunReadinessError, EmbeddingConfigError) as exc:
        checks.append(_failed("output_paths", exc))

    return EmbeddingDryRunReadinessReport(checks=tuple(checks))


def require_embedding_dry_run_ready(
    *,
    manifest: IngestionManifest,
    readiness_report: IngestionReadinessReport,
    config: EmbeddingExtractionConfig,
    provenance: EmbeddingProvenanceManifest,
) -> EmbeddingDryRunReadinessReport:
    """Return a dry-run readiness report or raise if any check failed."""

    report = build_embedding_dry_run_readiness_report(
        manifest=manifest,
        readiness_report=readiness_report,
        config=config,
        provenance=provenance,
    )

    if not report.is_ready:
        failed = ", ".join(check.name for check in report.failed_checks)
        raise EmbeddingDryRunReadinessError(
            f"embedding dry-run readiness failed: {failed}."
        )

    return report


def embedding_dry_run_readiness_to_dict(
    report: EmbeddingDryRunReadinessReport,
) -> dict[str, Any]:
    """Serialize a dry-run readiness report to a plain dictionary."""

    return {
        "is_ready": report.is_ready,
        "checks": [
            {
                "name": check.name,
                "passed": check.passed,
                "message": check.message,
            }
            for check in report.checks
        ],
    }
