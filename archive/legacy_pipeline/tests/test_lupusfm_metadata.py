import math

import pytest

from lupusfm.data.labels import ClinicalStatus
from lupusfm.data.metadata import (
    extract_donor_ids,
    get_obs_column_values,
    make_donor_labels_from_obs,
    require_obs_columns,
)


class FakeAnnData:
    def __init__(self, obs):
        self.obs = obs


def test_require_obs_columns_accepts_mapping_obs():
    adata = FakeAnnData(obs={"donor_id": ["FLARE1"], "cell_type": ["B cell"]})

    assert require_obs_columns(adata, ["donor_id", "cell_type"]) == (
        "donor_id",
        "cell_type",
    )


def test_require_obs_columns_rejects_missing_column():
    adata = FakeAnnData(obs={"cell_type": ["B cell"]})

    with pytest.raises(ValueError, match="Missing required adata.obs column"):
        require_obs_columns(adata, ["donor_id"])


def test_require_obs_columns_rejects_objects_without_obs():
    with pytest.raises(TypeError, match=r"\.obs"):
        require_obs_columns(object(), ["donor_id"])


def test_get_obs_column_values_returns_plain_list():
    adata = FakeAnnData(obs={"donor_id": ("FLARE1", "123")})

    assert get_obs_column_values(adata, "donor_id") == ["FLARE1", "123"]


def test_extract_donor_ids_preserves_first_seen_order_and_deduplicates():
    adata = FakeAnnData(
        obs={"donor_id": ["FLARE1", "123", "FLARE1", "IGTB1", "123"]}
    )

    assert extract_donor_ids(adata) == ["FLARE1", "123", "IGTB1"]


def test_extract_donor_ids_normalizes_whitespace():
    adata = FakeAnnData(obs={"donor_id": ["  HC-001  "]})

    assert extract_donor_ids(adata) == ["HC-001"]


@pytest.mark.parametrize("bad_donor_id", [None, math.nan])
def test_extract_donor_ids_rejects_missing_values(bad_donor_id):
    adata = FakeAnnData(obs={"donor_id": ["FLARE1", bad_donor_id]})

    with pytest.raises(ValueError, match="Missing donor id"):
        extract_donor_ids(adata)


def test_extract_donor_ids_rejects_empty_values():
    adata = FakeAnnData(obs={"donor_id": ["FLARE1", "   "]})

    with pytest.raises(ValueError, match="donor_id"):
        extract_donor_ids(adata)


def test_make_donor_labels_from_obs_applies_approved_label_rule():
    adata = FakeAnnData(obs={"donor_id": ["FLARE1", "123", "IGTB1", "HC-001"]})

    labels = make_donor_labels_from_obs(adata)

    assert [label.donor_id for label in labels] == ["FLARE1", "123", "IGTB1", "HC-001"]
    assert [label.clinical_status for label in labels] == [
        ClinicalStatus.FLARE,
        ClinicalStatus.MANAGED,
        ClinicalStatus.HEALTHY,
        ClinicalStatus.HEALTHY,
    ]


def test_make_donor_labels_from_obs_fails_closed_for_unknown_donors():
    adata = FakeAnnData(obs={"donor_id": ["FLARE1", "SLE-001"]})

    with pytest.raises(ValueError, match="Unrecognized donor_id pattern"):
        make_donor_labels_from_obs(adata)
