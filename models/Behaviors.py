from enum import IntEnum


class CollisionBehavior(IntEnum):
    BOUNCE = 1
    DISAPPEAR = 2
    DAMAGE = 3
    STICKY = 4
    AREA_TRANSITION = 5
