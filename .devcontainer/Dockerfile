ARG ARCH=amd64
FROM lopsided/archlinux-$ARCH

WORKDIR /archlinux

RUN mkdir -p /archlinux/rootfs

COPY pacstrap-docker /archlinux/

RUN ./pacstrap-docker /archlinux/rootfs \
      bash sed gzip pacman archlinux-keyring && \
    # Install Arch Linux ARM keyring if available
    (pacman -r /archlinux/rootfs -S --noconfirm archlinuxarm-keyring || true) && \
    # Remove current pacman database, likely outdated very soon
    rm rootfs/var/lib/pacman/sync/*

FROM scratch
ARG ARCH=amd64

COPY --from=0 /archlinux/rootfs/ /
COPY rootfs/common/ /
COPY rootfs/$ARCH/ /

ENV LANG=en_US.UTF-8

RUN locale-gen && \
    pacman-key --init && \
    pacman-key --populate archlinux && \
    (pacman-key --populate archlinuxarm || true)

CMD ["/usr/bin/bash"]