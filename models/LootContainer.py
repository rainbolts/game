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
        for y in range(self.height - loot.height + 1):
            for x in range(self.width - loot.width + 1):
                if self.try_add_loot_at_position(loot, (x, y)):
                    return True

        return False

    def try_add_loot_at_position(self, loot: Loot, position: tuple[int, int]) -> bool:
        for dy in range(loot.height):
            for dx in range(loot.width):
                if (position[0] + dx, position[1] + dy) in self.loot:
                    return False
        self.loot[(position[0], position[1])] = loot
        return True

    def to_grid(self) -> list[list[bool]]:
        grid = [[False for _ in range(self.width)] for _ in range(self.height)]
        for (x, y) in self.loot.keys():
            grid[y][x] = True
        return grid
