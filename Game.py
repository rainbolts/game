import sys
from enum import IntEnum

import pygame

from models.Enemy import Enemy
from models.Entity import Entity
from models.Area import Area
from models.Player import Player
from models.Settings import Settings
from systems.AreaSystem import AreaSystem
from systems.DamageSystem import DamageSystem
from systems.MovementSystem import PlayerCentricMovementSystem, AreaCentricMovementSystem
from systems.SkillSystem import SkillSystem


class Event(IntEnum):
    FPS = pygame.USEREVENT + 1


class Game:
    def __init__(self):
        pygame.init()

        if self.debug_enabled():
            window_flags = pygame.SCALED
        else:
            window_flags = pygame.FULLSCREEN | pygame.SCALED

        self.settings = Settings()
        self.window = pygame.display.set_mode((self.settings.game_width, self.settings.game_height), window_flags)
        self.clock = pygame.time.Clock()

        self.area_system = AreaSystem()
        self.movement_system = PlayerCentricMovementSystem(self.settings)
        self.skill_system = SkillSystem()
        self.damage_system = DamageSystem()

        self.player = Player((self.settings.game_width // 2, self.settings.game_height // 2), self.settings)
        Enemy((60, 60), 1000)

    def run(self):
        should_run = True

        pygame.time.set_timer(Event.FPS, 1000)

        while should_run:
            self.clock.tick(100)
            self.window.fill(0)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    should_run = False

                if event.type == Event.FPS:
                    self.update_fps()

            keys = pygame.key.get_pressed()
            mouse_position = pygame.mouse.get_pos()

            self.area_system.generate_area()
            self.movement_system.move(keys, self.area_system.current_area)
            self.skill_system.use_skills(keys, mouse_position)
            self.damage_system.apply_damage()

            self.window.blit(self.area_system.current_area, self.area_system.current_area.offset)
            Entity.entity_group.draw(self.window)
            self.update_fps()

            pygame.display.update()

    def update_fps(self):
        fps = self.clock.get_fps()
        font = pygame.font.SysFont('Arial', 16)
        text_to_show = font.render(str(int(fps)), False, (150, 150, 255))
        self.window.blit(text_to_show, (0, 0))

    @staticmethod
    def debug_enabled():
        # https://stackoverflow.com/a/77627075/3224483
        try:
            if sys.gettrace() is not None:
                return True
        except AttributeError:
            pass

        try:
            if sys.monitoring.get_tool(sys.monitoring.DEBUGGER_ID) is not None:
                return True
        except AttributeError:
            pass

        return False


if __name__ == '__main__':
    Game().run()
