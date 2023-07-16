<div align="center">
  <img src="https://user-images.githubusercontent.com/65948476/184596703-fdac6419-ed4a-4fd8-b2d3-1f35854d563e.png" width="500px" alt="logo">
  <h1>SweetBerry</h1>
  <p>A pastel themed rice 🍚</p>
  <h6>
    <a href="https://ko-fi.com/Deathemonic">Buy me a Coffee</a>
    ·
    <a href="https://github.com/Deathemonic/SweetDots/wiki">Wiki</a>
    ·
    <a href="https://github.com/Deathemonic/Pastel">Pastel</a>
    ·
    <a href="https://github.com/Deathemonic/SweetDots/projects">Projects</a>
  </h6>
  <p>
	  <a href="https://github.com/Deathemonic/SweetDots/stargazers">
		  <img alt="Stargazers" src="https://img.shields.io/github/stars/deathemonic/SweetDots?style=for-the-badge&logo=starship&color=FFFBDE&logoColor=FFDEDE&labelColor=212529"></a>
	  <a href="https://github.com/Deathemonic/SweetDots/issues">
		  <img alt="Issues" src="https://img.shields.io/github/issues/deathemonic/cat-dots?style=for-the-badge&logo=gitbook&color=DEFBFF&logoColor=FFDEDE&labelColor=212529"></a>
  </p>
</div>

## :question: <samp>ABOUT</samp>

<img alt="Rice Preview" align="right" width="400px" src="https://raw.githubusercontent.com/Deathemonic/SweetDots/xorg/.github/assets/unixporn.png"/>

Welcome, Thanks for droping by! This is my dotfiles that I made, it's a dotfiles design to be understandable and hackable by anyone and themed with [**SweetPastel**](https://github.com/SweetPastel).

Instead of making multiple ``Window Manager Configs`` with different style I opt in on just one style but it should be compatible to other ``Window Manage`` so if you switch to another ``Window Manager`` it should be the same style, plus it's less work. All the configs are stored in a folder so it won't conflict at your pre existing configs **(Except of the window managers they will conflict unless you backup your old files)**

