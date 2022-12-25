from json import dumps, loads
from os import path
from pathlib import Path, PosixPath
from typing import Callable

from dynaconf import Dynaconf
from requests import get, exceptions


current_dir = Path(__file__).resolve().parent
config = Dynaconf(
    settings_files=[f'{current_dir}/../config.toml']
)


def get_location() -> dict | None:
    try:
        response = get('https://api64.ipify.org?format=json').json()
        ip_address = response['ip']
        response = get(f'https://ipapi.co/{ip_address}/json/').json()
        return {
            'latitude': response.get('latitude'),
            'longitude': response.get('longitude'),
            'city': response.get('city'),
            'country': response.get('country_name'),
            'language': response.get('languages').split(',')[0],
        }
    except exceptions.ConnectionError:
        return None


def auto_locate(cache_dir: str) -> dict | None:
    cache_posix_path = PosixPath(f"{cache_dir}/location.json")
    if not cache_posix_path.is_file():
        fetched_location = get_location()

        if not fetched_location:
            return None

        cache_posix_path.write_text(dumps(fetched_location))
        return fetched_location
    return loads(cache_posix_path.read_text())


def fetch_save(link: str, save_path: str, callback: Callable = None) -> bool:
    try:
        data = get(link)
        if data.status_code == 200:
            metadata = data.json()
            if callback:
                metadata = callback(metadata)
            PosixPath(save_path).write_text(dumps(metadata))
            return True
        return False
    except exceptions.ConnectionError:
        return False


def path_expander(pathname: str) -> None:
    return path.expanduser(path.expandvars(pathname))