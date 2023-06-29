#!/usr/bin/env bash
set -ex

black spex
isort --profile=black spex 
