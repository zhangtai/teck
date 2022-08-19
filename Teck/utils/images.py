from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg
from StreamDeck.Devices.StreamDeck import StreamDeck
from StreamDeck.ImageHelpers import PILHelper

from config.settings import DEFAULT_FONT, ButtonConfig


def position_to_index(position: tuple[int, int], layout: tuple[int, int] = (3, 5)) -> int:
    return (position[0] - 1) * layout[1] + position[1] - 1


def svg_to_png(source: str) -> str:
    drawing = svg2rlg(source)
    filename_no_ext = Path(source).stem
    final_image = f"assets/temp/{filename_no_ext}.png"
    renderPM.drawToFile(drawing, final_image, fmt="PNG")
    return final_image


def generate_button_function_image(script: str, font_filename: str = DEFAULT_FONT):
    image = Image.new(mode="RGB", size=(72, 72), color=(0, 0, 0))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_filename, 30)
    draw.text((image.width / 2, image.height - 5), text=eval(script), font=font, anchor="ms", fill="white")
    return image


def render_button_image(
    deck: StreamDeck,
    icon: Image,
    label_text: str,
    pressed: bool = False,
    font_filename: str = DEFAULT_FONT,
):
    margins = [10, 10, 30, 10] if pressed else [0, 0, 20, 0]
    image = PILHelper.create_scaled_image(deck, icon, margins=margins)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_filename, 14)
    draw.text((image.width / 2, image.height - 5), text=label_text, font=font, anchor="ms", fill="white")
    return PILHelper.to_native_format(deck, image)


def update_button_image(deck: StreamDeck, button: ButtonConfig, state: bool):
    button_index = position_to_index(button.position)
    if button_index >= 0 and button_index <= deck.key_count() - 1:
        icon = Image.open("assets/default_icon.png")
        if button.image_provider == "fontawesome":
            png_path = svg_to_png(button.image)
            if state:
                icon = Image.open(png_path)
            else:
                icon = ImageOps.invert(Image.open(png_path))
        if button.image_provider == "file":
            icon = Image.open(button.image)
        if button.image_provider == "function":
            icon = generate_button_function_image(button.image)

        image = render_button_image(
            deck,
            icon,
            button.label,
        )
        with deck:
            # Update requested key with the generated image.
            deck.set_key_image(button_index, image)
