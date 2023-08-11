ARG ARCH=amd64
FROM lopsided/archlinux-$ARCH

ENV LANG=en_US.UTF-8

RUN cp /etc/pacman.d/mirrorlist /etc/pacman.d/mirrorlist.backup
RUN rankmirrors -n 6 /etc/pacman.d/mirrorlist.backup > /etc/pacman.d/mirrorlist

RUN pacman -Syu bash zsh dash sed gzip pacman \
    archlinux-keyring git neovim base base-devel shadow \
    ttf-jetbrains-mono xdg-user-dirs neofetch bat ripgrep aria2 \
    --noconfirm --needed

RUN pacman-key --init
RUN pacman-key --populate archlinux

RUN locale-gen

RUN useradd -m -G wheel -s $(which zsh) user
RUN echo "user ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
RUN chown -R user:wheel /usr/local/src/

USER user
WORKDIR /usr/local/src/

RUN git clone https://aur.archlinux.org/paru-bin.git && \
    cd paru-bin && \
    makepkg -si --noconfirm && \
    cd .. && rm -rf paru-bin

RUN paru -Syy python3 pypy3 python-virtualenv python-ruff python-black python-isort python-mypy python-pip --needed --noconfirm

CMD ["/usr/bin/env dash"]
