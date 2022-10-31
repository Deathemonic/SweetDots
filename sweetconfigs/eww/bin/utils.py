import sys.path as spath

from dynaconf import Dynaconf
from fast_colorthief import get_dominant_color, get_palette
from pathlib import Path
from PIL import Image, ImageFilter

current_dir = Path(__file__).resolve().parent
config = Dynaconf(
    setting_files = [f'{current_dir}/../config.toml']
)


# Here we add our arguments so it could be dynamic
def color_img(imagepath: str, quality: int = 1, colors: int = 10, primary: bool = False):
    """
        We will use fast_colorthief for fetching colors from a image
            - Why not use colorthief?
                It's pretty slow cause it use python as the backend while fast_colorthief uses C++
            - Why not wand or pillow?
                Wand is still slow and Pillow I have to make a custom module for that
    """

    dominant, palette = (
        get_dominant_color(imagepath, quality),  # We fetch the dominant color from the image depending on the quality
        get_palette(imagepath, color_count=colors, quality=quality)  # We fetch the palette of the image depending on how many colors we want
    )
    # We use a lambda expression to change the binary tuple into hexadecimal
    rgb_to_hex = lambda rgb: '#' + ''.join(f'{i:02X}' for i in rgb)  # We join the # in the list comprehension so the result won't be ['#EC', '#FF', '#01']
    # We check if primary is true or not
    if primary:
        return rgb_to_hex(dominant)  # If true returns just the dominant color
    else:
        return [rgb_to_hex(color) for color in palette]  # If false returns the palette

    # This should run ~0.45 seconds or lower


# Now to the image blurring unlike color_img we have to pass the save directory in order to save the image
def blur_img(imagepath: str, save: str, intensity: int = 6):
    """
        We will use PIL to filter the image
            - Why not use wand?
                It's slower than PIL
    """
    image = Image.open(imagepath)  # We open the image using the imagepath argument
    blur = image.filter(ImageFilter.GaussianBlur(intensity))  # We filter the image using gaussian blur depending on the intensity
    blur.save(save)  # And we save the image using the save argument

    # This should run ~0.75 seconds or lower

# If you have something to add or fix feel free to make a pull request
