import logging
import os

import arcade
import arcade.gui
from arcade.gui import UIAnchorLayout, UIBoxLayout, UIFlatButton, UILabel

from src.ui.components.Radio import Radio
from src.utils import conf
from src.engine.World import World
from src.ui.views.game_view import GameView, GameMode
from src.ui.components.Counter import Counter

logger = logging.getLogger(__name__)

class MenuView(arcade.gui.UIView):

    def __init__(self):

        logger.debug(f'[{os.path.basename(__file__)}] - Initializing MenuView')
        super().__init__()
        # Arcade’s GUI module provides classes to interact with the user using buttons, labels etc...
        # Each view should have its own UIManager
        # call the add() function of UIManager to add widget to the GUI
        self.ui_manager = arcade.gui.UIManager()
        root = self.ui_manager.add( UIAnchorLayout() )
        # Layouts are containers that automatically position widgets based on the layout rules
        self.layout = root.add( UIBoxLayout( space_between=20 ) )

        self.layout.add(UILabel(text=conf['game_name'], font_size=conf['views']['menu']['title_font_size']))
        self.counter_bots = self.layout.add(Counter(text='Number of bots', min=1, max=30, value=6))
        self.counter_orbs = self.layout.add(Counter(text='Number of orbs', min=1, max=150, value=20))

        self.radio_game_mode = self.layout.add(Radio(
            text='Game mode :',
            options=[GameMode.LEARN.value, GameMode.PLAY.value, GameMode.BOTS.value],
            default=GameMode.LEARN.value
        ))
        self.radio_auto_retry = self.layout.add(Radio(
            text='Auto retry',
            options=['Yes', 'No'],
            default='Yes'
        ))

        self.start_button = self.layout.add(UIFlatButton(text='Start Game', width=200))
        self.start_button.on_click = self.start_game

    def on_show_view(self) -> None:

        arcade.set_background_color(conf['views']['menu']['background_color'])
        self.ui_manager.enable()

    def on_hide_view(self) -> None:
        self.ui_manager.disable()

    def on_draw(self):
        self.clear()
        self.ui_manager.draw()

    def start_game(self, _event):

        game_mode_chosen = GameMode(self.radio_game_mode.current_value)
        world = World(
            nb_col=conf['grid']['nb_col'], nb_row=conf['grid']['nb_row'],
            game_mode=game_mode_chosen,
            auto_retry=self.radio_auto_retry.current_value=='Yes'
        )
        world.create_orbs(quantity=self.counter_orbs.value)

        first_is_a_player = game_mode_chosen == GameMode.PLAY
        nb_snakes = self.counter_bots.value + 1 if first_is_a_player else self.counter_bots.value
        world.create_snakes(
            quantity=nb_snakes,
            first_is_a_player=first_is_a_player
        )
        game_view = GameView(
            world=world,
            game_mode=GameMode(self.radio_game_mode.current_value)
        )
        game_view.setup()
        self.window.show_view(game_view)

