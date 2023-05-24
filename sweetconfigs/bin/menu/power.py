#!/usr/bin/env python

import sys
import logging
import os

from argparse import ArgumentParser
from enum import Enum
from pathlib import Path
from shlex import split
from subprocess import run
from time import sleep

from pydbus import SystemBus
from yad import YAD

sys.path.insert(1, f"{Path(__file__).resolve().parent}/../system")
import utils  # type: ignore


class Actions:
    def __init__(self):
        self.dialog = YAD().execute(
            args=[
                '--title="Confirm?"',
                "--center",
                "--fixed",
                "--undecorated",
                "--button=Yes:0",
                "--button=No:1",
                '--text="Are you sure?"',
                "--text-align=center",
            ],
        )
        self.proxy = SystemBus().get("org.freedesktop.login1", "/org/freedesktop/login1")

    def shutdown(self):
        if self.dialog[1] == 0 and self.proxy.CanPowerOff() == "yes":
            countdown(3, "Shutting Down")
            self.proxy.PowerOff(False)
        elif self.proxy.CanPowerOff in ["no", "na", "challenge"]:
            logging.error("Permission not set")
        elif self.dialog[1] == 1:
            exit(1)

    def reboot(self):
        if self.dialog[1] == 0 and self.proxy.CanReboot() == "yes":
            countdown(3, "Rebooting")
            self.proxy.Reboot(False)
        elif self.proxy.CanReboot() in ["no", "na", "challenge"]:
            logging.error("Permission not set")
        elif self.dialog[1] == 1:
            exit(1)

    def suspend(self):
        if self.dialog[1] == 0 and self.proxy.CanSuspend() == "yes":
            countdown(3, "Rebooting")
            self.proxy.Suspend(False)
        elif self.proxy.CanSuspend() in ["no", "na", "challenge"]:
            logging.error("Permission not set")
        elif self.dialog[1] == 1:
            exit(1)

    def logout(self):
        if self.dialog[1] == 0:
            utils.notify(app="System", summary="Power", body="Logging Out", urgent=0)
            self.proxy.TerminateSession(os.environ["XDG_SESSION_ID"])
        elif self.dialog[1] == 1:
            exit(1)


def countdown(count: int, message: str) -> None:
    for sec in range(count, 0, -1):
        utils.notify(
            app="Countdown", summary="Power", body=f"{message} in: {sec}", urgent=0
        )
        sleep(1)


def command(lines: int, cmd: list[str], app: str, **kwargs) -> list[str]:
    parameters = {
        "rofi": [
            "-dmenu",
            "-p",
            kwargs.get("promt", "Which action do you prefer"),
            "-selected-row",
            "0",
            "-l",
            f"{lines}",
        ],
        "wofi": [
            "--dmenu",
            "-p",
            kwargs.get("promt", "Which action do you prefer"),
            "-L",
            f"{lines}",
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


def get_selection() -> None:
    power_conf, app = (
        utils.config.menu.power,
        utils.config.menu.get("app", "rofi"),
    )
    cmd = split(app)

    class Choices(Enum):
        shutdown = power_conf.icons.get("shutdown", "S")
        reboot = power_conf.icons.get("reboot", "R")
        lock = power_conf.icons.get("lock", "L")
        suspend = power_conf.icons.get("suspend", "S")
        logout = power_conf.icons.get("logout", "E")

    caller = run(
        ["echo", "-e", "\n".join(c.value for c in Choices)], capture_output=True
    ).stdout

    chosen = (
        run(
            command(
                len(Choices),
                cmd,
                app,
                config=utils.path_expander(power_conf.config),
                style=utils.path_expander(power_conf.style),
                color=utils.path_expander(power_conf.colors),
            ),
            input=caller,
            capture_output=True,
        )
        .stdout.decode("utf-8")
        .strip()
        if app == "wofi"
        else run(
            command(
                len(Choices),
                cmd,
                app,
                config=passer(utils.path_expander(power_conf.config), cmd, app),
            ),
            input=caller,
            capture_output=True,
        )
        .stdout.decode("utf-8")
        .strip()
        if app in ["rofi", "wofi"]
        else exit(1)
    )

    match chosen:
        case Choices.shutdown.value:
            Actions().shutdown()
        case Choices.reboot.value:
            Actions().reboot()
        case Choices.suspend.value:
            Actions().suspend()
        case Choices.logout.value:
            Actions().logout()


def arguments():
    parser = ArgumentParser(description="a simple power script")
    parser.add_argument(
        "-s", "--shutdown", action="store_true", help="shutdown the system in 3 seconds"
    )
    parser.add_argument(
        "-r",
        "--reboot",
        action="store_true",
        help="reboots the system in 3 seconds",
    )
    parser.add_argument(
        "-d",
        "--suspend",
        action="store_true",
        help="suspend the system in 3 seconds",
    )
    parser.add_argument(
        "-l", "--logout", action="store_true", help="logout of the session"
    )
    parser.add_argument("-c", "--lock", action="store_true", help="lock the system")
    parser.add_argument(
        "-m",
        "--menu",
        action="store_true",
        help="launch rofi or wofi as it's fontend (only works if you have sweetconfigs)",
    )
    return parser.parse_args()


def main() -> None:
    args = arguments()

    if args.shutdown:
        Actions().shutdown()
    elif args.reboot:
        Actions().reboot()
    elif args.suspend:
        Actions().suspend()
    elif args.logout:
        Actions().logout()
    elif args.menu:
        get_selection()


if __name__ == "__main__":
    main()
