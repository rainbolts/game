from typing import Any

from models.Loot import Loot


class LootContainer:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.loot: dict[tuple[int, int], Loot] = {}  # Key is top left corner of loot position

    def try_add_loot(self, loot: Loot) -> bool:
        """
        Find a position to place loot, and place it. Scans left to right first, top to bottom second.
        :param loot:
        :return: True if loot was added, else False
        """
        for y in range(self.height - loot.inventory_height + 1):
            for x in range(self.width - loot.inventory_width + 1):
                if self.try_add_loot_at_position(loot, (x, y)):
                    return True

        return False

    def try_add_loot_at_position(self, loot: Loot, position: tuple[int, int]) -> bool:
        for dy in range(loot.inventory_height):
            for dx in range(loot.inventory_width):
                if (position[0] + dx, position[1] + dy) in self.loot:
                    return False
        self.loot[(position[0], position[1])] = loot
        return True

    def to_broadcast(self):
        return {
            'width': self.width,
            'height': self.height,
            'loot': [(x, y, loot.to_broadcast()) for (x, y), loot in self.loot.items()]
        }

    def merge_broadcast(self, data: dict[str, Any]):
        for x, y, loot_update in data['loot']:
            loot = Loot.from_broadcast(loot_update)
            self.loot[(x, y)] = loot

    @staticmethod
    def from_broadcast(data: dict[str, Any]) -> 'LootContainer':
        result = LootContainer(data['width'], data['height'])
        for x, y, loot_update in data['loot']:
            loot = Loot.from_broadcast(loot_update)
            result.loot[(x, y)] = loot
        return result
