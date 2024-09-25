from models.Area import Area


class AreaSystem:
    def __init__(self):
        self.current_area = None

    def generate_area(self):
        if self.current_area is None:
            self.current_area = Area((20, 20), 2000)
