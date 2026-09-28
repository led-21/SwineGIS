# -*- coding: utf-8 -*-
"""Unit tests for agronomic standards."""

from core.domain.models import FacilityType
from core.domain.standards import SWINE_STANDARDS


def test_standards_contain_all_facility_types():
    """Verify all facility types have calibrated standard defaults."""
    for ftype in FacilityType:
        assert ftype in SWINE_STANDARDS
        std = SWINE_STANDARDS[ftype]
        assert "recommended_buffer_m" in std
        assert "sanitary_isolation_m" in std
        assert "min_spacing_between_sheds" in std
        assert std["recommended_buffer_m"] > 0
        assert std["sanitary_isolation_m"] >= std["recommended_buffer_m"]


def test_animal_housing_specific_standards():
    """Verify housing types define m2 per head according to technical standards."""
    assert SWINE_STANDARDS[FacilityType.FINISHING]["m2_per_head"] == 1.00
    assert SWINE_STANDARDS[FacilityType.NURSERY]["m2_per_head"] == 0.35
    assert SWINE_STANDARDS[FacilityType.GESTATION]["m2_per_head"] == 2.50
    assert SWINE_STANDARDS[FacilityType.FARROWING]["m2_per_head"] == 4.50

    # Non-animal facilities should not have animal housing densities
    assert SWINE_STANDARDS[FacilityType.FEED_SILO]["m2_per_head"] is None
    assert SWINE_STANDARDS[FacilityType.MANURE_LAGOON]["m2_per_head"] is None
