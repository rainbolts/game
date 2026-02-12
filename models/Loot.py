from enum import IntEnum, auto
from typing import Any

from models.Entity import Entity
from models.LootModifier import LootModifier


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

    def __str__(self) -> str:
        return {
            LootType.SHOULDER: 'Shoulder',
            LootType.NECKLACE: 'Necklace',
            LootType.LANTERN: 'Lantern',
            LootType.CAPE: 'Cape',
            LootType.RING: 'Ring',
            LootType.GLOVES: 'Gloves',
            LootType.BODY: 'Body',
            LootType.HELMET: 'Helmet',
            LootType.WEAPON: 'Weapon',
            LootType.SHIELD: 'Shield',
        }[self]


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
    NECK = auto()
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
    GEAR_COMPATIBILITY: dict[LootType, list[GearSlot]] = {
        LootType.RING: [
            GearSlot.FINGER1,
            GearSlot.FINGER2,
            GearSlot.FINGER3,
            GearSlot.FINGER4,
            GearSlot.FINGER5,
            GearSlot.FINGER6,
            GearSlot.FINGER7,
            GearSlot.FINGER8,
        ],
        LootType.NECKLACE: [GearSlot.NECK],
        LootType.LANTERN: [GearSlot.LANTERN],
        LootType.CAPE: [GearSlot.CAPE],
        LootType.GLOVES: [GearSlot.HANDS],
        LootType.BODY: [GearSlot.BODY],
        LootType.HELMET: [GearSlot.HEAD],
        LootType.WEAPON: [GearSlot.MAIN_HAND, GearSlot.OFF_HAND],
        LootType.SHIELD: [GearSlot.OFF_HAND, GearSlot.MAIN_HAND],
        LootType.SHOULDER: [GearSlot.SHOULDER],
    }

    def __init__(self, server_id: int, loot_id: int, spawn: tuple[int, int], inventory_width: int,
                 inventory_height: int, loot_type: LootType):
        super().__init__(spawn, 40, 40, (0, 255, 255), 0)
        self.server_id = server_id
        self.loot_id = loot_id
        self.inventory_width = inventory_width
        self.inventory_height = inventory_height
        self.loot_type = loot_type
        self.modifiers: list[LootModifier] = []

    def to_broadcast(self) -> dict[str, Any]:
        result = super().to_broadcast()
        result['server_id'] = self.server_id
        result['loot_id'] = self.loot_id
        result['type'] = self.loot_type
        result['modifiers'] = [modifier.to_broadcast() for modifier in self.modifiers]
        return result

    @staticmethod
    def from_broadcast(data: dict[str, Any]) -> 'Loot':
        loot_type = int(data['type'])
        server_id = int(data['server_id'])
        loot_id = int(data['loot_id'])
        spawn = (int(data['x']), int(data['y']))
        modifiers = [LootModifier.from_broadcast(mod_data) for mod_data in data['modifiers']]
        if loot_type == LootType.RING:
            result = RingLoot(server_id, loot_id, spawn)
        else:
            raise ValueError(f'Unknown loot type: {loot_type}')
        result.modifiers = modifiers
        return result


class RingLoot(Loot):
    def __init__(self, server_id: int, loot_id: int, spawn: tuple[int, int]):
        super().__init__(server_id, loot_id, spawn, 1, 1, LootType.RING)
