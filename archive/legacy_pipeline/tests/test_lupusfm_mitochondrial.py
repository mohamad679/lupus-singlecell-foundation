import pytest

from lupusfm.qc.mitochondrial import (
    MitochondrialGeneAnnotationError,
    count_mitochondrial_genes,
    extract_gene_symbols,
    is_mitochondrial_gene_symbol,
    make_mitochondrial_gene_mask,
    require_explicit_gene_symbol_column,
    require_var_columns,
    summarize_mitochondrial_gene_annotation,
)


class FakeAnnData:
    def __init__(self, var):
        self.var = var


def test_require_var_columns_accepts_mapping_var():
    adata = FakeAnnData(var={"gene_symbol": ["MT-CO1"], "gene_id": ["ENSG1"]})

    assert require_var_columns(adata, ["gene_symbol", "gene_id"]) == (
        "gene_symbol",
        "gene_id",
    )


def test_require_var_columns_rejects_missing_column():
    adata = FakeAnnData(var={"gene_id": ["ENSG1"]})

    with pytest.raises(
        MitochondrialGeneAnnotationError,
        match="Missing required adata.var column",
    ):
        require_var_columns(adata, ["gene_symbol"])


def test_require_var_columns_rejects_objects_without_var():
    with pytest.raises(TypeError, match=r"\.var"):
        require_var_columns(object(), ["gene_symbol"])


@pytest.mark.parametrize("bad_column", [None, "", "   "])
def test_gene_symbol_column_must_be_explicit(bad_column):
    with pytest.raises(MitochondrialGeneAnnotationError, match="gene_symbol_column"):
        require_explicit_gene_symbol_column(bad_column)


def test_extract_gene_symbols_uses_explicit_column_and_normalizes_whitespace():
    adata = FakeAnnData(var={"feature_name": [" MT-CO1 ", " IFI44L "]})

    assert extract_gene_symbols(adata, gene_symbol_column="feature_name") == [
        "MT-CO1",
        "IFI44L",
    ]


def test_extract_gene_symbols_refuses_to_fall_back_to_var_names():
    adata = FakeAnnData(var={"gene_id": ["ENSG00000198804", "ENSG00000137959"]})

    with pytest.raises(
        MitochondrialGeneAnnotationError,
        match="refusing to infer mitochondrial genes from adata.var_names",
    ):
        extract_gene_symbols(adata, gene_symbol_column=None)


@pytest.mark.parametrize(
    ("gene_symbol", "expected"),
    [
        ("MT-CO1", True),
        ("mt-nd1", True),
        ("MTRNR2L12", False),
        ("IFI44L", False),
    ],
)
def test_is_mitochondrial_gene_symbol_uses_prefix_rule(gene_symbol, expected):
    assert is_mitochondrial_gene_symbol(gene_symbol) is expected


@pytest.mark.parametrize("bad_symbol", [None, "", "   "])
def test_is_mitochondrial_gene_symbol_rejects_missing_symbols(bad_symbol):
    with pytest.raises(MitochondrialGeneAnnotationError, match="gene symbol"):
        is_mitochondrial_gene_symbol(bad_symbol)


def test_make_mitochondrial_gene_mask_from_explicit_symbol_column():
    adata = FakeAnnData(var={"gene_symbol": ["MT-CO1", "IFI44L", "MT-ND1"]})

    assert make_mitochondrial_gene_mask(adata, "gene_symbol") == [
        True,
        False,
        True,
    ]


def test_count_mitochondrial_genes_from_explicit_symbol_column():
    adata = FakeAnnData(var={"gene_symbol": ["MT-CO1", "IFI44L", "MT-ND1"]})

    assert count_mitochondrial_genes(adata, "gene_symbol") == 2


def test_summarize_mitochondrial_gene_annotation_does_not_filter_data():
    adata = FakeAnnData(var={"gene_symbol": ["MT-CO1", "IFI44L", "ISG15"]})

    assert summarize_mitochondrial_gene_annotation(adata, "gene_symbol") == {
        "total_gene_count": 3,
        "mitochondrial_gene_count": 1,
        "non_mitochondrial_gene_count": 2,
    }


def test_custom_mitochondrial_prefix_is_supported():
    adata = FakeAnnData(var={"gene_symbol": ["chrM-CO1", "IFI44L"]})

    assert make_mitochondrial_gene_mask(
        adata,
        gene_symbol_column="gene_symbol",
        mito_prefix="chrM-",
    ) == [True, False]
