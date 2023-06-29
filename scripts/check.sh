#!/usr/bin/env bash
set -ex

flake8 spex
mypy spex
