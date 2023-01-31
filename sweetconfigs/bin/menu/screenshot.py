#!/usr/bin/env python


import os
import pathlib
import string
import sys
import logging

from argparse import ArgumentParser
from datetime import datetime
from enum import Enum

from secrets import choice
from shlex import split
from subprocess import run
from time import sleep

from yad import YAD

sys.path.insert(1, f'{pathlib.Path(__file__).resolve().parent}/../system')
import utils  #type: ignore


class Capture:
    screenshot_conf = utils.config.menu.screenshot
    
    target_file, location_path = (
        utils.path_expander(screenshot_conf.get(
                'directory', '$HOME/Pictures/Screenshots'
            )
        ),
        f'Screenshot_{datetime.now():%Y-%m-%d-%H-%M-%S}_' \
        f'{"".join(choice(string.ascii_letters + string.digits) for _ in range(10))}.png'
    )
    
    def __init__(self, session: str) -> None:
        self.session = session

    def clipboard(self):
        if self.session == 'wayland':
            with open(f'{self.location_path}/{self.target_file}', 'rb') as output:
                run(['wl-copy', '-t', 'image/png'], stdin=output) if utils.check_installed('wl-copy') else \
                    logging.warning('wl-copy is not installed')
        elif self.session == 'x11':
            run(['xclip', '-selection', 'clipboard', '-t', 'image/png', '-i', '']) if utils.check_installed('xclip') else \
                logging.warning('xclip is not installed')
        else:
            exit(1)
                
    def now(self):
        run(['main', '-u', '-f', 'png', f'{self.location_path}/{self.target_file}']) if self.session == 'x11' else run(['grim', f'{self.location_path}/{self.target_file}'])
        Capture(self.session).clipboard()
        open_file()
        
    def window(self):
        if self.session == 'wayland':
            if utils.process_fetch('sway'):
                active_window = run(
                    ['swaymsg', '-t', 'get_tree'],
                    capture_output=True
                ).stdout
                position = run(
                    [
                        'jq', '-r',
                        '.. | select(.type?) | select(.focused).rect | "\\(.x),\\(.y) \\(.width)x\\(.height)"'
                    ],
                    input=active_window,
                    capture_output=True,
                ).stdout.decode('utf-8').strip()
                run(['grim', '-g', position, f''])
            elif utils.process_fetch('Hyprland') or utils.process_fetch('hyprland'):
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
                run(['grim', '-g', f'{position} {location}', f'{self.location_path}/{self.target_file}'])
            else:
                logging.error('Unable to capture active windoww')
                exit(1)
            Capture(self.session).clipboard()
            open_file()
    
    def area(self):
        if self.session == 'wayland':
            area = run(
                ['slurp', '-b', '1B1F23AA', '-c', 'FFDEDEFF', '-s', '00000000'],
                check=True,
                text=True,
                capture_output=True
            ).stdout.rstrip()
            run(['grim', '-g', area, f'{self.location_path}/{self.target_file}'])
        elif self.session == 'x11':
            run(['maim', '-u', '-f', 'png', '-s', '-b', '2', '-c',
                '0.35,0.55,0.85,0.25', '-l', f'{self.location_path}/{self.target_file}'])
        
        Capture(self.session).clipboard()
        open_file()
            
    def timer(self, time: int):
        countdown(time)
        sleep(2)
        
        run(['grim', f'{self.location_path}/{self.target_file}']) if self.session == 'wayland' else run([
            'maim', '-u', '-f', 'png' f'{self.location_path}/{self.target_file}'])
        
        Capture(self.session).clipboard()
        open_file()
            

def open_file():
    utils.notify(app='Clipboard', summary='Screenshot', body='Saved on Clipboard', urgent=0)
    run(['xdg-open', f'{Capture.location_path}/{Capture.target_file}']) if utils.check_installed('xdg-open') else \
        logging.warning('cannot execute xdg-open')
    if os.path.exists(f'{Capture.location_path}/{Capture.target_file}'):
        utils.notify(
            app='Screenshot',
            summary='Screenshot',
            body='Saved',
            icon=f'{Capture.location_path}/{Capture.target_file}',
            urgent=0
        )
    else:
        utils.notify(
            app='Screenshot',
            summary='Screenshot',
            body='Deleted',
            urgent=0
        )


