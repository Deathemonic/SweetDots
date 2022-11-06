#!/usr/bin/env --split-string=python -u

from gi import require_version

require_version('Playerctl', '2.0')
from json import dumps, loads
from os import path
from pathlib import Path, PosixPath
from shutil import copyfileobj
from urllib.parse import unquote, urlparse

from gi.repository import GLib, Playerctl
from requests import exceptions, get
from utils import color_img, config


def player_metadata(*args):
    metadata = {
                   'mpris:artUrl': fallback_cover,
                   'xesam:artist': 'Unknown',
                   'xesam:title': 'Unknown',
                   'xesam:album': 'Unknown',
                   'status': 'Stopped',
               } | {key: val for key, val in dict(args[1]).items() if val}

    name = args[0].props.player_name
    metadata['player'] = name or 'none'
    metadata['status'] = args[0].props.status

    if 'mpris:trackid' in args[0].props.metadata.keys() and \
            '/ad/' in args[0].props.metadata['mpris:trackid']:
        metadata['xesam:title'] = 'Advertisement'
        metadata['xesam:artist'] = 'Free Plan'

    if not ''.join(metadata['xesam:artist']):
        metadata['xesam:artist'] = 'Unknown'
    elif len(metadata['xesam:artist']) == 1:
        if metadata['xesam:artist'] != list:
            metadata['xesam:artist'] = metadata['xesam:artist']
        else:
            metadata['xesam:artist'] = metadata['xesam:artist'][0]
    elif len(metadata['xesam:artist']) == 2:
        metadata['xesam:artist'] = ' and '.join(metadata['xesam:artist'])
    else:
        if metadata['xesam:artist'] != list:
            metadata['xesam:artist'] = metadata['xesam:artist']
        else:
            metadata['xesam:artist'] = ' and '.join(
                [', '.join(metadata['xesam:artist'][:-1]), metadata['xesam:artist'][-1]]
            )

    if (
            'file://' not in metadata['mpris:artUrl']
            and fallback_cover not in metadata['mpris:artUrl']
    ):
        metadata['mpris:artUrl'] = fetch(metadata)

    metadata |= fetch_col(unquote(urlparse(metadata['mpris:artUrl']).path))
    print(dumps(metadata))


def play(player, *_):
    player_metadata(player, player.props.metadata)


def player_listen(name):
    player = Playerctl.Player.new_from_name(name)
    player.connect('metadata', player_metadata, manager)
    player.connect('playback-status::playing', play, manager)
    manager.manage_player(player)


def player_null_check(player_manager) -> bool:
    if not len(player_manager.props.player_names):
        metadata = {
            'mpris:artUrl': fallback_cover,
            'xesam:artist': 'Unavailable',
            'xesam:title': 'Unavailable',
            'xesam:album': 'Unavailable',
            'status': 'Stopped',
            'player': 'none',
        }
        metadata |= fetch_col(fallback_cover)
        print(dumps(metadata))
        return False
    return True


def appeared_vanished(player_manager, name):
    if player_null_check(player_manager):
        player_listen(name)


def fetch_cover(link: str, save_path: str) -> bool:
    data = get(link, stream=True)
    if data.status_code == 200:
        data.raw.decode_content = True
        with open(save_path, 'wb') as file:
            copyfileobj(data.raw, file)
        return True
    return False


def fetch(metadata: dict) -> str:
    player_dir = f'{cache_path}/{metadata["player"]}'

    def hex_path(unique_path: list) -> str:
        return ''.join([f'{char:X}' for char in unique_path])

    if metadata['player'] not in ['none', 'firefox']:
        new_meta = {
            'artist': hex_path(metadata['xesam:artist']),
            'album': hex_path(metadata['xesam:album']),
        }
        gen_path = f'{player_dir}/{new_meta["artist"]}'
        if not path.isdir(gen_path):
            Path(gen_path).mkdir(parents=True, exist_ok=True)

        cover_path = f'{gen_path}/{new_meta["album"]}.png'
        if not path.exists(cover_path):
            try:
                return (
                    cover_path if fetch_cover(metadata['mpris:artUrl'], cover_path)
                    else fallback_cover
                )
            except exceptions.ConnectionError:
                return fallback_cover
        return cover_path
    return fallback_cover


def fetch_col(image_path: str) -> dict:
    colors, color_cached = (
        color_img(image_path),
        PosixPath(f'{cache_path}/colors.json')
    )
    parsed_colors = {
        'bright': colors[3],
        'dark': colors[8]
    }

    """
        Because I want the colors to be output the in real time
        I disabled caching, but if you experience lag or slowness,
        Just Uncomment the lines below
    """
    # if color_cached.is_file():
    #     return loads(color_cached.read_text())
    # if 'firefox-mpris' in image_path:
    #     return parsed_colors
    # color_cached.write_text(dumps(parsed_colors))

    return parsed_colors


if __name__ == '__main__':
    cache_path, fallback_cover, manager, loop = (
        path.expandvars(config.music.cache_dir),
        path.expandvars(config.music.fallback_cover),
        Playerctl.PlayerManager(),
        GLib.MainLoop()
    )
    PosixPath(cache_path).mkdir(parents=True, exist_ok=True)

    if player_null_check(manager):
        player = Playerctl.Player()
        player_metadata(player, player.props.metadata)
    manager.connect('name-appeared', appeared_vanished)
    manager.connect('name-vanished', appeared_vanished)
    [player_listen(name) for name in manager.props.player_names]

    try:
        loop.run()
    except (KeyboardInterrupt, Exception):
        loop.quit()
