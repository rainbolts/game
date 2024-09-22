from pygame.key import ScancodeWrapper

from models.Entity import Entity


class Enemy(Entity):
    def __init__(self, spawn_x: int, spawn_y: int):
        super().__init__(spawn_x, spawn_y, 40, 40, (255, 0, 0))

    def get_preferred_velocity(self, keys: ScancodeWrapper):
        return self._preferred_velocity