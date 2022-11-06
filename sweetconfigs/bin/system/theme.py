#!/usr/bin/env python

from os import path
from shutil import which
from subprocess import run

from utils import config, path_expander


def execute(commands: tuple, main: str = ''):
    for command in commands:
        match main:
            case 'sed':
                cmd = ['sed', '-i']
            case 'gsettings':
                cmd = ['gsettings', 'set']
        # noinspection PyUnboundLocalVariable
        cmd.extend(command)  # type: ignore
        return cmd  # type: ignore


def change_value(keyval, file):
    var, val = keyval.split('=')
    return [f's/^{var}\\=.*/{var}={val}/', file]


def settings(**kwargs):
    schema, peripheral, preferences, easyeffects = ('org.gnome.desktop.interface',
                                                    'org.gnome.deskop.peripherals',
                                                    'org.gnome.desktop.wm.preferences',
                                                    'com.github.wwmm.easyeffects')
    assign = (
        [schema, 'gtk-theme', kwargs['theme']],
        [schema, 'icon-theme', kwargs['icon']],
        [schema, 'cursor-theme', kwargs['cursor']],
        [schema, 'cursor-size', kwargs['cursor_size']],
        [schema, 'font-name', kwargs['font'], kwargs['font_size']],
        [preferences, 'button-layout', ':'],
        [preferences, 'theme', kwargs['theme']],
        [f'{peripheral}.keyboard', 'repeat-interval', '30'],
        [f'{peripheral}.keyboard', 'delay', '250'],
        [f'{peripheral}.mouse', 'natural-scroll', 'false'],
        [f'{peripheral}.mouse', 'speed', '0.0'],
        [f'{peripheral}.mouse', 'accel-profile', 'default'],
    )
    assign_easyeffects = (
        [easyeffects, 'process-all-inputs', 'true'],
        [easyeffects, 'process-all-outputs', 'true'],
    )

    # noinspection PyTypeChecker
    def options(file, c='', s=' '):
        configure = (
            change_value(f'gtk-theme-name={c}{kwargs["theme"]}{c}', file),
            change_value(f'gtk-icon-theme-name={c}{kwargs["icon"]}{c}', file),
            change_value(f'gtk-font-name={c}{kwargs["font"]}{s}{kwargs["font_size"]}{c}', file),
            change_value(f'gtk-cursor-theme-name={c}{kwargs["cursor"]}{c}', file),
            change_value(f'gtk-cursor-theme-size={kwargs["cursor_size"]}', file),
        )
        if conf.dark:
            configure_dark = [change_value(f'gtk-application-prefer-dark-theme={c}1{c}', file)]
        else:
            configure_dark = [change_value(f'gtk-application-prefer-dark-theme={c}0{c}', file)]

        run(execute(configure_dark, main='sed'))  # type: ignore
        run(execute(configure, main='sed'))  # type: ignore

    options(path_expander(kwargs['gtk3']))
    options(path_expander(kwargs['gtk2']), '"')

    run(execute(assign, main='gsettings'))  # type: ignore
    if which('easyeffects'):
        run(execute(assign_easyeffects, main='gsettings'))  # type: ignore


if __name__ in '__main__':
    conf = config.gtk
    settings(
        theme=conf.theme,
        icon=conf.icons,
        cursor=conf.cursor,
        font=conf.font,
        cursor_size=conf.cursor_size,
        font_size=conf.font_size,
        gtk2=conf.gtk2_dir,
        gtk3=conf.gtk3_dir
    )
