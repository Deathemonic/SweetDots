#!/usr/bin/env python

from argparse import ArgumentParser
from os import environ, path
from pathlib import Path
from subprocess import run
from sys import path as spath

current_dir = Path(__file__).resolve().parent
spath.insert(1, f'{current_dir}/../system')
from utils import config, path_expander  # type: ignore


def arguments():
    parser = ArgumentParser(description='a simple terminal script')
    parser.add_argument('-f', '--float', action='store_true', help='launch the terminal in floating mode')
    parser.add_argument('-F', '--full', action='store_true', help='launch the terminal in fullscreen mode')
    parser.add_argument('-a', '--area', action='store_true', help='launch the terminal in a specified area')
    parser.add_argument('-x', '--alacritty', action='store_true', help='will use alacritty instead of foot')
    return parser.parse_args()


def launch(do: str, forced: int = False):
    session = environ['XDG_SESSION_TYPE']
    match do:
        case 'float':
            if session == 'wayland' and forced is False:
                run(['foot', '--app-id=foot_floating', f'--config={conf_foot}'])
            elif session == 'x11' or forced is True:
                run(['alacritty', '--class', 'alacritty_floating', '--config-file', conf_ala])
        case 'full':
            if session == 'wayland' and forced is False:
                run(['foot', '--fullscreen', '--app-id=foot_fullscreen', f'--config={conf_foot}'])
            elif session == 'x11' or forced is True:
                run(['alacritty', '--class', 'alacritty_fullscreen', '--config-file', conf_ala])
        case 'area':
            if session == 'wayland' and forced is False:
                area = run(['slurp', '-b', '1B1F23AA', '-c', 'FFDEDEFF', '-s', '00000000', '-w', '2', '-f', '%wx%h'],
                           check=True,
                           text=True,
                           capture_output=True).stdout
                run(['foot', '--app-id=foot_floating', f'--config={conf_foot}',
                     f'--window-size-pixels={area.rstrip()}'])
            elif session == 'x11' or forced is True:
                run(['alacritty', '--class', '--config-file', conf_ala])
        case _:
            if session == 'wayland' and forced is False:
                run(['foot', f'--config={conf_foot}'])
            elif session == 'x11' or forced is True:
                run(['alacritty', '--config-file', conf_ala])


def main():
    if args.float:
        if args.alacritty:
            launch('float', forced=True)
        else:
            launch('float')
    elif args.full:
        if args.alacritty:
            launch('full', forced=True)
        else:
            launch('full')
    elif args.area:
        if args.alacritty:
            launch('area', forced=True)
        else:
            launch('area')
    else:
        if args.alacritty:
            launch('normal', forced=True)
        else:
            launch('normal')


if __name__ == '__main__':
    args, conf_foot, conf_ala = (
        arguments(),
        path_expander(config.terminal.foot_config_file),
        path_expander(config.terminal.alacritty_config_file)
    )
