import copy

import pytest

from src.utils import conf
from src.engine.Orb import Orb
from src.engine.Snake import Snake, Direction
from src.engine.World import get_n_consecutive_empty_cells_from_grid, get_empty_map, World, CellType


def test_create_snakes(an_empty_world):
    an_empty_world.create_snakes(quantity=3)
    assert len(an_empty_world.snakes) == 3
    assert isinstance(next(iter(an_empty_world.snakes.values())), Snake)
    snake = next(iter(an_empty_world.snakes.values()))
    assert len(snake.positions) == snake.length
    assert isinstance(snake.positions, list)
    assert 'x' in snake.positions[0]
    assert 'y' in snake.positions[0]
    assert isinstance(snake.positions[0]['x'], int)
    assert isinstance(snake.positions[0]['y'], int)
    assert 0 <= snake.positions[0]['x'] <= an_empty_world.nb_col
    assert 0 <= snake.positions[0]['y'] <= an_empty_world.nb_row

def test_create_orbs(an_empty_world):
    number_of_orbs = 15
    an_empty_world.create_orbs(quantity=number_of_orbs)
    assert len(an_empty_world.orbs) == number_of_orbs
    first_orb = next(iter(an_empty_world.orbs.values()))
    assert isinstance(first_orb, Orb)
    assert isinstance(first_orb.x, int)
    assert isinstance(first_orb.y, int)

def test_get_map_empty_cells(an_empty_world):
    number_of_orbs = 15
    number_of_snakes = 3
    nb_empty_cells_before = len(an_empty_world.get_map_empty_cells())

    an_empty_world.create_orbs(quantity=number_of_orbs)
    an_empty_world.create_snakes(quantity=number_of_snakes)

    nb_empty_cells_after = len(an_empty_world.get_map_empty_cells())
    assert nb_empty_cells_before - nb_empty_cells_after == (number_of_orbs + number_of_snakes * conf['snakes']['length_initial'])

@pytest.mark.parametrize('nb_col, nb_row, expected', [
    (0, 0, {}),
    (0, 1, {}),
    (1, 1, {(0,0): CellType.EMPTY}),
    (1, 2, {(0,0): CellType.EMPTY,
            (0,1): CellType.EMPTY}),
    (4, 6, {(0,0): CellType.EMPTY, (1,0): CellType.EMPTY, (2,0): CellType.EMPTY, (3,0): CellType.EMPTY,
            (0,1): CellType.EMPTY, (1,1): CellType.EMPTY, (2,1): CellType.EMPTY, (3,1): CellType.EMPTY,
            (0,2): CellType.EMPTY, (1,2): CellType.EMPTY, (2,2): CellType.EMPTY, (3,2): CellType.EMPTY,
            (0,3): CellType.EMPTY, (1,3): CellType.EMPTY, (2,3): CellType.EMPTY, (3,3): CellType.EMPTY,
            (0,4): CellType.EMPTY, (1,4): CellType.EMPTY, (2,4): CellType.EMPTY, (3,4): CellType.EMPTY,
            (0,5): CellType.EMPTY, (1,5): CellType.EMPTY, (2,5): CellType.EMPTY, (3,5): CellType.EMPTY})
])
def test_get_empty_map(nb_col, nb_row, expected):
    assert get_empty_map(nb_col=nb_col, nb_row=nb_row) == expected

