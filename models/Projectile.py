from typing import Any

from pygame import Vector2

from models.Behaviors import CollisionBehavior
from models.Entity import Entity


class Projectile(Entity):
    def __init__(self, spawn: tuple[int, int], time_to_live: int, initial_velocity: Vector2, height: int = 10, width: int = 10):
        super().__init__(spawn, height, width, (0, 255, 255), time_to_live)
        self.damage = 1
        self._preferred_velocity = initial_velocity

    def get_collision_behaviors(self) -> list[CollisionBehavior]:
        return [CollisionBehavior.DISAPPEAR, CollisionBehavior.DAMAGE]

    def to_broadcast(self) -> dict[str, Any]:
        result = super().to_broadcast()
        result['vx'] = self._preferred_velocity.x
        result['vy'] = self._preferred_velocity.y
        return result

    @staticmethod
    def from_broadcast(data: dict[str, Any]) -> 'Projectile':
        vx = float(data['vx'])
        vy = float(data['vy'])
        return Projectile((int(data['x']), int(data['y'])) , 0, Vector2(vx, vy))
