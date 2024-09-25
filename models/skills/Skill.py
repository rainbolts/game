import math

from pygame import Vector2

from models.Projectile import Projectile


class Skill:
    def __init__(self, origin: tuple[int, int], destination: tuple[int, int]):
        self.damage = 1
        self.speed = 10
        self.time_to_live = 60
        self.origin = origin
        self.destination = destination

    def spawn_projectiles(self) -> list[Projectile]:
        projectile = Projectile(self.origin, self.time_to_live)
        dx, dy = self.destination[0] - self.origin[0], -1 * (self.destination[1] - self.origin[1])
        direction = math.atan2(dy, dx)
        projectile_velocity = Vector2()
        projectile_velocity.from_polar((self.speed, direction / math.pi * 180))
        projectile.set_preferred_velocity(projectile_velocity)
        return [projectile]
