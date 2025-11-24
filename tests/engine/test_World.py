import pytest
from src.engine.Orb import Orb
from src.engine.Snake import Snake
from src.engine.World import get_n_consecutive_empty_cells_from_grid, get_empty_map


def test_create_snakes(an_empty_world):
    an_empty_world.create_snakes(quantity=3)
    assert len(an_empty_world.snakes) == 3
    assert isinstance(next(iter(an_empty_world.snakes.values())), Snake)
    assert next(iter(an_empty_world.snakes.values())).positions == []

def test_create_orbs(an_empty_world):
    number_of_orbs = 15
    an_empty_world.create_orbs(quantity=number_of_orbs)
    assert len(an_empty_world.orbs) == number_of_orbs
    first_orb = an_empty_world.orbs[0]
    assert isinstance(first_orb, Orb)
    assert first_orb.x is None
    assert first_orb.y is None

def test_spawn_snakes(a_world_with_one_snake):
    a_world_with_one_snake.spawn_snakes()
    snake = next(iter(a_world_with_one_snake.snakes.values()))
    assert len(snake.positions) == snake.length
    assert isinstance(snake.positions, list)
    assert 'x' in snake.positions[0]
    assert 'y' in snake.positions[0]
    assert isinstance(snake.positions[0]['x'], int)
    assert isinstance(snake.positions[0]['y'], int)
    assert 0 <= snake.positions[0]['x'] <= a_world_with_one_snake.nb_col
    assert 0 <= snake.positions[0]['y'] <= a_world_with_one_snake.nb_row

def test_spawn_ten_snakes(a_world_with_five_snakes):
    nb_empty_cells_before = len(a_world_with_five_snakes.get_map_empty_cells())
    a_world_with_five_snakes.spawn_snakes()
    nb_cells_with_snakes = sum([snake.length for snake in a_world_with_five_snakes.snakes.values()])
    nb_empty_cells_after = len(a_world_with_five_snakes.get_map_empty_cells())
    assert nb_empty_cells_before == nb_empty_cells_after + nb_cells_with_snakes

def test_spawn_orbs(a_world_with_10_orbs):
    nb_empty_cells_before = len(a_world_with_10_orbs.get_map_empty_cells())
    a_world_with_10_orbs.spawn_orbs()
    nb_empty_cells_after = len(a_world_with_10_orbs.get_map_empty_cells())
    assert isinstance(a_world_with_10_orbs.orbs[0].x, int)
    assert isinstance(a_world_with_10_orbs.orbs[0].y, int)
    assert nb_empty_cells_before - nb_empty_cells_after == 10

def test_get_map_empty_cells(a_world_with_one_snake_ten_orbs):
    total_cells = a_world_with_one_snake_ten_orbs.nb_col * a_world_with_one_snake_ten_orbs.nb_row
    cells_not_empty = 10 + next(iter(a_world_with_one_snake_ten_orbs.snakes.values())).length
    a_world_with_one_snake_ten_orbs.spawn_orbs()
    a_world_with_one_snake_ten_orbs.spawn_snakes()
    empty_cells = a_world_with_one_snake_ten_orbs.get_map_empty_cells()
    assert len(empty_cells) == total_cells - cells_not_empty

def test_update_map(a_world_with_one_snake_ten_orbs):
    total_cells = a_world_with_one_snake_ten_orbs.nb_col * a_world_with_one_snake_ten_orbs.nb_row
    assert len(a_world_with_one_snake_ten_orbs.get_map_empty_cells()) == total_cells
    a_world_with_one_snake_ten_orbs.spawn_orbs()
    a_world_with_one_snake_ten_orbs.spawn_snakes()
    cells_not_empty = 10 + next(iter(a_world_with_one_snake_ten_orbs.snakes.values())).length
    assert len(a_world_with_one_snake_ten_orbs.get_map_empty_cells()) == total_cells - cells_not_empty

@pytest.mark.parametrize('nb_col, nb_row, expected', [
    (0, 0, {}),
    (0, 1, {}),
    (1, 1, {(0,0): 0}),
    (1, 2, {(0,0): 0,
            (0,1): 0}),
    (4, 6, {(0,0): 0, (1,0): 0, (2,0): 0, (3,0): 0,
            (0,1): 0, (1,1): 0, (2,1): 0, (3,1): 0,
            (0,2): 0, (1,2): 0, (2,2): 0, (3,2): 0,
            (0,3): 0, (1,3): 0, (2,3): 0, (3,3): 0,
            (0,4): 0, (1,4): 0, (2,4): 0, (3,4): 0,
            (0,5): 0, (1,5): 0, (2,5): 0, (3,5): 0})
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
def test_get_n_consecutive_empty_cells_from_two_dimensional_list(n, empty_value, nb_cols, nb_rows, grid, expected):
    assert get_n_consecutive_empty_cells_from_grid(n=n, grid=grid, empty_value=empty_value, nb_cols=nb_cols, nb_rows=nb_rows) == expected