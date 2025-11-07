from src.engine.World import World
from src.utils import conf

def main() -> None:
    world = World(xmax=conf['grid']['nb_col'], ymax=conf['grid']['nb_row'])
    world.create_orbs(quantity=10)
    world.create_snakes(quantity=1)
    world.spawn_orbs()
    world.spawn_snakes()
    world.show_map()

if __name__ == '__main__':
    print(f'Welcome to {conf['game_name']}!')
    main()