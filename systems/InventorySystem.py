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
        input_system.subscribe(Control.BASIC_INTERACTION, self.grab_item)

    def grab_item(self, event) -> None:
        if self.player is None:
            return

        interactable = self.interactable_system.hit_test(event.pos)
        if interactable is None:
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

        # Drop loot into inventory
        elif isinstance(interactable.obj, tuple) and len(interactable.obj) == 3:
            container, col, row = interactable.obj
            if not isinstance(container, LootContainer):
                return

            if self.player.cursor_loot.get_loot_count() == 0:
                return

            cursor_loot = next(iter(self.player.cursor_loot.loot_dict.values()))
            self.server.sendall(f'drop_inventory:{cursor_loot.server_id}:{cursor_loot.loot_id}:{col}:{row}\n'.encode())
