import asyncio
import logging
import pathlib
import subprocess
from argparse import ArgumentParser, Namespace
from typing import Any, Literal

from utilities.utils import config, notify, path_expander


async def controller(**icon) -> None:
    icon_path: pathlib.PosixPath = pathlib.PosixPath(
        path_expander(config().notifications.icon_path)
    )

    try:
        current: str = subprocess.run(
            ['brightnessctl', 'get'], capture_output=True, text=True
        ).stdout.strip()
        maximum: str = subprocess.run(
            ['brightnessctl', 'max'], capture_output=True, text=True
        ).stdout.strip()
        brightness: int = round((int(current) / int(maximum)) * 100)

    except FileNotFoundError:
        logging.error('brightnessctl is not installed.')
        exit(1)

    icons: pathlib.PosixPath = icon_path.joinpath(
        icon.get('icon_low', 'brightness_low.svg')
        if int(brightness) < 35
        else icon.get('icon_medium', 'brightness_medium.svg')
        if int(brightness) < 75
        else icon.get('icon_low', 'brightness_low.svg')
    )

    await notify(
        app='brightness',
        summary=f'Brightness: {brightness}%',
        icon=str(icons),
        urgent=0,
    )


def arguments() -> Namespace:
    parser = ArgumentParser(description='a simple backlight changer')

    parser.add_argument(
        '-u',
        '--up',
        action='store_true',
        help='increase the brightness',
    )

    parser.add_argument(
        '-d',
        '--down',
        action='store_true',
        help='decrease the brightness',
    )

    parser.add_argument(
        '-s',
        '--steps',
        help='set how many steps to adjust the brightness',
    )

    return parser.parse_args()


async def main() -> None:
    args: Namespace = arguments()

    direction = None
    if args.up:
        direction = '+'

    elif args.down:
        direction = '-'

    steps: Any | Literal['5'] = args.steps if args.steps else '5'

    if direction:
        subprocess.run(['brightnessctl', 'set', f'{steps}%{direction}', '-q'])

    await controller()


if __name__ == '__main__':
    asyncio.run(main())
