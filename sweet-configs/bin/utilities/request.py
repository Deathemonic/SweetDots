from datetime import datetime, timedelta
from typing import Any, Callable, Optional, Union

import requests
from requests_cache import CachedSession


def fetch_location() -> Optional[dict]:
    try:
        session = CachedSession(
            'location',
            use_cache_dir=True,
            stale_if_error=True,
            stale_while_revalidate=True,
        )

        response: Any = session.get(
            'https://api64.ipify.org?format=json'
        ).json()
        ip_address: Any = response['ip']
        response = session.get(f'https://ipapi.co/{ip_address}/json/')
        data: Any = response.json()

        if response.status_code == 429:
            raise requests.exceptions.ConnectionError

        return {
            'latitude': data.get('latitude'),
            'longitude': data.get('longitude'),
            'city': data.get('city'),
            'country': data.get('country_name'),
            'language': data.get('languages').split(',')[0],
        }

    except requests.exceptions.ConnectionError:
        return None


def fetch_link(
    link: str,
    filename: str,
    timeout: Union[str, int, float, None, timedelta, datetime] = None,
    callback: Optional[Callable] = None,
) -> Optional[Any]:
    try:
        session = CachedSession(
            filename,
            use_cache_dir=True,
            stale_if_error=True,
            stale_while_revalidate=True,
            expire_after=timeout,
        )
        data: Any = session.get(link)

        if data.status_code == 200:
            metadata: Any = data.json()

            if callback:
                metadata = callback(metadata)

            return metadata

        if data.status_code == 404:
            raise requests.exceptions.ConnectionError

    except requests.exceptions.ConnectionError:
        return None
