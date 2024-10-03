import math

from pygame import Vector2

from models.Behaviors import CollisionBehavior
from models.Direction import Direction
from models.Entity import Entity


class Player(Entity):
    def __init__(self, spawn: tuple[int, int]):
        super().__init__(spawn, 40, 40, (0, 255, 0))
        self.movement_speed: int = 10

    def get_collision_behaviors(self) -> list[CollisionBehavior]:
        return []

    def get_preferred_velocity(self, direction: Direction) -> Vector2:
        go_left = Direction.LEFT in direction
        go_right = Direction.RIGHT in direction
        go_up = Direction.UP in direction
        go_down = Direction.DOWN in direction

        # No movement
        if not go_left and not go_right and not go_up and not go_down:
            self._preferred_velocity.from_polar((0, 0))

        # Opposing horizontal movement, no vertical
        elif go_left and go_right and not go_up and not go_down:
            self._preferred_velocity.from_polar((0, 0))

        # Opposing vertical movement, no horizontal
        elif not go_left and not go_right and go_up and go_down:
            self._preferred_velocity.from_polar((0, 0))

        # Opposing vertical and horizontal movement
        elif go_left and go_right and go_up and go_down:
            self._preferred_velocity.from_polar((0, 0))

        else:
            direction = math.atan2(go_up - go_down, go_right - go_left)
            self._preferred_velocity.from_polar((self.movement_speed, direction / math.pi * 180))

        return self._preferred_velocity
