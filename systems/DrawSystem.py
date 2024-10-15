import math
import random

import pygame

from models.Area import Area
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
                pygame.image.load('images/projectile3.png').convert_alpha()
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
            # 'exit': pygame.image.load('images/exit.png').convert()
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

            self.screen.blit(area.surface, offset)

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

    def draw_fps(self):
        fps = self.clock.get_fps()
        font = pygame.font.SysFont('Arial', 16)
        text_to_show = font.render(str(int(fps)), False, (150, 150, 255))
        self.screen.blit(text_to_show, (0, 0))
