from typing import Any

from models.Loot import Loot


class LootContainer:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.loot: dict[tuple[int, int], Loot] = {}  # (x, y) of top left corner => loot
        self.loot_dict: dict[tuple[int, int], Loot] = {}  # (server_id, loot_id) => loot

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
        self.loot_dict[(loot.server_id, loot.loot_id)] = loot
        return True

    def move_to_container(self, loot: Loot, other_container: 'LootContainer') -> bool:
        if other_container.try_add_loot(loot):
            for position, existing_loot in self.loot.items():
                if existing_loot == loot:
                    del self.loot[position]
                    del self.loot_dict[(loot.server_id, loot.loot_id)]
                    return True
        return False

    def get_loot(self, server_id: int, loot_id: int) -> Loot | None:
        return self.loot_dict.get((server_id, loot_id))

    def get_loot_count(self) -> int:
        return len(self.loot_dict)

    def to_broadcast(self):
        return {
            'width': self.width,
            'height': self.height,
            'loot': [(x, y, loot.to_broadcast()) for (x, y), loot in self.loot.items()]
        }

    def merge_broadcast(self, data: dict[str, Any]):
        incoming_position_dict = {}
        incoming_loot_dict = {}
        for x, y, loot_update in data['loot']:
            loot = Loot.from_broadcast(loot_update)
            incoming_position_dict[(x, y)] = loot
            incoming_loot_dict[(loot.server_id, loot.loot_id)] = loot

        # Remove, add, update
        for position, loot in list(self.loot.items()):  # NOSONAR Cannot modify iterable while iterating, so copy is required
            if position not in incoming_position_dict:
                del self.loot[position]
                del self.loot_dict[(loot.server_id, loot.loot_id)]

        for position, loot in incoming_position_dict.items():
            if position not in self.loot:
                self.loot[position] = loot
                self.loot_dict[(loot.server_id, loot.loot_id)] = loot
            else:
                self.loot[position].merge_broadcast(incoming_position_dict[position].to_broadcast())
                self.loot_dict[(loot.server_id, loot.loot_id)] = self.loot[position]

    @staticmethod
    def from_broadcast(data: dict[str, Any]) -> 'LootContainer':
        result = LootContainer(data['width'], data['height'])
        for x, y, loot_update in data['loot']:
            loot = Loot.from_broadcast(loot_update)
            result.loot[(x, y)] = loot
            result.loot_dict[(loot.server_id, loot.loot_id)] = loot
        return result
