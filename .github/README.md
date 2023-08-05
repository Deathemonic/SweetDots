What is planned?

- ~~I'm merging both my xorg and wayland dotfiles into one and port most the scripts into python (Might re-port it to lua).~~

- Will be a collection of configs that make up a full desktop.

- Should be easily be used by other window manager, if you don't like the current window manager you can switch to a new one without needing to change main configs.

- It will be managed by `config.toml` file so you don't have to edit the configs that often.

Current problems

- The scripts relay on one python file called ``utils.py`` which holds custom functions and config parser so removing or moving the file will cause the dotfiles to not work.

- You also can't move the config file and it's required.

- [PEP 0668](https://peps.python.org/pep-0668) states that you need to create a virtual environment first which I'm not a fan of because my dotfile relies on installing pip packages at global or local, because it breaks the system we can't do that now. I have to find a work around without using the break-system option and I don't think that --user will work.

How do I solve it

- I need to make a argument to the ``utils.py`` to accept the custom location of the config file and make a default config somewhere in the ``usr`` and make it the fallback config in case the config file is deleted

- I might use python packages provided by the package manager but they some unmaintained or outdated, or I might use a virtualenv and use like a shebang but I fear it might lose performance, also other option is to abandon python entirely and use a different language like lua or rust.

Configs

![](https://us-central1-progress-markdown.cloudfunctions.net/progress/51)

Scripts

![](https://us-central1-progress-markdown.cloudfunctions.net/progress/25)

Window Manager Configs

![](https://us-central1-progress-markdown.cloudfunctions.net/progress/25)

EWW

![](https://us-central1-progress-markdown.cloudfunctions.net/progress/0)

Sweetpastel Ports

![](https://us-central1-progress-markdown.cloudfunctions.net/progress/69)

README

![](https://us-central1-progress-markdown.cloudfunctions.net/progress/0)

Installer

![](https://us-central1-progress-markdown.cloudfunctions.net/progress/10)

> **Note**: The branch is work in progress something might subject to change 
