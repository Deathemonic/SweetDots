What is planned?

- ~~I'm merging both my xorg and wayland dotfiles into one and port most the scripts into python (Might re-port it to lua).~~

- Will be a collection of configs that make up a full desktop.

- Should be easily be used by other window manager, if you don't like the current window manager you can switch to a new one without needing to change main configs.

- It will be managed by `config.toml` file so you don't have to edit the configs that often.

Current problems

- The scripts relay on one python file called ``utils.py`` which holds custom functions and config parser so removing or moving the file will cause the dotfiles to not work.

- You also can't move the config file and it's required.

How do I solve it

- I need to make a argument to the ``utils.py`` to accept the custom location of the config file and make a default config somewhere in the ``usr`` and make it the fallback config in case the config file is deleted

Configs

![](https://us-central1-progress-markdown.cloudfunctions.net/progress/45)

Scripts

![](https://us-central1-progress-markdown.cloudfunctions.net/progress/24)

Window Manager Configs

![](https://us-central1-progress-markdown.cloudfunctions.net/progress/10)

EWW

![](https://us-central1-progress-markdown.cloudfunctions.net/progress/0)

Sweetpastel Ports

![](https://us-central1-progress-markdown.cloudfunctions.net/progress/69)

README

![](https://us-central1-progress-markdown.cloudfunctions.net/progress/0)

Installer

![](https://us-central1-progress-markdown.cloudfunctions.net/progress/10)

> **Note**: The branch is work in progress something might subject to change 
