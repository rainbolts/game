import sys
from enum import IntEnum

import pygame

from models.Enemy import Enemy
from models.Floor import Floor
from models.Player import Player
from models.Projectile import Projectile
from models.Settings import Settings
from systems.MovementSystem import PlayerCentricMovementSystem, FloorCentricMovementSystem


class Event(IntEnum):
    FPS = pygame.USEREVENT + 1


class Game:
    def __init__(self):
        pygame.init()

        self.settings = Settings()

        if self.debug_enabled():
            window_flags = pygame.SCALED
        else:
            window_flags = pygame.FULLSCREEN | pygame.SCALED
        self.window = pygame.display.set_mode((self.settings.game_width, self.settings.game_height), window_flags)
        self.clock = pygame.time.Clock()

        self.floor = Floor(offset=(20, 20), width=self.settings.game_width - 40, height=self.settings.game_height - 40)

        player = Player(spawn_x=self.settings.game_width // 2, spawn_y=self.settings.game_height // 2, settings=self.settings)
        self.player_group = pygame.sprite.Group()
        self.player_group.add(player)

        enemy = Enemy(spawn_x=60, spawn_y=60)
        self.enemy_group = pygame.sprite.Group()
        self.enemy_group.add(enemy)

        projectile = Projectile(spawn_x=100, spawn_y=100)
        projectile.get_preferred_velocity(None).from_polar((5, -45))
        self.projectile_group = pygame.sprite.Group()
        self.projectile_group.add(projectile)

        self.movement_system = PlayerCentricMovementSystem(self.settings, self.floor, player)
        self.movement_system.add_entity(enemy)
        self.movement_system.add_entity(projectile)

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

            self.movement_system.move(keys)

            self.window.blit(self.floor, self.floor.offset)
            self.enemy_group.draw(self.window)
            self.player_group.draw(self.window)
            self.projectile_group.draw(self.window)
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
