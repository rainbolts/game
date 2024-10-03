import pygame
import socket
import threading

from models.Client import Client
from systems.AreaSystem import AreaSystem
from systems.ServerBroadcastSystem import ServerBroadcastSystem
from systems.MovementSystem import MovementSystem
from systems.ServerReceiverSystem import ServerReceiverSystem


class GameServer:
    """
    Manager of all server side systems and threads. The entry point for the game server.
    """

    def __init__(self):
        pygame.init()

        self.host = '127.0.0.1'
        self.port = 8888
        self.running = False
        self.clients: dict[socket, Client] = {}

        self.area_system = AreaSystem()
        self.movement_system = MovementSystem()
        self.broadcaster = ServerBroadcastSystem(self.clients, self.area_system)
        self.receiver = ServerReceiverSystem(self.clients, self.movement_system)

    def run(self):
        self.running = True
        threading.Thread(target=self.server_thread, daemon=True).start()
        self.game_thread()

    def client_thread(self, connection: socket, address: str) -> None:
        """
        Listens for client updates until the client disconnects.
        """
        print(f'Client {address} connected.')

        client = Client(connection)
        self.clients[connection] = client

        try:
            while self.running:
                self.receiver.receive_updates(client, address)
        except ConnectionResetError as e:
            print(e)
        finally:
            del self.clients[connection]
            connection.close()

    def server_thread(self) -> None:
        """
        Listens for new clients until the server is stopped.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()

            print(f'Server running on {self.host}:{self.port}')
            while self.running:
                connection, address = s.accept()
                threading.Thread(target=self.client_thread, args=(connection, address)).start()

    def game_thread(self) -> None:
        """
        Runs the game loop until the game is closed.
        """
        pygame.display.set_caption('Server')
        clock = pygame.time.Clock()
        self.running = True

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.area_system.generate_area()
            self.movement_system.move(self.area_system.current_area)
            self.broadcaster.send_updates()
            clock.tick(60)

        pygame.quit()


if __name__ == '__main__':
    GameServer().run()
