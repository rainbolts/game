import sys

import pygame
from pygame import Surface


class Area:
    def __init__(self, size: int, seed: int | None = None):
        import random
        if seed is None:
            seed = random.randrange(sys.maxsize)
        self.seed: int = seed
        self.random = random.Random(seed)

        self._generate(40)
        self.surface = self._draw(size)
        self.mask = pygame.mask.from_surface(self.surface)

    def _generate(self, size):
        tiles = [x[:] for x in [[False] * size] * size]

        rng = range(size)
        for i in rng:
            if i == 0 or i == size - 1:
                continue
            for j in rng:
                if j == 0 or j == size - 1 or self.random.randint(0, 99) < 40:
                    tiles[i][j] = True

        for _ in range(10):
            new_tiles = [[False] * size for _ in rng]

            for i in rng:
                for j in rng:
                    if j == 0 or j == size - 1 or i == 0 or i == size - 1:
                        new_tiles[i][j] = True
                    else:
                        new_tiles[i][j] = (tiles[i - 1][j - 1] + tiles[i - 1][j] + tiles[i - 1][j + 1] +
                                           tiles[i][j - 1] + tiles[i][j] + tiles[i][j + 1] +
                                           tiles[i + 1][j - 1] + tiles[i + 1][j] + tiles[i + 1][j + 1]) >= 5
                    j += 1
                i += 1
            tiles = new_tiles

        self.tiles = tiles

    def _draw(self, size: int) -> Surface:
        surface = Surface((size, size), pygame.SRCALPHA)
        scale = size // len(self.tiles)
        for i, row in enumerate(self.tiles):
            for j, tile in enumerate(row):
                if tile:
                    pygame.draw.rect(surface, (255, 255, 255), (i * scale, j * scale, scale, scale))
        return surface
