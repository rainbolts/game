import time

from pygame import Vector2


class Player:
    def __init__(self, spawn: tuple[int, int]):
        self.position = spawn
        self.movement_speed: int = 200
        self.last_move_time: float = time.time()
        self.preferred_velocity: Vector2 = Vector2(0, 0)
