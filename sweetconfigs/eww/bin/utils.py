import sys.path as spath

from dynaconf import Dynaconf
from fast_colorthief import get_dominant_color, get_palette
from pathlib import Path
from PIL import Image, ImageFilter

current_dir = Path(__file__).resolve().parent
config = Dynaconf(
    setting_files = [f'{current_dir}/../config.toml']
)


def color_img(imagepath: str, quality: int = 1, colors: int = 10, primary: bool = False):
    dominant, palette = (
        get_dominant_color(imagepath, quality),
        get_palette(imagepath, color_count=colors, quality=quality)
    )
    rgb_to_hex = lambda rgb: '#' + ''.join(f'{i:02X}' for i in rgb)
    if primary:
        return rgb_to_hex(dominant)
    else:
        return [rgb_to_hex(color) for color in palette]


def blur_img(imagepath: str, save: str, intensity: int = 6):
    image = Image.open(imagepath)
    blur = image.filter(ImageFilter.GaussianBlur(intensity))
    blur.save(save)
