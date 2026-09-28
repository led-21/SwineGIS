# -*- coding: utf-8 -*-
"""Unit tests for effluents calculations, pond sizing, and fertigation areas."""

from core.domain.effluents import (
    PRODUCTION_SYSTEMS,
    PLANT_P2O5_REQUIREMENTS,
    solve_frustum_dimensions,
    estimate_fertigation_areas,
)


def test_production_systems_coefficients():
    """Verify standard emission coefficients for all production systems."""
    for sys_name, data in PRODUCTION_SYSTEMS.items():
        assert "effluent_m3_day_per_head" in data
        assert "p2o5_kg_year_per_head" in data
        assert data["effluent_m3_day_per_head"] > 0
        assert data["p2o5_kg_year_per_head"] > 0


def test_solve_frustum_dimensions():
    """Verify numerical solution of waste lagoon dimensions."""
    volume = 1500.0  # m3
    depth = 3.0      # m
    res = solve_frustum_dimensions(volume, depth, length_to_width_ratio=2.0)

    assert res is not None
    assert res["depth"] == depth
    assert res["top_length"] > res["base_length"]
    assert res["top_width"] > res["base_width"]
    assert res["top_length"] >= res["top_width"]


def test_estimate_fertigation_areas():
    """Verify required crop area calculation based on P2O5 recycling."""
    total_p2o5 = 4500.0  # kg/ano
    areas = estimate_fertigation_areas(total_p2o5)

    # Pasture demand is 45 kg/ha -> 4500 / 45 = 100 ha
    assert areas["Pastagem"] == 100.0
    # Soybean demand is 80 kg/ha -> 4500 / 80 = 56.25 ha
    assert areas["Soja"] == 56.25
    # Corn demand is 90 kg/ha -> 4500 / 90 = 50.0 ha
    assert areas["Milho"] == 50.0
