import dbus
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')

from html.parser import HTMLParser
from io import StringIO
from json import dumps, loads
from os import path
from pathlib import Path, PosixPath
from random import choice
from re import search
from sys import stderr, stdout
from time import sleep
from typing import Callable, Iterable
from unicodedata import category

from dynaconf import Dynaconf
from fast_colorthief import get_dominant_color, get_palette
from gi.repository import GdkPixbuf, Gio, GLib, Gtk
from PIL import Image, ImageFilter
from requests import exceptions, get

current_dir = Path(__file__).resolve().parent
config = Dynaconf(
    settings_files=[f'{current_dir}/../config.toml']
)


class PangoStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def contains_pango(string: str) -> bool:
    return any(item in string for item in ['<span>', '</a>', '</span'])


def strip_pango_tags(pango: str) -> str:
    stripper = PangoStripper()
    stripper.feed(pango)
    return stripper.get_data()


def make_parents(file_path: str):
    PosixPath(path.dirname(file_path)).mkdir(parents=True, exist_ok=True)
    PosixPath(file_path).touch(exist_ok=True)


def watcher(file_path: str, callback: Callable, interval: int, initial: bool = True):
    try:
        old = PosixPath(file_path).read_text()
        if initial:
            callback(old)
        while not sleep(interval):
            new = PosixPath(file_path).read_text()
            if new != old:
                callback(new)
                old = new
    except KeyboardInterrupt:
        stdout.write('Closed.\n')
    except FileNotFoundError:
        stderr.write('The path does not exist!\n')
    except Exception as e:
        stderr.write(f'{e}\n')


def gen_quote(file_path: str, default_quote: str) -> str:
    loaded_quotes: str = PosixPath(file_path).read_text().strip()
    return choice(loaded_quotes.splitlines()) if loaded_quotes else default_quote


def matched_index_rm(file_path: str, pattern: str):
    posix_file_path = PosixPath(file_path)
    lines = posix_file_path.read_text().splitlines()
    rm_index_lines = [
        lines[index]
        for index in range(len(lines))
        if not search(pattern, lines[index])
    ]

    if len(lines) != len(rm_index_lines):
        posix_file_path.write_text('\n'.join(rm_index_lines))


def rm_line(file_path: str, position: int | bool | range = True):
    file = PosixPath(file_path)
    match str(type(position)):
        case '<class "int">':
            file_contents = file.read_text().splitlines()
            if position == 0:
                rm_line(file_path, position=True)
                return
            elif position == len(file_contents) - 1:
                rm_line(file_path, position=False)
                return
            line_removed_contents = []
            for index in range(len(file_contents)):
                if index != position:
                    line_removed_contents += [file_contents[index]]
            file.write_text("\n".join(line_removed_contents))
        case '<class "bool">':
            file_contents = file.read_text().splitlines()
            file_contents = file_contents[1:] if position else file_contents[:-1]
            file.write_text('\n'.join(file_contents))
        case '<class "range">':
            if not position:
                file.write_text('')
                return
            file_contents = file.read_text().splitlines()
            write_contents = [file_contents[index] for index in range(len(file_contents)) if index not in position]
            file.write_text('\n'.join(write_contents))


def prettify_name(name: str) -> str:
    return ' '.join(
        item.capitalize()
        for item in name.replace('-', ' ').replace('_', ' ').split(' ')
    )


def file_add_line(file_path: str, write_contents: str, limit: int, top: bool = True):
    file = PosixPath(file_path)
    file_contents = file.read_text().splitlines()
    if len(file_contents) == limit:
        file_contents = file_contents[:-1]
    file_contents = (
        [write_contents] + file_contents if top else file_contents + [write_contents]
    )
    file.write_text('\n'.join(file_contents))


def parse_and_print_stats(content: str) -> dict:
    stats = {
        'critical': 0,
        'low': 0,
        'normal': 0,
        'total': 0
    }

    for line in content.splitlines():
        if 'CRITICAL' in line:
            stats['critical'] += 1
            stats['total'] += 1
        elif 'LOW' in line:
            stats['low'] += 1
            stats['total'] += 1
        elif 'NORMAL' in line:
            stats['normal'] += 1
            stats['total'] += 1

    stats['critical'] = (
        stats['critical'] * 100 /
        stats['total'] if stats["critical"] > 0 else 0
    )
    stats['normal'] = (
        stats['normal'] * 100 / stats['total'] if stats['normal'] > 0 else 0
    )
    stats['low'] = stats['low'] * 100 / \
        stats['total'] if stats['low'] > 0 else 0
    return stats


