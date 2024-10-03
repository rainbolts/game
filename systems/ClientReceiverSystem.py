import json
from socket import socket

from models.Player import Player
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
                print('Received:', message)
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
