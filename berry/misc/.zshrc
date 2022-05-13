#Prompt
PS1="%F{cyan}%B%~/%b%f "

#Exports 
export PATH="$HOME/.local/bin/:$PATH"
export ZSH=$HOME/.oh-my-zsh

# OMZ
DISABLE_AUTO_UPDATE="true"
plugins=(git)
source $ZSH/oh-my-zsh.sh

# Aliases
alias cava='cava -p $HOME/.config/berry/cava'
alias ls='ls --color=auto -t'
alias cls='clear'
alias py='python3'
alias pip='pip3'
alias ytdl='youtube-dl'
alias docker='sudo docker'
alias open='xdg-open'
alias sudo='sudo -p "$(printf "\033[1;31mPassword: \033[0;0m" )"'
alias rm='printf "\033[1;31m" && rm -rIv'
alias cp='printf "\033[1;32m" && cp -rv'
alias mv='printf "\033[1;34m" && mv -v'
alias mkdir='printf "\033[1;33m" && mkdir -v'
alias rmdir='printf "\033[1;35m" && rmdir -v'
alias l='ls -lh'
alias ll='ls -lah'
alias la='ls -a'
alias lm='ls -m'
alias lr='ls -R'
alias lg='ls -l --group-directories-first'
alias gcl='git clone --depth 1'
alias gi='git init'
alias ga='git add'
alias gc='git commit -m'
alias gp='git push origin master'
alias vim='nvim'
alias anime='ani-cli'
alias manga='manga-cli'
alias yt='ytfzf'

# History
HISTSIZE=500
SAVEHIST=1000
HISTFILE=.cache/zsh_history

# Tab completion
autoload -U compinit
zstyle ':completion:*' menu select
zmodload zsh/complist
compinit
_comp_options+=(globdots)

# Binds
bindkey "^[[3~" delete-char
bindkey "^A" beginning-of-line
bindkey "^Q" end-of-line
bindkey "^[[1;5C" forward-word
bindkey "^[[1;5D" backward-word

# Spicetify
export PATH="$PATH:$HOME/.spicetify"