def non_eng(string: str) -> dict:
    return {
        'CJK': any(category(char) == 'Lo' for char in string),
        'CYR': any(category(char) == 'Lu' for char in string),
    }


def unwrap(value: dbus.Array
           | dbus.Boolean
           | dbus.Byte
           | dbus.Dictionary
           | dbus.Double
           | dbus.Int16
           | dbus.ByteArray
           | dbus.Int32
           | dbus.Int64
           | dbus.Signature
           | dbus.UInt16
           | dbus.UInt32
           | dbus.UInt64
           | dbus.String) -> str | int | list | tuple | float | dict | bool | bytes:
    if isinstance(value, dbus.ByteArray):
        return "".join([str(byte) for byte in value])
    if isinstance(value, (dbus.Array, list, tuple)):
        return [unwrap(item) for item in value]
    if isinstance(value, (dbus.Dictionary, dict)):
        return dict([(unwrap(x), unwrap(y)) for x, y in value.items()])
    if isinstance(value, (dbus.Signature, dbus.String)):
        return str(value)
    if isinstance(value, dbus.Boolean):
        return bool(value)
    if isinstance(
        value,
        (dbus.Int16, dbus.UInt16, dbus.Int32,
         dbus.UInt32, dbus.Int64, dbus.UInt64),
    ):
        return int(value)
    if isinstance(value, dbus.Byte):
        return bytes([int(value)])
    return value


def save_img_byte(px_args: Iterable, save_path: str):
    GdkPixbuf.Pixbuf.new_from_bytes(
        width=px_args[0],  # noqa
        height=px_args[1],  # noqa
        has_alpha=px_args[3],  # noqa
        data=GLib.Bytes(px_args[6]),  # noqa
        colorspace=GdkPixbuf.Colorspace.RGB,
        rowstride=px_args[2],  # noqa
        bits_per_sample=px_args[4],  # noqa
    ).savev(save_path, 'png')  # noqa


def get_icon_path(icon_name: str, size: int = 128) -> str:
    if size < 32:
        return path.expandvars(config.notification.empty_icon)
    if info := Gtk.IconTheme.get_default().lookup_icon(icon_name, size, 0):
        return info.get_filename()
    return get_icon_path(icon_name, size - 1)


def get_mime_path(mimetype: str, size: int = 32) -> str:
    icon = Gio.content_type_get_icon(mimetype)
    theme = Gtk.IconTheme.get_default()
    if info := theme.choose_icon(icon.get_names(), size, 0):
        return info.get_filename()


def get_location() -> dict | None:
    try:
        response = get('https://api64.ipify.org?format=json').json()
        ip_address = response['ip']
        response = get(f'https://ipapi.co/{ip_address}/json/').json()
        return {
            'latitude': response.get('latitude'),
            'longitude': response.get('longitude'),
            'city': response.get('city'),
            'country': response.get('country_name'),
            'language': response.get('languages').split(',')[0],
        }
    except exceptions.ConnectionError:
        return None


def auto_locate(cache_dir: str) -> dict | None:
    cache_posix_path = PosixPath(f"{cache_dir}/location.json")
    if not cache_posix_path.is_file():
        fetched_location = get_location()

        if not fetched_location:
            return None

        cache_posix_path.write_text(dumps(fetched_location))
        return fetched_location
    return loads(cache_posix_path.read_text())


def fetch_save(link: str, save_path: str, callback: Callable = None) -> bool:
    try:
        data = get(link)
        if data.status_code == 200:
            metadata = data.json()
            if callback:
                metadata = callback(metadata)
            PosixPath(save_path).write_text(dumps(metadata))
            return True
        return False
    except exceptions.ConnectionError:
        return False


def color_img(imagepath: any, quality: int = 1, colors: int = 10, primary: bool = False) -> str | list[str]:
    dominant, palette = (
        get_dominant_color(imagepath, quality),
        get_palette(imagepath, color_count=colors, quality=quality)
    )

    def rgb_to_hex(rgb: tuple):
        return '#' + ''.join(f'{bi:02X}' for bi in rgb)

    if primary:
        return rgb_to_hex(dominant)
    return [rgb_to_hex(c) for c in palette]


def blur_img(imagepath: str, save: str, intensity: int):
    image = Image.open(imagepath)
    blur = image.filter(ImageFilter.GaussianBlur(intensity))
    blur.save(save)


def path_expander(pathname: str):
    return path.expanduser(path.expandvars(pathname))