## :books: <samp>WIKI</samp> <kbd>RECOMMENDED</kbd>
If you have problems or need some information about the dotfiles check [wiki page](https://github.com/Deathemonic/SweetDots/wiki), it provides extra information, some documentation, and a troubleshoot page

   <table align="right">
   <tr>
      <th align="center">
         <sup><sub>:warning: WARNING :warning:</sub></sup>
      </th>
   </tr>
   <tr>
      <td align="center">
         <sup>
            <sub>
               <samp>
                  THIS DOTFILES IS CONFIGURED AT 1080x800 WITH 96 DPI!
		  <br>
                  SOME STUFF MIGHT BREAK ON LOWER OR HIGHER
                  <p align="center">
                     RESOLUTIONS BUT WILL STILL WORK!
                  </p>
               </samp>
            </sub>
         </sup>
      </td>
   </tr>
   </table>

## :package: <samp>INSTALL</samp>

<details open>
	<summary><b><samp>AUTO INSTALL</samp></b></summary>
<br>

<kbd>RECOMMENDED</kbd>

Copy and paste this command at your **Terminal**
	
```sh
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Deathemonic/SweetDots/xorg/install)"
```

> **Note**: You need ``curl``, ``bash`` and ``git`` installed in your system. Also if you are not using ``archlinux`` the installer won't install the dependencies automatically you have to manually install them. Check out this [link](https://github.com/Deathemonic/SweetDots/wiki/Documentation#dependencies) for the list of dependencies

</details>

<details>
	<summary><b><samp>MANUAL INSTALL</samp></b></summary>
<br>

> **Note**: First up install the dependencies need if not the dotfiles doesn't work. Check out this [link](https://github.com/Deathemonic/SweetDots/wiki/Documentation#dependencies) for the list of dependencies

1. Download or Clone the repo and go to that directory
	
```sh
git clone https://github.com/Deathemonic/SweetDots -b xorg && cd SweetDots
```

2. Make a backup folder for the conflicting folders
	
```sh
mkdir ~/.backups
```
	
3. Move the conflicting folders to the backup folder depending if you have them

```sh
mv ~/.config/berry ~/.backups/
mv ~/.config/bspwm ~/.backups/
mv ~/.config/i3 ~/.backups/
mv ~/.config/leftwm ~/.backups/
```

4. Copy the ``sweetconfigs-xorg`` to your ``~/.config``
	
```sh
cp -rf sweetconfigs-xorg ~/.config/
```
	
5. Copy the window manager you config in your ``~/.config``

```sh
cp -rf window-managers/* ~/.config/
```
	
- If you have bspwm then copy ``cp -rf window-managers/bspwm`` to ``~/.config`` then you if you have bspwm and berry then copy both folders and etc.

```sh
cp -rf window-managers/berry ~/.config/
cp -rf window-managers/bspwm ~/.config/
cp -rf window-managers/i3 ~/.config/
cp -rf window-managers/leftwm ~/.config/
```

- If you have berry you may have to copy the ``berry.desktop`` in the xsessions folder in order for the display manager to see it

```sh
sudo cp misc/xsessions/berry.desktop /usr/share/xsessions
```

6. Change the scripts into exutables

```sh
chmod +x ~/.config/sweetconfigs-xorg/bin/bar/*
chmod +x ~/.config/sweetconfigs-xorg/bin/menu/*
chmod +x ~/.config/sweetconfigs-xorg/bin/system/*
chmod +x ~/.config/sweetconfigs-xorg/bin/utilities/*
chmod +x ~/.config/sweetconfigs-xorg/bin/widgets/*
chmod +x ~/.config/sweetconfigs-xorg/eww/scripts/*
```

- If you only installed bspwm then make ``bspwmrc`` into a excutable

```sh
chmod +x ~/.config/bspwm/bspwmrc
```

- If you only installed berry then make ``autostart`` into a excutable

```sh
chmod +x ~/.config/berry/autostart
```

	
Finally just reboot or logout of your session and log back in

</details>

## :art: <samp>COLORSCHEME</samp>

It's the color scheme I made and improved by [**``siduck``**](https://github.com/siduck), I was originally just gonna use [``paradise``](https://github.com/paradise-theme/paradise) or [``gruvbox``](https://github.com/morhetz/gruvbox) because it didn't fit well so [**SweetPastel**](https://github.com/SweetPastel) was born.

If you want to see the ports check it out at it's official [Github Page](https://github.com/SweetPastel)

<div align="center">
	<img src="https://user-images.githubusercontent.com/65948476/184591339-beba74a0-ddee-450b-a53d-e494857ad4dc.png" />
</div>

## :coffee: <samp>TIP JAR</samp> <kbd>OPTIONAL</kbd>
If you like my rice feel free to buy me a coffee it will help me a lot

<a href='https://ko-fi.com/K3K8C2M9Y' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://cdn.ko-fi.com/cdn/kofi1.png?v=3' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>

## :bulb: <samp>ACKNOWLEDGEMENTS</samp>

- :two_hearts: **Thanks to**

	Here are the awesome people that ~~stole~~ borrowed code from
	
	- [`adi1090x`](https://github.com/adi1090x) - For his configs and archcraft
	- [`nickclyde`](https://github.com/nickclyde) - For his rofi-bluetooth script
	- [`firecat53`](https://github.com/firecat53) - For networkmanager-dmenu
	- [`siduck`](https://github.com/siduck) - For NvChad and base46
	- [`PrayagS`](https://github.com/PrayagS) - For zscroll module
	- [`beyond9thousand`](https://github.com/beyond9thousand) - For polybar system tray
	- [`Syndrizzle`](https://github.com/Syndrizzle) - For [dharmx's](https://github.com/dharmx) old logger
	- [`dharmx`](https://github.com/dharmx) - For making vile, and widget inspiration
	- [`coolors.co`](https://coolors.co) - Just a great color tool
	- [`Stack Overflow`](https://stackoverflow.com/) - For answering all my stupid questions <kbd>Ctrl + C, Ctrl + V</kbd>
	- [`kmakise_`](https://www.reddit.com/user/kmakise_/) - For finding a performance bug
	- [`r/unixporn`](https://www.reddit.com/r/unixporn/) - A great hub for unix customization (Goodbye :frowning_face:)

- :star2: **Inspiration**
 	- [`Manas140`](https://github.com/Manas140)
	- [`kizu`](https://github.com/janleigh)
	- [`rxyhn`](https://github.com/rxyhn)
	- [`dharmx`](https://github.com/dharmx)

- :muscle: **Contributors**
	- [`Deathemonic`](https://github.com/Deathemonic) - Me obviously
	- [`GG`](https://github.com/weebcyberpunk) - Added mkdir to make sure directories exist https://github.com/Deathemonic/SweetDots/pull/6
	- [`Rohith`](https://github.com/Rohith04MVK) - Fixed some paths https://github.com/Deathemonic/SweetDots/pull/7 https://github.com/Deathemonic/SweetDots/pull/8
	- [`Kutuzov`](https://github.com/ArchieSW) - bin/status/bar syntax fix https://github.com/Deathemonic/SweetDots/pull/10
	
	<br>

	<a href="https://github.com/Deathemonic/SweetDots/graphs/contributors">
            <img src="https://contrib.rocks/image?repo=Deathemonic/SweetDots"/>
       	</a>
	
## :memo: <samp>TODO</samp>

**Focusing**
- [ ] ~~Wayland Version~~ Merging everything to one branch (Wayland and Xorg)
- [ ] Port all the scripts to python

**Planning**
- [ ] Better Padding for Widgets
- [ ] Improve the widget layout
- [ ] Use a better text scroller (Might create my own in rust)
- [ ] Use modules more on widgets
- [ ] Add a cconfiguration file to manage the configs easily
- [ ] Add screenshots on README.md
- [ ] Nix Support

**Done**
- [x] Add top-panel to all window managers

**Removed**
- ~~Use pijulius's fork of picom~~
- ~~Use [xborders](https://github.com/deter0/xborder) for fixing the border bugs~~
- ~~Add more options for window manager forks~~ - Will heavily focus on just the configs

	
## :scroll: <samp>COPYING</samp>

**SweetDots** is license under [MIT License](https://github.com/Deathemonic/SweetDots/blob/xorg/LICENSE)

> Will free to use the code from this repo just make sure that credit me :smile:
