import socket

from models.Loot import Loot
from models.Player import Player
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
        if interactable is not None and isinstance(interactable.obj, Loot):
            loot = interactable.obj
            if self.player.show_character_panel:
                if self.player.cursor_loot.get_loot_count() == 0:
                    self.server.sendall(f'grab_inventory:{loot.server_id}:{loot.loot_id}\n'.encode())
