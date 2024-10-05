import random
from socket import socket

from pygame import Vector2

from models.Client import Client
from models.Direction import Direction
from models.Player import Player
from systems.MovementSystem import MovementSystem
from systems.SkillSystem import SkillSystem


class ServerReceiverSystem:
    def __init__(self,
                 clients: dict[socket, Client],
                 movement_system: MovementSystem,
                 skill_system: SkillSystem):
        self.clients = clients
        self.movement_system = movement_system
        self.skill_system = skill_system
        self.client_buffer: dict[Client, str] = {}

    def receive_updates(self, client: Client, address: str):
        if client not in self.client_buffer:
            self.client_buffer[client] = ''
        client_buffer = self.client_buffer[client]

        data = client.connection.recv(1024)
        if not data:
            raise ConnectionResetError(f'Client {address} disconnected.')
        client_buffer += data.decode()

        # Process all complete messages in the buffer
        while '\n' in client_buffer:
            message, client_buffer = client_buffer.split('\n', 1)

            if message == 'connect':
                self.spawn_player(client.connection)
                client.connection.sendall(f'connect:{id(client.connection)}\n'.encode())

            elif message.startswith('move:'):
                direction = Direction(int(message.split(':')[1]))
                self.movement_system.start_moving(client.player, direction)

            elif message.startswith('stop:'):
                direction = Direction(int(message.split(':')[1]))
                self.movement_system.stop_moving(client.player, direction)

            elif message.startswith('attack:'):
                angle, magnitude = message.split(':')[1].split(',')
                destination_vector = Vector2()
                destination_vector.from_polar((float(magnitude), float(angle)))
                self.skill_system.start_attacking(client.player, destination_vector)

            elif message.startswith('attack_stop'):
                self.skill_system.stop_attacking(client.player)

    def spawn_player(self, connection):
        x = random.randint(400, 600)
        y = random.randint(400, 600)
        client = self.clients[connection]
        client.player = Player((x, y))
