import json
import random
from logging import getLogger
from typing import Tuple
import arcade

logger = getLogger(__name__)

with open('src/game_conf.json') as f:
    conf = json.load(f)


def get_random_coordinate_on_grid() -> Tuple[int, int]:
    return random.choice([i for i in range(1, conf['grid']['nb_col']+1)]), random.choice([i for i in range(1, conf['grid']['nb_row']+1)])

def is_position_inside_grid(x: int, y: int) -> bool:
    return 0 < x <= conf['grid']['nb_col'] and 0 < y <= conf['grid']['nb_row']

def position_sprite_on_grid(sprite: arcade.Sprite, x: int, y: int) -> None:
    if is_position_inside_grid(x=x, y=y):
        x_cells = conf['grid']['cell_width'] * x - (conf['grid']['cell_width'] / 2)
        x_margins = conf['grid']['margin'] * x
        sprite.center_x = x_cells + x_margins
        y_cells = conf['grid']['cell_width'] * y - (conf['grid']['cell_width'] / 2)
        y_margins = conf['grid']['margin'] * y
        sprite.center_y = y_cells + y_margins
    else:
        logger.error(f'Illegal coordinate ({x}, {y}) for grid of size {conf['grid']['nb_col']}x{conf['grid']['nb_row']}')