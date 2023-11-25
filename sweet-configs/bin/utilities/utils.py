import contextlib
import logging
import os
import pathlib
import sys
from shutil import which
from typing import Any

import psutil
from dbus_next.aio.message_bus import MessageBus
from dbus_next.introspection import Node
from dynaconf import Dynaconf, LazySettings
from gi import require_version

require_version('Notify', '0.7')
from gi.repository import Notify  # type: ignore # noqa: E402


def config() -> LazySettings:
    root: pathlib.PosixPath = (
        pathlib.PosixPath(__file__).resolve().parent.parent.parent
    )
    file_names: tuple = (
        'config.toml',
        'config.yml',
        'config.yaml',
        'config.ini',
        'config.json',
        '.secrets.toml',
    )
    config_files: set[pathlib.PosixPath] = {
        root / file_name
        for file_name in file_names
        if (root / file_name).exists()
    }

    return Dynaconf(
        apply_default_on_none=True,
        envvar_prefix='SWEETCONF',
        settings_files=config_files,
        load_dotenv=True,
        merge_enabled=True,
    )


async def notify(urgent: int = 0, **kwargs) -> None:
    bus: MessageBus = await MessageBus().connect()
    try:
        introspect: Node = await bus.introspect(
            'org.freedesktop.Notifications',
            '/org/freedesktop/Notifications',
            timeout=3,
        )
        bus.get_proxy_object(
            'org.freedesktop.Notifications',
            '/org/freedesktop/Notifications',
            introspect,
        )

    except Exception:
        logging.error('No Notification daemon found.')

    Notify.init(kwargs.get('app', 'Application'))
    notice: Any = Notify.Notification.new(
        kwargs.get('summary', 'Unknown'),
        kwargs.get('body', ''),
        kwargs.get(
            'icon',
            '/usr/share/icons/Adwaita/scalable/emblems/emblem-system-symbolic.svg',
        ),
    )
    notice.set_urgency(urgent)
    notice.show()


def process_fetch(name: str, pid: bool = False) -> bool | int:
    for proc in psutil.process_iter():
        with contextlib.suppress(
            psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess
        ):
            if name.lower() in proc.name().lower():
                return proc.pid if pid else True
    return False


def setup_logging() -> None:
    logging.basicConfig(
        format='[%(levelname)s\033[0m] \033[1;31m %(module)s \033[0m: %(message)s',
        level='NOTSET',
        stream=sys.stdout,
    )
    logging.addLevelName(logging.ERROR, '\033[1;31mE')
    logging.addLevelName(logging.INFO, '\033[1;32mI')
    logging.addLevelName(logging.WARNING, '\033[1;33mW')


def check_installed(name: str) -> bool | None:
    return which(name) is not None


def path_expander(pathname: str) -> str:
    return os.path.expanduser(os.path.expandvars(pathname))
