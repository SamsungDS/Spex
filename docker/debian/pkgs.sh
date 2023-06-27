#!/usr/bin/env bash
export DEBIAN_FRONTEND=noninteractive
exrpot DEBIAN_PRIORITY=critical
apt-get -qy update
apt-get -qy \
	-o "Dpkg::Options::=--force-confdef" \
	-o "Dpkg::Options::=--force-confold" upgrade
apt-get -qy --no-install-recommends install \
	apt-utils
apt-get -qy autoclean
apt-get -qy install \
	bash \
	build-essential \
	git \
	pipx \
	python3 \
	python3-pip \
	python3-venv \
	vim
