from models.Behaviors import CollisionBehavior
from models.Enemy import BossEnemy
from models.ExitDoor import ExitDoor
from systems.AreaSystem import AreaSystem
from systems.LootSystem import LootSystem


class DamageSystem:
    def __init__(self, area_system: AreaSystem, loot_system: LootSystem):
        self.area_system = area_system
        self.loot_system = loot_system

    def apply_damage(self):
        for area in self.area_system.areas:
            for enemy in area.enemies:
                enemy_rect = enemy.image.get_rect(topleft=enemy.get_pixel_location())
                for projectile in area.projectiles:
                    proj_rect = projectile.image.get_rect(topleft=projectile.get_pixel_location())
                    if not enemy_rect.colliderect(proj_rect):
                        continue

                    collision_behaviors = projectile.get_collision_behaviors()
                    if CollisionBehavior.DAMAGE in collision_behaviors:
                        enemy.health -= projectile.damage
                        if enemy.health <= 0:
                            if isinstance(enemy, BossEnemy):
                                area.exit = ExitDoor(enemy.get_pixel_location())
                            self.loot_system.generate_loot(area, enemy)
                            enemy.kill()

                    if CollisionBehavior.DISAPPEAR in collision_behaviors:
                        projectile.kill()
