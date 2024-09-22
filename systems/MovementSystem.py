import math
from abc import ABC

from pygame import Mask, Vector2
from pygame.key import ScancodeWrapper

from models import Enemy, Floor, Player, Entity
from models.Settings import Settings


class MovementSystem(ABC):
    def __init__(self, settings: Settings, floor: Floor, player: Player):
        self.settings: Settings = settings
        self.floor: Floor = floor
        self.player: Player = player
        self.entities: list[Enemy] = []

    def move(self, keys: ScancodeWrapper):
        raise NotImplementedError

    def add_entity(self, entity: Entity):
        self.entities.append(entity)

    def get_actual_velocity(self, keys: ScancodeWrapper, entity: Entity):
        preferred_velocity = entity.get_preferred_velocity(keys)

        floor_mask = self.floor.mask
        move_x = self._get_move_x(self.player, preferred_velocity, self.floor, floor_mask)
        move_y = self._get_move_y(self.player, preferred_velocity, self.floor, floor_mask)

        actual_velocity = Vector2(move_x, move_y)
        return int(round(actual_velocity.x)), int(round(actual_velocity.y))

    @staticmethod
    def _get_move_x(entity: Entity, preferred_velocity: Vector2, floor: Floor, floor_mask: Mask) -> int:
        move = int(round(preferred_velocity.x))
        new_pos = entity.x + move
        entity_offset = (new_pos - floor.offset[0]), (entity.y - floor.offset[1])
        overlap = floor_mask.overlap(entity.mask, entity_offset)
        if overlap:
            overlap_mask = floor_mask.overlap_mask(entity.mask, entity_offset)
            overlap_rect = overlap_mask.get_bounding_rects()[0]
            overlap = overlap_rect.x
            overlap_width = overlap_rect.width
            move = overlap - entity.x + floor.offset[0] - int(entity.width / 2 + entity.width / 2 * math.copysign(1, move)) + int(overlap_width / 2 - overlap_width / 2 * math.copysign(1, move))
        return move

    @staticmethod
    def _get_move_y(entity: Entity, preferred_velocity: Vector2, floor: Floor, floor_mask: Mask) -> int:
        move = -int(round(preferred_velocity.y))
        new_pos = entity.y + move
        entity_offset = (entity.x - floor.offset[0]), (new_pos - floor.offset[1])
        overlap = floor_mask.overlap(entity.mask, entity_offset)
        if overlap:
            overlap_mask = floor_mask.overlap_mask(entity.mask, entity_offset)
            overlap_rect = overlap_mask.get_bounding_rects()[0]
            overlap = overlap_rect.y
            overlap_height = overlap_rect.height
            move = overlap - entity.y + floor.offset[1] - int(entity.height / 2 + entity.height / 2 * math.copysign(1, move)) + int(overlap_height / 2 - overlap_height / 2 * math.copysign(1, move))
        return move


class FloorCentricMovementSystem(MovementSystem):
    def __init__(self, settings: Settings, floor: Floor, player: Player):
        super().__init__(settings, floor, player)
        self.entities.append(player)

    def move(self, keys: ScancodeWrapper):
        for entity in self.entities:
            actual_velocity = self.get_actual_velocity(keys, entity)
            entity.move(*actual_velocity)


class PlayerCentricMovementSystem(MovementSystem):
    def move(self, keys: ScancodeWrapper):
        for entity in self.entities:
            actual_velocity = self.get_actual_velocity(keys, entity)
            entity.move(*actual_velocity)

        player_velocity = self.get_actual_velocity(keys, self.player)
        negative_velocity = -player_velocity[0], -player_velocity[1]
        if player_velocity != (0, 0):
            self.floor.move(*negative_velocity)
            for entity in self.entities:
                entity.move(*negative_velocity)
