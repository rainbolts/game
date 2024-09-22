from enum import IntEnum, auto

import pygame


class Controls(IntEnum):
    MENU = auto()
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    MOVE_UP = auto()
    MOVE_DOWN = auto()
    SKILL1 = auto()
    SKILL2 = auto()


class Settings:
    def __init__(self):
        self.game_width, self.game_height = self.get_game_size()
        self.hotkeys = {
            Controls.MENU: pygame.K_ESCAPE,
            Controls.MOVE_LEFT: pygame.K_a,
            Controls.MOVE_RIGHT: pygame.K_d,
            Controls.MOVE_UP: pygame.K_w,
            Controls.MOVE_DOWN: pygame.K_s,
            Controls.SKILL1: pygame.MOUSEBUTTONDOWN,
            Controls.SKILL2: pygame.MOUSEBUTTONDOWN
        }
        self.mouse_hotkeys = {
            Controls.MOVE_LEFT: 1,
            Controls.SKILL1: 1,
            Controls.SKILL2: 3
        }

    @staticmethod
    def get_game_size():
        display_info = pygame.display.Info()
        aspect_ratio = display_info.current_w / display_info.current_h
        game_height = 720
        game_width = int(game_height * aspect_ratio)

        return game_width, game_height

    def hotkey_pressed(self, keys, control):
        if self.hotkeys[control] == pygame.MOUSEBUTTONDOWN:
            return pygame.mouse.get_pressed()[self.mouse_hotkeys[control] - 1]
        else:
            return keys[self.hotkeys[control]]
