import json
from socket import socket

from models.Client import Client
from models.Entity import Entity
from systems import AreaSystem


class ServerBroadcastSystem:
    def __init__(self, clients: dict[socket, Client], area_system: AreaSystem):
        self.clients = clients
        self.area_system = area_system
        self.prev_state = {}

    def send_updates(self):
        entities = [x.to_broadcast() for x in Entity.entity_group]
        current_state = {
            'area_seed': self.area_system.current_area.seed,
            'entities': entities
        }

        if current_state == self.prev_state:
            return

        update_frame = (json.dumps(current_state) + '\n').encode()
        self.prev_state = current_state

        for client in self.clients:
            client.sendall(update_frame)
