#!/usr/bin/env bash

# venv module for python
apt-get install python3-venv

# pipx
/usr/bin/python -m pip install --user pipx
/usr/bin/python -m pipx ensurepath

# supervisor and prefect tool
pipx install supervisor
pipx install --python /home/pi/.pyenv/versions/3.10.2/bin/python prefect
pipx install --python /home/pi/.pyenv/versions/3.10.2/bin/python poetry

# start supervisor
supervisord -c murkelhausen-data/supervisord.conf

# register with prefect cloud
prefect auth login --key api_key
prefect create project 'murkelhausen'

git clone ...
cd murkelhausen-data
poetry config virtualenvs.in-project true
poetry shell
poetry install
