"""Ingestion-readiness reporting utilities.

These helpers combine lightweight schema, cohort, and gene-annotation checks
before any downstream embedding extraction or modeling is allowed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from lupusfm.data.anndata_schema import (
    AnnDataSchemaContract,
    AnnDataSchemaReport,
    PROJECT_INGESTION_SCHEMA,
    validate_anndata_schema,
)
from lupusfm.data.cohort import CohortSummary, summarize_cohort_from_obs
from lupusfm.data.metadata import DEFAULT_DONOR_COLUMN
from lupusfm.qc.mitochondrial import (
    DEFAULT_MITO_PREFIX,
    summarize_mitochondrial_gene_annotation,
)


DEFAULT_GENE_SYMBOL_COLUMN = "gene_symbol"


@dataclass(frozen=True)
class ReadinessCheck:
    """One ingestion-readiness check result."""

    name: str
    passed: bool
    message: str


@dataclass(frozen=True)
class IngestionReadinessReport:
    """Combined readiness report for one AnnData-like object."""

    schema_report: AnnDataSchemaReport | None
    cohort_summary: CohortSummary | None
    mitochondrial_gene_summary: dict[str, int] | None
    checks: tuple[ReadinessCheck, ...]

    @property
    def is_ready(self) -> bool:
        """Return True only when every readiness check passed."""

        return all(check.passed for check in self.checks)

    @property
    def failed_checks(self) -> tuple[ReadinessCheck, ...]:
        """Return failed readiness checks preserving execution order."""

        return tuple(check for check in self.checks if not check.passed)


def _passed(name: str, message: str) -> ReadinessCheck:
    return ReadinessCheck(name=name, passed=True, message=message)


def _failed(name: str, error: Exception | str) -> ReadinessCheck:
    if isinstance(error, Exception):
        message = f"{type(error).__name__}: {error}"
    else:
        message = error
    return ReadinessCheck(name=name, passed=False, message=message)


def build_ingestion_readiness_report(
    adata: Any,
    *,
    schema_contract: AnnDataSchemaContract = PROJECT_INGESTION_SCHEMA,
    donor_column: str = DEFAULT_DONOR_COLUMN,
    gene_symbol_column: str | None = DEFAULT_GENE_SYMBOL_COLUMN,
    mito_prefix: str = DEFAULT_MITO_PREFIX,
    minimum_donors: int = 1,
    require_mitochondrial_genes: bool = False,
) -> IngestionReadinessReport:
    """Build an ingestion-readiness report without mutating ``adata``.

    The report combines:

    - lightweight AnnData-like schema validation
    - donor/cell cohort summary
    - explicit gene-symbol mitochondrial annotation summary

    This function does not load files, filter cells, extract embeddings, train
    models, or download data.
    """

    checks: list[ReadinessCheck] = []
    schema_report: AnnDataSchemaReport | None = None
    cohort_summary: CohortSummary | None = None
    mitochondrial_gene_summary: dict[str, int] | None = None

    try:
        schema_report = validate_anndata_schema(adata, schema_contract)
        checks.append(
            _passed(
                "anndata_schema",
                f"validated {schema_report.n_obs} cells x {schema_report.n_vars} genes",
            )
        )
    except Exception as exc:  # noqa: BLE001 - report should collect validation failures
        checks.append(_failed("anndata_schema", exc))

    try:
        cohort_summary = summarize_cohort_from_obs(adata, donor_column=donor_column)
        if cohort_summary.total_donors < minimum_donors:
            checks.append(
                _failed(
                    "cohort_summary",
                    (
                        f"expected at least {minimum_donors} donor(s), "
                        f"got {cohort_summary.total_donors}"
                    ),
                )
            )
        else:
            checks.append(
                _passed(
                    "cohort_summary",
                    (
                        f"summarized {cohort_summary.total_donors} donor(s) "
                        f"and {cohort_summary.total_cells} cell(s)"
                    ),
                )
            )
    except Exception as exc:  # noqa: BLE001 - report should collect validation failures
        checks.append(_failed("cohort_summary", exc))

    try:
        mitochondrial_gene_summary = summarize_mitochondrial_gene_annotation(
            adata,
            gene_symbol_column=gene_symbol_column,
            mito_prefix=mito_prefix,
        )
        total_genes = mitochondrial_gene_summary["total_gene_count"]
        mito_genes = mitochondrial_gene_summary["mitochondrial_gene_count"]

        if total_genes == 0:
            checks.append(_failed("mitochondrial_annotation", "no genes available"))
        elif require_mitochondrial_genes and mito_genes == 0:
            checks.append(
                _failed(
                    "mitochondrial_annotation",
                    "expected at least one mitochondrial gene",
                )
            )
        else:
            checks.append(
                _passed(
                    "mitochondrial_annotation",
                    f"found {mito_genes} mitochondrial gene(s) among {total_genes} genes",
                )
            )
    except Exception as exc:  # noqa: BLE001 - report should collect validation failures
        checks.append(_failed("mitochondrial_annotation", exc))

    return IngestionReadinessReport(
        schema_report=schema_report,
        cohort_summary=cohort_summary,
        mitochondrial_gene_summary=mitochondrial_gene_summary,
        checks=tuple(checks),
    )
