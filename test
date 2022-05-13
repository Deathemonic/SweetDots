#!/bin/bash

read -p "[-] DO YOU WANT TO CONTINUE [Y/N] : " install

case $install in
    N*|n*)
    clear
    printf "${red}[!] Aborting!\n"
esac

case $install in
    Y*|y*) 
    mkdir -p $dir
    clear
    printf "${red}[!] If you are in archlinux or any archbased distro it will automatically install the needed dependencies if not it will just copy the files\n"
esac
