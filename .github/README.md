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

Welcome, Thanks for droping by! This is my dotfiles that I made, it's a dotfiles design to be understandable and hackable by anyone and themed with [**SweetPastel**](https://github.com/SweetPastel).

Instead of making multiple ``Window Manager Configs`` with different style I opt in on just one style but it should be compatible to other ``Window Manage`` so if you switch to another ``Window Manager`` it should be the same style, except for **``BSPWM``** and **``i3``** because there top bars are different but overall it should be the same, plus it's less work. All the configs are stored in a folder so it won't conflict at your pre existing configs **(Except of the window managers they will conflict unless you backup your old files)**

## :books: <samp>WIKI</samp> <kbd>RECOMMENDED</kbd>
If you have problems or need some information about the dotfiles check [wiki page](https://github.com/Deathemonic/SweetDots/wiki), it provides extra information, some documentation, and a troubleshoot page

## :package: <samp>INSTALL</samp>

<details open>
	<summary><b><samp>AUTO INSTALL</samp></b></summary>
<br>

<kbd>RECOMMENDED</kbd>
	
Just run this at your **Terminal** (``Curl`` and ``Bash`` needs to installed in your system)

```sh
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Deathemonic/SweetDots/xorg/install)"
```

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
	
6. If you have bspwm then copy ``cp -rf window-managers/bspwm`` to ``~/.config`` then you if you have bspwm and berry then copy both folders and etc.

```sh
cp -rf window-managers/berry ~/.config/
cp -rf window-managers/bspwm ~/.config/
cp -rf window-managers/i3 ~/.config/
cp -rf window-managers/leftwm ~/.config/
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

<details>
<summary><b>:two_hearts: <samp>THANKS TO</samp></b></summary>
<br>
	
Here are the awesome people that ~~stole~~ borrowed code from
	
WIP
	
</details>

- :star2: **Inspiration**
 	- [`Manas140`](https://github.com/Manas140)
	- [`kizu`](https://github.com/janleigh)
	- [`rxyhn`](https://github.com/rxyhn)
	- [`dharmx`](https://github.com/dharmx)

- :muscle: **Contributors**
	- [`Deathemonic`](https://github.com/Deathemonic) - Me obviously
	- [`GG`](https://github.com/weebcyberpunk) - https://github.com/Deathemonic/SweetDots/pull/6
	
	<br>

	<a href="https://github.com/Deathemonic/SweetDots/graphs/contributors">
            <img src="https://contrib.rocks/image?repo=Deathemonic/SweetDots"/>
       	</a>

### Stats

<details>
<summary>Rewrite Status</summary>

Configs (Xorg)

![](https://us-central1-progress-markdown.cloudfunctions.net/progress/98)

Configs (Wayland)

![](https://us-central1-progress-markdown.cloudfunctions.net/progress/55)

Window Manager Configs (Xorg)

![](https://us-central1-progress-markdown.cloudfunctions.net/progress/95)

Window Manager Configs (Wayland)

![](https://us-central1-progress-markdown.cloudfunctions.net/progress/37)

EWW (Xorg)

![](https://us-central1-progress-markdown.cloudfunctions.net/progress/99)

EWW (Wayland)

![](https://us-central1-progress-markdown.cloudfunctions.net/progress/50)

Sweetpastel Ports

![](https://us-central1-progress-markdown.cloudfunctions.net/progress/69)

README

![](https://us-central1-progress-markdown.cloudfunctions.net/progress/20)

Installer

![](https://us-central1-progress-markdown.cloudfunctions.net/progress/90)

</details>
