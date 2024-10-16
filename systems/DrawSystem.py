import math
import random

import pygame

from models.Area import Area, TileType
from models.Entity import Entity
from models.Loot import LootType
from models.Settings import Settings


class DrawSystem:
    def __init__(self, clock: pygame.time.Clock, settings: Settings):
        self.screen = pygame.display.set_mode((settings.game_width, settings.game_height))
        self.clock = clock
        self.draw_tiles = {
            # 'player': {
            #     'up': [pygame.image.load('images/player_up1.png').convert()],
            #     'down': [pygame.image.load('images/player_down1.png').convert()],
            #     'left': [pygame.image.load('images/player_left1.png').convert()],
            #     # right is left but mirrored
            # },
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
        }

    def draw(self, area: Area, offset: tuple[int, int]):
        self.screen.fill((0, 0, 0))

        if area is not None:
            self.draw_players(area.players, offset)
            self.draw_projectiles(area.projectiles, offset)
            self.draw_enemies(area.enemies, offset)
            self.draw_loots(area.loots, offset)
            if area.exit:
                self.draw_exit(area.exit, offset)

            self.draw_area(area, offset)

        self.draw_fps()
        pygame.display.flip()

    def draw_players(self, players: list[Entity], offset: tuple[int, int]):
        for player in players:
            entity_location = player.get_pixel_location()
            self.screen.blit(player.image, (entity_location[0] + offset[0], entity_location[1] + offset[1]))

    def draw_projectiles(self, projectiles: list[Entity], offset: tuple[int, int]):
        for projectile in projectiles:
            rand_int = random.randint(0, 2)
            image = self.draw_tiles['projectile'][rand_int]

            velocity = projectile.get_preferred_velocity()
            vx, vy = velocity.x, velocity.y
            angle = math.atan2(vy, vx) * 180 / math.pi - 90  # Images point up but 0 degrees is right
            rotated_image = pygame.transform.rotate(image, angle)

            entity_location = projectile.get_pixel_location()

            self.screen.blit(rotated_image, (entity_location[0] + offset[0], entity_location[1] + offset[1]))

    def draw_enemies(self, enemies: list[Entity], offset: tuple[int, int]):
        for enemy in enemies:
            entity_location = enemy.get_pixel_location()
            self.screen.blit(enemy.image, (entity_location[0] + offset[0], entity_location[1] + offset[1]))

    def draw_loots(self, loots: list[Entity], offset: tuple[int, int]):
        for loot in loots:
            entity_location = loot.get_pixel_location()
            self.screen.blit(loot.image, (entity_location[0] + offset[0], entity_location[1] + offset[1]))

    def draw_exit(self, exit: Entity, offset: tuple[int, int]):
        entity_location = exit.get_pixel_location()
        self.screen.blit(exit.image, (entity_location[0] + offset[0], entity_location[1] + offset[1]))

    def draw_area(self, area: Area, offset: tuple[int, int]):
        if not area.surface:
            # Calculate number of tiles from the length of the tile list
            num_tiles_x = len(area.tiles)
            num_tiles_y = len(area.tiles[0]) if area.tiles else 0

            # Surface size includes padding
            surface_width = (num_tiles_x + 20) * area.scale
            surface_height = (num_tiles_y + 20) * area.scale
            area.surface = pygame.Surface((surface_width, surface_height), pygame.SRCALPHA)

            # Draw the tiles inside the playable area
            for i, row in enumerate(area.tiles):
                for j, tile in enumerate(row):
                    if tile == TileType.WALL:
                        rand_int = random.randint(0, len(self.draw_tiles['wall']) - 1)
                        image = self.draw_tiles['wall'][rand_int]
                        area.surface.blit(image, ((i + 10) * area.scale, (j + 10) * area.scale))

            # Pad the area with 10 walls on all sides, progressively darker
            for i in range(-10, num_tiles_x + 10):
                for j in range(-10, num_tiles_y + 10):
                    # Only draw walls in the padding area
                    if i < 0 or i >= num_tiles_x or j < 0 or j >= num_tiles_y:
                        rand_int = random.randint(0, len(self.draw_tiles['wall']) - 1)
                        image = self.draw_tiles['wall'][rand_int]
                        padded_tile_position = ((i + 10) * area.scale, (j + 10) * area.scale)

                        # Calculate the distance from the edges of the original playable area
                        distance_from_original_x = max(0, 10 - (10 + i), i - num_tiles_x + 1)
                        distance_from_original_y = max(0, 10 - (10 + j), j - num_tiles_y + 1)
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
                        area.surface.blit(image, padded_tile_position)
                        area.surface.blit(overlay, padded_tile_position)

        # Calculate the offset and draw the surface
        this_offset = (offset[0] - 10 * area.scale, offset[1] - 10 * area.scale)
        self.screen.blit(area.surface, this_offset)

    def draw_fps(self):
        fps = self.clock.get_fps()
        font = pygame.font.SysFont('Arial', 16)
        text_to_show = font.render(str(int(fps)), False, (150, 150, 255))
        self.screen.blit(text_to_show, (0, 0))
