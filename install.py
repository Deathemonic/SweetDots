#!/usr/bin/env python3

# Work in Progress, not intended to be used.

import os
import subprocess


def fetch_req():
  print('Installing nessary python packages')
  
  subprocess.call([sys.executable, '-m', 'pip', 'install', '-r', './requirements.txt', '--upgrade'])


def menu():
  print('pass')


def logger():
  pass


def fetch_pkgs():
  pkgs = '''
    polybar-git rofi rofi-emoji rofi-greenclip alacritty picom-arian8j2-git dunst-git eww-git ffmpeg \
    pipewire pipewire-alsa pipewire-pulse pipewire-jack wireplumber alsa-utils pamixer \
    bluez bluez-utils \
    mpd mpdris2-git \
    brightnessctl playerctl light lm_sensors wmctrl \
    feh i3lock-color sddm yad xclip maim slop gpick xfce4-power-manager zscroll-git neovim viewnior stalonetray redshift \
    ttf-sarasa-gothic ttf-jetbrains-mono ttf-roboto nerd-fonts-jetbrains-mono \
    gtk3 gtk-engine-murrine gnome-themes-extra papirus-icon-theme
  '''

class Installer:
  pass


def copy_files():
  pass


if __name__ == '__main__':
  pass
