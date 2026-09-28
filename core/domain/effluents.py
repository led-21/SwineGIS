# -*- coding: utf-8 -*-
"""Domain parameters and calculations for swine effluents, manure storage, and fertigation."""

from typing import Dict, Any, Optional
import math


PRODUCTION_SYSTEMS: Dict[str, Dict[str, Any]] = {
    "Ciclo Completo (CC)": {
        "effluent_m3_day_per_head": 0.0471,
        "p2o5_kg_year_per_head": 49.6,
        "description": "Sistema completo com todas as fases produtivas (reprodução, maternidade, creche e terminação)."
    },
    "Unidade de Produção de Leitões (UPL)": {
        "effluent_m3_day_per_head": 0.0228,
        "p2o5_kg_year_per_head": 18.0,
        "description": "Foco na reprodução e produção de leitões até desmame/creche (~25 kg)."
    },
    "Unidade de Produção de Desmamados (UPD)": {
        "effluent_m3_day_per_head": 0.0162,
        "p2o5_kg_year_per_head": 8.5,
        "description": "Fase pós-desmame até a saída para terminação (~25 kg)."
    },
    "Crechário (CR)": {
        "effluent_m3_day_per_head": 0.0023,
        "p2o5_kg_year_per_head": 0.25,
        "description": "Animais alojados exclusivamente na fase de creche."
    },
    "Unidade de Terminação (UT)": {
        "effluent_m3_day_per_head": 0.0130,
        "p2o5_kg_year_per_head": 4.3,
        "description": "Animais em engorda e terminação (23 kg até ~120 kg de abate)."
    }
}

PLANT_P2O5_REQUIREMENTS: Dict[str, float] = {
    "Pastagem": 45.0,  # kg P2O5/ha/ano
    "Soja": 80.0,      # kg P2O5/ha/ano
    "Milho": 90.0,     # kg P2O5/ha/ano
}


def solve_frustum_dimensions(
    volume_m3: float,
    depth_m: float,
    length_to_width_ratio: float = 2.0,
    slope: float = 1.0,
    max_iterations: int = 60
) -> Optional[Dict[str, float]]:
    """Solve rectangular inverted frustum (pond/lagoon) dimensions for a given volume and liquid depth.

    Uses binary search to determine top dimensions such that the storage capacity
    satisfies the volume requirement under side-slope constraints.

    :param volume_m3: Required storage volume in cubic meters.
    :param depth_m: Working liquid depth in meters.
    :param length_to_width_ratio: Ratio between top length and top width (L/W >= 1.0).
    :param slope: Horizontal run per 1 unit vertical rise (e.g. 1:1 slope -> slope=1.0).
    :param max_iterations: Maximum binary search steps.
    :returns: Dictionary with top_length, top_width, base_length, base_width, height, volume.
    """
    if volume_m3 <= 0 or depth_m <= 0 or length_to_width_ratio < 1.0:
        return None

    min_width = 2.0 * depth_m * slope + 0.1
    top_width = min_width

    def frustum_volume(length_top: float, width_top: float) -> Optional[float]:
        length_bottom = length_top - (2.0 * depth_m * slope)
        width_bottom = width_top - (2.0 * depth_m * slope)
        if length_bottom <= 0 or width_bottom <= 0:
            return None
        # Prismoidal formula for frustum volume: h/6 * (A1 + A2 + 4*Am)
        # equivalent to: h/3 * (A1 + A2 + sqrt(A1*A2))
        a1 = length_top * width_top
        a2 = length_bottom * width_bottom
        return (depth_m / 3.0) * (a1 + a2 + math.sqrt(a1 * a2))

    # Expand upper bound until covering volume
    hi = top_width
    current_vol = frustum_volume(length_to_width_ratio * hi, hi)
    if current_vol is None:
        return None

    iterations = 0
    while current_vol < volume_m3 and iterations < max_iterations:
        hi *= 1.5
        current_vol = frustum_volume(length_to_width_ratio * hi, hi)
        if current_vol is None:
            return None
        iterations += 1

    if current_vol < volume_m3:
        return None

    lo = min_width
    for _ in range(max_iterations):
        mid = (lo + hi) / 2.0
        mid_vol = frustum_volume(length_to_width_ratio * mid, mid)
        if mid_vol is None:
            return None
        if abs(mid_vol - volume_m3) < 1e-3:
            top_width = mid
            break
        if mid_vol < volume_m3:
            lo = mid
        else:
            hi = mid
        top_width = mid

    top_length = length_to_width_ratio * top_width
    base_length = top_length - (2.0 * depth_m * slope)
    base_width = top_width - (2.0 * depth_m * slope)

    return {
        "top_length": round(top_length, 2),
        "top_width": round(top_width, 2),
        "base_length": round(base_length, 2),
        "base_width": round(base_width, 2),
        "depth": round(depth_m, 2),
        "volume_m3": round(volume_m3, 2),
    }


def estimate_fertigation_areas(total_p2o5_kg_year: float) -> Dict[str, float]:
    """Calculate required crop area (hectares) for agronomic recycling of phosphorus (P2O5)."""
    areas: Dict[str, float] = {}
    for crop_name, demand_kg_ha in PLANT_P2O5_REQUIREMENTS.items():
        if demand_kg_ha > 0 and total_p2o5_kg_year > 0:
            areas[crop_name] = round(total_p2o5_kg_year / demand_kg_ha, 2)
        else:
            areas[crop_name] = 0.0
    return areas
