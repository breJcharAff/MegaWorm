import pytest
import json

@pytest.fixture(scope='session')
def game_conf():
    with open('src/game_conf.json') as f:
        return json.load(f)