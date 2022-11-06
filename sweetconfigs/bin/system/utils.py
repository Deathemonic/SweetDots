from dynaconf import Dynaconf
from gi import require_version

require_version('Notify', '0.7')
from os import path
from pathlib import Path
from shutil import which

from gi.repository import Notify
from psutil import AccessDenied, NoSuchProcess, ZombieProcess, process_iter

current_dir = Path(__file__).resolve().parent
config = Dynaconf(
    settings_files=[f'{current_dir}/../../config.toml']
)


def notify(urgent: int = 0, **kwargs):
    Notify.init(kwargs.get('app', 'Application'))
    notice = Notify.Notification.new(
        kwargs.get('summary', 'Unknown'),
        kwargs.get('body', ''),
        kwargs.get('icon', '/usr/share/icons/Adwaita/scalable/emblems/emblem-system-symbolic.svg'),
    )
    notice.set_urgency(urgent)
    notice.show()


def process_fetch(name: str, pid: bool = False) -> bool | int:
    for proc in process_iter():
        try:
            if name.lower() in proc.name().lower():
                if pid:
                    return proc.pid
                return True
        except (NoSuchProcess,
                AccessDenied,
                ZombieProcess):
            pass
    return False


def check_installed(cmd: str):
    return which(cmd) is not None


def path_expander(pathname: str):
    return path.expanduser(path.expandvars(pathname))
