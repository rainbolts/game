from models.Area import Area
from models.Client import Client
from models.Player import Player
from systems.EnemySystem import EnemySystem


class AreaSystem:
    def __init__(self):
        self.enemy_system = EnemySystem()
        self.areas: list[Area] = []

    def run_once(self, clients: list[Client]):
        if len(clients) == 0:
            return

        # Remove empty areas
        self.areas = [area for area in self.areas if len(area.players) > 0]

        # Create the first area
        if len(self.areas) == 0:
            area = Area()
            self.enemy_system.spawn_enemies(area)
            self.areas.append(area)

        # Spawn newly connected players in the oldest area
        spawn_area = self.areas[0]
        for client in clients:
            if client.player is None:
                spawn = spawn_area.get_spawn()
                client.player = Player(client.client_id, spawn)
                spawn_area.players.add(client.player)

        # Move players between areas
        new_area = None
        for i, area in enumerate(self.areas):
            if not area.exit:
                continue
            exit_rect = area.exit.image.get_rect(topleft=area.exit.get_pixel_location())
            for player in area.players:
                player_rect = player.image.get_rect(topleft=player.get_pixel_location())
                if exit_rect.colliderect(player_rect):
                    # If the player is in the last area, create a new area
                    if i == len(self.areas) - 1 and not new_area:
                        new_area = Area()
                        move_area = new_area
                        self.enemy_system.spawn_enemies(new_area)
                    else:
                        move_area = self.areas[i + 1]

                    # Move the player to the next area
                    area.players.remove(player)
                    move_area.players.add(player)
                    player.move_absolute(*move_area.get_spawn())

        if new_area:
            self.areas.append(new_area)
