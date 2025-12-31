import logging
import os

import arcade

from src.utils import conf
from src.ui.views.menu_view import MenuView

logger = logging.getLogger(__name__)

WINDOW_WIDTH, WINDOW_HEIGHT = conf['views']['menu']['width'], conf['views']['menu']['height']
WINDOW_TITLE = conf['game_name']

class GameWindow(arcade.Window):

    def __init__(self, visible: bool = True):

        logger.debug(f'[{os.path.basename(__file__)}] - Initializing Arcade Window')
        super().__init__(width=WINDOW_WIDTH, height=WINDOW_HEIGHT, title=WINDOW_TITLE, center_window=True, visible=visible)
        # "activate" the MenuView
        self.show_view(MenuView())