def countdown(count: int):
    for sec in range(count, 0, -1):
        utils.notify(
            app='Countdown',
            summary='Screenshot',
            body=f'Capturing in: {sec}',
            urgent=0
        )
        sleep(1)
        

def command(lines: int, cmd: list, app: str, **kwargs) -> list:
    parameters = {
        'rofi': ['-dmenu', '-p', kwargs.get('promt', 'Take a Screenshot'),
                 '-selected-row', '0', '-l', f'{lines}'],
        'wofi': ['--dmenu', '-p', kwargs.get('promt', 'Take a Screenshot'),
                 '-L', f'{lines}',
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


def get_selection(session: str, app: str):
    shot_conf, app = Capture.screenshot_conf, utils.config.menu.get('app', 'rofi')
    cmd = split(app)
    class Choices(Enum):
        now = shot_conf.icons.get('now', 'N')
        win = shot_conf.icons.get('win', 'W')
        area = shot_conf.icons.get('area', 'A')
        timer = shot_conf.icons.get('timer', 'T')
    
    caller = run(
        ['echo', '-e', '\n'.join(c.value for c in Choices)],
        capture_output=True
    ).stdout
        
    chosen = run(
        command(
            len(Choices),
            cmd,
            app,
            config=utils.path_expander(shot_conf.config),
            style=utils.path_expander(shot_conf.style),
            color=utils.path_expander(shot_conf.colors)
        ),
        input=caller,
        capture_output=True
    ).stdout.decode('utf-8').strip() if app == 'wofi' and session == 'wayland' else run(
        command(
            len(Choices),
            cmd,
            app,
            config=passer(utils.path_expander(shot_conf.config), cmd, app)),
            input=caller,
            capture_output=True
        ).stdout.decode('utf-8').strip() if app == 'rofi' or 'wofi' and session == 'wayland' or 'x11' else exit(1)
    
    match chosen:
        case Choices.now.value:
            Capture(session).now()
        case Choices.win.value:
            Capture(session).window()
        case Choices.area.value:
            Capture(session).area()
        case Choices.timer.value:
            Capture(session).timer(yad.Scale(max=100, step=1))



def arguments():
    parser = ArgumentParser(description='a simple screenshot script')
    parser.add_argument(
        '-n', '--now', 
        action='store_true', 
        help='take a screenshot now'
    )
    parser.add_argument(
        '-w', '--window', action='store_true',
        help='take a screenshot of a active window (Wayland: Only works in Sway and Hyprland)')
    parser.add_argument('-a', '--area', action='store_true', help='take a screenshot of a specific area')
    parser.add_argument('-t', '--timer', action='store_true', help='set a timer to screenshot now')
    parser.add_argument('-m', '--menu', action='store_true',
                        help='launch Rofi or Wofi and use it screenshot (Only works if you have Sweetconfigs)')
    return parser.parse_args()


def main():
    args = arguments()
    
    try:
        session = os.environ['XDG_SESSION_TYPE']
    except KeyError:
        logging.error('XDG_SESSION_TYPE is not set')
        exit(1)
        
    if session == 'x11' and not utils.check_installed('main'):
        logging.error('main is not installed')
        exit(1)
    elif session == 'wayland' and not utils.check_installed('grim'):
        logging.error('grim is not installed')
        exit(1)
    
    pathlib.PosixPath(Capture.location_path).mkdir(parents=True, exist_ok=True)
    
    if args.now:
        Capture(session).now()
    elif args.window:
        Capture(session).window()
    elif args.area:
        Capture(session).area()
    elif args.timer:
        Capture(session).timer(yad.Scale(max=100, step=1))
    elif args.menu:
        get_selection()
        
        
if __name__ == '__main__':
    main()
    