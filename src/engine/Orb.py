from enum import Enum


class Movement(Enum):
    UP = 1
    RIGHT = 2
    BOTTOM = 3
    LEFT = 4

class Orb:

    number_of_orbs = 0

    def __init__(self):
        self.x = None
        self.y = None
        self.number_of_orbs += 1

    def set_position(self, x: int, y: int):
        self.x = x
        self.y = y
