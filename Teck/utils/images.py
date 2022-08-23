from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg
from StreamDeck.Devices.StreamDeck import StreamDeck
from StreamDeck.ImageHelpers import PILHelper

from config.button_display import time_display, today_time_remains  # noqa: F401 # pylint: disable=unused-import


def svg_to_png(source: str) -> str:
    drawing = svg2rlg(source)
    filename_no_ext = Path(source).stem
    final_image = f"assets/temp/{filename_no_ext}.png"
    renderPM.drawToFile(drawing, final_image, fmt="PNG")
    return final_image


def generate_button_function_image(script: str, font_filename: str = "assets/fonts/Roboto-Regular.ttf"):
    image = Image.new(mode="RGB", size=(72, 72), color=(0, 0, 0))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_filename, 30)
    draw.text(
        (image.width / 2, image.height - 5),
        text=eval(script),  # pylint: disable=eval-used
        font=font,
        anchor="ms",
        fill="white",
    )
    return image


def render_button_image(
    deck: StreamDeck,
    icon: Image.Image,
    label_text: str = "",
    pressed: bool = False,
    font_filename: str = "assets/fonts/Roboto-Regular.ttf",
):
    if label_text:
        margins = [5, 5, 25, 5] if pressed else [0, 0, 20, 0]
        image = PILHelper.create_scaled_image(deck, icon, margins=margins)
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(font_filename, 14)
        draw.text(
            (image.width / 2, image.height - 5),
            text=label_text,
            font=font,
            anchor="ms",
            fill="white",
        )
    else:
        margins = [10, 10, 10, 10] if pressed else [5, 5, 5, 5]
        image = PILHelper.create_scaled_image(deck, icon, margins=margins)
    return PILHelper.to_native_format(deck, image)


def open_image_as_png(input_file: str) -> Image.Image:
    if Path(input_file).suffix.lower() == ".svg":
        return Image.open(svg_to_png(input_file))
    if Path(input_file).suffix.lower() == ".png":
        return Image.open(input_file)
    raise TypeError
