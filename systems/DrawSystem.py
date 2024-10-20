import math
import random

import pygame

from models.Area import Area, TileType
from models.Direction import Direction
from models.Enemy import Enemy
from models.ExitDoor import ExitDoor
from models.Loot import LootType, Loot
from models.Player import Player
from models.Projectile import Projectile
from models.Settings import Settings


class DrawSystem:
    def __init__(self, clock: pygame.time.Clock, settings: Settings):
        self.screen = pygame.display.set_mode((settings.game_width, settings.game_height))
        self.clock = clock
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
            # 'enemy': {
            #     'up': [pygame.image.load('images/enemy_up1.png').convert()],
            #     'down': [pygame.image.load('images/enemy_down1.png').convert()],
            #     'left': [pygame.image.load('images/enemy_left1.png').convert()],
            #     # right is left but mirrored
            # },
            # 'loot': {
            #     'floor': {
            #         LootType.RING: pygame.image.load('images/ring_floor.png').convert(),
            #     },
            #     'inventory': {
            #         LootType.RING: pygame.image.load('images/ring_inventory.png').convert(),
            #     }
            # },
            # 'exit': pygame.image.load('images/exit.png').convert(),
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

    def draw(self, area: Area, offset: tuple[int, int]):
        self.screen.fill((0, 0, 0))

        if area is not None:
            self.draw_area(area, offset)

            self.draw_players(area.players, offset)
            self.draw_projectiles(area.projectiles, offset)
            self.draw_enemies(area.enemies, offset)
            self.draw_loots(area.loots, offset)
            if area.exit:
                self.draw_exit(area.exit, offset)

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
            entity_location = player.get_pixel_location()
            self.screen.blit(image, (entity_location[0] + offset[0], entity_location[1] + offset[1]))

    def draw_projectiles(self, projectiles: list[Projectile], offset: tuple[int, int]):
        for projectile in projectiles:
            rand_int = random.randint(0, 2)
            image = self.draw_tiles['projectile'][rand_int]

            velocity = projectile.get_preferred_velocity()
            vx, vy = velocity.x, velocity.y
            angle = math.atan2(vy, vx) * 180 / math.pi - 90  # Images point up but 0 degrees is right
            rotated_image = pygame.transform.rotate(image, angle)

            entity_location = projectile.get_pixel_location()

            self.screen.blit(rotated_image, (entity_location[0] + offset[0], entity_location[1] + offset[1]))

    def draw_enemies(self, enemies: list[Enemy], offset: tuple[int, int]):
        for enemy in enemies:
            entity_location = enemy.get_pixel_location()
            self.screen.blit(enemy.image, (entity_location[0] + offset[0], entity_location[1] + offset[1]))

    def draw_loots(self, loots: list[Loot], offset: tuple[int, int]):
        for loot in loots:
            entity_location = loot.get_pixel_location()
            self.screen.blit(loot.image, (entity_location[0] + offset[0], entity_location[1] + offset[1]))

    def draw_exit(self, exit: ExitDoor, offset: tuple[int, int]):
        entity_location = exit.get_pixel_location()
        self.screen.blit(exit.image, (entity_location[0] + offset[0], entity_location[1] + offset[1]))

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

                    darkness_level = random.randint(0, 40)
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
