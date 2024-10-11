from pygame import Vector2

from models.Player import Player
from models.skills.Skill import Skill
from systems.AreaSystem import AreaSystem


class SkillSystem:
    def __init__(self, area_system: AreaSystem) -> None:
        self.area_system = area_system
        self.attacking: dict[Player, Vector2] = {}

    def start_attacking(self, player, destination_vector: Vector2) -> None:
        self.attacking[player] = destination_vector

    def stop_attacking(self, player: Player) -> None:
        if player in self.attacking:
            del self.attacking[player]

    def use_skills(self) -> None:
        for area in self.area_system.areas:
            for player in area.players:
                if player in self.attacking:
                    destination_vector = self.attacking[player]

                    origin = player.get_center()
                    skill = Skill(origin, destination_vector)
                    projectiles = skill.spawn_projectiles()
                    area.projectiles.add(projectiles)

            for projectile in area.projectiles:
                projectile.age()
