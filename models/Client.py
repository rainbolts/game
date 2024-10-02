from socket import socket

from models.Player import Player


class Client:
    def __init__(self, connection: socket):
        self.connection = connection
        self.player: Player = Player((0, 0))
        self.buffer: str = ''
