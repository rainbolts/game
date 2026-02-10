from models.Area import Area
from models.Enemy import Enemy, NormalEnemy, BossEnemy
from models.Loot import RingLoot
from systems.AreaSystem import AreaSystem


class LootSystem:
    def __init__(self, area_system: AreaSystem, server_id: int):
        self.area_system = area_system
        self.server_id = server_id
        self.next_item_id = 1

    def check_collisions(self):
        for area in self.area_system.areas:
            for loot in area.loots:
                loot_rect = loot.image.get_rect(topleft=loot.get_pixel_location())
                for player in area.players:
                    player_rect = player.image.get_rect(topleft=player.get_pixel_location())
                    if loot_rect.colliderect(player_rect):
                        area.loots.remove(loot)
                        player.inventory.try_add_loot(loot)

    def generate_loot(self, area: Area, enemy: Enemy):
        if isinstance(enemy, NormalEnemy):
            num_loot = 1
        elif isinstance(enemy, BossEnemy):
            num_loot = 2
        else:
            raise ValueError(f'Unknown enemy type: {type(enemy)}')

        for _ in range(num_loot):
            loot_id = self.next_item_id
            self.next_item_id += 1
            area.loots.add(RingLoot(self.server_id, loot_id, enemy.get_pixel_location()))
