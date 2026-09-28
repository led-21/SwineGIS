# -*- coding: utf-8 -*-
"""Unit tests for domain models."""

import pytest
from core.domain.models import (
    FacilityType,
    ShapeType,
    FacilitySpecification,
    CalculatedMetrics,
)


def test_facility_type_enum():
    """Verify standard swine facility types are defined."""
    assert FacilityType.FINISHING.value == "Terminação"
    assert FacilityType.NURSERY.value == "Creche"
    assert FacilityType.GESTATION.value == "Gestação"
    assert FacilityType.FARROWING.value == "Maternidade"
    assert FacilityType.FEED_SILO.value == "Silo de Ração"
    assert FacilityType.MANURE_LAGOON.value == "Esterqueira / Lagoa de Dejetos"


def test_facility_specification_instantiation():
    """Verify facility specification creates immutable dataclass."""
    spec = FacilitySpecification(
        facility_type=FacilityType.FINISHING,
        shape_type=ShapeType.RECTANGULAR,
        length=100.0,
        width=12.0,
        count=3,
        spacing=18.0,
        center_x=500000.0,
        center_y=7000000.0,
    )
    assert spec.length == 100.0
    assert spec.width == 12.0
    assert spec.count == 3
    assert spec.spacing == 18.0

    # Ensure immutability
    with pytest.raises(Exception):
        spec.length = 120.0  # type: ignore
