from models.Area import Area
from models.Enemy import BossEnemy, NormalEnemy


class EnemySystem:
    def spawn_enemies(self, area: Area):
        num_packs = 4
        for _ in range(num_packs):
            self.spawn_pack(area)

        boss_spawn = area.get_boss_spawn()
        boss = BossEnemy(boss_spawn, 15)
        area.enemies.add(boss)

    def spawn_pack(self, area: Area):
        num_enemies = 5
        pack_location = self.get_pack_location(area)
        for _ in range(num_enemies):
            self.spawn_enemy(area, pack_location)

    @staticmethod
    def spawn_enemy(area: Area, pack_location: tuple[int, int]):
        tiles = area.tiles

        # Find a random empty space near the pack location
        # Empty spaces are denoted by False
        x, y = pack_location
        while True:
            x += area.random.choice([-1, 0, 1])
            y += area.random.choice([-1, 0, 1])

            if x < 0 or y < 0 or x >= len(tiles) or y >= len(tiles):
                continue

            if not tiles[y][x]:
                enemy_location = x * 40, y * 40
                enemy = NormalEnemy(enemy_location, 3)
                area.enemies.add(enemy)
                break

    @staticmethod
    def get_pack_location(area: Area) -> tuple[int, int]:
        tiles = area.tiles

        # Find a random empty space in tiles
        # Empty spaces are denoted by False
        x, y = 0, 0
        while tiles[y][x]:
            x = area.random.randint(0, len(tiles) - 1)
            y = area.random.randint(0, len(tiles) - 1)

            if not tiles[y][x]:
                return x, y

        return x, y
