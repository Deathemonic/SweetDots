#!/usr/bin/env --split-string=python -u

from argparse import ArgumentParser
from ast import dump
from json import dumps

import gi

gi.require_version('Playerctl', '2.0')
from gi.repository import GLib, Playerctl


def arguments():
    parser = ArgumentParser(description='a music script for waybar or polybar')
    parser.add_argument('-s', '--status', action='store_true', help='prints the status of the player')
    parser.add_argument('-t', '--text', action='store_true', help='prints the title and artist in a single string')
    parser.add_argument('-i', '--icon', action='store_true', help='prints the icon of the player status')
    parser.add_argument('-l', '--loop', action='store_true', help='loops the script and output a new string if theres a update')
    parser.add_argument('-n', '--space', action='store_true', help="don't add spacing on the text")
    return parser.parse_args()
    

def player_metadata(player, *other):
    metadata = {
        'text': 'Offline',
        'icon': '',
        'class': f'custom-playpause-{player.props.status.lower()}',
        'alt': player.props.player_name,
    }

    if 'mpris:trackid' in player.props.metadata.keys() and \
            '/ad/' in player.props.metadata['mpris:trackid']:
        metadata['text'] = 'Free Plan - Advertisement'
    elif player.get_artist() != '' and player.get_title() != '':
        metadata['text'] = f'{player.get_artist()} - {player.get_title()}'
    else:
        metadata['text'] = player.get_title()
    
    match player.props.status:
        case 'Playing':
            metadata['icon'] = ''
        case 'Paused':
            metadata['icon'] = ''
        case 'Stopped':
            metadata['icon'] = ''
        case _:
            metadata['icon'] = ''
    
    if args.status:
        print(player.props.status)
    elif args.text:
        if player.props.status == 'Stopped' or player.props.status == 'Paused' \
                and not args.space:
            metadata['text'] = f'      {player.props.status}      '
        elif args.space:
            metadata['text'] = player.props.status
        print(metadata['text'])
    elif args.icon:
        print(metadata['icon'])
    else:
        print(dumps(metadata))


def play(player, *_):
    player_metadata(player)

    
def player_listen(name):
    player = Playerctl.Player.new_from_name(name)
    player.connect('metadata', player_metadata, manager)
    player.connect('playback-status::playing', play, manager)
    manager.manage_player(player)


def player_null_check(player_manager) -> bool:
    if not len(player_manager.props.player_names):
        metadata = {
            'text': 'Offline',
            'icon': '',
            'class': 'custom-playpause-stopped',
            'alt': 'none',
        }
        if args.status:
            print('Stopped')
        elif args.text:
            if not args.space:
                metadata['text'] = f'    Offline    '
            print(metadata['text'])
        elif args.icon:
            print(metadata['icon'])
        else:
            print(dumps(metadata))
        return False
    return True


def appeared_vanished(player_manager, name):
    if player_null_check(player_manager):
        player_listen(name)


def main():
    loop = GLib.MainLoop()

    if player_null_check(manager):
        player = Playerctl.Player()
        player_metadata(player)
    
    if args.loop:
        try:
            loop.run()
        except (KeyboardInterrupt, Exception):
            loop.quit()
        

if __name__ == '__main__':
    args = arguments()

    manager = Playerctl.PlayerManager()
    manager.connect('name-appeared', appeared_vanished)
    manager.connect('name-appeared', appeared_vanished)
    [player_listen(name) for name in manager.props.player_names]

    main()
