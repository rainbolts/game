import time
from enum import Flag, auto

from models.Player import Player


class Direction(Flag):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()


class MovementSystem:
    def __init__(self):
        self.moving: dict[Player, Direction] = {}

    def start_moving(self, player, direction: Direction):
        if player not in self.moving:
            self.moving[player] = Direction(0)
            player.last_move_time = time.time()
        self.moving[player] = self.moving[player] | direction

    def stop_moving(self, player: Player, direction: Direction):
        if player not in self.moving:
            return
        self.moving[player] = self.moving[player] & ~direction

    def move(self):
        for player in self.moving:
            if player.position is None:
                return

            current_time = time.time()
            last_move_time = player.last_move_time

            time_delta = current_time - last_move_time

            move_distance = min(player.movement_speed * time_delta, player.movement_speed)

            x, y = player.position

            if Direction.UP in self.moving[player]:
                y -= move_distance
            if Direction.DOWN in self.moving[player]:
                y += move_distance
            if Direction.LEFT in self.moving[player]:
                x -= move_distance
            if Direction.RIGHT in self.moving[player]:
                x += move_distance

            player.position = (x, y)
            player.last_move_time = current_time
