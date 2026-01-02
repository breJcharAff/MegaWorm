import arcade
from arcade.gui import bind, Property

from src.utils import conf


class Counter(arcade.gui.UIBoxLayout):

    value = Property(0)

    def __init__(self, text: str = '', min: int = -9999, max: int = 9999, value: int = 0) -> None:

        super().__init__(vertical=False, space_between=20)

        self.min = min
        self.max = max
        self.value = value

        self.add(arcade.gui.UILabel(text=text, font_size=conf['views']['menu']['font_size']))
        self.btn_minus = self.add(arcade.gui.UIFlatButton(text='-', width=35))
        self.label = self.add(arcade.gui.UILabel(text=str(self.value), font_size=conf['views']['menu']['font_size']))
        self.btn_plus = self.add(arcade.gui.UIFlatButton(text='+', width=35))

        self.btn_plus.on_click = self.increase
        self.btn_minus.on_click = self.decrease

        # trigger a render when the value changes
        bind(self, 'value', self.update_label)

    def increase(self, _event) -> None:
        if self.value + 1 <= self.max:
            self.value += 1

    def decrease(self, _event) -> None:
        if self.value - 1 >= self.min:
            self.value -= 1

    def update_label(self) -> None:
        self.label.text = str(self.value)