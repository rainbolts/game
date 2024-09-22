from pygame import Vector2

from models.Entity import Entity


class Projectile(Entity):
    def __init__(self, spawn_x: int, spawn_y: int):
        super().__init__(spawn_x, spawn_y, 10, 10, (0, 255, 255))
        self.damage = 1
        self.time_to_live = 60

        self._preferred_velocity = Vector2()

    def age(self) -> bool:
        self.time_to_live -= 1
        return self.time_to_live <= 0

    def get_preferred_velocity(self, _):
        return self._preferred_velocity

    def set_preferred_velocity(self, velocity: Vector2):
        self._preferred_velocity = velocity
