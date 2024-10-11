from abc import ABC
from typing import Any

from pygame import mask, Surface, Vector2
from pygame.sprite import Sprite

from models.Behaviors import CollisionBehavior


class Entity(Sprite, ABC):
    def __init__(self, spawn: tuple[int, int], width: int, height: int, color: tuple[int, int, int],
                 time_to_live: int = None):
        super().__init__()

        self.width = width
        self.height = height

        self.image = Surface((width, height))
        self.image.fill(color)
        self.mask = mask.from_surface(self.image)
        self.time_to_live = time_to_live

        self._preferred_velocity = Vector2()
        self._precise_location: tuple[float, float] = spawn

    def get_collision_behaviors(self) -> list[CollisionBehavior]:
        return []

    def get_preferred_velocity(self) -> Vector2:
        return self._preferred_velocity

    def age(self):
        if self.time_to_live is None:
            return

        if self.time_to_live <= 1:
            self.kill()

        self.time_to_live -= 1

    def get_pixel_location(self) -> tuple[int, int]:
        return int(round(self._precise_location[0])), int(round(self._precise_location[1]))

    def get_precise_location(self) -> tuple[float, float]:
        return self._precise_location

    def get_center(self) -> tuple[int, int]:
        top_left = self.get_pixel_location()
        return top_left[0] + self.width // 2, top_left[1] + self.height // 2

    def move_absolute(self, x: float, y: float):
        self._precise_location = x, y

    def move_relative(self, dx: float, dy: float):
        rounded_dx = int(round(dx))
        rounded_dy = int(round(dy))
        if rounded_dx == 0 and rounded_dy == 0:
            return

        self._precise_location = self._precise_location[0] + dx, self._precise_location[1] + dy

    def to_broadcast(self) -> dict[str, Any]:
        return {
            'x': int(round(self._precise_location[0])),
            'y': int(round(self._precise_location[1]))
        }

    @staticmethod
    def from_broadcast(data: dict[str, Any]) -> 'Entity':
        raise NotImplementedError('This method must be overridden in a subclass.')
