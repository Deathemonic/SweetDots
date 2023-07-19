import contextlib
import logging
import pathlib
import psutil
import os
import sys

from shutil import which

from dynaconf import Dynaconf
from gi import require_version

require_version("Notify", "0.7")
from gi.repository import Notify

config = Dynaconf(
    settings_files=[f"{pathlib.Path(__file__).resolve().parent}/../../config.yml"]
)


def notify(urgent: int = 0, **kwargs) -> None:
    Notify.init(kwargs.get("app", "Application"))
    notice = Notify.Notification.new(
        kwargs.get("summary", "Unknown"),
        kwargs.get("body", ""),
        kwargs.get(
            "icon",
            "/usr/share/icons/Adwaita/scalable/emblems/emblem-system-symbolic.svg",
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
    try:
        from rich.logging import RichHandler

        logging.basicConfig(
            format="%(message)s",
            level="NOTSET",
            datefmt="[%X]",
            handlers=[RichHandler(rich_tracebacks=True)],
        )
        logging.getLogger("rich")
    except ImportError:
        logging.basicConfig(
            format="[%(levelname)s\033[0m] \033[1;31m %(module)s \033[0m: %(message)s",
            level="NOTSET",
            stream=sys.stdout,
        )
        logging.addLevelName(logging.ERROR, "\033[1;31mE")
        logging.addLevelName(logging.INFO, "\033[1;32mI")
        logging.addLevelName(logging.WARNING, "\033[1;33mW")


def check_installed(name: str) -> None:
    return which(name) is not None


def path_expander(pathname: str) -> str:
    return os.path.expanduser(os.path.expandvars(pathname))
