import argparse

import arcade

from src.engine.World import World
from src.ui.arcade_view import MapWindow
from src.utils import conf, setup_logging


def main(debug_level: int) -> None:

    setup_logging(level=debug_level)

    world = World(nb_col=conf['grid']['nb_col'], nb_row=conf['grid']['nb_row'])
    world.create_orbs(quantity=30)
    world.create_snakes(quantity=3, first_is_a_player=True)

    window = MapWindow(world=world, debug_level=debug_level)
    window.setup()
    arcade.run()

if __name__ == '__main__':
    print(f'Welcome to {conf['game_name']}!')
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-v',
        '--verbose',
        action='count',
        default=0,
        help='-v : full logs / -vv full logs + map debug'
    )
    args = parser.parse_args()
    main(args.verbose)