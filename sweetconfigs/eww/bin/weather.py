#!/usr/bin/env python

from argparse import ArgumentParser
from datetime import datetime
from json import loads, dumps
from pathlib import PosixPath
from os import path
from utils import config, color_img, auto_locate, fetch_save


def arguments():
    parser = ArgumentParser()
    parser.add_argument('-f', '--fetch', action='store_true', help='fetch the weather in a json format')
    parser.add_argument('-g', '--gist', action='store', help='fetch a specific info from the weather json')
    return parser.parse_args()


def fetch_api(option: dict) -> str | None:
    api = f'https://api.openweathermap.org/data/2.5/weather?appid={config.tokens.openweathermap}'
    params = ''

    if option['latitude'] and option['longitude']:
        params += f'&lat={option["latitude"]}&lon={option["longitude"]}'
    else:
        if option['city']:
            params += f'&q={option["city"]}'
        if not option['country']:
            return
        if option['zip_code'] and not option['city']:
            params += f'&zip={option["zip_code"]}'
        params += f',{option["country"]}'
    if option['language']:
        params += f'&lang={option["language"]}'
    if config.weather.units:
        params += f'&units={config.weather.units}'

    return f'{api}{params}' if params else None


def assign(icon_name: str, icons: dict) -> str:
    try:
        return path.expandvars(icons[icon_name])
    except KeyError:
        return path.expandvars(icons['default'])


def cache(setting: dict) -> dict | str | None:
    if config.location.auto_locate:
        location = auto_locate(cache_path)
    else:
        location = setting

    call_api = fetch_api(location)
    cache_file = PosixPath(f'{cache_path}/weather-{datetime.now():%F-%I}.json')

    def callback(data: dict) -> dict:
        for name in range(len(data['weather'])):
            data['weather'][name]['glyph'] = assign(data['weather'][0]['icon'], config.weather.icons)
            data['weather'][name]['image'] = assign(data['weather'][0]['icon'], config.weather.images)
            data['weather'][name]['image_colors'] = color_img(data['weather'][name]['image'])
        return data

    if not cache_file.is_file() and not fetch_save(call_api, str(cache_file), callback):
        return fallback
    return loads(cache_file.read_text())


if __name__ == '__main__':
    cache_path = path.expandvars(config.location.cache_dir)
    PosixPath(cache_path).mkdir(parents=True, exist_ok=True)

    fallback = {
        'weather': [
            {
                'main': 'NA',
                'glyph': path.expandvars(config.weather.icons.default),
                'image': path.expandvars(config.weather.images.default),
                'icon': '01d'
            }
        ],
        'main': {
            'temp': 'NA',
            'feels_like': 'NA',
            'temp_min': 'NA',
            'temp_max': 'NA',
            'pressure': 'NA',
            'humidity': 'NA'
        },
        'sys': {
            'country': 'NA'
        },
        'name': 'NA'
    }
    metadata, args = (
        cache(config.location),
        arguments()
    )

    if args.fetch is True:
        print(dumps(metadata))
    elif args.gist:
        info = [metadata['weather'][index][args.gist] for index in range(len(metadata['weather']))]
        print(', '.join(info) if len(info) > 2 else ' and '.join(info))
