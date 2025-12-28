class Orb:

    number_of_orbs = 0

    def __init__(self):
        self.id = self.number_of_orbs+1
        self.x = None
        self.y = None
        Orb.number_of_orbs += 1

    def set_position(self, x: int, y: int):
        self.x = x
        self.y = y
