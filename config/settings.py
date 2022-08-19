import platform
from dataclasses import dataclass
from pathlib import Path

import yaml

FONTAWESOME_PATH = "assets/fontawesome"
DEFAULT_FONT = "assets/fonts/Roboto-Regular.ttf"

@dataclass
class ButtonConfig:
    label: str
    image_provider: str
    image: str
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


def get_deck_config(config_file: str = f"config/{platform.system()}.demo.yaml") -> DeckConfig:
    config_dict = yaml.load(Path(config_file).read_text(), Loader=yaml.FullLoader)
    configs = DeckConfig(
        refresh_interval=config_dict.get("refresh_interval", 3),
        retry_interval=config_dict.get("retry_interval", 5),
        pages={},
    )
    for name, page in config_dict.get("pages").items():
        buttons = []
        for button in page["buttons"]:
            button_config = ButtonConfig(**button)
            if button_config.image_provider == "fontawesome":
                button_config.image = f"{FONTAWESOME_PATH}/svgs/{button_config.image}"
            if button_config.image_provider == "file":
                button_config.image = f"assets/pages/{name}/{button_config.image}"
            buttons.append(button_config)
        configs.pages[name] = PageConfig(
            name=name,
            buttons=buttons,
        )
    return configs


DECK_CONFIG = get_deck_config()
