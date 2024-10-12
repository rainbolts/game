from enum import IntEnum
from typing import Any

from models.Entity import Entity


class LootType(IntEnum):
    RING = 0


class Loot(Entity):
    def __init__(self, spawn: tuple[int, int]):
        super().__init__(spawn, 40, 40, (0, 255, 255), 0)


class RingLoot(Loot):
    def __init__(self, spawn: tuple[int, int]):
        super().__init__(spawn)

    def to_broadcast(self) -> dict[str, Any]:
        result = super().to_broadcast()
        result['type'] = LootType.RING
        return result

    @staticmethod
    def from_broadcast(data: dict) -> 'RingLoot':
        return RingLoot((int(data['x']), int(data['y'])))
