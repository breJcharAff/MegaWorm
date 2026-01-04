import logging
import os
from enum import Enum

import arcade
import matplotlib.pyplot as plt

from src.engine.Snake import Direction
from src.engine.World import World, CellType, GameMode
from src.utils import conf

# Window size depends on grid dimension
WINDOW_WIDTH = (conf['grid']['cell_width'] + conf['grid']['margin']) * conf['grid']['nb_col'] + conf['grid']['margin']
WINDOW_HEIGHT = (conf['grid']['cell_height'] + conf['grid']['margin']) * conf['grid']['nb_row'] + conf['grid']['margin']

logger = logging.getLogger(__name__)

class CellColor(Enum):
    EMPTY = conf['empty']['color']
    ORB = conf['orbs']['color']
    SNAKE = conf['snakes']['color']
    MAIN_SNAKE = conf['snakes']['main']['color']

class GameView(arcade.View):

    def __init__(self, world: World, game_mode: GameMode):

        logger.debug(f'[{os.path.basename(__file__)}] - Initializing GameView')
        super().__init__()
        self.window.set_size(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        self.window.center_window()

        self.refresh_time = conf['refresh_time']
        self.elapsed_time = 0.0
        self.world = world
        self.game_mode = game_mode
        self.nb_row = conf['grid']['nb_row']
        self.nb_col = conf['grid']['nb_col']
        self.map = None
        self.grid_sprite_list = None
        self.orb_texture = None
        self.ai_info_text = None

        # DEBUG
        self.grid_coordinates = []

    def setup(self):
        """Set up the game here. Call to restart the game."""
        self.create_grid_sprite_list()
        self.resync_grid_with_map()
        self.ai_info_text = arcade.Text(text=self.world.get_ai_info_text(), x=7, y=7, color=(255, 255, 255, 255))

    def on_draw(self):
        """Render the screen."""
        # clear() method should always be called first (ensure a clean state)
        self.clear()
        self.resync_grid_with_map()
        self.grid_sprite_list.draw()
        self.ai_info_text.draw()
        if self.window.debug_level >= 2:
            for text in self.grid_coordinates:
                text.draw()

    def on_update(self, delta_time):
        """Similar to on_draw(). Called 60 times per second (by default)."""
        self.elapsed_time += delta_time
        if self.elapsed_time >= self.refresh_time and not self.world.game_over:
            self.world.update()
            if not self.world.game_over:
                self.ai_info_text.text = self.world.get_ai_info_text()
            self.elapsed_time = 0.0

    def on_close(self) -> None:
        self.world.save_q_table()
        plt.plot(self.world.score_history)
        plt.show()

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed"""

        if self.game_mode == GameMode.PLAY:
            if key == arcade.key.UP or key == arcade.key.Z:
                self.world.set_direction_player(Direction.UP)
            elif key == arcade.key.DOWN or key == arcade.key.S:
                self.world.set_direction_player(Direction.DOWN)
            elif key == arcade.key.RIGHT or key == arcade.key.D:
                self.world.set_direction_player(Direction.RIGHT)
            elif key == arcade.key.LEFT or key == arcade.key.Q:
                self.world.set_direction_player(Direction.LEFT)

        if self.game_mode == GameMode.LEARN:
            if key == arcade.key.E:
                self.world.get_main_snake().exploration += 0.05

        if key == arcade.key.R:
            self.world.reset_world()

        elif key == arcade.key.NUM_ADD:
            self.refresh_time *= 1.05
        elif key == arcade.key.NUM_SUBTRACT:
            self.refresh_time *= 0.95
            logger.info(f'{self.refresh_time=}')

    def create_grid_sprite_list(self) -> None:
        """Creates the grid representing the map (similar to World.map)
        but filled with Sprites aimed to be displayed."""
        self.grid_sprite_list = arcade.SpriteList()
        for row in range(self.nb_row):
            for col in range(self.nb_col):
                x = col * conf['grid']['cell_width'] + (conf['grid']['cell_width'] / 2) + conf['grid']['margin'] * (col - 1)
                y = row * conf['grid']['cell_height'] + (conf['grid']['cell_height'] / 2) + conf['grid']['margin'] * (row - 1)
                sprite = arcade.SpriteSolidColor(width=conf['grid']['cell_width'], height=conf['grid']['cell_width'],
                                                 color=CellColor.EMPTY.value)
                sprite.center_x = x
                sprite.center_y = y
                self.grid_sprite_list.append(sprite)
                if self.window.debug_level >= 2:
                    self.grid_coordinates.append(
                        arcade.Text(f'{col}, {row}', x=x, y=y, color=(255, 0, 0, 255), font_size=8))

    def resync_grid_with_map(self) -> None:
        """Set the color of every Sprite/square of self.grid_sprite_list based on
        World.map which knows if a square (coordinate x,y) is empty, an orb or a snake."""
        self.map = self.world.get_state()['map']
        for row in range(self.nb_row):
            for col in range(self.nb_col):
                pos = row * self.nb_col + col
                if self.map[(col, row)] == CellType.EMPTY:
                    self.grid_sprite_list[pos].color = CellColor.EMPTY.value
                elif self.map[(col, row)] == CellType.ORB:
                    self.grid_sprite_list[pos].color = CellColor.ORB.value
                elif self.map[(col, row)] == CellType.SNAKE:
                    self.grid_sprite_list[pos].color = CellColor.SNAKE.value
                else:
                    self.grid_sprite_list[pos].color = CellColor.MAIN_SNAKE.value
