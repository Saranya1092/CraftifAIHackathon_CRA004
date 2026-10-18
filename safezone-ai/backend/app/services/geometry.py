"""
Point-in-polygon utilities using the ray-casting algorithm.

All coordinates are normalised to [0, 1] relative to frame dimensions.
"""
from __future__ import annotations

from typing import List, Tuple


def point_in_polygon(px: float, py: float, polygon: List[Tuple[float, float]]) -> bool:
    """
    Ray-casting algorithm.  Returns True when (px, py) is inside the polygon
    defined by the list of (x, y) tuples.  Boundary points are treated as inside.
    """
    n = len(polygon)
    if n < 3:
        return False

    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        # Check if the point sits exactly on an edge (treat as inside)
        if _on_segment(px, py, xi, yi, xj, yj):
            return True
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i

    return inside


def _on_segment(px: float, py: float, x1: float, y1: float, x2: float, y2: float) -> bool:
    """Return True when P lies on segment (x1,y1)-(x2,y2)."""
    # Cross product must be zero for collinearity
    cross = (py - y1) * (x2 - x1) - (px - x1) * (y2 - y1)
    if abs(cross) > 1e-10:
        return False
    # Dot product checks that P is between the endpoints
    dot = (px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)
    if dot < 0:
        return False
    sq_len = (x2 - x1) ** 2 + (y2 - y1) ** 2
    return dot <= sq_len


def coords_to_tuples(coords: list) -> List[Tuple[float, float]]:
    """Convert [{x, y}] dicts to [(x, y)] tuples."""
    return [(c["x"], c["y"]) for c in coords]
