import importlib
import json
from socket import socket

from models.Entity import Entity
from systems.AreaSystem import AreaSystem


class ClientReceiverSystem:
    def __init__(self,
                 server: socket,
                 area_system: AreaSystem):
        self.server = server
        self.area_system = area_system
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

                area_seed = update['area_seed']
                self.area_system.generate_area(area_seed)

                entity_updates = update['entities']
                for entity in Entity.entity_group:
                    entity.kill()
                for entity_update in entity_updates:
                    module = importlib.import_module(entity_update['module'])
                    klass = getattr(module, entity_update['class'])
                    klass.from_broadcast(entity_update)

