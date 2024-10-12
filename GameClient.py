import pygame
import socket
import threading

from models.Direction import Direction
from models.Entity import Entity
from models.Player import Player
from models.Settings import Settings, Controls
from systems.ClientReceiverSystem import ClientReceiverSystem


class GameClient:
    def __init__(self):
        pygame.init()
        self.host = '127.0.0.1'
        self.port = 8888
        self.running = False
        self.attacking = False
        self.player: Player | None = None
        self.clock = pygame.time.Clock()

        self.settings = Settings()
        self.screen = pygame.display.set_mode((self.settings.game_width, self.settings.game_height))
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.receiver = ClientReceiverSystem(self.server)

    def run(self):
        self.running = True
        threading.Thread(target=self.client_thread, args=(), daemon=True).start()
        self.game_thread()

    def client_thread(self):
        self.server.connect((self.host, self.port))
        print('Connected to server.')
        self.server.sendall('connect\n'.encode())
        try:
            while self.running:
                self.receiver.receive_updates()
        except ConnectionResetError as e:
            print(e)
        finally:
            self.server.close()

    def game_thread(self):
        pygame.display.set_caption('Client')

        while self.running:
            self.screen.fill((0, 0, 0))

            offset = (0, 0)
            if self.receiver.area:
                for player in self.receiver.area.players:
                    if self.receiver.client_id == player.client_id:
                        self.player = player
                        x, y = self.player.get_center()
                        offset = (int(round(self.settings.game_width / 2 - x)), int(round(self.settings.game_height / 2 - y)))
                        break

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.KEYDOWN:
                    if self.settings.is_hotkey(event.key, Controls.MOVE_UP):
                        self.server.sendall(f'move:{Direction.UP.value}\n'.encode())
                    elif self.settings.is_hotkey(event.key, Controls.MOVE_DOWN):
                        self.server.sendall(f'move:{Direction.DOWN.value}\n'.encode())
                    elif self.settings.is_hotkey(event.key, Controls.MOVE_LEFT):
                        self.server.sendall(f'move:{Direction.LEFT.value}\n'.encode())
                    elif self.settings.is_hotkey(event.key, Controls.MOVE_RIGHT):
                        self.server.sendall(f'move:{Direction.RIGHT.value}\n'.encode())
                    elif self.settings.is_hotkey(event.key, Controls.SKILL1):
                        self.attack(offset)

                elif event.type == pygame.KEYUP:
                    if self.settings.is_hotkey(event.key, Controls.MOVE_UP):
                        self.server.sendall(f'stop:{Direction.UP.value}\n'.encode())
                    elif self.settings.is_hotkey(event.key, Controls.MOVE_DOWN):
                        self.server.sendall(f'stop:{Direction.DOWN.value}\n'.encode())
                    elif self.settings.is_hotkey(event.key, Controls.MOVE_LEFT):
                        self.server.sendall(f'stop:{Direction.LEFT.value}\n'.encode())
                    elif self.settings.is_hotkey(event.key, Controls.MOVE_RIGHT):
                        self.server.sendall(f'stop:{Direction.RIGHT.value}\n'.encode())
                    elif self.settings.is_hotkey(event.key, Controls.SKILL1):
                        self.attacking = False
                        self.server.sendall('attack_stop\n'.encode())

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.settings.is_mouse_hotkey(event.button, Controls.MOVE_UP):
                        self.server.sendall(f'move:{Direction.UP.value}\n'.encode())
                    elif self.settings.is_mouse_hotkey(event.button, Controls.MOVE_DOWN):
                        self.server.sendall(f'move:{Direction.DOWN.value}\n'.encode())
                    elif self.settings.is_mouse_hotkey(event.button, Controls.MOVE_LEFT):
                        self.server.sendall(f'move:{Direction.LEFT.value}\n'.encode())
                    elif self.settings.is_mouse_hotkey(event.button, Controls.MOVE_RIGHT):
                        self.server.sendall(f'move:{Direction.RIGHT.value}\n'.encode())
                    elif self.settings.is_mouse_hotkey(event.button, Controls.SKILL1):
                        self.attack(offset)

                elif event.type == pygame.MOUSEBUTTONUP:
                    if self.settings.is_mouse_hotkey(event.button, Controls.MOVE_UP):
                        self.server.sendall(f'stop:{Direction.UP.value}\n'.encode())
                    elif self.settings.is_mouse_hotkey(event.button, Controls.MOVE_DOWN):
                        self.server.sendall(f'stop:{Direction.DOWN.value}\n'.encode())
                    elif self.settings.is_mouse_hotkey(event.button, Controls.MOVE_LEFT):
                        self.server.sendall(f'stop:{Direction.LEFT.value}\n'.encode())
                    elif self.settings.is_mouse_hotkey(event.button, Controls.MOVE_RIGHT):
                        self.server.sendall(f'stop:{Direction.RIGHT.value}\n'.encode())
                    elif self.settings.is_mouse_hotkey(event.button, Controls.SKILL1):
                        self.attacking = False
                        self.server.sendall('attack_stop\n'.encode())

                elif event.type == pygame.MOUSEMOTION:
                    if self.attacking:
                        angle, magnitude = self.settings.vector_to_cursor(self.player, offset)
                        self.server.sendall(f'attack:{angle},{magnitude}\n'.encode())

            if self.receiver.area:
                for player in self.receiver.area.players:
                    entity_location = player.get_pixel_location()
                    self.screen.blit(player.image, (entity_location[0] + offset[0], entity_location[1] + offset[1]))

                for projectile in self.receiver.area.projectiles:
                    entity_location = projectile.get_pixel_location()
                    self.screen.blit(projectile.image, (entity_location[0] + offset[0], entity_location[1] + offset[1]))

                for enemy in self.receiver.area.enemies:
                    entity_location = enemy.get_pixel_location()
                    self.screen.blit(enemy.image, (entity_location[0] + offset[0], entity_location[1] + offset[1]))

                for loot in self.receiver.area.loots:
                    entity_location = loot.get_pixel_location()
                    self.screen.blit(loot.image, (entity_location[0] + offset[0], entity_location[1] + offset[1]))

                if self.receiver.area.exit:
                    entity_location = self.receiver.area.exit.get_pixel_location()
                    self.screen.blit(self.receiver.area.exit.image, (entity_location[0] + offset[0], entity_location[1] + offset[1]))

                self.screen.blit(self.receiver.area.surface, offset)

            self.update_fps()

            pygame.display.flip()
            self.clock.tick(140)

        pygame.quit()
        self.server.close()

    def attack(self, offset):
        if not self.player:
            return
        self.attacking = True
        angle, magnitude = self.settings.vector_to_cursor(self.player, offset)
        self.server.sendall(f'attack:{angle},{magnitude}\n'.encode())

    def update_fps(self):
        fps = self.clock.get_fps()
        font = pygame.font.SysFont('Arial', 16)
        text_to_show = font.render(str(int(fps)), False, (150, 150, 255))
        self.screen.blit(text_to_show, (0, 0))


if __name__ == '__main__':
    GameClient().run()
