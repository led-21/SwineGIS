# -*- coding: utf-8 -*-
"""Domain data models for swine production facilities planning."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple


class ShapeType(str, Enum):
    """Supported facility geometric shapes."""
    RECTANGULAR = "Retangular"
    CIRCULAR = "Circular"


class FacilityType(str, Enum):
    """Typical facilities in swine production units."""
    FINISHING = "Terminação"
    NURSERY = "Creche"
    GESTATION = "Gestação"
    FARROWING = "Maternidade"
    WEAN_TO_FINISH = "Wean-to-Finish"
    QUARANTINE = "Quarentena / Isolamento"
    FEED_SILO = "Silo de Ração"
    MANURE_LAGOON = "Esterqueira / Lagoa de Dejetos"
    COMPOSTING = "Compostagem"


@dataclass(frozen=True)
class FacilitySpecification:
    """User input specification for facility design."""
    facility_type: FacilityType
    shape_type: ShapeType
    length: float = 0.0          # in meters (for rectangular)
    width: float = 0.0           # in meters (for rectangular)
    radius: float = 0.0          # in meters (for circular)
    count: int = 1               # number of repeating units
    spacing: float = 15.0        # spacing distance between units in meters
    center_x: float = 0.0        # initial reference X
    center_y: float = 0.0        # initial reference Y
    rotation_deg: float = 0.0    # rotation relative to East-West axis (0 deg = East-West)


@dataclass(frozen=True)
class CalculatedMetrics:
    """Calculated technical and agronomic indicators."""
    unit_footprint_m2: float
    total_footprint_m2: float
    estimated_capacity_heads: Optional[int]
    recommended_buffer_m: float
    sanitary_isolation_m: float
    recommended_spacing_m: float
    warnings: List[str] = field(default_factory=list)


@dataclass
class PlannedFacility:
    """A single spatial facility instance ready for GIS conversion."""
    identifier: str
    facility_type: FacilityType
    shape_type: ShapeType
    unit_index: int
    center_x: float
    center_y: float
    footprint_m2: float
    capacity_heads: Optional[int]
    polygon_coords: List[Tuple[float, float]]  # List of (x, y) coordinates forming closed polygon
    buffer_polygon_coords: List[Tuple[float, float]] = field(default_factory=list)


@dataclass
class PlanningResult:
    """Overall result of the spatial planning generation."""
    specification: FacilitySpecification
    metrics: CalculatedMetrics
    facilities: List[PlannedFacility]
    crs_auth_id: str = "EPSG:4326"
