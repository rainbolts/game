from models.Behaviors import CollisionBehavior
from models.Enemy import Enemy
from models.Projectile import Projectile


class DamageSystem:
    def apply_damage(self):
        enemies = Enemy.enemy_group
        projectiles = Projectile.projectile_group
        for projectile in projectiles:
            for enemy in enemies:
                if not enemy.rect.colliderect(projectile.rect):
                    continue

                collision_behaviors = projectile.get_collision_behaviors()
                if CollisionBehavior.DAMAGE in collision_behaviors:
                    enemy.health -= projectile.damage
                    if enemy.health <= 0:
                        enemy.kill()

                if CollisionBehavior.DISAPPEAR in collision_behaviors:
                    projectile.kill()