import pygame
from pygame import Surface


class Floor(Surface):
    def __init__(self, offset: tuple[int, int], width: int, height: int):
        super().__init__((width, height), pygame.SRCALPHA)
        self.__offset = offset
        self.__draw_walls(width, height)
        self.__mask = pygame.mask.from_surface(self)

    def __draw_walls(self, width: int, height: int):
        walls = [
            ((0, 0), (width, 0)),
            ((0, 0), (0, height)),
            ((width, 0), (width, height)),
            ((0, height), (width, height))
        ]
        for wall in walls:
            pygame.draw.line(self, (255, 255, 255), wall[0], wall[1], 10)

    @property
    def offset(self):
        return self.__offset

    @property
    def mask(self):
        return self.__mask

    def move(self, dx: int, dy: int):
        self.__offset = self.__offset[0] + dx, self.__offset[1] + dy
