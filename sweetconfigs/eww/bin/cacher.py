import utils

from datetime import datetime
from dbus import lowlevel, SessionBus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
from os import path
from pathlib import PosixPath
from sys import stderr
from typing import Callable


class Urgency:
    low = b'\x00'
    normal = b'\x01'
    critical = b'\x02'


class Eavesdropper:
    def __init__(self, callback: Callable = print, cache_dir: str = '/tmp'):
        self.callback = callback
        self.cache_dir = f'{path.expandvars(cache_dir)}/image-data'
        PosixPath(self.cache_dir).mkdir(parents=True, exist_ok=True)

    def message_callback(self, _, message: lowlevel.MethodCallMessage or lowlevel.MethodCallMessage):
        if type(message) != lowlevel.MethodCallMessage:
            return

        args_list = message.get_args_list()
        args_list = [utils.unwrap(item) for item in args_list]
        details = {
            'appname': args_list[0].strip() or 'Unknown',
            'summary': args_list[3].strip() or 'Summary Unavailable',
            'body': args_list[4].strip() or 'Body Unavailable',
            'id': f'{datetime.now():%s}',
            'urgency': 'Unknown',
        }

        if args_list[2].strip():
            if '/' in args_list[2] or '.' in args_list[2]:
                details['iconpath'] = args_list[2]
            else:
                details['iconpath'] = utils.get_icon_path(args_list[2])
        else:
            details['iconpath'] = utils.get_icon_path('custom-notification')
        if 'image-data' in args_list[6]:
            details['iconpath'] = f'{self.cache_dir}/{details["appname"]}-{details["id"]}.png'
            utils.save_img_byte(args_list[6]['image-data'], details['iconpath'])
        if 'value' in args_list[6]:
            details['progress'] = args_list[6]['value']

        self.callback(details)

    def eavesdrop(self, timeout: int or bool = False, timeout_callback: Callable = print):
        DBusGMainLoop(set_as_default=True)
        rules = {
            'interface': 'org.freedesktop.Notifications',
            'member': 'Notify',
            'eavesdrop': 'true'
        }
        bus = SessionBus()

        bus.add_match_string(','.join([f'{key}={value}' for key, value in rules.items()]))
        bus.add_message_filter(self.message_callback)

        try:
            loop = GLib.MainLoop()
            if timeout:
                GLib.set_timeout(timeout, timeout_callback)
            loop.run()
        except (KeyboardInterrupt, Exception) as e:
            stderr.write(f'{e}\n')
            bus.close()
