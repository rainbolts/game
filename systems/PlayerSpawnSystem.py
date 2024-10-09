from collections.abc import Iterable

from models.Client import Client
from models.Player import Player
from systems.AreaSystem import AreaSystem


class PlayerSpawnSystem:
    def __init__(self, area_system: AreaSystem):
        self.area_system = area_system

    def spawn_players(self, clients: Iterable[Client]):
        area = self.area_system.current_area
        if area is None:
            return

        for client in clients:
            if client.player is None:
                spawn = area.get_spawn()
                client.player = Player(client.client_id, spawn)
