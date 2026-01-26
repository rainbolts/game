from enum import IntEnum
from typing import Any

from models.Entity import Entity


class LootType(IntEnum):
    RING = 0


class Loot(Entity):
    def __init__(self, spawn: tuple[int, int], inventory_width: int, inventory_height: int):
        super().__init__(spawn, 40, 40, (0, 255, 255), 0)
        self.inventory_width = inventory_width
        self.inventory_height = inventory_height

    @staticmethod
    def from_broadcast(data: dict[str, Any]) -> 'Loot':
        loot_type = int(data['type'])
        if loot_type == LootType.RING:
            return RingLoot.from_broadcast(data)
        else:
            raise ValueError(f'Unknown loot type: {loot_type}')


class RingLoot(Loot):
    def __init__(self, spawn: tuple[int, int]):
        super().__init__(spawn, 1, 1)

    def to_broadcast(self) -> dict[str, Any]:
        result = super().to_broadcast()
        result['type'] = LootType.RING
        return result

    @staticmethod
    def from_broadcast(data: dict) -> 'RingLoot':
        return RingLoot((int(data['x']), int(data['y'])))
