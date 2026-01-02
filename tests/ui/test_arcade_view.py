from arcade import SpriteList

from src.ui.game_window import GameWindow
from src.ui.views.game_view import GameView, GameMode


def test_create_grid_sprite_list(an_empty_world):
    _window = GameWindow(visible=False)
    game_view = GameView(world=an_empty_world, game_mode=GameMode.BOTS)
    game_view.create_grid_sprite_list()
    assert isinstance(game_view.grid_sprite_list, SpriteList)
    assert len(game_view.grid_sprite_list) == game_view.nb_row * game_view.nb_col
