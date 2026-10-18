"""Tests for point-in-polygon geometry utilities."""
import pytest
from app.services.geometry import point_in_polygon, coords_to_tuples

# Simple unit square polygon
SQUARE = [(0.2, 0.2), (0.8, 0.2), (0.8, 0.8), (0.2, 0.8)]

# Triangle
TRIANGLE = [(0.5, 0.1), (0.9, 0.9), (0.1, 0.9)]


class TestPointInPolygon:
    def test_center_inside_square(self):
        assert point_in_polygon(0.5, 0.5, SQUARE) is True

    def test_outside_square(self):
        assert point_in_polygon(0.1, 0.1, SQUARE) is False

    def test_on_boundary_treated_as_inside(self):
        # Point on a horizontal edge
        assert point_in_polygon(0.5, 0.2, SQUARE) is True

    def test_corner_point(self):
        # Corner is on the boundary – treated as inside
        assert point_in_polygon(0.2, 0.2, SQUARE) is True

    def test_just_outside_edge(self):
        assert point_in_polygon(0.81, 0.5, SQUARE) is False

    def test_inside_triangle(self):
        assert point_in_polygon(0.5, 0.5, TRIANGLE) is True

    def test_outside_triangle(self):
        assert point_in_polygon(0.1, 0.1, TRIANGLE) is False

    def test_degenerate_polygon_returns_false(self):
        # Fewer than 3 vertices
        assert point_in_polygon(0.5, 0.5, [(0.2, 0.2), (0.8, 0.8)]) is False

    def test_empty_polygon_returns_false(self):
        assert point_in_polygon(0.5, 0.5, []) is False

    def test_coords_to_tuples_conversion(self):
        coords = [{"x": 0.2, "y": 0.2}, {"x": 0.8, "y": 0.2}, {"x": 0.5, "y": 0.8}]
        tuples = coords_to_tuples(coords)
        assert tuples == [(0.2, 0.2), (0.8, 0.2), (0.5, 0.8)]
