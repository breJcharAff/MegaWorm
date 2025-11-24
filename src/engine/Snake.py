import random
from typing import List
from enum import Enum

class Movement(Enum):
    UP = {'x': -1, 'y': 0}
    RIGHT = {'x': 0, 'y': 1}
    DOWN = {'x': 1, 'y': 0}
    LEFT = {'x': 0, 'y': -1}

class Snake:

    number_of_snakes = 0

    def __init__(self, length: int, speed: int):
        self.id = self.number_of_snakes+1
        self.length = length
        self.speed = speed
        self.positions = []
        self.direction = None
        Snake.number_of_snakes += 1

    def set_positions(self, positions: List[dict]) -> None:
        self.positions = positions

    def move(self):
        """Random move for now"""
        self.move_to(move=random.choice(list(Movement)).value)

    def move_to(self, move: Movement) -> None:
        """Move the snake (UP/RIGHT/DOWN/LEFT)"""
        new_positions = []
        for cell in self.positions:
            new_position_cell = {'x': cell['x'] + move['x'], 'y': cell['y'] + move['y']}
            new_positions.append( new_position_cell )
        self.positions = new_positions

        print(f'Position before : {self.positions}')
        print(f'Move = {move}')
        print(f'Position after  : {new_positions}')