@pytest.mark.parametrize('n, empty_value, nb_cols, nb_rows, grid, expected', [

    (   0, 0, 0, 0, [],   None ),                      # Invalid param 'grid'
    (   0, 0, 0, 0, {}, [] ),                          # No cell = no empty cells
    (   1, 0, 0, 0, {}, [] ),                          # Same
    (   1, 0, 1, 1, {(0,0): 2}, [] ),                  # 1 cell but it is not empty = no empty cells
    (   1, 0, 1, 1, {(0,0): 0}, [[{'x':0, 'y': 0}]] ), # 1 cell and it is empty = 1 empty cell
    (   1, 9, 1, 1, {(0,0): 9}, [[{'x':0, 'y': 0}]] ), # Same (different empty value)
    (   2, 0, 1, 1, {(0,0): 0}, []),                   # Need 2 empty cells in a row but map contains only 1 empty cell

    (   # Need 2 empty cells in a row and map has that 1 time (2 columns)
        2, 0, 2, 1, {(0,0): 0, (1,0): 0},
        [[{'x':0, 'y': 0}, {'x':1, 'y': 0}]]
    ),
    (   # Need 2 empty cells in a row and map has that 1 time (2 rows)
        2, 0, 1, 2, {(0,0): 0, (0,1): 0},
        [[{'x':0, 'y': 0}, {'x':0, 'y': 1}]]
    ),
    (   # Need 2 empty cells in a row and map has that 2 times (2 rows)
        2, 0, 1, 9,
        {(0,0): 9,
         (0,1): 0,
         (0,2): 0,
         (0,3): 8,
         (0,4): 7,
         (0,5): 6,
         (0,6): 5,
         (0,7): 0,
         (0,8): 0},
        [[{'x': 0, 'y': 1}, {'x': 0, 'y': 2}],
         [{'x': 0, 'y': 7}, {'x': 0, 'y': 8}]]
    ),
    (   # Need 2 empty cells in a row and map has that 2 times (2 columns)
        2, 0, 9, 1,
        {(0, 0): 0, (1, 0): 0, (2, 0): 9, (3, 0): 8, (4, 0): 7, (5, 0): 6, (6, 0): 0, (7, 0): 0, (8, 0): 5},
        [[{'x': 0, 'y': 0}, {'x': 1, 'y': 0}], [{'x': 6, 'y': 0}, {'x': 7, 'y': 0}]]
    ),
    (   # Need 2 empty cells in a row and map has that 3 times (2 in a row + 1)
        2, 0, 9, 1,
        {(0, 0): 9, (1, 0): 0, (2, 0): 0, (3, 0): 0, (4, 0): 8, (5, 0): 7, (6, 0): 0, (7, 0): 0, (8, 0): 6},
        [[{'x': 1, 'y': 0}, {'x': 2, 'y': 0}], [{'x': 2, 'y': 0}, {'x': 3, 'y': 0}], [{'x': 6, 'y': 0}, {'x': 7, 'y': 0}]]
    ),
    (   # Need 4 empty cells in a row -> grid 7x7 - custom
        4, 0, 7, 7,
        {(0, 0): 1, (1, 0): 1, (2, 0): 1, (3, 0): 1, (4, 0): 1, (5, 0): 1, (6, 0): 1,
         (0, 1): 1, (1, 1): 1, (2, 1): 1, (3, 1): 0, (4, 1): 0, (5, 1): 0, (6, 1): 0,
         (0, 2): 1, (1, 2): 0, (2, 2): 1, (3, 2): 1, (4, 2): 1, (5, 2): 1, (6, 2): 1,
         (0, 3): 1, (1, 3): 0, (2, 3): 1, (3, 3): 1, (4, 3): 1, (5, 3): 1, (6, 3): 1,
         (0, 4): 1, (1, 4): 0, (2, 4): 1, (3, 4): 1, (4, 4): 1, (5, 4): 1, (6, 4): 1,
         (0, 5): 1, (1, 5): 0, (2, 5): 1, (3, 5): 1, (4, 5): 1, (5, 5): 1, (6, 5): 1,
         (0, 6): 1, (1, 6): 0, (2, 6): 0, (3, 6): 0, (4, 6): 0, (5, 6): 0, (6, 6): 0},

        [
            [{'x': 3, 'y': 1}, {'x': 4, 'y': 1}, {'x': 5, 'y': 1}, {'x': 6, 'y': 1}],
            [{'x': 1, 'y': 2}, {'x': 1, 'y': 3}, {'x': 1, 'y': 4}, {'x': 1, 'y': 5}],
            [{'x': 1, 'y': 3}, {'x': 1, 'y': 4}, {'x': 1, 'y': 5}, {'x': 1, 'y': 6}],
            [{'x': 1, 'y': 6}, {'x': 2, 'y': 6}, {'x': 3, 'y': 6}, {'x': 4, 'y': 6}],
            [{'x': 2, 'y': 6}, {'x': 3, 'y': 6}, {'x': 4, 'y': 6}, {'x': 5, 'y': 6}],
            [{'x': 3, 'y': 6}, {'x': 4, 'y': 6}, {'x': 5, 'y': 6}, {'x': 6, 'y': 6}],
        ]
    )
])
def test_get_n_consecutive_empty_cells_from_grid(n, empty_value, nb_cols, nb_rows, grid, expected):
    assert get_n_consecutive_empty_cells_from_grid(n=n, grid=grid, empty_value=empty_value, nb_cols=nb_cols, nb_rows=nb_rows) == expected

