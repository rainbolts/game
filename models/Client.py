import socket

from models.Player import Player


class Client:
    def __init__(self, connection: socket.socket):
        self.client_id = id(connection)
        self.connection = connection
        self.player: Player | None = None
        self.buffer: str = ''
