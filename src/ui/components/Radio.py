import arcade
from arcade.gui import UILabel, UIBoxLayout, UITextureButton


class Radio(arcade.gui.UIBoxLayout):

    def __init__(self, text: str, options: list[str], default: str = None):

        super().__init__(vertical=False, space_between=20)

        self.with_border(color=arcade.color.WHITE)
        self.options = options
        self.current_value = default if default is not None else options[0]

        self.off_texture = arcade.make_circle_texture(diameter=25, color=arcade.color.WHITE)
        self.on_texture = arcade.make_circle_texture(diameter=25, color=arcade.color.GREEN)

        self.add(UILabel(text=text))

        self.ui_options = {}
        self.build_options()

    def build_options(self):

        for option in self.options:
            # small container for text + button
            container = UIBoxLayout(vertical=False, space_between=10)

            is_selected = option == self.current_value
            texture = self.on_texture if is_selected else self.off_texture

            button = UITextureButton(texture=texture, width=20, height=20)
            button.text_key = option

            button.on_click = self.on_radio_click

            self.ui_options[option] = button

            container.add(button)
            container.add(UILabel(text=option))
            self.add(container)

    def on_radio_click(self, event):
        clicked_button = event.source
        selected_option = clicked_button.text_key
        self.current_value = selected_option
        # Set current btn to off, all others to on
        for option_name, button in self.ui_options.items():
            if option_name == self.current_value:
                button.texture = self.on_texture
            else:
                button.texture = self.off_texture

