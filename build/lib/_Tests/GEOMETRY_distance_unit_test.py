import math
import unittest

from Geometry.distance import point_3d, distance


class TestGeometery(unittest.TestCase):
    def setUp(self):
        self.coordinates = [
            (0, 0, 0),
            (1, 1, 1),
            (-1, -1, -1),
            (math.sqrt(0.5), math.sqrt(0.0), math.sqrt(0.5)),
            (-0.286548, 0.766123, - 0.575279)
        ]

    def test_point(self):
        point = point_3d(*self.coordinates[0])
        self.assertEqual(point.y, 0)
        self.assertEqual(str(point), str((0.0, 0.0, 0.0)))
        self.assertEqual(point.is_vector(), False)

    def test_vector(self):
        vector = point_3d(*self.coordinates[3])
        self.assertEqual(vector.is_vector(), True)
        vector = point_3d(*self.coordinates[4])
        self.assertEqual(vector.is_vector(), True)

    def test_distance_between_points(self):
        point_a = point_3d(*self.coordinates[0])
        point_b = point_3d(*self.coordinates[1])
        distance_a_b = distance.between_points(point_a, point_b)
        self.assertEqual(distance_a_b, math.sqrt(3))

    def test_distance_between_point_and_vector(self):
        point_a = point_3d(*self.coordinates[1])
        vector = point_3d(*self.coordinates[3])
        distance_a_b = distance.between_point_and_vector(point_a, vector)
        self.assertTrue(distance_a_b - 1 < 0.00000000001)
