import logging

from enum import Enum
from typing import List

logger = logging.getLogger(__name__)

class Direction(Enum):
    UP    = {'x':  0, 'y':  1}
    RIGHT = {'x':  1, 'y':  0}
    DOWN  = {'x':  0, 'y': -1}
    LEFT  = {'x': -1, 'y':  0}

class Snake:

    number_of_snakes = 0

    def __init__(self, length: int, speed: int):
        self.id = self.number_of_snakes+1
        self.length = length
        self.speed = speed
        self.positions = []
        self.direction = None
        self.is_bot = True
        self.is_main_snake = False
        Snake.number_of_snakes += 1

    def set_snake_as_player(self) -> None:
        """The snake is controlled by (human) keyboard input"""
        self.is_bot = False
        self.is_main_snake = True

    def can_change_direction(self, direction: Direction):
        """A snake cannot go the opposite way."""
        if direction == Direction.UP and self.direction == Direction.DOWN:
            return False
        if direction == Direction.DOWN and self.direction == Direction.UP:
            return False
        if direction == Direction.LEFT and self.direction == Direction.RIGHT:
            return False
        if direction == Direction.RIGHT and self.direction == Direction.LEFT:
            return False
        return True

    def authorized_direction(self) -> List[Direction]:
        """Get the 3 authorized directions for a snake (a snake cannot go the opposite way)."""
        match self.direction:
            case Direction.UP:
                return [Direction.UP, Direction.RIGHT, Direction.LEFT]
            case Direction.RIGHT:
                return [Direction.UP, Direction.RIGHT, Direction.DOWN]
            case Direction.DOWN:
                return [Direction.RIGHT, Direction.DOWN, Direction.LEFT]
            case Direction.LEFT:
                return [Direction.UP, Direction.DOWN, Direction.LEFT]
            case _:
                return self.authorized_directions_based_on_body()

    def authorized_directions_based_on_body(self) -> List[Direction]:
        """Get the 3 authorized directions for a snake (a snake cannot go the opposite way).
        Used only at the beginning when the snake direction is not yet set."""
        all_directions = list(Direction)
        if self.length <= 1:
            return all_directions

        head = self.positions[-1]
        neck = self.positions[-2]

        authorized = []
        for direction in all_directions:
            target_cell = {
                'x': head['x'] + direction.value['x'],
                'y': head['y'] + direction.value['y']
            }
            if target_cell != neck:
                authorized.append(direction)

        return authorized

    def set_direction(self, direction: Direction) -> None:
        self.direction = direction
        logger.debug(f'Snake {self.id} new direction = {self.direction}')

    def next_position(self, direction: Direction | None = None) -> dict:
        """Give the next x/y position for the snake head if it were to move
        1 cell in its current direction or the direction provided."""
        direction_ = direction if direction is not None else self.direction
        head = self.positions[-1]
        return {
            'x': head['x'] + direction_.value['x'],
            'y': head['y'] + direction_.value['y']
        }

    def move(self, grow: bool) -> None:
        """Actually moves the snake."""
        self.positions.append( self.next_position() )
        if not grow:
            self.positions.pop(0)
        logger.debug(f'Snake {self.id} moved to {self.positions} - {self.direction} - Grow = {grow}')

    def snake_str(self) -> str:
        """Used for debugging."""
        return (f'\n   - Id        = {self.id}\n'
               f'   - Length    = {self.length}\n'
               f'   - Position  = {self.positions}\n'
               f'   - Direction = {self.direction}\n'
               f'   - Speed     = {self.speed}\n'
               f'   - Is bot    = {self.is_bot}')
