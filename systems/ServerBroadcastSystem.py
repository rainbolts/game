import json
from socket import socket

from models.Client import Client
from systems.AreaSystem import AreaSystem


class ServerBroadcastSystem:
    def __init__(self, clients: dict[socket, Client], area_system: AreaSystem):
        self.clients = clients
        self.area_system = area_system
        self.prev_update: dict[Client, dict] = {}

    def send_updates(self):
        player_area = {player: area for area in self.area_system.areas for player in area.players}
        area_broadcast_dict = {area: area.to_broadcast() for area in self.area_system.areas}
        for client in self.clients.values():
            if client.player not in player_area:
                continue

            area = player_area[client.player]
            update = area_broadcast_dict[area]

            if client in self.prev_update and update == self.prev_update[client]:
                continue
            self.prev_update[client] = update

            update_frame = (json.dumps(update) + '\n').encode()
            client.connection.sendall(update_frame)
