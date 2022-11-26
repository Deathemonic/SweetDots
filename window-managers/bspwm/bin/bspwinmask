#!/usr/bin/env bash

## Copyright (C) 2020-2022 Aditya Shakya <adi1090x@gmail.com>
## Everyone is permitted to copy and distribute copies of this file under GNU-GPL3

masked=$(bspc query -N -n .hidden -d focused)

if [ -z "$masked" ]; then
	bspc node focused -g hidden=on
else
	bspc node "$masked" -g hidden=off
fi
