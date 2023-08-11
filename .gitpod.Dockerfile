ARG ARCH=amd64
FROM lopsided/archlinux-$ARCH

WORKDIR /archlinux

RUN mkdir -p /archlinux/rootfs

COPY pacstrap-docker /archlinux/

RUN ./pacstrap-docker /archlinux/rootfs \
    bash zsh dash sed gzip pacman archlinux-keyring git neovim base base-devel && \
    rm rootfs/var/lib/pacman/sync/*

FROM scratch

COPY --from=0 /archlinux/rootfs/ /
COPY rootfs/common/ /
COPY rootfs/$ARCH/ /

ENV LANG=en_US.UTF-8

RUN locale-gen && \
    pacman-key --init && \
    pacman-key --populate archlinux

RUN pacman -Syu ttf-jetbrains-mono xdg-user-dirs neofetch bat ripgrep aria2

RUN git clone https://aur.archlinux.org/paru-bin.git && \
    cd paru-bin && \
    makepkg -si && \
    cd .. && rm -rf paru-bin

CMD ["/usr/bin/bash"]