# -*- coding: utf-8 -*-
"""Service orchestrating domain validation, calculations and geometric planning."""

import math
from typing import List, Optional
from ..domain.models import (
    FacilitySpecification,
    ShapeType,
    CalculatedMetrics,
    PlannedFacility,
    PlanningResult,
)
from ..domain.standards import SWINE_STANDARDS
from ..domain.validators import validate_specification
from ..geometry.builders import (
    build_rectangle_polygon,
    build_circle_polygon,
    build_buffered_polygon,
    calculate_series_positions,
)


class SwineFacilityPlannerService:
    """Core domain service to compute dimensions, capacities, and layout geometries."""

    @classmethod
    def calculate_metrics(cls, spec: FacilitySpecification) -> CalculatedMetrics:
        """Calculate technical indicators, capacities and agronomic buffers."""
        warnings = validate_specification(spec)
        standards = SWINE_STANDARDS.get(spec.facility_type, {})

        # Compute single unit footprint
        if spec.shape_type == ShapeType.RECTANGULAR:
            unit_footprint = spec.length * spec.width
        else:
            unit_footprint = math.pi * (spec.radius ** 2)

        total_footprint = unit_footprint * spec.count

        # Estimate animal capacity if applicable
        m2_per_head = standards.get("m2_per_head")
        estimated_capacity: Optional[int] = None
        if m2_per_head and m2_per_head > 0:
            # Capacity per unit and total
            capacity_per_unit = int(unit_footprint / m2_per_head)
            estimated_capacity = capacity_per_unit * spec.count

        recommended_buffer = float(standards.get("recommended_buffer_m", 50.0))
        sanitary_isolation = float(standards.get("sanitary_isolation_m", 100.0))
        recommended_spacing = float(standards.get("min_spacing_between_sheds", 15.0))

        return CalculatedMetrics(
            unit_footprint_m2=round(unit_footprint, 2),
            total_footprint_m2=round(total_footprint, 2),
            estimated_capacity_heads=estimated_capacity,
            recommended_buffer_m=recommended_buffer,
            sanitary_isolation_m=sanitary_isolation,
            recommended_spacing_m=recommended_spacing,
            warnings=warnings,
        )

    @classmethod
    def plan_layout(
        cls,
        spec: FacilitySpecification,
        crs_auth_id: str = "EPSG:4326"
    ) -> PlanningResult:
        """Generate full spatial plan with geometries and agronomic buffers."""
        metrics = cls.calculate_metrics(spec)

        # Determine breadth for series spacing (width for rectangle, diameter for circle)
        if spec.shape_type == ShapeType.RECTANGULAR:
            unit_breadth = spec.width
        else:
            unit_breadth = spec.radius * 2.0

        # Calculate unit centers (distribution axis perpendicular to shed orientation by default)
        distribution_axis_deg = spec.rotation_deg + 90.0
        centers = calculate_series_positions(
            start_x=spec.center_x,
            start_y=spec.center_y,
            count=spec.count,
            unit_breadth=unit_breadth,
            spacing=spec.spacing,
            axis_rotation_deg=distribution_axis_deg,
        )

        m2_per_head = SWINE_STANDARDS.get(spec.facility_type, {}).get("m2_per_head")
        unit_capacity: Optional[int] = None
        if m2_per_head and m2_per_head > 0:
            unit_capacity = int(metrics.unit_footprint_m2 / m2_per_head)

        facilities: List[PlannedFacility] = []

        for idx, (cx, cy) in enumerate(centers, start=1):
            identifier = f"{spec.facility_type.name}_{idx:02d}"

            if spec.shape_type == ShapeType.RECTANGULAR:
                polygon = build_rectangle_polygon(
                    center_x=cx,
                    center_y=cy,
                    length=spec.length,
                    width=spec.width,
                    rotation_deg=spec.rotation_deg,
                )
            else:
                polygon = build_circle_polygon(
                    center_x=cx,
                    center_y=cy,
                    radius=spec.radius,
                )

            # Build sanitary buffer polygon around facility
            buffer_poly = build_buffered_polygon(
                polygon,
                buffer_distance=metrics.recommended_buffer_m
            )

            facilities.append(
                PlannedFacility(
                    identifier=identifier,
                    facility_type=spec.facility_type,
                    shape_type=spec.shape_type,
                    unit_index=idx,
                    center_x=cx,
                    center_y=cy,
                    footprint_m2=metrics.unit_footprint_m2,
                    capacity_heads=unit_capacity,
                    polygon_coords=polygon,
                    buffer_polygon_coords=buffer_poly,
                )
            )

        return PlanningResult(
            specification=spec,
            metrics=metrics,
            facilities=facilities,
            crs_auth_id=crs_auth_id,
        )
