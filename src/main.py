import time

from src.engine.World import World
from src.utils import conf

def main() -> None:
    world = World(nb_col=conf['grid']['nb_col'], nb_row=conf['grid']['nb_row'])
    world.create_orbs(quantity=10)
    world.create_snakes(quantity=1)
    world.spawn_orbs()
    world.spawn_snakes()
    world.show_map()

    for i in range(0, 3):
        world.update()
        time.sleep(3)
        world.show_map()

if __name__ == '__main__':
    print(f'Welcome to {conf['game_name']}!')
    main()