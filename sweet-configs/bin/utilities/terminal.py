#!/usr/bin/env pypy3

import os
import pathlib
import sys

from argparse import ArgumentParser
from subprocess import run

sys.path.insert(1, f'{pathlib.Path(__file__).resolve().parent}/../system')
from utils import config, path_expander


def launch(action: str, session: str = '') -> None:    
    if session == 'tty':
        session = 'x11'

    foot_conf: str = path_expander(config.terminal.foot_config_file)
    alac_conf: str = path_expander(config.terminal.alacritty_config_file)



    command: dict = {
        'float': {
            'wayland': ['foot', '--app-id=foot_floating', f'--config={foot_conf}'],
            'x11': ['alacritty', '--class', 'alacritty_floating', '--config-file', alac_conf]
        },
        'full': {
            'wayland': ['foot', '--fullscreen', '--app-id=foot_fullscreen', f'--config={foot_conf}'],
            'x11': ['alacritty', '--class', 'alacritty_fullscreen', '--config-file', alac_conf]
        },
        'area': {
            'wayland': ['foot', '--app-id=foot_area', f'--config={foot_conf}'],
            'x11': ['alacritty', '--class', 'alacritty_floating', '--config-file', alac_conf]
        },
        'normal': {
            'wayland': ['foot', f'--config={foot_conf}'],
            'x11': ['alacritty', '--config-file', alac_conf]
        }
    }

    if action == 'area' and session == 'wayland':
        area = run(
            ['slurp', '-b', '1B1F23AA', '-c', 'FFDEDEFF', '-s', '00000000', '-w', '2', '-f', '%wx%h'],
            check=True,
            text=True,
            capture_output=True,
        ).stdout

        command[action][session] += f'--window-size-pixels={area.rstrip()}'

    run(command[action][session])


def arguments():
    parser = ArgumentParser(description='a simple terminal script')

    parser.add_argument(
        '-f',
        '--float',
        action='store_true',
        help='launch the terminal in floating mode',
    )

    parser.add_argument(
        '-F',
        '--full',
        action='store_true',
        help='launch the terminal in fullscreen mode',
    )

    parser.add_argument(
        '-a',
        '--area',
        action='store_true',
        help='launch the terminal in a specified area',
    )

    parser.add_argument(
        '-x',
        '--alacritty',
        action='store_true',
        help='will force to use alacritty in wayland'
    )

    return parser.parse_args()


def main():
    args = arguments()
    forced: bool = config.terminal.force_use_alacritty
    session: str = os.environ['XDG_SESSION_TYPE']

    if args.float:
        action: str = 'float'
    
    elif args.full:
        action: str = 'full'
    
    elif args.area:
        action: str = 'area'
    
    else:
        action: str = 'normal'
 
    if args.alacritty is True and forced is False:
        session = 'x11'

    launch(action, session)


if __name__ == '__main__':
    main()
