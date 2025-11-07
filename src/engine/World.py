import logging
import random
from typing import List
from enum import Enum

from src.engine.Orb import Orb
from src.engine.Snake import Snake

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

def get_empty_map(xmax: int, ymax: int) -> dict:
    map = {}
    for y in range(0, ymax):
        for x in range(0, xmax):
            map[(x, y)] = CellType.EMPTY.value
    return map


class World:

    def __init__(self, xmax: int, ymax: int):
        self.xmax = xmax
        self.ymax = ymax
        # self.map = [[EMPTY for _ in range(0, ymax)] for _ in range(0, xmax) ]
        self.map = get_empty_map(xmax=xmax, ymax=ymax)
        self.snakes = []
        self.orbs = []

    def create_snakes(self, quantity: int) -> None:
        for _ in range(0, quantity):
            self.snakes.append( Snake(length=3, speed=1) )

    def create_orbs(self, quantity: int) -> None:
        for _ in range(0, quantity):
            self.orbs.append( Orb() )

    def spawn_snakes(self) -> None:
        for snake in self.snakes:
            snake.positions = self.get_random_n_consecutive_empty_cells(snake.length)
            print(f'Empty cells chosen to spawn snake: {snake.positions}')
        self.update_map()

    def spawn_orbs(self) -> None:
        random_cells = random.sample(population=self.get_map_empty_cells(), k=len(self.orbs))
        for i, orb in enumerate(self.orbs):
            orb.x, orb.y = random_cells[i]['x'], random_cells[i]['y']
        self.update_map()

    def update_map(self) -> None:
        self.map = get_empty_map(xmax=self.xmax, ymax=self.ymax)
        for orb in self.orbs:
            if isinstance(orb.x, int) and isinstance(orb.y, int):
                self.map[(orb.x, orb.y)] = CellType.ORB.value
        for snake in self.snakes:
            for cell in snake.positions:
                x, y = cell['x'], cell['y']
                self.map[(x,y)] = snake.id

    def show_map(self):
        """used for debugging"""
        map_str = '   ' + ''.join(str(i)+'  ' if len(str(i))<2 else str(i)+' ' for i in range(0, self.xmax)) + '\n'
        for y in range(0, self.ymax):
            map_str += str(y) + '  ' if len(str(y)) < 2 else str(y) + ' '
            for x in range(0, self.xmax):
                map_str += str(self.map[(x,y)]) + '  '
            map_str += '\n'
        print(map_str)

    def get_map_empty_cells(self) -> List[dict]:
        """Get all the map cells that are empty"""
        empty_cells = []
        for y in range(0, self.ymax):
            for x in range(0, self.xmax):
                if self.map[(x,y)] == CellType.EMPTY.value:
                    empty_cells.append( {'x':x, 'y':y} )
        return empty_cells

    def get_random_n_consecutive_empty_cells(self, n: int) -> List[dict]:
        empty_cells = get_n_consecutive_empty_cells_from_grid(n=n, grid=self.map, nb_cols=self.xmax, nb_rows=self.ymax, empty_value=CellType.EMPTY.value)
        return random.choice(empty_cells)