@pytest.mark.parametrize('snake_positions, orbs_positions, map_before, map_after', [
    (
        [{'x':0,'y':0}, {'x':1,'y':0}, {'x':2,'y':0},],
        [(0,1), (0,2), (0,3), (0,4)],

        {(0,0): CellType.EMPTY, (1,0): CellType.EMPTY, (2,0): CellType.EMPTY, (3,0): CellType.EMPTY,
         (0,1): CellType.EMPTY, (1,1): CellType.EMPTY, (2,1): CellType.EMPTY, (3,1): CellType.EMPTY,
         (0,2): CellType.EMPTY, (1,2): CellType.EMPTY, (2,2): CellType.EMPTY, (3,2): CellType.EMPTY,
         (0,3): CellType.EMPTY, (1,3): CellType.EMPTY, (2,3): CellType.EMPTY, (3,3): CellType.EMPTY,
         (0,4): CellType.EMPTY, (1,4): CellType.EMPTY, (2,4): CellType.EMPTY, (3,4): CellType.EMPTY,
         (0,5): CellType.EMPTY, (1,5): CellType.EMPTY, (2,5): CellType.EMPTY, (3,5): CellType.EMPTY},

        {(0, 0): CellType.SNAKE, (1, 0): CellType.SNAKE, (2, 0): CellType.SNAKE, (3, 0): CellType.EMPTY,
         (0, 1): CellType.ORB,   (1, 1): CellType.EMPTY, (2, 1): CellType.EMPTY, (3, 1): CellType.EMPTY,
         (0, 2): CellType.ORB,   (1, 2): CellType.EMPTY, (2, 2): CellType.EMPTY, (3, 2): CellType.EMPTY,
         (0, 3): CellType.ORB,   (1, 3): CellType.EMPTY, (2, 3): CellType.EMPTY, (3, 3): CellType.EMPTY,
         (0, 4): CellType.ORB,   (1, 4): CellType.EMPTY, (2, 4): CellType.EMPTY, (3, 4): CellType.EMPTY,
         (0, 5): CellType.EMPTY, (1, 5): CellType.EMPTY, (2, 5): CellType.EMPTY, (3, 5): CellType.EMPTY}
    )
])
def test_update_map_state(snake_positions, orbs_positions, map_before, map_after):
    world = World(nb_col=4, nb_row=6)
    world.map = copy.deepcopy(map_before)
    snake = Snake(length=3, speed=1)
    snake.positions = snake_positions
    world.snakes[1] = snake
    for i, position in enumerate(orbs_positions):
        orb = Orb()
        orb.x, orb.y = position
        world.orbs[i] = orb
    assert world.map == map_before
    world.update_map_state()
    assert world.map == map_after

def test_get_snake_player():
    world = World(nb_col=24, nb_row=24)
    world.create_snakes(quantity=5, first_is_a_player=True)
    first_snake = next(iter(world.snakes.values()))
    assert world.get_snake_player() == first_snake

def test_set_player_direction():
    world = World(nb_col=4, nb_row=6)
    world.create_snakes(quantity=2, first_is_a_player=True)
    player = next(iter(world.snakes.values()))
    player.direction = Direction.DOWN
    success = world.set_player_direction(direction=Direction.LEFT)
    assert success
    assert player.direction == Direction.LEFT
