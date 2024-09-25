import math
from abc import ABC

from pygame import Mask, Vector2
from pygame.key import ScancodeWrapper

from models.Behaviors import CollisionBehavior
from models.Entity import Entity
from models.Area import Area
from models.Player import Player
from models.Settings import Settings


class MovementSystem(ABC):
    def __init__(self, settings: Settings):
        self.settings = settings

    def move(self, keys: ScancodeWrapper, area: Area):
        raise NotImplementedError

    def try_get_actual_velocity(self, keys: ScancodeWrapper, entity: Entity, area: Area) -> tuple[float, float] | None:
        preferred_velocity = entity.get_preferred_velocity(keys)
        if preferred_velocity == (0, 0):
            return 0, 0

        collision_behaviors = entity.get_collision_behaviors()

        area_mask = area.mask
        move_x, did_collide_x = self._get_move_x(entity, preferred_velocity, area, area_mask)
        move_y, did_collide_y = self._get_move_y(entity, preferred_velocity, area, area_mask)

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

        actual_velocity = Vector2(move_x, move_y)
        return actual_velocity.x, actual_velocity.y

    @staticmethod
    def _get_move_x(entity: Entity, preferred_velocity: Vector2, floor: Area, floor_mask: Mask) -> tuple[float, bool]:
        did_collide = False
        current_location = entity.get_precise_location()
        move = preferred_velocity.x
        new_pos = int(round(current_location[0] + preferred_velocity.x))
        entity_offset = (new_pos - floor.offset[0]), (current_location[1] - floor.offset[1])
        overlap = floor_mask.overlap(entity.mask, entity_offset)
        if overlap:
            did_collide = True
            overlap_mask = floor_mask.overlap_mask(entity.mask, entity_offset)
            overlap_rect = overlap_mask.get_bounding_rects()[0]
            overlap = overlap_rect.x
            overlap_width = overlap_rect.width
            move = (overlap - current_location[0] + floor.offset[0]
                    - (entity.width / 2 + entity.width / 2 * math.copysign(1, preferred_velocity.x))
                    + (overlap_width / 2 - overlap_width / 2 * math.copysign(1, preferred_velocity.x)))
        return move, did_collide

    @staticmethod
    def _get_move_y(entity: Entity, preferred_velocity: Vector2, floor: Area, floor_mask: Mask) -> tuple[float, bool]:
        did_collide = False
        current_location = entity.get_precise_location()
        move = -preferred_velocity.y
        new_pos = int(round(current_location[1] + move))
        entity_offset = (current_location[0] - floor.offset[0]), (new_pos - floor.offset[1])
        overlap = floor_mask.overlap(entity.mask, entity_offset)
        if overlap:
            did_collide = True
            overlap_mask = floor_mask.overlap_mask(entity.mask, entity_offset)
            overlap_rect = overlap_mask.get_bounding_rects()[0]
            overlap = overlap_rect.y
            overlap_height = overlap_rect.height
            move = (overlap - current_location[1] + floor.offset[1]
                    - (entity.height / 2 + entity.height / 2 * math.copysign(1, -preferred_velocity.y))
                    + (overlap_height / 2 - overlap_height / 2 * math.copysign(1, -preferred_velocity.y)))
        return move, did_collide


class AreaCentricMovementSystem(MovementSystem):
    def move(self, keys: ScancodeWrapper, area: Area):
        for entity in Entity.entity_group:
            actual_velocity = self.try_get_actual_velocity(keys, entity, area)
            if actual_velocity:
                entity.move_precisely(*actual_velocity)


class PlayerCentricMovementSystem(MovementSystem):
    def move(self, keys: ScancodeWrapper, area: Area):
        dx, dy = 0, 0
        for entity in Entity.entity_group:
            actual_velocity = self.try_get_actual_velocity(keys, entity, area)
            if actual_velocity:
                if isinstance(entity, Player):
                    x, y = entity.rect.x, entity.rect.y
                    entity.move_precisely(*actual_velocity)
                    dx, dy = int(entity.rect.x - x), int(entity.rect.y - y)
                else:
                    entity.move_precisely(*actual_velocity)

        if dx or dy:
            negative_velocity = -dx, -dy
            area.move(*negative_velocity)
            for other_entity in Entity.entity_group:
                other_entity.move_precisely(*negative_velocity)

