import contextlib
import logging
import os
import pathlib
import sys
from datetime import timedelta
from shutil import which
from typing import Any, Callable, Optional

import psutil
import requests
from requests_cache import CachedSession
from dbus_next.aio.message_bus import MessageBus
from dynaconf import Dynaconf, LazySettings
from gi import require_version

require_version('Notify', '0.7')
from gi.repository import Notify  # type: ignore # noqa: E402


def config() -> LazySettings:
    root: pathlib.PosixPath = pathlib.PosixPath(__file__).resolve().parent.parent.parent
    file_names: tuple = (
        'config.toml',
        'config.yml',
        'config.yaml',
        'config.ini',
        'config.json',
        '.secrets.toml',
        '.secrets.yml',
        '.secrets.yaml',
        '.secrets.ini',
        '.secrets.json',
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
        introspect = await bus.introspect(
            'org.freedesktop.Notifications', '/org/freedesktop/Notifications', timeout=3
        )
        bus.get_proxy_object(
            'org.freedesktop.Notifications',
            '/org/freedesktop/Notifications',
            introspect,
        )

    except Exception as e:
        raise Exception('No notification daemon found') from e

    Notify.init(kwargs.get('app', 'Application'))
    notice = Notify.Notification.new(
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


def fetch_location() -> Optional[dict]:
    try:
        session = CachedSession(
            'location',
            use_cache_dir=True,
            stale_if_error=True,
            stale_while_revalidate=True,
        )

        response: Any = session.get('https://api64.ipify.org?format=json').json()
        ip_address: Any = response['ip']
        response = session.get(f'https://ipapi.co/{ip_address}/json/').json()

        return {
            'latitude': response.get('latitude'),
            'longitude': response.get('longitude'),
            'city': response.get('city'),
            'country': response.get('country_name'),
            'language': response.get('languages').split(',')[0],
        }

    except requests.exceptions.ConnectionError:
        return None


def fetch_link(
    link: str, filename: str, timeout: int, callback: Callable | None = None
) -> Optional[Any]:
    try:
        session = CachedSession(
            filename,
            use_cache_dir=True,
            stale_if_error=True,
            stale_while_revalidate=True,
            expire_after=timedelta(hours=timeout),
        )
        data: Any = session.get(link)

        if data.status_code == 200:
            metadata: Any = data.json()

            if callback:
                metadata = callback(metadata)

            return metadata

    except requests.exceptions.ConnectionError:
        return None


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
