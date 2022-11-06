#!/usr/bin/env python

from os import environ, path
from pathlib import Path
from subprocess import run
from sys import path as spath

from PIL import Image

current_dir = Path(__file__).resolve().parent
spath.insert(1, f'{current_dir}/../system')
from utils import notify  # type: ignore

if __name__ == '__main__':
    session = environ['XDG_SESSION_TYPE']
    match session:
        case 'wayland':
            color = run(['hyprpicker', '--no-fancy'], capture_output=True, text=True).stdout.rstrip()
        case 'x11':
            color = run(['gpick', '-pso', '--no-newline'], capture_output=True, text=True).stdout.rstrip()
        case _:
            exit(1)

    # noinspection PyUnboundLocalVariable
    location = f'/tmp/{color}.png'
    Image.new('RGB', (48, 48), color).save(location)

    if path.exists(location):
        match environ['XDG_SESSION_TYPE']:
            case 'wayland':
                run(['wl-copy', color])
                notify(app='Color Picker', summary=color, body='Saved in clipboard', icon=location, urgent=1)
            case 'x11':
                run(['xclip', '-selection', 'clipboard', color])
                notify(app='Color Picker', summary=color, body='Saved in clipboard', icon=location, urgent=1)
            case _:
                exit(1)
