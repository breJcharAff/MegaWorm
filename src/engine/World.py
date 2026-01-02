import logging
import os.path
import random
from typing import List, Dict
from enum import Enum

from src.utils import conf
from src.engine.Orb import Orb
from src.engine.Snake import Snake, Direction

logger = logging.getLogger(__name__)

class CellType(Enum):
    EMPTY = 0
    ORB = 1
    SNAKE = 2

class World:

    def __init__(self, nb_col: int, nb_row: int):
        logger.debug(f'[{os.path.basename(__file__)}] : Creating empty world and map.')
        self.nb_col = nb_col
        self.nb_row = nb_row
        self.map = get_empty_map(nb_col=nb_col, nb_row=nb_row)
        self.snakes: Dict[int, Snake] = {}
        self.orbs: Dict[int, Orb] = {}
        self.game_over = False

    def create_snakes(self, quantity: int, first_is_a_player: bool = False) -> None:
        """Creates and spawns snakes (ready to play)."""
        for i in range(0, quantity):
            snake = Snake(length=conf['snakes']['length_initial'], speed=1)
            snake.positions = self.get_random_n_consecutive_empty_cells(snake.length)
            if i==0 and first_is_a_player:
                snake.set_snake_as_player()
            self.snakes[snake.id] = snake
            self.set_snake_direction_random(snake_id=snake.id)
            logger.info(f'[{os.path.basename(__file__)}] - NEW SNAKE : {snake.snake_str()}')
        self.update_map_state()

    def create_orbs(self, quantity: int) -> None:
        """Creates and spawns orbs."""
        empty_cells = self.get_map_empty_cells()
        if len(empty_cells) >= quantity:
            random_cells = random.sample(population=empty_cells, k=quantity)
            for i in range(0, quantity):
                self.create_orb(x=random_cells[i]['x'], y=random_cells[i]['y'])
            self.update_map_state()

    def create_orb(self, x: int, y: int) -> None:
        orb = Orb()
        orb.set_position(x=x, y=y)
        self.orbs[orb.id] = orb
        logger.debug(f'[{os.path.basename(__file__)}] - NEW ORB at x={orb.x}, y={orb.y}')

    def update_map_state(self) -> None:
        """Refresh the World.map dictionary to reflect latest state."""
        self.map = get_empty_map(nb_col=self.nb_col, nb_row=self.nb_row)
        for orb_id, orb in self.orbs.items():
            self.map[(orb.x, orb.y)] = CellType.ORB
        for snake_id, snake in self.snakes.items():
            for cell in snake.positions:
                x, y = cell['x'], cell['y']
                self.map[(x,y)] = CellType.SNAKE

    def update(self) -> None:
        """Called every ticks"""

        self.set_bots_direction()
        self.update_map_state()

        dead_snake_ids = []

        for snake_id, snake in self.snakes.items():

            new_head = self.snakes[snake_id].next_position()
            x = new_head['x']
            y = new_head['y']

            if self.is_collision(x=x, y=y, snake_id=snake_id):
                logging.info(f'Snake {snake_id} collided and died.')
                dead_snake_ids.append(snake_id)
                if snake.is_main_snake:
                    self.game_over = True
                    return
                continue


            if self.map[(x,y)] == CellType.ORB:
                self.snakes[snake_id].move(grow=True)
                self.snakes[snake_id].score += 1
                self.create_orbs(quantity=1)
                self.remove_orb_at_position(x=x, y=y)
                logging.debug(f'Snake {snake_id} ate an orb')

            else:
                self.snakes[snake_id].move(grow=False)

            self.map[(x, y)] = self.snakes[snake_id].id

        self.kill_snakes(snake_ids=dead_snake_ids)
        self.update_map_state()

    def get_state(self) -> dict:
        self.update_map_state()
        return {
            'map': self.map,
            'snakes': self.snakes,
            'orbs': self.orbs
        }

    def show_map_in_console(self) -> None:
        """used for debugging"""
        map_str = '   ' + ''.join(str(i)+'  ' if len(str(i))<2 else str(i)+' ' for i in range(0, self.nb_col)) + '\n'
        for y in range(0, self.nb_row):
            map_str += str(y) + '  ' if len(str(y)) < 2 else str(y) + ' '
            for x in range(0, self.nb_col):
                map_str += str(self.map[(x,y)].value) + '  '
            map_str += '\n'
        print(map_str)

    def get_map_empty_cells(self) -> List[dict]:
        """Get all the map cells that are empty"""
        empty_cells = []
        for y in range(0, self.nb_row):
            for x in range(0, self.nb_col):
                if self.map[(x,y)] == CellType.EMPTY:
                    empty_cells.append( {'x':x, 'y':y} )
        return empty_cells

    def get_random_n_consecutive_empty_cells(self, n: int) -> List[dict]:
        empty_cells = get_n_consecutive_empty_cells_from_grid(n=n, grid=self.map, nb_cols=self.nb_col, nb_rows=self.nb_row, empty_value=CellType.EMPTY)
        return random.choice(empty_cells)

    def set_snake_direction(self, snake_id: int, direction: Direction) -> bool:
        if self.snakes[snake_id].can_change_direction(direction):
            self.snakes[snake_id].set_direction(direction)
            return True
        return False

    def set_player_direction(self, direction: Direction) -> bool:
        """Called from Arcade (keyboard input), set the direction of the Snake that is a player"""
        player = self.get_snake_player()
        return self.set_snake_direction(snake_id=player.id, direction=direction)

    def set_bots_direction(self) -> None:
        """Set random new directions for all bots."""
        for snake_id, snake in self.snakes.items():
            if snake.is_bot:
                self.set_snake_direction_random(snake_id=snake_id)

    def set_snake_direction_random(self, snake_id: int) -> None:
        """Set a random new direction for the snake (that should not collide)."""
        direction = self.get_random_direction_that_does_not_collide(snake_id=snake_id)
        self.set_snake_direction(snake_id=snake_id, direction=direction)

    def get_random_direction_that_does_not_collide(self, snake_id: int) -> Direction:
        """Get a random authorized direction that will not kill the snake (last one otherwise)."""
        authorized = self.snakes[snake_id].authorized_direction()
        directions = random.sample(authorized, k=len(authorized))
        for direction in directions:
            new_head = self.snakes[snake_id].next_position(direction=direction)
            if not self.is_collision(x=new_head['x'], y=new_head['y'], snake_id=snake_id):
                return direction
        return directions[0]

    def is_collision(self, x: int, y: int, snake_id: int) -> bool:
        """Checks if coordinates is a wall or another snake."""
        if not self.is_inside_map(x=x, y=y):
            return True
        if self.map[(x,y)] == CellType.SNAKE and self.get_snake_at_position(x=x, y=y).id != snake_id:
            return True
        return False

    def get_snake_at_position(self, x: int, y: int) -> Snake | None:
        for snake_id, snake in self.snakes.items():
            for cell in snake.positions:
                if cell['x'] == x and cell['y'] == y:
                    return snake

    def is_inside_map(self, x: int, y: int) -> bool:
        return (0 <= x < self.nb_col) and (0 <= y < self.nb_row)

    def get_snake_player(self) -> Snake:
        for snake_id, snake in self.snakes.items():
            if not snake.is_bot:
                return snake

    def get_main_snake(self) -> Snake:
        """The first snake is the bot that learns (and which matters)."""
        return next(iter(self.snakes.values()))

    def remove_orb_at_position(self, x: int, y: int) -> bool:
        for orb_id, orb in self.orbs.items():
            if orb.x == x and orb.y == y:
                del self.orbs[orb_id]
                return True
        return False

    def kill_snakes(self, snake_ids: List[int]):
        """Transform the body of all dead snakes into orbs and remove them from the game."""
        for snake_id, snake in self.snakes.items():
            if snake_id in snake_ids:
                self.transform_snake_into_orb(snake_id=snake_id)
        self.snakes = {snake_id: snake for snake_id, snake in self.snakes.items() if snake_id not in snake_ids}

    def transform_snake_into_orb(self, snake_id: int):
        """Transform the snake body into orbs."""
        for cell in self.snakes[snake_id].positions:
            self.create_orb(x=cell['x'], y=cell['y'])

def get_n_consecutive_empty_cells_from_grid(n: int, grid: dict, nb_cols: int, nb_rows: int, empty_value: CellType) -> List[List[dict]] | None:
    """get a 3-dimensional list where the 2nd degree lists represent every possible 'n' cells that are both aligned (vertic. & horiz.) AND empty
        Example for n=3, if the output is
            [ [ {x:0, y:2}, (x:0, y:3), (x:0, y:4)  ] ]
        ...this would mean that the only 3 cells of the grid that are both aligned and empty are the ones located at these coordinates.
    """
    is_a_valid_grid = isinstance(grid, dict)
    if is_a_valid_grid and len(grid) > 0:
        is_a_valid_grid = isinstance(next(iter(grid.keys())), tuple)
    if not is_a_valid_grid:
        logger.error(f'Arg grid must be a dictionary mapping tuples to integers (Ex: (2,3): 4.')
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
    for row in range(0, nb_row):
        for col in range(0, nb_col):
            map[(col, row)] = CellType.EMPTY
    return map

