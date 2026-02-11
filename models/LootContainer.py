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
        # Bounds check top left corner
        x, y = position
        if x < 0 or y < 0:
            return False

        # Bounds check bottom right corner
        if x + loot.inventory_width > self.width or y + loot.inventory_height > self.height:
            return False

        # Check for overlap with existing loot
        for dy in range(loot.inventory_height):
            for dx in range(loot.inventory_width):
                if (x + dx, y + dy) in self.loot:
                    return False

        # Place loot at the requested top-left position
        self.loot[(x, y)] = loot
        self.loot_dict[(loot.server_id, loot.loot_id)] = loot
        return True

    def move_to_container(self,
                          loot: Loot,
                          other_container: 'LootContainer',
                          col: int | None = None,
                          row: int | None = None) -> None:
        # Check loot exists in this container
        source_position = None
        for position, existing_loot in self.loot.items():
            if existing_loot == loot:
                source_position = position
                break
        if source_position is None:
            return

        # Attempt placement in other container
        if col is not None and row is not None:
            placed = other_container.try_add_loot_at_position(loot, (col, row))
        else:
            placed = other_container.try_add_loot(loot)

        if not placed:
            return

        # Remove from this container
        del self.loot[source_position]
        if (loot.server_id, loot.loot_id) in self.loot_dict:
            del self.loot_dict[(loot.server_id, loot.loot_id)]

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
            incoming_loot = Loot.from_broadcast(loot_update)
            incoming_position_dict[(x, y)] = incoming_loot
            incoming_loot_dict[(incoming_loot.server_id, incoming_loot.loot_id)] = incoming_loot

        # Remove, add, update
        for position, existing_loot in list(self.loot.items()):  # NOSONAR Cannot modify iterable while iterating, so copy is required
            if position not in incoming_position_dict:
                del self.loot[position]
                del self.loot_dict[(existing_loot.server_id, existing_loot.loot_id)]

        for position, incoming_loot in incoming_position_dict.items():
            if position not in self.loot:
                self.loot[position] = incoming_loot
                self.loot_dict[(incoming_loot.server_id, incoming_loot.loot_id)] = incoming_loot
            else:
                self.loot[position].merge_broadcast(incoming_position_dict[position].to_broadcast())
                self.loot_dict[(incoming_loot.server_id, incoming_loot.loot_id)] = self.loot[position]

    @staticmethod
    def from_broadcast(data: dict[str, Any]) -> 'LootContainer':
        result = LootContainer(data['width'], data['height'])
        for x, y, loot_update in data['loot']:
            loot = Loot.from_broadcast(loot_update)
            result.loot[(x, y)] = loot
            result.loot_dict[(loot.server_id, loot.loot_id)] = loot
        return result
