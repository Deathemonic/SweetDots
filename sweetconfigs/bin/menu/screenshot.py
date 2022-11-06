#!/usr/bin/env python

from argparse import ArgumentParser
from datetime import datetime
from enum import Enum
from os import environ, path
from pathlib import Path, PosixPath
from secrets import choice
from shlex import split
from string import ascii_letters, digits
from subprocess import run
from sys import path as spath
from time import sleep

from yad import YAD

current_dir = Path(__file__).resolve().parent
spath.insert(1, f'{current_dir}/../system')
from utils import (check_installed, config, notify,  # type: ignore
                   path_expander, process_fetch)


def arguments():
    parser = ArgumentParser(description='a simple screenshot script')
    parser.add_argument('-n', '--now', action='store_true', help='take a screenshot now')
    parser.add_argument('-w', '--window', action='store_true',
                        help='take a screenshot of a active window (Wayland: Only works in Sway and Hyprland)')
    parser.add_argument('-a', '--area', action='store_true', help='take a screenshot of a specific area')
    parser.add_argument('-t', '--timer', action='store_true', help='set a timer to screenshot now')
    parser.add_argument('-m', '--menu', action='store_true',
                        help='launch Rofi or Wofi and use it screenshot (Only works if you have Sweetconfigs)')
    return parser.parse_args()


def open_file():
    notify(app='Clipboard', summary='Screenshot', body='Saved on Clipboard', urgent=0)
    run(['xdg-open', f'{cpath}/{cfile}'])
    if path.exists(f'{cpath}/{cfile}'):
        notify(
            app='Screenshot',
            summary='Screenshot',
            body='Saved',
            icon=f'{cpath}/{cfile}',
            urgent=0
        )
    else:
        notify(
            app='Screenshot',
            summary='Screenshot',
            body='Saved',
            urgent=0
        )


def countdown(count: int):
    for sec in range(count, 0, -1):
        notify(
            app='Countdown',
            summary='Screenshot',
            body=f'Capturing in: {sec}',
            urgent=0
        )
        sleep(1)


class Capture:
    def __init__(self, session: str):
        self.session = session

    def clipboard(self):
        match self.session:
            case 'x11':
                run(['xclip', '-selection', 'clipboard', '-t', 'image/png', '-i', ''])
            case 'wayland':
                with open(f'{cpath}/{cfile}', 'rb') as outfile:
                    run(['wl-copy', '-t', 'image/png'], stdin=outfile)

    def shot_now(self):
        match self.session:
            case 'x11':
                run(['main', '-u', '-f', 'png', f'{cpath}/{cfile}'])
                Capture(self.session).clipboard()
                open_file()
            case 'wayland':
                run(['grim', f'{cpath}/{cfile}'])
                Capture(self.session).clipboard()
                open_file()

    def shot_window(self):
        match self.session:
            case 'x11':
                active_window = run(
                    ['xdotool', 'getactivewindow'],
                    check=True,
                    text=True,
                    capture_output=True,
                ).stdout.rstrip()
                run(['maim', '-u', '-f', 'png', '-i', active_window, f'{cpath}/{cfile}'])
                Capture(self.session).clipboard()
                open_file()
            case 'wayland':
                if process_fetch('sway'):
                    active_window = run(
                        ['swaymsg', '-t', 'get_tree'],
                        capture_output=True
                    ).stdout
                    position = run(
                        ['jq', '-r',
                         '.. | select(.type?) | select(.focused).rect | "\\(.x),\\(.y) \\(.width)x\\(.height)"'],
                        input=active_window,
                        capture_output=True,
                    ).stdout.decode('utf-8').rstrip()
                    run(['grim', '-g', position, f'{cpath}/{cfile}'])
                    Capture(self.session).clipboard()
                    open_file()
                elif process_fetch('Hyprland') or process_fetch('hyprland'):
                    active_window = run(
                        ['hyprctl', 'activewindow'],
                        capture_output=True
                    ).stdout
                    position = run(
                        ['awk', 'NR==2 {print $2}'],
                        input=active_window,
                        capture_output=True
                    ).stdout.decode('utf-8').rstrip()
                    location = run(
                        ['awk', 'NR==3 {sub(/,/,"x"); print $2}'],
                        input=active_window,
                        capture_output=True
                    ).stdout.decode('utf-8').rstrip()
                    run(['grim', '-g', f'{position} {location}', f'{cpath}/{cfile}'])
                    Capture(self.session).clipboard()
                    open_file()
                else:
                    print('Unable to fetch active window')
                    exit(1)

    def shot_area(self):
        match self.session:
            case 'x11':
                run(['maim', '-u', '-f', 'png', '-s', '-b', '2', '-c',
                     '0.35,0.55,0.85,0.25', '-l', f'{cpath}/{cfile}'])
                Capture(self.session).clipboard()
                open_file()
            case 'wayland':
                area = run(
                    ['slurp', '-b', '1B1F23AA', '-c', 'FFDEDEFF', '-s', '00000000'],
                    check=True,
                    text=True,
                    capture_output=True
                ).stdout.rstrip()
                run(['grim', '-g', area, f'{cpath}/{cfile}'])
                Capture(self.session).clipboard()
                open_file()

    def shot_timer(self, time: int):
        match self.session:
            case 'x11':
                countdown(time)
                sleep(2)
                run(['maim', '-u', '-f', 'png', f'{cpath}/{cfile}'])
                Capture(self.session).clipboard()
                open_file()
            case 'wayland':
                countdown(time)
                sleep(2)
                run(['grim', f'{cpath}/{cfile}'])
                Capture(self.session).clipboard()
                open_file()


