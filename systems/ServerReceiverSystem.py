from socket import socket

from pygame import Vector2

from models.Client import Client
from models.Direction import Direction
from models.Loot import GearSlot, Loot
from systems.MovementSystem import MovementSystem
from systems.SkillSystem import SkillSystem


class ServerReceiverSystem:
    def __init__(self,
                 clients: dict[socket, Client],
                 movement_system: MovementSystem,
                 skill_system: SkillSystem):
        self.clients = clients
        self.movement_system = movement_system
        self.skill_system = skill_system
        self.client_buffer: dict[Client, str] = {}
        self.loot_system = None
        self.broadcaster = None

    def receive_updates(self, client: Client, address: str):
        if client not in self.client_buffer:
            self.client_buffer[client] = ''
        client_buffer = self.client_buffer[client]

        data = client.connection.recv(1024)
        if not data:
            raise ConnectionResetError(f'Client {address} disconnected.')
        client_buffer += data.decode()

        # Process all complete messages in the buffer
        while '\n' in client_buffer:
            message, client_buffer = client_buffer.split('\n', 1)

            if message == 'connect':
                client.connection.sendall(f'connect:{client.client_id}\n'.encode())

            elif message.startswith('move:'):
                direction = Direction(int(message.split(':')[1]))
                self.movement_system.start_moving(client.player, direction)

            elif message.startswith('stop:'):
                direction = Direction(int(message.split(':')[1]))
                self.movement_system.stop_moving(client.player, direction)

            elif message.startswith('attack:'):
                angle, magnitude = message.split(':')[1].split(',')
                destination_vector = Vector2()
                destination_vector.from_polar((float(magnitude), float(angle)))
                self.skill_system.start_attacking(client.player, destination_vector)

            elif message.startswith('attack_stop'):
                self.skill_system.stop_attacking(client.player)

            elif message.startswith('grab_inventory:'):
                split = message.split(':')
                server_id = int(split[1])
                loot_id = int(split[2])
                loot = client.player.inventory.get_loot(server_id, loot_id)
                client.player.inventory.move_to_container(loot, client.player.cursor_loot)

            elif message.startswith('drop_inventory:'):
                split = message.split(':')
                # Expected format: drop_inventory:server_id:loot_id:col:row
                server_id = int(split[1])
                loot_id = int(split[2])
                col = int(split[3])
                row = int(split[4])
                loot = client.player.cursor_loot.get_loot(server_id, loot_id)
                if loot is not None:
                    client.player.cursor_loot.move_to_container(loot, client.player.inventory, col, row)

            elif message.startswith('grab_gear:'):
                # Format: grab_gear:slot_value
                slot_value = int(message.split(':')[1])
                slot = GearSlot(slot_value)
                loot = client.player.gear.get(slot)
                if loot is not None and client.player.cursor_loot.get_loot_count() == 0:
                    # Move gear item to cursor
                    client.player.gear[slot] = None
                    client.player.cursor_loot.add_loot(loot)

            elif message.startswith('drop_gear:'):
                # Format: drop_gear:server_id:loot_id:slot_value
                split = message.split(':')
                server_id = int(split[1])
                loot_id = int(split[2])
                slot_value = int(split[3])
                slot = GearSlot(slot_value)

                loot = client.player.cursor_loot.get_loot(server_id, loot_id)
                if loot is None:
                    continue

                is_empty = client.player.gear.get(slot) is None
                if not is_empty:
                    continue

                if slot in Loot.GEAR_COMPATIBILITY[loot.loot_type]:
                    client.player.cursor_loot.remove(loot)
                    client.player.gear[slot] = loot

        self.client_buffer[client] = client_buffer
