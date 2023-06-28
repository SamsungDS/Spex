FROM nixos/nix:master

RUN mkdir -p ~/.config/nix \
    && echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf

COPY nix-build-script.sh /nix-build-script.sh

WORKDIR /spex-dir
CMD bash /nix-build-script.sh
