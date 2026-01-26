import pygame
import socket
import threading

from models.Direction import Direction
from models.Player import Player
from models.Settings import Settings, Control
from systems.AudioSystem import AudioSystem
from systems.ClientReceiverSystem import ClientReceiverSystem
from systems.DrawSystem import DrawSystem


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
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.draw_system = DrawSystem(self.clock, self.settings)
        self.audio_system = AudioSystem()

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
            if self.receiver.area:
                for player in self.receiver.area.players:
                    if self.receiver.client_id == player.client_id:
                        self.player = player
                        self.draw_system.player = player

            offset = self.get_offset()
            self.handle_events(offset)
            self.draw_system.draw(self.receiver.area, offset)
            self.audio_system.play()
            self.clock.tick(140)

        pygame.quit()
        self.server.close()

    def get_offset(self):
        if self.player:
            x, y = self.player.get_center()
            return int(round(self.settings.game_width / 2 - x)), int(round(self.settings.game_height / 2 - y))

        return 0, 0

    def handle_events(self, offset: tuple[int, int]):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                is_mouse = event.type == pygame.MOUSEBUTTONDOWN
                key = event.button if is_mouse else event.key
                if self.settings.is_hotkey(key, Control.MOVE_UP, is_mouse):
                    self.server.sendall(f'move:{Direction.UP.value}\n'.encode())
                elif self.settings.is_hotkey(key, Control.MOVE_DOWN, is_mouse):
                    self.server.sendall(f'move:{Direction.DOWN.value}\n'.encode())
                elif self.settings.is_hotkey(key, Control.MOVE_LEFT, is_mouse):
                    self.server.sendall(f'move:{Direction.LEFT.value}\n'.encode())
                elif self.settings.is_hotkey(key, Control.MOVE_RIGHT, is_mouse):
                    self.server.sendall(f'move:{Direction.RIGHT.value}\n'.encode())
                elif self.settings.is_hotkey(key, Control.INVENTORY, is_mouse):
                    if self.player:
                        self.player.show_inventory = not self.player.show_inventory
                elif self.settings.is_hotkey(key, Control.SKILL1, is_mouse):
                    self.attacking = True
                    self.attack(offset)

            elif event.type == pygame.KEYUP or event.type == pygame.MOUSEBUTTONUP:
                is_mouse = event.type == pygame.MOUSEBUTTONUP
                key = event.button if is_mouse else event.key
                if self.settings.is_hotkey(key, Control.MOVE_UP, is_mouse):
                    self.server.sendall(f'stop:{Direction.UP.value}\n'.encode())
                elif self.settings.is_hotkey(key, Control.MOVE_DOWN, is_mouse):
                    self.server.sendall(f'stop:{Direction.DOWN.value}\n'.encode())
                elif self.settings.is_hotkey(key, Control.MOVE_LEFT, is_mouse):
                    self.server.sendall(f'stop:{Direction.LEFT.value}\n'.encode())
                elif self.settings.is_hotkey(key, Control.MOVE_RIGHT, is_mouse):
                    self.server.sendall(f'stop:{Direction.RIGHT.value}\n'.encode())
                elif self.settings.is_hotkey(key, Control.SKILL1, is_mouse):
                    self.attacking = False
                    self.server.sendall('attack_stop\n'.encode())

            elif event.type == pygame.MOUSEMOTION:
                if self.attacking:
                    self.attack(offset)

    def attack(self, offset):
        if not self.player:
            return
        angle, magnitude = self.settings.vector_to_cursor(self.player, offset)
        self.server.sendall(f'attack:{angle},{magnitude}\n'.encode())


if __name__ == '__main__':
    GameClient().run()
