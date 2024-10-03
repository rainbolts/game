from socket import socket

from models.Player import Player


class Client:
    def __init__(self, connection: socket):
        self.connection = connection
        self.player: Player | None = None
        self.buffer: str = ''
