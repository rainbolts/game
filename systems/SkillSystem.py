from pygame import Vector2

from models.Player import Player
from models.Projectile import Projectile
from models.skills.Skill import Skill


class SkillSystem:
    def __init__(self) -> None:
        self.attacking: dict[Player, Vector2] = {}

    def start_attacking(self, player, destination_vector: Vector2) -> None:
        self.attacking[player] = destination_vector

    def stop_attacking(self, player: Player) -> None:
        if player in self.attacking:
            del self.attacking[player]

    def use_skills(self) -> None:
        for player, destination_vector in self.attacking.copy().items():
            origin = player.get_center()
            skill = Skill(origin, destination_vector)
            skill.spawn_projectiles()

        for projectile in Projectile.projectile_group:
            projectile.age()
