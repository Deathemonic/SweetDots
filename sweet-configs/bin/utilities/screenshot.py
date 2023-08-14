import asyncio
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

from pydub import AudioSegment, playback
from yad import YAD

sys.path.insert(1, f'{pathlib.Path(__file__).resolve().parent}/../system')
import utils  # noqa: E402


class Capture:
    def __init__(self, session: str) -> None:
        self.session = 'x11' if session == 'tty' else session
        self.scrconf = utils.config.menu.screenshot
        self.path = utils.path_expander(
            self.scrconf.get('directory', '$HOME/Pictures/Screenshots')
        )
        self.file = (
            f'Screenshot_{datetime.now():%Y-%m-%d-%H-%M-%S}_'
            f'{str(uuid.uuid4())[:8]}.png'
        )
        self.dir = pathlib.Path(self.path).joinpath(self.file)

    async def execute(self, command: list) -> None:
        args = arguments()
        cmd = {'wayland': ['grim'], 'x11': ['maim', '-u', '-f', 'png']}

        if command:
            cmd[self.session] += command

        try:
            subprocess.run(cmd[self.session])

        except FileExistsError:
            logging.error(f'{cmd[self.session][0]} is not installed')
            exit(1)

        playback.play(
            AudioSegment.from_ogg(
                '/usr/share/sounds/freedesktop/stereo/screen-capture.oga'
            )
        )

        if args.effects:
            effects(self.dir)

        clipboard(self.session, self.dir)
        open_image(self.dir)

    async def now(self) -> None:
        await self.execute([self.dir])

    async def window(self) -> None:
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

            await self.execute(['-g', position, self.dir])

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
                .stdout.decode('utf-8')
                .strip()
            )

            location = (
                subprocess.run(
                    ['awk', 'NR==3 {sub(/,/,"x"); print $2}'],
                    input=active_window,
                    capture_output=True,
                )
                .stdout.decode('utf-8')
                .strip()
            )

            await self.execute(['-g', f'{position} {location}', self.dir])

        elif self.session == 'x11':
            try:
                active_window = subprocess.run(
                    ['xdotool', 'getactivewindow'], check=True, capture_output=True
                ).stdout

            except FileExistsError:
                logging.error(
                    'Failed to capture window,' 'either xdotool is not installed.'
                )
                exit(1)

            await self.execute(['-i', active_window, self.dir])

        else:
            logging.error('Unable to capture active window.')
            exit(1)

    async def area(self) -> None:
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

                await self.execute(['-g', area, self.dir])

            case 'x11':
                await self.execute(
                    [
                        '-s',
                        '-b',
                        '2',
                        '-c',
                        '0.35,0.55,0.85,0.25',
                        '-l',
                        self.dir,
                    ]
                )

    async def timer(self, time: int) -> None:
        await countdown(time)
        await asyncio.sleep(1)
        await self.execute([self.dir])


def clipboard(session: str, dir: pathlib.Path) -> None:
    match session:
        case 'wayland':
            try:
                with open(dir, 'rb') as output:
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
                        dir,
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


def open_image(dir: pathlib.Path) -> None:
    # sourcery skip: remove-redundant-pass
    try:
        subprocess.run(['xdg-open', dir])

    except FileNotFoundError:
        logging.warning(
            'Either xdg-utils package is'
            'not installed or image can not be open. Skipping...'
        )
        pass

    if pathlib.Path(dir).exists():
        utils.notify(
            app='Screenshot',
            summary='Screenshot',
            body='Saved',
            icon=str(dir),
            urgent=1,
        )

    else:
        utils.notify(app='Screenshot', summary='Screenshot', body='Deleted', urgent=1)


# TODO: use pillow or wand if I know how to do it (Help Wanted)
def effects(dir: pathlib.Path) -> None:
    try:
        round_corner = f"""
            convert {dir} +antialias
            \( +clone -alpha extract
            -draw 'fill black polygon 0,0 0,20 20,0 fill white circle 20,20 20,0'
            \( +clone -flip \) -compose Multiply -composite
            \( +clone -flop \) -compose Multiply -composite 
            \) -alpha off -compose CopyOpacity -composite {dir}
        """

        subprocess.run(split(round_corner))

        shadow = f"""
            convert {dir} 
            \( +clone -background black -shadow 69x20+0+10 \) 
            +swap -background none -layers merge +repage {dir}
        """

        subprocess.run(split(shadow))

    except FileNotFoundError:
        logging.error('Unable to add effects, either imagemagick is not installed.')
        exit(1)


async def countdown(count: int) -> None:
    for sec in range(count, 0, -1):
        utils.notify(
            app='Screenshot', summary='Screenshot', body=f'Capturing in {sec}', urgent=0
        )
        await asyncio.sleep(1)


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
        return cmd + ['theme', conf]
    return cmd + []


async def menu_selection(session: str) -> None:
    scrconf = Capture(session).scrconf
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
            await Capture(session).now()
        case Choices.win.value:
            await Capture(session).window()
        case Choices.area.value:
            await Capture(session).area()
        case Choices.timer.value:
            await Capture(session).timer(
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
        '-e',
        '--effects',
        action='store_true',
        help='adds effects to the image (experimental)',
    )

    parser.add_argument(
        '-m',
        '--menu',
        action='store_true',
        help="launch rofi, wofi or eww as it's ui",
    )

    return parser.parse_args()


async def main():
    args = arguments()

    try:
        session = os.environ['XDG_SESSION_TYPE']
    except KeyError:
        logging.error('XDG_SESSION_TYPE is not set')
        exit(1)

    pathlib.Path(Capture(session).path).mkdir(parents=True, exist_ok=True)

    if args.now:
        await Capture(session).now()

    elif args.window:
        await Capture(session).window()

    elif args.area:
        await Capture(session).area()

    elif args.timer:
        await Capture(session).timer(
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
        await menu_selection(session)


if __name__ == '__main__':
    asyncio.run(main())
