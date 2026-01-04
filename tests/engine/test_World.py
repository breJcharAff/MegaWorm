import copy
from typing import Tuple, List

import pytest

from src.ui.views.game_view import GameMode
from src.engine.Orb import Orb
from src.engine.Snake import Snake, Direction
from src.engine.World import get_n_consecutive_empty_cells_from_grid, get_empty_map, World, CellType, get_new_position

@pytest.mark.parametrize('', [
    ()
])
def test_create_snakes_():
    pass

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

@pytest.mark.parametrize('nb_col, nb_row, expected_before, nb_snakes, nb_orbs, expected_after', [
    (  1,  1,   1, 0,   0,  1 ), # 1x1   - empty
    (  4,  3,  12, 0,   0, 12 ), # 4x3   - empty
    (  1,  1,   1, 0,   1,  0 ), # 1x1   - 1 orb (full)
    (  1,  3,   3, 1,   0,  0 ), # 1x3   - 1 snake (=3 cells)  (full)
    (  3,  6,  18, 1,   0, 15 ), # 3x6   - 1 snake             (=18-3)
    (  3,  6,  18, 1,   1, 14 ), # 3x6   - 1 snake  - 1 orb    (=18-3-1)
    (  9,  7,  63, 3,   4, 50 ), # 9x7   - 3 snakes - 4 orbs   (=67-3x3-4x1)
    ( 15, 10, 150, 5, 100, 35 ), # 15x10 - 5 snakes - 100 orbs (=150-5x3-100x1)
    ( 15, 10, 150, 0, 150,  0 ), # 15x10 - map full of orbs
])
def test_get_map_empty_cells(nb_col: int, nb_row: int, expected_before: int, nb_snakes: int, nb_orbs: int, expected_after: int):
    world = World(nb_col=nb_col, nb_row=nb_row, game_mode=GameMode.BOTS, auto_retry=False)
    assert len(world.get_map_empty_cells()) == expected_before
    world.create_snakes(quantity=nb_snakes)
    world.create_orbs(quantity=nb_orbs)
    assert len(world.get_map_empty_cells()) == expected_after

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
        [{'x':0,'y':0}, {'x':1,'y':0}, {'x':2,'y':0}],
        [(0,1), (0,2), (0,3), (0,4)],

        {(0,0): CellType.EMPTY, (1,0): CellType.EMPTY, (2,0): CellType.EMPTY, (3,0): CellType.EMPTY,
         (0,1): CellType.EMPTY, (1,1): CellType.EMPTY, (2,1): CellType.EMPTY, (3,1): CellType.EMPTY,
         (0,2): CellType.EMPTY, (1,2): CellType.EMPTY, (2,2): CellType.EMPTY, (3,2): CellType.EMPTY,
         (0,3): CellType.EMPTY, (1,3): CellType.EMPTY, (2,3): CellType.EMPTY, (3,3): CellType.EMPTY,
         (0,4): CellType.EMPTY, (1,4): CellType.EMPTY, (2,4): CellType.EMPTY, (3,4): CellType.EMPTY,
         (0,5): CellType.EMPTY, (1,5): CellType.EMPTY, (2,5): CellType.EMPTY, (3,5): CellType.EMPTY},

        {(0, 0): CellType.MAIN_SNAKE, (1, 0): CellType.MAIN_SNAKE, (2, 0): CellType.MAIN_SNAKE, (3, 0): CellType.EMPTY,
         (0, 1): CellType.ORB,        (1, 1): CellType.EMPTY,      (2, 1): CellType.EMPTY,      (3, 1): CellType.EMPTY,
         (0, 2): CellType.ORB,        (1, 2): CellType.EMPTY,      (2, 2): CellType.EMPTY,      (3, 2): CellType.EMPTY,
         (0, 3): CellType.ORB,        (1, 3): CellType.EMPTY,      (2, 3): CellType.EMPTY,      (3, 3): CellType.EMPTY,
         (0, 4): CellType.ORB,        (1, 4): CellType.EMPTY,      (2, 4): CellType.EMPTY,      (3, 4): CellType.EMPTY,
         (0, 5): CellType.EMPTY,      (1, 5): CellType.EMPTY,      (2, 5): CellType.EMPTY,      (3, 5): CellType.EMPTY}
    )
])
def test_update_map_state(snake_positions, orbs_positions, map_before, map_after):
    world = World(nb_col=4, nb_row=6, game_mode=GameMode.BOTS, auto_retry=False)
    world.map = copy.deepcopy(map_before)
    snake = Snake(length=3, speed=1)
    snake.positions = snake_positions
    snake.is_main_snake = True
    world.snakes[1] = snake
    for i, position in enumerate(orbs_positions):
        orb = Orb()
        orb.x, orb.y = position
        world.orbs[i] = orb
    assert world.map == map_before
    world.update_map_state()
    assert world.map == map_after

