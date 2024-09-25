from abc import ABC

from pygame import mask, Surface, Vector2
from pygame.key import ScancodeWrapper
from pygame.sprite import Sprite, Group

from models.Behaviors import CollisionBehavior


class Entity(Sprite, ABC):
    entity_group = Group()

    def __init__(self, spawn: tuple[int, int], width: int, height: int, color: tuple[int, int, int],
                 time_to_live: int = None):
        super().__init__()

        self.image = Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = spawn[0] - width // 2
        self.rect.y = spawn[1] - height // 2
        self.mask = mask.from_surface(self.image)
        self.time_to_live = time_to_live
        self.entity_group.add(self)

        self._preferred_velocity = Vector2()
        self._precise_location: tuple[float, float] = self.rect.x, self.rect.y

    def get_collision_behaviors(self) -> list[CollisionBehavior]:
        raise NotImplementedError

    def get_preferred_velocity(self, keys: ScancodeWrapper) -> Vector2:
        raise NotImplementedError

    def get_preferred_skills(self, keys: ScancodeWrapper, mouse_position: tuple[int, int]) -> Vector2:
        raise NotImplementedError

    def age(self):
        if self.time_to_live is None:
            return

        if self.time_to_live <= 1:
            self.kill()

        self.time_to_live -= 1

    def get_precise_location(self) -> tuple[float, float]:
        return self._precise_location

    def move_precisely(self, dx: float, dy: float):
        rounded_dx = int(round(dx))
        rounded_dy = int(round(dy))
        if rounded_dx == 0 and rounded_dy == 0:
            return

        self._precise_location = self._precise_location[0] + dx, self._precise_location[1] + dy
        self.rect.x = int(round(self._precise_location[0]))
        self.rect.y = int(round(self._precise_location[1]))

    @property
    def width(self):
        return self.rect.width

    @property
    def height(self):
        return self.rect.height
