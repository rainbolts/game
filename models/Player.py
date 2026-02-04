import math
from typing import Any

from pygame import Vector2

from models.Direction import Direction
from models.Entity import Entity
from models.LootContainer import LootContainer


class Player(Entity):
    def __init__(self, client_id: int | None, spawn: tuple[int, int]):
        super().__init__(spawn, 40, 40, (0, 255, 0))
        self.client_id = client_id
        self.movement_speed: float = 3.0
        self.attacks_per_second: float = 1.0

        self.last_direction: Direction = Direction.DOWN
        self.last_attacked_time: int = 0

        self.inventory = LootContainer(10, 10)
        self.show_character_panel = False

    def set_preferred_velocity(self, direction: Direction):
        go_left = Direction.LEFT in direction
        go_right = Direction.RIGHT in direction
        go_up = Direction.UP in direction
        go_down = Direction.DOWN in direction

        # No movement
        if not go_left and not go_right and not go_up and not go_down:
            self._preferred_velocity.from_polar((0, 0))

        # Opposing horizontal movement, no vertical
        elif go_left and go_right and not go_up and not go_down:
            self._preferred_velocity.from_polar((0, 0))

        # Opposing vertical movement, no horizontal
        elif not go_left and not go_right and go_up and go_down:
            self._preferred_velocity.from_polar((0, 0))

        # Opposing vertical and horizontal movement
        elif go_left and go_right and go_up and go_down:
            self._preferred_velocity.from_polar((0, 0))

        else:
            direction = math.atan2(go_up - go_down, go_right - go_left)
            self._preferred_velocity.from_polar((self.movement_speed, direction / math.pi * 180))

    def get_preferred_velocity(self) -> Vector2:
        return self._preferred_velocity

    def to_broadcast(self) -> dict[str, Any]:
        result = super().to_broadcast()
        result['client_id'] = self.client_id
        result['inventory'] = self.inventory.to_broadcast()
        return result

    def merge_broadcast(self, data: dict[str, Any]):
        super().merge_broadcast(data)
        self.inventory.merge_broadcast(data['inventory'])

    @staticmethod
    def from_broadcast(data: dict[str, Any]) -> 'Player':
        result = Player(int(data['client_id']), (int(data['x']), int(data['y'])))
        vx = float(data['vx'])
        vy = float(data['vy'])
        result._preferred_velocity = Vector2(vx, vy)
        result.inventory = LootContainer.from_broadcast(data['inventory'])
        return result
