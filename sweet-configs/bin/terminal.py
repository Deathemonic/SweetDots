import logging
import os
import subprocess
from argparse import ArgumentParser, Namespace

from dynaconf import LazySettings
from utilities.utils import config, path_expander


def get_commands(foot_conf: str, alac_conf: str) -> dict:
    return {
        'float': {
            'wayland': [
                'foot',
                '--app-id=foot_floating',
                f'--config={foot_conf}',
            ],
            'x11': [
                'alacritty',
                '--class',
                'alacritty_floating',
                '--config-file',
                alac_conf,
            ],
        },
        'full': {
            'wayland': [
                'foot',
                '--fullscreen',
                '--app-id=foot_fullscreen',
                f'--config={foot_conf}',
            ],
            'x11': [
                'alacritty',
                '--class',
                'alacritty_fullscreen',
                '--config-file',
                alac_conf,
            ],
        },
        'normal': {
            'wayland': [
                'foot',
                f'--config={foot_conf}',
            ],
            'x11': [
                'alacritty',
                '--config-file',
                alac_conf,
            ],
        },
    }


def launch(action: str, session: str, conf: LazySettings, extra: list) -> None:
    if session == 'tty':
        session = 'x11'

    foot_conf: str = path_expander(
        conf.terminal.get('foot_config_file', '$HOME/.config/foot/foot.ini')
    )
    alac_conf: str = path_expander(
        conf.terminal.get(
            'alacritty_config_file', '$HOME/.config/alacritty/alacritty.yml'
        )
    )

    command: dict = get_commands(foot_conf, alac_conf)

    if action == 'area' and session == 'wayland':
        try:
            area: str = subprocess.run(
                [
                    'slurp',
                    '-b',
                    '1B1F23AA',
                    '-c',
                    'FFDEDEFF',
                    '-s',
                    '00000000',
                    '-w',
                    '2',
                    '-f',
                    '%wx%h',
                ],
                check=True,
                text=True,
                capture_output=True,
            ).stdout
            command['float'][
                session
            ] += f'--window-size-pixels={area.rstrip()}'

        except FileNotFoundError:
            logging.error('slurp is not installed.')
            exit(1)

    if extra:
        command[action][session].extend(extra)

    try:
        subprocess.Popen(command[action][session])

    except FileNotFoundError:
        logging.error(f'{command[action][session][0]} is not installed.')
        exit(1)


def arguments() -> Namespace:
    parser = ArgumentParser(description='a simple terminal script')

    parser.add_argument(
        '-f',
        '--float',
        action='store_true',
        help='launch the terminal in floating mode',
    )

    parser.add_argument(
        '-F',
        '--full',
        action='store_true',
        help='launch the terminal in fullscreen mode',
    )

    parser.add_argument(
        '-a',
        '--area',
        action='store_true',
        help='launch the terminal in a specified area',
    )

    parser.add_argument(
        '-x',
        '--alacritty',
        action='store_true',
        help='will force to use alacritty in wayland',
    )

    parser.add_argument(
        '-E',
        '--extra',
        nargs='...',
        help='pipe extra arguments to the terminal',
    )

    return parser.parse_args()


def main() -> None:
    args: Namespace = arguments()
    conf: LazySettings = config()
    forced: bool = conf.terminal.get('force_use_alacritty', False)

    try:
        session: str = os.environ['XDG_SESSION_TYPE']

    except KeyError:
        logging.error('XDG_SESSION_TYPE is not set')
        exit(1)

    action = 'normal'
    if args.float:
        action = 'float'

    elif args.full:
        action = 'full'

    elif args.area:
        action = 'area'

    if args.alacritty is True and not forced:
        session = 'x11'

    launch(action, session, conf, args.extra)


if __name__ == '__main__':
    main()
