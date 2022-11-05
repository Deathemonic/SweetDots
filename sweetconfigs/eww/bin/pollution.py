#!/usr/bin/env python

from datetime import datetime
from pathlib import PosixPath
from os import path
from utils import config, auto_locate, fetch_save


def fetch_api(option: dict) -> str | None:
    api = f'https://api.openweathermap.org/data/2.5/air_pollution?appid={config.tokens.openweathermap}'
    params = ''

    if option['latitude'] and option['longitude']:
        params += f'&lat={option["latitude"]}&lon={option["longitude"]}'
    return f'{api}{params}' if params else None


def cache(setting: dict) -> dict | str | None:
    if config.location.auto_locate:
        location = auto_locate(cache_path)
    else:
        location = setting

    call_api = fetch_api(location)
    cache_file = PosixPath(f'{cache_path}/pollution-{datetime.now():%F-%I}.json')
    if not cache_file.is_file():
        def callback(data: dict) -> dict:
            data['icons'] = config.pollution.icons
            return data
        fetch_save(call_api, str(cache_file), callback)
    return cache_file.read_text()


if __name__ == '__main__':
    cache_path = path.expandvars(config.location.cache_dir)
    PosixPath(cache_path).mkdir(parents=True, exist_ok=True)

    print(cache(config.location))
