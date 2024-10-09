from typing import Any

from pygame import Vector2
from pygame.sprite import Group

from models.Behaviors import CollisionBehavior
from models.Entity import Entity


class Projectile(Entity):
    projectile_group = Group()

    def __init__(self, spawn: tuple[int, int], time_to_live: int):
        super().__init__(spawn, 10, 10, (0, 255, 255), time_to_live)
        self.projectile_group.add(self)

        self.damage = 1
        self._preferred_velocity = Vector2()

    def get_collision_behaviors(self) -> list[CollisionBehavior]:
        return [CollisionBehavior.DISAPPEAR, CollisionBehavior.DAMAGE]

    def set_preferred_velocity(self, velocity: Vector2):
        self._preferred_velocity = velocity

    @staticmethod
    def from_broadcast(data: dict[str, Any]) -> 'Projectile':
        return Projectile((int(data['x']), int(data['y'])), 0)
