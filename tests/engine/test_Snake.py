from typing import List

import pytest

from src.engine.Snake import Direction, Snake


def test_set_snake_as_player(a_world_with_one_snake):
    snake = next(iter(a_world_with_one_snake.snakes.values()))
    assert snake.is_bot
    snake.set_snake_as_player()
    assert not snake.is_bot

@pytest.mark.parametrize('direction_snake, direction_desired, expected', [
    ( Direction.UP, Direction.DOWN, False ),
    ( Direction.DOWN, Direction.UP, False ),
    ( Direction.LEFT, Direction.RIGHT, False ),
    ( Direction.RIGHT, Direction.LEFT, False ),

    ( Direction.UP, Direction.RIGHT, True ),
    ( Direction.UP, Direction.LEFT, True ),
    ( Direction.DOWN, Direction.LEFT, True ),
    ( Direction.RIGHT, Direction.UP, True ),
])
def test_can_change_direction(direction_snake, direction_desired, expected):
    snake = Snake(length=3, speed=1)
    snake.direction = direction_snake
    assert snake.can_change_direction(direction=direction_desired) == expected

@pytest.mark.parametrize('positions, expected', [
    ( # cannot go LEFT
        [{'x': 0, 'y': 0}, {'x': 1, 'y': 0}, {'x': 2, 'y': 0}],
        [Direction.UP, Direction.RIGHT, Direction.DOWN]
    ),
    ( # cannot go UP
        [{'x': 0, 'y': 2}, {'x': 0, 'y': 1}, {'x': 0, 'y': 0}],
        [Direction.RIGHT, Direction.DOWN, Direction.LEFT]
    ),
    ( # cannot go RIGHT
        [{'x': 2, 'y': 0}, {'x': 1, 'y': 0}, {'x': 0, 'y': 0}],
        [Direction.UP, Direction.DOWN, Direction.LEFT]
    ),
    ( # cannot go DOWN
        [{'x': 0, 'y': 0}, {'x': 0, 'y': 1}, {'x': 0, 'y': 2}],
        [Direction.UP, Direction.RIGHT, Direction.LEFT]
    )
])
def test_authorized_directions_based_on_body(positions: List[dict], expected: List[Direction]):
    snake = Snake(length=3, speed=1)
    snake.positions = positions
    assert snake.authorized_directions_based_on_body() == expected