def command(lines: int, **kwargs):
    parameters = {
        'rofi': ['-dmenu', '-p', kwargs.get('promt', 'Take a Screenshot'),
                 '-selected-row', '0', '-l', f'{lines}'],
        'wofi': ['--dmenu', '-p', kwargs.get('promt', 'Take a Screenshot'),
                 '-L', f'{lines}',
                 '--conf', kwargs.get('config', ''),
                 '--style', kwargs.get('style', ''),
                 '--color', kwargs.get('color', '')]
    }
    if app == 'rofi' or 'wofi':
        cmd.extend(parameters.get(app))  # type: ignore
    return cmd


def passer(conf: str):
    if app == 'rofi' and screenshot.config.endswith('rasi'):
        return cmd.extend(['-theme', conf])
    return cmd.extend([])


def get_selection():
    class Choices(Enum):
        now = screenshot.icons.get('now', 'N')
        win = screenshot.icons.get('win', 'W')
        area = screenshot.icons.get('area', 'A')
        timer = screenshot.icons.get('timer', 'T')

    caller = run(
        ['echo', '-e', '\n'.join(c.value for c in Choices)],
        capture_output=True
    ).stdout

    match session:
        case 'x11':
            if app == 'wofi':
                chosen = run(
                    command(len(Choices),
                            config=path_expander(screenshot.config),
                            style=path_expander(screenshot.style),
                            color=path_expander(screenshot.colors)
                            ),
                    input=caller,
                    capture_output=True
                ).stdout.decode('utf-8').rstrip()
            elif app == 'rofi':
                chosen = run(
                    command(len(Choices),
                            config=passer(path_expander(screenshot.config))),
                    input=caller,
                    capture_output=True
                ).stdout.decode('utf-8').rstrip()
            else:
                exit(1)
        case 'wayland':
            if app == 'wofi' or app == 'rofi':
                chosen = run(
                    command(len(Choices),
                            config=passer(path_expander(screenshot.config))),
                    input=caller,
                    capture_output=True
                ).stdout.decode('utf-8').rstrip()
            else:
                exit(1)

    # noinspection PyUnboundLocalVariable
    match chosen:  # type: ignore
        case Choices.now.value:
            Capture(session).shot_now()
        case Choices.win.value:
            Capture(session).shot_window()
        case Choices.area.value:
            Capture(session).shot_area()
        case Choices.timer.value:
            Capture(session).shot_timer(yad.Scale(max=100, step=1))


def main():
    PosixPath(cpath).mkdir(parents=True, exist_ok=True)
    if args.now:
        Capture(session).shot_now()
    elif args.window:
        Capture(session).shot_window()
    elif args.area:
        Capture(session).shot_area()
    elif args.timer:
        Capture(session).shot_timer(yad.Scale(max=100, step=1))
    elif args.menu:
        get_selection()


if __name__ == '__main__':
    args, yad, session, screenshot = (
        arguments(),
        YAD(),
        environ['XDG_SESSION_TYPE'],
        config.menu.screenshot,
    )
    app = config.menu.get('app', 'rofi')
    cmd, random = (
        split(app),
        ''.join(choice(ascii_letters + digits) for _ in range(10))
    )
    cpath, cfile = (
        path_expander(screenshot.get('directory', '$HOME/Pictures/Screenshots')),
        f'Screenshot_{datetime.now():%Y-%m-%d-%I-%S}_{random}.png'
    )

    match session:
        case 'x11' if check_installed('maim'):
            main()
        case 'wayland' if check_installed('grim'):
            main()
        case _:
            print('Cannot start script do to lack of dependencies, Please install grim or maim')
