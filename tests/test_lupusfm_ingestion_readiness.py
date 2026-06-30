from lupusfm.data.anndata_schema import AnnDataSchemaContract
from lupusfm.data.ingestion_readiness import (
    IngestionReadinessReport,
    ReadinessCheck,
    build_ingestion_readiness_report,
)
from lupusfm.data.labels import ClinicalStatus


class FakeMatrix:
    def __init__(self, shape):
        self.shape = shape


class FakeAnnData:
    def __init__(self, obs, var, X=None, layers=None, uns=None):
        self.obs = obs
        self.var = var
        self.X = X
        self.layers = layers or {}
        self.uns = uns or {}


def valid_contract():
    return AnnDataSchemaContract(
        required_obs_columns=("donor_id", "cell_type", "split_group"),
        required_var_columns=("gene_symbol", "feature_type"),
        required_uns_keys=("dataset_id",),
        required_layers=("counts",),
        split_column="split_group",
        allowed_split_values=("patient_level", "cohort_level"),
    )


def valid_adata():
    return FakeAnnData(
        obs={
            "donor_id": ["FLARE1", "FLARE1", "123", "HC-001"],
            "cell_type": ["B cell", "T cell", "monocyte", "NK cell"],
            "split_group": [
                "patient_level",
                "patient_level",
                "cohort_level",
                "cohort_level",
            ],
        },
        var={
            "gene_symbol": ["MT-CO1", "IFI44L", "MX1"],
            "feature_type": [
                "Gene Expression",
                "Gene Expression",
                "Gene Expression",
            ],
        },
        X=FakeMatrix((4, 3)),
        layers={"counts": FakeMatrix((4, 3))},
        uns={"dataset_id": "mock-dataset"},
    )


def test_build_ingestion_readiness_report_accepts_valid_object():
    report = build_ingestion_readiness_report(
        valid_adata(),
        schema_contract=valid_contract(),
        require_mitochondrial_genes=True,
    )

    assert isinstance(report, IngestionReadinessReport)
    assert report.is_ready is True
    assert report.failed_checks == ()
    assert [check.name for check in report.checks] == [
        "anndata_schema",
        "cohort_summary",
        "mitochondrial_annotation",
    ]
    assert report.schema_report is not None
    assert report.schema_report.n_obs == 4
    assert report.schema_report.n_vars == 3
    assert report.cohort_summary is not None
    assert report.cohort_summary.total_donors == 3
    assert report.cohort_summary.total_cells == 4
    assert report.mitochondrial_gene_summary == {
        "total_gene_count": 3,
        "mitochondrial_gene_count": 1,
        "non_mitochondrial_gene_count": 2,
    }


def test_report_properties_expose_failed_checks():
    report = IngestionReadinessReport(
        schema_report=None,
        cohort_summary=None,
        mitochondrial_gene_summary=None,
        checks=(
            ReadinessCheck("first", True, "ok"),
            ReadinessCheck("second", False, "bad"),
        ),
    )

    assert report.is_ready is False
    assert report.failed_checks == (ReadinessCheck("second", False, "bad"),)


def test_report_collects_schema_failure_without_raising():
    adata = valid_adata()
    adata.X = FakeMatrix((2, 3))

    report = build_ingestion_readiness_report(
        adata,
        schema_contract=valid_contract(),
    )

    assert report.is_ready is False
    assert report.schema_report is None
    assert report.failed_checks[0].name == "anndata_schema"
    assert "X must have shape" in report.failed_checks[0].message


def test_report_collects_unknown_donor_label_failure():
    adata = valid_adata()
    adata.obs["donor_id"] = ["FLARE1", "SLE-001", "123", "HC-001"]

    report = build_ingestion_readiness_report(
        adata,
        schema_contract=valid_contract(),
    )

    assert report.is_ready is False
    failed_names = [check.name for check in report.failed_checks]
    assert failed_names == ["cohort_summary"]
    assert "Unrecognized donor_id pattern" in report.failed_checks[0].message


def test_report_enforces_minimum_donor_count():
    adata = valid_adata()
    adata.obs["donor_id"] = ["FLARE1", "FLARE1", "FLARE1", "FLARE1"]

    report = build_ingestion_readiness_report(
        adata,
        schema_contract=valid_contract(),
        minimum_donors=2,
    )

    assert report.is_ready is False
    assert report.cohort_summary is not None
    assert report.cohort_summary.total_donors == 1
    assert report.failed_checks == (
        ReadinessCheck(
            "cohort_summary",
            False,
            "expected at least 2 donor(s), got 1",
        ),
    )


def test_report_rejects_cell_level_split_assignments():
    adata = valid_adata()
    adata.obs["split_group"] = [
        "patient_level",
        "cell_level",
        "cohort_level",
        "cohort_level",
    ]

    report = build_ingestion_readiness_report(
        adata,
        schema_contract=valid_contract(),
    )

    assert report.is_ready is False
    assert report.failed_checks[0].name == "anndata_schema"
    assert "cell-level split" in report.failed_checks[0].message


def test_report_requires_explicit_gene_symbol_column():
    report = build_ingestion_readiness_report(
        valid_adata(),
        schema_contract=valid_contract(),
        gene_symbol_column=None,
    )

    assert report.is_ready is False
    assert report.failed_checks == (
        ReadinessCheck(
            "mitochondrial_annotation",
            False,
            (
                "MitochondrialGeneAnnotationError: gene_symbol_column must be "
                "provided explicitly; refusing to infer mitochondrial genes from "
                "adata.var_names."
            ),
        ),
    )


def test_report_can_require_at_least_one_mitochondrial_gene():
    adata = valid_adata()
    adata.var["gene_symbol"] = ["IFI44L", "MX1", "ISG15"]

    report = build_ingestion_readiness_report(
        adata,
        schema_contract=valid_contract(),
        require_mitochondrial_genes=True,
    )

    assert report.is_ready is False
    assert report.mitochondrial_gene_summary == {
        "total_gene_count": 3,
        "mitochondrial_gene_count": 0,
        "non_mitochondrial_gene_count": 3,
    }
    assert report.failed_checks == (
        ReadinessCheck(
            "mitochondrial_annotation",
            False,
            "expected at least one mitochondrial gene",
        ),
    )


def test_report_preserves_clinical_status_summary():
    report = build_ingestion_readiness_report(
        valid_adata(),
        schema_contract=valid_contract(),
    )

    assert report.cohort_summary is not None
    status_counts = {
        item.clinical_status: item.n_donors
        for item in report.cohort_summary.clinical_status_counts
    }

    assert status_counts == {
        ClinicalStatus.FLARE: 1,
        ClinicalStatus.MANAGED: 1,
        ClinicalStatus.HEALTHY: 1,
    }
