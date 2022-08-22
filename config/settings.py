import platform
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml
from PIL import Image, ImageOps
from Teck.utils.images import generate_button_function_image, svg_to_png

FONTAWESOME_PATH = "assets/vendor/fontawesome"
SIMPLE_ICONS_PATH = "assets/vendor/simple-icons"
DEFAULT_FONT = "assets/fonts/Roboto-Regular.ttf"


@dataclass
class ButtonImage:
    provider: str
    pil_image: Optional[Image.Image]
    path: Optional[str]
    function: Optional[str]


@dataclass
class ButtonConfig:
    label: str
    image: ButtonImage
    position: tuple[int, int]
    action: dict[str, str]


@dataclass
class PageConfig:
    name: str
    buttons: list[ButtonConfig]


@dataclass
class DeckConfig:
    refresh_interval: int
    retry_interval: int
    pages: dict[str, PageConfig]


def get_deck_config(
    config_file: str = f"config/{platform.system()}.demo.yaml",
) -> DeckConfig:
    config_dict = yaml.load(Path(config_file).read_text(encoding="utf-8"), Loader=yaml.FullLoader)
    configs = DeckConfig(
        refresh_interval=config_dict.get("refresh_interval", 3),
        retry_interval=config_dict.get("retry_interval", 5),
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
            elif (
                button["image"]["provider"] == "fontawesome"
                and Path(f"{FONTAWESOME_PATH}/svgs/{button['image']['path']}").exists()
            ):
                png_path = svg_to_png(f"{FONTAWESOME_PATH}/svgs/{button['image']['path']}")
                button_image.pil_image = ImageOps.invert(Image.open(png_path))
                button_image.path = button['image']['path']
            elif (
                button["image"]["provider"] == "file"
                and Path(f"assets/pages/{page_name}/{button['image']['path']}").exists()
            ):
                button_image.pil_image = Image.open(f"assets/pages/{page_name}/{button['image']['path']}")
                button_image.path = button['image']['path']

            button_config = ButtonConfig(
                label=button["label"],
                image=button_image,
                position=button["position"],
                action=button["action"]
            )
            buttons.append(button_config)
        configs.pages[page_name] = PageConfig(
            name=page_name,
            buttons=buttons,
        )
    return configs


DECK_CONFIG = get_deck_config()
