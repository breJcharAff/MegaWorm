import arcade
from arcade.types import Color

GAME_NAME = 'MegaWorm'
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = GAME_NAME

class MapWindow(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):
        # Call the parent class to set up the window
        super().__init__(width=WINDOW_WIDTH, height=WINDOW_HEIGHT, title=WINDOW_TITLE, center_window=True)
        self.background_color = Color(20, 20, 19, 255)

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
    print(f'Welcome to {GAME_NAME}!')
    main()