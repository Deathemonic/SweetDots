import json
import logging
import sys
import pathlib
import urllib.parse
from typing import Optional
from dynaconf import LazySettings

from dynaconf.vendor.box import BoxKeyError

sys.path.insert(1, str(pathlib.Path(__file__).resolve().parent.parent.joinpath('core')))
from utils import fetch_link, fetch_location, config, path_expander  # noqa: E402


def format_api(option: Optional[dict], conf: LazySettings) -> Optional[str]:
    api: str = f'https://api.openweathermap.org/data/2.5/weather?appid={conf.tokens.openweathermap}'
    params: dict = {}

    if option is None:
        return None

    try:
        if not option['latitude'] or not option['longitude']:
            raise BoxKeyError

        params['lat'] = option['latitude']
        params['lon'] = option['longitude']

    except BoxKeyError:
        if option['city']:
            params['q'] = option['city']

        if not option['country']:
            return

        if option['zip_code'] and not option['city']:
            params['zip'] = option['zip_code']

        params['country'] = option['country']

    if option['language']:
        params['lang'] = option['language']

    if config().weather.units:
        params['units'] = conf.weather.units

    params_str: str = urllib.parse.urlencode(params)

    return f'{api}&{params_str}' if params else None


def assign(icon_name: str, icons: dict) -> str:
    try:
        return path_expander(icons[icon_name])

    except KeyError:
        return path_expander(icons['default'])


def cache(settings: dict, fallback: dict, conf: LazySettings) -> Optional[dict]:
    location: Optional[dict] = (
        fetch_location() if conf.location.get('auto_locate', True) else settings
    )
    api: Optional[str] = format_api(location, conf)

    def callback(data: dict) -> dict:
        for name in range(len(data['weather'])):
            data['weather'][name]['glyph'] = assign(
                data['weather'][0]['icon'], conf.weather.icons
            )
            data['weather'][name]['image'] = assign(
                data['weather'][0]['icon'], conf.weather.images
            )

        return data

    if fetch_location() is None or api is None:
        return fallback

    return fetch_link(api, 'weather', 1, callback)


def main() -> None:
    conf: LazySettings = config()
    fallback: dict = {
        'weather': [{
            'main': 'NA',
            'glyph': path_expander(conf.weather.icons.default),
            'image': path_expander(conf.weather.images.default),
            'icon': '01d',
        }],
        'main': {
            'temp': 'NA',
            'feels_like': 'NA',
            'temp_min': 'NA',
            'temp_max': 'NA',
            'pressure': 'NA',
            'humidity': 'NA',
        },
        'sys': {'country': 'NA'},
        'name': 'NA',
    }

    print(json.dumps(cache(conf.location, fallback, conf)))


if __name__ == '__main__':
    main()