def test_get_snake_player():
    world = World(nb_col=24, nb_row=24, game_mode=GameMode.BOTS, auto_retry=False)
    world.create_snakes(quantity=5, first_is_a_player=True)
    first_snake = next(iter(world.snakes.values()))
    assert world.get_snake_player() == first_snake

def test_set_player_direction():
    world = World(nb_col=4, nb_row=6, game_mode=GameMode.BOTS, auto_retry=False)
    world.create_snakes(quantity=2, first_is_a_player=True)
    player = next(iter(world.snakes.values()))
    player.direction = Direction.DOWN
    success = world.set_direction_player(direction=Direction.LEFT)
    assert success
    assert player.direction == Direction.LEFT

@pytest.mark.parametrize('initial_position, direction, nb_of_moves, expected', [
    ((0, 0), Direction.RIGHT, 0, (0, 0)), # no move
    ((0, 0), Direction.RIGHT, 6, (6, 0)), # 6 -> RIGHT
    ((0, 0), Direction.DOWN,  6, (0, -6)),
    ((2, 6), Direction.UP,    3, (2, 9))
])
def test_get_new_position(initial_position: Tuple[int, int], direction: Direction, nb_of_moves: int, expected: Tuple[int, int]):
    assert expected == get_new_position(initial_position=initial_position, direction=direction, nb_of_moves=nb_of_moves)


@pytest.mark.parametrize('radar_nb_cells, snake_positions, map, expected', [
    ( # HEAD = (1,2) - Radar = 3 cells
        3,
        [{'x':0,'y':3}, {'x':1,'y':3}],
        {(0, 5): CellType.EMPTY,      (1, 5): CellType.SNAKE,      (2, 5): CellType.EMPTY, (3, 5): CellType.EMPTY, (4, 5): CellType.EMPTY,
         (0, 4): CellType.ORB,        (1, 4): CellType.ORB,        (2, 4): CellType.EMPTY, (3, 4): CellType.EMPTY, (4, 4): CellType.EMPTY,
         (0, 3): CellType.MAIN_SNAKE, (1, 3): CellType.MAIN_SNAKE, (2, 3): CellType.EMPTY, (3, 3): CellType.EMPTY, (4, 3): CellType.ORB,
         (0, 2): CellType.ORB,        (1, 2): CellType.EMPTY,      (2, 2): CellType.EMPTY, (3, 2): CellType.EMPTY, (4, 2): CellType.EMPTY,
         (0, 1): CellType.ORB,        (1, 1): CellType.EMPTY,      (2, 1): CellType.EMPTY, (3, 1): CellType.EMPTY, (4, 1): CellType.EMPTY,
         (0, 0): CellType.EMPTY,      (1, 0): CellType.EMPTY,      (2, 0): CellType.EMPTY, (3, 0): CellType.EMPTY, (4, 0): CellType.EMPTY},
        (
            # Number of empty cells before orb       --> UP: 0          / RIGHT: 2       / DOWN: 3 (no orb = max = 3) / LEFT: 3 (no orb = max = 3)
            0, 2, 3, 3,
            # Number of empty cells before collision --> UP: 1 (ennemi) / RIGHT: 3 (max) / DOWN: 3 (max)              / LEFT: 1 (wall)
            1, 3, 3, 1
        )
    )
])
def test_get_state_snake(radar_nb_cells: int, snake_positions: List[dict], map: dict[Tuple, CellType], expected: Tuple[int]):
    world = World(nb_col=5, nb_row=6, game_mode=GameMode.LEARN, auto_retry=False)
    world.map = map
    snake = Snake(length=2, speed=1)
    snake.positions = snake_positions
    snake.radar_nb_cells = radar_nb_cells
    world.snakes[snake.id] = snake
    assert world.get_state_snake(snake_id=snake.id) == expected

