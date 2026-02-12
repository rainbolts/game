from enum import StrEnum
from typing import Any


class ModifierType(StrEnum):
    DAMAGE_FLAT = "Your projectiles deal # more damage."
    DAMAGE_PERCENT = "Your projectiles deal #% more damage."
    ATTACK_SPEED_PERCENT = "Your attacks are #% faster."
    MOVEMENT_SPEED_PERCENT = "You move #% faster."


class LootModifier:
    def __init__(self, server_id: int, loot_id: int, modifier_id: int, modifier_type: ModifierType, values: list[int|float]) -> None:
        self.server_id = server_id
        self.loot_id = loot_id
        self.modifier_id = modifier_id
        self.modifier_type = modifier_type
        self.values = values

    def to_broadcast(self) -> dict[str, Any]:
        return {
            'server_id': self.server_id,
            'loot_id': self.loot_id,
            'modifier_id': self.modifier_id,
            'type': self.modifier_type,
            'values': self.values,
        }

    @staticmethod
    def from_broadcast(data: dict[str, Any]) -> 'LootModifier':
        return LootModifier(
            server_id=data['server_id'],
            loot_id=data['loot_id'],
            modifier_id=data['modifier_id'],
            modifier_type=ModifierType(data['type']),
            values=data['values']
        )