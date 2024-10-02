import math

from pygame.key import ScancodeWrapper

from models import Settings
from models.Entity import Entity
from models.Settings import Controls
from models.skills.Skill import Skill


class Player(Entity):
    def __init__(self, spawn: tuple[int, int], settings: Settings):
        super().__init__(spawn, 40, 40, (0, 255, 0))
        self.settings = settings
        self.maximum_speed = 4
        self.last_time_did_move = False
        self.last_time_keys_pressed = [False, False, False, False]

    def get_collision_behaviors(self):
        return []

    def get_preferred_velocity(self, keys: ScancodeWrapper):
        self._preferred_velocity.from_polar((0, 0))

        left_pressed = self.settings.hotkey_pressed(keys, Controls.MOVE_LEFT)
        right_pressed = self.settings.hotkey_pressed(keys, Controls.MOVE_RIGHT)
        up_pressed = self.settings.hotkey_pressed(keys, Controls.MOVE_UP)
        down_pressed = self.settings.hotkey_pressed(keys, Controls.MOVE_DOWN)

        # Same movement as last time, and last time we didn't move
        # If objects with collision start moving, this check will become invalid
        this_time_keys_pressed = [left_pressed, right_pressed, up_pressed, down_pressed]
        if not self.last_time_did_move and this_time_keys_pressed == self.last_time_keys_pressed:
            return self._preferred_velocity

        # No movement
        if not left_pressed and not right_pressed and not up_pressed and not down_pressed:
            return self._preferred_velocity

        # Opposing horizontal (cancels out), no vertical
        if left_pressed and right_pressed and not up_pressed and not down_pressed:
            return self._preferred_velocity

        # Opposing vertical (cancels out), no horizontal
        if not left_pressed and not right_pressed and up_pressed and down_pressed:
            return self._preferred_velocity

        # Opposing vertical and horizontal
        if left_pressed and right_pressed and up_pressed and down_pressed:
            return self._preferred_velocity

        direction = math.atan2(up_pressed - down_pressed, right_pressed - left_pressed)
        self._preferred_velocity.from_polar((self.maximum_speed, direction / math.pi * 180))
        return self._preferred_velocity

    def get_preferred_skills(self, keys: ScancodeWrapper, mouse_position: tuple[int, int]) -> list[Skill]:
        if self.settings.hotkey_pressed(keys, Controls.SKILL1):
            proj_x = int(round(self.rect.centerx))
            proj_y = int(round(self.rect.centery))
            return [Skill((proj_x, proj_y), mouse_position)]
        else:
            return []
