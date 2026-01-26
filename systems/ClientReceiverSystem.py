import json
import socket

from models.Area import Area


class ClientReceiverSystem:
    def __init__(self, server: socket.socket):
        self.server = server
        self.area: Area | None = None
        self.client_id: int | None = None
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
                self.area = Area.from_broadcast(update, self.area)
