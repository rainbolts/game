from enum import Flag, auto
from typing import Optional

from pygame import Vector2


class Direction(Flag):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

    @staticmethod
    def from_velocity(vel: Vector2) -> Optional['Direction']:
        """
        Round a vector to the nearest orthogonal direction.
        :param vel: The vector to find the direction of.
        :return: The direction orthogonally closest to the given vector. Returns None if the vector is (0, 0).
        """
        if vel.length() == 0 or vel == (0, 0):
            return None

        # Divide the radians into 8 sections of 45 degrees each. For example, right is anything from -22.5 to 22.5.
        angle = vel.as_polar()[1] % 360

        if 22.5 <= angle < 67.5:
            return Direction.UP | Direction.RIGHT
        if 67.5 <= angle < 112.5:
            return Direction.UP
        if 112.5 <= angle < 157.5:
            return Direction.UP | Direction.LEFT
        if 157.5 <= angle < 202.5:
            return Direction.LEFT
        if 202.5 <= angle < 247.5:
            return Direction.DOWN | Direction.LEFT
        if 247.5 <= angle < 292.5:
            return Direction.DOWN
        if 292.5 <= angle < 337.5:
            return Direction.DOWN | Direction.RIGHT
        if 337.5 <= angle or angle < 22.5:
            return Direction.RIGHT

        raise ValueError(f'Angle {angle} is not in the expected range.')
