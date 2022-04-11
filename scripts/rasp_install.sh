#!/usr/bin/env bash

# venv module for python
apt-get install python3-venv

# pipx
/usr/bin/python -m pip install --user pipx
/usr/bin/python -m pipx ensurepath

# supervisor tool
pipx install supervisor
