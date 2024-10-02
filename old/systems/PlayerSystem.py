from models import Settings
from models.Player import Player
from systems.NetCode import NetCodeServer


class PlayerSystem:
    def __init__(self, settings: Settings, server: NetCodeServer):
        self.settings = settings
        self.server = server
        self.players = {}

    def spawn_players(self):
        for client in self.server.clients:
            if client not in self.players:
                spawn_x = 400
                spawn_y = 400
                player = Player((spawn_x, spawn_y), self.settings)
                self.players[client] = player
                self.server.broadcast(f'spawn:{spawn_x},{spawn_y}', client)