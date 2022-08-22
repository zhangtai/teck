import platform
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml
from PIL import Image, ImageOps
from Teck.utils.images import generate_button_function_image, open_image_as_png

DEFAULT_FONT = "assets/fonts/Roboto-Regular.ttf"

IMAGE_PROVIDERS = {
    "file": {
        "path": "assets/pages"
    },
    "fontawesome": {
        "path": "assets/vendor/fontawesome/svgs",
        "inverted": True
    },
    "fluentui-emoji": {
        "path": "assets/vendor/fluentui-emoji/assets"
    },
    "google-cloud-icons": {
        "path": "assets/vendor/google-cloud-icons"
    },
}


@dataclass
class ButtonImage:
    provider: str
    pil_image: Optional[Image.Image]
    path: Optional[str]
    function: Optional[str]


@dataclass
class ButtonAction:
    type: str
    instruction: str


@dataclass
class ButtonActions:
    short: ButtonAction
    long: Optional[ButtonAction]


@dataclass
class ButtonConfig:
    label: str
    image: ButtonImage
    position: tuple[int, int]
    actions: ButtonActions


@dataclass
class PageConfig:
    name: str
    buttons: list[ButtonConfig]


@dataclass
class DeckConfig:
    refresh_interval: int
    retry_interval: int
    action_triggers: dict[str, list[tuple[int, int]]]
    pages: dict[str, PageConfig]


def get_deck_config(
    config_file: str = f"config/{platform.system()}.demo.yaml",
) -> DeckConfig:
    config_dict = yaml.load(Path(config_file).read_text(encoding="utf-8"), Loader=yaml.FullLoader)
    configs = DeckConfig(
        refresh_interval=config_dict.get("refresh_interval", 3),
        retry_interval=config_dict.get("retry_interval", 5),
        action_triggers=config_dict.get("action_triggers"),
        pages={},
    )
    for page_name, page_config in config_dict.get("pages").items():
        buttons = []
        for button in page_config["buttons"]:
            pil_image = Image.open("assets/default_icon.png")
            button_image = ButtonImage(
                provider=button["image"]["provider"],
                pil_image=pil_image,
                path="",
                function="",
            )

            if button["image"]["provider"] == "function":
                button_image.pil_image = generate_button_function_image(button["image"]["function"])
                button_image.function = button["image"]["function"]
            else:
                if button["image"]["provider"] == "file":
                    image_base_path = IMAGE_PROVIDERS.get(button["image"]["provider"]).get("path") + "/" + page_name
                else:
                    image_base_path = IMAGE_PROVIDERS.get(button["image"]["provider"]).get("path")
                button_image.pil_image = open_image_as_png(f"{image_base_path}/{button['image']['path']}")
                if IMAGE_PROVIDERS.get(button["image"]["provider"]).get("inverted", False):
                    button_image.pil_image = ImageOps.invert(button_image.pil_image)
                button_image.path = button['image']['path']

            short_action = ButtonAction(**button["actions"]["short"])
            long_action = ButtonAction(**button["actions"]["long"]) if button["actions"].get("long", None) else None
            button_config = ButtonConfig(
                label=button["label"],
                image=button_image,
                position=button["position"],
                actions=ButtonActions(
                    short=short_action,
                    long=long_action,
                ),
            )
            buttons.append(button_config)
        configs.pages[page_name] = PageConfig(
            name=page_name,
            buttons=buttons,
        )
    return configs


DECK_CONFIG = get_deck_config()
