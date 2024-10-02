import json
from socket import socket

from models.Player import Player


class ClientReceiverSystem:
    def __init__(self, connection: socket, players: dict[str, Player]):
        self.connection = connection
        self.players = players
        self.client_id: str | None = None
        self.buffer: str = ''

    def receive_updates(self):
        data = self.connection.recv(1024)
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

                player_positions = update['player_positions']
                for player_position in player_positions:
                    player_id = player_position['id']
                    x = int(player_position['x'])
                    y = int(player_position['y'])
                    if player_id not in self.players:
                        self.players[player_id] = Player((x, y))
                    else:
                        self.players[player_id].position = (x, y)
