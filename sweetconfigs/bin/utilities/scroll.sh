#!/bin/bash

current_dir="$(dirname "$(readlink -m "${0}")")"
case $1 in
    --zscroll | -z)
        zscroll -l 20 \
            --delay 1 \
            --scroll-padding " | " \
            --match-command "$current_dir/music.py -s"
            --match-text "Playing" "--scroll 1" \
            --match-text "Paused" "--scroll 0" \
            --match-text "Stopped" "--scroll 0" \
            --update-check true "$current_dir/music.py -t -n"
        wait
    ;;
    --roller | -r)
        $current_dir/music.py -t -l | roller -t 20 -i 1000 -s " | "
    ;;
esac
