from pygame import Vector2

from models.Area import Area
from models.Behaviors import CollisionBehavior
from models.Direction import Direction
from models.Entity import Entity
from models.Player import Player
from models.Projectile import Projectile


class MovementSystem:
    def __init__(self):
        self.moving: dict[Player, Direction] = {}

    def start_moving(self, player, direction: Direction):
        if player not in self.moving:
            self.moving[player] = Direction(0)
        self.moving[player] = self.moving[player] | direction

    def stop_moving(self, player: Player, direction: Direction):
        if player not in self.moving:
            return
        self.moving[player] = self.moving[player] & ~direction

    def move(self, area: Area):
        for player in self.moving:
            player.set_preferred_velocity(self.moving[player])
            actual_velocity = self.try_get_actual_velocity(player, area)
            if actual_velocity is None:
                continue
            if actual_velocity == (0, 0):
                continue
            player.move_relative(*actual_velocity)

        for projectile in Projectile.projectile_group:
            actual_velocity = self.try_get_actual_velocity(projectile, area)
            if actual_velocity is None:
                continue
            if actual_velocity == (0, 0):
                continue
            projectile.move_relative(*actual_velocity)

    def try_get_actual_velocity(self, entity: Entity, area: Area) -> tuple[float, float] | None:
        preferred_velocity = entity.get_preferred_velocity()
        if preferred_velocity is None:
            return None
        if preferred_velocity == (0, 0):
            return 0, 0

        collision_behaviors = entity.get_collision_behaviors()

        move_x, did_collide_x = self._get_move_x(entity, preferred_velocity, area)
        move_y, did_collide_y = self._get_move_y(entity, move_x, preferred_velocity, area)

        if CollisionBehavior.STICKY in collision_behaviors and (did_collide_x or did_collide_y):
            preferred_velocity.from_polar((0, 0))
            return 0, 0

        if CollisionBehavior.DISAPPEAR in collision_behaviors and (did_collide_x or did_collide_y):
            entity.kill()
            return None

        if CollisionBehavior.BOUNCE in collision_behaviors and did_collide_x:
            preferred_velocity.x *= -1
        if CollisionBehavior.BOUNCE in collision_behaviors and did_collide_y:
            preferred_velocity.y *= -1

        return move_x, move_y

    @staticmethod
    def _get_move_x(entity: Entity, preferred_velocity: Vector2, area: Area) -> tuple[float, bool]:
        current_location = entity.get_precise_location()
        move = preferred_velocity.x
        new_pos = int(round(current_location[0] + preferred_velocity.x))
        entity_offset = new_pos, int(round(current_location[1]))
        overlap = area.mask.overlap(entity.mask, entity_offset)
        if overlap:
            return 0, True
        return move, False

    @staticmethod
    def _get_move_y(entity: Entity, move_x: float, preferred_velocity: Vector2, area: Area) -> tuple[float, bool]:
        current_location = entity.get_precise_location()
        current_location = current_location[0] + move_x, current_location[1]
        move = -preferred_velocity.y
        new_pos = int(round(current_location[1] + move))
        entity_offset = int(round(current_location[0])), new_pos
        overlap = area.mask.overlap(entity.mask, entity_offset)
        if overlap:
            return 0, True
        return move, False
