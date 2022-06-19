#!/usr/bin/env python

import subprocess
import json
import re
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

def parse_icon_name(app_name):
  app_name = app_name.lower()
  if app_name in icon_names:
    return icon_names[app_name]
  if app_name.endswith('telegram_desktop'):
    return 'telegram'
  if app_name.startswith('gimp'):
    return 'gimp'
  return app_name

def get_icon(app_name):
  icon_info = icon_theme.lookup_icon(parse_icon_name(app_name), 48, 0)
  if icon_info == None:
    print("Failed to get icon for: " + app_name)
  return icon_info.get_filename() if icon_info != None else default_icon_file

def get_cons(tree):
  if len(tree.get('nodes')) == 0 and len(tree.get('floating_nodes')) == 0 and (tree.get('type') == 'con' or tree.get('type') == 'floating_con'):
    return [tree]
  nodes = []
  for node in tree.get('floating_nodes'):
    cons = get_cons(node)
    nodes += cons
  for node in tree.get('nodes'):
    cons = get_cons(node)
    nodes += cons
  return nodes

def show_wofi(windows):
  command = 'wofi -c $HOME/.config/sway/wofi/window -s $HOME/.config/sway/wofi/style.css -I -d -i -b -k /dev/null -p "Window" 2>/dev/null'
  process = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
  (result, _) = process.communicate(input='\n'.join(windows).encode())
  return result


def get_tree():
  sway_tree = subprocess.check_output(['swaymsg', '-rt', 'get_tree'])
  return json.loads(sway_tree)

def get_windows():
  cons = get_cons(get_tree())
  windows = []
  for con in cons:
    name = con['name']
    if len(name) > 70:
      name = name[:67]+"..."
    app_id = con.get('app_id')
    if app_id == None:
      window_prop = con.get('window_properties')
      if window_prop != None:
        app_id = window_prop.get('instance')
    
    if app_id != None:
      app_icon = get_icon(app_id)
    else:
      app_icon = default_icon_file

    windows.append("img:id=" + str(con.get('id')) +":img:" + app_icon + ":text:" + name)
  return windows

def parse_selection(selection):
  id_search = re.search('id=([0-9]*):', selection, re.IGNORECASE)
  if id_search:
    return id_search.group(1)
  return None

def switch_window(id):
  command="swaymsg [con_id={}] focus".format(id)
  process = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE)
  process.communicate()

if __name__ == "__main__":
  icon_theme = Gtk.IconTheme.get_default()
  default_icon = icon_theme.lookup_icon("preferences-system-windows", 48, 0)
  default_icon_file = ""
  if default_icon:
    default_icon_file = default_icon.get_filename()

  icon_names = {
    "code": "visual-studio-code",
    "qt5ct": "preferences-desktop-theme"
  }

  windows = get_windows()
  selection = show_wofi(windows)
  con_id = parse_selection(str(selection))
  if con_id:
    switch_window(con_id)
