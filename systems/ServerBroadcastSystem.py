import json
from socket import socket

from models.Client import Client
from systems import AreaSystem


class ServerBroadcastSystem:
    def __init__(self, clients: dict[socket, Client], area_system: AreaSystem):
        self.clients = clients
        self.area_system = area_system
        self.prev_state = {}

    def send_updates(self):
        player_positions = [{
            'id': id(connection),
            'x': client.player.rect.x,
            'y': client.player.rect.y
        } for connection, client in self.clients.items()]

        current_state = {
            'area_seed': self.area_system.current_area.seed,
            'player_positions': player_positions
        }

        if current_state == self.prev_state:
            return

        update_frame = (json.dumps(current_state) + '\n').encode()
        self.prev_state = current_state

        for client in self.clients:
            client.sendall(update_frame)
