from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg
from StreamDeck.Devices.StreamDeck import StreamDeck
from StreamDeck.ImageHelpers import PILHelper

from config.button_display import time_display, today_time_remains


def position_to_index(
    position: tuple[int, int], layout: tuple[int, int] = (3, 5)
) -> int:
    return (position[0] - 1) * layout[1] + position[1] - 1


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
    label_text: str,
    pressed: bool = False,
    font_filename: str = "assets/fonts/Roboto-Regular.ttf",
):
    margins = [10, 10, 30, 10] if pressed else [0, 0, 20, 0]
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
    return PILHelper.to_native_format(deck, image)


def open_image_as_png(input_file: str) -> Image.Image:
    if Path(input_file).suffix.lower() == ".svg":
        return ImageOps.invert(Image.open(svg_to_png(input_file)))
    if Path(input_file).suffix.lower() == ".png":
        return Image.open(input_file)
    raise TypeError
