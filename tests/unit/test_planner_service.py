# -*- coding: utf-8 -*-
"""Unit tests for the SwineFacilityPlannerService."""

import math
from core.domain.models import FacilitySpecification, FacilityType, ShapeType
from core.services.planner import SwineFacilityPlannerService


def test_planner_finishing_facility():
    """Verify metrics and facilities generation for finishing unit."""
    spec = FacilitySpecification(
        facility_type=FacilityType.FINISHING,
        shape_type=ShapeType.RECTANGULAR,
        length=100.0,
        width=12.0,
        count=2,
        spacing=15.0,
        center_x=0.0,
        center_y=0.0,
    )
    result = SwineFacilityPlannerService.plan_layout(spec)

    # 100 * 12 = 1200 m2
    assert result.metrics.unit_footprint_m2 == 1200.0
    # 2 units = 2400 m2
    assert result.metrics.total_footprint_m2 == 2400.0

    # 1.0 m2/head -> 1200 pigs/unit, 2400 pigs total
    assert result.metrics.estimated_capacity_heads == 2400

    assert len(result.facilities) == 2
    assert result.facilities[0].identifier == "FINISHING_01"
    assert result.facilities[1].identifier == "FINISHING_02"
    assert len(result.facilities[0].polygon_coords) == 5
    assert len(result.facilities[0].buffer_polygon_coords) == 5


def test_planner_circular_silo():
    """Verify metrics and facility generation for feed silo."""
    spec = FacilitySpecification(
        facility_type=FacilityType.FEED_SILO,
        shape_type=ShapeType.CIRCULAR,
        radius=4.0,
        count=1,
    )
    result = SwineFacilityPlannerService.plan_layout(spec)

    expected_area = round(math.pi * 16.0, 2)
    assert result.metrics.unit_footprint_m2 == expected_area
    assert result.metrics.estimated_capacity_heads is None
    assert len(result.facilities) == 1
    assert result.facilities[0].identifier == "FEED_SILO_01"
