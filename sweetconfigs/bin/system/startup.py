#!/usr/bin/env python

from os import environ, path
from subprocess import Popen

from utils import config, process_fetch, path_expander


def execute(cmd: tuple):
    for command in cmd:
        Popen(command)


if __name__ == '__main__':
    session = environ['XDG_SESSION_TYPE']
    check = (
        'sxhkd',
        'polybar',
        'waybar',
        'picom',
        'dunst',
        'mako',
        'mpd',
        'mpDris2',
        'greenclip',
        'xfce4-power-manager',
        'eww',
        'eww-wl',
        'bspc',
        'berryc'
    )

    commands = {
        'global': (
            ['xrdb', path_expander('$HOME/.Xresources')],
            ['xsetroot', '-cursor_name', 'left_ptr'],
            ['/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1'],
            ['greenclip', 'daemon'],
            ['mpd'],
            ['mpDris2']
        ),
        'wayland': (
            ['swaybg', '--output', '*', '--mode', 'fill', '--image', path_expander(config.wallpaper)]
        ),
        'x11': (
            ['feh', '--bg-fill', '-r', '-z', path_expander(config.wallpaper)],
            ['xfce4-power-manager'],
        )
    }

    for kill in check:
        if process_fetch(kill):
            print(kill)

    if session == 'wayland':
        if not process_fetch('mako'):
            Popen(['mako', '--config', path_expander(config.notification.mako_config_file)])
        execute(commands.get('wayland'))
    elif session == 'x11':
        if not process_fetch('dunst'):
            Popen(['dunst', '-config', path_expander(config.notification.dunst_config_file)])
        if not process_fetch('picom'):
            Popen(['picom', '--config', path_expander(config.xcompositor_config_file)])
        execute(commands.get('x11'))
    execute(commands.get('global'))
