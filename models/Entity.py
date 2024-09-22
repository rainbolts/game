from abc import ABC

import pygame
from pygame.key import ScancodeWrapper


class Entity(pygame.sprite.Sprite, ABC):
    def __init__(self, spawn_x: int, spawn_y: int, width: int, height: int, color: tuple[int, int, int]):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = spawn_x - width // 2
        self.rect.y = spawn_y - height // 2
        self.mask = pygame.mask.from_surface(self.image)
        self._preferred_velocity = pygame.Vector2()

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def get_preferred_velocity(self, keys: ScancodeWrapper):
        raise NotImplementedError

    @property
    def x(self):
        return self.rect.x

    @property
    def y(self):
        return self.rect.y

    @property
    def width(self):
        return self.rect.width

    @property
    def height(self):
        return self.rect.height
