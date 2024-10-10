from typing import Any

from models.Behaviors import CollisionBehavior
from models.Entity import Entity


class ExitDoor(Entity):
    def __init__(self, spawn):
        super().__init__(spawn, 40, 40, (128, 0, 128), 0)

    def get_collision_behaviors(self):
        return [CollisionBehavior.AREA_TRANSITION]

    @staticmethod
    def from_broadcast(data: dict[str, Any]) -> 'ExitDoor':
        return ExitDoor((int(data['x']), int(data['y'])))
