from argparse import ArgumentParser, Namespace

from dynaconf import LazySettings
from dynaconf.vendor.box import BoxKeyError
from utilities.utils import config


def formats(conf: LazySettings) -> None:
    format: dict[str, str] = {
        'screenshot': '(preview :identity "{identity}" :close_action "{close_action}" :limit_body "{limit_body}" :limit_summary "{limit_summary}" :delete "{delete}" :open "{open}" :summary "{summary} :image "{image}" :appname "{appname}" :image_height 250 :image_width 100 :urgency "{urgency}" :close_icon "{close_icon}" :timestamp "{timestamp}")',
        'notify-send': '(image :identity "{identity}" :close_action "{close_action}" :limit_body "{limit_body}" :limit_summary "{limit_summary}" :summary "{summary}" :body "{body}" :close_icon "{close_icon}" :image_height {image_height} :image_width {image_width} :image "{image}" :appname "{appname}" :icon "{icon}" :icon_height {icon_height} :icon_width {icon_width} :timestamp "{timestamp}" :urgency "{urgency}")',
        'empty': '(box :class "disclose-empty-box" :height 750 :orientation "vertical" :space-evenly false (image :class "disclose-empty-banner" :valign "end" :vexpand true :path "./assets/nonotifications.png" :image-width 250 :image-height 250) (label :vexpand true :valign "start" :wrap true :class "disclose-empty-labelf" :text "{fallback_message}"))',
    }

    try:
        format.update(conf.formats)
        print(format)

    except BoxKeyError:
        print(format)


def arguments() -> Namespace:
    parser = ArgumentParser(description='a notification logger')

    parser.add_argument(
        '-w',
        '--watch',
        action='store_true',
        help='prints out the notification logs in real time',
    )

    parser.add_argument(
        '-r',
        '--remove-id',
        help='remove a notification by given id',
    )

    parser.add_argument(
        '-c',
        '--clear',
        action='store_true',
        help='clear the entire notifications',
    )

    parser.add_argument(
        '-i',
        '--init',
        action='store_true',
        help='initialize notification logging',
    )

    return parser.parse_args()


def main():
    conf: LazySettings = config().notifications
    formats(conf)


if __name__ == '__main__':
    main()
