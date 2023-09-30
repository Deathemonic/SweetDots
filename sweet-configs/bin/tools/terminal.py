import logging
import os
import pathlib
import subprocess
import sys
from argparse import ArgumentParser

sys.path.insert(1, str(pathlib.Path(__file__).resolve().parent.parent.joinpath('core')))
from utils import config, path_expander  # noqa: E402

def launch(action: str, session: str, extra_args: list) -> None:
    if session == 'tty':
        session = 'x11'

    foot_conf: str = path_expander(
        config().terminal.get('foot_config_file', '$HOME/.config/foot/foot.ini')
    )
    alac_conf: str = path_expander(
        config().terminal.get(
            'alacritty_config_file', '$HOME/.config/alacritty/alacritty.yml'
        )
    )

    command: dict = {
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

    if action == 'area' and session == 'wayland':
        try:
            area = subprocess.run(
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
            command['float'][session] += f'--window-size-pixels={area.rstrip()}'

        except FileNotFoundError:
            logging.error('slurp is not installed.')
            exit(1)

    try:
        subprocess.Popen(command[action][session])

    except FileNotFoundError:
        logging.error(f'{command[action][session][0]} is not installed.')
        exit(1)

def arguments():
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
        '-e',
        '--extra',
        nargs='*',
        help='pipe extra arguments to the terminal',
    )

    return parser.parse_args()

def main() -> None:
    args = arguments()
    forced: bool = config().terminal.get('force_use_alacritty', False)

    try:
        session = os.environ['XDG_SESSION_TYPE']

    except KeyError:
        logging.error('XDG_SESSION_TYPE is not set')
        exit(1)

    if args.float:
        action = 'float'

    elif args.full:
        action = 'full'

    elif args.area:
        action = 'area'

    else:
        action = 'normal'

    if args.alacritty is True and not forced:
        session = 'x11'

    print(args.extra)
    launch(action, session, args.extra)

if __name__ == '__main__':
    main()
