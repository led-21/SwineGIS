# -*- coding: utf-8 -*-
"""Pure Python geometric polygon builders for facilities and buffers.

All calculations operate on Euclidean coordinates (X, Y in meters or projected coordinates).
Returns closed rings of (x, y) tuples where the first point equals the last.
"""

import math
from typing import List, Tuple

Coordinate = Tuple[float, float]
PolygonRing = List[Coordinate]


def rotate_point(x: float, y: float, origin_x: float, origin_y: float, angle_rad: float) -> Coordinate:
    """Rotate a point (x, y) around (origin_x, origin_y) by angle_rad (counter-clockwise)."""
    dx = x - origin_x
    dy = y - origin_y
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    rx = origin_x + (dx * cos_a - dy * sin_a)
    ry = origin_y + (dx * sin_a + dy * cos_a)
    return (rx, ry)


def build_rectangle_polygon(
    center_x: float,
    center_y: float,
    length: float,
    width: float,
    rotation_deg: float = 0.0
) -> PolygonRing:
    """Generate a closed polygon ring for a rectangle centered at (center_x, center_y).

    Length is oriented along the X-axis before rotation.
    Width is oriented along the Y-axis before rotation.
    rotation_deg: rotation angle in degrees counter-clockwise.
    """
    half_l = length / 2.0
    half_w = width / 2.0

    raw_corners = [
        (center_x - half_l, center_y - half_w),  # Bottom-left
        (center_x + half_l, center_y - half_w),  # Bottom-right
        (center_x + half_l, center_y + half_w),  # Top-right
        (center_x - half_l, center_y + half_w),  # Top-left
    ]

    angle_rad = math.radians(rotation_deg)
    if abs(angle_rad) > 1e-9:
        rotated = [rotate_point(px, py, center_x, center_y, angle_rad) for px, py in raw_corners]
    else:
        rotated = raw_corners

    # Close the ring
    rotated.append(rotated[0])
    return rotated


def build_circle_polygon(
    center_x: float,
    center_y: float,
    radius: float,
    segments: int = 36
) -> PolygonRing:
    """Generate a regular polygon approximating a circle centered at (center_x, center_y)."""
    if segments < 8:
        segments = 8

    ring: PolygonRing = []
    step = (2 * math.pi) / segments

    for i in range(segments):
        theta = i * step
        px = center_x + radius * math.cos(theta)
        py = center_y + radius * math.sin(theta)
        ring.append((px, py))

    # Close the ring
    ring.append(ring[0])
    return ring


def calculate_series_positions(
    start_x: float,
    start_y: float,
    count: int,
    unit_breadth: float,
    spacing: float,
    axis_rotation_deg: float = 90.0
) -> List[Coordinate]:
    """Calculate center positions for multiple consecutive parallel units.

    By default, sheds are distributed along the North-South axis (90 deg)
    while individual sheds extend East-West (0 deg) for optimum solar orientation.

    step_distance = unit_breadth + spacing
    """
    centers: List[Coordinate] = []
    step_distance = unit_breadth + spacing
    rad = math.radians(axis_rotation_deg)
    step_dx = step_distance * math.cos(rad)
    step_dy = step_distance * math.sin(rad)

    for i in range(count):
        cx = start_x + (i * step_dx)
        cy = start_y + (i * step_dy)
        centers.append((cx, cy))

    return centers


def build_buffered_polygon(
    base_coords: PolygonRing,
    buffer_distance: float,
    segments_per_quadrant: int = 8
) -> PolygonRing:
    """Generate an outward buffer ring around a simple convex polygon ring.

    For rectangular/circular facilities, this provides an accurate geometric buffer
    independently of external GIS libraries (ideal for unit testing and standalone mode).
    """
    if buffer_distance <= 0 or len(base_coords) < 4:
        return list(base_coords)

    # For circles (many vertices approximated from center):
    # If the base coords look like a regular polygon approximated circle,
    # expand the radius from the center point directly:
    xs = [p[0] for p in base_coords[:-1]]
    ys = [p[1] for p in base_coords[:-1]]
    center_x = sum(xs) / len(xs)
    center_y = sum(ys) / len(ys)

    radii = [math.hypot(p[0] - center_x, p[1] - center_y) for p in base_coords[:-1]]
    is_circular = max(radii) - min(radii) < 1e-3 and len(base_coords) > 16

    if is_circular:
        base_radius = radii[0]
        return build_circle_polygon(center_x, center_y, base_radius + buffer_distance, segments=len(base_coords) - 1)

    # For 4-point rectangles (5 coords closed):
    if len(base_coords) == 5:
        # Calculate width and length by vector norms
        c0, c1, c2, c3 = base_coords[0], base_coords[1], base_coords[2], base_coords[3]
        len_1 = math.hypot(c1[0] - c0[0], c1[1] - c0[1])
        len_2 = math.hypot(c2[0] - c1[0], c2[1] - c1[1])
        # Center of rectangle
        cx = (c0[0] + c1[0] + c2[0] + c3[0]) / 4.0
        cy = (c0[1] + c1[1] + c2[1] + c3[1]) / 4.0

        angle_deg = math.degrees(math.atan2(c1[1] - c0[1], c1[0] - c0[0]))
        return build_rectangle_polygon(
            cx, cy,
            length=len_1 + (2 * buffer_distance),
            width=len_2 + (2 * buffer_distance),
            rotation_deg=angle_deg
        )

    # Generic fallback: uniform scaling from centroid
    buffered: PolygonRing = []
    for px, py in base_coords[:-1]:
        vx = px - center_x
        vy = py - center_y
        dist = math.hypot(vx, vy)
        if dist > 1e-9:
            scale = (dist + buffer_distance) / dist
            bx = center_x + vx * scale
            by = center_y + vy * scale
            buffered.append((bx, by))
        else:
            buffered.append((px, py))
    buffered.append(buffered[0])
    return buffered
