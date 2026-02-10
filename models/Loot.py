from enum import IntEnum, auto
from typing import Any

from models.Entity import Entity


class LootType(IntEnum):
    SHOULDER = auto()
    NECKLACE = auto()
    LANTERN = auto()
    CAPE = auto()
    RING = auto()
    GLOVES = auto()
    BODY = auto()
    HELMET = auto()
    WEAPON = auto()
    SHIELD = auto()


class GearSlot(IntEnum):
    FEET = auto()
    POTION1 = auto()
    POTION2 = auto()
    LEGS = auto()
    CHARM1 = auto()
    CHARM2 = auto()
    CHARM3 = auto()
    CHARM4 = auto()
    BELT = auto()
    SHOULDER = auto()
    NECKLACE = auto()
    LANTERN = auto()
    CAPE = auto()
    FINGER1 = auto()
    FINGER2 = auto()
    FINGER3 = auto()
    FINGER4 = auto()
    FINGER5 = auto()
    FINGER6 = auto()
    FINGER7 = auto()
    FINGER8 = auto()
    HANDS = auto()
    BODY = auto()
    HEAD = auto()
    MAIN_HAND = auto()
    OFF_HAND = auto()


class Loot(Entity):
    def __init__(self, server_id: int, loot_id: int, spawn: tuple[int, int], inventory_width: int, inventory_height: int):
        super().__init__(spawn, 40, 40, (0, 255, 255), 0)
        self.server_id = server_id
        self.loot_id = loot_id
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
    def __init__(self, server_id: int, loot_id: int, spawn: tuple[int, int]):
        super().__init__(server_id, loot_id, spawn, 1, 1)

    def to_broadcast(self) -> dict[str, Any]:
        result = super().to_broadcast()
        result['server_id'] = self.server_id
        result['loot_id'] = self.loot_id
        result['type'] = LootType.RING
        return result

    @staticmethod
    def from_broadcast(data: dict) -> 'RingLoot':
        return RingLoot(int(data['server_id']), int(data['loot_id']), (int(data['x']), int(data['y'])))
