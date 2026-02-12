import random

from models.Area import Area
from models.Enemy import Enemy, NormalEnemy, BossEnemy
from models.Loot import RingLoot, Loot
from models.LootModifier import ModifierType, LootModifier
from systems.AreaSystem import AreaSystem


class LootSystem:
    def __init__(self, area_system: AreaSystem, server_id: int) -> None:
        self.area_system = area_system
        self.server_id = server_id
        self.next_loot_id = 1
        self.next_modifier_id = 1

    def check_collisions(self) -> None:
        for area in self.area_system.areas:
            for loot in area.loots:
                loot_rect = loot.image.get_rect(topleft=loot.get_pixel_location())
                for player in area.players:
                    player_rect = player.image.get_rect(topleft=player.get_pixel_location())
                    if loot_rect.colliderect(player_rect):
                        area.loots.remove(loot)
                        player.inventory.try_add_loot(loot)

    def generate_loot(self, area: Area, enemy: Enemy) -> None:
        if isinstance(enemy, NormalEnemy):
            num_loot = 1
        elif isinstance(enemy, BossEnemy):
            num_loot = 2
        else:
            raise ValueError(f'Unknown enemy type: {type(enemy)}')

        for _ in range(num_loot):
            loot_id = self.next_loot_id
            self.next_loot_id += 1
            loot = RingLoot(self.server_id, loot_id, enemy.get_pixel_location())
            self.generate_modifiers(loot)
            area.loots.add(loot)

    def generate_modifiers(self, loot: Loot) -> None:
        num_modifiers = random.randint(1, 3)
        modifier_types = list(ModifierType)
        for _ in range(num_modifiers):
            modifier_id = self.next_modifier_id
            self.next_modifier_id += 1
            modifier_type = random.choice(modifier_types)
            modifier_value = random.randint(1, 100)
            modifier = LootModifier(loot.server_id, loot.loot_id, modifier_id, modifier_type, [modifier_value])
            loot.modifiers.append(modifier)
