from models.Area import Area
from systems.EnemySystem import EnemySystem


class AreaSystem:
    def __init__(self):
        self.enemy_system = EnemySystem()
        self.current_area: Area | None = None

    def generate_area(self, seed: int | None = None):
        if self.current_area is None:
            self.current_area = Area(2000, seed)
            self.enemy_system.spawn_enemies(self.current_area)
