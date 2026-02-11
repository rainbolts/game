import math
import random

import pygame
from pygame import Surface

from models.Area import Area, TileType
from models.Direction import Direction
from models.Enemy import Enemy
from models.ExitDoor import ExitDoor
from models.Loot import Loot, GearSlot
from models.Player import Player
from models.Projectile import Projectile
from systems.InputSystem import InputSystem, Control
from systems.InteractableSystem import InteractableSystem, Interactable, ScreenLayer


class DrawSystem:
    def __init__(self, clock: pygame.time.Clock, input_system: InputSystem, interactable_system: InteractableSystem) -> None:
        self.input_system = input_system
        self.interactable_system = interactable_system
        self.screen = pygame.display.set_mode((self.input_system.game_width, self.input_system.game_height), pygame.SRCALPHA)
        self.clock = clock
        self.player: Player | None = None
        self.draw_tiles = {
            'player': {
                'sprite_sheet': pygame.image.load('images/player_sprite_sheet.png').convert(),
                Direction.UP: [
                    ((0, 28), (14, 46)),
                    ((0, 52), (14, 70)),
                    ((0, 76), (14, 94)),
                ],
                Direction.UP | Direction.RIGHT: [
                    ((16, 28), (30, 46)),
                    ((16, 52), (30, 70)),
                    ((16, 76), (30, 94)),
                ],
                Direction.RIGHT: [
                    ((32, 28), (46, 46)),
                    ((32, 52), (46, 70)),
                    ((32, 76), (46, 94)),
                ],
                Direction.DOWN | Direction.RIGHT: [
                    ((48, 28), (62, 46)),
                    ((48, 52), (62, 70)),
                    ((48, 76), (62, 94)),
                ],
                Direction.DOWN: [
                    ((64, 28), (78, 46)),
                    ((64, 52), (78, 70)),
                    ((64, 76), (78, 94)),
                ],
                Direction.DOWN | Direction.LEFT: [
                    ((80, 28), (94, 46)),
                    ((80, 52), (94, 70)),
                    ((80, 76), (94, 94)),
                ],
                Direction.LEFT: [
                    ((96, 28), (110, 46)),
                    ((96, 52), (110, 70)),
                    ((96, 76), (110, 94)),
                ],
                Direction.UP | Direction.LEFT: [
                    ((112, 28), (126, 46)),
                    ((112, 52), (126, 70)),
                    ((112, 76), (126, 94)),
                ],
            },
            'projectile': [
                pygame.image.load('images/projectile1.png').convert_alpha(),
                pygame.image.load('images/projectile2.png').convert_alpha(),
                pygame.image.load('images/projectile3.png').convert_alpha(),
            ],
            'wall': [
                pygame.image.load('images/wall1.png').convert(),
                pygame.image.load('images/wall2.png').convert(),
                pygame.image.load('images/wall3.png').convert(),
                pygame.image.load('images/wall4.png').convert(),
                pygame.image.load('images/wall5.png').convert(),
                pygame.image.load('images/wall6.png').convert(),
            ],
            'floor': [
                pygame.image.load('images/floor_theme_2/floor1.png').convert(),
                pygame.image.load('images/floor_theme_2/floor2.png').convert(),
                pygame.image.load('images/floor_theme_2/floor3.png').convert(),
                pygame.image.load('images/floor_theme_2/floor4.png').convert(),
                pygame.image.load('images/floor_theme_2/floor5.png').convert(),
                pygame.image.load('images/floor_theme_2/floor6.png').convert(),
            ],
        }
        self.input_system.subscribe(Control.CHARACTER_PANEL, self.toggle_character_panel)

    def toggle_character_panel(self, _) -> None:
        if not self.player:
            return
        self.player.show_character_panel = not self.player.show_character_panel

    def draw(self, area: Area):
        self.screen.fill((0, 0, 0))
        self.interactable_system.reset()
        if self.player is None:
            pygame.display.flip()
            return

        offset = self.input_system.get_offset(self.player)

        if area is not None:
            self.draw_area(area, offset)

            self.draw_players(area.players, offset)
            self.draw_projectiles(area.projectiles, offset)
            self.draw_enemies(area.enemies, offset)
            self.draw_loots(area.loots, offset)
            if area.exit:
                self.draw_exit(area.exit, offset)

        self.draw_character_panel()

        self.draw_cursor_loot()

        self.draw_fps()
        pygame.display.flip()

    def draw_players(self, players: list[Player], offset: tuple[int, int]):
        for player in players:
            velocity = player.get_preferred_velocity()
            if velocity.length() == 0:
                direction = player.last_direction
                frame = 1
            else:
                direction = Direction.from_velocity(velocity)
                player.last_direction = direction
                frame = (pygame.time.get_ticks() // 300) % 3

            sprite_sheet = self.draw_tiles['player']['sprite_sheet']
            top_left, bottom_right = self.draw_tiles['player'][direction][frame]
            width, height = bottom_right[0] - top_left[0], bottom_right[1] - top_left[1]

            image = sprite_sheet.subsurface(pygame.Rect(top_left[0], top_left[1], width, height))
            image = pygame.transform.scale(image, (50, 50))
            location = player.get_pixel_location()
            offset_location = (location[0] + offset[0], location[1] + offset[1])
            self._draw_interactable(image, offset_location, ScreenLayer.ABOVE_GROUND, player)

    def draw_projectiles(self, projectiles: list[Projectile], offset: tuple[int, int]):
        for projectile in projectiles:
            rand_int = random.randint(0, 2)
            image = self.draw_tiles['projectile'][rand_int]

            velocity = projectile.get_preferred_velocity()
            vx, vy = velocity.x, velocity.y
            angle = math.atan2(vy, vx) * 180 / math.pi - 90  # Images point up but 0 degrees is right
            rotated_image = pygame.transform.rotate(image, angle)

            location = projectile.get_pixel_location()
            offset_location = (location[0] + offset[0], location[1] + offset[1])
            self.screen.blit(rotated_image, offset_location)

    def draw_enemies(self, enemies: list[Enemy], offset: tuple[int, int]):
        for enemy in enemies:
            location = enemy.get_pixel_location()
            offset_location = (location[0] + offset[0], location[1] + offset[1])
            self._draw_interactable(enemy.image, offset_location, ScreenLayer.ABOVE_GROUND, enemy)

    def draw_loots(self, loots: list[Loot], offset: tuple[int, int]):
        for loot in loots:
            location = loot.get_pixel_location()
            offset_location = (location[0] + offset[0], location[1] + offset[1])
            self._draw_interactable(loot.image, offset_location, ScreenLayer.ON_GROUND, loot)

    def draw_exit(self, exit: ExitDoor, offset: tuple[int, int]):
        location = exit.get_pixel_location()
        offset_location = (location[0] + offset[0], location[1] + offset[1])
        self._draw_interactable(exit.image, offset_location, ScreenLayer.ON_GROUND, exit)

    def draw_area(self, area: Area, offset: tuple[int, int]):
        self.draw_floor(area, offset)
        self.draw_walls(area, offset)

    def draw_floor(self, area: Area, offset: tuple[int, int]):
        if not area.floor_surface:
            surface_width = area.map_grid_size * area.scale
            surface_height = area.map_grid_size * area.scale
            area.floor_surface = pygame.Surface((surface_width, surface_height), pygame.SRCALPHA)

            # Draw the tiles inside the playable area
            for i, row in enumerate(area.tiles):
                for j, tile in enumerate(row):
                    rand_int = random.randint(0, len(self.draw_tiles['floor']) - 1)
                    image = self.draw_tiles['floor'][rand_int]

                    # Rotate the image randomly
                    rand_int = random.randint(0, 3)
                    image = pygame.transform.rotate(image, 90 * rand_int)

                    darkness_level = random.randint(0, 0)
                    overlay = pygame.Surface((area.scale, area.scale), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, darkness_level))

                    area.floor_surface.blit(image, (i * area.scale, j * area.scale))
                    area.floor_surface.blit(overlay, (i * area.scale, j * area.scale))

            area.floor_surface = pygame.transform.box_blur(area.floor_surface, 30)
            area.floor_surface.fill((90, 90, 90), special_flags=pygame.BLEND_RGB_SUB)

        # Calculate the offset and draw the surface
        self.screen.blit(area.floor_surface, offset)

    def draw_walls(self, area: Area, offset: tuple[int, int]):
        if not area.wall_surface:
            # Surface size includes padding
            surface_width = (area.map_grid_size + 20) * area.scale
            surface_height = (area.map_grid_size + 20) * area.scale
            area.wall_surface = pygame.Surface((surface_width, surface_height), pygame.SRCALPHA)

            # Draw the tiles inside the playable area
            for i, row in enumerate(area.tiles):
                for j, tile in enumerate(row):
                    if tile == TileType.WALL:
                        rand_int = random.randint(0, len(self.draw_tiles['wall']) - 1)
                        image = self.draw_tiles['wall'][rand_int]
                        area.wall_surface.blit(image, ((i + 10) * area.scale, (j + 10) * area.scale))

            # Pad the area with 10 walls on all sides, progressively darker
            for i in range(-10, area.map_grid_size + 10):
                for j in range(-10, area.map_grid_size + 10):
                    # Only draw walls in the padding area
                    if i < 0 or i >= area.map_grid_size or j < 0 or j >= area.map_grid_size:
                        rand_int = random.randint(0, len(self.draw_tiles['wall']) - 1)
                        image = self.draw_tiles['wall'][rand_int]
                        padded_tile_position = ((i + 10) * area.scale, (j + 10) * area.scale)

                        # Rotate the image randomly
                        rand_int = random.randint(0, 3)
                        image = pygame.transform.rotate(image, 90 * rand_int)

                        # Calculate the distance from the edges of the original playable area
                        distance_from_original_x = max(0, 10 - (10 + i), i - area.map_grid_size + 1)
                        distance_from_original_y = max(0, 10 - (10 + j), j - area.map_grid_size + 1)
                        total_distance = max(distance_from_original_x, distance_from_original_y)

                        # Compute darkness level; the closer to the center, the less dark (brighter)
                        darkness_level = total_distance * (245 // 10)

                        # Add a little bit of randomness to the darkness level
                        darkness_level = darkness_level + random.randint(-30, 30)

                        darkness_level = pygame.math.clamp(darkness_level, 0, 255)

                        # Create a dark overlay
                        overlay = pygame.Surface((area.scale, area.scale), pygame.SRCALPHA)
                        overlay.fill((0, 0, 0, darkness_level))  # Fill with black and the calculated alpha

                        # Blit the wall image and then the overlay
                        area.wall_surface.blit(image, padded_tile_position)
                        area.wall_surface.blit(overlay, padded_tile_position)

        # Calculate the offset and draw the surface
        this_offset = (offset[0] - 10 * area.scale, offset[1] - 10 * area.scale)
        self.screen.blit(area.wall_surface, this_offset)

    def draw_fps(self):
        fps = self.clock.get_fps()
        font = pygame.font.SysFont('Arial', 16)
        text_to_show = font.render(str(int(fps)), False, (150, 150, 255))
        self.screen.blit(text_to_show, (0, 0))

    def draw_character_panel(self):
        if not self.player.show_character_panel:
            return

        screen_width, screen_height = self.screen.get_size()

        # Character panel
        panel_w = int(screen_width * 0.3)
        panel_h = screen_height
        panel_x = screen_width - panel_w
        panel_y = 0
        self._draw_rect_alpha((40, 40, 40, 230), (panel_x, panel_y, panel_w, panel_h))

        # Gear sub-panel
        common_pad_x = int(panel_w * 0.1)
        common_pad_y = int(panel_h * 0.05)
        common_inner_w = panel_w - (2 * common_pad_x)
        common_inner_x = panel_x + common_pad_x

        gear_sub_h = int(panel_h * 0.7)
        gear_inner_y = panel_y + common_pad_y
        gear_inner_h = gear_sub_h - (2 * common_pad_y)

        self._draw_rect_alpha((30, 30, 30, 200), (common_inner_x, gear_inner_y, common_inner_w, gear_inner_h))
        self.draw_character_gear(common_inner_w, gear_sub_h - common_pad_y, common_inner_x, gear_inner_y)

        # Inventory sub-panel
        inventory_sub_h = int(panel_h * 0.3)
        inventory_inner_h = inventory_sub_h - (2 * common_pad_y)
        inventory_inner_y = panel_y + panel_h - inventory_sub_h

        self._draw_rect_alpha((30, 30, 30, 200), (common_inner_x, inventory_inner_y, common_inner_w, inventory_inner_h))
        self.draw_character_inventory(common_inner_w, common_inner_x, inventory_inner_y)

    def draw_loot_slot(self, x: int, y: int, width: int, height: int) -> None:
        slot_color = (0, 0, 0, 180)
        self._draw_rect_alpha(slot_color, (x, y, width, height))

    def draw_character_gear(self, panel_width: int,  panel_height: int, panel_x: int, panel_y: int) -> None:
        cols = 6
        rows = 12
        gap = 2

        # Compute max square cell size that fits inside the panel, accounting for gaps
        cell_size_w = (panel_width - gap * (cols - 1)) // cols
        cell_size_h = (panel_height - gap * (rows - 1)) // rows
        cell_size = min(cell_size_w, cell_size_h)

        # Compute horizontal offset to center the grid
        total_grid_width = cell_size * cols + gap * (cols - 1)
        x_offset = panel_x + (panel_width - total_grid_width) // 2

        def cell_to_px(cell_col: int, cell_row: int) -> tuple[int, int]:
            # col, row are 1-based
            x = x_offset + (cell_col - 1) * (cell_size + gap)
            y = panel_y + (cell_row - 1) * (cell_size + gap)
            return x, y

        layout = {
            # slot: (x, y, cell width, cell height)
            GearSlot.CAPE: (1, 1, 2, 3),
            GearSlot.LANTERN: (5, 1, 1, 1),
            GearSlot.HEAD: (3, 1, 2, 2),
            GearSlot.NECKLACE: (5, 2, 1, 1),
            GearSlot.BODY: (3, 3, 2, 3),
            GearSlot.SHOULDER: (5, 3, 2, 1),
            GearSlot.MAIN_HAND: (1, 4, 2, 3),
            GearSlot.OFF_HAND: (5, 4, 2, 3),
            GearSlot.BELT: (3, 6, 2, 1),
            GearSlot.HANDS: (1, 7, 2, 2),
            GearSlot.POTION1: (5, 7, 1, 2),
            GearSlot.POTION2: (6, 7, 1, 2),
            GearSlot.LEGS: (3, 7, 2, 3),
            GearSlot.FINGER1: (1, 9, 1, 1),
            GearSlot.FINGER2: (2, 9, 1, 1),
            GearSlot.FINGER3: (1, 10, 1, 1),
            GearSlot.FINGER4: (2, 10, 1, 1),
            GearSlot.FINGER5: (5, 9, 1, 1),
            GearSlot.FINGER6: (6, 9, 1, 1),
            GearSlot.FINGER7: (5, 10, 1, 1),
            GearSlot.FINGER8: (6, 10, 1, 1),
            GearSlot.FEET: (3, 10, 2, 2),
            GearSlot.CHARM1: (1, 11, 1, 1),
            GearSlot.CHARM2: (2, 11, 1, 1),
            GearSlot.CHARM3: (5, 11, 1, 1),
            GearSlot.CHARM4: (6, 11, 1, 1),
        }

        for col, row, w, h in layout.values():
            lx, ly = cell_to_px(col, row)
            self.draw_loot_slot(
                lx,
                ly,
                cell_size * w + (w - 1) * gap,
                cell_size * h + (h - 1) * gap,
            )

    def draw_character_inventory(self, panel_width: int, panel_x: int, panel_y: int) -> None:
        gap = 3

        cols = max(1, self.player.inventory.width)
        space_for_cells = panel_width - gap * (cols - 1)
        cell_size = max(1, space_for_cells // cols)

        # Draw cells
        for row in range(self.player.inventory.height):
            for col in range(cols):
                cell_x = panel_x + col * (cell_size + gap)
                cell_y = panel_y + row * (cell_size + gap)
                rect = (cell_x, cell_y, cell_size, cell_size)

                self._draw_interactable_rect_alpha((0, 0, 0, 180), rect, ScreenLayer.UI, (self.player.inventory, col, row))

        for (col, row), loot in self.player.inventory.loot.items():
            cell_x = panel_x + col * (cell_size + gap)
            cell_y = panel_y + row * (cell_size + gap)

            loot_px_w = loot.inventory_width * cell_size + (loot.inventory_width - 1) * gap
            loot_px_h = loot.inventory_height * cell_size + (loot.inventory_height - 1) * gap

            scaled = pygame.transform.scale(
                loot.image,
                (loot_px_w, loot_px_h),
            )

            self._draw_interactable(scaled, (cell_x, cell_y), ScreenLayer.UI, loot)

    def draw_cursor_loot(self) -> None:
        """Draw the first loot from the player's cursor_loot container at the mouse cursor.
        This renders on top of the UI so the player sees the item they're holding.
        """
        if not self.player:
            return

        if self.player.cursor_loot.get_loot_count() == 0:
            return

        # Prefer the lookup by loot_dict (maps loot_id -> loot)
        loot = next(iter(self.player.cursor_loot.loot_dict.values()))
        if loot is None:
            return

        # Draw the loot image at the mouse position, centered. Scale to a reasonable UI size.
        mouse_x, mouse_y = pygame.mouse.get_pos()
        draw_size = 32
        scaled = pygame.transform.scale(loot.image, (draw_size, draw_size))

        rect = scaled.get_rect(center=(mouse_x, mouse_y))
        self.screen.blit(scaled, rect.topleft)

    def _draw_interactable(self, surface: Surface, location: tuple[int, int], layer: ScreenLayer, obj: object):
        interactable = Interactable(layer, surface.get_rect(topleft=location), obj)
        self.screen.blit(surface, interactable.hitbox)
        self.interactable_system.add_interactable(interactable)

    def _draw_rect_alpha(self,
                         argb: tuple[int, int, int, int],
                         rect: tuple[int, int, int, int]):
        shape_surf = Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
        pygame.draw.rect(shape_surf, argb, shape_surf.get_rect())
        self.screen.blit(shape_surf, rect)

    def _draw_interactable_rect_alpha(self,
                                      argb: tuple[int, int, int, int],
                                      rect: tuple[int, int, int, int],
                                      layer: ScreenLayer,
                                      obj: object):
        self._draw_rect_alpha(argb, rect)
        interactable = Interactable(layer, pygame.Rect(rect), obj)
        self.interactable_system.add_interactable(interactable)

