from typing import List, Tuple


class Snake:

    number_of_snakes = 0

    def __init__(self, length: int, speed: int):
        self.id = self.number_of_snakes+1
        self.length = length
        self.speed = speed
        self.number_of_snakes += 1
        self.positions = []

    def set_positions(self, positions: List[Tuple[int, int]]) -> None:
        self.positions = positions