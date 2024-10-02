import json
from socket import socket

from models.Client import Client


class ServerBroadcastSystem:
    def __init__(self, clients: dict[socket, Client]):
        self.clients = clients

    def send_updates(self):
        player_positions = [{
            'id': id(connection),
            'x': client.player.position[0],
            'y': client.player.position[1]
        } for connection, client in self.clients.items()]

        update = {
            'player_positions': player_positions
        }
        update_frame = (json.dumps(update) + '\n').encode()

        for client in self.clients:
            client.sendall(update_frame)
