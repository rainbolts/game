import socket

from models.Loot import Loot
from models.Player import Player
from models.LootContainer import LootContainer
from systems.InputSystem import InputSystem, Control
from systems.InteractableSystem import InteractableSystem


class InventorySystem:
    def __init__(self, input_system: InputSystem, interactable_system: InteractableSystem, server: socket.socket) -> None:
        self.player: Player | None = None
        self.interactable_system = interactable_system
        self.server = server
        self.input_system = input_system
        input_system.subscribe(Control.BASIC_INTERACTION, self.grab_item)

    def grab_item(self, event) -> None:
        if self.player is None:
            return

        interactable = self.interactable_system.hit_test(event.pos)
        if interactable is None:
            # Drop loot on ground from cursor
            if self.player.cursor_loot.get_loot_count() > 0:
                cursor_loot = next(iter(self.player.cursor_loot.loot_dict.values()))
                offset_x, offset_y = self.input_system.get_offset(self.player)
                world_x = int(event.pos[0] - offset_x)
                world_y = int(event.pos[1] - offset_y)
                self.server.sendall(f'drop_ground:{cursor_loot.server_id}:{cursor_loot.loot_id}:{world_x}:{world_y}\n'.encode())

            return

        # Grab loot from inventory
        if isinstance(interactable.obj, Loot):
            loot = interactable.obj
            if self.player.show_character_panel:
                if self.player.cursor_loot.get_loot_count() == 0:
                    # Cursor empty, clicked on item in inventory. Request a grab.
                    self.server.sendall(f'grab_inventory:{loot.server_id}:{loot.loot_id}\n'.encode())
                else:
                    # Loot swap not implemented
                    pass

        # Drop loot into gear slot
        elif isinstance(interactable.obj, tuple) and len(interactable.obj) == 2:
            player, gear_slot = interactable.obj
            if isinstance(player, Player) and isinstance(gear_slot, int):
                gear_slot = int(gear_slot)
                if self.player.cursor_loot.get_loot_count() == 1:
                    cursor_loot = next(iter(self.player.cursor_loot.loot_dict.values()))
                    self.server.sendall(f'drop_gear:{cursor_loot.server_id}:{cursor_loot.loot_id}:{gear_slot}\n'.encode())

        # Grab loot from gear slot
        elif (isinstance(interactable.obj, tuple)
              and len(interactable.obj) == 3
              and isinstance(interactable.obj[0], Player)
              and isinstance(interactable.obj[1], int)
              and isinstance(interactable.obj[2], Loot)):
            player, gear_slot, loot = interactable.obj
            gear_slot = int(gear_slot)
            if self.player.cursor_loot.get_loot_count() == 0:
                self.server.sendall(f'grab_gear:{gear_slot}\n'.encode())

        # Drop loot into inventory
        elif (isinstance(interactable.obj, tuple)
              and len(interactable.obj) == 3
              and isinstance(interactable.obj[0], LootContainer)
              and isinstance(interactable.obj[1], int)
              and isinstance(interactable.obj[2], int)):
            _inventory, col, row = interactable.obj

            if self.player.cursor_loot.get_loot_count() == 0:
                return

            cursor_loot = next(iter(self.player.cursor_loot.loot_dict.values()))
            self.server.sendall(f'drop_inventory:{cursor_loot.server_id}:{cursor_loot.loot_id}:{col}:{row}\n'.encode())
