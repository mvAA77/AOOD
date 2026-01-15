import math

class Triangle:

    sides = 3

    def __init__(self, side1, side2, side3):
        if (side1 + side2 <= side3 or
            side1 + side3 <= side2 or
            side2 + side3 <= side1):
            raise ValueError("Invalid side lengths for a triangle")

        self.side1 = side1
        self.side2 = side2
        self.side3 = side3

    def __eq__(self, other):
        if not isinstance(other, Triangle):
            return False
        return sorted([self.side1, self.side2, self.side3]) == \
               sorted([other.side1, other.side2, other.side3])

    def perimeter(self):
        return self.side1 + self.side2 + self.side3


    def tangent(self, angle_number):
        if angle_number == 1:
            angle = math.acos(
                (self.side2**2 + self.side3**2 - self.side1**2) /
                (2 * self.side2 * self.side3)
            )
        elif angle_number == 2:
            angle = math.acos(
                (self.side1**2 + self.side3**2 - self.side2**2) /
                (2 * self.side1 * self.side3)
            )
        elif angle_number == 3:
            angle = math.acos(
                (self.side1**2 + self.side2**2 - self.side3**2) /
                (2 * self.side1 * self.side2)
            )
        else:
            raise ValueError("Angle must be 1, 2, or 3")

        return math.tan(angle)


triangle1 = Triangle(3, 4, 5)
triangle2 = Triangle(5, 3, 4)

print("Perimeter:", triangle1.perimeter())
print("Tangent of angle 1:", triangle1.tangent(1))
print("Triangles equal:", triangle1 == triangle2)
print("Number of sides:", Triangle.sides)
