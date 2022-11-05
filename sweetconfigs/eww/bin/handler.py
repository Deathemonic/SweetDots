
import utils

from cacher import Urgency
from datetime import datetime
from pathlib import Path


def formater(formats, attributes: dict):
    attributes['TIMESTAMP'] = f'{datetime.now():{attributes["TIMESTAMP_FORMAT"]}}'
    match attributes['urgency']:
        case Urgency.low:
            attributes['URGENCY'] = 'LOW'
        case Urgency.normal:
            attributes['URGENCY'] = 'NORMAL'
        case Urgency.critical:
            attributes['URGENCY'] = 'CRITICAL'
        case _:
            attributes['URGENCY'] = 'NORMAL'

    attributes['body'] = attributes['body'].replace('\n', ' ')
    attributes['summary'] = attributes['summary'].replace('\n', ' ')

    if utils.contains_pango(attributes['body']):
        attributes['body'] = utils.strip_pango_tags(attributes['body'])
    if utils.contains_pango(attributes['summary']):
        attributes['summary'] = utils.strip_pango_tags(attributes['summary'])

    if "'" in attributes['body']:
        attributes['body'] = attributes['body'].replace("'", "\\'")
    if "'" in attributes['summary']:
        attributes['summary'] = attributes['summary'].replace("'", "\\'")

    attributes['SUMMARY_LIMITER'] = ''
    sum_lang_check = utils.non_eng(attributes['summary'][:15])

    if sum_lang_check['CJK']:
        attributes['SUMMARY_LIMITER'] = 14
    elif sum_lang_check['CYR']:
        attributes['SUMMARY_LIMITER'] = 30

    attributes['BODY_LIMITER'] = ''
    body_lang_check = utils.non_eng(attributes['body'][:70])
    if body_lang_check['CJK']:
        attributes['BODY_LIMITER'] = 80
    elif body_lang_check['CYR']:
        attributes['BODY_LIMITER'] = 110
    else:
        attributes['BODY_LIMITER'] = 100

    match attributes['appname']:
        case 'notify-send':
            notify_send_handler(formats, attributes)
        case 'screenshot':
            screenshot_handler(formats, attributes)
        case 'Spotify':
            spotify_handler(formats, attributes)
        case _:
            default_handler(formats, attributes)


def default_handler(formats, attributes: dict) -> str:
    attributes['appname'] = utils.prettify_name(attributes['appname'])
    return formats['default'] % attributes


def notify_send_handler(formats, attributes: dict) -> str:
    attributes['appname'] = utils.prettify_name(attributes['appname'])
    return formats['notify-send'] % attributes


def screenshot_handler(formats, attributes: dict) -> str:
    current_file = Path(__file__).resolve().parent
    attributes['DELETE'] = f'rm -f \\"{attributes["iconpath"]}\\" && {current_file}/notification.py -r {attributes["id"]}'
    attributes['OPEN'] = f'xdg-open \\"{attributes["iconpath"]}\\"'

    attributes['appname'] = utils.prettify_name(attributes['appname'])
    return formats['screenshot'] % attributes


def spotify_handler(formats, attributes: dict) -> str:
    return formats['Spotify'] % attributes
