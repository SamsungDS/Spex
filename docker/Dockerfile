# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

FROM nixos/nix:2.13.3
# These files, see the spex-repos, define the environment
RUN mkdir -p ~/.config/nix \
  && echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf \
  && mkdir -p /tmp/.nixenv
COPY ./flake.lock /tmp/.nixenv/flake.lock
COPY ./flake.nix /tmp/.nixenv/flake.nix
RUN mkdir -p ~/.config/nix \
  && echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf
# This will populate the cache, such that it will be faster upon use
RUN cd /tmp/.nixenv && nix develop .# -c true
