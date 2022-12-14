import subprocess
import time
from typing import Callable

import pyautogui
from PIL import Image
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.Devices.StreamDeck import StreamDeck

from config.logger import get_logger
from config.settings import DECK_CONFIG, ButtonAction, ButtonConfig, get_deck_config
from Teck.utils.applications import bring_window_front
from Teck.utils.buttons import get_pressed_buttons_states, position_to_index
from Teck.utils.images import (
    add_pin,
    generate_button_function_image,
    render_button_image,
)

logger = get_logger(__name__)


class Teck():
    def __init__(self) -> None:
        logger.info("Connecting device")
        self.device = self._discover_first_deck()
        self.config = DECK_CONFIG
        self.active_page: str = list(self.config.pages.keys())[0]
        self.page_freezed = False
        self._active_process_name: str = ""
        self.button_pressed_time = [0.0] * 15

        self.device.open()
        self.device.reset()
        self.device.set_brightness(50)

        logger.info("First refresh page when init device")
        self.refresh_page()

    def _discover_first_deck(self) -> StreamDeck:
        streamdecks = DeviceManager().enumerate()
        if streamdecks:
            return streamdecks[0]
        else:
            raise ModuleNotFoundError

    def update_config(self) -> None:
        self.config = get_deck_config()
        logger.info("Teck config updated")
        self.refresh_page()

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
        logger.info("Refreshing page: %s", self.active_page)
        page = self.config.pages.get(self.active_page)
        assert page is not None
        for button in page.buttons:
            logger.debug(button.position)
            pinned = bool(button.position == [1, 1] and self.page_freezed)
            update_button_image(self.device, button, self.config.display_label, pinned, False)
        self.device.set_key_callback(get_callback(self, self.device, self.active_page))

    def refresh_button_text_image(self) -> None:
        page = self.config.pages.get(self.active_page)
        assert page is not None
        function_image_buttons = filter(
            lambda b: b.image.provider == "function",
            page.buttons,
        )
        for button in function_image_buttons:
            assert button.image.pil_image is not None
            assert button.image.function is not None

            image = render_button_image(
                self.device,
                generate_button_function_image(button.image.function),
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


def update_button_image(
    deck: StreamDeck, button: ButtonConfig, pinned: bool, display_label: bool, pressed: bool
):
    button_index = position_to_index(button.position)
    if 0 <= button_index <= deck.key_count() - 1:
        assert button.image.pil_image is not None
        icon = add_pin(button.image.pil_image) if pinned else button.image.pil_image
        assert icon is not None
        label = button.label if display_label else ""
        image = render_button_image(deck, icon, label, pressed)
        with deck:
            deck.set_key_image(button_index, image)


def get_callback(teck: Teck, deck: StreamDeck, page_name: str) -> Callable:
    def key_callback(stream_deck: StreamDeck, button_index: int, pressed: bool):
        logger.info("Page: %s. %s: %s", page_name, button_index, pressed)
        page = DECK_CONFIG.pages.get(page_name)
        assert page is not None
        button = next(
            (b for b in page.buttons if position_to_index(b.position) == button_index),
            None,
        )
        if button:
            if stream_deck.key_states() == get_pressed_buttons_states(DECK_CONFIG.action_triggers["freeze_page"]):
                teck.toggle_freeze()
            if stream_deck.key_states() == get_pressed_buttons_states(DECK_CONFIG.action_triggers["reload_config"]):
                teck.update_config()
            pinned = bool(button.position == [1, 1] and teck.page_freezed)
            update_button_image(deck, button, pinned, teck.config.display_label, pressed)
            if pressed:
                teck.button_pressed_time[button_index] = time.time()
            else:
                duration = time.time() - teck.button_pressed_time[button_index]
                logger.debug("Pressing duration: %s", duration)
                action = button.actions.short if duration < 0.55 or not button.actions.long else button.actions.long
                logger.debug("Action is: %s", action)
                execute_action(teck, action)
                teck.button_pressed_time[button_index] = 0
    return key_callback


def execute_action(teck: Teck, action: ButtonAction) -> None:
    if action.type == "subprocess":
        subprocess.Popen(action.instruction)
    if action.type == "hotkeys":
        pyautogui.hotkey(*action.instruction.split("+"))
    if action.type == "key_sequences":
        for key in action.instruction.split(","):
            if "+" in key:
                pyautogui.hotkey(*key.split("+"))
            else:
                pyautogui.press(key)
            time.sleep(0.1)
    if action.type == "page":
        teck.active_page = action.instruction
        teck.blank_page()
        teck.refresh_page()
        teck.page_freezed = True
    if action.type == "activate_window":
        bring_window_front(action.instruction, lambda k, t: k == t)
