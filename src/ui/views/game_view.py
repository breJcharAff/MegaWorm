import logging
import os
from enum import Enum

import arcade

from src.engine.Snake import Direction
from src.engine.World import World, CellType
from src.utils import conf

# Window size depends on grid dimension
WINDOW_WIDTH = (conf['grid']['cell_width'] + conf['grid']['margin']) * conf['grid']['nb_col'] + conf['grid']['margin']
WINDOW_HEIGHT = (conf['grid']['cell_height'] + conf['grid']['margin']) * conf['grid']['nb_row'] + conf['grid']['margin']

logger = logging.getLogger(__name__)

class CellColor(Enum):
    EMPTY = conf['empty']['color']
    ORB = conf['orbs']['color']
    SNAKE = conf['snakes']['color']


class GameView(arcade.View):

    def __init__(self, world: World, debug_level: int = 0):

        logger.debug(f'[{os.path.basename(__file__)}] - Initializing GameView')
        super().__init__()
        self.window.set_size(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        self.window.center_window()

        self.elapsed_time = 0.0
        self.world = world
        self.player = None
        self.nb_row = conf['grid']['nb_row']
        self.nb_col = conf['grid']['nb_col']
        self.map = None
        self.grid_sprite_list = None
        self.orb_texture = None

        # DEBUG
        self.debug_level = debug_level
        self.grid_coordinates = []

    def setup(self):
        """Set up the game here. Call to restart the game."""
        self.create_grid_sprite_list()
        self.resync_grid_with_map()

    def on_draw(self):
        """Render the screen."""
        # clear() method should always be called first (ensure a clean state)
        self.clear()
        self.resync_grid_with_map()
        self.grid_sprite_list.draw()
        if self.debug_level >= 2:
            for text in self.grid_coordinates:
                text.draw()

    def on_update(self, delta_time):
        """Similar to on_draw(). Called 60 times per second (by default)."""
        self.elapsed_time += delta_time
        if self.elapsed_time >= conf['refresh_time']:
            self.world.update()
            self.elapsed_time = 0.0
            if self.world.game_over:
                exit()
                # TODO: DO

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed"""
        logger.debug(f'Pressed {key}')
        if key == arcade.key.UP or key == arcade.key.Z:
            self.world.set_player_direction(Direction.UP)
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.world.set_player_direction(Direction.DOWN)
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.world.set_player_direction(Direction.RIGHT)
        elif key == arcade.key.LEFT or key == arcade.key.Q:
            self.world.set_player_direction(Direction.LEFT)
        elif key == arcade.key.ESCAPE:
            from src.ui.views.menu_view import MenuView
            self.window.show_view(MenuView())

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
                if self.debug_level >= 2:
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
                else:
                    self.grid_sprite_list[pos].color = CellColor.SNAKE.value
