import math

import pytest

from lupusfm.data.cohort import (
    ClinicalStatusCellCount,
    CohortSummary,
    DonorCellCount,
    count_cells_by_donor,
    summarize_clinical_status_counts,
    summarize_cohort_from_obs,
)
from lupusfm.data.labels import ClinicalStatus


class FakeAnnData:
    def __init__(self, obs):
        self.obs = obs


def test_count_cells_by_donor_preserves_first_seen_order_and_counts_cells():
    adata = FakeAnnData(
        obs={"donor_id": ["FLARE1", "123", "FLARE1", "IGTB1", "123", "123"]}
    )

    assert count_cells_by_donor(adata) == [
        DonorCellCount("FLARE1", ClinicalStatus.FLARE, 2),
        DonorCellCount("123", ClinicalStatus.MANAGED, 3),
        DonorCellCount("IGTB1", ClinicalStatus.HEALTHY, 1),
    ]


def test_count_cells_by_donor_normalizes_whitespace():
    adata = FakeAnnData(obs={"donor_id": ["  HC-001  ", "HC-001"]})

    assert count_cells_by_donor(adata) == [
        DonorCellCount("HC-001", ClinicalStatus.HEALTHY, 2),
    ]


@pytest.mark.parametrize("bad_donor_id", [None, math.nan])
def test_count_cells_by_donor_rejects_missing_donor_ids(bad_donor_id):
    adata = FakeAnnData(obs={"donor_id": ["FLARE1", bad_donor_id]})

    with pytest.raises(ValueError, match="Missing donor id"):
        count_cells_by_donor(adata)


def test_count_cells_by_donor_rejects_empty_donor_ids():
    adata = FakeAnnData(obs={"donor_id": ["FLARE1", "   "]})

    with pytest.raises(ValueError, match="donor_id"):
        count_cells_by_donor(adata)


def test_count_cells_by_donor_fails_closed_for_unknown_donor_patterns():
    adata = FakeAnnData(obs={"donor_id": ["FLARE1", "SLE-001"]})

    with pytest.raises(ValueError, match="Unrecognized donor_id pattern"):
        count_cells_by_donor(adata)


def test_summarize_clinical_status_counts_includes_zero_count_groups():
    adata = FakeAnnData(obs={"donor_id": ["FLARE1", "FLARE2", "123"]})

    assert summarize_clinical_status_counts(adata) == [
        ClinicalStatusCellCount(ClinicalStatus.FLARE, n_donors=2, n_cells=2),
        ClinicalStatusCellCount(ClinicalStatus.MANAGED, n_donors=1, n_cells=1),
        ClinicalStatusCellCount(ClinicalStatus.HEALTHY, n_donors=0, n_cells=0),
    ]


def test_summarize_cohort_from_obs_returns_total_donor_and_status_summary():
    adata = FakeAnnData(
        obs={"donor_id": ["FLARE1", "FLARE1", "123", "IGTB1", "HC-001"]}
    )

    summary = summarize_cohort_from_obs(adata)

    assert summary == CohortSummary(
        total_cells=5,
        total_donors=4,
        donor_counts=(
            DonorCellCount("FLARE1", ClinicalStatus.FLARE, 2),
            DonorCellCount("123", ClinicalStatus.MANAGED, 1),
            DonorCellCount("IGTB1", ClinicalStatus.HEALTHY, 1),
            DonorCellCount("HC-001", ClinicalStatus.HEALTHY, 1),
        ),
        clinical_status_counts=(
            ClinicalStatusCellCount(ClinicalStatus.FLARE, n_donors=1, n_cells=2),
            ClinicalStatusCellCount(ClinicalStatus.MANAGED, n_donors=1, n_cells=1),
            ClinicalStatusCellCount(ClinicalStatus.HEALTHY, n_donors=2, n_cells=2),
        ),
    )


def test_custom_donor_column_is_supported():
    adata = FakeAnnData(obs={"patient": ["FLARE1", "123", "123"]})

    assert count_cells_by_donor(adata, donor_column="patient") == [
        DonorCellCount("FLARE1", ClinicalStatus.FLARE, 1),
        DonorCellCount("123", ClinicalStatus.MANAGED, 2),
    ]


def test_missing_donor_column_raises_clear_error():
    adata = FakeAnnData(obs={"cell_type": ["B cell"]})

    with pytest.raises(ValueError, match="Missing required adata.obs column"):
        count_cells_by_donor(adata)
