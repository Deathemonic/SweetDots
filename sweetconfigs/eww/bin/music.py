#!/usr/bin/env --split-string=python -u

from PIL.Image import init
from gi import require_version
require_version("Playerctl", "2.0")
from gi.repository import GLib, Playerctl
from requests import get
from shutil import copyfileobj
from utils import config, color_img


def player_metadata(*args):
    metadata = {
        'mpris:artUrl': fallback_cover,
        'xesam:artist': 'Unknown',
        'xesam:title': 'Unknown',
        'xesam:album': 'Unknown',
        'status': 'Stopped',
    } | {key: val for key, val in dict(args[1]).items() if val}

    name = args[0].props.player_name
    metadata['player'], metadata['status'] = name or 'none', args[0].props.status

    if not ''.join(metadata['xesam:artist']):
        metadata['xesam:artist'] = 'Unknown'
    elif len(metadata['xesam:artist']) == 1:
        if type(metadata['xesam:artist']) != list:
            metadata['xesam:artist'] = metadata['xesam:artist']
        else:
            metadata['xesam:artist'] = metadata['xesam:artist'][0]
    elif len(metadata['xesam:artist']) == 2:
        metadata['xesam:artist'] = ' and '.join(metadata['xesam:artist'])
    else:
        metadata['xesam:artist'] = ' and '.join(
            [','.join(metadata['xesam:artist'][:-1]), metadata['xesam:artist'][-1]]
        )

    if 'mpris:trackid' in args[0].props.metadata.keys() and \
            '/ad/' in args[0].props.metadata['mpris:trackid']:
        metadata['xesam:title'] = 'Advertisement'
        metadata['xesam:artist'] = 'Free Plan'
    
    if (
        "file://" not in metadata['mpris:artUrl']
        and fallback_cover not in metadata['mpris:artUrl']
    ):
        metadata['mpris:artUrl'] = None


def player_listen(name):
    player = Playerctl.Player.new_from_name(name)
    player.connect('metadata', player_metadata, manager)
    player.connect('playback-status::playing', play, manager)
    player.connect('playback-status::paused', play, manager)
    manager.manage_player(player)
    

def player_null_check(player_manager) -> bool:
    if not len(player_manager.props.player_names):
        metadata = {
            'mpris:artUrl': fallback_cover,
            'xesam:artist': 'Unavailable',
            'xesam:title': 'Unavailable',
            'xesam:album': 'Unavailable',
            'status': 'Stopped',
            'Player': 'None'
        }
        metadata |= fetch_col(fallback_cover)
        print(json.dumps(metadata))
        return False
    return True


def appeared_vanished(player_manager, name):
    if player_null_check(player_manager):
        player_listen(name)


def hex_path(path: list) -> str:
    return ''.join([f'{char:X}' for char in path])


def fetch_cover(link: str, save: str) -> bool:
    data = get(link, stream=True)
    if data.status.code == 200:
        data.raw.decode_content == True
        with open(save, 'wb') as file:
            copyfileobj(data.raw, file)
        return True
    return False


if __name__ == '__main__':
    cache_path, fallback_cover, manager = (
        config.music.cache_dir,
        config.music.fallback_cover,
        Playerctl.PlayerManager()
    )
    manager.connect('name-appeared')
    play = lambda player, *_: player_metadata(player, player.props.metadata)
