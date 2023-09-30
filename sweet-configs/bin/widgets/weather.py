import logging
import sys
import pathlib
import urllib.parse
from typing import Optional

from dynaconf.vendor.box import BoxKeyError

sys.path.insert(1, str(pathlib.Path(__file__).resolve().parent.parent.joinpath('core')))
from utils import fetch_link, fetch_location, config, path_expander  # noqa: E402


def format_api(option: Optional[dict]) -> Optional[str]:
    api: str = f'https://api.openweathermap.org/data/2.5/weather?appid={config().tokens.openweathermap}'
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
        params['units'] = config().weather.units

    params_str: str = urllib.parse.urlencode(params)

    return f'{api}&{params_str}' if params else None


def assign(icon_name: str, icons: dict) -> str:
    try:
        return path_expander(icons[icon_name])

    except KeyError:
        return path_expander(icons['default'])


def cache(settings: dict, fallback: dict) -> Optional[dict]:
    location: Optional[dict] = (
        fetch_location() if config().location.get('auto_locate', True) else settings
    )
    api: str | None = format_api(location)

    def callback(data: dict) -> dict:
        for name in range(len(data['weather'])):
            data['weather'][name]['glyph'] = assign(
                data['weather'][0]['icon'], config().weather.icons
            )
            data['weather'][name]['image'] = assign(
                data['weather'][0]['icon'], config().weather.images
            )

        return data

    if api is None:
        logging.error('Unable to fetch api.')
        exit(1)

    if fetch_location() is None:
        return fallback

    return fetch_link(api, 'weather', 1, callback)


def main() -> None:
    fallback: dict = {
        'weather': [{
            'main': 'NA',
            'glyph': path_expander(config().weather.icons.default),
            'image': path_expander(config().weather.images.default),
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

    print(cache(config().location, fallback))


if __name__ == '__main__':
    main()
