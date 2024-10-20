from models.Area import Area
from models.Enemy import Enemy, NormalEnemy, BossEnemy
from models.Loot import RingLoot
from systems.AreaSystem import AreaSystem


class LootSystem:
    def __init__(self, area_system: AreaSystem):
        self.area_system = area_system

    def check_collisions(self):
        for area in self.area_system.areas:
            for loot in area.loots:
                loot_rect = loot.image.get_rect(topleft=loot.get_pixel_location())
                for player in area.players:
                    player_rect = player.image.get_rect(topleft=player.get_pixel_location())
                    if loot_rect.colliderect(player_rect):
                        area.loots.remove(loot)
                        player.inventory.try_add_loot(loot)

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