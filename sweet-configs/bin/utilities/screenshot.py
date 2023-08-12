import logging
import os
import pathlib
import subprocess
import sys
import uuid
from argparse import ArgumentParser
from datetime import datetime
from enum import Enum
from shlex import split
from time import sleep

from yad import YAD

sys.path.insert(1, f'{pathlib.Path(__file__).resolve().parent}/../system')
import utils  # noqa: E402


class Capture:
    def __init__(self, session: str = 'x11') -> None:
        self.session = 'x11' if session == 'tty' else session
        self.scrconf = utils.config.menu.screenshot
        self.path = utils.path_expander(
            self.scrconf.get('directory', '$HOME/Pictures/Screenshots')
        )
        self.file = (
            f'Screenshot_{datetime.now():%Y-%m-%d-%H-%M-%S}_'
            f'{str(uuid.uuid4())[:8]}.png'
        )

    def execute(self, command: list) -> None:
        cmd = {'wayland': ['grim'], 'x11': ['maim', '-u', '-f', 'png']}

        if command:
            cmd[self.session] += command

        try:
            subprocess.run(cmd[self.session])
        except FileExistsError:
            logging.error(f'{cmd[self.session][0]} is not installed')
            exit(1)

        clipboard(self.session, self.path, self.file)
        open_image(self.path, self.file)

    def now(self) -> None:
        self.execute([f'{self.path}/{self.file}'])

    def window(self) -> None:
        if utils.process_fetch('sway'):
            active_window = subprocess.run(
                ['swaymsg', '-t', 'get_tree'], capture_output=True
            ).stdout

            try:
                position = (
                    subprocess.run(
                        [
                            'jq',
                            '-r',
                            '.. | select(.type?) | select(.focused).rect | "\\(.x),\\(.y) \\(.width)x\\(.height)"',  # noqa: E501
                        ],
                        input=active_window,
                        capture_output=True,
                    )
                    .stdout.decode('utf-8')
                    .strip()
                )

            except FileExistsError:
                logging.error('Failed to capture window, either jq is not installed.')
                exit(1)

            self.execute(['-g', position, f'{self.path}/{self.file}'])

        elif utils.process_fetch('Hyprland') or utils.process_fetch('hyprland'):
            active_window = subprocess.run(
                ['hyprctl', 'activewindow'], capture_output=True
            ).stdout

            position = (
                subprocess.run(
                    ['awk', 'NR==2 {print $2}'],
                    input=active_window,
                    capture_output=True,
                )
                .stdout.decode("utf-8")
                .strip()
            )

            location = (
                subprocess.run(
                    ['awk', 'NR==3 {sub(/,/,"x"); print $2}'],
                    input=active_window,
                    capture_output=True,
                )
                .stdout.decode("utf-8")
                .strip()
            )

            self.execute(['-g', f'{position} {location}', f'{self.path}/{self.file}'])

        elif self.session == 'x11':
            try:
                active_window = subprocess.run(
                    ['xdotool', 'getactivewindow'],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout

            except FileExistsError:
                logging.error(
                    'Failed to capture window,' 'either xdotool is not installed.'
                )
                exit(1)

            self.execute(['-i', active_window, f'{self.path}/{self.file}'])

        else:
            logging.error('Unable to capture active window.')
            exit(1)

    def area(self) -> None:
        match self.session:
            case 'wayland':
                try:
                    area = subprocess.run(
                        ['slurp', '-b', '1B1F23AA', '-c', 'FFDEDEFF', '-s', '00000000'],
                        check=True,
                        text=True,
                        capture_output=True,
                    ).stdout.strip()
                except FileExistsError:
                    logging.error(
                        'Failed to capture area,' 'either slurp is not installed.'
                    )
                    exit(1)

                self.execute(['-g', area, f'{self.path}/{self.file}'])

            case 'x11':
                self.execute(
                    [
                        '-s',
                        '-b',
                        '2',
                        '-c',
                        '0.35,0.55,0.85,0.25',
                        '-l',
                        f'{self.path}/{self.file}',
                    ]
                )

    def timer(self, time: int) -> None:
        countdown(time)
        self.execute([f'{self.path}/{self.file}'])


def clipboard(session: str, path: str, file: str) -> None:
    match session:
        case 'wayland':
            try:
                with open(f'{path}/{file}', 'rb') as output:
                    subprocess.run(['wl-copy', '-t', 'image/png'], stdin=output)

                utils.notify(
                    app='Clipboard',
                    summary='Screenshot',
                    body='Saved on clipboard',
                    urgent=0,
                )

            except FileNotFoundError:
                logging.warning('wl-clipboard is not installed. Skipping...')
                pass

        case 'x11':
            try:
                subprocess.run(
                    [
                        'xclip',
                        '-selection',
                        'clipboard',
                        '-t',
                        'image/png',
                        '-i',
                        f'{path}/{file}',
                    ]
                )

                utils.notify(
                    app='Clipboard',
                    summary='Screenshot',
                    body='Saved on clipboard',
                    urgent=0,
                )

            except FileNotFoundError:
                logging.warning('xclip is not installed. Skipping ...')
                pass


def open_image(path: str, file: str) -> None:
    # sourcery skip: remove-redundant-pass
    try:
        subprocess.run(['xdg-open', f'{path}/{file}'])

    except FileNotFoundError:
        logging.warning(
            'Either xdg-utils package is'
            'not installed or image can not be open. Skipping...'
        )
        pass

    if os.path.exists(f'{path}/{file}'):
        utils.notify(
            app='Screenshot',
            summary='Screenshot',
            body='Saved',
            icon=f'{path}/{file}',
            urgent=1,
        )

    else:
        utils.notify(app='Screenshot', summary='Screenshot', body='Deleted', urgent=1)


def effects():
    pass


def countdown(count: int) -> None:
    for sec in range(count, 0, -1):
        utils.notify(
            app='Screenshot', summary='Screenshot', body=f'Capturing in {sec}', urgent=1
        )
        sleep(1)


def menu(lines: int, cmd: list, app: str, **kwargs) -> list:
    parameters = {
        'rofi': [
            '-dmenu',
            '-p',
            kwargs.get('promt', 'Take a screenshot'),
            '-selected-row',
            '0',
            '-l',
            f'{lines}',
        ],
        'wofi': [
            '--dmenu',
            '-p',
            kwargs.get('promt', 'Take a Screenshot'),
            '-L',
            f'{lines}',
            '--conf',
            kwargs.get('config', ''),
            '--style',
            kwargs.get('style', ''),
            '--color',
            kwargs.get('color', ''),
        ],
    }

    cmd.extend(parameters.get(app, 'rofi'))
    return cmd


def menu_passer(conf: str, cmd: list, app: str) -> None | list:
    if app == 'rofi' and conf.endswith('.rasi'):
        return cmd.extend(['theme', conf])
    return cmd.extend([])


def menu_selection(session: str) -> None:
    scrconf = Capture().scrconf
    app = utils.path_expander(utils.config.menu.get('app', 'rofi'))
    cmd = split(app)

    class Choices(Enum):
        now = scrconf.icons.get('now', 'N')
        win = scrconf.icons.get('win', 'W')
        area = scrconf.icons.get('area', 'A')
        timer = scrconf.icons.get('timer', 'T')

    caller = subprocess.run(
        ['printf', '\n'.join(c.value for c in Choices)], capture_output=True
    ).stdout

    try:
        chosen = (
            subprocess.run(
                menu(
                    len(Choices),
                    cmd,
                    app,
                    config=utils.path_expander(scrconf.get('config', '')),
                    style=utils.path_expander(scrconf.get('style', '')),
                    color=utils.path_expander(scrconf.get('colors', '')),
                ),
                input=caller,
                capture_output=True,
            )
            .stdout.decode('utf-8')
            .strip()
            if app == 'wofi' and session == 'wayland'
            else subprocess.run(
                menu(
                    len(Choices),
                    cmd,
                    app,
                    config=menu_passer(utils.path_expander(scrconf.config), cmd, app),
                ),
                input=caller,
                capture_output=True,
            )
            .stdout.decode('utf-8')
            .strip()
            if app in ['rofi', 'wofi'] and session in {'wayland', 'x11'}
            else exit(1)
        )

    except FileNotFoundError:
        logging.error(f'{app} is not installed.')
        exit(1)

    match chosen:
        case Choices.now.value:
            Capture(session).now()
        case Choices.win.value:
            Capture(session).window()
        case Choices.area.value:
            Capture(session).area()
        case Choices.timer.value:
            Capture(session).timer(
                YAD().Scale(
                    max=100,
                    center=True,
                    title='Set a number of seconds',
                    fixed=True,
                    on_top=True,
                    width=350,
                    height=100,
                )
            )


def arguments():
    parser = ArgumentParser(description='a simple screenshot script')

    parser.add_argument(
        '-n',
        '--now',
        action='store_true',
        help='take a screenshot now',
    )

    parser.add_argument(
        '-w',
        '--window',
        action='store_true',
        help='take a screenshot of a active window'
        '(wayland: only works in sway and hyprland)',
    )

    parser.add_argument(
        '-a',
        '--area',
        action='store_true',
        help='take a screenshot of a specific area',
    )

    parser.add_argument(
        '-t',
        '--timer',
        action='store_true',
        help='set a timer to screenshot now',
    )

    parser.add_argument(
        '-m',
        '--menu',
        action='store_true',
        help="launch rofi, wofi or eww as it's ui",
    )

    return parser.parse_args()


def main():
    args = arguments()

    try:
        session = os.environ['XDG_SESSION_TYPE']
    except KeyError:
        logging.error('XDG_SESSION_TYPE is not set')
        exit(1)

    pathlib.PosixPath(Capture().path).mkdir(parents=True, exist_ok=True)

    if args.now:
        Capture(session).now()

    elif args.window:
        Capture(session).window()

    elif args.area:
        Capture(session).area()

    elif args.timer:
        Capture(session).timer(
            YAD().Scale(
                max=100,
                center=True,
                title='Set a number of seconds',
                fixed=True,
                on_top=True,
                width=350,
                height=100,
            )
        )

    elif args.menu:
        menu_selection(session)


if __name__ == '__main__':
    main()