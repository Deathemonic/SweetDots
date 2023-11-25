import asyncio
import logging
import os
import pathlib
import subprocess

from PIL import Image
from utilities.utils import notify


async def pick_color(session: str) -> str:
    if session == 'tty':
        session = 'x11'

    match session:
        case 'wayland':
            command: list[str] = ['hyprpicker', '--no-fancy']

        case 'x11':
            command: list[str] = ['gpick', '-pso', '--no-newline']

        case _:
            logging.debug('Session is unknown. Exiting...')
            exit(1)

    try:
        color: str = subprocess.run(
            command,
            capture_output=True,
            text=True,
        ).stdout.strip()

    except FileNotFoundError:
        logging.error(f'{command[0]} is not installed.')
        exit(1)

    return color


async def copy_to_clipboard(session: str, color: str) -> None:
    match session:
        case 'wayland':
            command: list[str] = ['wl-copy', color]
            data = None

        case 'x11':
            command: list[str] = ['xclip', '-selection', 'clipboard']
            data: bytes | None = color.encode() if color else None
        case _:
            logging.debug('Session is unknown. Exiting...')
            exit(1)

    try:
        subprocess.run(command, input=data)

    except FileNotFoundError:
        logging.warning(f'{command[0]} is not installed.')


async def main() -> None:
    session: str = os.environ['XDG_SESSION_TYPE']
    color: str = await pick_color(session)

    location: pathlib.PosixPath = pathlib.PosixPath(
        f'/tmp/{color.replace("#", "")}.png'
    )
    Image.new('RGB', (48, 48), color).save(location)

    await copy_to_clipboard(session, color)

    await notify(
        urgent=1,
        app='Color Picker',
        summary=color,
        body='Saved in clipboard',
        icon=str(location),
    )


if __name__ == '__main__':
    asyncio.run(main())
