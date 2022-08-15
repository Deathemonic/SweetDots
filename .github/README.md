<div align="center">
  <img src="https://user-images.githubusercontent.com/65948476/184574939-8c3ee024-9f4d-4007-bf12-10ad61574777.png" width="500px" alt="logo">
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

# <samp>Welcome! Thanks for Dropping by :smiling_face_with_three_hearts:,</samp>

## :question: <samp>ABOUT</samp>

It's a dotfiles design to be understandable and hackable by anyone and themed with [**SweetPastel**](https://github.com/SweetPastel).

Instead of making multiple ``Window Manager Configs`` with different style I opt in on just one style but it should be compatible to other ``Window Manage`` so if you switch to another ``Window Manager`` it should be the same style, except for **``BSPWM``** and **``i3``** because there top bars are different but overall it should be the same, plus it's less work. All the configs are stored in a folder so it won't conflict at your pre existing configs **(Except of the window managers they will conflict unless you backup your old files)**

## :books: <samp>WIKI</samp>
If you have problems or need some information about the dotfiles check [wiki page](https://github.com/Deathemonic/SweetDots/wiki), it provides extra information, some documentation, and a troubleshoot page

## :package: <samp>INSTALL</samp>

<details open>
<summary>Auto Install</summary>
<br>

Just run this at your **Terminal** (``Curl`` and ``Bash`` needs to installed in your system)

```sh
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Deathemonic/SweetDots/xorg/install)"
```

</details>

<details>
<summary>Manual Install</summary>
<br>
	
<<<<<<< HEAD
> **Note**: First up install the dependencies need if not the dotfiles doesn't work. Check out this [link](https://github.com/Deathemonic/SweetDots/wiki/Documentation#dependencies) for the list of dependencies
=======
> **Note**: First up install the dependencies need if not the dotfiles doesn't work. Check out this link for the list of dependencies
>>>>>>> 5f32917637fb740e7fce82043f36a26b6181b1e8

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
<<<<<<< HEAD
=======

### Stats	
>>>>>>> 5f32917637fb740e7fce82043f36a26b6181b1e8

</details>

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
