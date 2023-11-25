import asyncio
import pathlib
from datetime import datetime
from enum import Enum
from typing import Any, Callable

from dbus_next.aio.message_bus import MessageBus
from dbus_next.constants import MessageType
from dbus_next.message import Message


class Urgency(Enum):
    LOW = b'\x00'
    NORMAL = b'\x01'
    CRITICAL = b'\x02'


loop = asyncio.get_event_loop()


class Eavesdropper:
    def __init__(
        self, callback: Callable = print, cache_dir: str = '/tmp'
    ) -> None:
        self.callback: Callable = callback
        self.cache_dir: pathlib.PosixPath = pathlib.PosixPath(
            cache_dir
        ).joinpath('image-data')
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _message_callback(self, message: Message) -> None:
        if message.message_type != MessageType.METHOD_CALL:
            return

        notify_data: list[Any] = message.body
        details: dict[str, Any] = {
            'appname': notify_data[0] or 'Unknown',
            'summary': notify_data[3] or 'Summary Unavailable.',
            'body': notify_data[4] or 'Body Unavailable.',
            'id': datetime.now().strftime('%s'),
            'urgency': 'low',
        }

        if 'urgency' in notify_data[6]:
            details['urgency'] = notify_data[6]['urgency']

        # TODO: set a fallback at utils that get the gtk icon path
        if notify_data[2]:
            if '/' in notify_data[2] or '.' in notify_data[2]:
                details['iconpath'] = notify_data[2]
        #   else:
        #         # and if the iconpath is just a string that has no extensions or,
        #         # a pathlike structure like: 'bell' or 'custom-folder-bookmark'
        #         # it might have a dash (-) sign but not all the time.
        #         # then fetch that actual path of that icon as that is a part of the
        #         # icon theme naming convention and the current icon theme should probably have it
        #         details['iconpath'] = utils.get_gtk_icon_path(args_list[2])
        # else:
        #     # if there are no icon hints then use fallback (generic bell)
        #     details['iconpath'] = utils.get_gtk_icon_path(
        #         'custom-notification'
        #     )

        # TODO: add a raw image cacher
        # if 'image-data' in args_list[6]:
        #     # capture the raw image bytes and save them to the cache_dir/x.png path
        #     details[
        #         'iconpath'
        #     ] = f"{self.cache_dir}/{details['appname']}-{details['id']}.png"
        #     utils.save_img_byte(
        #         args_list[6]['image-data'], details['iconpath']
        #     )

        if 'value' in notify_data[6]:
            details['progress'] = notify_data[6]['value']

        self.callback(details)

    async def eavesdrop(
        self, timeout: int | bool = False, timeout_callback: Callable = print
    ) -> None:
        rules: dict[str, str] = {
            'interface': 'org.freedesktop.Notifications',
            'member': 'Notify',
            'eavesdrop': 'true',
        }
        match_rule: str = ','.join(
            f'{key}={value}' for key, value in rules.items()
        )

        bus: MessageBus = await MessageBus().connect()

        bus.add_message_handler(self._message_callback)
        msg = Message(
            destination='org.freedesktop.DBus',
            path='/org/freedesktop/DBus',
            interface='org.freedesktop.DBus',
            member='AddMatch',
            signature='s',
            body=[match_rule],
        )
        await bus.call(msg)

        # await asyncio.sleep(timeout if isinstance(timeout, int) else 0)
        # timeout_callback()
        # await asyncio.Future()


async def main() -> None:
    await Eavesdropper(
        cache_dir='/home/zinth/Documents/SweetDots/sweet-configs'
    ).eavesdrop()
    await loop.create_future()


loop.run_until_complete(main())
