import json
from socket import socket

from models.Enemy import Enemy
from models.Player import Player
from models.Projectile import Projectile
from systems.AreaSystem import AreaSystem


class ClientReceiverSystem:
    def __init__(self,
                 server: socket,
                 players: dict[str, Player],
                 area_system: AreaSystem):
        self.server = server
        self.players = players
        self.area_system = area_system
        self.client_id: str | None = None
        self.buffer: str = ''

    def receive_updates(self):
        data = self.server.recv(1024)
        if not data:
            raise ConnectionResetError('Server disconnected.')

        self.buffer += data.decode()

        # Process all complete messages in the buffer
        while '\n' in self.buffer:
            message, self.buffer = self.buffer.split('\n', 1)
            if message.startswith('connect:'):
                client_id = message.split(':')[1]
                self.client_id = int(client_id)

            elif message.startswith('{'):
                update = json.loads(message)

                area_seed = update['area_seed']
                self.area_system.generate_area(area_seed)

                player_positions = update['player_positions']
                for player_position in player_positions:
                    player_id = player_position['id']
                    x = int(player_position['x'])
                    y = int(player_position['y'])
                    if player_id not in self.players:
                        self.players[player_id] = Player((x, y))
                    else:
                        player = self.players[player_id]
                        player.move_absolute(x, y)

                enemy_positions = update['enemy_positions']
                for enemy in Enemy.enemy_group:
                    enemy.kill()
                for enemy_position in enemy_positions:
                    x = int(enemy_position['x'])
                    y = int(enemy_position['y'])
                    Enemy((x, y), 0)

                projectile_positions = update['projectile_positions']
                for projectile in Projectile.projectile_group:
                    projectile.kill()
                for projectile_position in projectile_positions:
                    x = int(projectile_position['x'])
                    y = int(projectile_position['y'])
                    Projectile((x, y), 0)
