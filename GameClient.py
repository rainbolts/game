import socket
import threading

import pygame

from models.Player import Player
from systems.AudioSystem import AudioSystem
from systems.ClientReceiverSystem import ClientReceiverSystem
from systems.DrawSystem import DrawSystem
from systems.InputSystem import InputSystem, Control


class GameClient:
    def __init__(self):
        pygame.init()
        self.host = '127.0.0.1'
        self.port = 8888
        self.running = False
        self.attacking = False
        self.player: Player | None = None
        self.clock = pygame.time.Clock()

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.input_system = InputSystem(self.server)
        self.draw_system = DrawSystem(self.clock, self.input_system)
        self.audio_system = AudioSystem()
        self.receiver = ClientReceiverSystem(self.server)

        self.input_system.subscribe(Control.QUIT, self.stop)

    def run(self):
        self.running = True
        threading.Thread(target=self.client_thread, args=(), daemon=True).start()
        self.game_thread()

    def stop(self):
        self.running = False

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
                        self.input_system.player = player
                        self.draw_system.player = player

            self.input_system.handle_events()
            self.draw_system.draw(self.receiver.area)
            self.audio_system.play()
            self.clock.tick(140)

        pygame.quit()
        self.server.close()


if __name__ == '__main__':
    GameClient().run()
