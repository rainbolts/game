from enum import IntEnum

import pygame


class ScreenLayer(IntEnum):
    GROUND = 1
    ON_GROUND = 2
    ABOVE_GROUND = 3
    UI = 4


class Interactable:
    def __init__(self, layer: ScreenLayer, hitbox: pygame.Rect, obj: object) -> None:
        self.layer = layer
        self.hitbox = hitbox
        self.obj: object = obj


class InteractableSystem:
    def __init__(self) -> None:
        self.layer_test_order = list(reversed(ScreenLayer))
        self.layers: dict[ScreenLayer, list[Interactable]] = {}
        for layer in ScreenLayer:
            self.layers[layer] = []

    def add_interactable(self, interactable: Interactable) -> None:
        self.layers[interactable.layer].append(interactable)

    def reset(self) -> None:
        for layer in self.layers:
            self.layers[layer] = []

    def hit_test(self, point: tuple[int, int]) -> Interactable | None:
        for layer in self.layer_test_order:
            if layer not in self.layers:
                continue
            for interactable in self.layers[layer]:
                if interactable.hitbox.collidepoint(point):
                    return interactable
        return None