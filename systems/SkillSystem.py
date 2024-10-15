import pygame
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
        current_time = pygame.time.get_ticks()
        for area in self.area_system.areas:
            for player in area.players:
                if player in self.attacking:
                    last_attacked_time = player.last_attacked_time
                    attacks_per_second = player.attacks_per_second
                    attack_delay = 1000 / attacks_per_second
                    if current_time - last_attacked_time < attack_delay:
                        continue

                    destination_vector = self.attacking[player]

                    origin = player.get_center()
                    skill = Skill(origin, destination_vector)
                    projectiles = skill.spawn_projectiles()
                    area.projectiles.add(projectiles)

                    player.last_attacked_time = current_time

            for projectile in area.projectiles:
                projectile.age()
