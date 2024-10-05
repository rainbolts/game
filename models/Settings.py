import math
from enum import IntEnum, auto

import pygame

from models.Player import Player


class Controls(IntEnum):
    MENU = auto()
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    MOVE_UP = auto()
    MOVE_DOWN = auto()
    SKILL1 = auto()
    SKILL2 = auto()


class Settings:
    def __init__(self) -> None:
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
            Controls.SKILL1: 1,
            Controls.SKILL2: 3
        }

    @staticmethod
    def get_game_size() -> tuple[int, int]:
        display_info = pygame.display.Info()
        aspect_ratio = display_info.current_w / display_info.current_h
        game_height = 720
        game_width = int(game_height * aspect_ratio)

        return game_width, game_height

    @staticmethod
    def vector_to_cursor(player: Player, player_offset: tuple[int, int]) -> tuple[float, float]:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        player_x, player_y = map(int, player.rect.center)
        x = mouse_x - player_x - player_offset[0]
        y = -1 * (mouse_y - player_y - player_offset[1])
        angle = math.atan2(y, x) / math.pi * 180
        magnitude = math.sqrt(x ** 2 + y ** 2)
        return angle, magnitude

    def is_hotkey(self, key, control) -> bool:
        if control not in self.hotkeys:
            return False
        return self.hotkeys[control] == key

    def is_mouse_hotkey(self, mouse_key, control) -> bool:
        if control not in self.mouse_hotkeys:
            return False
        return self.mouse_hotkeys[control] == mouse_key
