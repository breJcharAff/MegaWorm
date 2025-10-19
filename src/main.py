from typing import List, Any, Optional
import arcade
from arcade import SpriteList, Sprite
from arcade.types import Color
from src.utils import conf, position_sprite_on_grid, get_random_coordinate_on_grid

WINDOW_TITLE = conf['game_name']
# Window size depends on grid dimension
WINDOW_WIDTH = (conf['grid']['cell_width'] + conf['grid']['margin']) * conf['grid']['nb_col'] + conf['grid']['margin']
WINDOW_HEIGHT = (conf['grid']['cell_width'] + conf['grid']['margin']) * conf['grid']['nb_row'] + conf['grid']['margin']

def create_snakes() -> SpriteList[Sprite]:
    snake_texture = arcade.load_texture('src/images/snake_head_green.png')
    snake_sprite = arcade.Sprite(path_or_texture=snake_texture, scale=conf['snakes']['scaling'])
    position_sprite_on_grid(sprite=snake_sprite, x=1, y=1)
    snakes = arcade.SpriteList()
    snakes.append(snake_sprite)
    return snakes

def create_orbs(number_of_orbs: int) -> SpriteList[Sprite]:
    orbs = arcade.SpriteList(use_spatial_hash=True)
    available_orbs_colors = ['blue', 'green', 'yellow']
    for i in range(0, number_of_orbs):
        orb_color = available_orbs_colors[ i % len(available_orbs_colors) ]
        filename = 'src/images/orb_' + orb_color + '.png'
        orb = arcade.Sprite(path_or_texture=filename, scale=conf['orbs']['scaling'])
        x, y = get_random_coordinate_on_grid()
        position_sprite_on_grid(sprite=orb, x=x, y=y)
        orbs.append(orb)
    return orbs

def create_grid_sprites(grid_width: int, grid_height: int, grid_margin: int) -> List[List[arcade.Sprite]]:
    """Creates a 2-dimensional grid of Sprite to represent the map's grid."""
    grid_sprites_two_dimensions = []
    for row in range(conf['grid']['nb_row']):
        grid_sprites_two_dimensions.append( [] )
        for column in range(conf['grid']['nb_col']):
            x = column * (grid_width + grid_margin) + (grid_width / 2 + grid_margin)
            y = row * (grid_height + grid_margin) + (grid_height / 2 + grid_margin)
            sprite = arcade.SpriteSolidColor(grid_width, grid_height, Color(20, 20, 19, 255))
            sprite.center_x = x
            sprite.center_y = y
            grid_sprites_two_dimensions[row].append(sprite)
    return grid_sprites_two_dimensions

def two_dim_to_one_dim_list(two_dim_list: List[List[Any]], arcade_list: Optional[bool] = False) -> List[Any] | arcade.SpriteList[Any]:
    """Converts any list of list (2 dimensions) to a simple list (1 dimension)."""
    if arcade_list:
        one_dim_list = arcade.SpriteList()
    else:
        one_dim_list = []
    if isinstance(two_dim_list, list):
        for inner_list in two_dim_list:
            if isinstance(inner_list, list):
                for element in inner_list:
                    one_dim_list.append( element )
    return one_dim_list

class MapWindow(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):
        # Call the parent class to set up the window
        super().__init__(width=WINDOW_WIDTH, height=WINDOW_HEIGHT, title=WINDOW_TITLE, center_window=True)
        self.snakes = create_snakes()
        self.orbs = create_orbs(number_of_orbs=10)
        self.grid_sprites_two_dimensions = create_grid_sprites(grid_width=conf['grid']['cell_width'],
                                                               grid_height=conf['grid']['cell_width'],
                                                               grid_margin=conf['grid']['margin'])
        self.grid_sprites_one_dimension = two_dim_to_one_dim_list(two_dim_list=self.grid_sprites_two_dimensions, arcade_list=True)


    def setup(self):
        """Set up the game here. Call to restart the game."""
        pass

    def on_draw(self):
        """Render the screen."""
        # clear() method should always be called first (ensure a clean state)
        self.clear()

        self.grid_sprites_one_dimension.draw()
        self.snakes.draw()
        self.orbs.draw()


def main():
    """Main function"""
    window = MapWindow()
    window.setup()
    arcade.run()


if __name__ == '__main__':
    print(f'Welcome to {conf['game_name']}!')
    main()