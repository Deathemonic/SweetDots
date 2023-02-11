#!/usr/bin/env python

import sys
import os

from argparse import ArgumentParser
from pathlib import Path
from shlex import split
from subprocess import run

sys.path.insert(1, f"{Path(__file__).resolve().parent}/../system")
import utils  # type: ignore


def command(show: str, cmd: list, app: str, terminal: str = "alacritty", **kwargs) -> list[str]:
    parameters = {
        "rofi": [
            "-show",
            show,
            "-modi",
            kwargs.get("modi", show),
            "-scroll-method",
            "0",
            "-drun-match-field",
            "all",
            "-drun-display-format",
            "{name}",
            "-no-drun-show-actions",
            "-terminal",
            terminal,
        ],
        "wofi": [
            "--show",
            show,
            "--term",
            terminal,
            "--gtk-dark",
            "--conf",
            kwargs.get("config", ""),
            "--style",
            kwargs.get("style", ""),
            "--color",
            kwargs.get("color", ""),
        ],
    }
    cmd.extend(parameters.get(app, "rofi"))
    return cmd


def passer(conf: str, cmd: list, app: str) -> None | list[str]:
    if app == "rofi" and conf.endswith(".rasi"):
        return cmd.extend(["-theme", conf])
    return cmd.extend([])


def arguments():
    parser = ArgumentParser(description="a simple launcher script")
    parser.add_argument("modi", help="specify which modi to show")
    return parser.parse_args()


def main():
    term, launcher, app, args = (
        utils.config.menu.get("terminal", "alacritty"),
        utils.config.menu.launcher,
        utils.config.menu.get("app", "rofi"),
        arguments(),
    )
    cmd = split(app)

    try:
        session = os.environ["XDG_SESSION_TYPE"]
    except KeyError:
        print("XDG_SESSION_TYPE is not set")
        exit(1)

    if session == "wayland" and app == "wofi" and args.modi:
        run(
            command(
                args.modi,
                cmd,
                app,
                term,
                config=utils.path_expander(launcher.config),
                style=utils.path_expander(launcher.style),
                color=utils.path_expander(launcher.colors),
            )
            if app == "wofi"
            else command(
                args.modi,
                cmd,
                app,
                term,
                modi=utils.config.menu.modi,
                config=utils.passer(utils.path_expander(launcher.config, cmd, app)),
            )
        )
    else:
        run(
            command(
                args.modi,
                cmd,
                app,
                term,
                modi=utils.config.menu.modi,
                config=utils.passer(utils.path_expander(launcher.config, cmd, app)),
            )
        )


if __name__ == "__main__":
    main()
