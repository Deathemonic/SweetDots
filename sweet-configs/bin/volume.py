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
        volume: str = (
            subprocess.run(
                ['pamixer', '--get-volume-human'],
                capture_output=True,
                text=True,
            )
            .stdout.strip()
            .replace('%', '')
        )

    except FileNotFoundError:
        logging.error('pamixer is not installed.')
        exit(1)

    if volume == 'muted':
        await notify(
            app='Volume',
            summary='Muted',
            icon=str(
                icon_path.joinpath(icon.get('icon_mute', 'volume_mute.svg'))
            ),
            urgent=0,
        )

    else:
        icons: pathlib.PosixPath = icon_path.joinpath(
            icon.get('icon_low', 'volume_low.svg')
            if int(volume) < 35
            else icon.get('icon_medium', 'volume_medium.svg')
            if int(volume) < 70
            else icon.get('icon_low', 'volume_low.svg')
        )

        await notify(
            app='Volume',
            summary=f'Volume: {volume}%',
            icon=str(icons),
            urgent=0,
        )


def arguments() -> Namespace:
    parser = ArgumentParser(description='a simple volume changer')

    parser.add_argument(
        '-u',
        '--up',
        action='store_true',
        help='increase the volume',
    )

    parser.add_argument(
        '-d',
        '--down',
        action='store_true',
        help='decrease the volume',
    )

    parser.add_argument(
        '-m',
        '--mute',
        action='store_true',
        help='toggle mute',
    )

    parser.add_argument(
        '-a',
        '--allow-boost',
        action='store_true',
        help='allow volume to go above 100',
    )

    parser.add_argument(
        '-s',
        '--steps',
        help='set how many steps to adjust the volume',
    )

    return parser.parse_args()


async def main() -> None:
    args: Namespace = arguments()

    direction = None
    if args.up:
        direction = '-i'

    elif args.down:
        direction = '-d'

    steps: Any | Literal['5'] = args.steps if args.steps else '5'
    boost: list[str] = (
        ['--allow-boost'] if args.allow_boost else ['--set-limit', '100']
    )

    if direction:
        command: list[Any] = ['pamixer', direction, steps]
        command.extend(boost)
        subprocess.run(command)

    if args.mute:
        subprocess.run(['pamixer', '-t'])

    await controller()


if __name__ == '__main__':
    asyncio.run(main())
