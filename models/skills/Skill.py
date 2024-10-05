from pygame import Vector2

from models.Projectile import Projectile


class Skill:
    def __init__(self, origin: tuple[int, int], destination_vector: Vector2):
        self.damage = 1
        self.speed = 10
        self.time_to_live = 60
        self.origin = origin
        self.destination_vector = destination_vector

    def spawn_projectiles(self) -> list[Projectile]:
        projectile = Projectile(self.origin, self.time_to_live)
        projectile_velocity = Vector2(self.destination_vector)
        if projectile_velocity.length() == 0:
            projectile_velocity = Vector2(1, 0)
        projectile_velocity.scale_to_length(self.speed)
        projectile.set_preferred_velocity(projectile_velocity)
        return [projectile]
