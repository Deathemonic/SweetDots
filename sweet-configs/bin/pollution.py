import json
import urllib.parse
from datetime import timedelta
from typing import Any, Optional

from dynaconf import LazySettings
from dynaconf.vendor.box import BoxKeyError

from utilities.utils import config
from utilities.request import fetch_link, fetch_location


def format_api(option: Optional[dict], conf: LazySettings) -> Optional[str]:
    api: str = f'https://api.openweathermap.org/data/2.5/air_pollution?appid={conf.tokens.openweathermap}'
    params: dict = {}

    if option is None:
        return None

    try:
        if not option['latitude'] or not option['longitude']:
            raise BoxKeyError

        params['lat'] = option['latitude']
        params['lon'] = option['longitude']

    except BoxKeyError:
        if 'city' not in option and 'zip_code' not in option:
            return None

        geo: str = ''
        if 'city' in option:
            params['q'] = option['city']
            geo: str = 'direct'

        elif 'zip_code' in option:
            params['zip'] = option['zip_code']
            geo: str = 'zip'

        geocode_api: str = f'https://api.openweathermap.org/geo/1.0/{geo}?appid={conf.tokens.openweathermap}&limit=1'
        params_str: str = urllib.parse.urlencode(params)
        response: Optional[Any] = fetch_link(
            f'{geocode_api}&{params_str}', 'geocode', timedelta(days=1)
        )

        if response is None:
            return None

        params['lat'] = response[0]['lat']
        params['lon'] = response[0]['lon']
        params.pop('q', None)

    params_str: str = urllib.parse.urlencode(params)
    return f'{api}&{params_str}' if params else None


def cache(settings: dict, conf: LazySettings, fallback: dict) -> Optional[Any]:
    location: Optional[dict] = (
        fetch_location()
        if conf.location.get('auto_locate', True)
        else settings
    )
    api: Optional[str] = format_api(location, conf)

    def callback(data: dict) -> dict:
        data['icons'] = conf.pollution.icons
        return data

    if api is None:
        return fallback

    return fetch_link(api, 'pollution', timedelta(hours=1), callback)


def main() -> None:
    conf: LazySettings = config()

    fallback: dict = {
        'list': [
            {
                'main': {'aqi': 'N/A'},
                'components': {
                    'co': 'N/A',
                    'no': 'N/A',
                    'no2': 'N/A',
                    'o3': 'N/A',
                    'so2': 'N/A',
                    'pm2_5': 'N/A',
                    'pm10': 'N/A',
                    'nh3': 'N/A',
                },
                'dt': 'N/A',
            }
        ],
    }

    print(json.dumps(cache(conf.location, conf, fallback)))


if __name__ == '__main__':
    main()
