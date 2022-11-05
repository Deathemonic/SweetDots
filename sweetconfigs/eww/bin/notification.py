#!/usr/bin/env --split-string=python -u

import utils

from argparse import ArgumentParser
from cacher import Eavesdropper
from handler import formater
from json import dumps
from os import path
from pathlib import Path, PosixPath
from sys import stdout


def arguments():
    parser = ArgumentParser(description='notification logger')
    parser.add_argument('-l', '--listen', action='store_true', help='listen to the notification logs via yuck literals')
    parser.add_argument('-r', '--rmid', action='store', help='removes a id from the notification cache')
    parser.add_argument('-R', '--rm', action='store', help='removes a line from the notification cache')
    parser.add_argument('-s', '--stats', action='store_true', help='prints the stats from the notification cache')
    parser.add_argument('-c', '--clear', action='store_true', help='clears everything including cache')
    parser.add_argument('-q', '--quote', action='store_true', help='generate a random quote or use the default quote')
    parser.add_argument('-d', '--daemon', action='store_true',
                        help='initialize the script or else the logging wont work')
    return parser.parse_args()


def main():
    current_dir = Path(__file__).resolve().parent
    cache_file = f'{path.expandvars(cache_path)}/notifications.txt'
    quote_file = f'{path.expandvars(cache_path)}/quotes.txt'
    utils.make_parents(cache_file)
    utils.make_parents(quote_file)

    formats = {
        'empty': f'(box :class "notify-empty-box" :height 750 :orientation "v" :space-evenly false (image :class "notify-empty-icon" :valign "end" :vexpand true :path "{path.expandvars(utils.config.notification.empty_icon)}" :image-width 250 :image-height 250) (label :vexpand true :valign "start" :wrap true :class "notify-empty-label" :text "{utils.gen_quote(quote_file, quote)}"))',
        'default': f'(notify_card :identity ":::###::::XXXWWW%(id)s===::" :close_action "{current_dir}/combine.sh" :limit_body "%(BODY_LIMITER)s" :limit_summary "%(SUMMARY_LIMITER)s" :summary "%(summary)s" :body "%(body)s" :close "X" :image_height 100 :image_width 100 :image "%(iconpath)s" :appname "%(appname)s" :icon "%(iconpath)s" :icon_height 32 :timestamp "%(TIMESTAMP)s" :urgency "%(URGENCY)s")',
        'notify-send': f'(notify_card :identity ":::###::::XXXWWW%(id)s===::" :close_action "{current_dir}/combine.sh" :limit_body "%(BODY_LIMITER)s" :limit_summary "%(SUMMARY_LIMITER)s" :summary "%(summary)s" :body "%(body)s" :close "X" :image_height 100 :image_width 100 :image "%(iconpath)s" :appname "%(appname)s" :icon "%(iconpath)s" :icon_height 32 :timestamp "%(TIMESTAMP)s" :urgency "%(URGENCY)s")',
        'screenshot': f'(notify_img :identity ":::###::::XXXWWW%(id)s===::" :close_action "{current_dir}/combine.sh" :limit_body "%(BODY_LIMITER)s" :limit_summary "%(SUMMARY_LIMITER)s" :delete "%(DELETE)s" :open "%(OPEN)s" :summary "%(summary)s" :body "%(body)s" :close "X" :image_height 100 :image_width 100 :image "%(iconpath)s" :appname "%(appname)s" :icon "%(iconpath)s" :icon_height 32 :timestamp "%(TIMESTAMP)s" :urgency "%(URGENCY)s")',
        'Spotify': f'(notify_card :class "spotify" :identity ":::###::::XXXWWW%(id)s===::" :close_action "{current_dir}/combine.sh" :limit_body "%(BODY_LIMITER)s" :limit_summary "%(SUMMARY_LIMITER)s" :summary "%(summary)s" :body "%(body)s" :close "X" :image_height 100 :image_width 100 :image "%(iconpath)s" :appname "%(appname)s" :icon "%(iconpath)s" :icon_height 32 :timestamp "%(TIMESTAMP)s" :urgency "%(URGENCY)s")',
    }

    if args.daemon:
        def master_callback(details: dict):
            details['TIMESTAMP_FORMAT'] = timestamp
            if not exclude or details['appname'] not in exclude:
                saved_path = formater(formats, details)
                utils.file_add_line(cache_file, saved_path, history_limit)

        Eavesdropper(master_callback, cache_path).eavesdrop()
    elif args.listen:
        utils.watcher(
            cache_file,
            lambda contents: stdout.write(
                '(box :spacing 20 :orientation "v" :space-evenly false ' +
                contents.replace('\n', ' ') + ')\n'
                if contents.strip()
                else (
                        formats['empty'] + '\n'
                )
            ),
            interval
        )
    elif args.rmid:
        utils.matched_index_rm(cache_file, f':identity ":::###::::XXXWWW{args.rmid}===::"')
    elif args.rm:
        utils.rm_line(cache_file, int(args.rm))
    elif args.stats:
        stdout.write(
            dumps(
                utils.parse_and_print_stats(
                    PosixPath(cache_file).read_text()
                )
            ) + '\n'
        )
    elif args.clear:
        PosixPath(cache_file).write_text('')
    elif args.quote:
        stdout.write(utils.gen_quote(quote_file, quote))


if __name__ == '__main__':
    history_limit, cache_path, quote, interval, timestamp, exclude, args = (
        utils.config.notification.limit,
        utils.config.notification.cache_dir,
        utils.config.notification.empty_message,
        utils.config.notification.interval,
        utils.config.notification.timestamp,
        utils.config.notification.exclude_appnames,
        arguments()
    )

    main()
