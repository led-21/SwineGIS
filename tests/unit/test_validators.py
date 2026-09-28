# -*- coding: utf-8 -*-
"""Unit tests for input validators."""

import pytest
from core.domain.models import FacilitySpecification, FacilityType, ShapeType
from core.domain.validators import validate_specification, ValidationError


def test_validator_valid_rectangular_spec():
    """Valid rectangular specification passes without raising."""
    spec = FacilitySpecification(
        facility_type=FacilityType.FINISHING,
        shape_type=ShapeType.RECTANGULAR,
        length=80.0,
        width=12.0,
        count=2,
        spacing=15.0,
    )
    warnings = validate_specification(spec)
    assert isinstance(warnings, list)
    assert len(warnings) == 0


def test_validator_invalid_count():
    """Negative or zero count raises ValidationError."""
    with pytest.raises(ValidationError, match="no mínimo 1"):
        validate_specification(
            FacilitySpecification(
                facility_type=FacilityType.FINISHING,
                shape_type=ShapeType.RECTANGULAR,
                length=50.0,
                width=10.0,
                count=0,
            )
        )


def test_validator_invalid_dimensions():
    """Zero or negative length/width raises ValidationError."""
    with pytest.raises(ValidationError, match="comprimento.*maior que zero"):
        validate_specification(
            FacilitySpecification(
                facility_type=FacilityType.FINISHING,
                shape_type=ShapeType.RECTANGULAR,
                length=0.0,
                width=10.0,
            )
        )

    with pytest.raises(ValidationError, match="largura.*maior que zero"):
        validate_specification(
            FacilitySpecification(
                facility_type=FacilityType.FINISHING,
                shape_type=ShapeType.RECTANGULAR,
                length=50.0,
                width=-5.0,
            )
        )


def test_validator_circular_dimensions():
    """Invalid circle radius raises ValidationError."""
    with pytest.raises(ValidationError, match="raio.*maior que zero"):
        validate_specification(
            FacilitySpecification(
                facility_type=FacilityType.FEED_SILO,
                shape_type=ShapeType.CIRCULAR,
                radius=0.0,
            )
        )


def test_validator_spacing_warning():
    """Spacing smaller than recommended triggers advisory warning."""
    spec = FacilitySpecification(
        facility_type=FacilityType.FINISHING,
        shape_type=ShapeType.RECTANGULAR,
        length=100.0,
        width=12.0,
        count=3,
        spacing=5.0,  # Below recommended 15m
    )
    warnings = validate_specification(spec)
    assert len(warnings) > 0
    assert any("inferior ao mínimo recomendado" in w for w in warnings)
