import logging
import os.path
import pickle
import random
from collections import Counter
from typing import List, Dict, Tuple
from enum import Enum

from src.utils import conf
from src.engine.Orb import Orb
from src.engine.Snake import Snake, Direction

logger = logging.getLogger(__name__)

FILE_AGENT = f'agent_v{conf['AI']['version']}.qtable'

class GameMode(Enum):
    LEARN = 'learn'
    PLAY  = 'play (no learning)'
    BOTS  = 'full bots (no learning)'

class CellType(Enum):
    EMPTY      = 0
    ORB        = 1
    SNAKE      = 2
    MAIN_SNAKE = 3 # player or main bot

class Reward(Enum):
    DEFAULT   = -1
    COLLISION = -500
    ORB       = 30

class World:

    def __init__(self, nb_col: int, nb_row: int, game_mode: GameMode, auto_retry: bool):

        logger.debug(f'[{os.path.basename(__file__)}] : Creating empty world and map.')
        self.nb_col = nb_col
        self.nb_row = nb_row
        self.game_over = False
        self.game_mode = game_mode
        self.auto_retry = auto_retry
        self.score_history = []
        # saves the main snake q_table between tries (the snake is deleted when it dies)
        self.last_q_table = {}
        self.settings = {
            'nb_snakes': 0,
            'nb_orbs': 0
        }
        self.map = get_empty_map(nb_col=nb_col, nb_row=nb_row)
        self.snakes: Dict[int, Snake] = {}
        self.orbs: Dict[int, Orb] = {}

    def create_snakes(self, quantity: int, first_is_a_player: bool = False, change_settings: bool = True) -> None:
        """Creates and spawns snakes (ready to play)."""
        logger.info(f'---------------- CREATING {quantity} SNAKES ----------------')
        if change_settings:
            self.settings['nb_snakes'] += quantity
        for i in range(quantity):
            snake = Snake(length=conf['snakes']['length_initial'], speed=1)
            snake.positions = self.get_random_n_consecutive_empty_cells(snake.length)
            self.snakes[snake.id] = snake
            self.update_map_state_with_snake_positions(snake_id=snake.id)
            if i==0:
                if first_is_a_player:
                    snake.set_snake_as_player()
                    self.set_direction_snake_random(snake_id=snake.id, can_collide=False)
                else:
                    snake.is_main_snake = True
                    if self.game_mode == GameMode.LEARN:
                        snake.state = self.get_state_snake(snake_id=snake.id)
                        snake.q_table = self.last_q_table
            logger.info(f'[{os.path.basename(__file__)}] - NEW SNAKE : {snake.snake_ai_str() if snake.is_main_snake else snake.snake_str()}')
        self.set_direction_bots(game_mode=self.game_mode)

        if change_settings and self.game_mode == GameMode.LEARN:
            self.retrieve_history()

    def create_orbs(self, quantity: int, change_settings: bool = True) -> None:
        """Creates and spawns orbs."""
        logger.info(f'---------------- CREATING {quantity} ORBS ----------------')
        if change_settings:
            self.settings['nb_orbs'] += quantity
        empty_cells = self.get_map_empty_cells()
        if len(empty_cells) >= quantity:
            random_cells = random.sample(population=empty_cells, k=quantity)
            for i in range(quantity):
                self.create_orb(x=random_cells[i]['x'], y=random_cells[i]['y'])

    def create_orb(self, x: int, y: int) -> None:
        """Creates one orb at position (x,y)"""
        orb = Orb()
        orb.set_position(x=x, y=y)
        self.orbs[orb.id] = orb
        self.update_map_state_with_orb_position(orb_id=orb.id)
        logger.debug(f'[{os.path.basename(__file__)}] - NEW ORB at x={orb.x}, y={orb.y}')

    def update(self) -> None:
        """Called every ticks"""

        self.update_map_state()

        self.set_direction_bots(game_mode=self.game_mode)

        reward_main_snake = None
        is_main_snake_alive = True

        for snake_id, snake in self.snakes.items():

            new_head = self.snakes[snake_id].next_position()
            x = new_head['x']
            y = new_head['y']

            if self.is_collision(x=x, y=y, snake_id=snake_id):
                logging.info(f'Snake {snake_id} collided and died.')
                reward = Reward.COLLISION
                snake.is_alive = False
                if snake.is_main_snake:
                    is_main_snake_alive = False

            elif self.map[(x,y)] == CellType.ORB:
                reward = Reward.ORB
                self.snakes[snake_id].move(grow=True)
                logging.debug(f'Snake {snake_id} ate an orb')

            else:
                reward = Reward.DEFAULT
                self.snakes[snake_id].move(grow=False)

            self.update_map_state()

            self.snakes[snake_id].score += reward.value
            self.snakes[snake_id].iteration += 1
            if snake.is_main_snake:
                reward_main_snake = reward

        self.update_q_table(reward=reward_main_snake)
        if not is_main_snake_alive:
            self.handle_game_over()
        self.kill_snakes()
        self.kill_orbs()
        self.update_map_state()

    # ----------------- MAP ----------------- #

    def update_map_state(self) -> None:
        """Refresh the World.map dictionary to reflect latest state."""
        self.map = get_empty_map(nb_col=self.nb_col, nb_row=self.nb_row)
        for orb_id, _orb in self.orbs.items():
            self.update_map_state_with_orb_position(orb_id=orb_id)
        for snake_id, _snake in self.snakes.items():
            self.update_map_state_with_snake_positions(snake_id=snake_id)

    def update_map_state_with_snake_positions(self, snake_id: int) -> None:
        #FIXME: DOES NOT SET MAP CELL BACK TO EMPTY WHEN SNAKE MOVES (without eating)
        #FIXME: EITHER USE update_map_state() instead or pass as a param the old cells occupied by the snake (before moving)
        for cell in self.snakes[snake_id].positions:
            x, y = cell['x'], cell['y']
            if self.snakes[snake_id].is_main_snake:
                self.map[(x, y)] = CellType.MAIN_SNAKE
            else:
                self.map[(x, y)] = CellType.SNAKE

    def update_map_state_with_orb_position(self, orb_id: int) -> None:
        x, y = self.orbs[orb_id].x, self.orbs[orb_id].y
        self.map[(x, y)] = CellType.ORB

    def get_map_str(self) -> str:
        """used for debugging"""
        map_str = '   ' + ''.join(str(i)+'  ' if len(str(i))<2 else str(i)+' ' for i in range(0, self.nb_col)) + '\n'
        for y in range(0, self.nb_row):
            map_str += str(y) + '  ' if len(str(y)) < 2 else str(y) + ' '
            for x in range(0, self.nb_col):
                map_str += str(self.map[(x,y)].value) + '  '
            map_str += '\n'
        return map_str

    def show_map_in_console(self) -> None:
        """used for debugging"""
        print(self.get_map_str())

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

    # ----------------- DIRECTION ----------------- #

    def set_direction_snake(self, snake_id: int, direction: Direction) -> bool:
        if self.snakes[snake_id].can_change_direction(direction):
            self.snakes[snake_id].set_direction(direction)
            return True
        return False

    def set_direction_player(self, direction: Direction) -> bool:
        """Called from Arcade (keyboard input), set the direction of the Snake that is a player"""
        player = self.get_snake_player()
        return self.set_direction_snake(snake_id=player.id, direction=direction)

    def set_direction_bots(self, game_mode: GameMode) -> None:
        """For all bots, set a new random direction that should not collide.
        If the GameMode is LEARN, the main bot get a direction based on its q_table."""
        for snake_id, snake in self.snakes.items():
            if snake.is_main_snake and game_mode == GameMode.LEARN:
                if random.random() > snake.exploration and snake.state in snake.q_table:
                    self.set_direction_snake_best_from_q_table(snake_id=snake_id)
                else:
                    snake.exploration *= 0.99
                    self.set_direction_snake_random(snake_id=snake_id, can_collide=True)
            elif snake.is_bot:
                self.set_direction_snake_random(snake_id=snake_id, can_collide=False)

    def set_direction_snake_random(self, snake_id: int, can_collide: bool) -> None:
        """Set a random new direction for the snake.
        If can_collide is False, the snake will, if possible, not chose a direction that would collide."""
        if can_collide:
            direction = self.get_direction_authorized_random(snake_id=snake_id)
        else:
            direction = self.get_direction_authorized_random_that_does_not_collide(snake_id=snake_id)
        self.set_direction_snake(snake_id=snake_id, direction=direction)

    def get_direction_authorized_random(self, snake_id: int) -> Direction:
        """Get one random authorized direction for the Snake"""
        authorized = self.snakes[snake_id].authorized_direction()
        return random.choice(authorized)

    def get_directions_authorized_shuffled(self, snake_id: int) -> List[Direction]:
        """Get all authorized direction for the Snake, shuffled."""
        authorized = self.snakes[snake_id].authorized_direction()
        return random.sample(authorized, k=len(authorized))

    def get_direction_authorized_random_that_does_not_collide(self, snake_id: int) -> Direction:
        """Get a random authorized direction that will not kill the snake (last one otherwise)."""
        directions = self.get_directions_authorized_shuffled(snake_id=snake_id)
        for direction in directions:
            new_head = self.snakes[snake_id].next_position(direction=direction)
            if not self.is_collision(x=new_head['x'], y=new_head['y'], snake_id=snake_id):
                return direction
        return directions[0]

    def set_direction_snake_best_from_q_table(self, snake_id: int):
        """Look up (in the q_table) the direction with the best reward and set it to the snake."""
        snake = self.snakes[snake_id]
        state = snake.q_table[snake.state]
        action = max(state, key=state.get)
        #FIXME: set_snake_direction() can prevent the snake from changing direction (if not authorized)
        self.set_direction_snake(snake_id=snake_id, direction=Direction[action])

    # ----------------- AI ----------------- #

    def save_q_table(self) -> None:
        logger.warning(f'--------- SAVING Q_TABLE ({len(self.last_q_table)}) + '
                    f'SCORE HISTORY ({len(self.score_history)}) TO {FILE_AGENT} ---------')
        with open(FILE_AGENT, 'wb') as file:
            pickle.dump((self.last_q_table, self.score_history), file)

    def load_q_table(self) -> None:
        if os.path.exists(FILE_AGENT):
            main_snake = self.get_main_snake()
            with open(FILE_AGENT, 'rb') as file:
                main_snake.q_table, self.score_history = pickle.load(file)
            logger.warning(f'--------- LOADING Q_TABLE ({len(main_snake.q_table)}) + '
                           f'SCORE HISTORY ({len(self.score_history)}) FROM {FILE_AGENT} ---------')
        else:
            logger.warning(f'{FILE_AGENT} not found: no QTable and score history.')

    def update_q_table(self, reward: Reward):
        """Updates the Snake q_table and state based on the direction/action it chose."""
        main_snake = self.get_main_snake()
        next_state = self.get_state_snake(snake_id=main_snake.id)
        action_performed = main_snake.direction.name

        if main_snake.state not in main_snake.q_table:
            main_snake.q_table[main_snake.state] = {'UP': 0, 'RIGHT': 0, 'DOWN': 0, 'LEFT': 0}
        if next_state not in main_snake.q_table:
            main_snake.q_table[next_state] = {'UP': 0, 'RIGHT': 0, 'DOWN': 0, 'LEFT': 0}

        # Q(s, a) += Q(s, a) + alpha * [r + gamma * max Q(s') - Q(s, a)]
        delta = main_snake.learning_rate * (
                reward.value
                + main_snake.discount_factor
                * max(main_snake.q_table[next_state].values()) - main_snake.q_table[main_snake.state][action_performed]
        )
        main_snake.q_table[main_snake.state][action_performed] += delta
        main_snake.state = next_state

    def get_state_snake(self, snake_id):
        """
        Calculate a representation of the environment (what the bot sees)
        for each 4 directions: the number of empty cells to the nearest...
        (
            top, right, bottom, left -> ... orb (=goal)
            top, right, bottom, left -> ... collision (wall or snake or exit map)
        )
        LIMITED TO 'Snake.radar_nb_cells' CELLS (too many possibilities otherwise)
        if no orbs or collision within 'Snake.radar_nb_cells' cells in the given
        direction, value is set to 'Snake.radar_nb_cells' (the max).
        """
        snake = self.snakes[snake_id]
        position_head = snake.positions[-1]['x'], snake.positions[-1]['y']

        state = { # Possible values = {-1, 0, 1, 2, 3} (where -1 = the snake is on the same cell as the orb and 3 = didn't find any orb in this direction)
            'orb':       { Direction.UP: -1, Direction.RIGHT: -1, Direction.DOWN: -1, Direction.LEFT: -1 },
            'collision': { Direction.UP: 0, Direction.RIGHT: 0, Direction.DOWN: 0, Direction.LEFT: 0 }
        } # for 'collision' the minimum is 0 since the snake has not / cannot move inside a 'collision' square
        final_state = {
            'orb':       { Direction.UP: None, Direction.RIGHT: None, Direction.DOWN: None, Direction.LEFT: None },
            'collision': { Direction.UP: None, Direction.RIGHT: None, Direction.DOWN: None, Direction.LEFT: None }
        }

        for nb_move in range(0, snake.radar_nb_cells+1): #+1 since we first check the current position (no move)

            for direction in list(Direction):

                x, y = get_new_position(initial_position=position_head, direction=direction, nb_of_moves=nb_move)
                found_orb       = final_state['orb'][direction] is not None
                found_collision = final_state['collision'][direction] is not None

                if self.is_inside_map(x=x, y=y):
                    if self.map[(x,y)] in (CellType.EMPTY, CellType.MAIN_SNAKE):
                        state['orb'][direction] += 1
                        state['collision'][direction] += 1
                    elif self.map[(x,y)] == CellType.ORB:
                        if not found_orb:
                            # The snake can be on the same cell as an orb!
                            # in this case, it's a new state that is '-1'
                            # with the associated high reward for orb,
                            # it should incite snake to capture more / look more for this exacte state
                            final_state['orb'][direction] = nb_move-1
                        state['collision'][direction] += 1
                    elif self.map[(x,y)] == CellType.SNAKE:
                        if not found_collision:
                            # the snake will never go to a 'collision' square
                            # so the snake has not physically moved to the collision square.
                            # if reward = collision and current nb_move = 1 for direction (0 = impossible)
                            # it will 'know' this direction is bad
                            final_state['collision'][direction] = nb_move-1
                        state['orb'][direction] += 1
                else:
                    if not found_orb:
                        final_state['orb'][direction] = snake.radar_nb_cells  # max (could not find orb outside map)
                    if not found_collision:
                        final_state['collision'][direction] = nb_move-1

        # If no orb / collision found in the given direction, set the value to the max (radar range)
        for nb_move in range(0, snake.radar_nb_cells):
            for direction in list(Direction):
                for to_check in ('collision', 'orb'):
                    if final_state[to_check][direction] is None:
                        final_state[to_check][direction] = snake.radar_nb_cells

        return (
            final_state['orb'][Direction.UP],       final_state['orb'][Direction.RIGHT],       final_state['orb'][Direction.DOWN],       final_state['orb'][Direction.LEFT],
            final_state['collision'][Direction.UP], final_state['collision'][Direction.RIGHT], final_state['collision'][Direction.DOWN], final_state['collision'][Direction.LEFT]
        )

    def retrieve_history(self):
        main_snake = self.get_main_snake()
        if main_snake is None:
            raise Exception('Main snake should be created first')
        if main_snake.q_table:
            raise Exception('retrieve_history() would erase the existing (in memory) snake history.')

        self.load_q_table()

    # ----------------- GAME-OVER ----------------- #

    def is_collision(self, x: int, y: int, snake_id: int) -> bool:
        """Checks if coordinates is a wall or another snake."""
        if not self.is_inside_map(x=x, y=y):
            return True
        if self.map[(x,y)] in (CellType.SNAKE, CellType.MAIN_SNAKE) and self.get_snake_at_position(x=x, y=y).id != snake_id:
            return True
        return False

    def kill_snakes(self):
        """Transform the body of all dead snakes into orbs and remove them from the game."""
        for snake_id, snake in self.snakes.items():
            if not snake.is_alive:
                self.transform_snake_into_orb(snake_id=snake_id)
        self.snakes = {snake_id: snake for snake_id, snake in self.snakes.items() if snake.is_alive}

    def kill_orbs(self):
        """Remove 'dead' (eaten) orbs from the game and spawn one new"""
        for orb_id, orb in self.orbs.items():
            if not orb.is_alive:
                self.create_orbs(quantity=1, change_settings=False)
        self.orbs = {orb_id: orb for orb_id, orb in self.orbs.items() if orb.is_alive}

    def transform_snake_into_orb(self, snake_id: int):
        """Transform the snake body into orbs."""
        for cell in self.snakes[snake_id].positions:
            self.create_orb(x=cell['x'], y=cell['y'])

    def handle_game_over(self):
        self.game_over = True
        main_snake = self.get_main_snake()
        self.score_history.append(main_snake.score)
        self.last_q_table |= main_snake.q_table
        if self.auto_retry:
            self.reset_world()

    def reset_world(self) -> None:
        """Put the World in the same state as it was when instantiating it."""
        logger.info('---------------- RESETTING WORLD ----------------')
        self.map = get_empty_map(nb_col=self.nb_col, nb_row=self.nb_row)
        self.snakes: Dict[int, Snake] = {}
        self.orbs: Dict[int, Orb] = {}
        self.game_over = False

        self.create_orbs(
            quantity=self.settings['nb_orbs'],
            change_settings=False
        )
        self.create_snakes(
            quantity=self.settings['nb_snakes'],
            first_is_a_player=self.game_mode==GameMode.PLAY,
            change_settings=False
        )

    # ----------------- OTHERS ----------------- #

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

    def get_main_snake(self) -> Snake | None:
        """The main snake is the bot that learns (and which matters)."""
        for snake in self.snakes.values():
            if snake.is_main_snake:
                return snake

    def remove_orb_at_position(self, x: int, y: int) -> bool:
        for orb_id, orb in self.orbs.items():
            if orb.x == x and orb.y == y:
                del self.orbs[orb_id]
                return True
        return False

    def get_state(self) -> dict:
        self.update_map_state()
        return {
            'map': self.map,
            'snakes': self.snakes,
            'orbs': self.orbs
        }

    def get_snakes_str(self) -> str:
        """For debugging"""
        output = ''
        for snake in self.snakes.values():
            if snake.is_main_snake:
                output += snake.snake_ai_str()
            else:
                output += snake.snake_str()
        return output

    def show_entire_world_in_console(self) -> None:
        """For debugging"""
        logger.info(f'\n\n\n----------------- ENTIRE WORLD STATE -----------------\n\n')
        print(
            f'Dimensions: {self.nb_col} x {self.nb_row}\n'
            f'Game Mode : {self.game_mode}\n'
            f'Auto retry: {self.auto_retry}\n'
            f'Game Over : {self.game_over}\n'
            f'Settings  : {self.settings}'
        )
        print(f'\n----------- SNAKES {len(self.snakes)} -----------\n')
        print(self.get_snakes_str())
        print(f'\n----------- ORBS   {len(self.orbs)} -----------\n')
        for orb in self.orbs.values():
            print(f'ID={orb.id} - x={orb.x}, y={orb.y}')
        self.show_map_in_console()

    def get_ai_info_text(self) -> str:
        main_snake = self.get_main_snake()
        return (f'Loop: {main_snake.iteration} - Score: {main_snake.score} - '
                f'Exploration: {round(main_snake.exploration, 3)} - QTable: {len(main_snake.q_table)}')


