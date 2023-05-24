#!/bin/sh

files="$HOME/.config/sweetconfigs/bar/waybar/config.json $HOME/.config/sweetconfigs/bar/waybar/style.css"
config="$HOME/.config/sweetconfigs/bar/waybar/config.json"
style="$HOME/.config/sweetconfigs/bar/waybar/style.css"

trap "killall waybar" EXIT

while true; do
    waybar -c $config -s $style &
    inotifywait -e create,modify $files
    killall waybar
done
