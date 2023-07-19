#!/bin/sh

files="$HOME/.config/sweet-configs/panels/waybar/config.json $HOME/.config/sweet-configs/panels/waybar/style.css"
config="$HOME/.config/sweet-configs/panels/waybar/config.json"
style="$HOME/.config/sweet-configs/panels/waybar/style.css"

trap "killall waybar" EXIT

while true; do
    waybar -c $config -s $style &
    inotifywait -e create,modify $files
    killall waybar
done
