import pygame

from models.Settings import Settings
from systems.AreaSystem import AreaSystem
from systems.DamageSystem import DamageSystem
from systems.EnemySystem import EnemySystem
from systems.MovementSystem import PlayerCentricMovementSystem, AreaCentricMovementSystem
from systems.NetCode import NetCodeServer
from systems.PlayerSystem import PlayerSystem
from systems.SkillSystem import SkillSystem


class GameServer:
    def __init__(self):
        pygame.init()

        self.settings = Settings()
        self.server = NetCodeServer()
        self.clock = pygame.time.Clock()

        self.player_system = PlayerSystem(self.settings, self.server)
        self.enemy_system = EnemySystem()
        self.area_system = AreaSystem(self.enemy_system)
        self.movement_system = AreaCentricMovementSystem()
        self.skill_system = SkillSystem()
        self.damage_system = DamageSystem()

    def run(self):
        should_run = True

        while should_run:
            self.clock.tick(500)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    should_run = False

            keys = pygame.key.get_pressed()
            mouse_position = pygame.mouse.get_pos()

            self.player_system.spawn_players()
            self.area_system.generate_area()
            self.movement_system.move(keys, self.area_system.current_area)
            self.skill_system.use_skills(keys, mouse_position)
            self.damage_system.apply_damage()


if __name__ == '__main__':
    GameServer().run()
