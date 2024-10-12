from models.Area import Area
from models.Enemy import Enemy, NormalEnemy, BossEnemy
from models.Loot import RingLoot


class LootSystem:
    @staticmethod
    def generate_loot(area: Area, enemy: Enemy):
        if isinstance(enemy, NormalEnemy):
            num_loot = 1
        elif isinstance(enemy, BossEnemy):
            num_loot = 2
        else:
            raise ValueError(f'Unknown enemy type: {type(enemy)}')

        for _ in range(num_loot):
            area.loots.add(RingLoot(enemy.get_pixel_location()))