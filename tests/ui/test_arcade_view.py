from arcade import SpriteList
from src.ui.arcade_view import MapWindow


def test_create_grid_sprite_list(an_empty_world):
    window = MapWindow(world=an_empty_world, visible=False)
    window.create_grid_sprite_list()
    assert isinstance(window.grid_sprite_list, SpriteList)
    assert len(window.grid_sprite_list) == window.nb_row * window.nb_col
