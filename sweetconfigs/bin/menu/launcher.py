#!/usr/bin/env python

from argparse import ArgumentParser
from sys import path as spath
from pathlib import Path
from subprocess import run
from shlex import split
from os import path, environ

current_dir = Path(__file__).resolve().parent
spath.insert(1, f'{current_dir}/../system')
from utils import config  # type: ignore


def arguments():
    parser = ArgumentParser(description='a simple launcher script')
    parser.add_argument('modi', help='specify which modi to show')
    return parser.parse_args()


def command(show: str, terminal='alacritty', **kwargs):
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
    if app == 'rofi' or 'wofi':
        cmd.extend(parameters.get(app))
    return cmd


def passer(conf: str):
    if app == 'rofi' and conf.endswith('rasi'):
        return cmd.extend(['-theme', conf])
    return cmd.extend([])


def main():
    match session:
        case 'wayland':
            if app == 'wofi' and args.modi:
                run(command(args.modi, term, config=path.expandvars(launcher.config),
                            style=path.expandvars(launcher.style), color=path.expandvars(launcher.colors)))
            elif app == 'rofi' and args.modi:
                run(command(args.modi, term, modi=config.menu.modi, config=passer(path.expandvars(launcher.config))))
            else:
                exit(1)
        case 'x11':
            if app == 'wofi' or app == 'rofi' and args.modi:
                run(command(args.modi, term, modi=config.menu.modi, config=passer(path.expandvars(launcher.config))))
            else:
                exit(1)


if __name__ == '__main__':
    term, launcher, app, args, session = (
        config.menu.terminal,
        config.menu.launcher,
        config.menu.app,
        arguments(),
        environ['XDG_SESSION_TYPE']
    )
    cmd = split(app)
    main()
