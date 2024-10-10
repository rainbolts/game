from abc import ABC
from enum import IntEnum
from typing import Any

from pygame.sprite import Group

from models.Entity import Entity


class EnemyType(IntEnum):
    NORMAL = 0
    BOSS = 1


class Enemy(Entity, ABC):
    enemy_group = Group()

    def __init__(self, spawn: tuple[int, int], health: int, color: tuple[int, int, int]):
        super().__init__(spawn, 40, 40, color, 0)
        self.enemy_group.add(self)

        self.health = health

    def to_broadcast(self) -> dict[str, Any]:
        result = super().to_broadcast()
        result['health'] = self.health
        return result


class NormalEnemy(Enemy):
    def __init__(self, spawn: tuple[int, int], health: int = 30):
        super().__init__(spawn, health, (255, 0, 0))

    @staticmethod
    def from_broadcast(data: dict[str, Any]) -> 'NormalEnemy':
        return NormalEnemy((data['x'], data['y']), data['health'])


class BossEnemy(Enemy):
    def __init__(self, spawn: tuple[int, int], health: int = 100):
        super().__init__(spawn, health, (255, 0, 255))

    @staticmethod
    def from_broadcast(data: dict[str, Any]) -> 'BossEnemy':
        return BossEnemy((int(data['x']), int(data['y'])), int(data['health']))
