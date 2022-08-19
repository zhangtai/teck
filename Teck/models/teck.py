import logging
import subprocess
from typing import Callable

import pyautogui
from PIL import Image, ImageOps
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.Devices.StreamDeck import StreamDeck

from ..utils.images import (
    position_to_index,
    svg_to_png,
    generate_button_function_image,
    render_button_image,
)
from config.settings import ButtonConfig, DECK_CONFIG

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Teck(object):
    def __init__(self) -> None:
        self.device = self._discover_first_deck()
        self.config = DECK_CONFIG
        self.active_page: str = list(self.config.pages.keys())[0]
        self._active_process_name: str = ""

        self.device.open()
        self.device.reset()
        self.device.set_brightness(50)
        self.refresh_page()

    def _discover_first_deck(self) -> StreamDeck:
        streamdecks = DeviceManager().enumerate()
        if streamdecks:
            return streamdecks[0]
        else:
            raise (ModuleNotFoundError)

    def get_button_config(self, key_index):
        return next(
            (
                b
                for b in self.config.pages.get(self.active_page).buttons
                if position_to_index(b.position) == key_index
            ),
            None,
        )

    def blank_page(self):
        image = Image.new(mode="RGB", size=(72, 72), color=(0, 0, 0))
        button_image = render_button_image(self.device, image, "")

        with self.device:
            for key in range(self.device.key_count()):
                self.device.set_key_image(key, button_image)

    def refresh_page(self) -> None:
        logger.info(self.active_page)
        for button in self.config.pages.get(self.active_page).buttons:
            update_button_image(self.device, button, False)
        self.device.set_key_callback(get_callback(self.device, self.active_page))

    def refresh_button_text_image(self) -> None:
        function_image_buttons = filter(
            lambda b: b.image_provider == "function",
            self.config.pages.get(self.active_page).buttons,
        )
        for button in function_image_buttons:
            icon = generate_button_function_image(button.image)
            image = render_button_image(
                self.device,
                icon,
                button.label,
            )
            with self.device:
                self.device.set_key_image(position_to_index(button.position), image)


def update_button_image(deck: StreamDeck, button: ButtonConfig, pressed: bool):
    button_index = position_to_index(button.position)
    if button_index >= 0 and button_index <= deck.key_count() - 1:
        icon = Image.open("assets/default_icon.png")
        if button.image_provider == "fontawesome":
            png_path = svg_to_png(button.image)
            icon = ImageOps.invert(Image.open(png_path))
        if button.image_provider == "file":
            icon = Image.open(button.image)
        if button.image_provider == "function":
            icon = generate_button_function_image(button.image)
        image = render_button_image(
            deck,
            icon,
            button.label,
            pressed,
        )
        with deck:
            deck.set_key_image(button_index, image)


def get_callback(deck: StreamDeck, page_name: str) -> Callable:
    def key_callback(stream_deck: StreamDeck, key: int, pressed: bool):
        logger.info("Page: %s. %s: %s", page_name, key, pressed)
        button = next(
            (
                b
                for b in DECK_CONFIG.pages.get(page_name).buttons
                if position_to_index(b.position) == key
            ),
            None,
        )
        if button:
            update_button_image(deck, button, pressed)
            if pressed:
                action = list(button.action.keys())[0]
                if action == "subprocess":
                    subprocess.Popen(button.action["subprocess"])
                if action == "hotkeys":
                    pyautogui.hotkey(*button.action["hotkeys"].split("|"))

    return key_callback
