import logging
import random
from typing import List, Dict
from enum import Enum

from src.engine.Orb import Orb
from src.engine.Snake import Snake, Movement


class CellType(Enum):
    EMPTY = 0
    ORB = 'X'

def get_n_consecutive_empty_cells_from_grid(n: int, grid: dict, nb_cols: int, nb_rows: int, empty_value: int) -> List[List[dict]] | None:
    """get a 3-dimensional list where the 2nd degree lists represent every possible 'n' cells that are both aligned (vertic. & horiz.) AND empty
        Example for n=3, if the output is
            [ [ {x:0, y:2}, (x:0, y:3), (x:0, y:4)  ] ]
        ...this would mean that the only 3 cells of the grid that are both aligned and empty are the ones located at these coordinates.
    """
    is_a_valid_grid = isinstance(grid, dict)
    if is_a_valid_grid and len(grid) > 0:
        is_a_valid_grid = isinstance(next(iter(grid.keys())), tuple)
    if not is_a_valid_grid:
        logging.error(f'Arg grid must be a dictionary mapping tuples to integers (Ex: (2,3): 4.')
        return None

    consecutive = []
    consecutive_on_x = [[] for _ in range(nb_cols)]
    consecutive_on_y = []

    def check_consecutive():
        for x in range(0, len(consecutive_on_x)):
            if len(consecutive_on_x[x]) >= n:
                consecutive.append( consecutive_on_x[x][-n:] )
        if len(consecutive_on_y) >= n:
            consecutive.append( consecutive_on_y[-n:] )

    for y in range(0, nb_rows):
        for x in range(0, nb_cols):
            cell = grid[(x,y)]
            is_empty = cell == empty_value
            if is_empty:
                consecutive_on_x[x].append( {'x':x, 'y':y} )
                consecutive_on_y.append( {'x':x, 'y':y} )
            else:
                consecutive_on_x[x] = []
                consecutive_on_y = []
            check_consecutive()

    no_duplicate = []
    for element in consecutive:
        if element not in no_duplicate:
            no_duplicate.append(element)

    return no_duplicate

def get_empty_map(nb_col: int, nb_row: int) -> dict:
    map = {}
    for y in range(0, nb_row):
        for x in range(0, nb_col):
            map[(x, y)] = CellType.EMPTY.value
    return map


class World:

    def __init__(self, nb_col: int, nb_row: int):
        self.nb_col = nb_col
        self.nb_row = nb_row
        self.map = get_empty_map(nb_col=nb_col, nb_row=nb_row)
        self.snakes: Dict[int, Snake] = {}
        self.orbs: List[Orb] = []

    def create_snakes(self, quantity: int) -> None:
        for _ in range(0, quantity):
            snake = Snake(length=3, speed=1)
            self.snakes[snake.id] = snake

    def create_orbs(self, quantity: int) -> None:
        for _ in range(0, quantity):
            self.orbs.append( Orb() )

    def spawn_snakes(self) -> None:
        for snake_id, snake in self.snakes.items():
            snake.positions = self.get_random_n_consecutive_empty_cells(snake.length)
            self.set_snake_initial_direction(snake_id=snake_id)
            print(f'Empty cells chosen to spawn snake: {snake.positions}')
            # FIXME: Got this once -> "Empty cells chosen to spawn snake: [{'x': 24, 'y': 7}, {'x': 0, 'y': 8}, {'x': 1, 'y': 8}]"
            # FIXME: Got this once -> "Empty cells chosen to spawn snake: [{'x': 23, 'y': 20}, {'x': 24, 'y': 20}, {'x': 0, 'y': 21}]"
        self.update_map_state()

    def spawn_orbs(self) -> None:
        random_cells = random.sample(population=self.get_map_empty_cells(), k=len(self.orbs))
        for i, orb in enumerate(self.orbs):
            orb.x, orb.y = random_cells[i]['x'], random_cells[i]['y']
        self.update_map_state()

    def update_map_state(self) -> None:
        """Refresh the World.map dictionary to reflect latest state."""
        self.map = get_empty_map(nb_col=self.nb_col, nb_row=self.nb_row)
        for orb in self.orbs:
            if isinstance(orb.x, int) and isinstance(orb.y, int):
                self.map[(orb.x, orb.y)] = CellType.ORB.value
        for snake_id, snake in self.snakes.items():
            for cell in snake.positions:
                x, y = cell['x'], cell['y']
                self.map[(x,y)] = snake.id

    def update(self):
        """Called every ticks"""
        self.update_map_state()
        for snake_id, snake in self.snakes.items():
            snake.move()
        self.update_map_state()

    def get_state(self) -> dict:
        return {
            'snakes': self.snakes,
            'orbs': self.orbs
        }

    def show_map(self):
        """used for debugging"""
        map_str = '   ' + ''.join(str(i)+'  ' if len(str(i))<2 else str(i)+' ' for i in range(0, self.nb_col)) + '\n'
        for y in range(0, self.nb_row):
            map_str += str(y) + '  ' if len(str(y)) < 2 else str(y) + ' '
            for x in range(0, self.nb_col):
                map_str += str(self.map[(x,y)]) + '  '
            map_str += '\n'
        print(map_str)

    def get_map_empty_cells(self) -> List[dict]:
        """Get all the map cells that are empty"""
        empty_cells = []
        for y in range(0, self.nb_row):
            for x in range(0, self.nb_col):
                if self.map[(x,y)] == CellType.EMPTY.value:
                    empty_cells.append( {'x':x, 'y':y} )
        return empty_cells

    def get_random_n_consecutive_empty_cells(self, n: int) -> List[dict]:
        empty_cells = get_n_consecutive_empty_cells_from_grid(n=n, grid=self.map, nb_cols=self.nb_col, nb_rows=self.nb_row, empty_value=CellType.EMPTY.value)
        return random.choice(empty_cells)

    def set_snake_initial_direction(self, snake_id: int) -> bool:
        """Chose a direction for a Snake that just spawned."""
        head_position = self.snakes[snake_id].positions[0]
        x, y = head_position['x'], head_position['y']
        can_go_up =    y > 0 and self.map[(x,y-1)] == CellType.EMPTY
        can_go_right = x < self.nb_col-1 and self.map[(x+1, y)] == CellType.EMPTY
        can_go_down =  y < self.nb_row-1 and self.map[(x,y+1)] == CellType.EMPTY
        can_go_left =  x > 0 and self.map[(x-1,y)] == CellType.EMPTY
        if can_go_up:
            self.snakes[snake_id].direction = Movement.UP
        elif can_go_right:
            self.snakes[snake_id].direction = Movement.RIGHT
        elif can_go_down:
            self.snakes[snake_id].direction = Movement.DOWN
        elif can_go_left:
            self.snakes[snake_id].direction = Movement.LEFT
        else:
            logging.error(f'Snake {snake_id} cannot move.')
            return False
        return True