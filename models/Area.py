import sys
from enum import IntEnum

import pygame
from pygame import Surface, Mask
from pygame.sprite import Group

from models.Enemy import EnemyType, NormalEnemy, BossEnemy
from models.ExitDoor import ExitDoor
from models.Loot import LootType, RingLoot
from models.Player import Player
from models.Projectile import Projectile


class TileType(IntEnum):
    EMPTY = 0
    WALL = 1
    SPAWN = 2
    BOSS = 3
    EXIT = 4


class Area:
    def __init__(self, seed: int | None = None):
        import random
        if seed is None:
            seed = random.randrange(sys.maxsize)
        self.seed: int = seed
        self.random = random.Random(seed)

        self._spawn = None
        self._boss = None

        self.map_size = 2000

        self.tiles = self.generate_tiles(40)
        self.scale = self.map_size // len(self.tiles)
        self.populate_tiles(self.tiles)

        self.mask = self._get_mask()
        self.surface = None

        self.exit: ExitDoor | None = None
        self.players = Group()
        self.projectiles = Group()
        self.enemies = Group()
        self.loots = Group()

    def get_spawn(self) -> tuple[int, int]:
        unscaled_spawn = self._spawn
        return unscaled_spawn[0] * self.scale, unscaled_spawn[1] * self.scale

    def get_boss_spawn(self) -> tuple[int, int]:
        unscaled_boss = self._boss
        return unscaled_boss[0] * self.scale, unscaled_boss[1] * self.scale

    def generate_tiles(self, size: int) -> list[list[TileType]]:
        tiles = [x[:] for x in [[TileType.EMPTY] * size] * size]

        rng = range(size)
        for i in rng:
            if i == 0 or i == size - 1:
                continue
            for j in rng:
                if j == 0 or j == size - 1 or self.random.randint(0, 99) < 40:
                    tiles[i][j] = TileType.WALL

        for _ in range(10):
            new_tiles = [[TileType.EMPTY] * size for _ in rng]

            for i in rng:
                for j in rng:
                    if j == 0 or j == size - 1 or i == 0 or i == size - 1:
                        new_tiles[i][j] = TileType.WALL
                    else:
                        if (tiles[i - 1][j - 1] + tiles[i - 1][j] + tiles[i - 1][j + 1] +
                                           tiles[i][j - 1] + tiles[i][j] + tiles[i][j + 1] +
                                           tiles[i + 1][j - 1] + tiles[i + 1][j] + tiles[i + 1][j + 1]) >= 5:
                            new_tiles[i][j] = TileType.WALL
                    j += 1
                i += 1
            tiles = new_tiles

        return tiles

    def populate_tiles(self, original_tiles: list[list[TileType]]) -> None:
        """
        Populates the largest open area with spawn and boss tiles.

        :param original_tiles: A list of tiles.
        """
        largest_empty = Area.find_largest_empty(original_tiles)

        self._spawn, self._boss = Area.most_distant_tiles(largest_empty)
        original_tiles[self._spawn[0]][self._spawn[1]] = TileType.SPAWN
        original_tiles[self._boss[0]][self._boss[1]] = TileType.BOSS

    @staticmethod
    def find_largest_empty(tiles: list[list[TileType]]) -> list[list[TileType]]:
        """
        Given a list of tiles, returns a copy with all except the largest open area filled in with walls.
        Does not modify the original tiles.

        :param tiles: A list of tiles.
        :return: A copy of the tiles with all except the largest open area filled in with walls.
        """
        copy_of_tiles = [x[:] for x in tiles]
        largest_area_size = 0
        largest_area_position = (0, 0)
        areas = set()
        for i in range(len(copy_of_tiles)):
            for j in range(len(copy_of_tiles[0])):
                if copy_of_tiles[i][j] == TileType.EMPTY:
                    area_size = Area.flood_fill(copy_of_tiles, i, j)
                    if area_size > largest_area_size:
                        largest_area_size = area_size
                        largest_area_position = (i, j)
                    areas.add((i, j))

        copy_of_tiles = [x[:] for x in tiles]
        for area in areas:
            if area != largest_area_position:
                Area.flood_fill(copy_of_tiles, area[0], area[1])

        return copy_of_tiles

    @staticmethod
    def most_distant_tiles(tiles: list[list[TileType]]) -> tuple[tuple[int, int], tuple[int, int]]:
        """
        Given a list of tiles that contain exactly one open area, returns the two empty tiles that are the farthest apart.

        :param tiles: A list of tiles.
        :return: The positions of the two tiles that are the farthest apart.
        """
        def distance_squared(a: tuple[int, int], b: tuple[int, int]) -> int:
            return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2

        empty_tiles = [(i, j) for i, row in enumerate(tiles) for j, tile in enumerate(row) if tile == TileType.EMPTY]
        return max(((a, b) for a in empty_tiles for b in empty_tiles if a < b), key=lambda x: distance_squared(*x))

    def _get_mask(self) -> Mask:
        surface = Surface((self.map_size, self.map_size), pygame.SRCALPHA)
        for i, row in enumerate(self.tiles):
            for j, tile in enumerate(row):
                if tile == TileType.WALL:
                    pygame.draw.rect(surface, (255, 255, 255), (i * self.scale, j * self.scale, self.scale, self.scale))
        return pygame.mask.from_surface(surface)

    @staticmethod
    def flood_fill(holey_tiles: list[list[TileType]], i: int, j: int) -> int:
        if i < 0 or i >= len(holey_tiles) or j < 0 or j >= len(holey_tiles[0]):
            return 0
        if holey_tiles[i][j] != TileType.EMPTY:
            return 0

        # Stack for DFS
        stack = [(i, j)]
        area_size = 0

        while stack:
            x, y = stack.pop()

            # Skip if this tile is already processed
            if holey_tiles[x][y] != TileType.EMPTY:
                continue

            # Mark the current tile as visited
            holey_tiles[x][y] = TileType.WALL
            area_size += 1

            # Check up, down, left, and right
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < len(holey_tiles) and 0 <= ny < len(holey_tiles[0]):
                    if holey_tiles[nx][ny] == TileType.EMPTY:
                        stack.append((nx, ny))

        return area_size

    def to_broadcast(self):
        return {
            'seed': self.seed,
            'players': [player.to_broadcast() for player in self.players],
            'projectiles': [projectile.to_broadcast() for projectile in self.projectiles],
            'enemies': [enemy.to_broadcast() for enemy in self.enemies],
            'loot': [loot.to_broadcast() for loot in self.loots],
            'exit': self.exit.to_broadcast() if self.exit else None
        }

    @staticmethod
    def from_broadcast(update: dict, diff_from_area = None) -> 'Area':
        if diff_from_area and diff_from_area.seed == update['seed']:
            area = diff_from_area
        else:
            area = Area(update['seed'])

        area.players.empty()
        area.players.add([Player.from_broadcast(player) for player in update['players']])

        area.projectiles.empty()
        area.projectiles.add([Projectile.from_broadcast(projectile) for projectile in update['projectiles']])

        area.enemies.empty()
        for enemy_update in update['enemies']:
            enemy_type = int(enemy_update['type'])
            if enemy_type == EnemyType.NORMAL:
                area.enemies.add(NormalEnemy.from_broadcast(enemy_update))
            elif enemy_type == EnemyType.BOSS:
                area.enemies.add(BossEnemy.from_broadcast(enemy_update))
            else:
                raise ValueError(f'Unknown enemy type: {enemy_type}')

        area.loots.empty()
        for loot_update in update['loot']:
            loot_type = int(loot_update['type'])
            if loot_type == LootType.RING:
                area.loots.add(RingLoot.from_broadcast(loot_update))
            else:
                raise ValueError(f'Unknown loot type: {loot_type}')

        if area.exit:
            area.exit.kill()
        area.exit = ExitDoor.from_broadcast(update['exit']) if update['exit'] else None

        return area
