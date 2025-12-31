import argparse

import arcade

from src.ui.game_window import GameWindow
from src.utils import conf, setup_logging


def main(debug_level: int) -> None:

    setup_logging(level=debug_level)

    _window = GameWindow()
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