def get_empty_map(nb_col: int, nb_row: int) -> dict:
    map = {}
    for row in range(0, nb_row):
        for col in range(0, nb_col):
            map[(col, row)] = CellType.EMPTY
    return map

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

    # consecutive_col[x] -> vertical streak for column x
    consecutive_col = [[] for _ in range(nb_cols)]

    for y in range(nb_rows):
        # -> horizontal streak row y (current)
        consecutive_row = []

        for x in range(nb_cols):
            cell = grid[(x, y)]
            is_empty = cell == empty_value

            if is_empty:
                coord = {'x': x, 'y': y}
                # ROW
                consecutive_row.append(coord)
                if len(consecutive_row) >= n:
                    # -> last n elements = valid streak
                    consecutive.append(consecutive_row[-n:])
                # COL
                consecutive_col[x].append(coord)
                if len(consecutive_col[x]) >= n:
                    # -> last n elements = valid streak
                    consecutive.append(consecutive_col[x][-n:])

            else:
                # Not empty: reset streaks
                consecutive_row = []
                consecutive_col[x] = []

    no_duplicate = []
    for element in consecutive:
        if element not in no_duplicate:
            no_duplicate.append(element)

    return no_duplicate

def get_new_position(initial_position: Tuple[int, int], direction: Direction, nb_of_moves: int) -> Tuple[int, int]:
    if nb_of_moves < 1:
        return initial_position
    target_position = Counter({'x': initial_position[0], 'y': initial_position[1]})
    for i in range(nb_of_moves):
        target_position.update(direction.value)
    return target_position['x'], target_position['y']
