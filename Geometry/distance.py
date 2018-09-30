import math


class point_3d():
    def __init__(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __str__(self):
        return str((self.x, self.y, self.z))

    def is_vector(self):
        return math.fabs(1 - math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)) < 0.0000001


class distance():
    @classmethod
    def between_points(cls, point_a, point_b):
        return math.sqrt(
            (point_a.x - point_b.x) ** 2 +
            (point_a.y - point_b.y) ** 2 +
            (point_a.z - point_b.z) ** 2
        )

    @classmethod
    def between_point_and_vector(cls, point, vector):
        P = point
        V = vector
        if not vector.is_vector():
            raise ValueError("{} not a vector".format(vector))
        return math.sqrt(
            (P.x ** 2 + P.y ** 2 + P.z ** 2) - \
            (P.x * V.x + P.y * V.y + P.z * V.z) ** 2
        )
