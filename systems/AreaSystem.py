from models.Area import Area
from systems.EnemySystem import EnemySystem


class AreaSystem:
    current_area: Area = None

    def __init__(self, enemy_system: EnemySystem):
        self.enemy_system = enemy_system

    def generate_area(self):
        if AreaSystem.current_area is None:
            AreaSystem.current_area = Area((20, 20), 2000)
            self.enemy_system.spawn_enemies(AreaSystem.current_area)
