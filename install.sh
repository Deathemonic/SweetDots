#!/bin/bash


cache_dir="$HOME/.cache"
config_dir="$HOME/.config"
backups_dir="$HOME/.backups"


if ! command -v gum && command -v pacman >/dev/null; then
   sudo pacman -S gum
else
   echo && echo "Gum is not installed which is required"
   echo "Please check: https://github.com/charmbracelet/gum#installation" && echo
   exit 1
fi



gum style \
	--foreground 212 --border-foreground 212 --border double \
	--align center --margin "1 2" --padding "2 4" \
  'SweetDots' 'Dotfiles that are sweet to manage!'


starting () {
  first_choice=$(gum choose "Install" "Backup" "Fix" "Readme") >/dev/null
  gum spin --spinner dot --title "Working on it..." -- sleep 1

  case $first_choice in
    Install)
      clear
      if ! command -v pacman >/dev/null; then
        echo '{{ Color "99" "It seams that you are not on" }} {{ Bold "Archlinux," }} {{ Color "99" "will now fallback to simple install" }}' | gum format -t template
        echo
      fi
      gum confirm 'Are you sure you want to proceed?' && setting_up || exit 1
    ;;
    Backup)
      gum confirm 'Do you want to proceed?'
    ;;
  esac
}


setting_up () {
  echo
  [[ ! -d $HOME/.cache ]] && mkdir -p "$cache_dir"
  [[ ! -d $HOME/.backups ]] && mkdir -p "$backups_dir"
  [[ ! -d /usr/share/xsessions ]] && sudo mkdir -p /usr/share/xsessions/
  gum spin --spinner dot --title "Setting it up..." -- sleep 2
  echo '{{ Bold "Done" }}' | gum format -t template && sleep 1
  echo
  clear
  installing_aurhelper
}


installing_core () {
  packages=$(awk '{printf("%s ", $0)} END {printf("\n")}' packages.txt)
  echo "sudo pacman -S $packages"
}


installing_aurhelper () {
  if [[ ! -f "$HOME/.cache/packages.txt" ]]; then
    echo '{{ Color "99" "packages.txt was not found select where its located" }}' | gum format -t template
    packages=$(awk '{printf("%s ", $0)} END {printf("\n")}' "$(gum file "$HOME" -a --file)")
    clear
  else
    packages=$(awk '{printf("%s ", $0)} END {printf("\n")}' "$HOME/.cache/packages.txt")
  fi

  if ! command -v yay && ! command -v paru; then
    echo && echo '{{ Color "99" "Cant find a AUR Helper, Installing..." }}' | gum format -t template && sleep 1

    clear

    echo && echo '{{ Color "99" "Pick a AUR Helper" }}' | gum format -t template && echo

    choice=$(gum choose "Paru" "Yay") >/dev/null
    case $choice in
      Paru)
        clear
        cd "$cache_dir" || return
        git clone https://aur.archlinux.org/paru-bin.git
        cd paru-bin || return
        makepkg -si
      ;;
      Yay)
        cd "$cache_dir" || return
        git clone https://aur.archlinux.org/yay-bin.git
        cd yay-bin || return
        makepkg -si
      ;;
    esac
  else
    command -v paru >/dev/null && paru -S "$packages" || command -v yay >/dev/null && yay -S "$packages"
    echo && echo '{{ Bold "Done" }}' | gum format -t template && sleep 1
  fi
}


installing_windowmanager () {
  clear
  echo && echo '{{ Color "99" "Choose your display server" }}' | gum format -t template && echo

  display_server=$(gum confirm "Choose your display server" --affirmative="Wayland" --negative="Xorg")
  if $display_server; then
    clear
    echo && echo '{{ Color "99" "Choose your window manager" }}' | gum format -t template && echo
    windowmanagers=$(gum choose "River" "Hyprland" "Sway" "Newm" --no-limit) >/dev/null
    echo "$windowmanagers"
  else
    clear
    echo && echo '{{ Color "99" "Choose your window manager" }}' | gum format -t template && echo
    windowmanagers=$(gum choose "BSPWM" "BerryWM" "i3-gaps" "LeftWM" --no-limit) >/dev/null
    echo "$windowmanagers"
  fi
}
