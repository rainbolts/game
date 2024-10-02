import pygame
import socket
import threading

from models.Player import Player
from models.Settings import Settings, Controls
from systems.ClientReceiverSystem import ClientReceiverSystem
from systems.MovementSystem import Direction


class GameClient:
    def __init__(self):
        pygame.init()
        self.host = '127.0.0.1'
        self.port = 8888
        self.running = False
        self.settings = Settings()
        self.players: dict[str, Player] = {}
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.client_receiver_system = ClientReceiverSystem(self.connection, self.players)

    def run(self):
        self.running = True
        threading.Thread(target=self.client_thread, args=(), daemon=True).start()
        self.game_thread()

    def client_thread(self):
        self.connection.connect((self.host, self.port))
        print('Connected to server.')
        self.connection.sendall('connect\n'.encode())
        try:
            while self.running:
                self.client_receiver_system.receive_updates()
        except ConnectionResetError as e:
            print(e)
        finally:
            self.connection.close()

    def game_thread(self):
        screen = pygame.display.set_mode((640, 480))
        pygame.display.set_caption('Client')

        clock = pygame.time.Clock()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.KEYDOWN:
                    if self.settings.is_hotkey(event.key, Controls.MOVE_UP):
                        self.connection.sendall(f'move:{Direction.UP.value}\n'.encode())
                    elif self.settings.is_hotkey(event.key, Controls.MOVE_DOWN):
                        self.connection.sendall(f'move:{Direction.DOWN.value}\n'.encode())
                    elif self.settings.is_hotkey(event.key, Controls.MOVE_LEFT):
                        self.connection.sendall(f'move:{Direction.LEFT.value}\n'.encode())
                    elif self.settings.is_hotkey(event.key, Controls.MOVE_RIGHT):
                        self.connection.sendall(f'move:{Direction.RIGHT.value}\n'.encode())

                elif event.type == pygame.KEYUP:
                    if self.settings.is_hotkey(event.key, Controls.MOVE_UP):
                        self.connection.sendall(f'stop:{Direction.UP.value}\n'.encode())
                    elif self.settings.is_hotkey(event.key, Controls.MOVE_DOWN):
                        self.connection.sendall(f'stop:{Direction.DOWN.value}\n'.encode())
                    elif self.settings.is_hotkey(event.key, Controls.MOVE_LEFT):
                        self.connection.sendall(f'stop:{Direction.LEFT.value}\n'.encode())
                    elif self.settings.is_hotkey(event.key, Controls.MOVE_RIGHT):
                        self.connection.sendall(f'stop:{Direction.RIGHT.value}\n'.encode())

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.settings.is_mouse_hotkey(event.button, Controls.MOVE_UP):
                        self.connection.sendall(f'move:{Direction.UP.value}\n'.encode())
                    elif self.settings.is_mouse_hotkey(event.button, Controls.MOVE_DOWN):
                        self.connection.sendall(f'move:{Direction.DOWN.value}\n'.encode())
                    elif self.settings.is_mouse_hotkey(event.button, Controls.MOVE_LEFT):
                        self.connection.sendall(f'move:{Direction.LEFT.value}\n'.encode())
                    elif self.settings.is_mouse_hotkey(event.button, Controls.MOVE_RIGHT):
                        self.connection.sendall(f'move:{Direction.RIGHT.value}\n'.encode())

            screen.fill((0, 0, 0))

            for client_id, player in self.players.items():
                if client_id == self.client_receiver_system.client_id:
                    player_color = (0, 255, 0)
                else:
                    player_color = (255, 0, 0)
                pygame.draw.rect(screen, player_color, (player.position[0], player.position[1], 50, 50))

            pygame.display.flip()
            clock.tick(140)

        pygame.quit()
        self.connection.close()


if __name__ == '__main__':
    GameClient().run()
