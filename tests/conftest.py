import pytest
import json

from src.engine.World import World
from src.ui.views.game_view import GameMode


@pytest.fixture(scope='session')
def game_conf():
    with open('src/game_conf.json') as f:
        return json.load(f)

@pytest.fixture()
def an_empty_world(game_conf):
    return World(nb_col=game_conf['grid']['nb_row'], nb_row=game_conf['grid']['nb_col'], game_mode=GameMode.BOTS, auto_retry=False)

@pytest.fixture()
def a_world_with_one_snake(an_empty_world):
    an_empty_world.create_snakes(quantity=1)
    return an_empty_world

@pytest.fixture()
def a_world_with_five_snakes(an_empty_world):
    an_empty_world.create_snakes(quantity=5)
    return an_empty_world

@pytest.fixture()
def a_world_with_10_orbs(an_empty_world):
    an_empty_world.create_orbs(quantity=10)
    return an_empty_world

@pytest.fixture()
def a_world_with_one_snake_ten_orbs(a_world_with_one_snake):
    a_world_with_one_snake.create_orbs(quantity=10)
    return a_world_with_one_snake
