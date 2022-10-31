#!/usr/bin/env --split-string=python -u

from gi import require_version
require_version("Playerctl", "2.0")
from gi.repository import GLib, Playerctl
from utils import config


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

    if name == 'spotify' and \ 
            'mpris:trackid' in args[0].props.metadata.keys() and \
            'ad' in args[0].props.metadata['mpris:trackid']:
        metadata['xesam:title'] = 'Advertisement'
        metadata['xesam:artist'] = 'Free Plan'
    
    if (
        "file://" not in metadata['mpris:artUrl']
        and fallback_cover not in metadata['mpris:artUrl']
    ):
        metadata['mpris:artUrl'] = None
    

if __name__ == '__main__':
    pass
