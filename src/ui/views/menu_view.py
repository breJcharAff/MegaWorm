import logging
import os

import arcade
import arcade.gui

from src.engine.World import World
from src.ui.views.game_view import GameView
from src.utils import conf

logger = logging.getLogger(__name__)

class MenuView(arcade.View):

    def __init__(self):

        logger.debug(f'[{os.path.basename(__file__)}] - Initializing MenuView')
        super().__init__()
        # Arcade’s GUI module provides classes to interact with the user using buttons, labels etc...
        # Each view should have its own UIManager
        self.ui_manager = arcade.gui.UIManager()

        self.v_box = arcade.gui.UIBoxLayout()


    def on_show_view(self) -> None:

        arcade.set_background_color(conf['views']['menu']['background_color'])
        self.ui_manager.enable()

    def on_hide_view(self) -> None:
        self.ui_manager.disable()

    def on_draw(self) -> bool | None:
        self.ui_manager.draw()

    def on_key_press(self, key: int, modifiers: int) -> bool | None:

        # temporary (before implementing real menu and button "play")
        if key == arcade.key.ESCAPE:
            world = World(nb_col=conf['grid']['nb_col'], nb_row=conf['grid']['nb_row'])
            world.create_orbs(quantity=30)
            world.create_snakes(quantity=3, first_is_a_player=False)

            game_view = GameView(world=world)
            game_view.setup()
            self.window.show_view(game_view)