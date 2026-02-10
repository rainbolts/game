import math
import socket
from enum import IntEnum, auto
from functools import partial
from typing import Callable

import pygame

from models.Direction import Direction
from models.Player import Player


class Control(IntEnum):
    QUIT = auto()
    CHARACTER_PANEL = auto()
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    MOVE_UP = auto()
    MOVE_DOWN = auto()
    STOP_MOVE_LEFT = auto()
    STOP_MOVE_RIGHT = auto()
    STOP_MOVE_UP = auto()
    STOP_MOVE_DOWN = auto()
    SKILL1 = auto()
    STOP_SKILL1 = auto()
    AIM = auto()
    BASIC_INTERACTION = auto()


class InputSystem:
    def __init__(self, server: socket.socket) -> None:
        self.server = server
        self.subscriptions: dict[Control, set[Callable]] = {}
        self.player: Player | None = None
        self.attacking: bool = False
        self.game_width, self.game_height = self._get_game_size()
        self.control_input_map = {
            Control.QUIT: [(pygame.QUIT, None)],
            Control.CHARACTER_PANEL: [(pygame.KEYDOWN, pygame.K_i)],
            Control.MOVE_LEFT: [(pygame.KEYDOWN, pygame.K_a)],
            Control.MOVE_RIGHT: [(pygame.KEYDOWN, pygame.K_d)],
            Control.MOVE_UP: [(pygame.KEYDOWN, pygame.K_w)],
            Control.MOVE_DOWN: [(pygame.KEYDOWN, pygame.K_s)],
            Control.STOP_MOVE_LEFT: [(pygame.KEYUP, pygame.K_a)],
            Control.STOP_MOVE_RIGHT: [(pygame.KEYUP, pygame.K_d)],
            Control.STOP_MOVE_UP: [(pygame.KEYUP, pygame.K_w)],
            Control.STOP_MOVE_DOWN: [(pygame.KEYUP, pygame.K_s)],
            Control.SKILL1: [(pygame.MOUSEBUTTONDOWN, 1)],
            Control.STOP_SKILL1: [(pygame.MOUSEBUTTONUP, 1)],
            Control.AIM: [(pygame.MOUSEMOTION, None)],
            Control.BASIC_INTERACTION: [(pygame.MOUSEBUTTONDOWN, 1)]
        }
        self.input_control_map = self.invert_control_input_map()
        self.subscribe_all()

    def invert_control_input_map(self) -> dict[tuple[int, int], Control]:
        inverted_map = {}
        for control, inputs in self.control_input_map.items():
            for event_type, key in inputs:
                if (event_type, key) not in inverted_map:
                    inverted_map[(event_type, key)] = []
                inverted_map[(event_type, key)].append(control)
        return inverted_map

    def subscribe(self, control: Control, callback: Callable) -> None:
        if control not in self.subscriptions:
            self.subscriptions[control] = set()
        self.subscriptions[control].add(callback)

    def unsubscribe(self, control: Control, callback: Callable) -> None:
        if control in self.subscriptions:
            self.subscriptions[control].discard(callback)
            if not self.subscriptions[control]:
                del self.subscriptions[control]

    def handle_events(self) -> None:
        for event in pygame.event.get():
            # Translate event to control
            is_mouse = event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP)
            is_key = event.type in (pygame.KEYDOWN, pygame.KEYUP)
            key = None
            if is_mouse:
                key = event.button
            elif is_key:
                key = event.key
            controls = self.input_control_map.get((event.type, key), [])

            # Notify subscribers
            for control in controls:
                if control in self.subscriptions:
                    for callback in self.subscriptions[control]:
                        callback(event)

    def subscribe_all(self):
        self.subscribe(Control.MOVE_UP, partial(self.move_start, Direction.UP))
        self.subscribe(Control.MOVE_DOWN, partial(self.move_start, Direction.DOWN))
        self.subscribe(Control.MOVE_LEFT, partial(self.move_start, Direction.LEFT))
        self.subscribe(Control.MOVE_RIGHT, partial(self.move_start, Direction.RIGHT))
        self.subscribe(Control.STOP_MOVE_UP, partial(self.move_stop, Direction.UP))
        self.subscribe(Control.STOP_MOVE_DOWN, partial(self.move_stop, Direction.DOWN))
        self.subscribe(Control.STOP_MOVE_LEFT, partial(self.move_stop, Direction.LEFT))
        self.subscribe(Control.STOP_MOVE_RIGHT, partial(self.move_stop, Direction.RIGHT))
        self.subscribe(Control.SKILL1, self.attack_start)
        self.subscribe(Control.STOP_SKILL1, self.attack_stop)
        self.subscribe(Control.AIM, self.attack_aim)

    def move_start(self, direction: Direction, _) -> None:
        self.server.sendall(f'move:{direction.value}\n'.encode())

    def move_stop(self, direction: Direction, _) -> None:
        self.server.sendall(f'stop:{direction.value}\n'.encode())

    def attack_start(self, _):
        if not self.player:
            return

        offset = self.get_offset(self.player)
        angle, magnitude = self.vector_to_cursor(self.player, offset)
        self.server.sendall(f'attack:{angle},{magnitude}\n'.encode())
        self.attacking = True

    def attack_aim(self, _):
        if self.attacking:
            self.attack_start(_)

    def attack_stop(self, _):
        self.server.sendall('attack_stop\n'.encode())
        self.attacking = False

    def get_offset(self, player: Player) -> tuple[int, int]:
        x, y = player.get_center()
        return int(round(self.game_width / 2 - x)), int(round(self.game_height / 2 - y))

    @staticmethod
    def vector_to_cursor(player: Player, player_offset: tuple[int, int]) -> tuple[float, float]:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        player_x, player_y = map(int, player.get_center())
        x = mouse_x - player_x - player_offset[0]
        y = -1 * (mouse_y - player_y - player_offset[1])
        angle = math.atan2(y, x) / math.pi * 180
        magnitude = math.sqrt(x ** 2 + y ** 2)
        return angle, magnitude

    @staticmethod
    def _get_game_size() -> tuple[int, int]:
        display_info = pygame.display.Info()
        aspect_ratio = display_info.current_w / display_info.current_h
        game_height = 720
        game_width = int(game_height * aspect_ratio)
        return game_width, game_height
