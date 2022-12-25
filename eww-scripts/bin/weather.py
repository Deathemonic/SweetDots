from argparse import ArgumentParser
from datetime import datetime
from json import dumps, loads
from pathlib import PosixPath

from utils import config, auto_locate, fetch_save, path_expander


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
        return path_expander(icons[icon_name])
    except KeyError:
        return path_expander(icons['default'])


def cache(setting: dict) -> dict | str | None:
    location = auto_locate(CACHE_PATH) if config.location.auto_locate else setting
    
    call_api = fetch_api(location)
    cache_file = PosixPath(f'{CACHE_PATH}/weather-{datetime.now():%F-%I}.json')

    def callback(data: dict) -> dict:
        for name in range(len(data['weather'])):
            data['weather'][name]['glyph'] = assign(data['weather'][0]['icon'], config.weather.icons)
            data['weather'][name]['image'] = assign(data['weather'][0]['icon'], config.weather.images)
        return data

    if not cache_file.is_file() and not fetch_save(call_api, str(cache_file), callback):
        return FALLBACK
    return loads(cache_file.read_text())


def arguments():
    parser = ArgumentParser()
    parser.add_argument('-f', '--fetch', action='store_true', help='fetch the weather in a json format')
    parser.add_argument('-g', '--gist', action='store', help='fetch a specific info from the weather json')
    return parser.parse_args()


def main():
    metadata, args = (
        cache(config.location),
        arguments()
    )

    if args.fetch is True:
        print(dumps(metadata))
    elif args.gist:
        info = [metadata['weather'][index][args.gist] for index in range(len(metadata['weather']))]
        print(', '.join(info) if len(info) > 2 else ' and '.join(info))


if __name__ == '__main__':
    CACHE_PATH = path_expander(config.location.cache_dir)
    PosixPath(CACHE_PATH).mkdir(parents=True, exist_ok=True)
    
    FALLBACK = {
        'weather': [
            {
                'main': 'NA',
                'glyph': path_expander(config.weather.icons.default),
                'image': path_expander(config.weather.images.default),
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
    
    main()
    