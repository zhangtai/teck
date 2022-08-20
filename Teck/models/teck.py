import logging
import subprocess
from typing import Callable

import pyautogui
from PIL import Image, ImageDraw
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.Devices.StreamDeck import StreamDeck

from config.settings import DECK_CONFIG, ButtonConfig

from ..utils.images import (
    position_to_index,
    render_button_image,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Teck(object):
    def __init__(self) -> None:
        self.device = self._discover_first_deck()
        self.config = DECK_CONFIG
        self.active_page: str = list(self.config.pages.keys())[0]
        self.page_freezed = False
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
            raise ModuleNotFoundError

    def get_button_config(self, key_index):
        page = self.config.pages.get(self.active_page)
        assert page is not None
        return next(
            (b for b in page.buttons if position_to_index(b.position) == key_index),
            None,
        )

    def blank_page(self):
        image = Image.new(mode="RGB", size=(72, 72), color=(0, 0, 0))
        button_image = render_button_image(self.device, image, "")

        with self.device:
            for key in range(self.device.key_count()):
                self.device.set_key_image(key, button_image)

    def refresh_page(self) -> None:
        # logger.info(self.active_page)
        page = self.config.pages.get(self.active_page)
        assert page is not None
        for button in page.buttons:
            logger.debug(button.position)
            pinned = bool(button.position == [1, 1] and self.page_freezed)
            update_button_image(self.device, button, pinned, False)
        self.device.set_key_callback(get_callback(self, self.device, self.active_page))

    def refresh_button_text_image(self) -> None:
        page = self.config.pages.get(self.active_page)
        assert page is not None
        function_image_buttons = filter(
            lambda b: b.image_provider == "function",
            page.buttons,
        )
        for button in function_image_buttons:
            image = render_button_image(
                self.device,
                button.image,
                button.label,
            )
            with self.device:
                self.device.set_key_image(position_to_index(button.position), image)

    def toggle_freeze(self) -> None:
        if self.page_freezed:
            logger.info("Unfreezing page %s", self.active_page)
        else:
            logger.info("Freezing page %s", self.active_page)
        self.page_freezed = not self.page_freezed


def add_pin(base: Image) -> Image:
    logger.debug(base.size)
    draw = ImageDraw.Draw(base)
    draw.ellipse(
        (
            base.size[0] - base.size[0] / 4,
            base.size[1] - base.size[0] / 4,
            base.size[0],
            base.size[1],
        ),
        fill=(255, 0, 0),
        outline=(255, 0, 0),
    )
    return base


def update_button_image(
    deck: StreamDeck, button: ButtonConfig, pinned: bool, pressed: bool
):
    button_index = position_to_index(button.position)
    if button_index >= 0 and button_index <= deck.key_count() - 1:
        icon = add_pin(button.image) if pinned else button.image
        image = render_button_image(deck, icon, button.label, pressed)
        with deck:
            deck.set_key_image(button_index, image)


def get_callback(teck: Teck, deck: StreamDeck, page_name: str) -> Callable:
    def key_callback(stream_deck: StreamDeck, key: int, pressed: bool):
        logger.info("Page: %s. %s: %s", page_name, key, pressed)
        page = DECK_CONFIG.pages.get(page_name)
        assert page is not None
        button = next(
            (b for b in page.buttons if position_to_index(b.position) == key),
            None,
        )
        if button:
            freezed_state = [
                True,
                False,
                False,
                False,
                True,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
            ]
            if stream_deck.key_states() == freezed_state:
                teck.toggle_freeze()
            pinned = bool(button.position == [1, 1] and teck.page_freezed)
            update_button_image(deck, button, pinned, pressed)
            if pressed:
                action = list(button.action.keys())[0]
                if action == "subprocess":
                    subprocess.Popen(button.action["subprocess"])
                if action == "hotkeys":
                    pyautogui.hotkey(*button.action["hotkeys"].split("|"))

    return key_callback
