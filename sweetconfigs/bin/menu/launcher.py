#!/usr/bin/env python

from argparse import ArgumentParser
from os import environ
from pathlib import Path
from shlex import split
from subprocess import run
from sys import path as spath

current_dir = Path(__file__).resolve().parent
spath.insert(1, f'{current_dir}/../system')
from utils import config, path_expander  # type: ignore


def command(show: str, cmd: list, app: str, terminal: str = 'alacritty', **kwargs) -> list:
    parameters = {
        'rofi': ['-show', show, '-modi', kwargs.get('modi', show),
                 '-scroll-method', '0', '-drun-match-field', 'all',
                 '-drun-display-format', '{name}', '-no-drun-show-actions',
                 '-terminal', terminal],
        'wofi': ['--show', show, '--term', terminal, '--gtk-dark',
                 '--conf', kwargs.get('config', ''),
                 '--style', kwargs.get('style', ''),
                 '--color', kwargs.get('color', '')]
    }
    cmd.extend(parameters.get(app))
    return cmd


def passer(conf: str, cmd: list, app: str) -> list:
    if app == 'rofi' and conf.endswith('.rasi'):
        return cmd.extend(['-theme', conf])
    return cmd.extend([])


def arguments():
    parser = ArgumentParser(description='a simple launcher script')
    parser.add_argument('modi', help='specify which modi to show')
    return parser.parse_args()


def main():
    term, launcher, app, args = (
        config.menu.terminal,
        config.menu.launcher,
        config.menu.app,
        arguments(),
    )
    cmd = split(app)
    
    try:
        session = environ['XDG_SESSION_TYPE']
    except KeyError:
        print('XDG_SESSION_TYPE is not set')
        exit(1)
        
    
    if session == 'wayland' and app == 'wofi' and args.modi:
        run(command(
                args.modi, cmd, app, term, 
                config=path_expander(launcher.config),
                style=path_expander(launcher.style), 
                color=path_expander(launcher.colors)
            ) if app == 'wofi' else command(
                args.modi, cmd, app, term, 
                modi=config.menu.modi, 
                config=passer(path_expander(launcher.config, cmd, app))
            )
        )
    elif session == 'x11' and args.modi and app == 'rofi' or app == 'wofi':
        run(command(
                args.modi, cmd, app, term, 
                modi=config.menu.modi, 
                config=passer(path_expander(launcher.config, cmd, app))
            )
        )
    else:
        exit(1)


if __name__ == '__main__':
    main()
