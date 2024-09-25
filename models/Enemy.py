from pygame.key import ScancodeWrapper
from pygame.sprite import Group

from models.Behaviors import CollisionBehavior
from models.Entity import Entity


class Enemy(Entity):
    enemy_group = Group()

    def __init__(self, spawn: tuple[int, int], health: int):
        super().__init__(spawn, 40, 40, (255, 0, 0))

        self.health = health
        self.enemy_group.add(self)

    def get_collision_behaviors(self) -> list[CollisionBehavior]:
        return []

    def get_preferred_velocity(self, keys: ScancodeWrapper):
        return self._preferred_velocity

    def get_preferred_skills(self, *_):
        return []
