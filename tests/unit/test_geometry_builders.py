# -*- coding: utf-8 -*-
"""Unit tests for geometric polygon builders."""

import math
import pytest
from core.geometry.builders import (
    build_rectangle_polygon,
    build_circle_polygon,
    calculate_series_positions,
    build_buffered_polygon,
    rotate_point,
)


def test_rotate_point_90_degrees():
    """Verify 90 degree counter-clockwise rotation around origin."""
    px, py = rotate_point(1.0, 0.0, 0.0, 0.0, math.radians(90.0))
    assert math.isclose(px, 0.0, abs_tol=1e-7)
    assert math.isclose(py, 1.0, abs_tol=1e-7)


def test_build_rectangle_polygon_closed_and_dimensions():
    """Verify rectangle coordinates are closed and conform to length x width."""
    length = 60.0
    width = 12.0
    coords = build_rectangle_polygon(0.0, 0.0, length, width, rotation_deg=0.0)

    # 4 corners + closed point = 5 coordinates
    assert len(coords) == 5
    assert coords[0] == coords[-1]

    # Verify bounding box matches
    xs = [p[0] for p in coords]
    ys = [p[1] for p in coords]
    assert math.isclose(max(xs) - min(xs), length)
    assert math.isclose(max(ys) - min(ys), width)


def test_build_circle_polygon():
    """Verify circle polygon approximation vertex count and radius."""
    radius = 10.0
    segments = 32
    coords = build_circle_polygon(100.0, 200.0, radius=radius, segments=segments)

    assert len(coords) == segments + 1
    assert coords[0] == coords[-1]

    for px, py in coords[:-1]:
        dist = math.hypot(px - 100.0, py - 200.0)
        assert math.isclose(dist, radius, rel_tol=1e-5)


def test_calculate_series_positions():
    """Verify series of sheds are correctly spaced along axis."""
    start_x = 0.0
    start_y = 0.0
    count = 3
    unit_breadth = 12.0
    spacing = 15.0
    # Axis = 90 deg (North-South distribution)
    centers = calculate_series_positions(
        start_x, start_y, count, unit_breadth, spacing, axis_rotation_deg=90.0
    )

    assert len(centers) == 3
    assert centers[0] == (0.0, 0.0)

    step = unit_breadth + spacing  # 27.0
    assert math.isclose(centers[1][0], 0.0, abs_tol=1e-7)
    assert math.isclose(centers[1][1], step, abs_tol=1e-7)
    assert math.isclose(centers[2][1], 2 * step, abs_tol=1e-7)


def test_build_buffered_polygon():
    """Verify buffered polygon expands outer boundaries."""
    base_coords = build_rectangle_polygon(0.0, 0.0, length=50.0, width=10.0)
    buf_coords = build_buffered_polygon(base_coords, buffer_distance=20.0)

    assert len(buf_coords) == len(base_coords)
    assert buf_coords[0] == buf_coords[-1]

    base_xs = [p[0] for p in base_coords]
    buf_xs = [p[0] for p in buf_coords]

    # Length was 50, with 20m buffer on each side, should be 90
    assert math.isclose(max(buf_xs) - min(buf_xs), 90.0, abs_tol=1e-5)
