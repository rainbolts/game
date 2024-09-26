import random

import pygame
from pygame import Surface


class Area(Surface):
    def __init__(self, offset: tuple[int, int], size: int):
        super().__init__((size, size), pygame.SRCALPHA)
        self._offset = offset

        self.tiles = self._generate(40)
        self.draw(size)

        self._mask = pygame.mask.from_surface(self)

    @property
    def offset(self):
        return self._offset

    @property
    def mask(self):
        return self._mask

    @staticmethod
    def _generate(size):
        tiles = [x[:] for x in [[False] * size] * size]

        rng = range(size)
        for i in rng:
            if i == 0 or i == size - 1:
                continue
            for j in rng:
                if j == 0 or j == size - 1 or random.randint(0, 99) < 40:
                    tiles[i][j] = True

        for _ in range(10):
            new_tiles = [[False] * size for _ in rng]

            for i in rng:
                for j in rng:
                    if j == 0 or j == size - 1 or i == 0 or i == size - 1:
                        new_tiles[i][j] = True
                    else:
                        new_tiles[i][j] = tiles[i - 1][j - 1] + tiles[i - 1][j] + tiles[i - 1][j + 1] + tiles[i][
                            j - 1] + tiles[i][j] + tiles[i][j + 1] + tiles[i + 1][j - 1] + tiles[i + 1][j] + \
                                          tiles[i + 1][j + 1] >= 5
                    j += 1
                i += 1
            tiles = new_tiles

        return tiles

    def move(self, dx: int, dy: int):
        self._offset = self._offset[0] + dx, self._offset[1] + dy

    def draw(self, size):
        scale = size // len(self.tiles)
        for i, row in enumerate(self.tiles):
            for j, tile in enumerate(row):
                if tile:
                    pygame.draw.rect(self, (255, 255, 255), (i * scale, j * scale, scale, scale))
