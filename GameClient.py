import pygame
import socket
import threading

from pygame import Surface

from models.Direction import Direction
from models.Entity import Entity
from models.Player import Player
from models.Settings import Settings, Controls
from systems.AreaSystem import AreaSystem
from systems.ClientReceiverSystem import ClientReceiverSystem


class GameClient:
    def __init__(self):
        pygame.init()
        self.host = '127.0.0.1'
        self.port = 8888
        self.running = False
        self.players: dict[str, Player] = {}
        self.clock = pygame.time.Clock()

        self.settings = Settings()
        self.screen = pygame.display.set_mode((self.settings.game_width, self.settings.game_height))
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.area_system = AreaSystem()
        self.receiver = ClientReceiverSystem(self.server, self.players, self.area_system)

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

                elif event.type == pygame.KEYUP:
                    if self.settings.is_hotkey(event.key, Controls.MOVE_UP):
                        self.server.sendall(f'stop:{Direction.UP.value}\n'.encode())
                    elif self.settings.is_hotkey(event.key, Controls.MOVE_DOWN):
                        self.server.sendall(f'stop:{Direction.DOWN.value}\n'.encode())
                    elif self.settings.is_hotkey(event.key, Controls.MOVE_LEFT):
                        self.server.sendall(f'stop:{Direction.LEFT.value}\n'.encode())
                    elif self.settings.is_hotkey(event.key, Controls.MOVE_RIGHT):
                        self.server.sendall(f'stop:{Direction.RIGHT.value}\n'.encode())

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.settings.is_mouse_hotkey(event.button, Controls.MOVE_UP):
                        self.server.sendall(f'move:{Direction.UP.value}\n'.encode())
                    elif self.settings.is_mouse_hotkey(event.button, Controls.MOVE_DOWN):
                        self.server.sendall(f'move:{Direction.DOWN.value}\n'.encode())
                    elif self.settings.is_mouse_hotkey(event.button, Controls.MOVE_LEFT):
                        self.server.sendall(f'move:{Direction.LEFT.value}\n'.encode())
                    elif self.settings.is_mouse_hotkey(event.button, Controls.MOVE_RIGHT):
                        self.server.sendall(f'move:{Direction.RIGHT.value}\n'.encode())

            if self.receiver.client_id in self.players:
                x, y = self.players[self.receiver.client_id].rect.x, self.players[self.receiver.client_id].rect.y
                offset = (self.settings.game_width / 2 - x, self.settings.game_height / 2 - y)
            else:
                offset = (0, 0)

            for entity in Entity.entity_group:
                self.screen.blit(entity.image, (entity.rect.x + offset[0], entity.rect.y + offset[1]))

            if self.area_system.current_area:
                area_surface = self.area_system.current_area.surface
                self.screen.blit(area_surface, offset)

            self.update_fps()

            pygame.display.flip()
            self.clock.tick(140)

        pygame.quit()
        self.server.close()

    def update_fps(self):
        fps = self.clock.get_fps()
        font = pygame.font.SysFont('Arial', 16)
        text_to_show = font.render(str(int(fps)), False, (150, 150, 255))
        self.screen.blit(text_to_show, (0, 0))


if __name__ == '__main__':
    GameClient().run()
