import pygame
import socket
import threading

from models.Client import Client
from systems.AreaSystem import AreaSystem
from systems.DamageSystem import DamageSystem
from systems.LootSystem import LootSystem
from systems.ServerBroadcastSystem import ServerBroadcastSystem
from systems.MovementSystem import MovementSystem
from systems.ServerReceiverSystem import ServerReceiverSystem
from systems.SkillSystem import SkillSystem


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
        self.loot_system = LootSystem(self.area_system)
        self.movement_system = MovementSystem(self.area_system)
        self.skill_system = SkillSystem(self.area_system)
        self.damage_system = DamageSystem(self.area_system, self.loot_system)
        self.broadcaster = ServerBroadcastSystem(self.clients, self.area_system)
        self.receiver = ServerReceiverSystem(self.clients, self.movement_system, self.skill_system)

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
            if client.player:
                client.player.kill()
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

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            clients = list(self.clients.values())

            self.area_system.run_once(clients)
            self.movement_system.move()
            self.skill_system.use_skills()
            self.damage_system.apply_damage()
            self.loot_system.check_collisions()
            self.broadcaster.send_updates()

            clock.tick(60)

        pygame.quit()


if __name__ == '__main__':
    GameServer().run()
