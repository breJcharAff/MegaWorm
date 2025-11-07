import arcade
from src.utils import conf

WINDOW_TITLE = conf['game_name']
# Window size depends on grid dimension
WINDOW_WIDTH = (conf['grid']['cell_width'] + conf['grid']['margin']) * conf['grid']['nb_col'] + conf['grid']['margin']
WINDOW_HEIGHT = (conf['grid']['cell_width'] + conf['grid']['margin']) * conf['grid']['nb_row'] + conf['grid']['margin']


class MapWindow(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):
        # Call the parent class to set up the window
        super().__init__(width=WINDOW_WIDTH, height=WINDOW_HEIGHT, title=WINDOW_TITLE, center_window=True)

    def setup(self):
        """Set up the game here. Call to restart the game."""
        pass

    def on_draw(self):
        """Render the screen."""
        # clear() method should always be called first (ensure a clean state)
        self.clear()


def main():
    """Main function"""
    window = MapWindow()
    window.setup()
    arcade.run()

if __name__ == '__main__':
    main()