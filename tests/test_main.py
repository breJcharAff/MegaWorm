import pytest
from src.utils import is_position_inside_grid

@pytest.mark.parametrize(
    'x, y, expected',
     [
         (0, 0, False),
         (1, 1, True),
     ])
def test_is_position_inside_grid(x: int, y: int, expected: bool):
    assert is_position_inside_grid(x=x, y=y) == expected
