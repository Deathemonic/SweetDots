#!/usr/bin/env python

from argparse import ArgumentParser
from sys import path as spath
from pathlib import Path
from subprocess import run
from os import path

current_dir = Path(__file__).resolve().parent
spath.insert(1, f'{current_dir}/../system')
from utils import config, notify  # type: ignore


def arguments():
    parser = ArgumentParser(description='a simple volume script')
    parser.add_argument('-u', '--up', action='store_true', help='increase the volume')
    parser.add_argument('-d', '--down', action='store_true', help='decrease the volume')
    parser.add_argument('-m', '--mute', action='store_true', help='toggle mute')
    return parser.parse_args()


def send(**kwargs):
    volume = run(['pamixer', '--get-volume'], capture_output=True, text=True).stdout.rstrip()
    if run(['pamixer', '--get-mute'], capture_output=True, text=True).stdout.rstrip() == 'true':
        icon = f'{icon_path}/{kwargs.get("icon_mute", "volume_mute.svg")}'
        notify(app='Volume', summary='Muted', icon=icon, urgent=0)
    else:
        if int(volume) < 35:
            icon = f'{icon_path}/{kwargs.get("icon_low", "volume_low.svg")}'
        elif int(volume) < 70:
            icon = f'{icon_path}/{kwargs.get("icon_medium", "volume_medium.svg")}'
        else:
            icon = f'{icon_path}/{kwargs.get("icon_high", "volume_high.svg")}'
        notify(app='Volume', summary=f'Volume: {volume}', icon=icon, urgent=0)


if __name__ == '__main__':
    args, icon_path = (
        arguments(),
        path.expandvars(config.notify_icon_dir)
    )

    if args.up:
        run(['pamixer', '-i', '5', '--set-limit', '100'])
        send()
    elif args.down:
        run(['pamixer', '-d', '5', '--set-limit', '100'])
        send()
    elif args.mute:
        run(['pamixer', '-t'])
        send()
        print(type(args))
