import pytest

from lupusfm.data.anndata_schema import (
    AnnDataSchemaContract,
    AnnDataSchemaError,
    AnnDataSchemaReport,
    validate_anndata_schema,
)


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


def make_valid_adata():
    return FakeAnnData(
        obs={
            "donor_id": ["FLARE1", "123", "HC-001"],
            "cell_type": ["B cell", "T cell", "monocyte"],
            "split_group": ["patient_level", "patient_level", "cohort_level"],
        },
        var={
            "gene_symbol": ["IFI44L", "MX1"],
            "feature_type": ["Gene Expression", "Gene Expression"],
        },
        X=FakeMatrix((3, 2)),
        layers={"counts": FakeMatrix((3, 2))},
        uns={"dataset_id": "mock-dataset"},
    )


def test_validate_anndata_schema_accepts_valid_object_and_returns_report():
    contract = AnnDataSchemaContract(
        required_obs_columns=("donor_id", "cell_type"),
        required_var_columns=("gene_symbol", "feature_type"),
        required_uns_keys=("dataset_id",),
        required_layers=("counts",),
        split_column="split_group",
        allowed_split_values=("patient_level", "cohort_level"),
    )

    report = validate_anndata_schema(make_valid_adata(), contract)

    assert report == AnnDataSchemaReport(
        n_obs=3,
        n_vars=2,
        x_shape=(3, 2),
        obs_columns=("donor_id", "cell_type", "split_group"),
        var_columns=("gene_symbol", "feature_type"),
        validated_obs_columns=("donor_id", "cell_type"),
        validated_var_columns=("gene_symbol", "feature_type"),
    )


def test_default_contract_requires_donor_id_gene_symbol_and_x_shape():
    adata = FakeAnnData(
        obs={"donor_id": ["FLARE1"]},
        var={"gene_symbol": ["IFI44L"]},
        X=FakeMatrix((1, 1)),
    )

    report = validate_anndata_schema(adata)

    assert report.n_obs == 1
    assert report.n_vars == 1
    assert report.x_shape == (1, 1)


def test_validate_anndata_schema_rejects_missing_obs():
    adata = object()

    with pytest.raises(AnnDataSchemaError, match="missing .obs"):
        validate_anndata_schema(adata)


def test_validate_anndata_schema_rejects_missing_required_obs_column():
    adata = make_valid_adata()
    adata.obs.pop("donor_id")

    with pytest.raises(AnnDataSchemaError, match="donor_id"):
        validate_anndata_schema(adata)


def test_validate_anndata_schema_rejects_missing_required_var_column():
    adata = make_valid_adata()
    adata.var.pop("gene_symbol")

    with pytest.raises(AnnDataSchemaError, match="gene_symbol"):
        validate_anndata_schema(adata)


def test_validate_anndata_schema_rejects_inconsistent_obs_column_lengths():
    adata = make_valid_adata()
    adata.obs["cell_type"] = ["B cell"]

    with pytest.raises(AnnDataSchemaError, match="obs columns have inconsistent lengths"):
        validate_anndata_schema(adata)


def test_validate_anndata_schema_rejects_x_shape_mismatch():
    adata = make_valid_adata()
    adata.X = FakeMatrix((2, 2))

    with pytest.raises(AnnDataSchemaError, match="X must have shape"):
        validate_anndata_schema(adata)


def test_validate_anndata_schema_rejects_missing_required_layer():
    contract = AnnDataSchemaContract(required_layers=("counts", "log_normalized"))
    adata = make_valid_adata()

    with pytest.raises(AnnDataSchemaError, match="log_normalized"):
        validate_anndata_schema(adata, contract)


def test_validate_anndata_schema_rejects_layer_shape_mismatch():
    contract = AnnDataSchemaContract(required_layers=("counts",))
    adata = make_valid_adata()
    adata.layers["counts"] = FakeMatrix((3, 1))

    with pytest.raises(AnnDataSchemaError, match="Layer 'counts'"):
        validate_anndata_schema(adata, contract)


def test_validate_anndata_schema_rejects_cell_level_split_values():
    contract = AnnDataSchemaContract(split_column="split_group")
    adata = make_valid_adata()
    adata.obs["split_group"] = ["patient_level", "cell_level", "cohort_level"]

    with pytest.raises(AnnDataSchemaError, match="cell-level split"):
        validate_anndata_schema(adata, contract)


def test_validate_anndata_schema_rejects_non_patient_or_cohort_split_values():
    contract = AnnDataSchemaContract(
        split_column="split_group",
        allowed_split_values=("patient_level", "cohort_level"),
    )
    adata = make_valid_adata()
    adata.obs["split_group"] = ["train", "test", "patient_level"]

    with pytest.raises(AnnDataSchemaError, match="patient-level or cohort-level"):
        validate_anndata_schema(adata, contract)


def test_mapping_shape_with_nested_columns_is_supported():
    adata = {
        "obs": {
            "index": ["cell-1", "cell-2"],
            "columns": {
                "donor_id": ["FLARE1", "123"],
                "cell_type": ["B cell", "T cell"],
            },
        },
        "var": {
            "index": ["gene-1"],
            "columns": {
                "gene_symbol": ["IFI44L"],
            },
        },
        "X": {"shape": (2, 1)},
    }

    report = validate_anndata_schema(adata)

    assert report.n_obs == 2
    assert report.n_vars == 1
    assert report.x_shape == (2, 1)
